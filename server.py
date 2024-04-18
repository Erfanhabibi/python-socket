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
        self.server_socket = None
        self.socket = None

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

        hostname = socket.gethostname()
        HOST = socket.gethostbyname(hostname)

        # HOST = '127.0.0.1'  # Change to the server's IP address or 'localhost' for local testing
        PORT = 12345

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()

        self.status_label.config(
            text=f"Server is listening on {HOST}:{PORT}")
        self.root.update()

        conn, addr = self.server_socket.accept()

        self.socket = conn

        self.status_label.config(text=f"Connected by {addr}")
        
        self.capture_button.config(state=tk.NORMAL)
        self.record_button.config(state=tk.NORMAL)
        
        self.root.update()

        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                self.process_data(data)
            except Exception as e:
                self.status_label.config(
                    text=f"Error receiving data from client: {str(e)}")
                break

    def process_data(self, data):
        # Determine the type of data received and call the appropriate function
        if data.startswith(b'IMG'):  # Assuming image data starts with 'IMG'
            self.receive_image(data[3:])  # Remove the 'IMG' header
        elif data.startswith(b'AUDIO'):  # Assuming audio data starts with 'AUDIO'
            self.receive_audio(data[5:])  # Remove the 'AUDIO' header
        else:
            self.status_label.config(text="Unknown data received")

    def receive_image(self, img_bytes):
        # Save the received image to a file
        folder_path = "received_images_server"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(
            folder_path, f"received_image_{timestamp}.jpg")
        with open(image_path, 'wb') as img_file:
            img_file.write(img_bytes)
        self.status_label.config(text=f"Image received and saved: {image_path}")

    def receive_audio(self, audio_bytes):
        # Save the received audio to a file
        folder_path = "received_audio_server"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join(
            folder_path, f"received_audio_{timestamp}.wav")
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(audio_bytes)
        self.status_label.config(text=f"Audio received and saved: {audio_path}")

    def send_data(self, data):
        try:
            if self.socket:
                self.socket.sendall(data)
            else:
                self.status_label.config(text="Not connected to client")
        except Exception as e:
            self.status_label.config(
                text=f"Error sending data to client: {str(e)}")

    def capture_image(self):
        if hasattr(self, 'cap'):
            ret, frame = self.cap.read()
            if ret:
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

                # Convert frame to bytes
                with open(image_path, 'rb') as img_file:
                    img_bytes = img_file.read()

                # Send image data to the server
                self.send_data(b'IMG' + img_bytes)
        else:
            self.status_label.config(text="Webcam not available")

    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 5
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

        # Convert audio file to bytes
        with open(audio_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()

        # Send audio data to the server
        self.send_data(b'AUDIO' + audio_bytes)

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
        if self.server_socket:
            self.server_socket.close()
        if self.cap:
            self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
