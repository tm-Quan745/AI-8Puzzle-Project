import tkinter as tk
from .imports import *
import time
from ui.partial_obs_visualizer import PartialObsVisualizerWindow
from algorithms.uninformed_search import (
    bfs_solve, dfs_solve, ucs_solve, iddfs_solve
)
from algorithms.informed_search import (
    greedy_best_first_search, a_star_search, ida_star_search
)
from algorithms.local_search import (
    hill_climbing_simple, hill_climbing_steepest, stochastic_hill_climbing,
    simulated_annealing, beam_search
)
from algorithms.genetic_algorithm import genetic_algorithm
from algorithms.complex_search import (
    and_or_search, partial_obs_solve, non_observe
)
from algorithms.constraint_search import (
    backtracking_solve_with_constraints, forward_checking, ac3_solve
)
from algorithms.reinforcement_learning import (
    q_learning
)

class PuzzleSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        self.root.state('zoomed')  # Mở cửa sổ full màn hình
        
        # Khởi tạo trạng thái ban đầu và đích
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
        self.current_state = [row[:] for row in self.initial_state]
        
        # Trạng thái thuật toán
        self.solution = None
        self.current_algorithm = None
        self.step = 0
        self.total_steps = 0
        self.stop_flag = False
        
        # Trạng thái thời gian
        self.execution_time = 0
        self.animation_start_time = None
        self.animation_elapsed_time = 0
        
        # Trạng thái animation
        self.is_animating = False
        self.animation_speed = 20  # frames per second
        self.animation_frames = 10  # frames per move
        
        # Lịch sử thuật toán
        self.algorithm_history = []
        
        self.setup_ui()

    def setup_ui(self):
        # Tạo style cho các widget
        style = ttk.Style()
        
        # Cấu hình màu nền tổng thể
        self.root.configure(bg='#f4f8fb')  # Nền sáng xanh nhẹ
        
        # Style cho LabelFrame
        style.configure('My.TLabelframe', background='#e3f2fd', borderwidth=0)
        style.configure('My.TLabelframe.Label', 
            font=('Segoe UI', 12, 'bold'), 
            foreground='#1976d2', 
            background='#e3f2fd'
        )
        style.configure('TButton', font=('Segoe UI', 11), padding=8)
        style.configure('TLabel', font=('Segoe UI', 11))
        
        # Frame chính (cố định kích thước)
        main_frame = ttk.Frame(self.root, padding="20", style='My.TLabelframe', width=1200, height=700)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_propagate(False)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Tiêu đề (căn giữa, font lớn, màu nổi bật)
        title_label = ttk.Label(main_frame, text="8-Puzzle Solver", font=('Segoe UI', 28, 'bold'), foreground='#1565c0', anchor='center')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 24), sticky='ew')
          # Khung chứa nhóm thuật toán (trái)
        groups_frame = ttk.LabelFrame(main_frame, text="Algorithm Groups", padding="12", style='My.TLabelframe', width=300, height=380)
        groups_frame.grid(row=1, column=0, padx=(50, 24), sticky="n")
        groups_frame.grid_propagate(False)
        
        # Khung chứa thuật toán (giữa)
        self.algorithms_frame = ttk.LabelFrame(main_frame, text="Algorithms", padding="12", style='My.TLabelframe', width=300, height=380)
        self.algorithms_frame.grid(row=1, column=1, padx=24, pady=10, sticky="n")
        self.algorithms_frame.grid_propagate(False)
        
        # Khung chứa bảng trạng thái (phải)
        board_frame = ttk.LabelFrame(main_frame, text="Puzzle State", padding="12", style='My.TLabelframe', width=340, height=340)
        board_frame.grid(row=1, column=2, padx=(24, 50), sticky="n")
        board_frame.grid_propagate(False)

        # Tạo bảng trạng thái puzzle
        self.create_board(board_frame)

        # Thanh chỉnh tốc độ animation (slider) đặt dưới board
        speed_slider_frame = ttk.Frame(main_frame, style='My.TLabelframe', width=340)
        speed_slider_frame.grid(row=2, column=2, sticky="ew", pady=(10, 0))
        speed_label = ttk.Label(speed_slider_frame, text="Animation Speed", font=("Segoe UI", 10, "bold"), style='My.TLabelframe.Label')
        speed_label.pack(side='left', padx=(0, 8))
        self.animation_speed_factor = 1.0
        def on_speed_change(val):
            self.animation_speed_factor = float(val)
        self.speed_slider = tk.Scale(
            speed_slider_frame, from_=1.0, to=5.0, resolution=0.1, orient='horizontal',
            length=140, showvalue=True, digits=2, command=on_speed_change,
            bg='#e3f2fd', troughcolor='#bbdefb', highlightthickness=0
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side='left')

        # Thanh trạng thái di chuyển (move history) đặt dưới speed slider
        self.move_history_frame = tk.Frame(main_frame, bg='#f4f8fb', width=340, height=54)
        self.move_history_frame.grid(row=3, column=2, sticky="ew", pady=(10, 0))
        self.move_history_canvas = tk.Canvas(self.move_history_frame, bg='#f4f8fb', width=340, height=54, highlightthickness=0)
        self.move_history_canvas.pack(side='left', fill='both', expand=True)
        self.move_history_scroll = tk.Scrollbar(self.move_history_frame, orient='horizontal', command=self.move_history_canvas.xview)
        self.move_history_scroll.pack(side='bottom', fill='x')
        self.move_history_canvas.configure(xscrollcommand=self.move_history_scroll.set)
        self.move_history_inner = tk.Frame(self.move_history_canvas, bg='#f4f8fb')
        self.move_history_inner.pack_propagate(True)
        self.move_history_window = self.move_history_canvas.create_window((0, 0), window=self.move_history_inner, anchor='nw')
        self.move_history_labels = []
        def on_configure(event):
            self.move_history_canvas.configure(scrollregion=self.move_history_canvas.bbox('all'))
        self.move_history_inner.bind('<Configure>', on_configure)        # Frame chứa các nút chức năng
        functions_frame = tk.Frame(main_frame, bg='#e3f2fd', padx=10, pady=10)
        functions_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 10), padx=(50, 24))
        # Tooltip helper
        def add_tooltip(widget, text):
            def on_enter(e):
                self.info_label.configure(text=text)
            def on_leave(e):
                self.info_label.configure(text="")
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        # Nút Start
        start_button = tk.Button(
            functions_frame, text="Start", font=('Segoe UI', 11, 'bold'),
            bg='#43a047', fg='white',
            activebackground='#66bb6a', activeforeground='white',
            relief='groove', borderwidth=0, padx=18, pady=7,
            command=self.start_action, cursor='hand2', highlightthickness=0
        )
        start_button.grid(row=0, column=0, padx=12, pady=0, sticky='w')
        add_tooltip(start_button, "Bắt đầu chạy animation lời giải")
        
        # Nút Input
        input_button = tk.Button(
            functions_frame, text="Input", font=('Segoe UI', 11, 'bold'),
            bg='#039be5', fg='white',
            activebackground='#29b6f6', activeforeground='white',
            relief='groove', borderwidth=0, padx=18, pady=7,
            command=self.input_action, cursor='hand2', highlightthickness=0
        )
        input_button.grid(row=0, column=1, padx=12, pady=0, sticky='w')
        add_tooltip(input_button, "Nhập trạng thái puzzle mới")
        
        # Nút Cancel
        cancel_button = tk.Button(
            functions_frame, text="Cancel", font=('Segoe UI', 11, 'bold'),
            bg='#e53935', fg='white',
            activebackground='#ef5350', activeforeground='white',
            relief='groove', borderwidth=0, padx=18, pady=7,
            command=self.cancel_action, cursor='hand2', highlightthickness=0
        )
        cancel_button.grid(row=0, column=2, padx=12, pady=0, sticky='w')
        add_tooltip(cancel_button, "Dừng animation hiện tại")
        
        # Nút History
        history_button = tk.Button(
            functions_frame, text="History", font=('Segoe UI', 11, 'bold'),
            bg='#8e24aa', fg='white',
            activebackground='#ba68c8', activeforeground='white',
            relief='groove', borderwidth=0, padx=18, pady=7,
            command=self.show_history, cursor='hand2', highlightthickness=0
        )
        history_button.grid(row=0, column=3, padx=12, pady=0, sticky='w')
        add_tooltip(history_button, "Xem lịch sử chạy thuật toán")

        # Khởi tạo nhóm thuật toán
        self.algorithm_groups = {
            "Uninformed Search": {
                'BFS': bfs_solve,
                'DFS': dfs_solve,
                'UCS': ucs_solve,
                'IDDFS': iddfs_solve
            },
            "Informed Search": {
                'Greedy': greedy_best_first_search,
                'A*': a_star_search,
                'IDA*': ida_star_search
            },
            "Local Search": {
                'Hill Simple': hill_climbing_simple,
                'Hill Steepest': hill_climbing_steepest,
                'Stochastic': stochastic_hill_climbing,
                'Simulated Annealing': simulated_annealing,
                'Genetic': genetic_algorithm,
                'Beam': beam_search
            },
            "Complex Environment": {
                'And-Or': and_or_search,
                'Partial Observed': partial_obs_solve,
                'Non Observed': non_observe
            },
            "Constraint Search": {
                'Backtracking': backtracking_solve_with_constraints,
                'Forward Checking': forward_checking,
                'AC-3': ac3_solve
            },
            "Reinforcement Learning": {
                'Q-Learning': q_learning
            }
        }
        
        self.group_buttons = {}
        self.algorithm_buttons = {}
        self.current_group = None
        
        # Tạo nút nhóm thuật toán
        for i, (group_name, _) in enumerate(self.algorithm_groups.items()):
            btn = tk.Button(
                groups_frame,
                text=group_name,
                font=('Segoe UI', 12, 'bold'),
                bg='#bbdefb',
                fg='#1565c0',
                activebackground='#90caf9',
                activeforeground='#1565c0',
                relief='groove',
                borderwidth=0,
                padx=10,
                pady=7,
                width=20,
                command=lambda g=group_name: self.show_algorithms(g),
                cursor='hand2',
                highlightthickness=0
            )
            btn.grid(row=i, column=0, pady=7, sticky="ew")
            self.group_buttons[group_name] = btn
            add_tooltip(btn, f"Chọn nhóm: {group_name}")
        
        # Nút reset
        reset_btn = tk.Button(
            main_frame,
            text="Reset",
            font=('Segoe UI', 11, 'bold'),
            bg='#ffb300',
            fg='white',
            activebackground='#ffd54f',
            activeforeground='#ff6f00',
            relief='groove',
            borderwidth=0,
            padx=12,
            pady=7,
            command=self.reset_puzzle,
            cursor='hand2',
            highlightthickness=0
        )
        reset_btn.grid(row=3, column=0, columnspan=3, pady=(24, 8))
        add_tooltip(reset_btn, "Đặt lại trạng thái ban đầu")

        # Thanh trạng thái (task bar) bên dưới nút reset
        self.status_bar = tk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 11, "bold"),
            fg="#37474f",
            bg="#e3f2fd",
            anchor='center',
            relief='sunken',
            bd=1,
            height=2
        )
        self.status_bar.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(0, 0))

        # Nhãn hiển thị thông tin
        self.info_label = ttk.Label(main_frame, text="", font=('Segoe UI', 11), foreground='#1976d2', anchor='center', background='#f4f8fb')
        self.info_label.grid(row=5, column=0, columnspan=3, pady=(10, 0), sticky='ew')
        
        # Cấu hình grid cho co giãn (không cho các panel nở ra)
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=0)
        main_frame.rowconfigure(1, weight=0)

    def create_board(self, parent):
        self.board_frame = ttk.Frame(parent, padding="10", width=320, height=320)
        self.board_frame.grid(row=0, column=0)
        self.board_frame.grid_propagate(False)

        self.tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                val = self.initial_state[i][j]
                label = tk.Label(
                    self.board_frame,
                    text=str(val) if val != 0 else "",
                    font=("Helvetica", 32, "bold"),
                    width=4,
                    height=2,
                    bg="#ffffff" if val != 0 else "#f5f5f5",
                    fg="#37474f",
                    relief="raised",
                    borderwidth=2
                )
                label.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                row.append(label)
            self.tiles.append(row)

        # Cho phép co giãn
        for i in range(3):
            self.board_frame.rowconfigure(i, weight=1)
            self.board_frame.columnconfigure(i, weight=1)
        # Thêm nhãn hiển thị hướng di chuyển bên dưới bảng
        self.move_label = tk.Label(self.board_frame, text="", font=("Segoe UI", 14, "bold"), fg="#1976d2", bg="#e3f2fd")
        self.move_label.grid(row=3, column=0, columnspan=3, pady=(10, 0))

    def update_move_history_display(self, current_step=None):
        for lbl in getattr(self, 'move_history_labels', []):
            lbl.destroy()
        self.move_history_labels = []

        if not hasattr(self, 'move_history') or not self.move_history:
            self.move_history_canvas.configure(scrollregion=self.move_history_canvas.bbox('all'))
            return

        for idx, arrow in enumerate(self.move_history):
            # Tạo frame cho mỗi bước để chứa cả mũi tên và số step
            step_frame = tk.Frame(self.move_history_inner, bg='#f4f8fb')
            if current_step is not None and idx == current_step:
                border_color = '#388e3c'
                fg_color = '#388e3c'
                bg_color = '#e8f5e9'
            else:
                border_color = '#d32f2f'
                fg_color = '#d32f2f'
                bg_color = '#fff'
            lbl = tk.Label(step_frame, text=arrow, font=("Segoe UI", 15, "bold"),
                        fg=fg_color, bg=bg_color, width=2, height=1, relief='solid', bd=1, padx=4, pady=0)
            lbl.pack(side='top', padx=2, pady=(0,0))
            lbl.config(highlightbackground=border_color, highlightcolor=border_color, highlightthickness=2)
            lbl.pack_propagate(False)
            # Thêm số step bên dưới
            step_num = tk.Label(step_frame, text=str(idx+1), font=("Segoe UI", 10, "bold"), fg='#616161', bg='#f4f8fb')
            step_num.pack(side='top', pady=(0,2))
            step_frame.pack(side='left', padx=4, pady=4)
            self.move_history_labels.append(step_frame)

        # Cập nhật kích thước scroll
        self.move_history_inner.update_idletasks()
        self.move_history_canvas.update_idletasks()
        self.move_history_canvas.configure(scrollregion=self.move_history_canvas.bbox('all'))

        # Focus vào bước hiện tại (bước mới nhất hoặc current_step)
        if self.move_history_labels:
            focus_idx = current_step if (current_step is not None and 0 <= current_step < len(self.move_history_labels)) else len(self.move_history_labels)-1
            try:
                frame = self.move_history_labels[focus_idx]
                self.move_history_canvas.update_idletasks()
                # Lấy bbox của frame trong canvas (tọa độ tuyệt đối)
                bbox = self.move_history_canvas.bbox(self.move_history_window)
                frame_bbox = frame.winfo_x(), frame.winfo_y(), frame.winfo_x() + frame.winfo_width(), frame.winfo_y() + frame.winfo_height()
                if bbox and frame_bbox:
                    x1, y1, x2, y2 = frame_bbox
                    canvas_width = self.move_history_canvas.winfo_width()
                    # Tính tỉ lệ vị trí phải scroll để frame focus nằm sát mép phải
                    scroll_to = max(0, (x2 - canvas_width) / max(1, self.move_history_inner.winfo_width()))
                    self.move_history_canvas.xview_moveto(scroll_to)
            except Exception as e:
                print("Scroll error:", e)

    def update_board(self, state, move=None, step=None):
        """
        Cập nhật bảng trạng thái. Nếu move được cung cấp, sẽ highlight các ô liên quan và hiển thị hướng di chuyển bên dưới.
        move: tuple (direction, from_pos, to_pos) hoặc chỉ direction (L/R/U/D)
        """
        highlight_from = highlight_to = None
        direction = None
        if isinstance(move, tuple) and len(move) == 3:
            direction, highlight_from, highlight_to = move
        elif isinstance(move, str):
            direction = move
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                label = self.tiles[i][j]
                bg = "#ffffff" if val != 0 else "#f5f5f5"
                if highlight_from == (i, j):
                    bg = "#fff59d"
                if highlight_to == (i, j):
                    bg = "#81d4fa"
                label.config(
                    text=str(val) if val != 0 else "",
                    bg=bg,
                    fg="#37474f"
                )
        # Hiển thị hướng di chuyển bên dưới bảng với mũi tên, các trạng thái di chuyển sẽ được nối dài ra (không mất đi bước trước)
        if not hasattr(self, 'move_history'):
            self.move_history = []
        arrow = ''
        if isinstance(move, tuple) and len(move) == 3:
            direction = move[0]
        elif isinstance(move, str):
            direction = move
        else:
            direction = None
        if direction == 'L':
            arrow = '←'
        elif direction == 'R':
            arrow = '→'
        elif direction == 'U':
            arrow = '↑'
        elif direction == 'D':
            arrow = '↓'
        if direction:
            idx = self.step-1 if step is None else step
            if idx >= 0 and len(self.move_history) <= idx:
                self.move_history.append(arrow)
        # Hiển thị toàn bộ lịch sử di chuyển với highlight
        if hasattr(self, 'move_history_frame'):
            idx = self.step-1 if step is None else step
            self.update_move_history_display(current_step=idx)
        # Hiển thị hướng di chuyển hiện tại (chỉ 1 mũi tên)
        if hasattr(self, 'move_label'):
            self.move_label.config(text=arrow if direction else "")

    def animate_solution(self):
        """Animation lời giải"""
        if self.step < self.total_steps and not self.stop_flag:
            # Cập nhật trạng thái
            self.current_state = self.solution[self.step+1]  # +1 vì bước 0 là initial
            # Tìm hướng di chuyển
            move = None
            if self.step >= 0:
                prev = self.solution[self.step]
                curr = self.current_state
                move, from_pos, to_pos = self.get_move_direction(prev, curr)
                self.step += 1
                self.update_board(curr, move=(move, from_pos, to_pos), step=self.step-1)
            # Cập nhật thời gian
            if self.animation_start_time:
                self.animation_elapsed_time = time.time() - self.animation_start_time
            # Hiển thị số bước và thời gian animation ở status bar
            self.status_bar.config(
                text=f"Step: {self.step}/{self.total_steps}   |   Animation: {self.animation_elapsed_time:.2f}s"
            )
            self.info_label.configure(
                text=f"Algorithm: {self.current_algorithm}\n"
                     f"Step: {self.step}/{self.total_steps}\n"
                     f"Execution time: {self.execution_time:.5f}s\n"
                     f"Animation time: {self.animation_elapsed_time:.2f}s"
            )            # Tiếp tục animation với delay phụ thuộc vào tốc độ
            base_delay = 800  # Delay cơ bản ở speed = 1
            if self.animation_speed_factor <= 1:
                delay = base_delay
            else:
                # Sử dụng hàm mũ để giảm delay nhanh hơn khi speed tăng
                delay = int(base_delay / (self.animation_speed_factor ** 2))
            if delay < 10:  # Giảm giới hạn tối thiểu xuống 10ms để cho phép tốc độ cao hơn
                delay = 10
            self.root.after(delay, self.animate_solution)
        else:
            self.complete_animation()

    def complete_animation(self):
        """Hoàn thành animation"""
        self.is_animating = False
        self.stop_flag = True
        self.info_label.configure(
            text=f"{self.current_algorithm} completed\n"
                 f"Execution time: {self.execution_time:.5f}s\n"
                 f"Total animation time: {self.animation_elapsed_time:.2f}s"
        )

    def cancel_action(self):
        """Xử lý khi nhấn nút Cancel"""
        if not self.is_animating:
            messagebox.showinfo("Thông báo", "Không có animation đang chạy!")
            return
            
        self.stop_flag = True
        self.is_animating = False
        
        if self.solution and self.step > 0:
            self.current_state = self.solution[0]
            self.update_board(self.current_state)
            self.step = 0
            
            self.info_label.configure(
                text=f"Algorithm: {self.current_algorithm}\n"
                     f"Total steps: {self.total_steps}\n"
                     f"Animation cancelled. Press Start to try again."
            )
        else:
            self.info_label.configure(text="Operation cancelled")

    def show_history(self):
        # Tạo cửa sổ mới cho lịch sử
        history_window = tk.Toplevel(self.root)
        history_window.title("Algorithm History")
        history_window.geometry("600x400")
        
        # Tạo frame chính
        main_frame = ttk.Frame(history_window, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Tiêu đề
        title_label = ttk.Label(
            main_frame,
            text="Lịch sử chạy thuật toán",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Tạo Treeview để hiển thị lịch sử
        columns = ('timestamp', 'algorithm', 'steps', 'time')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
        # Định nghĩa các cột
        tree.heading('timestamp', text='Thời gian')
        tree.heading('algorithm', text='Thuật toán')
        tree.heading('steps', text='Số bước')
        tree.heading('time', text='Thời gian chạy (s)')
        
        # Định nghĩa độ rộng cột
        tree.column('timestamp', width=150)
        tree.column('algorithm', width=150)
        tree.column('steps', width=100)
        tree.column('time', width=150)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí các widget
        tree.grid(row=1, column=0, sticky='nsew')
        scrollbar.grid(row=1, column=1, sticky='ns')
          # Thêm dữ liệu vào Treeview
        for entry in reversed(self.algorithm_history):  # Hiển thị mới nhất lên đầu
            tree.insert('', 'end', values=(
                entry['timestamp'],
                entry['algorithm'],
                entry['steps'],
                f"{entry['time']:.5f}"
            ))
        
        # Frame chứa nút
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        # Nút xóa lịch sử
        def clear_history():
            self.algorithm_history.clear()
            for item in tree.get_children():
                tree.delete(item)
        
        clear_button = tk.Button(
            button_frame,
            text="Xóa lịch sử",
            font=('Arial', 11, 'bold'),
            bg='#ffcdd2',  # Đỏ nhạt
            fg='#b71c1c',  # Đỏ đậm
            activebackground='#ef9a9a',
            activeforeground='#b71c1c',
            relief='raised',
            borderwidth=2,
            padx=20,
            pady=8,
            command=clear_history
        )
        clear_button.pack(side='left', padx=10)
        
        # Nút đóng
        close_button = tk.Button(
            button_frame,
            text="Đóng",
            font=('Arial', 11, 'bold'),
            bg='#bbdefb',  # Xanh dương nhạt
            fg='#0d47a1',  # Xanh dương đậm
            activebackground='#64b5f6',
            activeforeground='#0d47a1',
            relief='raised',
            borderwidth=2,
            padx=20,
            pady=8,
            command=history_window.destroy
        )
        close_button.pack(side='left', padx=10)
        
        # Cấu hình grid cho co giãn
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Căn giữa cửa sổ
        history_window.update_idletasks()
        width = history_window.winfo_width()
        height = history_window.winfo_height()
        x = (history_window.winfo_screenwidth() // 2) - (width // 2)
        y = (history_window.winfo_screenheight() // 2) - (height // 2)
        history_window.geometry(f'{width}x{height}+{x}+{y}')

    def input_action(self):
        """Xử lý khi nhấn nút Input"""
        # Tạo cửa sổ mới
        input_window = tk.Toplevel(self.root)
        input_window.title("Nhập trạng thái Puzzle")
        input_window.geometry("400x500")
        input_window.resizable(False, False)
        
        # Tạo frame chính với padding
        main_frame = ttk.Frame(input_window, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Tiêu đề
        title_label = ttk.Label(
            main_frame,
            text="Nhập trạng thái Puzzle 3x3",
            font=('Arial', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Hướng dẫn
        instruction_text = (
            "Hướng dẫn:\n"
            "• Nhập các số từ 0-8 vào ma trận\n"
            "• Số 0 đại diện cho ô trống\n"
            "• Mỗi số chỉ được xuất hiện một lần"
        )
        instruction_label = ttk.Label(
            main_frame,
            text=instruction_text,
            font=('Arial', 10),
            justify='left',
            wraplength=350
        )
        instruction_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Frame chứa ma trận nhập liệu
        matrix_frame = ttk.Frame(main_frame)
        matrix_frame.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # Tạo các ô nhập liệu với style đẹp hơn
        entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                # Frame chứa ô nhập liệu
                cell_frame = ttk.Frame(matrix_frame, padding="2")
                cell_frame.grid(row=i, column=j, padx=2, pady=2)
                
                # Ô nhập liệu
                entry = tk.Entry(
                    cell_frame,
                    width=4,
                    justify='center',
                    font=('Arial', 16, 'bold'),
                    relief='solid',
                    borderwidth=2
                )
                entry.pack(fill='both', expand=True)
                
                # Thêm validation
                def validate_input(P):
                    if P == "": return True
                    try:
                        num = int(P)
                        return 0 <= num <= 8
                    except ValueError:
                        return False
                
                vcmd = (input_window.register(validate_input), '%P')
                entry.config(validate='key', validatecommand=vcmd)
                
                row_entries.append(entry)
            entries.append(row_entries)
        
        # Frame chứa nút
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 20))
        
        def validate_and_save():
            try:
                # Lấy giá trị từ các ô nhập liệu
                matrix = []
                for row in entries:
                    row_values = []
                    for cell in row:
                        value = cell.get()
                        if not value:  # Kiểm tra ô trống
                            raise ValueError("Vui lòng điền đầy đủ tất cả các ô!")
                        row_values.append(int(value))
                    matrix.append(row_values)
                
                # Kiểm tra tính hợp lệ của ma trận
                numbers = [x for row in matrix for x in row]
                if sorted(numbers) != list(range(9)):
                    raise ValueError("Ma trận phải chứa các số từ 0-8, mỗi số xuất hiện đúng một lần")
                
                # Cập nhật trạng thái puzzle
                self.current_state = matrix
                self.update_board(self.current_state)
                
                # Reset các biến liên quan
                self.reset_algorithm_state()
                
                # Hiển thị thông báo thành công
                self.info_label.configure(text="Trạng thái puzzle đã được cập nhật!")
                input_window.destroy()
                
            except ValueError as e:
                messagebox.showerror("Lỗi", str(e))
            except Exception as e:
                messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên trong tất cả các ô!")
        
        # Nút OK
        ok_button = tk.Button(
            button_frame,
            text="Lưu",
            font=('Arial', 11, 'bold'),
            bg='#4caf50',  # Xanh lá
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief='raised',
            borderwidth=2,
            padx=20,
            pady=8,
            command=validate_and_save
        )
        ok_button.pack(side='left', padx=10)
        
        # Nút Cancel
        cancel_button = tk.Button(
            button_frame,
            text="Hủy",
            font=('Arial', 11, 'bold'),
            bg='#f44336',  # Đỏ
            fg='white',
            activebackground='#da190b',
            activeforeground='white',
            relief='raised',
            borderwidth=2,
            padx=20,
            pady=8,
            command=input_window.destroy
        )
        cancel_button.pack(side='left', padx=10)
        
        # Căn giữa cửa sổ
        input_window.update_idletasks()
        width = input_window.winfo_width()
        height = input_window.winfo_height()
        x = (input_window.winfo_screenwidth() // 2) - (width // 2)
        y = (input_window.winfo_screenheight() // 2) - (height // 2)
        input_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Đặt focus vào ô đầu tiên
        entries[0][0].focus()
        
        # Thêm phím tắt
        input_window.bind('<Return>', lambda e: validate_and_save())
        input_window.bind('<Escape>', lambda e: input_window.destroy())

    def reset_puzzle(self):
        """Reset trạng thái puzzle về ban đầu"""
        # Đặt lại trạng thái trò chơi
        self.current_state = [row[:] for row in self.initial_state]
        self.update_board(self.current_state)
        
        # Reset tất cả trạng thái
        self.reset_algorithm_state()
        
        # Reset màu của tất cả các nút nhóm thuật toán
        for btn in self.group_buttons.values():
            btn.configure(
                bg='#e1f5fe',
                fg='#0277bd'
            )
        
        # Reset màu của tất cả các nút thuật toán
        for btn in self.algorithm_buttons.values():
            btn.configure(
                bg='#d0f0c0',
                fg='#33691e'
            )
        
        # Reset move history
        self.move_history = []
        if hasattr(self, 'move_label'):
            self.move_label.config(text="")
        if hasattr(self, 'move_history_frame'):
            self.update_move_history_display(current_step=None)
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text="")
        
        # Cập nhật thông tin
        self.info_label.configure(text="Reset completed. Please select an algorithm.")

    def handle_successful_solution(self, algo_name):
        """Xử lý khi tìm thấy lời giải"""
        self.current_algorithm = algo_name
        self.total_steps = len(self.solution) - 1 if self.solution else 0
        # Thêm vào lịch sử
        history_entry = {
            'algorithm': algo_name,
            'steps': self.total_steps,
            'time': self.execution_time,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'initial_state': [row[:] for row in self.current_state]
        }
        self.algorithm_history.append(history_entry)
        # Cập nhật thông tin
        self.info_label.configure(
            text=f"Algorithm: {algo_name}\n"
                 f"Total steps: {self.total_steps}\n"
                 f"Time to find solution: {self.execution_time:.5f}s\n"
                 f"Press Start to begin animation"
        )

    def handle_failed_solution(self, algo_name):
        """Xử lý khi không tìm thấy lời giải"""
        self.info_label.configure(text=f"{algo_name}: No solution found!")

    def handle_algorithm_error(self, algo_name, error_msg):
        """Xử lý lỗi thuật toán"""
        self.info_label.configure(text=f"Error in {algo_name}: {error_msg}")

    def open_partial_observation_window(self):
        """Mở cửa sổ mới cho Partial Observation solver"""
        partial_obs_window = PartialObsVisualizerWindow(self.root)
        # Chỉnh initial state cho partial observe
        partial_obs_window.initial_state = [
            [1, 0, 3],
            [2, 5, 6],
            [7, 4, 8]
        ]
        partial_obs_window.goal_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 0]
        ]
        obs = partial_obs_window.get_observation(partial_obs_window.initial_state)
        partial_obs_window.update_board(partial_obs_window.observation_board, obs, True)
        partial_obs_window.run_search()
    def open_no_observation_window(self):
        """Open new window for No-Observation solver visualization"""
        from algorithms.no_observation import no_observation_search
        from ui.no_observation_visualizer import NoObservationVisualizerWindow
        initial_belief = [
            [[1,2,3],[4,5,6],[0,7,8]],
            [[1,2,3],[4,5,6],[7,0,8]]   
        ]
        goal_state = [row[:] for row in self.goal_state]
        import time
        start_time = time.time()
        solution, trace = no_observation_search(initial_belief, goal_state, max_steps=20)
        exec_time = time.time() - start_time
        visualizer = NoObservationVisualizerWindow(self.root, trace, solution, initial_belief=initial_belief, goal_state=goal_state)
        visualizer.exec_time = exec_time
    

    def open_andor_tree_window(self):
        """Open visualization window for AND-OR Tree"""
        from .andor_tree_visualizer import AndOrTreeVisualizer, build_andor_tree
        from algorithms.complex_search import and_or_search
        # Lấy trạng thái hiện tại và goal
        initial_state = [[1, 2, 3],
        [4, 5, 6],
        [7, 0, 8]]
        goal_state = self.goal_state
        # Gọi thuật toán and_or_search để lấy solution_path và tree_data
        result = and_or_search(initial_state, goal_state)
        if isinstance(result, tuple) and len(result) == 5:
            solution_path, nodes_explored, steps, exec_time, tree_data = result
        elif isinstance(result, tuple) and len(result) == 2:
            solution_path, tree_data = result
            nodes_explored = steps = exec_time = None
        else:
            solution_path = result
            tree_data = {'steps': []}
            nodes_explored = steps = exec_time = None
        # Luôn vẽ cây từ kết quả thật của bài toán 8-puzzle, truyền đủ initial_state và goal_state
        tree_root = build_andor_tree(initial_state, goal_state, steps=tree_data.get('steps'))
        AndOrTreeVisualizer(self.root, tree_root)

    def start_action(self):
        """Xử lý khi nhấn nút Start"""
        if not self.solution:
            tk.messagebox.showinfo("Thông báo", "Vui lòng chọn thuật toán trước!")
            return
        if self.is_animating:
            tk.messagebox.showinfo("Thông báo", "Animation đang chạy!")
            return
        if self.stop_flag:
            self.step = 0
            self.stop_flag = False
        self.animation_start_time = time.time()
        self.is_animating = True
        self.animate_solution()
    
    def show_algorithms(self, group_name):
        """Hiển thị các thuật toán thuộc nhóm được chọn và cập nhật giao diện nút nhóm"""
        # Reset màu của tất cả các nút nhóm
        for btn in self.group_buttons.values():
            btn.configure(
                bg='#e1f5fe',
                fg='#0277bd'
            )
        # Đổi màu nút được chọn
        self.group_buttons[group_name].configure(
            bg='#0288d1',  # Xanh dương đậm khi chọn
            fg='white'     # Chữ trắng khi chọn
        )
        # Xóa các nút thuật toán cũ
        for btn in self.algorithm_buttons.values():
            btn.destroy()
        self.algorithm_buttons.clear()
        # Tạo các nút thuật toán mới
        for i, (algo_name, algo_func) in enumerate(self.algorithm_groups[group_name].items()):
            btn = tk.Button(
                self.algorithms_frame,
                text=algo_name,
                font=('Segoe UI', 11),
                bg='#d0f0c0',  # Xanh mint
                fg='#33691e',  # Xanh lá đậm
                activebackground='#aed581',  # Xanh lá nhạt khi hover
                activeforeground='#33691e',  # Giữ màu chữ khi hover
                relief='raised',
                borderwidth=2,
                padx=8,
                pady=5,
                width=20,  # Cố định chiều rộng
                command=lambda a=algo_name, f=algo_func: self.run_algorithm(a, f)
            )
            btn.grid(row=i, column=0, pady=5, sticky="ew")
            self.algorithm_buttons[algo_name] = btn
        self.current_group = group_name

    def run_algorithm(self, algo_name, algo_func):
        """Chạy thuật toán được chọn và cập nhật trạng thái UI, animation"""
        # Kiểm tra trạng thái hiện tại
        if self.is_animating:
            tk.messagebox.showwarning("Cảnh báo", "Vui lòng đợi animation hiện tại kết thúc!")
            return
        # Xử lý đặc biệt cho các thuật toán có giao diện riêng
        if algo_name == 'Partial Observed':
            self.open_partial_observation_window()
            return
        elif algo_name == 'Non Observed':
            self.open_no_observation_window()
            return
        elif algo_name == 'Backtracking':
            self.reset_algorithm_state()
            self.update_algorithm_buttons(algo_name)
            self.info_label.configure(text=f"Đang chạy {algo_name}...")
            self.root.update_idletasks()
            start_time = time.time()
            try:
                from algorithms.constraint_search import backtracking_solve_with_constraints
                self.solution = backtracking_solve_with_constraints(self.current_state, self.goal_state)
                self.execution_time = time.time() - start_time
                if self.solution:
                    self.handle_successful_solution(algo_name)
                else:
                    self.handle_failed_solution(algo_name)
            except Exception as e:
                self.handle_algorithm_error(algo_name, str(e))
            return
        elif algo_name == 'Forward Checking':
            self.reset_algorithm_state()
            self.update_algorithm_buttons(algo_name)
            self.info_label.configure(text=f"Đang chạy {algo_name}...")
            self.root.update_idletasks()
            start_time = time.time()
            try:
                from algorithms.constraint_search import forward_checking
                self.solution = forward_checking(self.current_state, self.goal_state)
                self.execution_time = time.time() - start_time
                if self.solution:
                    self.handle_successful_solution(algo_name)
                else:
                    self.handle_failed_solution(algo_name)
            except Exception as e:
                self.handle_algorithm_error(algo_name, str(e))
            return
        elif algo_name == 'And-Or':
            self.open_andor_tree_window()
            return
        # Reset các trạng thái
        self.reset_algorithm_state()
        # Cập nhật UI
        self.update_algorithm_buttons(algo_name)
        self.info_label.configure(text=f"Đang chạy {algo_name}...")
        self.root.update_idletasks()
        # Bắt đầu tính thời gian
        start_time = time.time()
        try:
            # Chạy thuật toán
            result = algo_func(self.current_state, self.goal_state)
            # Kiểm tra nếu kết quả là tuple (như Q-Learning)
            if isinstance(result, tuple) and len(result) == 2:
                self.solution = result[0] # Gán solution path cho self.solution
                self.episodes_run = result[1] # Lưu số episode
            else:
                self.solution = result # Gán kết quả trực tiếp nếu không phải tuple
                self.episodes_run = None # Đảm bảo episodes_run là None cho các thuật toán khác
            # Tính thời gian thực thi
            self.execution_time = time.time() - start_time
            if self.solution:
                self.handle_successful_solution(algo_name)
            else:
                self.handle_failed_solution(algo_name)
        except Exception as e:
            self.handle_algorithm_error(algo_name, str(e))

    def reset_algorithm_state(self):
        """Reset tất cả trạng thái liên quan đến thuật toán"""
        self.solution = None
        self.step = 0
        self.total_steps = 0
        self.stop_flag = False
        self.execution_time = 0
        self.animation_start_time = None
        self.animation_elapsed_time = 0
        self.episodes_run = None # Khởi tạo episodes_run

    def update_algorithm_buttons(self, selected_algo):
        """Cập nhật trạng thái các nút thuật toán"""
        for btn in self.algorithm_buttons.values():
            btn.configure(
                bg='#d0f0c0',
                fg='#33691e'
            )
        if selected_algo in self.algorithm_buttons:
            self.algorithm_buttons[selected_algo].configure(
                bg='#558b2f',
                fg='white'
            )

    def get_move_direction(self, prev, curr):
        """Trả về (L/R/U/D, from_pos, to_pos) cho bước di chuyển từ prev -> curr"""
        # Tìm vị trí 0 trong prev và curr
        for i in range(3):
            for j in range(3):
                if prev[i][j] == 0:
                    prev_zero = (i, j)
                if curr[i][j] == 0:
                    curr_zero = (i, j)
        # Tìm vị trí số bị di chuyển
        di = curr_zero[0] - prev_zero[0]
        dj = curr_zero[1] - prev_zero[1]
        if di == 1:
            return 'D', (curr_zero[0], curr_zero[1]), (prev_zero[0], prev_zero[1])  # 0 đi xuống, số lên trên
        if di == -1:
            return 'U', (curr_zero[0], curr_zero[1]), (prev_zero[0], prev_zero[1])
        if dj == 1:
            return 'R', (curr_zero[0], curr_zero[1]), (prev_zero[0], prev_zero[1])
        if dj == -1:
            return 'L', (curr_zero[0], curr_zero[1]), (prev_zero[0], prev_zero[1])
        return '', (curr_zero[0], curr_zero[1]), (prev_zero[0], prev_zero[1])
