"""
Module for No-Observation Search implementation with belief states
"""
from models.puzzle_state import PuzzleState
import itertools

def get_valid_moves(state):
    """Get all valid moves for a state"""
    moves = []
    empty_pos = None
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                empty_pos = (i, j)
                break
        if empty_pos:
            break
            
    if not empty_pos:
        return []
        
    # Check all possible moves
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # up, down, left, right
        new_x, new_y = empty_pos[0] + dx, empty_pos[1] + dy
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            moves.append((new_x, new_y, get_move_direction(dx, dy)))
    return moves

def get_move_direction(dx, dy):
    """Convert delta x,y to move direction string"""
    if dx == -1: return "up"
    if dx == 1: return "down" 
    if dy == -1: return "left"
    if dy == 1: return "right"
    return None

def apply_move(state, move_pos):
    """Apply a move to a state and return new state"""
    new_state = [row[:] for row in state]
    empty_pos = None
    for i in range(3):
        for j in range(3):
            if new_state[i][j] == 0:
                empty_pos = (i, j)
                break
        if empty_pos:
            break
            
    if not empty_pos:
        return None
        
    new_x, new_y = move_pos[:2] # Ignore direction part
    old_x, old_y = empty_pos
    
    if not (0 <= new_x < 3 and 0 <= new_y < 3):
        return None
        
    new_state[old_x][old_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[old_x][old_y]
    return new_state

def no_observation_search(initial_belief_state, goal_state, max_steps=5):
    """
    No-Observation Search with belief states
    Returns: (solution, trace) where:
        - solution is list of moves if found, None if not
        - trace is list of steps showing search process
    """
    def belief_to_hashable(belief_state):
        """Convert belief state to hashable form for visited set"""
        return tuple(tuple(tuple(row) for row in state) for state in sorted(belief_state, key=str))

    def manhattan_distance(state1, state2):
        """Calculate Manhattan distance between two states"""
        distance = 0
        for i1 in range(3):
            for j1 in range(3):
                if state1[i1][j1] != 0:  # Don't count empty space
                    # Find same number in state2
                    for i2 in range(3):
                        for j2 in range(3):
                            if state2[i2][j2] == state1[i1][j1]:
                                distance += abs(i1 - i2) + abs(j1 - j2)
        return distance

    def estimate_distance_to_goal(belief_state):
        """Heuristic: minimum Manhattan distance from any belief state to goal"""
        return min(manhattan_distance(state, goal_state) for state in belief_state)

    trace = []  # Track search process
    path = []  # Track solution path
    visited = {belief_to_hashable(initial_belief_state)}
    
    def search_recursive(curr_belief, level=0):
        """Recursive implementation of no-observation search"""
        # Add current state to trace
        trace.append({
            'step': len(trace),
            'level': level,
            'belief_state_before': curr_belief,
            'chosen_action': None,
            'belief_state_after': curr_belief,
            'explanation': "Checking current belief state",
            'backtrack': False
        })

        # Check if exceeded max steps
        if level >= max_steps:
            trace[-1]['explanation'] = "Exceeded maximum steps"
            return None

        # Check if goal reached
        if any(state == goal_state for state in curr_belief):
            trace[-1]['explanation'] = "Goal state found!"
            return path

        # Get valid moves for all states
        all_moves = set()
        for state in curr_belief:
            moves = get_valid_moves(state)
            all_moves.update((m[2], m) for m in moves)  # Group by direction

        # Try each move
        for direction, move in sorted(all_moves):
            # Apply move to all states where possible
            next_belief = []
            for state in curr_belief:
                next_state = apply_move(state, move)
                if next_state:
                    next_belief.append(next_state)

            if not next_belief:
                continue

            # Check if belief state was visited
            belief_hash = belief_to_hashable(next_belief)
            if belief_hash in visited:
                continue

            # Record this step
            trace.append({
                'step': len(trace),
                'level': level,
                'belief_state_before': curr_belief,
                'chosen_action': direction,
                'belief_state_after': next_belief,
                'explanation': f"Trying {direction} move",
                'backtrack': False
            })

            # Add to visited and path
            visited.add(belief_hash)
            path.append(direction)

            # Recurse
            result = search_recursive(next_belief, level + 1)
            if result is not None:
                return result

            # Remove from path if failed
            path.pop()
            
            # Record backtrack
            trace.append({
                'step': len(trace),
                'level': level,
                'belief_state_before': next_belief,
                'chosen_action': None,
                'belief_state_after': curr_belief,
                'explanation': f"Backtracking from {direction} move",
                'backtrack': True
            })

        return None

    # Start search
    solution = search_recursive(initial_belief_state)
    return solution, trace
