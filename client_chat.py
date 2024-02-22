import socket
import threading

# Client code adjustments:
# - Make sure to cleanly exit the receive thread after sending a "quit" message.
# - Ensure the client exits gracefully without causing exceptions on the server.

def receive_messages(sock):
    try:
        while True:
            message = sock.recv(1024).decode()
            if message == "quit":
                print("Exiting chat.")
                break
            print(f"Received: {message}")
    except Exception as e:
        print("Connection closed by the server.")
    finally:
        if sock.close() == False:
            sock.close()

def send_messages(sock):
    try:
        while True:
            message = input()
            sock.sendall(message.encode())
            if message.strip().lower() == "quit":
                break
    except Exception as e:
        print("Error sending message.")
    finally:
        if sock.close() == False:
            sock.close()

def start_client(server_host='127.0.0.1', server_port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_host, server_port))
        print("Connected to the chat server.")
        
        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
        send_messages(sock)

if __name__ == "__main__":
    start_client()
