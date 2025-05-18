class PuzzleState:
    def __init__(self, state, parent=None, move=None, cost=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.cost = cost
        self.depth = parent.depth + 1 if parent else 0

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(str(self.state))

    def get_blank_position(self):
        for i in range(3):
            for j in range(3):
                if self.state[i][j] == 0:
                    return (i, j)
        return None

    def get_valid_moves(self):
        moves = []
        i, j = self.get_blank_position()
        
        # Up
        if i > 0:
            moves.append(('up', i-1, j))
        # Down
        if i < 2:
            moves.append(('down', i+1, j))
        # Left
        if j > 0:
            moves.append(('left', i, j-1))
        # Right
        if j < 2:
            moves.append(('right', i, j+1))
            
        return moves

    def make_move(self, move):
        direction, new_i, new_j = move
        i, j = self.get_blank_position()
        
        # Create new state
        new_state = [row[:] for row in self.state]
        new_state[i][j] = new_state[new_i][new_j]
        new_state[new_i][new_j] = 0
        
        return PuzzleState(new_state, self, direction, self.cost + 1)

    def get_path(self):
        path = []
        current = self
        while current:
            if current.move:
                path.append(current.move)
            current = current.parent
        return path[::-1]

    def get_states(self):
        states = []
        current = self
        while current:
            states.append(current.state)
            current = current.parent
        return states[::-1] 