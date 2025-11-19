# menu.py - PHIÊN BẢN HOÀN CHỈNH, KHÔNG CÒN LỖI THOÁT CHƯƠNG TRÌNH
import pygame
import socket
import json
import random
import string
import threading
import queue
import pyperclip
import sys

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

# Biến toàn cục
socket_client = None
my_name = ""
room = ""
state = "menu"
q = queue.Queue()
stop_listener = False
player_role = None

def listen_thread():
    global stop_listener, socket_client
    while not stop_listener:
        try:
            data = socket_client.recv(1024).decode('utf-8')
            if not data:
                break
            msg = json.loads(data)
            q.put(msg)
        except:
            break

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
                try: socket_client.close()
                except: pass

        if state == "menu":
            name_box.event(e)
            room_box.event(e)

            if e.type == pygame.MOUSEBUTTONDOWN:
                # TẠO PHÒNG
                if pygame.Rect(100,300,400,90).collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Người chơi 1"
                    if not my_name: continue
                    socket_client = socket.socket()
                    socket_client.connect(('127.0.0.1', 5555))
                    room = gen_code()
                    socket_client.send(json.dumps({'type':'join','room':room,'name':my_name}).encode())
                    stop_listener = False
                    threading.Thread(target=listen_thread, daemon=True).start()
                    state = "waiting"

                # THAM GIA PHÒNG
                if pygame.Rect(100,530,400,90).collidepoint(e.pos):
                    my_name = name_box.text.strip() or "Người chơi 2"
                    room = room_box.text.strip().upper()
                    if len(room) != 6: continue
                    socket_client = socket.socket()
                    socket_client.connect(('127.0.0.1', 5555))
                    socket_client.send(json.dumps({'type':'join','room':room,'name':my_name}).encode())
                    stop_listener = False
                    threading.Thread(target=listen_thread, daemon=True).start()
                    state = "waiting"

        if state == "waiting":
            if e.type == pygame.MOUSEBUTTONDOWN and copy_rect.collidepoint(e.pos):
                pyperclip.copy(room)
                copied_alpha = 255
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                state = "menu"
                stop_listener = True
                if socket_client:
                    try: socket_client.close()
                    except: pass
                    socket_client = None

    # VẼ GIAO DIỆN
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

    # XỬ LÝ TIN TỪ SERVER
    try:
        while True:
            msg = q.get_nowait()
            print(f"Menu nhận: {msg}")

            if msg['type'] == 'joined':
                player_role = msg['player']
                print(f"Đã vào phòng - Bạn là Player {player_role}")

            elif msg['type'] == 'start':
                if player_role is not None:
                    print(f"BẮT ĐẦU GAME! Player {player_role}")
                    import game
                    # CHỈ CHẠY GAME, KHÔNG THOÁT MENU
                    game.main(my_name, room, socket_client, msg['names'], player_role)
                    # Sau khi game kết thúc → quay lại menu
                    state = "menu"
                    player_role = None
                    room = ""
                    socket_client = None  # socket đã được đóng trong game.py
                else:
                    print("Lỗi: player_role chưa có!")

            elif msg['type'] == 'full':
                txt("Phòng đã đầy!", big, (255,100,100), WIDTH//2, 600)
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