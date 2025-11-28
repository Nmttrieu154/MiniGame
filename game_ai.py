# game_ai.py - CẬP NHẬT với Timer + Chặn 2 đầu + Nhấp nháy
import pygame
import time
from ai import CaroAI

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
BLINK_COLOR = (255, 215, 0)

TURN_TIME_LIMIT = 30  # 30 giây

def get_font(size, bold=False):
    return pygame.font.SysFont("Segoe UI", size, bold=bold)

f_title = get_font(42, True)
f_big = get_font(36, True)
f_med = get_font(30)
f_win = get_font(90, True)
f_timer = get_font(48, True)

def draw_board(board, blink_positions=None):
    """Vẽ bàn cờ với hiệu ứng nhấp nháy"""
    screen.fill(BG_COLOR)
    
    # Vẽ lưới
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, (60, 60 + i*CELL_SIZE), 
                         (60 + BOARD_SIZE*CELL_SIZE, 60 + i*CELL_SIZE), 2)
        pygame.draw.line(screen, LINE_COLOR, (60 + i*CELL_SIZE, 60), 
                         (60 + i*CELL_SIZE, 60 + BOARD_SIZE*CELL_SIZE), 2)
    
    # Nhấp nháy cho chuỗi 4
    blink_on = (int(pygame.time.get_ticks() / 300) % 2 == 0)
    
    # Vẽ quân cờ
    for y in range(15):
        for x in range(15):
            center_x = 60 + x * CELL_SIZE + CELL_SIZE // 2
            center_y = 60 + y * CELL_SIZE + CELL_SIZE // 2
            
            # Kiểm tra có nhấp nháy không
            should_blink = blink_positions and (x, y) in blink_positions
            
            if board[y][x] == 1:
                color = BLINK_COLOR if (should_blink and blink_on) else X_COLOR
                pygame.draw.line(screen, color, (center_x-18, center_y-18), 
                                (center_x+18, center_y+18), 10)
                pygame.draw.line(screen, color, (center_x-18, center_y+18), 
                                (center_x+18, center_y-18), 10)
            elif board[y][x] == 2:
                color = BLINK_COLOR if (should_blink and blink_on) else O_COLOR
                pygame.draw.circle(screen, color, (center_x, center_y), 20, 9)

def check_win(board, x, y, player):
    """Kiểm tra thắng với rule chặn 2 đầu"""
    dirs = [(1,0), (0,1), (1,1), (1,-1)]
    
    for dx, dy in dirs:
        count = 1
        positions = [(x, y)]
        
        # Đếm về phía trước
        for i in range(1, 5):
            nx, ny = x + dx*i, y + dy*i
            if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                break
            count += 1
            positions.append((nx, ny))
        
        # Đếm về phía sau
        for i in range(1, 5):
            nx, ny = x - dx*i, y - dy*i
            if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                break
            count += 1
            positions.insert(0, (nx, ny))
        
        # Nếu có 5 quân
        if count >= 5:
            # Kiểm tra chặn 2 đầu
            first_5 = positions[:5]
            start_x, start_y = first_5[0]
            end_x, end_y = first_5[-1]
            
            # Kiểm tra ô trước điểm bắt đầu
            before_x = start_x - dx
            before_y = start_y - dy
            before_blocked = False
            if 0 <= before_x < 15 and 0 <= before_y < 15:
                if board[before_y][before_x] == (3 - player):
                    before_blocked = True
            else:
                before_blocked = True
            
            # Kiểm tra ô sau điểm kết thúc
            after_x = end_x + dx
            after_y = end_y + dy
            after_blocked = False
            if 0 <= after_x < 15 and 0 <= after_y < 15:
                if board[after_y][after_x] == (3 - player):
                    after_blocked = True
            else:
                after_blocked = True
            
            # Nếu bị chặn 2 đầu thì không thắng
            if before_blocked and after_blocked:
                continue
            
            return True
    
    return False

def find_four_in_row(board):
    """Tìm tất cả chuỗi 4 quân liên tiếp để nhấp nháy"""
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
                
                # Đếm về phía trước
                for i in range(1, 4):
                    nx, ny = x + dx*i, y + dy*i
                    if not (0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == player):
                        break
                    count += 1
                    positions.append((nx, ny))
                
                # Nếu có đúng 4 quân và 2 đầu không bị chặn
                if count == 4:
                    # Kiểm tra 2 đầu
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
                    
                    # Nếu ít nhất 1 đầu còn trống
                    if before_open or after_open:
                        blink_positions.update(positions)
    
    return blink_positions

