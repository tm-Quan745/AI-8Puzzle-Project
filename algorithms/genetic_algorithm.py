"""
Implementation of Genetic Algorithm for 8-puzzle problem
"""
import random
from models.puzzle_state import PuzzleState

def genetic_algorithm(initial_state, goal_state):
    """
    Genetic Algorithm implementation for solving 8-puzzle.
    Uses population-based evolution with crossover and mutation operators.
    
    Args:
        initial_state: Starting puzzle configuration
        goal_state: Target puzzle configuration
        
    Returns:
        List of states showing solution path if found, None otherwise
    """
    def create_individual():
        numbers = list(range(9))
        random.shuffle(numbers)
        return [numbers[i:i+3] for i in range(0, 9, 3)]
        
    def fitness(state):
        count = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != goal_state[i][j]:
                    count += 1
        return count
        
    def crossover(parent1, parent2):
        child = [[0 for _ in range(3)] for _ in range(3)]
        used = set()
        
        # Copy some elements from parent1
        for i in range(3):
            for j in range(3):
                if random.random() < 0.5:
                    child[i][j] = parent1[i][j]
                    used.add(parent1[i][j])
                    
        # Fill remaining positions from parent2
        for i in range(3):
            for j in range(3):
                if child[i][j] == 0:
                    for num in parent2[i]:
                        if num not in used:
                            child[i][j] = num
                            used.add(num)
                            break
                            
        return child
        
    def mutate(state):
        i1, j1 = random.randint(0, 2), random.randint(0, 2)
        i2, j2 = random.randint(0, 2), random.randint(0, 2)
        state[i1][j1], state[i2][j2] = state[i2][j2], state[i1][j1]
        return state
        
    # Initialize population
    population = [create_individual() for _ in range(100)]
    generations = 1000
    
    for _ in range(generations):
        # Evaluate fitness
        fitness_scores = [(fitness(state), state) for state in population]
        fitness_scores.sort()
        
        # Check if solution found
        if fitness_scores[0][0] == 0:
            return [initial_state] + [state for _, state in fitness_scores[:10]]
            
        # Select parents
        parents = [state for _, state in fitness_scores[:20]]
        
        # Create new generation
        new_population = []
        while len(new_population) < 100:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = crossover(parent1, parent2)
            
            if random.random() < 0.1:
                child = mutate(child)
                
            new_population.append(child)
            
        population = new_population
        
    return None
