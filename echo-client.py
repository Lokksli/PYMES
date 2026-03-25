import socket 
import threading

HOST = "192.168.1.107"
PORT = 65432

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break

            print("\r" + data.decode("utf-8"))
            print("Type: ", end="", flush=True)

        except:
            break
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        thread = threading.Thread(target=receive_messages, args=(s,))
        thread.daemon = True
        thread.start()
        
        while True:
            message = input("Type: ")
            if not message:
                break

            s.sendall(message.encode("utf-8"))

          

main()