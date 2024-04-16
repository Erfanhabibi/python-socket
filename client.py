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
        self.close_button = tk.Button(self.root, text="Close", command=self.close_app)
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
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imshow('Captured Image', frame)
        cv2.waitKey(2000)  # Wait for 2 seconds
        cv2.destroyAllWindows()

        # Save the captured image to a folder with timestamp
        folder_path = "captured_images_client"
        os.makedirs(folder_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(
            folder_path, f"captured_image_{timestamp}.jpg")
        cv2.imwrite(image_path, frame)
        self.status_label.config(text=f"Image saved: {image_path}")

        # Convert frame to bytes
        _, img_bytes = cv2.imencode('.jpg', frame)
        # Send the picture bytes to the server
        host = self.IP_entry()  # Replace 'server_address' with the actual server address
        port = int(self.port_entry.get())         # Replace 12345 with the actual port number
        self.send_picture(img_bytes, host, port)

        cap.release()
     


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

    def process_data(self, data):
        try:
            # Attempt to open the data as an image
            image = Image.open(io.BytesIO(data))
            # If successful, save the image
            folder_path = "received_images_server"
            os.makedirs(folder_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(
                folder_path, f"received_image_{timestamp}.jpg")
            image.save(image_path)
            self.status_label.config(text=f"Image saved: {image_path}")
        except IOError:
            # If an error occurs, assume the data is audio and save it
            folder_path = "received_audio_server"
            os.makedirs(folder_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.join(folder_path, f"received_audio{timestamp}.wav")
            with open(audio_path, 'wb') as f:
                f.write(data)
            self.status_label.config(text=f"Audio saved: {audio_path}")


    def start_webcam(self):
        # Try different backends to open the webcam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        def update_frame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.webcam_label.img = img
                self.webcam_label.config(image=img)
            self.webcam_label.after(10, update_frame)

        update_frame()
    
    def close_app(self):
        self.root.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
