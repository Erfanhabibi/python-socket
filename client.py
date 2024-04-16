import tkinter as tk
import socket
import cv2
import pyaudio
import wave
import os
from PIL import Image, ImageTk
from datetime import datetime
import io


class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client Application")

        self.connect_button = tk.Button(
            self.root, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

        self.IP_label = tk.Label(self.root, text="Enter Server IP:")
        self.IP_label.pack()
        self.IP_entry = tk.Entry(self.root)
        self.IP_entry.pack()

        self.port_label = tk.Label(self.root, text="Enter Server Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.root)
        self.port_entry.pack()

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

    def connect_to_server(self):
        host = self.IP_entry.get()
        port = int(self.port_entry.get())

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((host, port))
                self.status_label.config(text=f"Connected to {host}:{port}")
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")
            self.root.update()

    def send_picture(self, image_bytes, host, port):
        # Establish a TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            # Send the size of the image data
            s.sendall(len(image_bytes).to_bytes(4, byteorder='big'))

            # Send the image data
            s.sendall(image_bytes)

    def capture_image(self):
        if hasattr(self, 'cap'):
            ret, frame = self.cap.read()
            if ret:
                # Convert frame to bytes and send to server
                _, img_bytes = cv2.imencode('.jpg', frame)
                # self.send_data(img_bytes)

                # Save the captured image to a folder with timestamp
                folder_path = "captured_images_client"
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
        folder_path = "captured_audio_client"
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

    def send_data(self, data):
        host = self.IP_entry.get()
        port = int(self.port_entry.get())

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((host, port))
                client_socket.sendall(data)
                self.status_label.config(text="Data sent to server")
            except Exception as e:
                self.status_label.config(text=f"Error: {e}")
            self.root.update()

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
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
