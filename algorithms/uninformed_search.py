"""
Module chứa các thuật toán tìm kiếm không có thông tin (Uninformed Search)
"""
from models.puzzle_state import PuzzleState
from collections import deque

def bfs_solve(initial_state, goal_state):
    """Breadth-First Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    queue = deque([initial])
    visited = {initial}
    
    while queue:
        current = queue.popleft()
        
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            
            if next_state.state == goal.state:
                return next_state.get_states()
                
            if next_state not in visited:
                visited.add(next_state)
                queue.append(next_state)
                
    return None

def dfs_solve(initial_state, goal_state):
    """Depth-First Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    stack = [initial]
    visited = {initial}
    
    while stack:
        current = stack.pop()
        
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            
            if next_state.state == goal.state:
                return next_state.get_states()
                
            if next_state not in visited:
                visited.add(next_state)
                stack.append(next_state)
                
    return None

def ucs_solve(initial_state, goal_state):
    """Uniform Cost Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    queue = [(0, initial)]
    visited = {initial}
    
    while queue:
        cost, current = queue.pop(0)
        
        if current.state == goal.state:
            return current.get_states()
            
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state.cost, next_state))
                queue.sort(key=lambda x: x[0])
                
    return None

def iddfs_solve(initial_state, goal_state):
    """Iterative Deepening Depth-First Search"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    def dls(node, depth):
        if depth == 0:
            return None if node.state != goal.state else [node.state]
            
        if node.state == goal.state:
            return [node.state]
            
        for move in node.get_valid_moves():
            next_state = node.make_move(move)
            result = dls(next_state, depth - 1)
            if result:
                return [node.state] + result
                
        return None
        
    depth = 0
    while True:
        result = dls(initial, depth)
        if result:
            return result
        depth += 1
