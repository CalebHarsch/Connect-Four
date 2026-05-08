import tkinter as tk
from tkinter import messagebox
import math
import time
import threading
from engine import Connect4Game, ROWS, COLS, EMPTY, PLAYER1, PLAYER2
from agents import MinimaxAgent, RandomAgent, evaluate_board

class ConnectFourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four AI - Capstone Project")
        self.root.geometry("850x650")
        self.root.configure(bg="#21201D") 
        
        self.game = Connect4Game()
        
        # Agents
        self.ai_player1 = None
        self.ai_player2 = MinimaxAgent(PLAYER2, max_depth=5)
        
        self.game_mode = "Human vs AI" # Can be 'Human vs AI', 'AI vs AI'
        
        self.is_ai_thinking = False
        self.game_over = False

        self.setup_ui()
        self.update_ui()
        self.show_title_screen()

    def setup_ui(self):
        # 1. Title Screen Frame
        self.title_frame = tk.Frame(self.root, bg="#21201D")
        
        title_label = tk.Label(self.title_frame, text="Connect Four AI", font=("Arial", 36, "bold"), bg="#21201D", fg="white")
        title_label.pack(pady=(150, 50))
        
        hvai_btn = tk.Button(self.title_frame, text="Play Human vs AI", font=("Arial", 16, "bold"), bg="#D13B35", fg="white", width=20, pady=10, command=lambda: self.start_game("Human vs AI"))
        hvai_btn.pack(pady=10)
        
        aivai_btn = tk.Button(self.title_frame, text="Play AI vs AI", font=("Arial", 16, "bold"), bg="#F2CD44", fg="#111111", width=20, pady=10, command=lambda: self.start_game("AI vs AI"))
        aivai_btn.pack(pady=10)

        # 2. Game Screen Frame
        self.game_frame = tk.Frame(self.root, bg="#21201D")

        # Top panel for controls
        self.top_frame = tk.Frame(self.game_frame, bg="#21201D")
        self.top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(self.top_frame, text="Main Menu", command=self.show_title_screen, bg="#444", fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Button(self.top_frame, text="Reset Game", command=self.reset_game, bg="#444", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT)
        self.status_label = tk.Label(self.top_frame, text="Your Turn (Red)", bg="#21201D", fg="white", font=("Arial", 14, "bold"))
        self.status_label.pack(side=tk.RIGHT, padx=40)

        # Main layout
        self.main_frame = tk.Frame(self.game_frame, bg="#21201D")
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Eval Bar Canvas (Left)
        self.eval_frame = tk.Frame(self.main_frame, bg="#21201D")
        self.eval_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        self.BAR_HEIGHT = 450
        self.BAR_WIDTH = 35
        self.eval_canvas = tk.Canvas(self.eval_frame, width=self.BAR_WIDTH, height=self.BAR_HEIGHT, bg="#333333", highlightthickness=0)
        self.eval_canvas.pack(pady=10)

        # Number score below eval bar
        self.score_label = tk.Label(self.eval_frame, text="0.0", bg="#21201D", fg="white", font=("Arial", 12, "bold"), width=6)
        self.score_label.pack(pady=5)
        
        # Board Canvas (Center)
        self.board_canvas = tk.Canvas(self.main_frame, width=490, height=420, bg="#262421", highlightthickness=0)
        self.board_canvas.pack(side=tk.LEFT, expand=False)
        self.board_canvas.bind("<Button-1>", self.on_board_click)
        
        # Info Panel
        self.info_frame = tk.Frame(self.main_frame, bg="#21201D")
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
        
        self.nodes_label = tk.Label(self.info_frame, text="Nodes Expanded:\n0", bg="#21201D", fg="white", font=("Arial", 12))
        self.nodes_label.pack(pady=10)
        
        self.tt_label = tk.Label(self.info_frame, text="Transposition Hits:\n0", bg="#21201D", fg="white", font=("Arial", 12))
        self.tt_label.pack(pady=10)
        
        self.time_label = tk.Label(self.info_frame, text="Decision Time:\n0.0s", bg="#21201D", fg="white", font=("Arial", 12))
        self.time_label.pack(pady=10)

    def show_title_screen(self):
        self.game_frame.pack_forget()
        self.title_frame.pack(expand=True, fill=tk.BOTH)
        
    def start_game(self, mode):
        self.game_mode = mode
        if self.game_mode == "AI vs AI":
            self.ai_player1 = MinimaxAgent(PLAYER1, max_depth=4) # Depth 4 for fast P1
        else:
            self.ai_player1 = None
            
        self.title_frame.pack_forget()
        self.game_frame.pack(expand=True, fill=tk.BOTH)
        self.reset_game()

    def reset_game(self):
        self.game.reset()
        if self.ai_player2:
            self.ai_player2.clear_ttable()
        if self.ai_player1:
            self.ai_player1.clear_ttable()
            
        self.game_over = False
        self.is_ai_thinking = False
        self.update_ui()
        self.status_label.config(text="Your Turn (Red)" if not self.ai_player1 else "AI 1 (Red) Thinking...")
        
        if self.game_mode == "AI vs AI":
            self.trigger_ai_move()

    def draw_board(self):
        self.board_canvas.delete("all")
        # Outer board
        self.board_canvas.create_rectangle(10, 10, 480, 410, fill="#235FD4", outline="#17449E", width=4)
        
        RADIUS = 25
        padding_x = 25
        padding_y = 25
        
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.game.board[r][c]
                color = "#21201D" # Empty
                if piece == PLAYER1:
                    color = "#D13B35" # Red
                elif piece == PLAYER2:
                    color = "#F2CD44" # Yellow
                
                # Math to draw pieces correctly (Row 0 is top visually, but logically it's bottom? No, engine logic: row 0 is top visually)
                # Engine logic: get_next_open_row goes from ROWS-1 down to 0. So row 5 is bottom, row 0 is top. This matches visuals perfectly!
                x0 = padding_x + c * 63
                y0 = padding_y + r * 63
                x1 = x0 + RADIUS * 2
                y1 = y0 + RADIUS * 2
                self.board_canvas.create_oval(x0, y0, x1, y1, fill=color, outline="#1a1917", width=3)

    def get_win_probability(self, score):
        return 0.5 + 0.5 * (2 / math.pi) * math.atan(score / 8.0)
                
    def update_eval_bar(self):
        # Always evaluate from player 1's perspective for the bar.
        current_eval = evaluate_board(self.game.board, PLAYER1)
        
        self.eval_canvas.delete("bar")
        self.eval_canvas.delete("text")
        
        h = self.BAR_HEIGHT
        w = self.BAR_WIDTH
        p1_prop = self.get_win_probability(current_eval)
        
        red_h = h * p1_prop
        yellow_h = h - red_h
        
        self.eval_canvas.create_rectangle(0, 0, w, yellow_h, fill="#F2CD44", outline="", tags="bar")
        self.eval_canvas.create_rectangle(0, yellow_h, w, h, fill="#D13B35", outline="", tags="bar")
        
        format_score = f"{current_eval:+.1f}" if abs(current_eval) < 1000 else ("+M" if current_eval > 0 else "-M")
        
        if current_eval >= 0:
            self.eval_canvas.create_text(w/2, h - 25, text=format_score, fill="white", font=("Arial", 9, "bold"), tags="text")
        else:
            self.eval_canvas.create_text(w/2, 25, text=format_score, fill="#111111", font=("Arial", 9, "bold"), tags="text")
            
        self.score_label.config(text=format_score)

    def update_ui(self):
        self.draw_board()
        self.update_eval_bar()

    def process_move(self, col):
        if self.game.make_move(col):
            self.update_ui()
            
            if self.game.winning_move(PLAYER1):
                self.status_label.config(text="Player 1 (Red) Wins!")
                self.game_over = True
            elif self.game.winning_move(PLAYER2):
                self.status_label.config(text="Player 2 (Yellow) Wins!")
                self.game_over = True
            elif len(self.game.get_valid_locations()) == 0:
                self.status_label.config(text="Draw!")
                self.game_over = True
            else:
                if self.game.current_player == PLAYER2:
                    self.status_label.config(text="AI Thinking...")
                    self.trigger_ai_move()
                elif self.game.current_player == PLAYER1 and self.game_mode == "AI vs AI":
                    self.status_label.config(text="AI 1 Thinking...")
                    self.trigger_ai_move()
                else:
                    self.status_label.config(text="Your Turn (Red)")

    def on_board_click(self, event):
        if self.game_over or self.is_ai_thinking or self.game_mode == "AI vs AI":
            return
            
        # Determine column based on click X coordinate
        col = (event.x - 25) // 63
        if 0 <= col < COLS and self.game.is_valid_location(col):
            self.process_move(col)

    def trigger_ai_move(self):
        if self.game_over:
            return
            
        self.is_ai_thinking = True
        # Run AI calculation in separate thread so UI doesn't freeze
        threading.Thread(target=self._ai_worker, daemon=True).start()
        
    def _ai_worker(self):
        start_time = time.time()
        agent = self.ai_player2 if self.game.current_player == PLAYER2 else self.ai_player1
        col = agent.get_action(self.game)
        elapsed = time.time() - start_time
        
        def finish():
            if type(agent) is MinimaxAgent:
                self.nodes_label.config(text=f"Nodes Expanded:\n{agent.nodes_expanded}")
                self.tt_label.config(text=f"Transposition Hits:\n{agent.ttable_hits}")
                self.time_label.config(text=f"Decision Time:\n{elapsed:.2f}s")
                
            self.is_ai_thinking = False
            self.process_move(col)
            
        self.root.after(100, finish)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourApp(root)
    root.mainloop()
