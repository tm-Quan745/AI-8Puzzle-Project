"""
Module for Forward Checking implementation in 8-puzzle solver
"""
from models.puzzle_state import PuzzleState

class ForwardCheckingController:
    def __init__(self, initial_state=None, goal_state=None):
        self.initial_state = initial_state or [
            [1, 2, 3],
            [4, 0, 6], 
            [7, 5, 8]
        ]
        self.goal_state = goal_state or [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        self.solution_steps = []
        
    def is_valid_move(self, state, x, y):
        """Check if a move is valid within the puzzle boundaries"""
        return 0 <= x < 3 and 0 <= y < 3

    def get_possible_moves(self, state):
        """Get all possible moves from current state"""
        moves = []
        blank_x, blank_y = None, None
        
        # Find blank position
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    blank_x, blank_y = i, j
                    break
            if blank_x is not None:
                break
                
        # Check all possible directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
        for dx, dy in directions:
            new_x, new_y = blank_x + dx, blank_y + dy
            if self.is_valid_move(state, new_x, new_y):
                moves.append((new_x, new_y))
        
        return moves, (blank_x, blank_y)

    def make_move(self, state, move_pos, blank_pos):
        """Make a move in the puzzle"""
        new_state = [row[:] for row in state]
        move_x, move_y = move_pos
        blank_x, blank_y = blank_pos
        
        # Swap blank with target position
        new_state[blank_x][blank_y], new_state[move_x][move_y] = \
            new_state[move_x][move_y], new_state[blank_x][blank_y]
            
        return new_state

    def forward_check(self, state):
        """Perform forward checking for the current state"""
        puzzle = PuzzleState(state)
        if puzzle.state == self.goal_state:
            return True
            
        possible_moves, blank_pos = self.get_possible_moves(state)
        
        for move in possible_moves:
            new_state = self.make_move(state, move, blank_pos)
            
            # Check if this move maintains valid state
            if self._is_valid_state(new_state):
                return True
        
        return False

    def _is_valid_state(self, state):
        """Check if the current state is valid"""
        # Check all numbers are present
        numbers = set()
        for row in state:
            for num in row:
                numbers.add(num)
        
        return len(numbers) == 9 and all(i in numbers for i in range(9))

    def solve(self, max_depth=31):
        """Solve the puzzle using forward checking"""
        self.solution_steps = []
        initial = PuzzleState(self.initial_state)
        
        def dfs(current_state, depth):
            if depth > max_depth:
                return False
                
            self.solution_steps.append(current_state)
            
            if current_state == self.goal_state:
                return True
                
            possible_moves, blank_pos = self.get_possible_moves(current_state)
            
            for move in possible_moves:
                new_state = self.make_move(current_state, move, blank_pos)
                
                if self.forward_check(new_state):
                    if dfs(new_state, depth + 1):
                        return True
            
            return False

        dfs(self.initial_state, 0)
        return self.solution_steps
