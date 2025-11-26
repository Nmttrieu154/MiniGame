# server.py - HOÀN CHỈNH
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
    if room_code not in rooms: 
        return
    
    print(f"📤 Gửi đến phòng {room_code}: {data}")
    for i, client in enumerate(rooms[room_code][:2]):
        if client and client != exclude:
            try:
                message = json.dumps(data, ensure_ascii=False) + '\n'
                client.send(message.encode('utf-8'))
                print(f"  ✅ Đã gửi đến Player {i}")
            except Exception as e:
                print(f"  ❌ Lỗi gửi đến Player {i}: {e}")

def handle_client(conn, addr):
    print(f"🔗 Kết nối mới: {addr}")
    room_code = None
    buffer = ""
    
    try:
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data: 
                    print(f"🔌 {addr} đóng kết nối")
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if not line.strip():
                        continue
                    
                    try:
                        msg = json.loads(line)
                        print(f"📥 Nhận từ {addr}: {msg}")
                        
                        if msg['type'] == 'join':
                            room_code = msg['room']
                            name = msg['name']
                            
                            if room_code not in rooms:
                                rooms[room_code] = [None, None, ["", ""]]
                                print(f"📦 Tạo phòng mới: {room_code}")
                            
                            if rooms[room_code][0] is None:
                                rooms[room_code][0] = conn
                                rooms[room_code][2][0] = name
                                response = {'type':'joined','player':0}
                                conn.send((json.dumps(response, ensure_ascii=False) + '\n').encode())
                                print(f"✅ {name} → Player 0")
                                
                            elif rooms[room_code][1] is None:
                                rooms[room_code][1] = conn
                                rooms[room_code][2][1] = name
                                response = {'type':'joined','player':1}
                                conn.send((json.dumps(response, ensure_ascii=False) + '\n').encode())
                                print(f"✅ {name} → Player 1")
                                
                                time.sleep(0.3)
                                start_msg = {'type':'start', 'names': rooms[room_code][2]}
                                broadcast(room_code, start_msg)
                                print(f"🎮 Bắt đầu game: {rooms[room_code][2]}")
                            else:
                                conn.send((json.dumps({'type':'full'}, ensure_ascii=False) + '\n').encode())
                                conn.close()
                                return
                        
                        elif msg['type'] == 'move':
                            print(f"♟️  {addr} đánh: ({msg['x']}, {msg['y']})")
                            broadcast(room_code, {'type':'move', 'x':msg['x'], 'y':msg['y']}, conn)
                        
                        elif msg['type'] == 'win':
                            print(f"🏆 {msg['winner']} thắng!")
                            broadcast(room_code, {'type':'win', 'winner':msg['winner']})
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Lỗi JSON từ {addr}: {e}")
                        continue
                        
            except ConnectionResetError:
                print(f"🔌 {addr} mất kết nối đột ngột")
                break
            except Exception as e:
                print(f"❌ Lỗi xử lý {addr}: {e}")
                break
                
    except Exception as e:
        print(f"❌ Lỗi handler {addr}: {e}")
    
    print(f"🔚 Ngắt kết nối: {addr} (room: {room_code})")
    if room_code and room_code in rooms:
        # Chỉ gửi thông báo opponent_left nếu còn người chơi khác trong phòng
        other_player_exists = False
        if conn == rooms[room_code][0]:
            rooms[room_code][0] = None
            if rooms[room_code][1] is not None:
                other_player_exists = True
        elif conn == rooms[room_code][1]:
            rooms[room_code][1] = None
            if rooms[room_code][0] is not None:
                other_player_exists = True
        
        if other_player_exists:
            broadcast(room_code, {'type':'opponent_left'})
        
        # Xóa phòng nếu cả 2 đều thoát
        if rooms[room_code][0] is None and rooms[room_code][1] is None:
            del rooms[room_code]
            print(f"🗑️  Đã xóa phòng: {room_code}")
    
    try:
        conn.close()
    except:
        pass

print("="*50)
print("🚀 Server Caro - 127.0.0.1:5555")
print("="*50)

while True:
    try:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except Exception as e:
        print(f"❌ Lỗi accept: {e}")