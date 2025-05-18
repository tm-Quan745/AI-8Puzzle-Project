"""
Module chứa các thuật toán tìm kiếm trong môi trường phức tạp
"""
from models.puzzle_state import PuzzleState

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
            moves.append((new_x, new_y))
    return moves

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
        
    new_x, new_y = move_pos
    old_x, old_y = empty_pos
    
    if not (0 <= new_x < 3 and 0 <= new_y < 3):
        return None
        
    new_state[old_x][old_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[old_x][old_y]
    return new_state

def and_or_search(initial_state, goal_state):
    """AND-OR Search algorithm"""
    MAX_DEPTH = 30
    visited = set()

    def or_search(state, path, depth=0):
        if state == goal_state:
            return []
        if tuple(map(tuple, state)) in path or depth > MAX_DEPTH:
            return None
        visited.add(tuple(map(tuple, state)))
        for move in get_valid_moves(state):
            next_state = apply_move(state, move)
            if next_state:
                result = and_search([next_state], path + [tuple(map(tuple, state))], depth + 1)
                if result is not None:
                    return [next_state] + result
        return None

    def and_search(states, path, depth):
        plan = []
        for state in states:
            subplan = or_search(state, path, depth)
            if subplan is None:
                return None
            plan.extend(subplan)
        return plan

    plan = or_search(initial_state, [])
    if plan:
        return [initial_state] + plan
    return None

def get_observation(state, observable_positions):
    """Get observation from state with observable positions"""
    observation = [[None for _ in range(3)] for _ in range(3)]
    for i, j in observable_positions:
        observation[i][j] = state[i][j]
    return observation

def is_observation_match(state, observation):
    """Check if a state matches an observation"""
    for i in range(3):
        for j in range(3):
            if observation[i][j] is not None and observation[i][j] != state[i][j]:
                return False
    return True

def update_belief_with_observation(belief_state, observation):
    """Update belief state based on new observation"""
    return [state for state in belief_state if is_observation_match(state, observation)]

def partial_obs_solve(initial_state, goal_state):
    from utils.validators import is_solvable
    import itertools

    # Set a fixed initial state for partial observation
    initial_state = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 0, 8]
    ]

    # Observable positions - can only see corners and center
    observable_positions = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]
    initial_obs = get_observation(initial_state, observable_positions)

    # Sinh tất cả các hoán vị có thể của 0-8
    all_numbers = set(range(9))
    possible_states = []
    for perm in itertools.permutations(range(9)):
        state = [list(perm[0:3]), list(perm[3:6]), list(perm[6:9])]
        # Kiểm tra observation
        match = True
        for i, j in observable_positions:
            if initial_obs[i][j] is not None and state[i][j] != initial_obs[i][j]:
                match = False
                break
        if match:
            possible_states.append(state)

    if not possible_states:
        return None

    # Lọc lại chỉ giữ các trạng thái solvable nếu goal_state cũng solvable
    if is_solvable(goal_state):
        possible_states = [s for s in possible_states if is_solvable(s)]
        if not possible_states:
            return None

    initial_belief_state = possible_states
    
    def belief_to_hashable(belief_state):
        return tuple(tuple(tuple(row) for row in state) for state in sorted(belief_state, key=str))

    def estimate_distance_to_goal(belief_state):
        total_distance, count = 0, 0
        for state in belief_state:
            for i, j in observable_positions:
                if state[i][j] != 0 and state[i][j] != goal_state[i][j]:
                    for x in range(3):
                        for y in range(3):
                            if goal_state[x][y] == state[i][j]:
                                total_distance += abs(i - x) + abs(j - y)
                                count += 1
                                break
        return total_distance / (count if count > 0 else 1)

    solution_path = []
    current_belief = initial_belief_state
    visited = {belief_to_hashable(initial_belief_state)}
    max_steps = 30

    for step in range(max_steps):
        solution_path.append(current_belief[0])
        
        obs = get_observation(current_belief[0], observable_positions)
        current_belief = update_belief_with_observation(current_belief, obs)

        # Check if goal reached
        if any(all(state[i][j] == goal_state[i][j] for i in range(3) for j in range(3)) 
               for state in current_belief):
            solution_path.append(goal_state)
            return solution_path

        # Get valid moves
        valid_moves = set()
        for state in current_belief:
            valid_moves.update(get_valid_moves(state))

        if not valid_moves:
            return None

        # Choose best move
        best_move_pos = None
        min_distance = float('inf')
        best_next_belief = None

        for move_pos in valid_moves:
            next_belief = []
            for state in current_belief:
                next_state = apply_move(state, move_pos)
                if next_state:
                    next_belief.append(next_state)

            if not next_belief:
                continue

            next_obs = get_observation(next_belief[0], observable_positions)
            updated_belief = update_belief_with_observation(next_belief, next_obs)
            
            if updated_belief:
                distance = estimate_distance_to_goal(updated_belief)
                if distance < min_distance:
                    min_distance = distance
                    best_move_pos = move_pos
                    best_next_belief = updated_belief

        if not best_move_pos or not best_next_belief:
            return None

        next_belief_hash = belief_to_hashable(best_next_belief)
        if next_belief_hash in visited:
            return None

        current_belief = best_next_belief
        visited.add(next_belief_hash)

    return None

def non_observe(initial_state, goal_state):
    """Non-Observable Search"""
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
