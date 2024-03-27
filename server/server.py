
# Server code to receive an image and a voice message
import socket
import wave
import pyaudio

# Server address and port numbers
server_address = ('localhost', 10001)
voice_server_address = ('localhost', 10002)

# Function to receive an image


def receive_image(sock, image_path):
    with open(image_path, 'wb') as image_file:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            image_file.write(data)

# Function to receive a voice message


def receive_voice(sock, voice_path):
    wf = wave.open(voice_path, 'wb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True)
    while True:
        data = sock.recv(1024)
        if not data:
            break
        wf.writeframes(data)
    stream.stop_stream()
    stream.close()
    p.terminate()


# Create sockets
image_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
voice_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the sockets
image_server_sock.bind(server_address)
voice_server_sock.bind(voice_server_address)

# Listen for incoming connections
image_server_sock.listen(1)
voice_server_sock.listen(1)

# Accept connections
image_connection, _ = image_server_sock.accept()
voice_connection, _ = voice_server_sock.accept()

try:
    # Receive image
    receive_image(image_connection, 'received_image.jpg')
    # Receive voice
    receive_voice(voice_connection, 'received_voice.wav')
finally:
    image_connection.close()
    voice_connection.close()
