# client_termux.py (Bish bish bish bish I love you version)

import socket
import threading
import curses
import os # We'll use this to call the Termux command

# --- Client Configuration ---
# IMPORTANT: Change this to the IP address of the computer running server.py
# Example: SERVER_HOST = '192.168.1.15'
SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 12345

def send_termux_notification(title, message):
    """Sends a native Android notification via the Termux:API."""
    try:
        # Construct the command-line call for the termux-notification tool
        # The -t is for title, -c is for content
        command = f'termux-notification -t "{title}" -c "{message}"'
        os.system(command) # Execute the command
    except Exception:
        # If the termux-api is not installed or not working, this will fail silently.
        pass

def receive_messages(client_socket, chat_win, own_username):
    """Listens for incoming messages and displays them."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            chat_win.addstr(message)
            chat_win.refresh()

            # If the message is from another user, send a Termux notification
            if ':' in message:
                sender_username = message.split(':', 1)[0]
                if sender_username != own_username and "[SYSTEM]" not in sender_username:
                    send_termux_notification(
                        title=f"New message from {sender_username}",
                        message=message.split(':', 1)[1].strip()
                    )
        except (curses.error, Exception):
            break

def main(stdscr):
    """The main function that sets up the UI and runs the chat client."""
    curses.curs_set(1)
    
    default_color = curses.A_NORMAL
    try:
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, -1, -1) 
            default_color = curses.color_pair(1)
            stdscr.bkgd(' ', default_color)
    except Exception:
        pass

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    stdscr.addstr(0, 0, "Enter your username: ", default_color)
    curses.echo()
    stdscr.refresh()
    username_bytes = stdscr.getstr(0, 22, 30)
    username = username_bytes.decode('utf-8', 'ignore').strip()
    curses.noecho()
    stdscr.clear()

    chat_win = curses.newwin(height - 3, width, 0, 0)
    chat_win.scrollok(True)
    chat_win.bkgd(' ', default_color)

    input_win = curses.newwin(3, width, height - 3, 0)
    input_win.box()
    input_win.bkgd(' ', default_color)
    
    stdscr.refresh()
    input_win.refresh()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        client.send(username.encode('utf-8'))
    except Exception as e:
        chat_win.addstr(f"Failed to connect to {SERVER_HOST}:{SERVER_PORT}\nError: {e}\n", default_color)
        chat_win.refresh()
        input_win.getch()
        return

    threading.Thread(target=receive_messages, args=(client, chat_win, username), daemon=True).start()

    current_message = ""
    while True:
        try:
            prompt = f"You > "
            input_win.clear()
            input_win.box()
            input_win.addstr(1, 1, prompt + current_message, default_color)
            input_win.refresh()
            
            key = input_win.getkey()

            if key == '\n':
                if current_message:
                    client.send(current_message.encode('utf-8'))
                    chat_win.addstr(f"{username}: {current_message}\n", default_color)
                    chat_win.refresh()
                    current_message = ""
            elif key == '\x7f' or key == curses.KEY_BACKSPACE or key == '\b':
                current_message = current_message[:-1]
            elif len(key) == 1 and key.isprintable():
                current_message += key
        except KeyboardInterrupt:
            break
        except Exception:
            pass
    
    client.close()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    finally:
        print("Chat client has been closed.")
