import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import urllib.request
import json
import math 

class DiceBettingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("주사위 합 10 넘기기 게임")
        # 창 크기 유지
        self.root.geometry("1100x750") 
        
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
        self.initial_coins_value = 3
        self.dice_values = [0, 0, 0]
        self.current_stage = 0
        self.round_number = 0
        self.max_rounds = 7
        
        self.profit_history = [] 

        # UI 요소 설정
        self.setup_ui()

    def setup_ui(self):
        # 전체 프레임 (왼쪽 게임 영역과 오른쪽 기록 영역 분리)
        main_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- [좌측] 게임 영역 프레임 ---
        game_frame = tk.Frame(main_frame, bg=self.COLOR_BG, width=750)
        game_frame.pack(side="left", fill="both", expand=True, padx=(0, 20)) 
        game_frame.pack_propagate(False)

        # --- 상단 정보 프레임 (pack 유지) ---
        top_frame = tk.Frame(game_frame, bg=self.COLOR_BG)
        top_frame.pack(pady=(0, 10), fill="x")

        self.info_label = tk.Label(top_frame, text="", font=("Malgun Gothic", 11), justify=tk.LEFT, bg=self.COLOR_BG, fg=self.COLOR_TEXT, height=2)
        self.info_label.pack(side="left")

        self.coins_label = tk.Label(top_frame, text=f"남은 코인: {self.coins}", font=("Malgun Gothic", 14, "bold"), bg=self.COLOR_BG, fg=self.COLOR_ACCENT)
        self.coins_label.pack(side="right")

        # --- 주사위 디스플레이 ---
        self.dice_display = tk.Label(game_frame, text="주사위: [ ? ] [ ? ] [ ? ]", font=("Malgun Gothic", 28, "bold"), bg=self.COLOR_BG, fg=self.COLOR_TEXT)
        self.dice_display.pack(pady=20)

        # --- 상태 메시지 ---
        self.status_label = tk.Label(game_frame, text="초기 코인을 설정하고 '새 라운드 시작'을 누르세요.", font=("Malgun Gothic", 12), bg=self.COLOR_BG, fg=self.COLOR_INFO)
        self.status_label.pack(pady=10)

        # --- 베팅 버튼 프레임 ---
        bet_frame = tk.Frame(game_frame, bg=self.COLOR_BG)
        bet_frame.pack(pady=15)
        
        btn_font = ("Malgun Gothic", 10, "bold")
        btn_style = {"font": btn_font, "bg": self.COLOR_BTN, "fg": self.COLOR_TEXT, "relief": tk.RAISED, "borderwidth": 3, "width": 18, "pady": 5}

        self.bet_button_over = tk.Button(bet_frame, text="▲ 10을 넘는다 (Over)", **btn_style, command=lambda: self.place_bet('over'), state=tk.DISABLED)
        self.bet_button_over.pack(side=tk.LEFT, padx=10)

        self.bet_button_under = tk.Button(bet_frame, text="▼ 10 이하다 (Under)", **btn_style, command=lambda: self.place_bet('under'), state=tk.DISABLED)
        self.bet_button_under.pack(side=tk.LEFT, padx=10)

        # --- 진행 버튼 ---
        self.next_roll_button = tk.Button(game_frame, text="다음 주사위 굴리기", font=btn_font, bg=self.COLOR_INFO, fg=self.COLOR_TEXT, relief=tk.RAISED, borderwidth=3, width=25, pady=4, command=self.next_roll, state=tk.DISABLED)
        self.next_roll_button.pack(pady=10)
        
        self.new_round_button = tk.Button(game_frame, text="새 라운드 시작", font=btn_font, relief=tk.RAISED, borderwidth=3, width=25, pady=4, command=self.start_new_round, state=tk.NORMAL)
        self.new_round_button.pack(pady=5)
        
        self.restart_button = tk.Button(game_frame, text="재시작", font=btn_font, bg=self.COLOR_ACCENT, fg=self.COLOR_BG, relief=tk.RAISED, borderwidth=3, width=25, pady=4, command=self.restart_game, state=tk.DISABLED)
        self.restart_button.pack(pady=5)
        
        
        # --- 하단 콘텐츠 프레임: grid 사용으로 밀림 방지 ---
        bottom_content_frame = tk.Frame(game_frame, bg=self.COLOR_BG)
        bottom_content_frame.pack(fill="x", pady=(15, 0))
        bottom_content_frame.grid_columnconfigure(0, weight=1) 
        
        # 1. 초기 코인 설정 프레임 (Row 0)
        initial_coins_frame = tk.Frame(bottom_content_frame, bg=self.COLOR_BG)
        initial_coins_frame.grid(row=0, column=0, pady=(20, 10)) 

        tk.Label(initial_coins_frame, text="초기 코인:", font=("Malgun Gothic", 10), bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(side=tk.LEFT, padx=5)

        self.minus_button = tk.Button(initial_coins_frame, text="-", font=("Malgun Gothic", 10, "bold"), bg=self.COLOR_BTN, fg=self.COLOR_TEXT, command=self.decrease_initial_coins, width=2)
        self.minus_button.pack(side=tk.LEFT)

        self.initial_coins_entry = tk.Entry(initial_coins_frame, width=4, font=("Malgun Gothic", 10, "bold"), justify='center', bg=self.COLOR_BTN, fg=self.COLOR_TEXT)
        self.initial_coins_entry.insert(0, str(self.initial_coins_value))
        self.initial_coins_entry.pack(side=tk.LEFT, padx=5)

        self.plus_button = tk.Button(initial_coins_frame, text="+", font=("Malgun Gothic", 10, "bold"), bg=self.COLOR_BTN, fg=self.COLOR_TEXT, command=self.increase_initial_coins, width=2)
        self.plus_button.pack(side=tk.LEFT)
        
        # 2. 결과 메시지 (Row 1)
        self.result_label = tk.Label(bottom_content_frame, text="", font=("Malgun Gothic", 12, "bold"), wraplength=750, justify=tk.CENTER, bg=self.COLOR_BG)
        self.result_label.grid(row=1, column=0, pady=(15, 10), sticky="ew") 

        # 3. 명언 레이블 (Row 2)
        self.quote_label = tk.Label(bottom_content_frame, text="", font=("Malgun Gothic", 10, "italic"),
                                     wraplength=750, justify=tk.CENTER, bg=self.COLOR_BG, 
                                     fg=self.COLOR_FAILURE)
        self.quote_label.grid(row=2, column=0, pady=(5, 5), sticky="ew") 
        
        # --- [우측] 기록 영역 프레임 ---
        self.history_frame = tk.Frame(main_frame, bg=self.COLOR_BG, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.history_frame.pack(side="right", fill="both", expand=True)
        self.history_frame.pack_propagate(False)

        tk.Label(self.history_frame, text="🏆 최고 이익률 Top 5 🏆", font=("Malgun Gothic", 14, "bold"), bg=self.COLOR_BG, fg=self.COLOR_ACCENT, pady=10).pack(fill="x")
        
        # 기록 표시 레이블들을 위한 컨테이너
        self.history_labels_container = tk.Frame(self.history_frame, bg=self.COLOR_BG)
        self.history_labels_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.update_history_display()

    def increase_initial_coins(self):
        try:
            current_value = int(self.initial_coins_entry.get())
            self.initial_coins_entry.delete(0, tk.END)
            self.initial_coins_entry.insert(0, str(current_value + 1))
        except ValueError:
            self.initial_coins_entry.delete(0, tk.END)
            self.initial_coins_entry.insert(0, "3")

    def decrease_initial_coins(self):
        try:
            current_value = int(self.initial_coins_entry.get())
            if current_value > 1:
                self.initial_coins_entry.delete(0, tk.END)
                self.initial_coins_entry.insert(0, str(current_value - 1))
        except ValueError:
            self.initial_coins_entry.delete(0, tk.END)
            self.initial_coins_entry.insert(0, "3")


    def start_new_round(self):
        if self.round_number >= self.max_rounds:
            self.end_game() 
            return

        if self.coins == 0 and self.round_number > 0:
            self.show_bankruptcy_screen()
            return

        # 초기 코인 설정 UI는 게임이 처음 시작될 때 단 한 번만 비활성화합니다.
        if self.round_number == 0:
            try:
                self.coins = int(self.initial_coins_entry.get())
                self.initial_coins_value = self.coins
                
                # 초기 코인 설정 UI 비활성화
                self.initial_coins_entry.config(state=tk.DISABLED, bg=self.COLOR_BTN, fg=self.COLOR_ACCENT)
                self.minus_button.config(state=tk.DISABLED, bg=self.COLOR_BG, fg=self.COLOR_BG)
                self.plus_button.config(state=tk.DISABLED, bg=self.COLOR_BG, fg=self.COLOR_BG)
            except (ValueError, TypeError):
                self.coins = 3
                self.initial_coins_value = 3

        self.round_number += 1
        self.dice_values = [0, 0, 0]
        self.current_stage = 0
        self.update_display()
        
        self.bet_button_over.config(state=tk.NORMAL)
        self.bet_button_under.config(state=tk.NORMAL)
        self.next_roll_button.config(state=tk.NORMAL)
        self.new_round_button.config(text="다음 라운드 시작", state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED) 
        self.result_label.config(text="")
        
        # 새 라운드 시작 시 명언 레이블 초기화
        self.quote_label.config(text="")


    def next_roll(self):
        # 주사위 굴리기
        if self.current_stage < 3:
            self.dice_values[self.current_stage] = random.randint(1, 6)
            self.current_stage += 1
            self.update_display()
        
        if self.current_stage >= 3:
            # 베팅 없이 모든 주사위를 굴린 경우
            total = sum(self.dice_values)
            self.status_label.config(text=f"베팅하지 않았습니다. 최종 합: {total}", fg=self.COLOR_INFO)
            self.end_round()
            return


    def place_bet(self, choice):
        min_bets = {0: 1, 1: 2, 2: 3}
        min_bet = min_bets[self.current_stage]
        
        # 베팅이 이루어진 단계 (0, 1, 2)를 저장
        betting_stage = self.current_stage

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
        self.update_display()
        
        # 베팅 단계를 resolve_bet까지 전달
        self.sequential_roll(self.current_stage, choice, bet_amount, betting_stage)

    def sequential_roll(self, dice_index, choice, bet_amount, betting_stage):
        if dice_index < 3:
            self.dice_values[dice_index] = random.randint(1, 6)
            self.update_display()
            self.root.after(1000, lambda: self.sequential_roll(dice_index + 1, choice, bet_amount, betting_stage))
        else:
            # 모든 주사위를 굴린 후, 베팅 정보를 가지고 결과 해결
            self.resolve_bet(choice, bet_amount, betting_stage)

    def resolve_bet(self, choice, bet_amount, betting_stage):
        # 기본 배율 설정 (베팅 단계 0: 4배, 1: 3배)
        payout = 0
        payout_description = ""
        
        if betting_stage == 0:
            payout = 4
            payout_description = "4배"
        elif betting_stage == 1:
            payout = 3
            payout_description = "3배"
        elif betting_stage == 2:
            # --- 3단계 (주사위 2개)의 확실성 기반 배율 로직 ---
            sum_first_two = self.dice_values[0] + self.dice_values[1]
            
            # 확실한 베팅 조건:
            # 1. 'Over 10'이 확실: 첫 두 주사위의 합이 10, 11, 12인 경우
            # 2. 'Under 10'이 확실: 첫 두 주사위의 합이 2, 3인 경우
            is_certain = (sum_first_two >= 10) or (sum_first_two <= 3)
            
            if is_certain:
                # 확실한 베팅: 1.3배
                payout = 1.3
                payout_description = "1.3배 (확실성 조건 충족)"
            else:
                # 불확실한 베팅: 2배 (원래 배율 유지)
                payout = 2.0 
                payout_description = "2배 (불확실성 조건)"
            # ---------------------------------------------------
        
        total = sum(self.dice_values)
        result = 'over' if total > 10 else 'under'
        
        if choice == result:
            # === 요청 사항 반영: 1.3배일 경우 소수점은 반올림(round) 처리 ===
            if payout == 1.3:
                winnings = round(bet_amount * payout) # 소수점 반올림 처리
            else:
                winnings = math.floor(bet_amount * payout) # 그 외 배율은 내림 처리 (기존 로직 유지)

            self.coins += winnings
            self.status_label.config(text="라운드 종료!", fg=self.COLOR_TEXT)
            self.result_label.config(text=f"✅ 성공! {winnings} 코인 (배율: {payout_description})을 얻었습니다.\n최종 합: {total}", fg=self.COLOR_SUCCESS)
            self.quote_label.config(text="") # 성공 시 명언 레이블 초기화
        else:
            full_message = "명언을 가져오는 데 실패했습니다."
            try:
                # 명언 API 호출
                with urllib.request.urlopen("https://korean-advice-open-api.vercel.app/api/advice") as response:
                    data = json.loads(response.read().decode())
                    quote = data.get('message') or data.get('advice', '다음에 더 잘할 수 있을 거예요.')
                    author = data.get('author', '')
                    
                    full_message = f'"{quote}"'
                    if author:
                        full_message += f"\n- {author}"
                    
            except Exception:
                pass
            
            self.status_label.config(text="라운드 종료!", fg=self.COLOR_TEXT)
            self.result_label.config(text=f"❌ 실패! {bet_amount} 코인을 잃었습니다.\n최종 합: {total}", fg=self.COLOR_FAILURE)
            self.quote_label.config(text=full_message)
        
        self.end_round()


    def end_round(self):
        self.update_display()
        self.bet_button_over.config(state=tk.DISABLED)
        self.bet_button_under.config(state=tk.DISABLED)
        self.next_roll_button.config(state=tk.DISABLED)
        
        if self.round_number < self.max_rounds:
            self.new_round_button.config(state=tk.NORMAL)
        else:
            self.end_game()
            return
            
        if self.coins == 0:
            self.show_bankruptcy_screen()
            
    def end_game(self):
        self.new_round_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.NORMAL)
        
        final_coins = self.coins
        initial_coins = self.initial_coins_value
        
        profit = final_coins - initial_coins
        
        if initial_coins > 0:
            profit_rate = (profit / initial_coins) * 100
        else:
            profit_rate = -math.inf 

        self.profit_history.append((profit_rate, initial_coins, final_coins))
        self.profit_history.sort(key=lambda x: x[0], reverse=True) 
        self.profit_history = self.profit_history[:5] 
        
        self.update_history_display()

        final_msg = f"🎉 **최종 게임 종료!** 🎉\n\n초기 코인: {initial_coins} | 최종 코인: {final_coins}\n이익률: {profit_rate:+.2f}%"
        self.status_label.config(text="게임을 마쳤습니다. 재시작 버튼을 누르세요.", fg=self.COLOR_TEXT)
        
        # 이전 라운드 결과를 덮어씁니다.
        if profit > 0:
            self.result_label.config(text=final_msg, fg=self.COLOR_SUCCESS)
        elif profit < 0:
            self.result_label.config(text=final_msg, fg=self.COLOR_FAILURE)
        else:
             self.result_label.config(text=final_msg, fg=self.COLOR_ACCENT)
        
        self.quote_label.config(text="") # 게임 종료 시 명언 레이블 초기화


    def show_bankruptcy_screen(self):
        self.end_game() 
        
        # 모든 위젯 제거
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 파산 메시지 표시
        bankruptcy_label = tk.Label(self.root, text="파산", font=("Malgun Gothic", 100, "bold"), bg=self.COLOR_BG, fg=self.COLOR_FAILURE)
        bankruptcy_label.pack(pady=(100, 0), expand=True)

        btn_font = ("Malgun Gothic", 12, "bold")
        new_game_button = tk.Button(self.root, text="새 게임", font=btn_font, bg=self.COLOR_BTN, fg=self.COLOR_TEXT, relief=tk.RAISED, borderwidth=3, width=20, pady=8, command=self.restart_game)
        new_game_button.pack(pady=(20, 100), expand=True)
        
    def restart_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.coins = 3
        self.initial_coins_value = 3
        self.dice_values = [0, 0, 0]
        self.current_stage = 0
        self.round_number = 0

        self.setup_ui()
        
    def update_history_display(self):
        for widget in self.history_labels_container.winfo_children():
            widget.destroy()

        if not self.profit_history:
            tk.Label(self.history_labels_container, text="아직 기록된 게임이 없습니다.", bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(pady=10)
            return

        for idx, (rate, initial, final) in enumerate(self.profit_history):
            if rate == -math.inf:
                rate_str = "파산"
            else:
                rate_str = f"{rate:+.2f}%"
            
            text = f"#{idx+1}. 이익률: {rate_str} (시작: {initial}, 최종: {final})"
            
            if rate > 0:
                fg_color = self.COLOR_SUCCESS
            elif rate < 0:
                fg_color = self.COLOR_FAILURE
            else:
                fg_color = self.COLOR_TEXT
                
            tk.Label(self.history_labels_container, text=text, anchor='w', justify=tk.LEFT,
                     font=("Malgun Gothic", 10, "bold"), bg=self.COLOR_BG, fg=fg_color).pack(fill="x", pady=2, padx=5)


    def update_display(self):
        stages_info = {
            0: "1단계: 주사위 0개 (최소 베팅: 1, 성공 시 4배)",
            1: "2단계: 주사위 1개 (최소 베팅: 2, 성공 시 3배)",
            # 3단계: 확실성 여부에 따라 1.3배 또는 2배가 적용됩니다.
            2: "3단계: 주사위 2개 (최소 베팅: 3, 성공 시 1.3배(확실, 반올림) / 2배(불확실, 내림))" 
        }
        stage_text = stages_info.get(self.current_stage, '베팅 결과 확인 중')
        
        info_text = f"라운드: {self.round_number}/{self.max_rounds}\n현재: {stage_text}"
        
        if self.round_number == 0:
            info_text = "\n" 
            
        self.info_label.config(text=info_text)
        
        self.coins_label.config(text=f"남은 코인: {self.coins}")

        dice_str = " ".join([f"[{val if val != 0 else '?'}]" for val in self.dice_values])
        self.dice_display.config(text=f"주사위: {dice_str}")

        if self.current_stage == 0:
            self.status_label.config(text="새 라운드 시작 또는 초기 코인을 설정하세요.", fg=self.COLOR_INFO)
            self.next_roll_button.config(text="다음 주사위 굴리기")
        elif self.current_stage == 1:
            self.status_label.config(text=f"첫 주사위는 {self.dice_values[0]}입니다. 베팅하거나 굴리세요.", fg=self.COLOR_INFO)
            self.next_roll_button.config(text="다음 주사위 굴리기")
        elif self.current_stage == 2:
            # 첫 두 주사위의 합을 계산하여 확실성 메시지를 추가적으로 표시합니다.
            sum_two = self.dice_values[0] + self.dice_values[1]
            if sum_two >= 10:
                 certainty_msg = "Over 10이 확실합니다. (배율: 1.3배, 반올림)"
            elif sum_two <= 3:
                 certainty_msg = "Under 10이 확실합니다. (배율: 1.3배, 반올림)"
            else:
                 certainty_msg = "결과가 불확실합니다. (배율: 2배, 내림)"
            
            self.status_label.config(text=f"두 주사위는 {self.dice_values[0]}, {self.dice_values[1]}입니다. {certainty_msg}", fg=self.COLOR_INFO)
            self.next_roll_button.config(text="결과 확인 (베팅 안함)")
        elif self.current_stage == 3 and not any(v == 0 for v in self.dice_values):
            pass


if __name__ == "__main__":
    root = tk.Tk()
    game = DiceBettingGame(root)
    root.mainloop()
