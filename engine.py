import numpy as np

ROWS = 6
COLS = 7

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

class Connect4Game:
    def __init__(self):
        # 0 is empty, 1 is Player 1 (Red), 2 is Player 2 (Yellow)
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.current_player = PLAYER1
        self.move_history = []

    def reset(self):
        self.board.fill(EMPTY)
        self.current_player = PLAYER1
        self.move_history.clear()

    def is_valid_location(self, col):
        # Check if the top row of a column is empty.
        return self.board[0][col] == EMPTY

    def get_valid_locations(self):
        # Return a list of playable columns.
        valid_locations = []
        for col in range(COLS):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations

    def get_next_open_row(self, col):
        # Find the lowest empty row in a given column.
        for r in range(ROWS-1, -1, -1):
            if self.board[r][col] == EMPTY:
                return r
        return -1

    def make_move(self, col):
        # Drops a piece in the column for the current player.
        if not self.is_valid_location(col):
            return False

        row = self.get_next_open_row(col)
        self.board[row][col] = self.current_player
        self.move_history.append(col)
        
        # Swap player
        self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1
        return True

    def undo_move(self):
        # Undoes the last move (useful for minimax traversal).
        if not self.move_history:
            return False
        
        col = self.move_history.pop()
        
        # Find the top-most piece in the column and remove it
        for r in range(ROWS):
            if self.board[r][col] != EMPTY:
                self.board[r][col] = EMPTY
                break
                
        # Swap player back
        self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1
        return True

    def winning_move(self, piece):
        # Checks if the specified piece has connected 4.
        # Check horizontal
        for c in range(COLS-3):
            for r in range(ROWS):
                if self.board[r][c] == piece and self.board[r][c+1] == piece and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True

        # Check vertical
        for c in range(COLS):
            for r in range(ROWS-3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True

        # Check positive sloping diaganols
        for c in range(COLS-3):
            for r in range(ROWS-3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True

        # Check negative sloping diaganols
        for c in range(COLS-3):
            for r in range(3, ROWS):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True

        return False

    def is_terminal_node(self):
        # Check if game is over manually.
        return self.winning_move(PLAYER1) or self.winning_move(PLAYER2) or len(self.get_valid_locations()) == 0

    def get_state_hash(self):
        # Returns a stringified/hashed version of the board for Transposition Tables.
        # tobytes() is extremely fast for hashing NumPy states
        return self.board.tobytes()
