"""
Module chứa các thuật toán tìm kiếm có thông tin (Informed Search)
"""
from models.puzzle_state import PuzzleState

def greedy_best_first_search(initial_state, goal_state):
    """Greedy Best-First Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    def heuristic(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal.state[i][j]:
                    count += 1
        return count
        
    queue = [(heuristic(initial.state), initial)]
    visited = {initial}
    
    while queue:
        _, current = queue.pop(0)
        
        if current.state == goal.state:
            return current.get_states()
            
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            
            if next_state not in visited:
                visited.add(next_state)
                queue.append((heuristic(next_state.state), next_state))
                queue.sort(key=lambda x: x[0])
                
    return None

def a_star_search(initial_state, goal_state):
    """A* Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    def heuristic(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal.state[i][j]:
                    count += 1
        return count
        
    queue = [(heuristic(initial.state), 0, initial)]
    visited = {initial}
    
    while queue:
        _, cost, current = queue.pop(0)
        
        if current.state == goal.state:
            return current.get_states()
            
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            
            if next_state not in visited:
                visited.add(next_state)
                new_cost = cost + 1
                queue.append((new_cost + heuristic(next_state.state), new_cost, next_state))
                queue.sort(key=lambda x: x[0])
                
    return None

def ida_star_search(initial_state, goal_state):
    """Iterative Deepening A* Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    def heuristic(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal.state[i][j]:
                    count += 1
        return count
        
    def search(node, g, bound):
        f = g + heuristic(node.state)
        if f > bound:
            return f
        if node.state == goal.state:
            return node.get_states()
            
        min_f = float('inf')
        for move in node.get_valid_moves():
            next_state = node.make_move(move)
            result = search(next_state, g + 1, bound)
            if isinstance(result, list):
                return [node.state] + result
            min_f = min(min_f, result)
            
        return min_f
        
    bound = heuristic(initial.state)
    while True:
        result = search(initial, 0, bound)
        if isinstance(result, list):
            return result
        bound = result
