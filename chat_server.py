import socket
import threading
import sys

def client_handler(connection, client_address, other_connection, stop_event):
    try:
        while not stop_event.is_set():
            try:
                connection.settimeout(1.0)  # Set a timeout for blocking operations
                message = connection.recv(1024)
                if message:
                    print(f"Received message from {client_address}: {message.decode()}")
                    other_connection.sendall(message)
                else:
                    # Connection closed
                    print(f"Connection with {client_address} closed.")
                    break
            except socket.timeout:
                continue  # Timeout occurred, loop back and check stop_event again
            except Exception as e:
                print(f"Error with {client_address}: {e}")
                break
    finally:
        connection.close()

def start_server(host='0.0.0.0', port=12345):
    stop_event = threading.Event()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)
    print(f"Server started. Listening for connections on {host}:{port}...")

    connections = []
    threads = []

    def accept_connections():
        while not stop_event.is_set():
            server_socket.settimeout(1.0)  # Set a timeout for accept call
            try:
                connection, client_address = server_socket.accept()
            except socket.timeout:
                continue  # Timeout occurred, loop back and check stop_event again
            print(f"Connection from {client_address}")
            connections.append(connection)
            if len(connections) == 2:
                t1 = threading.Thread(target=client_handler, args=(connections[0], 'Client 1', connections[1], stop_event))
                t2 = threading.Thread(target=client_handler, args=(connections[1], 'Client 2', connections[0], stop_event))
                t1.start()
                t2.start()
                threads.extend([t1, t2])

    accept_thread = threading.Thread(target=accept_connections)
    accept_thread.start()

    try:
        while not stop_event.is_set():
            cmd = input()
            if cmd.strip().lower() == "quit":
                print("Quit command received. Shutting down the server.")
                stop_event.set()
                break
    except KeyboardInterrupt:
        print("Server shutdown by KeyboardInterrupt")
        stop_event.set()

    # Wait for the accept thread to terminate
    accept_thread.join()

    # Close all client connections
    for conn in connections:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    # Wait for all client handler threads to terminate
    for t in threads:
        t.join()

    # Finally, close the server socket
    server_socket.close()
    print("Server has been shut down.")

if __name__ == "__main__":
    start_server()
