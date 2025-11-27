# game.py - HOÀN CHỈNH VỚI FIX
import pygame
import json
import threading
import queue
import time

pygame.init()
CELL_SIZE = 40
BOARD_SIZE = 15
WIDTH = CELL_SIZE * BOARD_SIZE + 220
HEIGHT = CELL_SIZE * BOARD_SIZE + 100
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

BG_COLOR = (245, 222, 179)
LINE_COLOR = (0, 0, 0)
X_COLOR = (200, 30, 60)
O_COLOR = (30, 100, 255)
PANEL_COLOR = (20, 30, 70)
PANEL_BORDER = (100, 180, 255)

def get_font(size, bold=False):
    return pygame.font.SysFont("Segoe UI", size, bold=bold)

f_title = get_font(42, True)
f_big = get_font(36, True)
f_med = get_font(30)
f_win = get_font(90, True)

def draw_board(board):
    screen.fill(BG_COLOR)
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, (60, 60 + i*CELL_SIZE), 
                         (60 + BOARD_SIZE*CELL_SIZE, 60 + i*CELL_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR, (60 + i*CELL_SIZE, 60), 
                         (60 + i*CELL_SIZE, 60 + BOARD_SIZE*CELL_SIZE), 2)
    
    for y in range(15):
        for x in range(15):
            center_x = 60 + x * CELL_SIZE + CELL_SIZE // 2
            center_y = 60 + y * CELL_SIZE + CELL_SIZE // 2
            if board[y][x] == 1:
                pygame.draw.line(screen, X_COLOR, (center_x-18, center_y-18), 
                                (center_x+18, center_y+18), 10)
                pygame.draw.line(screen, X_COLOR, (center_x-18, center_y+18), 
                                (center_x+18, center_y-18), 10)
            elif board[y][x] == 2:
                pygame.draw.circle(screen, O_COLOR, (center_x, center_y), 20, 9)

def check_win(board, x, y, player):
    dirs = [(1,0), (0,1), (1,1), (1,-1)]
    for dx, dy in dirs:
        count = 1
        for i in range(1, 5):
            nx, ny = x + dx*i, y + dy*i
            if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                break
            count += 1
        for i in range(1, 5):
            nx, ny = x - dx*i, y - dy*i
            if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                break
            count += 1
        if count >= 5:
            return True
    return False

