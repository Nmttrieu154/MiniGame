# train_ai.py - Train AI (Fixed)
import sys
import time
from ai import CaroAI

def main():
    print("\n" + "="*70)
    print("🤖 CARO AI TRAINING - Self-Play Method")
    print("="*70)
    print()
    print("🎮 Các tùy chọn:")
    print("  1️⃣  Quick Train (50 games) - ~2 phút")
    print("  2️⃣  Normal Train (100 games) - ~5 phút")
    print("  3️⃣  Good Train (200 games) - ~10 phút")
    print("  4️⃣  Strong Train (500 games) - ~25 phút")
    print("  5️⃣  Very Strong (1000 games) - ~50 phút")
    print("  6️⃣  EXTREME Train (10000 games) - ~8 giờ 🔥")
    print("  0️⃣  Thoát")
    print()
    
    choice = input("Chọn (0-6): ").strip()
    
    games_map = {
        "1": 50,
        "2": 100,
        "3": 200,
        "4": 500,
        "5": 1000,
        "6": 10000,
        "0": 0
    }
    
    num_games = games_map.get(choice, 0)
    
    if num_games == 0:
        print("\n👋 Tạm biệt!")
        return
    
    if choice not in games_map:
        print("\n❌ Lựa chọn không hợp lệ!")
        return
    
    print()
    print("="*70)
    print(f"🚀 Khởi tạo AI Training...")
    print("="*70)
    
    # Create AI (load model cũ nếu có)
    ai = CaroAI(difficulty="medium")
    print(f"📊 Trước train: {ai.get_model_info()}")
    print(f"✅ Sẽ cộng dồn +{num_games} games")
    print()
    
    # Start training
    start_time = time.time()
    
    try:
        ai.train_self_play(num_games=num_games)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        ai.save_knowledge()
        print(f"💾 Model saved: {ai.get_model_info()}")
        return
    
    # Time info
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    print()
    print("="*70)
    print("✅ HOÀN THÀNH TRAINING!")
    print("="*70)
    print(f"⏱️  Thời gian: {hours}h {minutes}m {seconds}s")
    print(f"📊 Model: {ai.get_model_info()}")
    print()
    print("💡 Các tùy chọn tiếp theo:")
    print("  1. Train thêm: python train_ai.py (AI sẽ khôn hơn)")
    print("  2. Chơi game: python menu.py")
    print()
    print("🎯 Mỗi lần train model sẽ được cải thiện!")
    print("   Càng train nhiều → AI càng khôn → Khó thắng hơn")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()