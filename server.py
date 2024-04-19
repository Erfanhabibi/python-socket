import time
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
        self.photo_server_socket = None
        self.audio_server_socket = None
        self.photo_socket = None
        self.audio_socket = None

        self.start_button = tk.Button(
            self.root, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.photo_status_label = tk.Label(self.root, text="")
        self.photo_status_label.pack()

        self.audio_status_label = tk.Label(self.root, text="")
        self.audio_status_label.pack()

        self.capture_button = tk.Button(
            self.root, text="Capture Image", command=self.capture_image, state=tk.DISABLED)
        self.capture_button.pack()

        self.record_button = tk.Button(
            self.root, text="Record Audio", command=self.record_audio, state=tk.DISABLED)
        self.record_button.pack()
        
        self.receive_image = tk.Button(
            self.root, text="Receive image", command=self.receive_image, state=tk.DISABLED)
        self.receive_image.pack()
        
        self.receive_voice = tk.Button(
            self.root, text="Receive voice", command=self.receive_voice, state=tk.DISABLED)
        self.receive_voice.pack()

        self.start_webcam()

        # Create a button to close the app
        self.close_button = tk.Button(
            self.root, text="Close", command=self.close_app)
        self.close_button.pack()

    def start_server(self):
        try:
            self.photo_status_label.config(text="Starting server...")
            self.audio_status_label.config(text="Starting server...")
            self.root.update()


            hostname = socket.gethostname()
            # getting the IP address using socket.gethostbyname() method
            HOST = socket.gethostbyname(hostname)
            # HOST = '127.0.0.1'
            PHOTO_PORT = 12345
            AUDIO_PORT = 12346

            self.photo_server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.photo_server_socket.bind((HOST, PHOTO_PORT))
            self.photo_server_socket.listen(1)

            self.audio_server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.audio_server_socket.bind((HOST, AUDIO_PORT))
            self.audio_server_socket.listen(1)

            self.photo_status_label.config(
                text=f"Server is listening on {HOST}:{PHOTO_PORT} for photos")
            self.audio_status_label.config(
                text=f"Server is listening on {HOST}:{AUDIO_PORT} for audio")
            self.root.update()

            photo_conn, photo_addr = self.photo_server_socket.accept()
            audio_conn, audio_addr = self.audio_server_socket.accept()

            self.photo_socket = photo_conn
            self.audio_socket = audio_conn

            self.photo_status_label.config(
                text=f"Connected for photos by {photo_addr}")
            self.audio_status_label.config(
                text=f"Connected for audio by {audio_addr}")

            self.capture_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL)
            self.receive_image.config(state=tk.NORMAL)
            self.receive_voice.config(state=tk.NORMAL)
                
            self.root.update()      


        except Exception as e:
            print(f"Error starting server: {str(e)}")


    def receive_image(self):

        timenow = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Receiving image data
        img_data = self.photo_socket.recv(100000)
        if img_data.startswith(b'IMG'):
            with open(f"received_image_server_{timenow}.jpg", 'wb') as img_file:
                img_file.write(img_data[3:])
            self.photo_status_label.config(
                text=f"Image received: received_image_server_{timenow}.jpg")


    def receive_voice(self):

        timenow = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Receiving audio data
        audio_data = self.audio_socket.recv(3000000)
        # Ensure that the received data starts with "AUDIO"
        
        if audio_data.startswith(b'AUDIO'):
            with open(f"received_audio_server_{timenow}.wav", 'wb') as audio_file:
                audio_file.write(audio_data[5:])
            self.audio_status_label.config(
                text=f"Audio received: received_audio_server_{timenow}.wav")


    def send_data(self, socket, data):
        try:
            if socket:
                socket.sendall(data)
            else:
                self.photo_status_label.config(text="Not connected to client")
                self.audio_status_label.config(text="Not connected to client")
        except Exception as e:
            print(f"Error sending data to client: {str(e)}")

    def capture_image(self):
        try:
            if hasattr(self, 'cap'):
                ret, frame = self.cap.read()
                if ret:
                    folder_path = "captured_images_server"
                    os.makedirs(folder_path, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = os.path.join(
                        folder_path, f"captured_image_{timestamp}.jpg")
                    cv2.imwrite(image_path, frame)
                    self.photo_status_label.config(
                        text=f"Image saved: {image_path}")

                    with open(image_path, 'rb') as img_file:
                        img_bytes = img_file.read()

                    self.send_data(self.photo_socket, b'IMG' + img_bytes)
            else:
                self.photo_status_label.config(text="Webcam not available")
        except Exception as e:
            print(f"Error capturing image: {str(e)}")

    def record_audio(self):
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 30
            p = pyaudio.PyAudio()

            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            frames = []

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

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

            self.audio_status_label.config(text=f"Audio saved: {audio_path}")

            with open(audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            self.send_data(self.audio_socket, b'AUDIO' + audio_bytes)
        except Exception as e:
            print(f"Error recording audio: {str(e)}")

    def start_webcam(self):
        try:
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
        except Exception as e:
            print(f"Error starting webcam: {str(e)}")

    def close_app(self):
        try:
            if self.photo_socket:
                self.photo_socket.close()
            if self.audio_socket:
                self.audio_socket.close()
            if hasattr(self, 'cap'):
                self.cap.release()
            self.root.destroy()
        except Exception as e:
            print(f"Error closing app: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
