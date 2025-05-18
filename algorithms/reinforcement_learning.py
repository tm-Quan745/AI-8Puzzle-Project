"""
Module chứa các thuật toán học máy (Machine Learning)
"""
import random
import numpy as np
from models.puzzle_state import PuzzleState

def q_learning(initial_state, goal_state, alpha=0.1, gamma=0.9, epsilon_start=0.1, epsilon_decay=0.99, epsilon_min=0.01, episodes=5000, max_steps=100):
    """Q-Learning algorithm with parameterized alpha, gamma, and epsilon.

    Args:
        initial_state (list[list[int]]): The starting state of the puzzle.
        goal_state (list[list[int]]): The target state of the puzzle.
        alpha (float): Learning rate (default 0.1).
        gamma (float): Discount factor (default 0.9).
        epsilon_start (float): Initial exploration rate (default 0.1).
        epsilon_decay (float): Decay rate for epsilon (default 0.99).
        epsilon_min (float): Minimum exploration rate (default 0.01).
        episodes (int): Number of training episodes (default 5000).
        max_steps (int): Maximum steps per episode (default 100).

    Returns:
        tuple: A tuple containing the solution path (list of states) and the number of episodes run.
               Returns (None, episodes_run) if no solution found in solving phase.
    """
    q_table = {}
    actions = ['up', 'down', 'left', 'right']

    def get_state_key(state):
        return tuple(tuple(row) for row in state)

    def get_action(state, epsilon):
        state_key = get_state_key(state)
        if state_key not in q_table:
            q_table[state_key] = {a: 0.0 for a in actions}

        if random.random() < epsilon:
            return random.choice(actions)
        return max(q_table[state_key], key=q_table[state_key].get)

    def update_q(state, action, reward, next_state):
        state_key = get_state_key(state)
        next_state_key = get_state_key(next_state)

        if state_key not in q_table:
            q_table[state_key] = {a: 0.0 for a in actions}
        if next_state_key not in q_table:
            q_table[next_state_key] = {a: 0.0 for a in actions}

        old_value = q_table[state_key][action]
        next_max = max(q_table[next_state_key].values())

        # Q-Learning formula
        q_table[state_key][action] = old_value + alpha * (reward + gamma * next_max - old_value)

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
    episodes_run = 0

    for episode in range(episodes):
        episodes_run += 1
        state = [row[:] for row in initial_state]
        epsilon = max(epsilon_min, epsilon_start * (epsilon_decay ** episode))

        for step in range(max_steps):
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
    max_solve_steps = 1000 # Increased max_solve_steps for better chance

    for _ in range(max_solve_steps):
        state_key = get_state_key(state)
        if state_key in visited:
            # print("Solving phase: Visited state detected, stopping.") # Debug print
            break
        visited.add(state_key)

        # Greedily choose the best action based on the learned Q-values
        action = None
        state_q_values = q_table.get(state_key, {a: 0.0 for a in actions})
        if state_q_values:
             action = max(state_q_values, key=state_q_values.get)

        if action is None or state_q_values[action] == 0.0:
            # print(f"Solving phase: No learned action or Q-value is 0 for state {state}, stopping.") # Debug print
            break # Cannot proceed if no action is chosen or Q-value is zero

        next_state = apply_action(state, action)

        # Check if the action actually changed the state (avoid getting stuck)
        if next_state == state:
             # print(f"Solving phase: Action '{action}' did not change state, stopping.") # Debug print
             break

        solution.append(next_state)

        if next_state == goal_state:
            # print("Solving phase: Goal state reached.") # Debug print
            return solution, episodes_run # Return solution and episodes run
        state = next_state

    # If solving phase finishes without reaching goal
    # print("Solving phase: Max steps reached or stuck, returning current solution.") # Debug print
    return None, episodes_run # Return None for solution if goal not reached, but return episodes run

