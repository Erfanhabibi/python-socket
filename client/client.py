# Client code to send an image and a voice message
import socket
import wave
import pyaudio

# Server address and port numbers
server_address = ('localhost', 10001)
voice_server_address = ('localhost', 10002)

# Function to send an image


def send_image(sock, image_path):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        sock.sendall(image_data)

# Function to send a voice message


def send_voice(sock, voice_path):
    wf = wave.open(voice_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(1024)
    while data != '':
        sock.sendall(data)
        data = wf.readframes(1024)
    stream.stop_stream()
    stream.close()
    p.terminate()


# Create sockets
image_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
voice_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the image server
image_sock.connect(server_address)
# Connect to the voice server
voice_sock.connect(voice_server_address)

try:
    # Send image
    send_image(image_sock, 'path_to_image.jpg')
    # Send voice
    send_voice(voice_sock, 'path_to_voice.wav')
finally:
    image_sock.close()
    voice_sock.close()
