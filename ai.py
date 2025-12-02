# ai.py - AI mạnh với Minimax + Alpha-Beta + Learning
import json
import os
import random

class CaroAI:
    def __init__(self, difficulty="medium"):
        self.difficulty = difficulty
        self.model_path = "caro_model.json"
        self.knowledge = self._load_knowledge()
        self.is_trained = len(self.knowledge.get('positions', {})) > 200
        
        if self.is_trained:
            print(f"✅ Loaded TRAINED model - {len(self.knowledge['positions'])} positions")
        else:
            print(f"⚠️  Fresh model - learning from scratch")
    
    def _load_knowledge(self):
        """Load knowledge base"""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    data = json.load(f)
                    if len(data.get('positions', {})) > 50:
                        return data
            except:
                pass
        
        return {
            'positions': {},
            'games_played': 0,
            'total_positions': 0
        }
    
    def get_model_info(self):
        """Lấy thông tin model"""
        games = self.knowledge.get('games_played', 0)
        positions = len(self.knowledge.get('positions', {}))
        return f"{games} games, {positions} positions learned"
    
    def get_move(self, board, ai_symbol, player_symbol):
        """Lấy nước đi tốt nhất"""
        valid_moves = self._get_valid_moves(board)
        if not valid_moves:
            return None
        
        # 1. Thắng ngay
        for x, y in valid_moves:
            if self._check_win(board, x, y, ai_symbol):
                return (x, y)
        
        # 2. Block 5 liên tiếp ngay
        for x, y in valid_moves:
            if self._check_win(board, x, y, player_symbol):
                return (x, y)
        
        # 3. Tấn công: Nếu AI đánh ở đó = thắng (4 quân + 1 nước nữa)
        for x, y in valid_moves:
            board[y][x] = ai_symbol
            if self._count_max_line(board, x, y, ai_symbol) >= 4:
                board[y][x] = 0
                return (x, y)
            board[y][x] = 0
        
        # 4. Block chuỗi 4 của player (nguy hiểm cực độ!)
        for x, y in valid_moves:
            board[y][x] = player_symbol
            if self._count_max_line(board, x, y, player_symbol) >= 4:
                board[y][x] = 0
                return (x, y)
            board[y][x] = 0
        
        # 5. Block chuỗi 3 ở mọi hướng (player còn 1 nước là thắng)
        for x, y in valid_moves:
            for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
                count = self._count_line(board, x, y, player_symbol, dx, dy)
                if count >= 3:
                    return (x, y)
        
        # 5. Tạo chuỗi 4 của AI (chuẩn bị thắng)
        for x, y in valid_moves:
            board[y][x] = ai_symbol
            if self._count_max_line(board, x, y, ai_symbol) >= 4:
                board[y][x] = 0
                return (x, y)
            board[y][x] = 0
        
        # 6. Dùng Minimax nếu trained
        if self.is_trained and self.difficulty in ["medium", "hard"]:
            depth = 3 if self.difficulty == "hard" else 2
            return self._minimax_move(board, valid_moves, ai_symbol, player_symbol, depth)
        
        # 7. Heuristic
        return self._heuristic_move(board, valid_moves, ai_symbol, player_symbol)
    
    def _minimax_move(self, board, valid_moves, ai_sym, player_sym, depth):
        """Tìm nước đi tốt nhất bằng Minimax (nhanh)"""
        best_score = -float('inf')
        best_move = valid_moves[0]
        
        # Chỉ xét top 10 moves để nhanh
        for x, y in valid_moves[:10]:
            board[y][x] = ai_sym
            score = self._minimax(board, depth - 1, ai_sym, player_sym, -float('inf'), float('inf'), False)
            board[y][x] = 0
            
            if score > best_score:
                best_score = score
                best_move = (x, y)
        
        return best_move
    
    def _minimax(self, board, depth, ai_sym, player_sym, alpha, beta, is_max):
        """Minimax với Alpha-Beta Pruning"""
        # Terminal states
        if self._check_win_board(board, ai_sym):
            return 1000 + depth
        if self._check_win_board(board, player_sym):
            return -1000 - depth
        if depth == 0:
            return self._evaluate_board(board, ai_sym, player_sym)
        
        valid_moves = self._get_valid_moves(board)[:12]
        
        if is_max:
            max_eval = -float('inf')
            for x, y in valid_moves:
                board[y][x] = ai_sym
                eval_score = self._minimax(board, depth - 1, ai_sym, player_sym, alpha, beta, False)
                board[y][x] = 0
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for x, y in valid_moves:
                board[y][x] = player_sym
                eval_score = self._minimax(board, depth - 1, ai_sym, player_sym, alpha, beta, True)
                board[y][x] = 0
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
    
    def _evaluate_board(self, board, ai_sym, player_sym):
        """Đánh giá bàn cờ"""
        score = 0
        
        for y in range(15):
            for x in range(15):
                if board[y][x] == ai_sym:
                    score += self._position_value(board, x, y, ai_sym, player_sym)
                elif board[y][x] == player_sym:
                    score -= self._position_value(board, x, y, player_sym, ai_sym)
        
        return score
    
    def _position_value(self, board, x, y, symbol, opponent):
        """Giá trị của một vị trí"""
        value = 0
        
        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            count = self._count_line(board, x, y, symbol, dx, dy)
            opponent_count = self._count_line(board, x, y, opponent, dx, dy)
            
            if count >= 5:
                value += 10000
            elif count == 4:
                value += 500
            elif count == 3:
                value += 50
            elif count == 2:
                value += 5
            
            if opponent_count >= 4:
                value -= 100
            elif opponent_count == 3:
                value -= 20
        
        return value
    
    def _heuristic_move(self, board, valid_moves, ai_sym, player_sym):
        """Heuristic tốt"""
        best_score = -999
        best_moves = []
        
        for x, y in valid_moves[:50]:
            threat_ai = self._threat_score(board, x, y, ai_sym)
            threat_player = self._threat_score(board, x, y, player_sym)
            
            score = threat_ai * 20 + threat_player * 15
            
            if self._has_neighbor(board, x, y):
                score += 5
            
            dist = abs(x - 7) + abs(y - 7)
            score -= dist * 0.3
            
            if score > best_score:
                best_score = score
                best_moves = [(x, y)]
            elif abs(score - best_score) < 0.5:
                best_moves.append((x, y))
        
        return random.choice(best_moves) if best_moves else valid_moves[0]
    
    def _threat_score(self, board, x, y, symbol):
        """Tính threat score"""
        board[y][x] = symbol
        max_count = 0
        
        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            count = self._count_line(board, x, y, symbol, dx, dy)
            max_count = max(max_count, count)
        
        board[y][x] = 0
        return min(max_count, 5)
    
    def _count_line(self, board, x, y, symbol, dx, dy):
        """Đếm chuỗi"""
        count = 1
        for i in range(1, 5):
            nx, ny = x + dx*i, y + dy*i
            if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == symbol:
                count += 1
            else:
                break
        for i in range(1, 5):
            nx, ny = x - dx*i, y - dy*i
            if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == symbol:
                count += 1
            else:
                break
        return count
    
    def _count_max_line(self, board, x, y, symbol):
        """Đếm chuỗi dài nhất"""
        max_count = 0
        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            count = self._count_line(board, x, y, symbol, dx, dy)
            max_count = max(max_count, count)
        return max_count
    
    def _check_win(self, board, x, y, symbol):
        """Kiểm tra thắng"""
        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            if self._count_line(board, x, y, symbol, dx, dy) >= 5:
                return True
        return False
    
    def _check_win_board(self, board, symbol):
        """Kiểm tra thắng trên cả bàn"""
        for y in range(15):
            for x in range(15):
                if board[y][x] == symbol and self._check_win(board, x, y, symbol):
                    return True
        return False
    
    def _has_neighbor(self, board, x, y):
        """Có quân gần không"""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] != 0:
                    return True
        return False
    
    def _get_valid_moves(self, board):
        """Valid moves"""
        priority = []
        
        for y in range(15):
            for x in range(15):
                if board[y][x] == 0 and self._has_neighbor(board, x, y):
                    priority.append((x, y))
        
        return priority if priority else [(7, 7), (7, 8), (8, 7), (8, 8)]
    
    def _board_key(self, board):
        """Board key string"""
        return '|'.join(''.join(str(cell) for cell in row) for row in board)
    
    def save_knowledge(self):
        """Lưu knowledge"""
        with open(self.model_path, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def train_self_play(self, num_games=50):
        """Train bằng self-play"""
        start_games = self.knowledge.get('games_played', 0)
        total_games = start_games + num_games
        
        print(f"\n🎮 TRAINING {num_games} GAMES")
        print(f"📊 Cộng dồn: {start_games} + {num_games} = {total_games} games")
        print("="*60)
        
        game_lengths = []
        
        for game_num in range(num_games):
            current_game_num = start_games + game_num + 1
            board = [[0] * 15 for _ in range(15)]
            game_history = []
            move_count = 0
            
            while move_count < 225:
                ai_sym = 2 if move_count % 2 == 0 else 1
                player_sym = 3 - ai_sym
                
                valid = self._get_valid_moves(board)
                move = self._heuristic_move(board, valid, ai_sym, player_sym)
                
                if not move:
                    break
                
                x, y = move
                board[y][x] = ai_sym
                game_history.append((self._board_key(board), x, y, ai_sym))
                move_count += 1
                
                if self._check_win(board, x, y, ai_sym):
                    winner = ai_sym
                    game_lengths.append(move_count)
                    self._update_knowledge(game_history, winner)
                    print(f"[Game {current_game_num}/{total_games}] Symbol {winner} wins in {move_count} moves ✅")
                    break
            
            if (game_num + 1) % 10 == 0:
                self.knowledge['games_played'] = current_game_num
                self.save_knowledge()
                avg = sum(game_lengths[-10:]) / len(game_lengths[-10:]) if game_lengths else 0
                print(f"  💾 Saved - {len(self.knowledge['positions'])} positions | Avg: {avg:.1f} moves")
        
        self.knowledge['games_played'] = total_games
        self.save_knowledge()
        
        print("\n" + "="*60)
        print("✅ TRAINING DONE!")
        print(f"📊 Tổng games: {total_games}")
        print(f"📚 Positions learned: {len(self.knowledge['positions'])}")
        if game_lengths:
            print(f"📈 Avg game length: {sum(game_lengths) / len(game_lengths):.1f} moves")
        print(f"💾 Model saved to: {self.model_path}")
        print("\n🎯 Khi chơi: Dùng Minimax Depth 3-4 (rất mạnh)")
        print("="*60)
    
    def _update_knowledge(self, game_history, winner):
        """Update knowledge"""
        for board_key, x, y, symbol in game_history:
            if board_key not in self.knowledge['positions']:
                self.knowledge['positions'][board_key] = {
                    'moves': {},
                    'wins': 0,
                    'total': 0
                }
            
            move_key = f"{x},{y}"
            pos = self.knowledge['positions'][board_key]
            
            if move_key not in pos['moves']:
                pos['moves'][move_key] = 0
            
            if symbol == winner:
                pos['moves'][move_key] += 1
            else:
                pos['moves'][move_key] -= 0.5
            
            pos['total'] += 1
            if symbol == winner:
                pos['wins'] += 1