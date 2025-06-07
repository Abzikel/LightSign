# Import libraries
import camera
import cv2
import math
import os
import mediapipe as mp
import pandas as pd

# Function to normalize the distance between to points
def distance(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Main code
if __name__ == "__main__":
    # MediaPipe setup
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

    # Get camera
    cameras = camera.get_camera_info()
    camera_index = camera.show_camera_selection(cameras)
    cap = cv2.VideoCapture(camera_index, cv2.CAP_ANY)

    # Dataset columns
    columns = [
        "WRIST_X", "WRIST_Y",
        "THUMB_TIP_X", "THUMB_TIP_Y",
        "INDEX_TIP_X", "INDEX_TIP_Y",
        "MIDDLE_TIP_X", "MIDDLE_TIP_Y",
        "label"
    ]
    data = pd.DataFrame(columns=columns)
    current_label = "TESTING"

    # Loop to read hands
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Get frame and hands results from MediaPipe
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # It is detecting the hands
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the conexions
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
                )

                # Get key points
                points = {
                    'WRIST': hand_landmarks.landmark[0],
                    'THUMB_TIP': hand_landmarks.landmark[4],
                    'INDEX_TIP': hand_landmarks.landmark[8],
                    'MIDDLE_TIP': hand_landmarks.landmark[12],
                    'MIDDLE_MCP': hand_landmarks.landmark[9] # Extra point to scale
                }

                # Normalization using the WRIST and MIDDLE_MCP
                wrist = points['WRIST']
                middle_mcp = points['MIDDLE_MCP']
                normalized_distance = distance(wrist, middle_mcp)

                # Do not try to divide by zero
                if normalized_distance == 0:
                    normalized_distance = 1e-6

                # Get normalized points
                normalized_points = []
                for key in ['WRIST', 'THUMB_TIP', 'INDEX_TIP', 'MIDDLE_TIP']:
                    point = points[key]
                    x_norm = (point.x - wrist.x) / normalized_distance
                    y_norm = (point.y - wrist.y) / normalized_distance
                    normalized_points.extend([x_norm, y_norm])

                # Draw original points to a better visualization
                height, width, _ = frame.shape
                colors = [(255, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
                for index, key in enumerate(['WRIST', 'THUMB_TIP', 'INDEX_TIP', 'MIDDLE_TIP']):
                    px, py = int(points[key].x * width), int(points[key].y * height)
                    cv2.circle(frame, (px, py), 6, colors[index], -1)

        # Get pressed key
        key = cv2.waitKey(1)

        # SPACE
        if key == 32:
                
            # Save data when pressing the SPACE button
            new_row = normalized_points + [current_label]
            data.loc[len(data)] = new_row

        # ESC
        elif key == 27:
            # Get the current working directory (which is usually your project's root)
            project_root = os.getcwd()

            # Define the path to the 'datasets' folder within your project
            dataset_folder = os.path.join(project_root, "datasets")

            # Create the 'datasets' folder if it doesn't exist
            if not os.path.exists(dataset_folder):
                os.makedirs(dataset_folder)

            # Define the file path inside the 'datasets' folder
            file_path = os.path.join(dataset_folder, current_label + ".csv")

            # Save Dataset
            data.to_csv(file_path, index=False)
            print(f"Dataset saved: {file_path}")

            # Clear camera and destroy the window
            cap.release()
            cv2.destroyAllWindows()
            exit()

        # Show current label on screen and define title
        cv2.putText(frame, f"Label: {current_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        cv2.imshow("Get Gestures - Press ESC to exit", frame)
