import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import os

# Adjust PYTHONPATH to import modules from the algorithms directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
if project_root not in sys.path:
    sys.path.append(os.path.join(project_root, 'algorithms'))

# Import specific algorithms from your project
try:
    from algorithms.constraint_search import (
        backtracking_solve_with_constraints,
        forward_checking,
        ac3_solve
    )
    print("Successfully imported constraint search algorithms.")
except ImportError as e:
    print(f"Error importing algorithms: {e}")
    print("Please ensure your project structure is correct and you are running the script from the project root.")
    sys.exit("Could not import algorithms. Please check your project setup.")

# Define the constraint search algorithms to compare
constraint_algorithms = {
    'Backtracking': backtracking_solve_with_constraints,
    'Forward Checking': forward_checking,
    'AC-3': ac3_solve
}

# Define a sample 8-puzzle problem
sample_problems = {
    'Bai toan mau': (
        [[1, 2, 3], [4, 0, 6], [7, 5, 8]],  # Initial State
        [[1, 2, 3], [4, 5, 6], [7, 8, 0]]   # Goal State
    ),
}

# Collect performance data
performance_data = {}

for problem_name, (initial_state, goal_state) in sample_problems.items():
    print(f"\nRunning algorithms on: {problem_name}")
    performance_data[problem_name] = {}

    for algo_name, algo_func in constraint_algorithms.items():
        print(f"  Running {algo_name}...")
        start_time = time.time()
        try:
            # Run the algorithm
            solution_path = algo_func(initial_state, goal_state)
            exec_time = time.time() - start_time

            steps = None
            if solution_path is not None:
                steps = len(solution_path) - 1 # Number of steps is path length - 1

            performance_data[problem_name][algo_name] = {
                'time': exec_time,
                'steps': steps
            }
            print(f"    Completed in {exec_time:.4f}s, steps: {steps if steps is not None else 'N/A'}")

        except Exception as e:
            print(f"    Error running {algo_name}: {e}")
            performance_data[problem_name][algo_name] = {
                'time': None,
                'steps': None,
                'error': str(e)
            }

# Plotting the results
problem_to_plot = list(sample_problems.keys())[0] # Assuming only one sample problem for now

if problem_to_plot in performance_data:
    problem_data = performance_data[problem_to_plot]

    # Prepare data for plotting
    algo_names = list(constraint_algorithms.keys())
    
    # Extract times, handle None values for plotting
    times = []
    for algo in algo_names:
        time_val = problem_data[algo].get('time')
        times.append(time_val if time_val is not None else 0)
    
    # Extract steps, handle None values for plotting and labels
    steps = []
    steps_labels = []
    for algo in algo_names:
        step_val = problem_data[algo].get('steps')
        steps.append(step_val if step_val is not None else 0)
        steps_labels.append(str(step_val) if step_val is not None else 'N/A')

    x = np.arange(len(algo_names))
    width = 0.35

    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle(f'So sánh hiệu suất thuật toán Tìm kiếm Ràng buộc trên "{problem_to_plot}"', y=1.02)

    # Biểu đồ Thời gian thực thi
    rects1 = ax[0].bar(x, times, width, label='Thời gian thực thi')
    ax[0].set_ylabel('Thời gian (s)')
    ax[0].set_title('Thời gian thực thi')
    ax[0].set_xticks(x)
    ax[0].set_xticklabels(algo_names)
    ax[0].legend()
    ax[0].bar_label(rects1, fmt='%.4f')

    # Biểu đồ Số bước của lời giải
    rects2 = ax[1].bar(x, steps, width, label='Số bước của lời giải', color='green')
    ax[1].set_ylabel('Số bước')
    ax[1].set_title('Số bước của lời giải')
    ax[1].set_xticks(x)
    ax[1].set_xticklabels(algo_names)
    ax[1].legend()
    for rect, label in zip(rects2, steps_labels):
        height = rect.get_height()
        ax[1].text(rect.get_x() + rect.get_width()/2., height, label,
                ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

else:
    print(f"Problem '{problem_to_plot}' not found in performance data.") 