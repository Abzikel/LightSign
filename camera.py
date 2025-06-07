# Import libraries
import cv2
import json
import os
import re
import platform
import subprocess
import numpy as np
from typing import List, Tuple

# Function to get the camera information
def get_camera_info() -> List[Tuple[int, str]]:
    # Array to save the camera information using and index and the name of the camera
    camera_info = []
    max_cameras = 3
    
    # Loop to check a maximum of 3 cameras
    for index in range(max_cameras):
        cap = None
        try:
            # Try to open the camera with different backends
            if platform.system() == 'Windows':
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(index)
            
            if cap.isOpened():
                # Default name
                camera_name = f"Camera {index}"
                
                # Platform-specific name detection
                if platform.system() == 'Windows':
                    try:
                        # Try to get device name through DirectShow
                        _, filename = os.path.split(cap.getBackendName())
                        camera_name = re.sub(r'_vid.*', '', filename, flags=re.I)
                    except:
                        pass
                
                # Linux
                elif platform.system() == 'Linux':
                    try:
                        # Use v4l2-ctl on Linux
                        result = subprocess.run(
                            ['v4l2-ctl', '--list-devices'],
                            capture_output=True,
                            text=True
                        )
                        lines = result.stdout.split('\n')
                        for i, line in enumerate(lines):
                            if f'/dev/video{index}' in line:
                                camera_name = lines[i-1].strip()
                                break
                    except:
                        pass
                
                # MacOs
                elif platform.system() == 'Darwin': 
                    try:
                        # Get camera information
                        result = subprocess.run(
                            ['system_profiler', 'SPCameraDataType', '-json'],
                            capture_output=True,
                            text=True
                        )
                        
                        # Convert result to JSON
                        camera_data = json.loads(result.stdout)
                        
                        # Get camera name
                        if 'SPCameraDataType' in camera_data:
                            cameras = []
                            for item in camera_data['SPCameraDataType']:
                                if '_name' in item:
                                    cameras.append(item['_name'])
                            
                            if index < len(cameras):
                                camera_name = cameras[index]
                                
                    except Exception as e:
                        print(f"Error trying to get camera from macOS: {str(e)}")

                        # Try another method
                        try:
                            result = subprocess.run(
                                ['ioreg', '-r', '-c', 'IOUSBDevice'],
                                capture_output=True,
                                text=True
                            )
                            usb_cameras = re.findall(r'"USB Camera" = "([^"]+)"', result.stdout)
                            if usb_cameras and index < len(usb_cameras):
                                camera_name = usb_cameras[index]
                        except:
                            pass
                
                # Add camera info
                camera_info.append((index, camera_name))
                
        finally:
            if cap is not None:
                cap.release()
    
    return camera_info

def show_camera_selection(cameras: List[Tuple[int, str]]) -> int:
    # Show camera selection menu
    if not cameras:
        print("No cameras found!")
        return None
    
    # Create selection window
    window_name = "Select Camera"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Add title
    cv2.putText(img, "Available Cameras", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    # Add camera options
    for index, (index, name) in enumerate(cameras):
        cv2.putText(img, f"[{index}] {name}", (50, 100 + index * 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Add instructions
    cv2.putText(img, "Press the NUMBER KEY of your choice", (50, 350), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(img, "or ESC to cancel", (50, 380), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Show window
    cv2.imshow(window_name, img)
    
    while True:
        # Get pressed key
        key = cv2.waitKey(1) & 0xFF
        
        # Check number keys (0-9)
        if 48 <= key <= 57:
            selection = key - 48
            if selection < len(cameras):
                cv2.destroyAllWindows()
                return cameras[selection][0]
        
        # ESC to exit
        if key == 27:
            break
    
    cv2.destroyAllWindows()
    return None

# Testing
if __name__ == "__main__":
    # Detect cameras and get information about them
    print("Detecting cameras...")
    cameras = get_camera_info()
    
    # If the program doesn't detect any camera, finish it
    if not cameras:
        print("No cameras found!")
        exit()
    
    # Print available cameras
    print("Available cameras:")
    for idx, (index, name) in enumerate(cameras):
        print(f"  [{idx}] {name}")
    
    # Get selected index
    selected_index = show_camera_selection(cameras)
    
    if selected_index is not None:
        # Print selected camera index and instance camera to show
        print(f"Selected camera index: {selected_index}")
        cap = cv2.VideoCapture(selected_index)
        
        # Test camera feed
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error reading from camera!")
                break
                
            cv2.imshow(f"Live Camera - Press ESC to quit", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        