import socket
import threading

HOST = '0.0.0.0'
PORT = 8081

clients = {}  # socket -> nickname
lock = threading.Lock()


def broadcast(message):
    """Відправка повідомлення всім клієнтам"""
    with lock:
        for client in list(clients.keys()):
            try:
                client.send(message.encode('utf-8'))
            except:
                try:
                    client.close()
                except:
                    pass
                remove_client(client)


def broadcast_user_list():
    """Розсилка списку користувачів"""
    with lock:
        users = ",".join(clients.values())
    broadcast("USERS:" + users)


def remove_client(sock):
    """Видаляє клієнта зі списку"""
    with lock:
        if sock in clients:
            nickname = clients[sock]
            del clients[sock]
        else:
            nickname = None

    if nickname:
        print(f"[Відключився] {nickname}")
        broadcast(f"MSG:⚠️ {nickname} вийшов із чату")
        broadcast_user_list()


def handle_client(sock, addr):
    try:
        nickname = sock.recv(1024).decode('utf-8').strip()
        if not nickname:
            nickname = f"User{addr[1]}"
        with lock:
            clients[sock] = nickname

        print(f"[Підключився] {nickname} з {addr}")
        broadcast(f"MSG:✅ {nickname} приєднався до чату")
        broadcast_user_list()

        while True:
            data = sock.recv(4096)
            if not data:
                break
            message = data.decode('utf-8').strip()
            print(f"[{nickname}] {message}")
            broadcast(f"MSG:{nickname}: {message}")
    except Exception as e:
        # для дебагу можна розкоментувати
        # print("Client handler error:", e)
        pass
    finally:
        remove_client(sock)
        try:
            sock.close()
        except:
            pass


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Сервер запущено] {HOST}:{PORT}")

    try:
        while True:
            sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(sock, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Сервер зупинено")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
