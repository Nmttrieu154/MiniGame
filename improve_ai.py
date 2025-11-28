# improve_ai.py - Cải thiện AI từ dữ liệu train đã có
import json
import os
from ai import CaroAI

def analyze_model():
    """Phân tích model hiện tại"""
    print("\n" + "="*70)
    print("🔍 PHÂN TÍCH MODEL AI")
    print("="*70)
    
    ai = CaroAI()
    
    if not os.path.exists("caro_model.json"):
        print("❌ Không có model. Hãy train trước!")
        return
    
    with open("caro_model.json", 'r') as f:
        data = json.load(f)
    
    positions = data.get('positions', {})
    games = data.get('games_played', 0)
    
    print(f"\n📊 THỐNG KÊ MODEL:")
    print(f"  • Tổng games train: {games}")
    print(f"  • Positions learned: {len(positions)}")
    
    if len(positions) == 0:
        print("❌ Model trống, hãy train trước!")
        return
    
    # Phân tích win rate
    total_wins = 0
    total_moves = 0
    best_moves = {}
    worst_moves = {}
    
    for board_key, pos_data in positions.items():
        moves_data = pos_data.get('moves', {})
        wins = pos_data.get('wins', 0)
        total = pos_data.get('total', 0)
        
        total_wins += wins
        total_moves += total
        
        # Tìm nước tốt nhất & tệ nhất
        for move_key, score in moves_data.items():
            if move_key not in best_moves:
                best_moves[move_key] = 0
                worst_moves[move_key] = 0
            
            best_moves[move_key] += score
            if score < 0:
                worst_moves[move_key] += abs(score)
    
    win_rate = (total_wins / total_moves * 100) if total_moves > 0 else 0
    
    print(f"\n📈 WIN RATE:")
    print(f"  • Tổng moves: {total_moves}")
    print(f"  • Moves thắng: {total_wins}")
    print(f"  • Win rate: {win_rate:.1f}%")
    
    # Top moves tốt nhất
    if best_moves:
        top_best = sorted(best_moves.items(), key=lambda x: -x[1])[:5]
        print(f"\n⭐ TOP 5 NƯỚC TỐT NHẤT:")
        for i, (move, score) in enumerate(top_best, 1):
            print(f"  {i}. Move {move}: Score {score:.1f}")
    
    # Top moves tệ nhất
    if worst_moves:
        top_worst = sorted(worst_moves.items(), key=lambda x: -x[1])[:5]
        print(f"\n❌ TOP 5 NƯỚC TỀ NHẤT:")
        for i, (move, score) in enumerate(top_worst, 1):
            print(f"  {i}. Move {move}: Score {score:.1f}")
    
    print("\n" + "="*70)

