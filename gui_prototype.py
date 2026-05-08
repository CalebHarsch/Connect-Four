import tkinter as tk
import math

class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four AI - Chess.com Style Eval Bar")
        self.root.geometry("800x600")
        self.root.configure(bg="#21201D")
        
        # Main layout
        self.main_frame = tk.Frame(self.root, bg="#21201D")
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Eval Bar Frame (Left side)
        self.eval_frame = tk.Frame(self.main_frame, bg="#21201D")
        self.eval_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Eval Bar Dimensions
        self.BAR_HEIGHT = 450
        self.BAR_WIDTH = 35
        # The canvas that holds the eval bar
        self.eval_canvas = tk.Canvas(
            self.eval_frame, width=self.BAR_WIDTH, height=self.BAR_HEIGHT, 
            bg="#333333", highlightthickness=0
        )
        self.eval_canvas.pack(pady=10)
        
        # Board Canvas
        self.board_canvas = tk.Canvas(
            self.main_frame, width=490, height=420, 
            bg="#262421", highlightthickness=0
        )
        self.board_canvas.pack(side=tk.LEFT, expand=False)
        self.draw_board()
        
        self.controls_frame = tk.Frame(self.main_frame, bg="#21201D")
        self.controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(30, 0))
        
        tk.Label(
            self.controls_frame, text="AI Heuristic Score", 
            bg="#21201D", fg="white", font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Slider to show changing heuristic score
        self.eval_slider = tk.Scale(
            self.controls_frame, from_=20.0, to=-20.0, resolution=0.1, 
            orient=tk.VERTICAL, command=self.update_eval_bar, length=300, 
            bg="#21201D", fg="white", highlightthickness=0, troughcolor="#333333"
        )
        self.eval_slider.set(0.0)
        self.eval_slider.pack(pady=10)
        
        # Label to show the exact numeric score
        self.eval_label = tk.Label(
            self.controls_frame, text="0.0", 
            bg="#21201D", fg="white", font=("Arial", 16, "bold"), width=6
        )
        self.eval_label.pack(pady=10)
        
        self.current_eval = 0.0
        self.update_eval_bar(0.0)

    def draw_board(self):
        # Draws a mockup of a Modern Connect 4 Board.
        # Outer board background
        self.board_canvas.create_rectangle(10, 10, 480, 410, fill="#235FD4", outline="#17449E", width=4, tags="board_bg")
        
        # Draw Connect 4 empty holes grids
        ROWS, COLS = 6, 7
        RADIUS = 25
        padding_x = 25
        padding_y = 25
        for r in range(ROWS):
            for c in range(COLS):
                x0 = padding_x + c * 63
                y0 = padding_y + r * 63
                x1 = x0 + RADIUS * 2
                y1 = y0 + RADIUS * 2
                self.board_canvas.create_oval(x0, y0, x1, y1, fill="#21201D", outline="#1a1917", width=3)
                
    def get_win_probability(self, score):
        # score / 4.0 manages the scaling curve (adjust 4.0 higher for a slower fill)
        return 0.5 + 0.5 * (2 / math.pi) * math.atan(score / 4.0)
                
    def update_eval_bar(self, val):
        self.current_eval = float(val)
        self.eval_canvas.delete("bar")
        self.eval_canvas.delete("text")
        
        h = self.BAR_HEIGHT
        w = self.BAR_WIDTH
        
        # Get purely mathematical split
        p1_prop = self.get_win_probability(self.current_eval)
        
        # Let Player 1 be Red (bottom) and Player 2 be Yellow (top)
        red_h = h * p1_prop
        yellow_h = h - red_h
        
        # Draw Yellow rectangle (Player 2)
        # Coordinates: top-left x, top-left y, bottom-right x, bottom-right y
        self.eval_canvas.create_rectangle(0, 0, w, yellow_h, fill="#F2CD44", outline="", tags="bar")
        
        # Draw Red rectangle (Player 1)
        self.eval_canvas.create_rectangle(0, yellow_h, w, h, fill="#D13B35", outline="", tags="bar")
        
        # If score is very high positive, show "M" logic (Mate in X) to stylize it.
        format_score = f"{self.current_eval:+.1f}" if abs(self.current_eval) < 18 else ("+M" if self.current_eval > 0 else "-M")
        
        if self.current_eval >= 0:
            # White text on red background near bottom
            self.eval_canvas.create_text(w/2, h - 25, text=format_score, fill="white", font=("Arial", 9, "bold"), tags="text")
        else:
            # Dark text on yellow background near top
            self.eval_canvas.create_text(w/2, 25, text=format_score, fill="#111111", font=("Arial", 9, "bold"), tags="text")
            
        # Update the main label under the slider
        self.eval_label.config(text=format_score)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    root.mainloop()
