# Connect Four AI

A Python-based Connect Four game featuring a custom Minimax AI with Alpha-Beta pruning, a graphical user interface, and performance benchmarking tools.

## How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/CalebHarsch/Connect-Four.git
   cd Connect-Four
   ```

2. **Install requirements**
   The project requires `numpy`. Install it via pip:
   ```bash
   pip install numpy
   ```

3. **Play the game**
   Launch the graphical interface to play against the AI or watch AI vs AI:
   ```bash
   python app.py
   ```

4. **Run AI benchmarks**
   To see performance metrics, win rates, and the impact of Alpha-Beta pruning:
   ```bash
   python evaluate.py
   ```
   This may take a bit depending on how many games you have it set to simulate. I currently have it set to 5 games.

Note: If this doesn't work we have a releases tab with the application. This should work.
