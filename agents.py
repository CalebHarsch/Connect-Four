import random
import time
import math
from engine import ROWS, COLS, EMPTY, PLAYER1, PLAYER2

class Agent:
    def __init__(self, player_id):
        self.player_id = player_id
        self.opponent_id = PLAYER1 if player_id == PLAYER2 else PLAYER2
        
    def get_action(self, game_state):
        raise NotImplementedError

class RandomAgent(Agent):
    def get_action(self, game_state):
        valid = game_state.get_valid_locations()
        return random.choice(valid) if valid else None

class GreedyAgent(Agent):
    """Looks 1 step ahead and picks the move with the highest immediate heuristic score."""
    def get_action(self, game_state):
        valid_locations = game_state.get_valid_locations()
        best_score = -float('inf')
        best_col = random.choice(valid_locations) if valid_locations else None
        
        for col in valid_locations:
            game_state.current_player = self.player_id
            game_state.make_move(col)
            score = evaluate_board(game_state.board, self.player_id)
            game_state.undo_move()
            
            if score > best_score:
                best_score = score
                best_col = col
                
        return best_col

def evaluate_window(window, piece):
    """Assigns scores to a sequence of 4 blocks based on how close piece is to winning."""
    score = 0
    opp_piece = PLAYER1 if piece == PLAYER2 else PLAYER2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    # Heavily penalize if opponent is about to win
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    """Calculates the positive feature score for a specific piece."""
    score = 0
    
    # Priority: Center column is extremely important in Connect 4
    center_array = list(board[:, COLS//2])
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontal
    for r in range(ROWS):
        row_array = list(board[r, :])
        for c in range(COLS-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Vertical
    for c in range(COLS):
        col_array = list(board[:, c])
        for r in range(ROWS-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Positive sloped diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative sloped diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def evaluate_board(board, piece):
    """Evaluates the zero-sum relative score of the board."""
    opp_piece = PLAYER1 if piece == PLAYER2 else PLAYER2
    return score_position(board, piece) - score_position(board, opp_piece)

class MinimaxAgent(Agent):
    def __init__(self, player_id, max_depth=5):
        super().__init__(player_id)
        self.max_depth = max_depth
        self.nodes_expanded = 0
        self.ttable = {}
        self.ttable_hits = 0

    def clear_ttable(self):
        self.ttable.clear()

    def get_action(self, game_state):
        self.nodes_expanded = 0
        self.ttable_hits = 0
        
        best_col = None
        
        # Iterative Deepening
        for depth in range(1, self.max_depth + 1):
            col, score = self.minimax(game_state, depth, -math.inf, math.inf, True)
            if col is not None:
                best_col = col
                
            # If we find a forced win, we can optionally break early to save time
            if score > 10000000:
                break
                
        return best_col

    def minimax(self, game, depth, alpha, beta, maximizingPlayer):
        valid_locations = game.get_valid_locations()
        is_terminal = game.is_terminal_node()
        
        # Check Transposition Table
        # We hash the board state + depth left + who is maximizing to ensure accuracy
        state_hash = game.get_state_hash()
        tt_key = (state_hash, depth, maximizingPlayer)
        if tt_key in self.ttable:
            self.ttable_hits += 1
            return self.ttable[tt_key]

        if depth == 0 or is_terminal:
            self.nodes_expanded += 1
            if is_terminal:
                # We reward heavily for winning faster (higher depth implies early termination)
                if game.winning_move(self.player_id):
                    return (None, 100000000000000 + depth * 1000)
                elif game.winning_move(self.opponent_id):
                    return (None, -10000000000000 - depth * 1000)
                else: # Draw
                    return (None, 0)
            else: # Depth 0 threshold reached
                return (None, evaluate_board(game.board, self.player_id))
        
        # Move Ordering: evaluate center columns first to maximize Alpha-Beta cutoffs!
        valid_locations.sort(key=lambda col: abs(COLS//2 - col))
        
        if maximizingPlayer:
            value = -math.inf
            best_col = random.choice(valid_locations) if valid_locations else None
            for col in valid_locations:
                # Assuming the internal game engine sets current_player properly if we swap
                # To be absolutely sure, we enforce standard swap
                game.current_player = self.player_id
                game.make_move(col)
                new_score = self.minimax(game, depth-1, alpha, beta, False)[1]
                game.undo_move()
                
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
                    
            self.ttable[tt_key] = (best_col, value)
            return best_col, value
            
        else: # Minimizing player
            value = math.inf
            best_col = random.choice(valid_locations) if valid_locations else None
            for col in valid_locations:
                game.current_player = self.opponent_id
                game.make_move(col)
                new_score = self.minimax(game, depth-1, alpha, beta, True)[1]
                game.undo_move()
                
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
                    
            self.ttable[tt_key] = (best_col, value)
            return best_col, value
