# Client code to send an image and receive a thank you message
import socket

# Create the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('localhost', 10001)
sock.connect(server_address)

try:
    # Open the image file in binary read mode
    with open('path_to_image.jpg', 'rb') as image_file:
        # Read the image data
        image_data = image_file.read()

        # Send the image data to the server
        sock.sendall(image_data)

    # Receive the thank you message from the server
    thank_you_message = sock.recv(1024)
    print(thank_you_message.decode('UTF-8'))
finally:
    # Close the socket
    sock.close()