def main(player_name, difficulty="medium"):
    """
    difficulty: "easy", "medium", "hard"
    """
    board = [[0] * 15 for _ in range(15)]
    ai = CaroAI(difficulty=difficulty)
    
    player_symbol = 1  # X
    ai_symbol = 2      # O
    my_turn = True
    game_over = False
    winner_name = ""
    ai_thinking = False
    
    # Timer
    turn_start_time = time.time()
    time_left = TURN_TIME_LIMIT
    
    print(f"[GAME AI] 🤖 AI Mode: {difficulty}")
    print(f"[GAME AI] 🎮 Player: {player_name} (X), AI ({difficulty}) (O)")
    
    running = True
    while running:
        # Cập nhật timer
        if my_turn and not game_over and not ai_thinking:
            elapsed = time.time() - turn_start_time
            time_left = max(0, TURN_TIME_LIMIT - int(elapsed))
            
            # Hết giờ
            if time_left <= 0:
                game_over = True
                winner_name = "AI (Timeout)"
                print("[GAME AI] ⏰ Hết giờ!")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and my_turn and not game_over and not ai_thinking:
                mx, my = event.pos
                if 60 <= mx <= 60 + BOARD_SIZE * CELL_SIZE and 60 <= my <= 60 + BOARD_SIZE * CELL_SIZE:
                    col = (mx - 60) // CELL_SIZE
                    row = (my - 60) // CELL_SIZE
                    
                    if board[row][col] == 0:
                        board[row][col] = player_symbol
                        print(f"[GAME AI] ♟️ Bạn đánh: ({col}, {row})")
                        
                        if check_win(board, col, row, player_symbol):
                            game_over = True
                            winner_name = player_name
                            print(f"[GAME AI] 🏆 {player_name} thắng!")
                        else:
                            my_turn = False
                            ai_thinking = True
        
        # AI tính toán nước đi
        if not my_turn and not game_over and ai_thinking:
            ai_move = ai.get_move(board, ai_symbol, player_symbol)
            if ai_move:
                x, y = ai_move
                board[y][x] = ai_symbol
                print(f"[GAME AI] 🤖 AI đánh: ({x}, {y})")
                
                if check_win(board, x, y, ai_symbol):
                    game_over = True
                    winner_name = "AI"
                    print(f"[GAME AI] 🏆 AI thắng!")
                else:
                    my_turn = True
                    turn_start_time = time.time()
                    time_left = TURN_TIME_LIMIT
            
            ai_thinking = False
        
        # Vẽ board với nhấp nháy
        blink_positions = find_four_in_row(board) if not game_over else set()
        draw_board(board, blink_positions)
        
        # Vẽ panel bên phải
        panel = pygame.Rect(WIDTH-210, 10, 200, HEIGHT-20)
        pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=25)
        pygame.draw.rect(screen, PANEL_BORDER, panel, 6, border_radius=25)
        
        y_pos = 50
        screen.blit(f_title.render("CỜ CARO", True, (255, 215, 0)), (WIDTH - 200, y_pos)); y_pos += 55
        
        difficulty_text = "🎯 Mode: " + difficulty.upper()
        screen.blit(f_med.render(difficulty_text, True, (180, 255, 180)), (WIDTH - 200, y_pos)); y_pos += 50
        
        screen.blit(f_med.render(f"Bạn: {player_name}", True, (100, 255, 150)), (WIDTH - 200, y_pos)); y_pos += 50
        screen.blit(f_med.render("AI: Máy tính", True, (255, 120, 120)), (WIDTH - 200, y_pos)); y_pos += 50
        
        screen.blit(f_big.render("X", True, X_COLOR), (WIDTH - 110, y_pos)); y_pos += 70
        
        # Hiển thị timer
        if not game_over and not ai_thinking:
            if my_turn:
                timer_color = (255, 0, 0) if time_left <= 10 else (255, 215, 0)
                timer_text = f_timer.render(f"{time_left}s", True, timer_color)
                screen.blit(timer_text, (WIDTH - 130, y_pos))
                y_pos += 70
        
        if game_over:
            status = "KẾT THÚC!"
            status_col = (255, 215, 0)
        elif ai_thinking:
            status = "AI ĐANG TÍNH..."
            status_col = (255, 150, 0)
            if int(pygame.time.get_ticks() / 300) % 2:
                status_col = (255, 200, 0)
        elif my_turn:
            status = "LƯỢT CỦA BẠN!"
            status_col = (0, 255, 0)
            if int(pygame.time.get_ticks() / 300) % 2:
                status_col = (50, 255, 50)
        else:
            status = "LƯỢT AI..."
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
    
    print("[GAME AI] 🛑 Game kết thúc")

if __name__ == "__main__":
    # Test: python game_ai.py
    main("Player", difficulty="medium")