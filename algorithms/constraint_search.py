"""
Module chứa các thuật toán tìm kiếm ràng buộc
"""
from models.puzzle_state import PuzzleState

def backtracking_solve_with_constraints(initial_state, goal_state):
    """Backtracking with Constraints"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    def is_valid(state):
        numbers = set()
        for row in state:
            for num in row:
                if num in numbers:
                    return False
                numbers.add(num)
        return len(numbers) == 9
        
    def backtrack(current, visited):
        if current.state == goal.state:
            return current.get_states()
            
        if current in visited:
            return None
            
        visited.add(current)
        
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            
            if is_valid(next_state.state):
                result = backtrack(next_state, visited)
                if result:
                    return result
                    
        return None
        
    return backtrack(initial, set())

def forward_checking(initial_state, goal_state):
    """Forward Checking"""
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)
    
    if initial.state == goal.state:
        return [initial.state]
        
    def get_domain(state):
        used = set()
        for row in state:
            for num in row:
                if num != 0:
                    used.add(num)
        return set(range(9)) - used
        
    def forward_check(current, move):
        next_state = current.make_move(move)
        domain = get_domain(next_state.state)
        
        if not domain:
            return None
            
        return next_state
        
    def search(current, visited):
        if current.state == goal.state:
            return current.get_states()
            
        if current in visited:
            return None
            
        visited.add(current)
        
        for move in current.get_valid_moves():
            next_state = forward_check(current, move)
            
            if next_state:
                result = search(next_state, visited)
                if result:
                    return result
                    
        return None
        
    return search(initial, set())

def ac3_solve(initial_state, goal_state):
    """AC-3 Algorithm (CSP style for 8-puzzle)"""
    from copy import deepcopy
    initial = PuzzleState(initial_state)
    goal = PuzzleState(goal_state)

    if initial.state == goal.state:
        return [initial.state]

    # Build variable list (positions of all tiles)
    variables = [(i, j) for i in range(3) for j in range(3)]
    # Build initial domains: each cell can be any value not already used in that cell
    def get_domains(state):
        used = set()
        for row in state:
            for num in row:
                if num != 0:
                    used.add(num)
        domains = {}
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    domains[(i, j)] = set(range(1, 9)) - used
                else:
                    domains[(i, j)] = {state[i][j]}
        return domains

    def ac3(domains):
        # Build all arcs (binary constraints: all pairs of variables must have different values)
        queue = [(xi, xj) for xi in variables for xj in variables if xi != xj]
        while queue:
            xi, xj = queue.pop(0)
            if revise(domains, xi, xj):
                if not domains[xi]:
                    return False
                for xk in variables:
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))
        return True

    def revise(domains, xi, xj):
        revised = False
        to_remove = set()
        for x in domains[xi]:
            # If for all y in domain[xj], x == y, then remove x
            if all(x == y for y in domains[xj]):
                to_remove.add(x)
                revised = True
        if to_remove:
            domains[xi] -= to_remove
        return revised

    def search(current, visited):
        if current.state == goal.state:
            return current.get_states()
        if current in visited:
            return None
        visited.add(current)
        domains = get_domains(current.state)
        if not ac3(domains):
            return None
        for move in current.get_valid_moves():
            next_state = current.make_move(move)
            result = search(next_state, visited)
            if result:
                return result
        return None

    return search(initial, set())