def main(player_name, room_code, client_socket, names, player_index):
    # Đảm bảo socket ở chế độ blocking
    client_socket.setblocking(True)
    
    # Đợi một chút để menu listener dừng hoàn toàn
    time.sleep(0.5)
    
    board = [[0] * 15 for _ in range(15)]
    my_symbol = 1 if player_index == 0 else 2
    opponent_name = names[1] if player_index == 0 else names[0]
    my_turn = (player_index == 0)
    game_over = False
    winner_name = ""
    msg_queue = queue.Queue()
    stop_listener = False

    def listener():
        nonlocal stop_listener
        buffer = ""
        
        print("[GAME] 🎧 Listener bắt đầu...")
        
        while not stop_listener and client_socket:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    print("[GAME] 🔌 Server đóng kết nối")
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        msg = json.loads(line)
                        
                        # Bỏ qua message 'start' và 'joined' vì đã xử lý ở menu
                        if msg['type'] in ['start', 'joined']:
                            print(f"[GAME] ⏭️  Bỏ qua message: {msg['type']}")
                            continue
                        
                        print(f"[GAME] 📩 Nhận: {msg}")
                        msg_queue.put(msg)
                    except Exception as e:
                        print(f"[GAME] ❌ Parse error: {e}, data: {line}")
                        continue
                        
            except Exception as e:
                if not stop_listener:
                    print(f"[GAME] ❌ Socket error: {e}")
                break
        
        print("[GAME] 🔇 Listener đã dừng")

    threading.Thread(target=listener, daemon=True).start()
    print(f"[GAME] 🚀 Game bắt đầu - Player {player_index}, Symbol: {'X' if my_symbol==1 else 'O'}")
    
    running = True
    while running:
        while True:
            try:
                msg = msg_queue.get_nowait()
                
                if msg['type'] == 'move':
                    opp_symbol = 3 - my_symbol
                    board[msg['y']][msg['x']] = opp_symbol
                    print(f"[GAME] ♟️  Đối thủ đánh: ({msg['x']}, {msg['y']})")
                    if check_win(board, msg['x'], msg['y'], opp_symbol):
                        game_over = True
                        winner_name = opponent_name
                        print(f"[GAME] 🏆 {opponent_name} thắng!")
                    my_turn = True
                
                elif msg['type'] == 'win':
                    game_over = True
                    winner_name = msg['winner']
                    print(f"[GAME] 🏆 {msg['winner']} thắng!")
                
                elif msg['type'] == 'opponent_left':
                    game_over = True
                    winner_name = player_name + " (Đối thủ rời)"
                    print("[GAME] 👋 Đối thủ đã rời")
                    
            except queue.Empty:
                break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_listener = True
            
            if event.type == pygame.MOUSEBUTTONDOWN and my_turn and not game_over:
                mx, my = event.pos
                if 60 <= mx <= 60 + BOARD_SIZE * CELL_SIZE and 60 <= my <= 60 + BOARD_SIZE * CELL_SIZE:
                    col = (mx - 60) // CELL_SIZE
                    row = (my - 60) // CELL_SIZE
                    
                    if board[row][col] == 0:
                        board[row][col] = my_symbol
                        print(f"[GAME] ♟️  Bạn đánh: ({col}, {row})")
                        
                        move_msg = {'type': 'move', 'x': col, 'y': row}
                        try:
                            msg_str = json.dumps(move_msg) + '\n'
                            client_socket.send(msg_str.encode())
                            print(f"[GAME] 📤 Gửi move: ({col}, {row})")
                        except Exception as e:
                            print(f"[GAME] ❌ Lỗi gửi move: {e}")
                        
                        if check_win(board, col, row, my_symbol):
                            game_over = True
                            winner_name = player_name
                            print(f"[GAME] 🏆 Bạn thắng!")
                            win_msg = {'type': 'win', 'winner': player_name}
                            try:
                                win_str = json.dumps(win_msg) + '\n'
                                client_socket.send(win_str.encode())
                            except Exception as e:
                                print(f"[GAME] ❌ Lỗi gửi win: {e}")
                        
                        my_turn = False

        draw_board(board)
        
        panel = pygame.Rect(WIDTH-210, 10, 200, HEIGHT-20)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=25)
        pygame.draw.rect(screen, PANEL_BORDER, panel, 6, border_radius=25)
        
        y_pos = 50
        screen.blit(f_title.render("CỜ CARO", True, (255, 215, 0)), (WIDTH - 200, y_pos)); y_pos += 55
        screen.blit(f_med.render(f"Phòng: {room_code}", True, (180, 255, 180)), (WIDTH - 200, y_pos)); y_pos += 50
        screen.blit(f_med.render(f"Bạn: {player_name}", True, (100, 255, 150)), (WIDTH - 200, y_pos)); y_pos += 50
        screen.blit(f_med.render(f"Đối thủ: {opponent_name}", True, (255, 120, 120)), (WIDTH - 200, y_pos)); y_pos += 50
        
        symbol_text = f_big.render("X" if my_symbol==1 else "O", True, X_COLOR if my_symbol==1 else O_COLOR)
        screen.blit(symbol_text, (WIDTH - 110, y_pos)); y_pos += 70
        
        if game_over:
            status = "KẾT THÚC!"
            status_col = (255, 215, 0)
        elif my_turn:
            status = "LƯỢT CỦA BẠN!"
            status_col = (0, 255, 0)
            if int(pygame.time.get_ticks() / 300) % 2:
                status_col = (50, 255, 50)
        else:
            status = "ĐỢI ĐỐI THỦ..."
            status_col = (255, 200, 0)
        
        status_surf = f_big.render(status, True, status_col)
        screen.blit(status_surf, (WIDTH - 200, 380))
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            win_text = f"{winner_name} THẮNG!"
            win_surf = f_win.render(win_text, True, (255, 215, 0))
            screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 100))
            
            again = f_med.render("Đóng cửa sổ để về menu", True, (200, 200, 200))
            screen.blit(again, (WIDTH//2 - again.get_width()//2, HEIGHT//2 + 20))

        pygame.display.flip()
        clock.tick(60)

    stop_listener = True
    print("[GAME] 🛑 Game kết thúc")
    try:
        client_socket.close()
    except:
        pass