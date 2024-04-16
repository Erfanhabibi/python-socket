import io
import tkinter as tk
import socket
import cv2
import pyaudio
import wave
import os
from PIL import Image, ImageTk
from datetime import datetime


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Application")

        self.start_button = tk.Button(
            self.root, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

        self.capture_button = tk.Button(
            self.root, text="Capture Image", command=self.capture_image)
        self.capture_button.pack()

        self.record_button = tk.Button(
            self.root, text="Record Audio", command=self.record_audio)
        self.record_button.pack()

        # Create a label to display the webcam feed
        self.webcam_label = tk.Label(self.root)
        self.webcam_label.pack()

        # Start webcam feed
        self.start_webcam()

        # Create a button to close the app
        self.close_button = tk.Button(
            self.root, text="Close", command=self.close_app)
        self.close_button.pack()

    def start_server(self):
        self.status_label.config(text="Server is running...")
        self.root.update()
        # ******
        # host_name = socket.gethostname()
        # HOST = socket.gethostname(host_name)
        # ******
        HOST = '127.0.0.1'  # Change to the server's IP address or 'localhost' for local testing
        # Change to a desired port number (make sure it's not in use)
        PORT = 12345

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()

            self.status_label.config(
                text=f"Server is listening on {HOST}:{PORT}")
            self.root.update()

            conn, addr = server_socket.accept()
            # conn = conn1   addr = 127.55.44.0 , 54123

            with conn:
                self.status_label.config(text=f"Connected by {addr}")
                self.root.update()

                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    self.process_data(data)

    def capture_image(self):
        if hasattr(self, 'cap'):
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to bytes and send to server
                _, img_bytes = cv2.imencode('.jpg', frame)
                # self.send_data(img_bytes)

                # Save the captured image to a folder with timestamp
                folder_path = "captured_images_server"
                os.makedirs(folder_path, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(
                    folder_path, f"captured_image_{timestamp}.jpg")
                cv2.imwrite(image_path, frame)
                self.status_label.config(text=f"Image saved: {image_path}")

                # Display the captured image on the webcam label
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.webcam_label.imgtk = imgtk
                self.webcam_label.configure(image=imgtk)
                self.root.update()
        else:
            self.status_label.config(text="Webcam not available")

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 5
        # WAVE_OUTPUT_FILENAME = "captured_audio_{timestamp}.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()
        # Save the recorded audio to a folder with timestamp
        folder_path = "captured_audio_server"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join(
            folder_path, f"captured_audio_{timestamp}.wav")
        with wave.open(audio_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        self.status_label.config(text=f"Audio saved: {audio_path}")
        self.send_data(audio_path)

    # def send_data(self, data):
    #     HOST = self.client_ip_entry.get()
    #     PORT = int(self.client_port_entry.get())

    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    #         try:
    #             client_socket.connect((HOST, PORT))
    #             client_socket.sendall(data)
    #             self.status_label.config(text="Data sent to client")
    #         except Exception as e:
    #             self.status_label.config(text=f"Error:{e}")
    #         self.root.update()

    def receive_picture(self, data):
        # Receive the picture data and save it
        folder_path = "received_images_server"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(
            folder_path, f"received_image_{timestamp}.jpg")
        with open(image_path, 'wb') as f:
            f.write(data)
        self.status_label.config(
            text=f"Image received and saved: {image_path}")

    def start_webcam(self):
        self.cap = cv2.VideoCapture(0)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.webcam_label.imgtk = imgtk
            self.webcam_label.configure(image=imgtk)
            self.root.update()

    def close_app(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
