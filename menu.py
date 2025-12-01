# menu.py - GIAO DIỆN MỚI SANG TRỌNG
import pygame
import socket
import json
import random
import string
import threading
import queue
import pyperclip
import sys
import time

pygame.init()
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cờ Caro Online")
clock = pygame.time.Clock()

# BỘ MÀU MỚI - SANG TRỌNG & HIỆN ĐẠI
BG_GRADIENT_TOP = (20, 30, 48)      # Xanh navy đậm
BG_GRADIENT_BOT = (36, 59, 85)      # Xanh dương đậm
ACCENT_PRIMARY = (52, 211, 153)     # Xanh lá mint
ACCENT_SECONDARY = (59, 130, 246)   # Xanh dương sáng
BUTTON_BG = (30, 41, 59)            # Xanh đậm
BUTTON_HOVER = (51, 65, 85)         # Xanh nhạt hơn
TEXT_WHITE = (248, 250, 252)        # Trắng tinh
TEXT_GRAY = (148, 163, 184)         # Xám nhạt
PANEL_BG = (30, 41, 59)             # Nền panel
BORDER_COLOR = (52, 211, 153)       # Viền xanh mint
INPUT_BG = (15, 23, 42)             # Nền input đậm
SUCCESS = (34, 197, 94)             # Xanh lá success
WARNING = (251, 146, 60)            # Cam warning
ERROR = (239, 68, 68)               # Đỏ error

def font(size, bold=False):
    for font_name in ["Segoe UI", "Arial", "Tahoma"]:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except:
            continue
    return pygame.font.Font(None, size)

title = font(72, True)
subtitle = font(36)
big = font(38, True)
med = font(30)
sml = font(24)
tiny = font(20)

