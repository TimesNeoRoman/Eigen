
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import urllib.request
import json

class DiceBettingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("주사위 합 10 넘기기 게임")
        self.root.geometry("800x550")

        # --- 디자인 설정 ---
        self.COLOR_BG = "#2E2E2E"
        self.COLOR_TEXT = "#EAEAEA"
        self.COLOR_ACCENT = "#FFD700"  # Gold
        self.COLOR_SUCCESS = "#4CAF50" # Green
        self.COLOR_FAILURE = "#F44336" # Red
        self.COLOR_INFO = "#2196F3"   # Blue
        self.COLOR_BTN = "#4A4A4A"

        self.root.config(bg=self.COLOR_BG)

        # 게임 변수
        self.coins = 3
        self.dice_values = [0, 0, 0]
        self.current_stage = 0
        self.round_number = 0
        self.max_rounds = 7

        # UI 요소 설정
        self.setup_ui()
        self.start_new_round()

    def setup_ui(self):
        # --- 상단 정보 프레임 ---
        top_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        top_frame.pack(pady=(20, 10), padx=20, fill="x")

        self.info_label = tk.Label(top_frame, text="", font=("Malgun Gothic", 11), justify=tk.LEFT, bg=self.COLOR_BG, fg=self.COLOR_TEXT)
        self.info_label.pack(side="left")

        self.coins_label = tk.Label(top_frame, text=f"남은 코인: {self.coins}", font=("Malgun Gothic", 14, "bold"), bg=self.COLOR_BG, fg=self.COLOR_ACCENT)
        self.coins_label.pack(side="right")

        # --- 주사위 디스플레이 ---
        self.dice_display = tk.Label(self.root, text="주사위: [ ? ] [ ? ] [ ? ]", font=("Malgun Gothic", 28, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TEXT)
        self.dice_display.pack(pady=20)

        # --- 상태 메시지 ---
        self.status_label = tk.Label(self.root, text="새로운 라운드를 시작합니다.", font=("Malgun Gothic", 12), bg=self.COLOR_BG, fg=self.COLOR_INFO)
        self.status_label.pack(pady=10)

        # --- 베팅 버튼 프레임 ---
        bet_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        bet_frame.pack(pady=15)
        
        btn_font = ("Malgun Gothic", 10, "bold")
        btn_style = {"font": btn_font, "bg": self.COLOR_BTN, "fg": self.COLOR_TEXT, "relief": tk.RAISED, "borderwidth": 3, "width": 18, "pady": 5}

        self.bet_button_over = tk.Button(bet_frame, text="▲ 10을 넘는다 (Over)", **btn_style, command=lambda: self.place_bet('over'))
        self.bet_button_over.pack(side=tk.LEFT, padx=10)

        self.bet_button_under = tk.Button(bet_frame, text="▼ 10 이하다 (Under)", **btn_style, command=lambda: self.place_bet('under'))
        self.bet_button_under.pack(side=tk.LEFT, padx=10)

        # --- 진행 버튼 ---
        self.next_roll_button = tk.Button(self.root, text="다음 주사위 굴리기", font=btn_font, bg=self.COLOR_INFO, fg=self.COLOR_TEXT, relief=tk.RAISED, borderwidth=3, width=25, pady=4, command=self.next_roll)
        self.next_roll_button.pack(pady=10)
        
        self.new_round_button = tk.Button(self.root, text="새 라운드 시작", font=btn_font, relief=tk.RAISED, borderwidth=3, width=25, pady=4, command=self.start_new_round, state=tk.DISABLED)
        self.new_round_button.pack(pady=5)

        # --- 결과 메시지 ---
        self.result_label = tk.Label(self.root, text="", font=("Malgun Gothic", 12, "bold"), wraplength=750, justify=tk.CENTER, bg=self.COLOR_BG)
        self.result_label.pack(pady=(15, 0))


    def start_new_round(self):
        if self.round_number >= self.max_rounds:
            messagebox.showinfo("게임 종료", f"7라운드가 모두 끝났습니다. 최종 코인: {self.coins}")
            self.root.quit()
            return

        if self.coins == 0:
            self.show_bankruptcy_screen()
            return

        self.round_number += 1
        self.dice_values = [0, 0, 0]
        self.current_stage = 0
        self.update_display()
        
        self.bet_button_over.config(state=tk.NORMAL)
        self.bet_button_under.config(state=tk.NORMAL)
        self.next_roll_button.config(state=tk.NORMAL)
        self.new_round_button.config(state=tk.DISABLED)
        self.result_label.config(text="")


    def next_roll(self):
        self.current_stage += 1
        if self.current_stage > 2:
            # 베팅 없이 모든 주사위를 굴린 경우
            self.dice_values[2] = random.randint(1, 6)
            self.status_label.config(text=f"베팅하지 않았습니다. 최종 합: {sum(self.dice_values)}")
            self.end_round()
            return

        self.dice_values[self.current_stage - 1] = random.randint(1, 6)
        self.update_display()
        
        if self.current_stage == 2: # 마지막 굴리기 기회
            self.next_roll_button.config(text="결과 확인 (베팅 안함)")


    def place_bet(self, choice):
        min_bets = {0: 1, 1: 2, 2: 3}
        min_bet = min_bets[self.current_stage]

        bet_amount_str = simpledialog.askstring("베팅", f"얼마를 베팅하시겠습니까? (최소: {min_bet})", parent=self.root)

        try:
            bet_amount = int(bet_amount_str)
            if bet_amount < min_bet:
                messagebox.showwarning("베팅 오류", f"최소 {min_bet} 코인을 베팅해야 합니다.")
                return
            if bet_amount > self.coins:
                messagebox.showwarning("베팅 오류", "가진 코인보다 많이 베팅할 수 없습니다.")
                return
        except (ValueError, TypeError):
            return

        self.coins -= bet_amount
        self.bet_button_over.config(state=tk.DISABLED)
        self.bet_button_under.config(state=tk.DISABLED)
        self.next_roll_button.config(state=tk.DISABLED)
        self.status_label.config(text="주사위를 굴립니다...", fg="black")
        self.update_display() # 코인 즉시 업데이트
        
        # 순차적으로 주사위 굴리기 시작
        self.sequential_roll(self.current_stage, choice, bet_amount)

    def sequential_roll(self, dice_index, choice, bet_amount):
        if dice_index < 3:
            self.dice_values[dice_index] = random.randint(1, 6)
            self.update_display()
            # 2초 후에 다음 주사위를 굴리도록 예약
            self.root.after(2000, lambda: self.sequential_roll(dice_index + 1, choice, bet_amount))
        else:
            # 모든 주사위를 굴렸으면 결과 처리
            self.resolve_bet(choice, bet_amount)

    def resolve_bet(self, choice, bet_amount):
        payouts = {0: 4, 1: 3, 2: 2}
        total = sum(self.dice_values)
        result = 'over' if total > 10 else 'under'

        if choice == result:
            winnings = bet_amount * payouts[self.current_stage]
            self.coins += winnings
            self.status_label.config(text="라운드 종료!", fg=self.COLOR_TEXT)
            self.result_label.config(text=f"성공! {winnings} 코인을 얻었습니다.\n합: {total}", fg=self.COLOR_SUCCESS)
        else:
            try:
                with urllib.request.urlopen("https://korean-advice-open-api.vercel.app/api/advice") as response:
                    data = json.loads(response.read().decode())
                    quote = data.get('message') or data.get('advice', '다음에 더 잘할 수 있을 거예요.')
                    author = data.get('author', '')
                    author_profile = data.get('author_profile', '')
                    
                    full_message = f'"{quote}"'
                    if author:
                        full_message += f"\n- {author}"
                    if author_profile:
                        full_message += f"\n({author_profile})"

            except Exception:
                full_message = "명언을 가져오는 데 실패했습니다."
            
            self.status_label.config(text="라운드 종료!", fg=self.COLOR_TEXT)
            self.result_label.config(text=f"실패! {bet_amount} 코인을 잃었습니다.\n합: {total}\n\n{full_message}", fg=self.COLOR_FAILURE)
        
        self.end_round()


    def end_round(self):
        self.update_display()
        self.bet_button_over.config(state=tk.DISABLED)
        self.bet_button_under.config(state=tk.DISABLED)
        self.next_roll_button.config(state=tk.DISABLED)
        self.new_round_button.config(state=tk.NORMAL)
        
        if self.coins == 0:
            self.show_bankruptcy_screen()

    def show_bankruptcy_screen(self):
        # 모든 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 파산 메시지 표시
        bankruptcy_label = tk.Label(self.root, text="파산", font=("Malgun Gothic", 100, "bold"), bg=self.COLOR_BG, fg=self.COLOR_FAILURE)
        bankruptcy_label.pack(pady=(100, 0), expand=True)

        # 새 게임 버튼
        btn_font = ("Malgun Gothic", 12, "bold")
        new_game_button = tk.Button(self.root, text="새 게임", font=btn_font, bg=self.COLOR_BTN, fg=self.COLOR_TEXT, relief=tk.RAISED, borderwidth=3, width=20, pady=8, command=self.restart_game)
        new_game_button.pack(pady=(20, 100), expand=True)

    def restart_game(self):
        # 모든 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()

        # 게임 상태 초기화
        self.coins = 3
        self.dice_values = [0, 0, 0]
        self.current_stage = 0
        self.round_number = 0

        # UI 재생성 및 새 라운드 시작
        self.setup_ui()
        self.start_new_round()


    def update_display(self):
        stages_info = {
            0: "1단계: 주사위 0개 (최소 베팅: 1, 성공 시 4배)",
            1: "2단계: 주사위 1개 (최소 베팅: 2, 성공 시 3배)",
            2: "3단계: 주사위 2개 (최소 베팅: 3, 성공 시 2배)"
        }
        self.info_label.config(text=f"라운드: {self.round_number}/{self.max_rounds}\n현재: {stages_info.get(self.current_stage, '라운드 종료')}")
        
        self.coins_label.config(text=f"남은 코인: {self.coins}")

        dice_str = " ".join([f"[{val if val != 0 else '?'}]" for val in self.dice_values])
        self.dice_display.config(text=f"주사위: {dice_str}")

        if self.current_stage == 0:
            self.status_label.config(text="베팅하거나 다음 주사위를 굴리세요.", fg=self.COLOR_INFO)
            self.next_roll_button.config(text="다음 주사위 굴리기")
        elif self.current_stage == 1:
            self.status_label.config(text=f"첫 주사위는 {self.dice_values[0]}입니다. 베팅하거나 굴리세요.", fg=self.COLOR_INFO)
        elif self.current_stage == 2:
            self.status_label.config(text=f"두 주사위는 {self.dice_values[0]}, {self.dice_values[1]}입니다. 베팅하거나 결과를 확인하세요.", fg=self.COLOR_INFO)
            self.next_roll_button.config(text="결과 확인 (베팅 안함)")


if __name__ == "__main__":
    root = tk.Tk()
    game = DiceBettingGame(root)
    root.mainloop()
