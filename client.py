import tkinter as tk
import socket
import cv2
import pyaudio
import wave
import os
from PIL import Image, ImageTk
from datetime import datetime


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

        self.photo_port_label = tk.Label(self.root, text="Enter Photo Port:")
        self.photo_port_label.pack()
        self.photo_port_entry = tk.Entry(self.root)
        self.photo_port_entry.pack()

        self.audio_port_label = tk.Label(self.root, text="Enter Audio Port:")
        self.audio_port_label.pack()
        self.audio_port_entry = tk.Entry(self.root)
        self.audio_port_entry.pack()

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

        # Create a label to display the webcam feed
        self.webcam_label = tk.Label(self.root)
        self.webcam_label.pack()

        # Start webcam feed
        self.start_webcam()

        # Create a button to close the app
        self.close_button = tk.Button(
            self.root, text="Close", command=self.close_app)
        self.close_button.pack()

        self.photo_socket = None
        self.audio_socket = None

    def connect_to_server(self):
        try:
            host = self.IP_entry.get()
            photo_port = int(self.photo_port_entry.get())
            audio_port = int(self.audio_port_entry.get())

            self.photo_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.photo_socket.connect((host, photo_port))

            self.audio_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.audio_socket.connect((host, audio_port))

            self.status_label.config(text="Connected to server")

            
            # Enable capture image and record audio buttons
            self.capture_button.config(state=tk.NORMAL)
            self.record_button.config(state=tk.NORMAL)
            self.receive_image.config(state=tk.NORMAL)
            self.receive_voice.config(state=tk.NORMAL)
            self.root.update()

        except Exception as e:
            self.status_label.config(
                text=f"Error connecting to server: {str(e)}")

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

    def send_data(self, socket, data):
        try:
            if socket:
                socket.sendall(data)
            else:
                self.status_label.config(text="Not connected to server")
        except Exception as e:
            self.status_label.config(
                text=f"Error sending data to server: {str(e)}")

    def capture_image(self):
        if hasattr(self, 'cap'):
            ret, frame = self.cap.read()
            if ret:
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

                # Convert frame to bytes
                with open(image_path, 'rb') as img_file:
                    img_bytes = img_file.read()

                # Send image data to the server
                self.send_data(self.photo_socket, b'IMG' + img_bytes)
        else:
            self.status_label.config(text="Webcam not available")

    def record_audio(self):
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

        # Convert audio file to bytes
        with open(audio_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()

        # Send audio data to the server
        self.send_data(self.audio_socket, b'AUDIO' + audio_bytes)

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
        if self.photo_socket:
            self.photo_socket.close()
        if self.audio_socket:
            self.audio_socket.close()
        if hasattr(self, 'cap'):
            self.cap.release()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
