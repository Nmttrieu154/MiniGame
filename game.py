# game.py - FIX TIMER CHẠY CẢ 2 BÊN
import pygame
import json
import threading
import queue
import time

pygame.init()
CELL_SIZE = 35
BOARD_SIZE = 15
WIDTH = 1200
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cờ Caro")
clock = pygame.time.Clock()

# COLORS
BG_COLOR = (20, 30, 48)
BOARD_BG = (230, 210, 180)
LINE_COLOR = (139, 115, 85)
X_COLOR = (59, 130, 246)
O_COLOR = (239, 68, 68)
PANEL_BG = (30, 41, 59)
PANEL_BORDER = (52, 211, 153)
TOP_BAR_BG = (15, 23, 42)
CIRCLE_OUTER = (15, 23, 42)
BLINK_COLOR = (251, 146, 60)

TURN_TIME_LIMIT = 30

def get_font(size, bold=False):
    for font_name in ["Segoe UI", "Arial", "Tahoma", "Verdana"]:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except:
            continue
    return pygame.font.Font(None, size)

f_title = get_font(40, True)
f_big = get_font(32, True)
f_med = get_font(28)
f_small = get_font(22)
f_timer = get_font(60, True)
f_win = get_font(80, True)

def draw_board(board, blink_positions=None):
    """Vẽ bàn cờ giống hình mẫu"""
    screen.fill(BG_COLOR)
    
    board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
    board_y = 130
    board_width = BOARD_SIZE * CELL_SIZE
    board_height = BOARD_SIZE * CELL_SIZE
    
    outer_border = pygame.Rect(board_x - 15, board_y - 15, 
                               board_width + 30, board_height + 30)
    pygame.draw.rect(screen, PANEL_BORDER, outer_border, 8)
    
    board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
    pygame.draw.rect(screen, BOARD_BG, board_rect)
    
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, 
                        (board_x, board_y + i * CELL_SIZE),
                        (board_x + board_width, board_y + i * CELL_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR,
                        (board_x + i * CELL_SIZE, board_y),
                        (board_x + i * CELL_SIZE, board_y + board_height), 2)
    
    blink_on = (int(pygame.time.get_ticks() / 300) % 2 == 0)
    
    for y in range(15):
        for x in range(15):
            center_x = board_x + x * CELL_SIZE + CELL_SIZE // 2
            center_y = board_y + y * CELL_SIZE + CELL_SIZE // 2
            
            should_blink = blink_positions and (x, y) in blink_positions
            
            if board[y][x] == 1:
                color = BLINK_COLOR if (should_blink and blink_on) else X_COLOR
                size = 13
                pygame.draw.line(screen, color, (center_x-size, center_y-size), 
                                (center_x+size, center_y+size), 7)
                pygame.draw.line(screen, color, (center_x-size, center_y+size), 
                                (center_x+size, center_y-size), 7)
            elif board[y][x] == 2:
                color = BLINK_COLOR if (should_blink and blink_on) else O_COLOR
                pygame.draw.circle(screen, color, (center_x, center_y), 15, 6)
    
    return board_x, board_y, board_width, board_height

