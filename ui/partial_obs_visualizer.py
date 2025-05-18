# ui/partial_obs_visualizer.py
import tkinter as tk
from tkinter import ttk
import time

class PartialObsVisualizerWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Partial Observation 8-Puzzle")
        self.window.geometry("800x600")
        # Create main layout frames
        self.control_frame = ttk.Frame(self.window, padding="10")
        self.control_frame.grid(row=0, column=0, sticky="nsew")
        self.visual_frame = ttk.Frame(self.window, padding="10")
        self.visual_frame.grid(row=1, column=0, sticky="nsew")
        self.info_frame = ttk.Frame(self.window, padding="10")
        self.info_frame.grid(row=2, column=0, sticky="nsew")
        # Observable positions configuration
        self.observable_positions = [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]
        self.current_step = 0
        self.solution = None  # Will be a list of (state, observation) tuples
        self.initial_state = [
            [1, 2, 3],
            [4, 0, 6],
            [7, 5, 8]
        ]
        self.goal_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        self.setup_control_panel()
        self.setup_visualization()
        self.setup_info_panel()

    def setup_control_panel(self):
        self.run_button = ttk.Button(
            self.control_frame,
            text="Run Search",
            command=self.run_search
        )
        self.run_button.pack(side="left", padx=5)
        step_frame = ttk.Frame(self.control_frame)
        step_frame.pack(side="left", padx=20)
        self.prev_button = ttk.Button(
            step_frame,
            text="← Prev",
            command=self.prev_step,
            state="disabled"
        )
        self.prev_button.pack(side="left", padx=5)
        self.next_button = ttk.Button(
            step_frame,
            text="Next →",
            command=self.next_step,
            state="disabled"
        )
        self.next_button.pack(side="left", padx=5)
        goto_frame = ttk.Frame(self.control_frame)
        goto_frame.pack(side="left", padx=10)
        ttk.Label(goto_frame, text="Go to Step:").pack(side="left")
        self.goto_var = tk.StringVar()
        self.goto_entry = ttk.Entry(goto_frame, width=4, textvariable=self.goto_var)
        self.goto_entry.pack(side="left")
        self.goto_entry.bind('<Return>', lambda e: self.goto_step())
        goto_btn = ttk.Button(goto_frame, text="Go", command=self.goto_step)
        goto_btn.pack(side="left", padx=2)
        self.restart_button = ttk.Button(
            self.control_frame,
            text="Restart",
            command=self.restart_solution,
            state="disabled"
        )
        self.restart_button.pack(side="left", padx=10)
        self.animate_var = tk.BooleanVar(value=False)
        self.animate_check = ttk.Checkbutton(
            self.control_frame,
            text="Animate",
            variable=self.animate_var
        )
        self.animate_check.pack(side="left", padx=20)
        self.speed_scale = ttk.Scale(
            self.control_frame,
            from_=0.1,
            to=2.0,
            orient="horizontal",
            length=100
        )
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side="left", padx=5)

    def goto_step(self):
        if not self.solution:
            return
        try:
            idx = int(self.goto_var.get())
            if 0 <= idx < len(self.solution):
                self.current_step = idx
                self.update_visualization()
                self.update_nav_buttons()
        except Exception:
            pass

    def restart_solution(self):
        if not self.solution:
            return
        self.current_step = 0
        self.update_visualization()
        self.update_nav_buttons()

    def update_nav_buttons(self):
        if not self.solution:
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self.restart_button.configure(state="disabled")
            return
        self.restart_button.configure(state="normal")
        if self.current_step == 0:
            self.prev_button.configure(state="disabled")
        else:
            self.prev_button.configure(state="normal")
        if self.current_step == len(self.solution)-1:
            self.next_button.configure(state="disabled")
        else:
            self.next_button.configure(state="normal")

    def setup_visualization(self):
        self.current_board = self.create_board(self.visual_frame, "Current State")
        self.current_board.grid(row=0, column=0, padx=20, pady=10)
        self.observation_board = self.create_board(self.visual_frame, "Observation")
        self.observation_board.grid(row=0, column=1, padx=20, pady=10)
        self.goal_board = self.create_board(self.visual_frame, "Goal State")
        self.goal_board.grid(row=0, column=2, padx=20, pady=10)

    def create_board(self, parent, title):
        frame = ttk.LabelFrame(parent, text=title, padding="10")
        cells = []
        for i in range(3):
            row = []
            for j in range(3):
                cell = ttk.Label(
                    frame,
                    width=4,
                    padding=10,
                    anchor="center",
                    background="#ffffff",
                    relief="solid",
                    borderwidth=1
                )
                cell.grid(row=i, column=j, padx=2, pady=2)
                row.append(cell)
            cells.append(row)
        frame.cells = cells
        return frame

    def setup_info_panel(self):
        self.status_var = tk.StringVar(value="Ready to start")
        self.status_label = ttk.Label(
            self.info_frame,
            textvariable=self.status_var,
            wraplength=600
        )
        self.status_label.pack(fill="x", padx=10, pady=5)
        self.step_var = tk.StringVar(value="Step: 0/0")
        self.step_label = ttk.Label(
            self.info_frame,
            textvariable=self.step_var
        )
        self.step_label.pack(fill="x", padx=10, pady=5)

    def get_observation(self, state):
        obs = [[None]*3 for _ in range(3)]
        for i, j in self.observable_positions:
            obs[i][j] = state[i][j]
        return obs

    def run_search(self):
        self.current_step = 0
        self.solution = None
        initial_state = self.initial_state
        goal_state = self.goal_state
        self.run_button.configure(state="disabled")
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        self.status_var.set("Running partial observation solver...")
        self.window.update_idletasks()
        self.update_board(self.current_board, initial_state)
        self.update_board(self.goal_board, goal_state)
        initial_obs = self.get_observation(initial_state)
        self.update_board(self.observation_board, initial_obs, True)
        from utils.validators import is_solvable
        if not is_solvable(initial_state):
            self.handle_search_error("Initial state is not solvable!")
            self.run_button.configure(state="normal")
            return
        try:
            start_time = time.time()
            from algorithms.complex_search import partial_obs_solve
            solution_path = partial_obs_solve(initial_state, goal_state)
            search_time = time.time() - start_time
            if solution_path and len(solution_path) > 0:
                self.solution = [(state, self.get_observation(state)) for state in solution_path]
                self.handle_successful_search(search_time)
            else:
                self.handle_failed_search()
        except Exception as e:
            self.handle_search_error(str(e))
        finally:
            self.run_button.configure(state="normal")

    def handle_successful_search(self, search_time):
        self.status_var.set(f"Solution found in {search_time:.2f} seconds!")
        self.step_var.set(f"Step: 0/{len(self.solution)-1}")
        self.current_step = 0
        self.update_visualization()
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="disabled")
        if self.animate_var.get():
            self.animate_solution()

    def handle_failed_search(self):
        self.status_var.set("No solution found! The puzzle may be unsolvable from this state.")
        self.step_var.set("Step: 0/0")

    def handle_search_error(self, error_msg):
        self.status_var.set(f"Error during search: {error_msg}")
        self.step_var.set("Step: 0/0")

    def update_board(self, board_frame, state, is_observation=False):
        for i in range(3):
            for j in range(3):
                cell = board_frame.cells[i][j]
                if is_observation and (i,j) not in self.observable_positions:
                    cell.configure(text="?", background="#e0e0e0", foreground="#888888")
                    continue
                value = state[i][j]
                if value == 0 or value is None:
                    cell.configure(text="", background="#ffffff", foreground="#37474f")
                else:
                    cell.configure(text=str(value), background="#e3f2fd", foreground="#37474f")

    def prev_step(self):
        if not self.solution or self.current_step <= 0:
            return
        self.current_step -= 1
        self.update_visualization()
        self.update_nav_buttons()

    def next_step(self):
        if not self.solution or self.current_step >= len(self.solution)-1:
            return
        self.current_step += 1
        self.update_visualization()
        self.update_nav_buttons()

    def update_visualization(self):
        if not self.solution:
            return
        state, observation = self.solution[self.current_step]
        self.update_board(self.current_board, state)
        self.update_board(self.observation_board, observation, True)
        self.step_var.set(f"Step: {self.current_step}/{len(self.solution)-1}")

    def animate_solution(self):
        if not self.solution or self.current_step >= len(self.solution)-1:
            return
        self.next_step()
        if self.animate_var.get() and self.current_step < len(self.solution)-1:
            delay = int(1000 / self.speed_scale.get())
            self.window.after(delay, self.animate_solution)
