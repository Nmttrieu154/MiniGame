# server.py - HOÀN CHỈNH (giữ nguyên)
import socket
import threading
import json
import time

HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

rooms = {}

def broadcast(room_code, data, exclude=None):
    if room_code not in rooms: return
    for client in rooms[room_code][:2]:
        if client and client != exclude:
            try:
                client.send(json.dumps(data).encode('utf-8'))
                print(f"  Gửi: {data}")
            except:
                pass

def handle_client(conn, addr):
    print(f"Kết nối: {addr}")
    room_code = None

    while True:
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data: break
            msg = json.loads(data)
            print(f"Nhận: {msg}")

            if msg['type'] == 'join':
                room_code = msg['room']
                name = msg['name']

                if room_code not in rooms:
                    rooms[room_code] = [None, None, ["", ""]]
                    print(f"Phòng mới: {room_code}")

                if rooms[room_code][0] is None:
                    rooms[room_code][0] = conn
                    rooms[room_code][2][0] = name
                    conn.send(json.dumps({'type':'joined','player':0}).encode())
                    print(f"  Player 0 ({name}) vào")
                elif rooms[room_code][1] is None:
                    rooms[room_code][1] = conn
                    rooms[room_code][2][1] = name
                    conn.send(json.dumps({'type':'joined','player':1}).encode())
                    print(f"  Player 1 ({name}) vào")
                    time.sleep(0.1)
                    start_msg = {'type':'start', 'names': rooms[room_code][2]}
                    broadcast(room_code, start_msg)
                    print(f"PHÒNG {room_code} BẮT ĐẦU: {rooms[room_code][2]}")
                else:
                    conn.send(json.dumps({'type':'full'}).encode())
                    conn.close()
                    return

            elif msg['type'] == 'move':
                broadcast(room_code, {'type':'move', 'x':msg['x'], 'y':msg['y']}, conn)

            elif msg['type'] == 'win':
                broadcast(room_code, {'type':'win', 'winner':msg['winner']})

        except Exception as e:
            print(f"Lỗi: {e}")
            break

    print(f"Ngắt kết nối: {addr}")
    if room_code and room_code in rooms:
        broadcast(room_code, {'type':'opponent_left'})
        del rooms[room_code]
    conn.close()

print("="*50)
print("Server chạy tại 127.0.0.1:5555")
print("="*50)

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()