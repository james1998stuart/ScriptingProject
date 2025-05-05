import socket

def wait_for_success():
    host = '127.0.0.1'
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print("🟡 Waiting for success signal...")
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if data == b'Success':
                print("🟢 Python script completed successfully!")

if __name__ == "__main__":
    wait_for_success()
