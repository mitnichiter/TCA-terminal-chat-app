# server.py

import socket
import threading

# --- Server Configuration ---
# Use '0.0.0.0' to be accessible from any computer on the network
HOST = '0.0.0.0'
PORT = 12345

# --- Global State ---
# Dictionary to store connected clients: {username: client_socket}
clients = {}
# List to store the running chat history
chat_history = []
# A lock to ensure that 'clients' and 'chat_history' are accessed safely by threads
lock = threading.Lock()

def broadcast(message, sender_username=None):
    """
    Sends a message to all clients and saves it to history.
    If a sender_username is provided, the message is not sent back to the sender.
    """
    with lock:
        # Add the message to our chat history so new users can see it
        chat_history.append(message)
        # Iterate over a copy of the clients dictionary's items
        # This prevents issues if a client disconnects during the broadcast
        for username, client_socket in list(clients.items()):
            if username != sender_username:
                try:
                    client_socket.send(message.encode('utf-8'))
                except BrokenPipeError:
                    # If sending fails, the client has likely disconnected.
                    # We will handle the cleanup in the handle_client function.
                    pass
                except Exception as e:
                    print(f"[ERROR] Could not send message to {username}: {e}")

def handle_client(client_socket, addr):
    """
    Handles a single client connection from start to finish.
    """
    username = None
    try:
        # The very first message from the client must be their username
        username = client_socket.recv(1024).decode('utf-8').strip()
        if not username:
            # If the client provides an empty username, disconnect them.
            raise ConnectionError("Client did not provide a valid username.")

        with lock:
            # Add the new client to our dictionary of online users
            clients[username] = client_socket

        print(f"[NEW CONNECTION] {addr} connected and registered as: {username}")

        # Send existing chat history to the newly connected client
        with lock:
            welcome_msg = f"--- Welcome to the Chat, {username}! ---\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            for msg in chat_history:
                client_socket.send(msg.encode('utf-8'))
        
        # Announce the new user's arrival to all other clients
        broadcast(f"[SYSTEM] {username} has joined the chat.\n", sender_username=username)

        # Main loop to listen for messages from this client
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # Format the message to include who sent it
                formatted_message = f"{username}: {message}\n"
                print(f"Broadcasting from {username}: {message.strip()}")
                # Broadcast the message to all other clients
                broadcast(formatted_message, sender_username=username)
            else:
                # An empty message means the client disconnected cleanly
                break
    
    except (ConnectionResetError, ConnectionError, BrokenPipeError):
        # This block catches various ways a client might disconnect
        print(f"[CONNECTION LOST] {addr} (user: {username}) disconnected.")
    except Exception as e:
        print(f"[ERROR] An error occurred with {username}: {e}")
    finally:
        # This block always runs, ensuring cleanup happens
        if username and username in clients:
            with lock:
                # Remove the client from the dictionary of online users
                del clients[username]
            # Announce that the user has left
            broadcast(f"[SYSTEM] {username} has left the chat.\n")
            print(f"[CONNECTION CLOSED] User {username} has been removed.")
        
        # Close the socket connection to the client
        client_socket.close()

def start_server():
    """
    Initializes and starts the chat server, listening for new clients.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # This option allows the server to reuse the address, preventing the "Address already in use" error
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((HOST, PORT))
    server.listen(10) # Allow a queue of up to 10 connections
    print(f"[*] Server is live and listening on {HOST}:{PORT}")

    while True:
        try:
            # Wait for a new client to connect
            client_socket, addr = server.accept()
            # Create a new thread to handle this client so the main loop can accept others
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Server is shutting down.")
            break
    
    server.close()

if __name__ == "__main__":
    start_server()