def draw_player_panel(x, y, name, symbol, is_turn=False, time_left=None):
    """Vẽ panel người chơi"""
    panel_w = 210
    panel_h = 340
    
    outer_rect = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(screen, PANEL_BORDER, outer_rect, 6)
    
    inner_rect = pygame.Rect(x + 6, y + 6, panel_w - 12, panel_h - 12)
    pygame.draw.rect(screen, PANEL_BG, inner_rect)
    
    if is_turn:
        glow_rect = pygame.Rect(x - 5, y - 5, panel_w + 10, panel_h + 10)
        for i in range(3):
            alpha_surface = pygame.Surface((panel_w + 10, panel_h + 10), pygame.SRCALPHA)
            pygame.draw.rect(alpha_surface, (*PANEL_BORDER, 50 - i*15), (i, i, panel_w + 10 - i*2, panel_h + 10 - i*2), 2)
            screen.blit(alpha_surface, (glow_rect.x, glow_rect.y))
    
    circle_y = y + 100
    circle_center = (x + panel_w // 2, circle_y)
    
    circle_bg_color = X_COLOR if symbol == "X" else O_COLOR
    pygame.draw.circle(screen, circle_bg_color, circle_center, 65)
    pygame.draw.circle(screen, PANEL_BORDER, circle_center, 65, 5)
    
    if symbol == "X":
        size = 28
        symbol_color = (255, 255, 255)
        pygame.draw.line(screen, symbol_color, 
                        (circle_center[0]-size, circle_center[1]-size),
                        (circle_center[0]+size, circle_center[1]+size), 9)
        pygame.draw.line(screen, symbol_color,
                        (circle_center[0]-size, circle_center[1]+size),
                        (circle_center[0]+size, circle_center[1]-size), 9)
    else:
        pygame.draw.circle(screen, (255, 255, 255), circle_center, 30, 8)
    
    name_surf = f_med.render(name[:8], True, (255, 255, 255))
    name_rect = name_surf.get_rect(center=(x + panel_w // 2, circle_y + 85))
    screen.blit(name_surf, name_rect)
    
    box_y = circle_y + 120
    box_rect = pygame.Rect(x + 25, box_y, panel_w - 50, 90)
    pygame.draw.rect(screen, CIRCLE_OUTER, box_rect, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, box_rect, 4, border_radius=8)
    
    # HIỂN THỊ TIMER
    if time_left is not None and time_left >= 0:
        if time_left <= 5:
            timer_color = (255, 50, 50)
        elif time_left <= 10:
            timer_color = (255, 150, 0)
        else:
            timer_color = (100, 255, 100)
        
        timer_surf = f_timer.render(str(time_left), True, timer_color)
        timer_rect = timer_surf.get_rect(center=(x + panel_w // 2, box_y + 35))
        screen.blit(timer_surf, timer_rect)
        
        sec_surf = f_small.render("giây", True, (200, 200, 200))
        sec_rect = sec_surf.get_rect(center=(x + panel_w // 2, box_y + 65))
        screen.blit(sec_surf, sec_rect)
    else:
        status_surf = f_med.render("Đợi...", True, (150, 150, 150))
        status_rect = status_surf.get_rect(center=(x + panel_w // 2, box_y + 45))
        screen.blit(status_surf, status_rect)

def check_win(board, x, y, player):
    dirs = [(1,0), (0,1), (1,1), (1,-1)]
    
    for dx, dy in dirs:
        count = 1
        positions = [(x, y)]
        
        for i in range(1, 5):
            nx, ny = x + dx*i, y + dy*i
            if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                break
            count += 1
            positions.append((nx, ny))
        
        for i in range(1, 5):
            nx, ny = x - dx*i, y - dy*i
            if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                break
            count += 1
            positions.insert(0, (nx, ny))
        
        if count >= 5:
            first_5 = positions[:5]
            start_x, start_y = first_5[0]
            end_x, end_y = first_5[-1]
            
            before_x = start_x - dx
            before_y = start_y - dy
            before_blocked = False
            if 0 <= before_x < 15 and 0 <= before_y < 15:
                if board[before_y][before_x] == (3 - player):
                    before_blocked = True
            else:
                before_blocked = True
            
            after_x = end_x + dx
            after_y = end_y + dy
            after_blocked = False
            if 0 <= after_x < 15 and 0 <= after_y < 15:
                if board[after_y][after_x] == (3 - player):
                    after_blocked = True
            else:
                after_blocked = True
            
            if before_blocked and after_blocked:
                continue
            
            return True
    
    return False

def find_four_in_row(board):
    blink_positions = set()
    dirs = [(1,0), (0,1), (1,1), (1,-1)]
    
    for y in range(15):
        for x in range(15):
            if board[y][x] == 0:
                continue
            
            player = board[y][x]
            
            for dx, dy in dirs:
                count = 1
                positions = [(x, y)]
                
                for i in range(1, 4):
                    nx, ny = x + dx*i, y + dy*i
                    if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                        break
                    count += 1
                    positions.append((nx, ny))
                
                if count == 4:
                    start_x, start_y = positions[0]
                    end_x, end_y = positions[-1]
                    
                    before_x = start_x - dx
                    before_y = start_y - dy
                    after_x = end_x + dx
                    after_y = end_y + dy
                    
                    before_open = (0 <= before_x < 15 and 0 <= before_y < 15 and 
                                   board[before_y][before_x] == 0)
                    after_open = (0 <= after_x < 15 and 0 <= after_y < 15 and 
                                  board[after_y][after_x] == 0)
                    
                    if before_open or after_open:
                        blink_positions.update(positions)
    
    return blink_positions

def main(player_name, room_code, client_socket, names, player_index):
    client_socket.setblocking(True)
    time.sleep(0.5)
    
    board = [[0] * 15 for _ in range(15)]
    my_symbol = 1 if player_index == 0 else 2
    opponent_name = names[1] if player_index == 0 else names[0]
    my_turn = (player_index == 0)
    game_over = False
    winner_name = ""
    msg_queue = queue.Queue()
    stop_listener = False
    
    # TIMER CHO CẢ 2 NGƯỜI
    turn_start_time = time.time()  # ← Luôn track thời gian
    my_time_left = TURN_TIME_LIMIT if my_turn else 0
    opp_time_left = TURN_TIME_LIMIT if not my_turn else 0  # ← Đối thủ cũng có timer

    def listener():
        nonlocal stop_listener
        buffer = ""
        
        while not stop_listener and client_socket:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        msg = json.loads(line)
                        if msg['type'] in ['start', 'joined']:
                            continue
                        msg_queue.put(msg)
                    except:
                        continue
                        
            except:
                break

    threading.Thread(target=listener, daemon=True).start()
    
    running = True
    while running:
        while True:
            try:
                msg = msg_queue.get_nowait()
                
                if msg['type'] == 'move':
                    opp_symbol = 3 - my_symbol
                    board[msg['y']][msg['x']] = opp_symbol
                    if check_win(board, msg['x'], msg['y'], opp_symbol):
                        game_over = True
                        winner_name = opponent_name
                    else:
                        my_turn = True
                        turn_start_time = time.time()  # ← Reset timer
                        my_time_left = TURN_TIME_LIMIT
                        opp_time_left = 0
                
                elif msg['type'] == 'win':
                    game_over = True
                    winner_name = msg['winner']
                
                elif msg['type'] == 'timeout':
                    game_over = True
                    winner_name = msg['winner']
                
                elif msg['type'] == 'opponent_left':
                    game_over = True
                    winner_name = player_name + " (Đối thủ rời)"
                    
            except queue.Empty:
                break

        # CẬP NHẬT TIMER THEO THỜI GIAN THỰC
        if not game_over:
            elapsed = time.time() - turn_start_time
            
            if my_turn:
                my_time_left = max(0, TURN_TIME_LIMIT - int(elapsed))
                opp_time_left = 0
                
                if my_time_left <= 0:
                    game_over = True
                    winner_name = opponent_name + " (Timeout)"
                    try:
                        timeout_msg = {'type': 'timeout', 'winner': opponent_name}
                        client_socket.send((json.dumps(timeout_msg) + '\n').encode())
                    except:
                        pass
            else:
                # Đối thủ đang chơi - cập nhật timer của đối thủ
                opp_time_left = max(0, TURN_TIME_LIMIT - int(elapsed))
                my_time_left = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_listener = True
            
            if event.type == pygame.MOUSEBUTTONDOWN and my_turn and not game_over:
                mx, my = event.pos
                board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
                board_y = 130
                if board_x <= mx <= board_x + BOARD_SIZE * CELL_SIZE and board_y <= my <= board_y + BOARD_SIZE * CELL_SIZE:
                    col = (mx - board_x) // CELL_SIZE
                    row = (my - board_y) // CELL_SIZE
                    
                    if board[row][col] == 0:
                        board[row][col] = my_symbol
                        
                        move_msg = {'type': 'move', 'x': col, 'y': row}
                        try:
                            client_socket.send((json.dumps(move_msg) + '\n').encode())
                        except:
                            pass
                        
                        if check_win(board, col, row, my_symbol):
                            game_over = True
                            winner_name = player_name
                            win_msg = {'type': 'win', 'winner': player_name}
                            try:
                                client_socket.send((json.dumps(win_msg) + '\n').encode())
                            except:
                                pass
                        else:
                            my_turn = False
                            turn_start_time = time.time()  # ← Reset cho đối thủ
                            my_time_left = 0
                            opp_time_left = TURN_TIME_LIMIT

        blink_positions = find_four_in_row(board) if not game_over else set()
        board_x, board_y, board_w, board_h = draw_board(board, blink_positions)
        
        # Top bar
        top_rect = pygame.Rect(0, 0, WIDTH, 80)
        pygame.draw.rect(screen, TOP_BAR_BG, top_rect)
        pygame.draw.rect(screen, PANEL_BORDER, (0, 75, WIDTH, 5))
        
        room_surf = f_title.render(f"PHÒNG: {room_code}", True, PANEL_BORDER)
        room_rect = room_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(room_surf, room_rect)
        
        # Player panels
        my_symbol_str = "X" if my_symbol == 1 else "O"
        opp_symbol_str = "O" if my_symbol == 1 else "X"
        
        board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
        
        # Left panel (player) - hiển thị timer của mình
        left_panel_x = board_x - 210 - 40
        draw_player_panel(left_panel_x, 160, player_name, my_symbol_str, 
                         my_turn and not game_over, 
                         my_time_left if my_turn else None)
        
        # Right panel (opponent) - hiển thị timer của đối thủ
        right_panel_x = board_x + BOARD_SIZE * CELL_SIZE + 40
        draw_player_panel(right_panel_x, 160, opponent_name, opp_symbol_str, 
                         not my_turn and not game_over, 
                         opp_time_left if not my_turn else None)
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(220)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            win_surf = f_win.render(f"{winner_name}", True, PANEL_BORDER)
            screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 100))
            
            win_label = f_big.render("CHIẾN THẮNG!", True, (255, 255, 255))
            screen.blit(win_label, (WIDTH//2 - win_label.get_width()//2, HEIGHT//2 - 20))
            
            again = f_med.render("Đóng cửa sổ để về menu", True, (200, 200, 200))
            screen.blit(again, (WIDTH//2 - again.get_width()//2, HEIGHT//2 + 40))

        pygame.display.flip()
        clock.tick(60)

    stop_listener = True
    try:
        client_socket.close()
    except:
        pass