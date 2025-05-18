"""
Visualization UI for No-Observation Search
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from algorithms.no_observation import no_observation_search

def format_state(state):
    """Format a single state as a string"""
    rows = []
    for row in state:
        row_str = ' '.join(str(x if x != 0 else '_') for x in row)
        rows.append(row_str)
    return '\n'.join(rows)

def format_belief_state(belief_state):
    """Format entire belief state as string"""
    state_strings = []
    for i, state in enumerate(belief_state):
        state_strings.append(f"State {i+1}:")
        state_strings.append(format_state(state))
    return '\n\n'.join(state_strings)

def run_search_and_display(text_widget):
    """Run search and display results"""
    text_widget.delete(1.0, tk.END)
    
    # Initial states representing uncertainty about blank position
    initial_belief_state = [
        [[1, 2, 3],
         [0, 4, 6],
         [7, 5, 8]],
        [[1, 2, 3],
         [4, 0, 6],
         [7, 5, 8]]
    ]
    
    goal_state = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ]
    
    # Run search with timing
    text_widget.insert(tk.END, "Starting search...\n\n")
    start_time = time.time()
    
    try:
        solution, trace = no_observation_search(initial_belief_state, goal_state)
        elapsed = time.time() - start_time
        
        text_widget.insert(tk.END, f"Search completed in {elapsed:.3f} seconds\n")
        text_widget.insert(tk.END, "="*60 + "\n\n")
        
        # Display trace
        for step in trace:
            # Step header
            text_widget.insert(tk.END, f"Step {step['step']} (Level {step['level']})\n")
            text_widget.insert(tk.END, "-"*40 + "\n")
            
            # Action and explanation
            if step['chosen_action']:
                text_widget.insert(tk.END, f"Action: {step['chosen_action']}\n")
            text_widget.insert(tk.END, f"Status: {step['explanation']}\n\n")
            
            # Belief states
            text_widget.insert(tk.END, "Current belief state:\n")
            text_widget.insert(tk.END, format_belief_state(step['belief_state_before']))
            text_widget.insert(tk.END, "\n\n")
            
            if step['belief_state_after'] != step['belief_state_before']:
                text_widget.insert(tk.END, "Resulting belief state:\n")
                text_widget.insert(tk.END, format_belief_state(step['belief_state_after']))
                text_widget.insert(tk.END, "\n")
            
            if step['backtrack']:
                text_widget.insert(tk.END, "🔙 BACKTRACKING\n")
                
            text_widget.insert(tk.END, "="*60 + "\n\n")
            text_widget.see(tk.END)
        
        # Display solution
        if solution:
            text_widget.insert(tk.END, "✅ Solution found!\n")
            text_widget.insert(tk.END, f"Path: {' → '.join(solution)}\n")
        else:
            text_widget.insert(tk.END, "❌ No solution found\n")
            
    except Exception as e:
        text_widget.insert(tk.END, f"Error occurred: {str(e)}\n")
    
    text_widget.see(tk.END)

def create_visualization_window():
    """Create the main visualization window"""
    window = tk.Tk()
    window.title("8-Puzzle No-Observation Search Visualization")
    window.geometry("1000x800")
    
    # Title
    title = tk.Label(
        window, 
        text="8-Puzzle No-Observation Search", 
        font=("Arial", 16, "bold")
    )
    title.pack(pady=10)
    
    # Description
    description = ttk.Label(
        window,
        text="Visualizing search through belief states with limited observability",
        wraplength=800
    )
    description.pack(pady=5)
    
    # Output text area
    text_output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        width=100,
        height=40,
        font=("Courier", 10)
    )
    text_output.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    
    # Control buttons
    button_frame = ttk.Frame(window)
    button_frame.pack(pady=10)
    
    run_button = ttk.Button(
        button_frame,
        text="Run Search",
        command=lambda: run_search_and_display(text_output)
    )
    run_button.pack(side=tk.LEFT, padx=5)
    
    clear_button = ttk.Button(
        button_frame,
        text="Clear",
        command=lambda: text_output.delete(1.0, tk.END)
    )
    clear_button.pack(side=tk.LEFT, padx=5)
    
    return window

def start_visualization():
    """Start the visualization"""
    window = create_visualization_window()
    window.mainloop()

if __name__ == "__main__":
    start_visualization()
