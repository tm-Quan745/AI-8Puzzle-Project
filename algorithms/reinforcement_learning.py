"""
Module chứa các thuật toán học máy (Machine Learning)
"""
import random
import numpy as np
from models.puzzle_state import PuzzleState

def q_learning(initial_state, goal_state):
    """Q-Learning algorithm"""
    q_table = {}
    actions = ['up', 'down', 'left', 'right']

    def get_state_key(state):
        return tuple(tuple(row) for row in state)

    def get_action(state, epsilon=0.1):
        state_key = get_state_key(state)
        if state_key not in q_table:
            q_table[state_key] = {a: 0.0 for a in actions}

        if random.random() < epsilon:
            return random.choice(actions)
        return max(q_table[state_key], key=q_table[state_key].get)

    def update_q(state, action, reward, next_state, alpha=0.1, gamma=0.9):
        state_key = get_state_key(state)
        next_state_key = get_state_key(next_state)

        if state_key not in q_table:
            q_table[state_key] = {a: 0.0 for a in actions}
        if next_state_key not in q_table:
            q_table[next_state_key] = {a: 0.0 for a in actions}

        old_value = q_table[state_key][action]
        next_max = max(q_table[next_state_key].values())

        new_value = old_value + alpha * (reward + gamma * next_max - old_value)
        q_table[state_key][action] = new_value

    def get_reward(state):
        return 100 if state == goal_state else -1

    def apply_action(state, action):
        state_copy = [row[:] for row in state]
        for i in range(3):
            for j in range(3):
                if state_copy[i][j] == 0:
                    x, y = i, j
        dx = {'up': -1, 'down': 1, 'left': 0, 'right': 0}
        dy = {'up': 0, 'down': 0, 'left': -1, 'right': 1}
        nx, ny = x + dx[action], y + dy[action]

        if 0 <= nx < 3 and 0 <= ny < 3:
            state_copy[x][y], state_copy[nx][ny] = state_copy[nx][ny], state_copy[x][y]
            return state_copy
        return state

    # Training phase
    episodes = 5000
    max_steps = 100

    for episode in range(episodes):
        state = [row[:] for row in initial_state]
        epsilon = max(0.01, 0.1 * (0.99 ** episode))

        for _ in range(max_steps):
            action = get_action(state, epsilon)
            next_state = apply_action(state, action)
            reward = get_reward(next_state)
            update_q(state, action, reward, next_state)
            state = next_state
            if state == goal_state:
                break

    # Solving phase
    state = [row[:] for row in initial_state]
    solution = [state]
    visited = set()
    max_solve_steps = 100

    for _ in range(max_solve_steps):
        state_key = get_state_key(state)
        if state_key in visited:
            break
        visited.add(state_key)

        action = get_action(state, epsilon=0)  # always exploit
        next_state = apply_action(state, action)
        solution.append(next_state)
        if next_state == goal_state:
            break
        state = next_state

    return solution

