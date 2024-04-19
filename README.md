# Server-Client Communication System

This project implements a server-client communication system using Python's sockets for transferring images and audio data.

## Server

The server application utilizes Tkinter for the graphical user interface (GUI) and OpenCV for capturing images from the webcam. It also uses PyAudio for recording audio. The server waits for client connections and can receive images and audio data from clients.

### Prerequisites
- Python 3.x
- OpenCV (`pip install opencv-python`)
- PyAudio (`pip install pyaudio`)
- Pillow (`pip install Pillow`)

### Usage
1. Run the `server.py` script.
2. Click on the "Start Server" button to initialize the server.
3. The server will display its IP address and port numbers for photo and audio communication.
4. Once connected to a client, you can capture images and record audio by clicking the respective buttons.
5. Received images and audio files will be saved in the `captured_images_server` and `captured_audio_server` folders, respectively.

## Client

The client application is responsible for sending images and audio data to the server. It can be implemented separately.

### Prerequisites
- Python 3.x

### Usage
1. Implement the client code based on the provided server IP address and port numbers.
2. Connect the client to the server.
3. Send images or audio data to the server as needed.

## Folder Structure
- `captured_images_server`: Contains images captured by the server.
- `captured_audio_server`: Contains audio recordings made by the server.

## Notes
- Make sure to have proper network configurations to allow communication between the server and clients.
- Adjust the IP address and port numbers in the code to match your network setup.

