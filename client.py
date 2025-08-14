# client.py (Final Version)

import socket
import threading
import curses
from plyer import notification

# --- Client Configuration ---
# IMPORTANT: Change this to the IP address of the computer running server.py
# Example: SERVER_HOST = '192.168.1.15'
SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 12345

def send_toast_notification(title, message):
    """Sends a desktop notification. Fails silently if unable."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='PyTerminal-Chat',
            timeout=10  # Notification will disappear after 10 seconds
        )
    except Exception:
        # This can fail if the OS notification system is not available.
        # We pass silently so the app doesn't crash.
        pass

def receive_messages(client_socket, chat_win, own_username):
    """Listens for incoming messages from the server and displays them."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break # Server has closed the connection
            
            # Display the message in the chat window
            chat_win.addstr(message)
            chat_win.refresh()

            # Send a desktop notification if the message is from another user
            if ':' in message: # A simple check to see if it's a user message
                sender_username = message.split(':', 1)[0]
                if sender_username != own_username and "[SYSTEM]" not in sender_username:
                    send_toast_notification(
                        title=f"New message from {sender_username}",
                        message=message.split(':', 1)[1].strip()
                    )
        except (curses.error, Exception):
            # Curses error can happen if the window is resized.
            # Other exceptions mean the connection is likely lost.
            break

def main(stdscr):
    """The main function that sets up the UI and runs the chat client."""
    # --- Curses and Color Setup ---
    curses.curs_set(1) # Make the cursor visible
    
    # Use a try-except block for robust color handling
    default_color = curses.A_NORMAL
    try:
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors() # <-- This is the key for terminal colors
            # Initialize color pair 1 with the terminal's default fg and bg
            curses.init_pair(1, -1, -1) 
            default_color = curses.color_pair(1)
            stdscr.bkgd(' ', default_color)
    except Exception:
        pass # If color setup fails, just continue in default black and white.

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # --- Username Input ---
    stdscr.addstr(0, 0, "Enter your username and press Enter: ", default_color)
    curses.echo() # Show characters as they are typed
    stdscr.refresh()
    # Get user input from the screen
    username_bytes = stdscr.getstr(0, 34, 30)
    username = username_bytes.decode('utf-8', 'ignore').strip()
    curses.noecho() # Turn off character echoing for the chat input
    stdscr.clear()

    # --- UI Windows Setup ---
    chat_win = curses.newwin(height - 3, width, 0, 0)
    chat_win.scrollok(True)
    chat_win.bkgd(' ', default_color)

    input_win = curses.newwin(3, width, height - 3, 0)
    input_win.box()
    input_win.bkgd(' ', default_color)
    
    stdscr.refresh()
    input_win.refresh()

    # --- Network Connection ---
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        client.send(username.encode('utf-8'))
    except Exception as e:
        chat_win.addstr(f"Failed to connect to server at {SERVER_HOST}:{SERVER_PORT}. Is it running?\nError: {e}\n", default_color)
        chat_win.refresh()
        input_win.getch() # Wait for user input before exiting
        return

    # Start a separate thread to listen for messages from the server
    threading.Thread(target=receive_messages, args=(client, chat_win, username), daemon=True).start()

    # --- Main Input Loop ---
    current_message = ""
    while True:
        try:
            # Refresh the input line prompt
            prompt = f"You > "
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 1, prompt + current_message, default_color)
            input_win.refresh()
            
            # Get a key from the user
            key = input_win.getkey()

            if key == '\n': # Enter key
                if current_message:
                    client.send(current_message.encode('utf-8'))
                    # Display our own message in the chat window immediately
                    chat_win.addstr(f"{username}: {current_message}\n", default_color)
                    chat_win.refresh()
                    current_message = ""
            elif key == '\x7f' or key == curses.KEY_BACKSPACE or key == '\b':
                current_message = current_message[:-1]
            # Filter out non-printable control characters
            elif len(key) == 1 and key.isprintable():
                current_message += key

        except KeyboardInterrupt:
            break
        except Exception:
            # This catches errors from getkey() if no key is pressed
            pass
    
    client.close()

if __name__ == "__main__":
    try:
        # curses.wrapper handles all the terminal setup and safe cleanup
        curses.wrapper(main)
    finally:
        print("Chat client has been closed.")
