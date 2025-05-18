"""
Module chứa các thuật toán tìm kiếm cục bộ (Local Search)
"""
import random
import math
from models.puzzle_state import PuzzleState

def hill_climbing_simple(initial_state, goal_state):
    """Simple Hill Climbing"""
    current = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if current.state == goal.state:
        return [current.state]
        
    def heuristic(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal.state[i][j]:
                    count += 1
        return count
        
    while True:
        best_neighbor = None
        best_score = heuristic(current.state)
        
        for move in current.get_valid_moves():
            neighbor = current.make_move(move)
            score = heuristic(neighbor.state)
            
            if score < best_score:
                best_score = score
                best_neighbor = neighbor
                
        if best_neighbor is None:
            return None
            
        current = best_neighbor
        if current.state == goal.state:
            return current.get_states()

def hill_climbing_steepest(initial_state, goal_state):
    """Steepest Ascent Hill Climbing"""
    current = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if current.state == goal.state:
        return [current.state]
        
    def heuristic(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal.state[i][j]:
                    count += 1
        return count
        
    while True:
        neighbors = []
        for move in current.get_valid_moves():
            neighbor = current.make_move(move)
            neighbors.append((heuristic(neighbor.state), neighbor))
            
        if not neighbors:
            return None
            
        best_score, best_neighbor = min(neighbors, key=lambda x: x[0])
        
        if best_score >= heuristic(current.state):
            return None
            
        current = best_neighbor
        if current.state == goal.state:
            return current.get_states()

def stochastic_hill_climbing(initial_state, goal_state):
    """Stochastic Hill Climbing"""
    current = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if current.state == goal.state:
        return [current.state]
        
    def heuristic(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal.state[i][j]:
                    count += 1
        return count
        
    while True:
        neighbors = []
        for move in current.get_valid_moves():
            neighbor = current.make_move(move)
            score = heuristic(neighbor.state)
            if score < heuristic(current.state):
                neighbors.append(neighbor)
                
        if not neighbors:
            return None
            
        current = random.choice(neighbors)
        if current.state == goal.state:
            return current.get_states()

def simulated_annealing(initial_state, goal_state, max_steps=10000):
    """Simulated Annealing"""
    current = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)

    if current.state == goal.state:
        return [current.state]

    def heuristic(state):
        return sum(1 for i in range(3) for j in range(3) 
                  if state[i][j] != goal.state[i][j] and state[i][j] != 0)

    temperature = 100.0
    cooling_rate = 0.995
    steps = 0

    while temperature > 0.1 and steps < max_steps:
        if current.state == goal.state:
            return current.get_states()

        neighbors = [current.make_move(move) for move in current.get_valid_moves()]
        neighbors = [n for n in neighbors if n is not None]

        if not neighbors:
            return None

        next_state = random.choice(neighbors)
        delta_e = heuristic(next_state.state) - heuristic(current.state)

        if delta_e < 0 or random.random() < math.exp(-delta_e / temperature):
            current = next_state

        temperature *= cooling_rate
        steps += 1

    return None

def beam_search(initial_state, goal_state):
    """Beam Search"""
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
        
    beam_width = 3
    current_level = [initial]
    visited = {initial}
    
    while current_level:
        next_level = []
        
        for node in current_level:
            if node.state == goal.state:
                return node.get_states()
                
            for move in node.get_valid_moves():
                next_state = node.make_move(move)
                
                if next_state not in visited:
                    visited.add(next_state)
                    next_level.append((heuristic(next_state.state), next_state))
                    
        if not next_level:
            return None
            
        next_level.sort(key=lambda x: x[0])
        current_level = [node for _, node in next_level[:beam_width]]
        
    return None
