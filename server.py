# server.py
import socket
import threading
import pickle
import time

HOST = "127.0.0.1"
PORT = 65432

BOARD_SIZE = 15
WIN_COUNT = 5

clients = []  # list of (conn, addr, symbol)
board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
current_player = 'X'
lock = threading.Lock()
game_over = False

def check_winner():
    # trả về 'X' hoặc 'O' nếu có thắng, 'Draw' nếu hòa, None nếu chưa kết thúc
    dirs = [(1,0),(0,1),(1,1),(1,-1)]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == '':
                continue
            p = board[r][c]
            for dr, dc in dirs:
                count = 1
                for k in range(1, WIN_COUNT):
                    rr = r + dr*k
                    cc = c + dc*k
                    if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and board[rr][cc] == p:
                        count += 1
                    else:
                        break
                if count >= WIN_COUNT:
                    return p
    if all(board[r][c] != '' for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
        return 'Draw'
    return None

def send_obj(conn, obj):
    try:
        data = pickle.dumps(obj)
        conn.sendall(data)
        return True
    except Exception:
        return False

def broadcast_state():
    obj = {'type':'update', 'board': board, 'current': current_player, 'game_over': game_over}
    for conn, addr, sym in clients:
        try:
            send_obj(conn, obj)
        except Exception:
            # will be cleaned on recv loop
            pass

def handle_client(conn, addr, symbol):
    global current_player, game_over
    print(f"[+] Client {addr} connected as {symbol}")
    # send initial assignment
    init = {'type':'init', 'symbol': symbol, 'board': board, 'current': current_player, 'game_over': game_over}
    if not send_obj(conn, init):
        conn.close()
        return

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                print(f"[-] {addr} disconnected")
                break
            try:
                msg = pickle.loads(data)
            except Exception:
                # ignore malformed
                continue

            if msg.get('type') == 'move':
                x = msg.get('x')
                y = msg.get('y')
                sym = msg.get('symbol')
                with lock:
                    if game_over:
                        # send back info
                        send_obj(conn, {'type':'error','msg':'Trò chơi đã kết thúc.'})
                        continue
                    if sym != current_player:
                        send_obj(conn, {'type':'error','msg':'Chưa tới lượt bạn.'})
                        continue
                    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                        send_obj(conn, {'type':'error','msg':'Toạ độ không hợp lệ.'})
                        continue
                    if board[y][x] != '':
                        send_obj(conn, {'type':'error','msg':'Ô đã có quân.'})
                        continue
                    # hợp lệ -> đặt quân
                    board[y][x] = sym
                    # kiểm tra thắng
                    winner = check_winner()
                    if winner:
                        game_over = True
                        # broadcast kết quả
                        broadcast_state()
                        result_obj = {'type':'result', 'winner': winner}
                        for c, a, s in clients:
                            send_obj(c, result_obj)
                    else:
                        # đổi lượt
                        current_player = 'O' if current_player == 'X' else 'X'
                        broadcast_state()
            # other message types can be added
    except ConnectionResetError:
        print(f"[-] ConnectionReset {addr}")
    except Exception as e:
        print("Lỗi handle_client:", e)
    finally:
        conn.close()
        # remove client from list
        for i, (c, a, s) in enumerate(clients):
            if c is conn:
                clients.pop(i)
                break
        print(f"[-] Cleaned up client {addr}")

def start_server():
    print("Server starting...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")

    # assign symbols in order X then O
    try:
        while True:
            conn, addr = s.accept()
            symbol = 'X' if len(clients) == 0 else 'O'
            clients.append((conn, addr, symbol))
            threading.Thread(target=handle_client, args=(conn, addr, symbol), daemon=True).start()
            # once two players connected, broadcast state (assignment already sent in handler)
            time.sleep(0.1)
            broadcast_state()
    except KeyboardInterrupt:
        print("Server stopping...")
    finally:
        s.close()
        for c, a, sbl in clients:
            try:
                c.close()
            except:
                pass

if __name__ == "__main__":
    start_server()
