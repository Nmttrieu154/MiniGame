# game_ai.py - GIAO DIỆN GIỐNG HỆT HÌNH MẪU
import pygame
import time
from ai import CaroAI

pygame.init()
CELL_SIZE = 35
BOARD_SIZE = 15
WIDTH = 1200
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cờ Caro - AI Mode")
clock = pygame.time.Clock()

BG_COLOR = (20, 30, 48)
BOARD_BG = (230, 210, 180)
LINE_COLOR = (139, 115, 85)
X_COLOR = (59, 130, 246)  # ← ĐỔI THÀNH MÀU XANH DƯƠNG
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
    """Vẽ bàn cờ"""
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

def draw_player_panel(x, y, name, symbol, is_turn=False, time_left=None, is_ai=False):
    """Vẽ panel người chơi - HIỂN THỊ TIMER"""
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
    
    # Avatar với màu theo symbol
    circle_bg_color = X_COLOR if symbol == "X" else O_COLOR
    pygame.draw.circle(screen, circle_bg_color, circle_center, 65)
    pygame.draw.circle(screen, PANEL_BORDER, circle_center, 65, 5)
    
    if symbol == "X":
        size = 28
        symbol_color = (255, 255, 255)  # Trắng để tương phản
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
    
    # HIỂN THỊ TIMER hoặc status
    if time_left is not None and is_turn and not is_ai:
        # Hiển thị timer cho người chơi
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
        # Hiển thị status
        if is_ai and is_turn:
            status_text = "AI đang tính..."
            status_color = (255, 200, 0)
        elif is_turn:
            status_text = "Lượt bạn!"
            status_color = (100, 255, 100)
        else:
            status_text = "Đợi..."
            status_color = (150, 150, 150)
        
        status_surf = f_med.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(center=(x + panel_w // 2, box_y + 45))
        screen.blit(status_surf, status_rect)

def check_win(board, x, y, player):
    """Kiểm tra thắng với rule chặn 2 đầu"""
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
    """Tìm chuỗi 4"""
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

def main(player_name, difficulty="medium"):
    board = [[0] * 15 for _ in range(15)]
    ai = CaroAI(difficulty=difficulty)
    
    player_symbol = 1
    ai_symbol = 2
    my_turn = True
    game_over = False
    winner_name = ""
    ai_thinking = False
    
    turn_start_time = time.time()
    time_left = TURN_TIME_LIMIT
    
    running = True
    while running:
        # Cập nhật timer
        if my_turn and not game_over and not ai_thinking:
            elapsed = time.time() - turn_start_time
            time_left = max(0, TURN_TIME_LIMIT - int(elapsed))
            
            if time_left <= 0:
                game_over = True
                winner_name = "AI (Timeout)"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and my_turn and not game_over and not ai_thinking:
                mx, my = event.pos
                board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
                board_y = 130
                if board_x <= mx <= board_x + BOARD_SIZE * CELL_SIZE and board_y <= my <= board_y + BOARD_SIZE * CELL_SIZE:
                    col = (mx - board_x) // CELL_SIZE
                    row = (my - board_y) // CELL_SIZE
                    
                    if board[row][col] == 0:
                        board[row][col] = player_symbol
                        
                        if check_win(board, col, row, player_symbol):
                            game_over = True
                            winner_name = player_name
                        else:
                            my_turn = False
                            ai_thinking = True
        
        # AI tính toán
        if not my_turn and not game_over and ai_thinking:
            ai_move = ai.get_move(board, ai_symbol, player_symbol)
            if ai_move:
                x, y = ai_move
                board[y][x] = ai_symbol
                
                if check_win(board, x, y, ai_symbol):
                    game_over = True
                    winner_name = "AI"
                else:
                    my_turn = True
                    turn_start_time = time.time()  # Reset timer
                    time_left = TURN_TIME_LIMIT
            
            ai_thinking = False
        
        blink_positions = find_four_in_row(board) if not game_over else set()
        board_x, board_y, board_w, board_h = draw_board(board, blink_positions)
        
        # Top bar
        top_rect = pygame.Rect(0, 0, WIDTH, 80)
        pygame.draw.rect(screen, TOP_BAR_BG, top_rect)
        pygame.draw.rect(screen, PANEL_BORDER, (0, 75, WIDTH, 5))
        
        mode_surf = f_title.render(f"PHÒNG: AI-{difficulty.upper()}", True, PANEL_BORDER)
        mode_rect = mode_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(mode_surf, mode_rect)
        
        # Panels
        board_x = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
        
        # Left panel (Player)
        left_panel_x = board_x - 210 - 40
        draw_player_panel(left_panel_x, 160, player_name, "X", 
                         my_turn and not game_over, 
                         time_left if my_turn else None, False)
        
        # Right panel (AI)
        right_panel_x = board_x + BOARD_SIZE * CELL_SIZE + 40
        draw_player_panel(right_panel_x, 160, "AI", "O", 
                         not my_turn and not game_over, None, True)
        
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

if __name__ == "__main__":
    main("Player", difficulty="medium")