import socket
import threading

HOST = "0.0.0.0"
PORT = 65432
users = []
user_id = 0
lock = threading.Lock()


def broadcast(message, sender_conn):
    with lock:
        for conn, _ in users:
            if conn != sender_conn:
                try:
                    conn.sendall(message)
                except:
                    pass


def handle_client(conn, addr, uid):
    print(f"Connected by {addr}, Hello user{addr}")

    with lock:
        users.append((conn, uid))

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = f"User {uid}: {data.decode('utf-8')}"
            print(message)

            broadcast(message.encode("utf-8"), conn)
    
    finally:
        with lock:
            users.remove((conn, uid))

        conn.close()
        print(f"User {uid} disconnected")


def main():
    global user_id
    global users

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server running...")

        while True:
            conn, addr = s.accept()

            with lock:
                uid = user_id
                user_id += 1
        
            thread = threading.Thread(
                target=handle_client,
                args=(conn, addr, uid)
            )
            thread.start()


class User:
    def __init__(self, id):
        self.id = id


def create_user(id) -> User:
    user = User(id)
    return user




main()