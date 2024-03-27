# Server code to receive an image and send a thank you message
import socket

# Create the socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the localhost:10001
server_address = ('localhost', 10001)
server_sock.bind(server_address)

# Listen for incoming connections
server_sock.listen(1)

try:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = server_sock.accept()
    print('connection from', client_address)

    # Receive the data in small chunks and write it to a file
    with open('received_image.jpg', 'wb') as image_file:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            image_file.write(data)

    # Send a thank you message to the client
    thank_you_message = 'Thank you for the image!'
    connection.sendall(thank_you_message.encode('UTF-8'))
finally:
    # Clean up the connection
    connection.close()
