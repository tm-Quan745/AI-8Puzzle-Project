import tkinter as tk
from tkinter import ttk

class NoObservationVisualizerWindow:
    def __init__(self, parent, trace, solution=None, initial_belief=None, goal_state=None):
        self.window = tk.Toplevel(parent)
        self.window.title("No-Observation Search Visualization")
        self.window.geometry("1200x750")
        self.trace = trace
        self.solution = solution
        self.current_step = 0
        self.initial_belief = initial_belief or []
        self.goal_state = goal_state
        self.is_animating = False
        self.setup_ui()
        self.show_step(0)

    def setup_ui(self):
        # Control panel
        control_frame = ttk.Frame(self.window, padding=10)
        control_frame.pack(fill="x")
        self.prev_btn = ttk.Button(control_frame, text="← Prev", command=self.prev_step)
        self.prev_btn.pack(side="left", padx=5)
        self.next_btn = ttk.Button(control_frame, text="Next →", command=self.next_step)
        self.next_btn.pack(side="left", padx=5)
        self.step_label = ttk.Label(control_frame, text="Step: 0/0")
        self.step_label.pack(side="left", padx=20)
        self.animate_var = tk.BooleanVar(value=False)
        self.animate_check = ttk.Checkbutton(control_frame, text="Animate", variable=self.animate_var, command=self.toggle_animation)
        self.animate_check.pack(side="left", padx=10)
        # Tăng tốc độ tối đa lên 5.0
        self.speed_scale = ttk.Scale(control_frame, from_=0.1, to=5.0, orient="horizontal", length=100)
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side="left", padx=5)
        # Main content
        self.content_frame = ttk.Frame(self.window, padding=10)
        self.content_frame.pack(fill="both", expand=True)
        # For dynamic content
        self.info_label = ttk.Label(self.content_frame, text="", font=("Arial", 12, "bold"), anchor="w", justify="left")
        self.info_label.pack(fill="x", pady=5)
        self.belief_frame = ttk.Frame(self.content_frame)
        self.belief_frame.pack(side="left", fill="y", pady=5, padx=10)
        self.goal_frame = ttk.Frame(self.content_frame)
        # Đặt goal_frame sát belief_frame hơn
        self.goal_frame.pack(side="left", fill="y", pady=5, padx=20)
        self.action_label = ttk.Label(self.content_frame, text="", font=("Arial", 11), anchor="w", justify="left")
        self.action_label.pack(fill="x", pady=5)
        self.explain_label = ttk.Label(self.content_frame, text="", font=("Arial", 10), anchor="w", justify="left", foreground="#666")
        self.explain_label.pack(fill="x", pady=5)
        # Show goal state
        if self.goal_state:
            self.show_goal_state()

    def show_step(self, idx):
        if not self.trace:
            return
        idx = max(0, min(idx, len(self.trace)-1))
        self.current_step = idx
        step = self.trace[idx]
        self.step_label.config(text=f"Step: {idx}/{len(self.trace)-1}")
        # Info
        self.info_label.config(text=f"Bước {idx} (Level {step.get('level', 0)})")
        # Belief states
        for widget in self.belief_frame.winfo_children():
            widget.destroy()
        belief_states = step.get('belief_state_before', [])
        # Gộp các trạng thái giống nhau
        unique_beliefs = []
        seen = set()
        found_goal = False
        for state in belief_states:
            t = tuple(tuple(row) for row in state)
            if t not in seen:
                unique_beliefs.append(state)
                seen.add(t)
            # Kiểm tra nếu có trạng thái trùng goal thì dừng animation
            if self.goal_state and state == self.goal_state:
                found_goal = True
        belief_label = ttk.Label(self.belief_frame, text=f"Trạng Thái Niềm Tin Hiện Tại ({len(unique_beliefs)} trạng thái)", font=("Arial", 11, "bold"))
        belief_label.pack(anchor="w")
        grid_frame = ttk.Frame(self.belief_frame)
        grid_frame.pack(anchor="w", pady=2)
        for idx_b, state in enumerate(unique_beliefs):
            state_frame = ttk.Frame(grid_frame, relief="solid", borderwidth=1)
            state_frame.grid(row=0, column=idx_b, padx=10)
            for i in range(3):
                for j in range(3):
                    val = state[i][j]
                    cell = ttk.Label(state_frame, text=str(val) if val != 0 else "", width=2, anchor="center", relief="ridge", borderwidth=1, font=("Arial", 14))
                    cell.grid(row=i, column=j, ipadx=6, ipady=4)
        # Action
        action = step.get('chosen_action', None)
        if action:
            self.action_label.config(text=f"Hành Động Được Chọn: {action}")
        else:
            self.action_label.config(text="")
        # Explanation
        explain = step.get('explanation', "")
        self.explain_label.config(text=explain)
        # Button state
        self.prev_btn.config(state="normal" if idx > 0 else "disabled")
        self.next_btn.config(state="normal" if idx < len(self.trace)-1 else "disabled")
        # Nếu đã đến bước cuối cùng hoặc đã tìm thấy goal thì thông báo đã tìm thấy hoặc kết thúc
        if found_goal or idx == len(self.trace)-1:
            self.is_animating = False
            self.animate_var.set(False)
            self.info_label.config(text=f"Đã tìm thấy trạng thái đích! Tổng số bước: {idx}" + (f"\nThời gian thực thi: {getattr(self, 'exec_time', 0):.3f} giây" if hasattr(self, 'exec_time') else ""))

    def show_goal_state(self):
        for widget in self.goal_frame.winfo_children():
            widget.destroy()
        label = ttk.Label(self.goal_frame, text="Trạng Thái Đích", font=("Arial", 11, "bold"), foreground="#d84315")
        label.pack(anchor="n")
        grid = ttk.Frame(self.goal_frame)
        grid.pack(anchor="n", pady=2)
        # Hiển thị trạng thái đích gần lại (padding nhỏ hơn, màu nổi bật)
        for i in range(3):
            for j in range(3):
                val = self.goal_state[i][j]
                cell = ttk.Label(grid, text=str(val) if val != 0 else "", width=2, anchor="center", relief="ridge", borderwidth=2, font=("Arial", 14, "bold"), background="#ffe0b2", foreground="#b71c1c")
                cell.grid(row=i, column=j, ipadx=6, ipady=4, padx=1, pady=1)
        grid.pack_configure(padx=5)

    def prev_step(self):
        self.show_step(self.current_step - 1)
    def next_step(self):
        self.show_step(self.current_step + 1)
    def toggle_animation(self):
        if self.animate_var.get():
            self.is_animating = True
            self.animate_steps()
        else:
            self.is_animating = False
    def animate_steps(self):
        if not self.is_animating:
            return
        if self.current_step < len(self.trace)-1:
            # Nếu belief state hiện tại đã có goal thì dừng luôn
            step = self.trace[self.current_step]
            belief_states = step.get('belief_state_before', [])
            if self.goal_state and any(state == self.goal_state for state in belief_states):
                self.is_animating = False
                self.animate_var.set(False)
                self.info_label.config(text=f"Đã tìm thấy trạng thái đích! Tổng số bước: {self.current_step}" + (f"\nThời gian thực thi: {getattr(self, 'exec_time', 0):.3f} giây" if hasattr(self, 'exec_time') else ""))
                return
            self.next_step()
            delay = int(1000 / (self.speed_scale.get() * 6))
            self.window.after(delay, self.animate_steps)
        else:
            self.is_animating = False
            self.animate_var.set(False)
            self.info_label.config(text=f"Đã hoàn thành! Tổng số bước: {len(self.trace)-1}" + (f"\nThời gian thực thi: {getattr(self, 'exec_time', 0):.3f} giây" if hasattr(self, 'exec_time') else ""))
