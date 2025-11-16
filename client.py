# client.py
import socket
import threading
import pickle
import tkinter as tk
from tkinter import messagebox

HOST = '127.0.0.1'
PORT = 65432

BOARD_SIZE = 15
CELL = 32

class CaroClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Caro Client (15x15)")
        self.symbol = None
        self.current = None
        self.game_over = False

        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE*CELL, height=BOARD_SIZE*CELL, bg="white")
        self.canvas.pack()
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối server:\n{e}")
            self.root.destroy()
            return

        # start receive thread
        threading.Thread(target=self.receive_loop, daemon=True).start()
        self.root.mainloop()

    def draw_grid(self):
        for i in range(BOARD_SIZE+1):
            x = i * CELL
            self.canvas.create_line(x, 0, x, BOARD_SIZE*CELL, fill="#aaa")
            y = i * CELL
            self.canvas.create_line(0, y, BOARD_SIZE*CELL, y, fill="#aaa")

    def on_click(self, event):
        if self.game_over:
            return
        if self.symbol is None:
            return
        # only allow if it's this client's turn
        if self.current != self.symbol:
            # optional: show message
            # messagebox.showinfo("Info", "Chưa tới lượt bạn")
            return
        x = event.x // CELL
        y = event.y // CELL
        # send move to server
        move = {'type':'move', 'x': x, 'y': y, 'symbol': self.symbol}
        try:
            self.sock.sendall(pickle.dumps(move))
        except Exception as e:
            print("Gửi move lỗi:", e)

    def receive_loop(self):
        try:
            while True:
                data = self.sock.recv(8192)
                if not data:
                    break
                try:
                    obj = pickle.loads(data)
                except Exception:
                    continue

                t = obj.get('type')
                if t == 'init':
                    self.symbol = obj.get('symbol')
                    self.current = obj.get('current')
                    self.game_over = obj.get('game_over', False)
                    # update board if any
                    b = obj.get('board')
                    if b:
                        self.update_board(b)
                    self.show_info(f"Bạn là {self.symbol}.")
                elif t == 'update':
                    self.current = obj.get('current')
                    self.game_over = obj.get('game_over', False)
                    b = obj.get('board')
                    if b:
                        self.update_board(b)
                    # enable/disable visually by title
                    self.update_title()
                elif t == 'error':
                    msg = obj.get('msg','')
                    self.show_info(msg)
                elif t == 'result':
                    winner = obj.get('winner')
                    if winner == 'Draw':
                        messagebox.showinfo("Kết quả", "Trận hòa!")
                    else:
                        messagebox.showinfo("Kết quả", f"Người chơi {winner} thắng!")
                    self.game_over = True
                # else ignore
        except Exception as e:
            print("Lỗi nhận:", e)
        finally:
            try:
                self.sock.close()
            except:
                pass
            self.root.after(0, lambda: messagebox.showwarning("Ngắt", "Ngắt kết nối từ server."))
            self.root.after(0, self.root.destroy)

    def update_board(self, board):
        # clear pieces tag
        self.canvas.delete("piece")
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                v = board[y][x]
                if v:
                    cx = x*CELL + CELL//2
                    cy = y*CELL + CELL//2
                    color = "red" if v == 'X' else "blue"
                    self.canvas.create_text(cx, cy, text=v, fill=color, font=("Arial", 14, "bold"), tags="piece")
        self.update_title()

    def update_title(self):
        title = f"Caro - Bạn: {self.symbol} | Lượt: {self.current}"
        if self.game_over:
            title += " | KẾT THÚC"
        self.root.title(title)

    def show_info(self, msg):
        print("INFO:", msg)

if __name__ == "__main__":
    CaroClient()