def improve_from_data():
    """Cải thiện AI bằng cách re-train từ dữ liệu cũ"""
    print("\n" + "="*70)
    print("🚀 CẢI THIỆN AI TỪ DỮ LIỆU ĐÃ TRAIN")
    print("="*70)
    
    ai = CaroAI()
    
    if not os.path.exists("caro_model.json"):
        print("❌ Không có model. Hãy train trước!")
        return
    
    with open("caro_model.json", 'r') as f:
        data = json.load(f)
    
    positions = data.get('positions', {})
    games = data.get('games_played', 0)
    
    print(f"\n📊 Model hiện tại:")
    print(f"  • Games: {games}")
    print(f"  • Positions: {len(positions)}")
    
    if len(positions) < 100:
        print("\n⚠️  Model quá nhỏ, hãy train thêm!")
        return
    
    print("\n🎯 CÁC CHIẾN LƯỢC CẢI THIỆN:")
    print("  1️⃣  Phân tích positions - tìm pattern thắng")
    print("  2️⃣  Gia tăng depth Minimax")
    print("  3️⃣  Học từ nước tốt nhất")
    print("  4️⃣  Huấn luyện thêm (Self-Play lần 2)")
    print("  5️⃣  Xóa dữ liệu cũ và train lại")
    
    choice = input("\nChọn (1-5): ").strip()
    
    if choice == "1":
        analyze_model()
    
    elif choice == "2":
        print("\n⚠️  Đang tăng depth Minimax...")
        # Cập nhật depth trong ai.py (depth 3 -> 4)
        print("✅ Hãy chỉnh trong ai.py: depth = 4")
        print("   Sau đó train thêm để AI học từ depth lớn hơn")
    
    elif choice == "3":
        print("\n🎯 Học từ nước tốt nhất...")
        print(f"📚 Phân tích {len(positions)} positions...")
        
        best_overall = {}
        for board_key, pos_data in positions.items():
            moves_data = pos_data.get('moves', {})
            for move_key, score in moves_data.items():
                if move_key not in best_overall:
                    best_overall[move_key] = 0
                best_overall[move_key] += score
        
        top_moves = sorted(best_overall.items(), key=lambda x: -x[1])[:10]
        print("\n⭐ TOP 10 NƯỚC ĐI ĐƯỢC TIN TỨC NHẤT:")
        for i, (move, score) in enumerate(top_moves, 1):
            print(f"  {i}. {move}: {score:.1f} points")
    
    elif choice == "4":
        print("\n🎮 Huấn luyện thêm từ dữ liệu cũ...")
        num = input("Số games muốn train thêm (gợi ý: 500): ").strip()
        try:
            num = int(num)
            print(f"\n✅ Sẽ train thêm {num} games...")
            ai.train_self_play(num_games=num)
        except:
            print("❌ Nhập sai!")
    
    elif choice == "5":
        confirm = input("\n⚠️  BẠN CHẮC CHẮN? Sẽ xóa hết dữ liệu cũ! (yes/no): ").strip()
        if confirm.lower() == "yes":
            os.remove("caro_model.json")
            print("✅ Đã xóa model cũ!")
            print("🚀 Hãy chạy: python train_ai.py (để train từ đầu)")
        else:
            print("❌ Hủy bỏ!")

def compare_versions():
    """So sánh performance trước/sau"""
    print("\n" + "="*70)
    print("📊 SO SÁNH PERFORMANCE")
    print("="*70)
    
    ai = CaroAI()
    
    with open("caro_model.json", 'r') as f:
        data = json.load(f)
    
    positions = data.get('positions', {})
    
    win_rate_samples = []
    for board_key, pos_data in list(positions.items())[:100]:
        wins = pos_data.get('wins', 0)
        total = pos_data.get('total', 1)
        win_rate_samples.append(wins / total)
    
    avg_win_rate = sum(win_rate_samples) / len(win_rate_samples) * 100 if win_rate_samples else 0
    
    print(f"\n📈 HIỆU SUẤT HIỆN TẠI:")
    print(f"  • Avg Win Rate (sample 100): {avg_win_rate:.1f}%")
    print(f"  • Total Positions: {len(positions)}")
    print(f"  • Model Quality: {'🔥 Excellent' if avg_win_rate > 60 else '🟡 Good' if avg_win_rate > 40 else '⚠️  Cần cải thiện'}")
    
    print("\n💡 KHUYẾN NGHỊ:")
    if avg_win_rate < 40:
        print("  • Train thêm 500+ games")
        print("  • Depth Minimax quá nông")
    elif avg_win_rate < 60:
        print("  • AI đang trung bình, train thêm 1000 games")
    else:
        print("  • AI rất mạnh! Có thể train 10000 games để siêu mạnh")
    
    print("\n" + "="*70)

def main():
    print("\n" + "="*70)
    print("🤖 AI IMPROVEMENT SYSTEM")
    print("="*70)
    print("\nCác tùy chọn:")
    print("  1️⃣  Phân tích model (analyze)")
    print("  2️⃣  Cải thiện AI (improve)")
    print("  3️⃣  So sánh performance")
    print("  0️⃣  Thoát")
    
    choice = input("\nChọn (0-3): ").strip()
    
    if choice == "1":
        analyze_model()
    elif choice == "2":
        improve_from_data()
    elif choice == "3":
        compare_versions()
    elif choice == "0":
        print("👋 Tạm biệt!")
    else:
        print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()