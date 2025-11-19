# game.py - BẢN FIX LỖI LƯỢT ĐI 100% (TESTED 2025) - KHÔNG CÒN LAG NỮA!
import pygame
import json
import threading
import queue

pygame.init()

CELL_SIZE = 40
BOARD_SIZE = 15
WIDTH = CELL_SIZE * BOARD_SIZE + 220
HEIGHT = CELL_SIZE * BOARD_SIZE + 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Màu sắc đẹp
BG_COLOR     = (245, 222, 179)   # nền gỗ ấm
LINE_COLOR   = (0, 0, 0)
X_COLOR      = (200, 30, 60)
O_COLOR      = (30, 100, 255)
PANEL_COLOR  = (20, 30, 70)
PANEL_BORDER = (100, 180, 255)

def get_font(size, bold=False):
    return pygame.font.SysFont("Segoe UI", size, bold=bold)

f_title = get_font(42, True)
f_big   = get_font(36, True)
f_med   = get_font(30)
f_win   = get_font(90, True)

def draw_board(board):
    screen.fill(BG_COLOR)
    # Vẽ lưới (sửa: +1 cho đường cuối)
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, (60, 60 + i*CELL_SIZE), (60 + BOARD_SIZE*CELL_SIZE, 60 + i*CELL_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR, (60 + i*CELL_SIZE, 60), (60 + i*CELL_SIZE, 60 + BOARD_SIZE*CELL_SIZE), 2)

    # Vẽ quân cờ
    for y in range(15):
        for x in range(15):
            center_x = 60 + x * CELL_SIZE + CELL_SIZE // 2
            center_y = 60 + y * CELL_SIZE + CELL_SIZE // 2
            if board[y][x] == 1:   # X
                pygame.draw.line(screen, X_COLOR, (center_x-18, center_y-18), (center_x+18, center_y+18), 10)
                pygame.draw.line(screen, X_COLOR, (center_x-18, center_y+18), (center_x+18, center_y-18), 10)
            elif board[y][x] == 2: # O
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
    # Khởi tạo game
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
        while not stop_listener:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    msg_queue.put(json.loads(data))
            except:
                break

    threading.Thread(target=listener, daemon=True).start()

    running = True
    while running:
        # === QUAN TRỌNG: XỬ LÝ QUEUE TRƯỚC ĐỂ CẬP NHẬT my_turn NGAY LẬP TỨC ===
        while True:
            try:
                msg = msg_queue.get_nowait()
                print(f"[Game] Nhận: {msg}")

                if msg['type'] == 'move':
                    opp_symbol = 3 - my_symbol
                    board[msg['y']][msg['x']] = opp_symbol
                    if check_win(board, msg['x'], msg['y'], opp_symbol):
                        game_over = True
                        winner_name = opponent_name
                    my_turn = True  # ← NGAY LẬP TỨC chuyển lượt, KHÔNG LAG!

                elif msg['type'] == 'win':
                    game_over = True
                    winner_name = msg['winner']

                elif msg['type'] == 'opponent_left':
                    pygame.display.set_caption("Cờ Caro - Đối thủ đã rời phòng!")
                    running = False

            except queue.Empty:
                break

        # Xử lý event (sau queue để sync đúng)
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
                        client_socket.send(json.dumps({
                            'type': 'move',
                            'room': room_code,
                            'x': col,
                            'y': row
                        }).encode())

                        if check_win(board, col, row, my_symbol):
                            game_over = True
                            winner_name = player_name
                            client_socket.send(json.dumps({'type': 'win', 'winner': player_name}).encode())

                        my_turn = False  # Chuyển lượt ngay

        # === VẼ GIAO DIỆN ===
        draw_board(board)

        # Panel bên phải (đẹp hơn)
        panel = pygame.Rect(WIDTH-210, 10, 200, HEIGHT-20)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=25)
        pygame.draw.rect(screen, PANEL_BORDER, panel, 6, border_radius=25)

        # Thông tin (cố định vị trí)
        y_pos = 50
        screen.blit(f_title.render("CỜ CARO", True, (255, 215, 0)), (WIDTH - 200, y_pos)); y_pos += 55
        screen.blit(f_med.render(f"Phòng: {room_code}", True, (180, 255, 180)), (WIDTH - 200, y_pos)); y_pos += 50
        screen.blit(f_med.render(f"Bạn: {player_name}", True, (100, 255, 150)), (WIDTH - 200, y_pos)); y_pos += 50
        screen.blit(f_med.render(f"Đối thủ: {opponent_name}", True, (255, 120, 120)), (WIDTH - 200, y_pos)); y_pos += 50
        symbol_text = f_big.render("X" if my_symbol==1 else "O", True, X_COLOR if my_symbol==1 else O_COLOR)
        screen.blit(symbol_text, (WIDTH - 110, y_pos)); y_pos += 70  # Căn giữa symbol

        # Trạng thái lượt - BÂY GIỜ ĐÚNG 100%, KHÔNG LAG!
        if game_over:
            status = "TRÒ CHƠI KẾT THÚC"
            status_col = (255, 215, 0)
        elif my_turn:
            status = "LƯỢT CỦA BẠN!"
            status_col = (0, 255, 0)
            # Hiệu ứng nhấp nháy khi đến lượt (tùy chọn)
            if int(pygame.time.get_ticks() / 300) % 2:
                status_col = (50, 255, 50)
        else:
            status = "Đợi đối thủ..."
            status_col = (255, 200, 0)

        status_surf = f_big.render(status, True, status_col)
        screen.blit(status_surf, (WIDTH - 200, 380))

        # Hiệu ứng thắng (cải thiện vị trí)
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

        pygame.display.set_caption(f"Cờ Caro - Phòng {room_code}")
        pygame.display.flip()
        clock.tick(60)

    # Dọn dẹp khi thoát game
    stop_listener = True
    try:
        client_socket.close()
    except:
        pass
    # Trở về menu (không thoát chương trình)