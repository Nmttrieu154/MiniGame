# menu.py - HOÀN CHỈNH - FIX LISTENER DỪNG NGAY
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
WIDTH, HEIGHT = 600, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cờ Caro Online")
clock = pygame.time.Clock()

BG = (15, 15, 35)
ACC = (70, 130, 255)
HOV = (100, 160, 255)
TXT = (255, 255, 255)
GRN = (0, 255, 120)

def font(size, bold=False):
    return pygame.font.SysFont("Segoe UI", size, bold=bold)

title = font(64, True)
big = font(36, True)
med = font(30)
sml = font(24)

def txt(text, fnt, col, x, y, center=True):
    s = fnt.render(text, True, col)
    r = s.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    screen.blit(s, r)

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Box:
    def __init__(self, x, y, w, h, hint):
        self.r = pygame.Rect(x, y, w, h)
        self.text = ""
        self.hint = hint
        self.active = False
    
    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.r.collidepoint(e.pos)
        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_v and (e.mod & pygame.KMOD_CTRL):
                self.text = pyperclip.paste()
            elif e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 20:
                self.text += e.unicode
    
    def draw(self):
        c = (70,70,140) if self.active else (40,40,90)
        pygame.draw.rect(screen, c, self.r, border_radius=12)
        pygame.draw.rect(screen, (120,120,220), self.r, 3, border_radius=12)
        t = self.text or self.hint
        col = TXT if self.text else (150,150,150)
        screen.blit(med.render(t, True, col), (self.r.x+15, self.r.y+20))

name_box = Box(100, 180, 400, 70, "Nhập tên của bạn")
room_box = Box(100, 430, 300, 70, "Dán mã phòng (Ctrl+V)")

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
            # Kiểm tra game_mode TRƯỚC KHI recv
            if game_mode:
                print("[MENU] 🛑 Game mode ON - dừng listener ngay")
                break
            
            # Set timeout để không bị block
            try:
                socket_client.settimeout(0.5)
            except:
                break
            
            try:
                data = socket_client.recv(1024).decode('utf-8')
            except socket.timeout:
                continue  # Timeout, kiểm tra lại game_mode
            except:
                break
            
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
                    
                    # Double check game_mode
                    if game_mode:
                        print(f"[MENU] ⏭️  Bỏ qua (game mode ON): {msg}")
                        continue
                    
                    q.put(msg)
                    print(f"[MENU] 📩 Nhận: {msg}")
                except Exception as e:
                    print(f"[MENU] ❌ Parse error: {e}")
                    continue
                    
        except Exception as e:
            if not stop_listener and not game_mode:
                print(f"[MENU] ❌ Socket error: {e}")
            break
    
    # Reset timeout về blocking mode
    try:
        if socket_client:
            socket_client.settimeout(None)
    except:
        pass
    
    print("[MENU] 🛑 Menu listener đã dừng hoàn toàn")

copy_rect = pygame.Rect(420, 360, 70, 70)
copied_alpha = 0

running = True
while running:
    screen.fill(BG)
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
                if pygame.Rect(100,300,400,90).collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Người chơi 1"
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
                        print(f"[MENU] 📡 Bắt đầu listener cho phòng {room}")
                    except Exception as e:
                        print(f"[MENU] ❌ Lỗi tạo phòng: {e}")
                        state = "menu"
                
                if pygame.Rect(100,530,400,90).collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Người chơi 2"
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
                        print(f"[MENU] 📡 Bắt đầu listener, join phòng {room}")
                    except Exception as e:
                        print(f"[MENU] ❌ Lỗi join phòng: {e}")
                        state = "menu"
        
        elif state == "waiting":
            if e.type == pygame.MOUSEBUTTONDOWN and copy_rect.collidepoint(e.pos):
                pyperclip.copy(room)
                copied_alpha = 255
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
        txt("CỜ CARO ONLINE", title, (100,200,255), WIDTH//2, 80)
        txt("Copy & Paste mã phòng thoải mái!", sml, (180,180,180), WIDTH//2, 130)
        name_box.draw()
        room_box.draw()
        
        for rect, text, y in [(pygame.Rect(100,300,400,90), "TẠO PHÒNG MỚI", 345),
                              (pygame.Rect(100,530,400,90), "THAM GIA PHÒNG", 575)]:
            col = HOV if rect.collidepoint(mouse) else ACC
            pygame.draw.rect(screen, col, rect, border_radius=20)
            txt(text, big, TXT, WIDTH//2, y)
    
    elif state == "waiting":
        txt("Đang chờ người chơi khác...", big, (255,255,100), WIDTH//2, 200)
        txt("Mã phòng:", med, TXT, WIDTH//2, 300)
        txt(room, big, GRN, WIDTH//2, 360)
        
        pygame.draw.rect(screen, (0,180,0), copy_rect, border_radius=15)
        pygame.draw.rect(screen, (0,255,0), copy_rect, 5, border_radius=15)
        txt("COPY", sml, TXT, copy_rect.centerx, copy_rect.centery-10)
        pygame.draw.rect(screen, TXT, (copy_rect.centerx-15, copy_rect.centery+8, 30, 20), 2)
        pygame.draw.rect(screen, TXT, (copy_rect.centerx-5, copy_rect.centery+3, 20, 15), 2)
        
        if copied_alpha > 0:
            s = pygame.Surface((200,50))
            s.set_alpha(copied_alpha)
            s.fill((0,220,0))
            screen.blit(s, (WIDTH//2-100, 500))
            txt("Đã copy!", med, (0,0,0), WIDTH//2, 525)
            copied_alpha = max(0, copied_alpha - 15)
        
        txt("Nhấn ESC để thoát", sml, (180,180,180), WIDTH//2, 600)

    try:
        while True:
            msg = q.get_nowait()
            
            if msg['type'] == 'joined':
                player_role = msg['player']
                print(f"[MENU] ✅ Đã join với role: {player_role}")
            
            elif msg['type'] == 'start':
                if player_role is not None:
                    print("[MENU] 🎮 Bắt đầu game...")
                    
                    # Bước 1: Đặt cờ game_mode NGAY
                    game_mode = True
                    print("[MENU] 🚫 Đã BẬT game_mode")
                    
                    # Bước 2: Đặt cờ stop
                    stop_listener = True
                    
                    # Bước 3: Đợi listener dừng
                    if listener_thread and listener_thread.is_alive():
                        print("[MENU] ⏳ Đang đợi listener dừng...")
                        
                        # Đợi tối đa 3 giây
                        for i in range(30):
                            if not listener_thread.is_alive():
                                break
                            time.sleep(0.1)
                        
                        if listener_thread.is_alive():
                            print("[MENU] ⚠️ Listener chưa dừng sau 3 giây!")
                        else:
                            print("[MENU] ✅ Listener đã dừng")
                    
                    # Bước 4: Clear queue
                    cleared = 0
                    while not q.empty():
                        try:
                            q.get_nowait()
                            cleared += 1
                        except:
                            break
                    print(f"[MENU] 🗑️  Đã xóa {cleared} messages cũ")
                    
                    # Bước 5: Đợi thêm
                    time.sleep(0.5)
                    
                    print("[MENU] 🔄 Chuyển socket sang game...")
                    import game
                    game.main(my_name, room, socket_client, msg['names'], player_role)
                    
                    print("[MENU] 🔙 Quay lại menu...")
                    state = "menu"
                    player_role = None
                    room = ""
                    socket_client = None
                    stop_listener = False
                    game_mode = False
            
            elif msg['type'] == 'full':
                print("[MENU] ⚠️ Phòng đầy")
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