def draw_gradient_bg():
    """Vẽ background gradient"""
    for y in range(HEIGHT):
        progress = y / HEIGHT
        r = int(BG_GRADIENT_TOP[0] + (BG_GRADIENT_BOT[0] - BG_GRADIENT_TOP[0]) * progress)
        g = int(BG_GRADIENT_TOP[1] + (BG_GRADIENT_BOT[1] - BG_GRADIENT_TOP[1]) * progress)
        b = int(BG_GRADIENT_TOP[2] + (BG_GRADIENT_BOT[2] - BG_GRADIENT_TOP[2]) * progress)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_button(x, y, w, h, text, hover=False, icon=None):
    """Vẽ nút bấm hiện đại"""
    # Shadow
    shadow_rect = pygame.Rect(x + 4, y + 4, w, h)
    shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 40), (0, 0, w, h), border_radius=12)
    screen.blit(shadow_surf, (x + 4, y + 4))
    
    # Button
    color = BUTTON_HOVER if hover else BUTTON_BG
    btn_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, btn_rect, border_radius=12)
    
    # Border glow khi hover
    if hover:
        pygame.draw.rect(screen, ACCENT_PRIMARY, btn_rect, 3, border_radius=12)
    else:
        pygame.draw.rect(screen, BORDER_COLOR, btn_rect, 2, border_radius=12)
    
    # Icon (vẽ hình thay vì dùng emoji)
    text_x = x + w // 2
    if icon == "game":
        # Vẽ icon game controller
        icon_x = x + 50
        icon_y = y + h // 2
        pygame.draw.rect(screen, ACCENT_PRIMARY, (icon_x - 15, icon_y - 8, 30, 16), border_radius=4)
        pygame.draw.circle(screen, ACCENT_PRIMARY, (icon_x - 8, icon_y), 4)
        pygame.draw.circle(screen, ACCENT_PRIMARY, (icon_x + 8, icon_y), 4)
        text_x = x + w // 2 + 20
    elif icon == "ai":
        # Vẽ icon robot/AI
        icon_x = x + 50
        icon_y = y + h // 2
        pygame.draw.rect(screen, ACCENT_PRIMARY, (icon_x - 10, icon_y - 10, 20, 20), border_radius=3)
        pygame.draw.circle(screen, BG_GRADIENT_TOP, (icon_x - 5, icon_y - 3), 3)
        pygame.draw.circle(screen, BG_GRADIENT_TOP, (icon_x + 5, icon_y - 3), 3)
        pygame.draw.rect(screen, BG_GRADIENT_TOP, (icon_x - 6, icon_y + 3, 12, 3))
        text_x = x + w // 2 + 20
    
    # Text
    text_surf = med.render(text, True, TEXT_WHITE)
    text_rect = text_surf.get_rect(center=(text_x, y + h // 2))
    screen.blit(text_surf, text_rect)

def draw_panel(x, y, w, h, title_text=None):
    """Vẽ panel với tiêu đề"""
    # Shadow
    shadow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (0, 0, w, h), border_radius=16)
    screen.blit(shadow_surf, (x + 6, y + 6))
    
    # Panel
    panel_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, PANEL_BG, panel_rect, border_radius=16)
    pygame.draw.rect(screen, BORDER_COLOR, panel_rect, 2, border_radius=16)
    
    # Title bar
    if title_text:
        title_bar = pygame.Rect(x, y, w, 60)
        pygame.draw.rect(screen, (20, 30, 48), title_bar, border_top_left_radius=16, border_top_right_radius=16)
        pygame.draw.line(screen, BORDER_COLOR, (x + 20, y + 60), (x + w - 20, y + 60), 2)
        
        title_surf = big.render(title_text, True, ACCENT_PRIMARY)
        title_rect = title_surf.get_rect(center=(x + w // 2, y + 30))
        screen.blit(title_surf, title_rect)

class InputBox:
    def __init__(self, x, y, w, h, hint):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.hint = hint
        self.active = False
    
    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)
        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_v and (e.mod & pygame.KMOD_CTRL):
                self.text = pyperclip.paste()
            elif e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 20:
                self.text += e.unicode
    
    def draw(self):
        # Input box
        color = BORDER_COLOR if self.active else (71, 85, 105)
        pygame.draw.rect(screen, INPUT_BG, self.rect, border_radius=10)
        pygame.draw.rect(screen, color, self.rect, 3 if self.active else 2, border_radius=10)
        
        # Text
        display_text = self.text or self.hint
        text_color = TEXT_WHITE if self.text else TEXT_GRAY
        text_surf = med.render(display_text, True, text_color)
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 20, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Cursor
        if self.active and int(pygame.time.get_ticks() / 500) % 2:
            cursor_x = self.rect.x + 20 + text_surf.get_width() + 2
            pygame.draw.line(screen, ACCENT_PRIMARY, 
                           (cursor_x, self.rect.y + 15), 
                           (cursor_x, self.rect.bottom - 15), 3)

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

name_box = InputBox(WIDTH//2 - 250, 200, 500, 60, "Nhập tên của bạn...")
room_box = InputBox(WIDTH//2 - 200, 480, 400, 60, "Nhập mã phòng...")

socket_client = None
my_name = ""
room = ""
state = "menu"
q = queue.Queue()
stop_listener = False
player_role = None
listener_thread = None
game_mode = False

def listen_thread():
    global stop_listener, game_mode
    buffer = ""
    
    while not stop_listener and socket_client:
        try:
            if game_mode:
                break
            
            socket_client.settimeout(0.5)
            
            try:
                data = socket_client.recv(1024).decode('utf-8')
            except socket.timeout:
                continue
            
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
                    
                    if game_mode:
                        continue
                    
                    q.put(msg)
                except Exception as e:
                    continue
                    
        except Exception as e:
            if not stop_listener and not game_mode:
                pass
            break
    
    try:
        socket_client.settimeout(None)
    except:
        pass

copy_feedback_alpha = 0

running = True
while running:
    draw_gradient_bg()
    mouse = pygame.mouse.get_pos()
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
            stop_listener = True
            if socket_client:
                try: 
                    socket_client.close()
                except: 
                    pass
        
        if state == "menu":
            name_box.event(e)
            room_box.event(e)
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Tạo phòng mới
                create_btn = pygame.Rect(WIDTH//2 - 250, 300, 500, 70)
                if create_btn.collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Player1"
                    if not my_name: 
                        continue
                    
                    try:
                        socket_client = socket.socket()
                        socket_client.connect(('127.0.0.1', 5555))
                        room = gen_code()
                        
                        join_msg = json.dumps({'type':'join','room':room,'name':my_name}) + '\n'
                        socket_client.send(join_msg.encode())
                        
                        stop_listener = False
                        game_mode = False
                        listener_thread = threading.Thread(target=listen_thread, daemon=True)
                        listener_thread.start()
                        state = "waiting"
                    except Exception as e:
                        state = "menu"
                
                # Chơi với AI
                ai_btn = pygame.Rect(WIDTH//2 - 250, 390, 500, 70)
                if ai_btn.collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Player"
                    if not my_name: 
                        continue
                    state = "ai_difficulty"
                
                # Tham gia phòng
                join_btn = pygame.Rect(WIDTH//2 - 200, 560, 400, 70)
                if join_btn.collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Player2"
                    room = room_box.text.strip().upper()
                    if len(room) != 6: 
                        continue
                    
                    try:
                        socket_client = socket.socket()
                        socket_client.connect(('127.0.0.1', 5555))
                        
                        join_msg = json.dumps({'type':'join','room':room,'name':my_name}) + '\n'
                        socket_client.send(join_msg.encode())
                        
                        stop_listener = False
                        game_mode = False
                        listener_thread = threading.Thread(target=listen_thread, daemon=True)
                        listener_thread.start()
                        state = "waiting"
                    except Exception as e:
                        state = "menu"
        
        elif state == "ai_difficulty":
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Easy
                easy_btn = pygame.Rect(WIDTH//2 - 380, 300, 220, 120)
                if easy_btn.collidepoint(e.pos):
                    try:
                        import game_ai
                        game_ai.main(my_name, "easy")
                    except:
                        pass
                    state = "menu"
                
                # Medium
                med_btn = pygame.Rect(WIDTH//2 - 110, 300, 220, 120)
                if med_btn.collidepoint(e.pos):
                    try:
                        import game_ai
                        game_ai.main(my_name, "medium")
                    except:
                        pass
                    state = "menu"
                
                # Hard
                hard_btn = pygame.Rect(WIDTH//2 + 160, 300, 220, 120)
                if hard_btn.collidepoint(e.pos):
                    try:
                        import game_ai
                        game_ai.main(my_name, "hard")
                    except:
                        pass
                    state = "menu"
            
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = "menu"
        
        elif state == "waiting":
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Copy button
                copy_btn = pygame.Rect(WIDTH//2 + 150, 325, 100, 60)
                if copy_btn.collidepoint(e.pos):
                    pyperclip.copy(room)
                    copy_feedback_alpha = 255
            
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = "menu"
                stop_listener = True
                game_mode = False
                if socket_client:
                    try: 
                        socket_client.close()
                    except: 
                        pass
                    socket_client = None

    if state == "menu":
        # Title
        title_surf = title.render("CỜ CARO", True, ACCENT_PRIMARY)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_surf, title_rect)
        
        subtitle_surf = subtitle.render("Chơi online với bạn bè", True, TEXT_GRAY)
        subtitle_rect = subtitle_surf.get_rect(center=(WIDTH//2, 150))
        screen.blit(subtitle_surf, subtitle_rect)
        
        # Name input
        name_box.draw()
        
        # Buttons
        create_rect = pygame.Rect(WIDTH//2 - 250, 300, 500, 70)
        draw_button(create_rect.x, create_rect.y, create_rect.w, create_rect.h, 
                   "Tạo Phòng Mới", create_rect.collidepoint(mouse), "game")
        
        ai_rect = pygame.Rect(WIDTH//2 - 250, 390, 500, 70)
        draw_button(ai_rect.x, ai_rect.y, ai_rect.w, ai_rect.h, 
                   "Chơi với AI", ai_rect.collidepoint(mouse), "ai")
        
        
        # Room input
        room_box.draw()
        
        join_rect = pygame.Rect(WIDTH//2 - 200, 560, 400, 70)
        draw_button(join_rect.x, join_rect.y, join_rect.w, join_rect.h, 
                   "Tham Gia Phòng", join_rect.collidepoint(mouse))
    
    elif state == "ai_difficulty":
        # Title
        title_surf = big.render("CHỌN ĐỘ KHÓ AI", True, ACCENT_PRIMARY)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 120))
        screen.blit(title_surf, title_rect)
        
        # Difficulty cards
        difficulties = [
            (WIDTH//2 - 380, "DỄ", SUCCESS, "Phù hợp mới chơi", "easy"),
            (WIDTH//2 - 110, "TRUNG BÌNH", WARNING, "Thử thách vừa phải", "medium"),
            (WIDTH//2 + 160, "KHÓ", ERROR, "Cho cao thủ", "hard")
        ]
        
        for x, label, color, desc, level in difficulties:
            rect = pygame.Rect(x, 300, 220, 120)
            is_hover = rect.collidepoint(mouse)
            
            # Card
            bg_color = BUTTON_HOVER if is_hover else BUTTON_BG
            pygame.draw.rect(screen, bg_color, rect, border_radius=12)
            pygame.draw.rect(screen, color, rect, 3 if is_hover else 2, border_radius=12)
            
            # Level indicator - vẽ các thanh
            bar_width = 12
            bar_gap = 6
            total_bars = 3 if level == "hard" else (2 if level == "medium" else 1)
            start_x = x + 110 - (3 * bar_width + 2 * bar_gap) // 2
            
            for i in range(3):
                bar_color = color if i < total_bars else (71, 85, 105)
                bar_x = start_x + i * (bar_width + bar_gap)
                bar_height = 20 + i * 10
                bar_y = 350 - bar_height // 2
                pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            
            # Label
            label_surf = med.render(label, True, TEXT_WHITE)
            label_rect = label_surf.get_rect(center=(x + 110, 385))
            screen.blit(label_surf, label_rect)
            
            # Description
            desc_surf = tiny.render(desc, True, TEXT_GRAY)
            desc_rect = desc_surf.get_rect(center=(x + 110, 410))
            screen.blit(desc_surf, desc_rect)
        
        # Back hint
        back_surf = sml.render("Nhấn ESC để quay lại", True, TEXT_GRAY)
        back_rect = back_surf.get_rect(center=(WIDTH//2, 500))
        screen.blit(back_surf, back_rect)
    
    elif state == "waiting":
        # Panel chính
        panel_w = 600
        panel_h = 400
        panel_x = WIDTH//2 - panel_w//2
        panel_y = HEIGHT//2 - panel_h//2
        draw_panel(panel_x, panel_y, panel_w, panel_h, "PHÒNG CHỜ")
        
        # Status
        status_surf = med.render("Đang chờ đối thủ tham gia...", True, TEXT_WHITE)
        status_rect = status_surf.get_rect(center=(WIDTH//2, panel_y + 120))
        screen.blit(status_surf, status_rect)
        
        # Loading animation
        dots = "." * (int(pygame.time.get_ticks() / 500) % 4)
        dots_surf = big.render(dots, True, ACCENT_PRIMARY)
        dots_rect = dots_surf.get_rect(midleft=(status_rect.right + 5, status_rect.centery))
        screen.blit(dots_surf, dots_rect)
        
        # Room code display
        code_label = sml.render("MÃ PHÒNG:", True, TEXT_GRAY)
        code_label_rect = code_label.get_rect(center=(WIDTH//2, panel_y + 200))
        screen.blit(code_label, code_label_rect)
        
        # Room code
        code_bg = pygame.Rect(WIDTH//2 - 150, panel_y + 230, 300, 80)
        pygame.draw.rect(screen, INPUT_BG, code_bg, border_radius=12)
        pygame.draw.rect(screen, ACCENT_PRIMARY, code_bg, 3, border_radius=12)
        
        code_surf = title.render(room, True, ACCENT_PRIMARY)
        code_rect = code_surf.get_rect(center=(WIDTH//2, panel_y + 270))
        screen.blit(code_surf, code_rect)
        
        # Copy button
        copy_btn = pygame.Rect(WIDTH//2 + 150, 325, 100, 60)
        copy_hover = copy_btn.collidepoint(mouse)
        copy_color = SUCCESS if copy_hover else (34, 197, 94, 180)
        pygame.draw.rect(screen, copy_color, copy_btn, border_radius=10)
        copy_text = sml.render("COPY", True, TEXT_WHITE)
        copy_rect = copy_text.get_rect(center=copy_btn.center)
        screen.blit(copy_text, copy_rect)
        
        # Copy feedback
        if copy_feedback_alpha > 0:
            feedback_surf = pygame.Surface((220, 60), pygame.SRCALPHA)
            feedback_rect_bg = pygame.Rect(WIDTH//2 - 110, panel_y + 350, 220, 60)
            pygame.draw.rect(feedback_surf, (*SUCCESS, copy_feedback_alpha), (0, 0, 220, 60), border_radius=10)
            screen.blit(feedback_surf, (WIDTH//2 - 110, panel_y + 350))
            
            # Vẽ icon checkmark
            if copy_feedback_alpha > 100:
                check_x = WIDTH//2 - 70
                check_y = panel_y + 380
                # Vẽ dấu tick
                pygame.draw.line(screen, TEXT_WHITE, (check_x, check_y), (check_x + 8, check_y + 8), 4)
                pygame.draw.line(screen, TEXT_WHITE, (check_x + 8, check_y + 8), (check_x + 18, check_y - 8), 4)
            
            feedback_text = med.render("Đã sao chép!", True, TEXT_WHITE)
            feedback_text_rect = feedback_text.get_rect(center=(WIDTH//2 + 20, panel_y + 380))
            screen.blit(feedback_text, feedback_text_rect)
            copy_feedback_alpha = max(0, copy_feedback_alpha - 5)
        
        # Back hint
        back_surf = tiny.render("Nhấn ESC để hủy", True, TEXT_GRAY)
        back_rect = back_surf.get_rect(center=(WIDTH//2, panel_y + panel_h - 40))
        screen.blit(back_surf, back_rect)

    try:
        while True:
            msg = q.get_nowait()
            
            if msg['type'] == 'joined':
                player_role = msg['player']
            
            elif msg['type'] == 'start':
                if player_role is not None:
                    game_mode = True
                    stop_listener = True
                    
                    if listener_thread and listener_thread.is_alive():
                        listener_thread.join(timeout=2.0)
                    
                    cleared = 0
                    while not q.empty():
                        try:
                            q.get_nowait()
                            cleared += 1
                        except:
                            break
                    
                    time.sleep(0.3)
                    
                    import game
                    game.main(my_name, room, socket_client, msg['names'], player_role)
                    
                    state = "menu"
                    player_role = None
                    room = ""
                    socket_client = None
                    stop_listener = False
                    game_mode = False
            
            elif msg['type'] == 'full':
                state = "menu"
                if socket_client:
                    socket_client.close()
                    socket_client = None
    
    except queue.Empty:
        pass

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()