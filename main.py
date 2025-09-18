
import json
import cv2
import os
from collections import Counter
from inference_sdk import InferenceHTTPClient

def main():
    # Initialize Roboflow client
    client = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key="OCYzLwdUcqDtypAh0OYT"
    )
    
    # Use the local living room image
    image_path = "living-room.jpg"
    
    print(f"Processing local image: {image_path}")
    print("Connecting to Roboflow...")
    
    try:
        # Try using a public COCO model first to test connectivity
        print("Testing with COCO object detection model...")
        result = client.infer(image_path, model_id="coco/3")
        
        print("✅ Successfully connected to Roboflow!")
        print("✅ COCO model working - now trying your custom workflow...")
        
        # Now try your custom workflow
        try:
            result = client.run_workflow(
                workspace_name="petes-workspace-oetpj",
                workflow_id="detect-count-and-visualise-furniture-instant",
                images={
                    "image": image_path
                },
                use_cache=True
            )
            print("✅ Custom workflow successful!")
        except Exception as workflow_error:
            print(f"Custom workflow failed: {workflow_error}")
            print("Continuing with COCO model results for demonstration...")
        
        print("✅ Successfully connected to Roboflow!")
        print("\n" + "="*50)
        print("DETECTION RESULTS")
        print("="*50)
        
        # Extract detections from the workflow result
        # The workflow returns a list with detection data
        detections = []
        
        if isinstance(result, list) and len(result) > 0:
            # Get the first result which contains the predictions
            first_result = result[0]
            if 'predictions' in first_result and 'predictions' in first_result['predictions']:
                detections = first_result['predictions']['predictions']
            elif 'detections' in first_result:
                detections = first_result['detections']
        
        if not detections:
            print("Raw result structure:")
            print(json.dumps(result, indent=2))
            return
        
        # Count objects by class
        object_counts = Counter()
        total_objects = 0
        
        print(f"Found {len(detections)} detections:\n")
        
        for i, detection in enumerate(detections, 1):
            class_name = detection.get('class', 'Unknown')
            confidence = detection.get('confidence', 0)
            x = detection.get('x', 0)
            y = detection.get('y', 0)
            width = detection.get('width', 0)
            height = detection.get('height', 0)
            
            object_counts[class_name] += 1
            total_objects += 1
            
            print(f"{i}. {class_name}")
            print(f"   Confidence: {confidence:.2%}")
            print(f"   Position: ({x:.1f}, {y:.1f})")
            print(f"   Size: {width:.1f} x {height:.1f}")
            print()
        
        # Display object counts
        print("="*50)
        print("OBJECT COUNTS")
        print("="*50)
        print(f"Total objects detected: {total_objects}\n")
        
        for class_name, count in object_counts.most_common():
            print(f"{class_name}: {count}")
        
        # Create visualization
        print("\n" + "="*50)
        print("CREATING VISUALIZATION")
        print("="*50)
        
        create_visualization(image_path, detections)
        
        # Save detection results to JSON
        output_file = "detection_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                'image_path': image_path,
                'total_objects': total_objects,
                'object_counts': dict(object_counts),
                'detections': detections
            }, f, indent=2)
        
        print(f"✅ Results saved to {output_file}")
        print(f"✅ Visualization saved to output_with_detections.jpg")
        
    except Exception as e:
        print(f"❌ Error connecting to Roboflow: {str(e)}")
        print("Please check your API key and internet connection.")

def create_visualization(image_source, detections):
    """Create a visualization of the detections on the image"""
    try:
        # Handle both local files and URLs
        if image_source.startswith('http'):
            # Download image from URL
            import urllib.request
            import numpy as np
            
            print(f"Downloading image from URL...")
            with urllib.request.urlopen(image_source) as response:
                image_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        else:
            # Load local image file
            image = cv2.imread(image_source)
        
        if image is None:
            print(f"Error: Could not load image from {image_source}")
            return
        
        # Define colors for different classes (BGR format for OpenCV)
        colors = [
            (255, 0, 0),    # Blue
            (0, 255, 0),    # Green
            (0, 0, 255),    # Red
            (255, 255, 0),  # Cyan
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Yellow
            (128, 0, 128),  # Purple
            (255, 165, 0),  # Orange
        ]
        
        class_color_map = {}
        color_index = 0
        
        # Draw bounding boxes and labels
        for detection in detections:
            class_name = detection.get('class', 'Unknown')
            confidence = detection.get('confidence', 0)
            x = detection.get('x', 0)
            y = detection.get('y', 0)
            width = detection.get('width', 0)
            height = detection.get('height', 0)
            
            # Assign color to class if not already assigned
            if class_name not in class_color_map:
                class_color_map[class_name] = colors[color_index % len(colors)]
                color_index += 1
            
            color = class_color_map[class_name]
            
            # Calculate bounding box coordinates
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with confidence
            label = f"{class_name}: {confidence:.2%}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Draw label background
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Save the visualization
        output_path = "output_with_detections.jpg"
        cv2.imwrite(output_path, image)
        
        print(f"Visualization created with {len(detections)} detections")
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")

if __name__ == "__main__":
    main()
