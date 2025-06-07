# Import libraries
import camera
import cv2
import math
import os
import time
import requests
import mediapipe as mp
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

# Configuration to connect with ESP32
ESP32_IP = "192.168.4.1"
ENDPOINT_URL = f"http://{ESP32_IP}/setColor"

# Function to send color
def send_color(hex_color):
    # Simple validation
    if not hex_color.startswith('#') or len(hex_color) != 7:
        print("Error: The color must be in a valid format (ej: #RRGGBB).")
        return

    try:
        # Send request as a POST with a timeout
        response = requests.post(ENDPOINT_URL, data=hex_color, timeout=0.5)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"Timeout error '{hex_color}'. Verify the connection with ESP32.")
    except requests.exceptions.ConnectionError:
        print(f"Conexion error ESP32. Verify access point.")
    except requests.exceptions.RequestException as e:
        print(f"Error while changing the color '{hex_color}': {e}")

# Function to normalize the distance between to points
def distancia(p1, p2):
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# Main code
if __name__ == "__main__":
    # Load dataset and import it to a DataFrame
    dataset_path = os.path.expanduser("gestures_dataset.csv")
    df = pd.read_csv(dataset_path)

    # Separate characteristics from labels
    X = df[[
        "WRIST_X", "WRIST_Y",
        "THUMB_TIP_X", "THUMB_TIP_Y",
        "INDEX_TIP_X", "INDEX_TIP_Y",
        "MIDDLE_TIP_X", "MIDDLE_TIP_Y"
    ]]
    Y = df["label"]

    # Train model using GradientBoosting
    model = GradientBoostingClassifier()
    model.fit(X, Y)

    # MediaPipe setup
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

    # Get camera
    cameras = camera.get_camera_info()
    camera_index = camera.show_camera_selection(cameras)
    cap = cv2.VideoCapture(camera_index, cv2.CAP_ANY)

    # Variables and control
    red, green, blue = 0, 0, 0
    selected_channel = None
    last_prediction = None
    prediction_start_time = None
    DELAY_SECONDS = 5

    # Variables for the ESP32
    last_sent_hex_color = ""
    last_sent_time = time.time()
    SEND_INTERVAL_SECONDS = 0.1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # It is detecting the hands
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get key points
                puntos = {
                    'WRIST': hand_landmarks.landmark[0],
                    'THUMB_TIP': hand_landmarks.landmark[4],
                    'INDEX_TIP': hand_landmarks.landmark[8],
                    'MIDDLE_TIP': hand_landmarks.landmark[12],
                    'MIDDLE_MCP': hand_landmarks.landmark[9]
                }

                wrist = puntos['WRIST']
                middle_mcp = puntos['MIDDLE_MCP']
                d = distancia(wrist, middle_mcp)
                if d == 0:
                    d = 1e-6

                normalized = []
                for key in ['WRIST', 'THUMB_TIP', 'INDEX_TIP', 'MIDDLE_TIP']:
                    p = puntos[key]
                    x = (p.x - wrist.x) / d
                    y = (p.y - wrist.y) / d
                    normalized.extend([x, y])

                # Predict gesture
                input_data = pd.DataFrame([normalized], columns=X.columns)
                prediction = model.predict(input_data)[0]

                # Gesture detection
                current_time = time.time()
                if prediction == last_prediction:
                    if prediction_start_time is None:
                        prediction_start_time = current_time
                    elif current_time - prediction_start_time >= DELAY_SECONDS:
                        if prediction == "NUMBER_1":
                            selected_channel = "red"
                        elif prediction == "NUMBER_2":
                            selected_channel = "green"
                        elif prediction == "NUMBER_3":
                            selected_channel = "blue"
                        elif prediction == "THUMB_UP" and selected_channel:
                            if selected_channel == "red":
                                red = min(255, red + 1)
                            elif selected_channel == "green":
                                green = min(255, green + 1)
                            elif selected_channel == "blue":
                                blue = min(255, blue + 1)
                        elif prediction == "THUMB_DOWN" and selected_channel:
                            if selected_channel == "red":
                                red = max(0, red - 1)
                            elif selected_channel == "green":
                                green = max(0, green - 1)
                            elif selected_channel == "blue":
                                blue = max(0, blue - 1)
                else:
                    last_prediction = prediction
                    prediction_start_time = current_time

                # Draw points
                h, w, _ = frame.shape
                for key in ['WRIST', 'THUMB_TIP', 'INDEX_TIP', 'MIDDLE_TIP']:
                    px, py = int(puntos[key].x * w), int(puntos[key].y * h)
                    cv2.circle(frame, (px, py), 6, (255, 0, 255), -1)

        # Show square of the current RGB color
        cv2.rectangle(frame, (10, 10), (80, 80), (blue, green, red), -1)

        # Show selected channel and RGB using hexadecimal value
        canal = selected_channel if selected_channel else "NINGUNO"
        hex_color = f"#{red:02X}{green:02X}{blue:02X}"
        cv2.putText(frame, f"Canal: {canal}", (100, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Color: {hex_color}", (100, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Send hexadecimal value to ESP32
        current_time_for_send = time.time()
        if hex_color != last_sent_hex_color and (current_time_for_send - last_sent_time) >= SEND_INTERVAL_SECONDS:
            send_color(hex_color)
            last_sent_hex_color = hex_color
            last_sent_time = current_time_for_send

        # Show window
        cv2.imshow("Detector de Gestos", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            # Turn off LED
            send_color("#000000")
            break

    cap.release()
    cv2.destroyAllWindows()
