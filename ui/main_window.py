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
        self.root.configure(bg='#fafafa')
        
        # Style cho LabelFrame
        style.configure('My.TLabelframe', background='#eeeeee')
        style.configure('My.TLabelframe.Label', 
            font=('Arial', 11, 'bold'), 
            foreground='#424242', 
            background='#eeeeee'
        )
        
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="8-Puzzle Solver", font=('Arial', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Khung chứa nhóm thuật toán (trái)
        groups_frame = ttk.LabelFrame(main_frame, text="Algorithm Groups", padding="10", style='My.TLabelframe')
        groups_frame.grid(row=1, column=0, padx=(0, 10), sticky="nsew")
        
        # Khung chứa thuật toán (giữa)
        self.algorithms_frame = ttk.LabelFrame(main_frame, text="Algorithms", padding="10", style='My.TLabelframe')
        self.algorithms_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Khung chứa bảng trạng thái (phải)
        board_frame = ttk.LabelFrame(main_frame, text="Puzzle State", padding="10", style='My.TLabelframe')
        board_frame.grid(row=1, column=2, sticky="nsew")
        
        # Frame chứa các nút chức năng
        functions_frame = tk.Frame(main_frame, bg='#ffffff', padx=10, pady=10)
        functions_frame.grid(row=2, column=1, sticky='ew', pady=(0, 10))
        
        # Nút Start
        start_button = tk.Button(
            functions_frame, text="Start", font=('Arial', 11, 'bold'),
            bg='#c8e6c9', fg='#1b5e20',
            activebackground='#81c784', activeforeground='#1b5e20',
            relief='raised', borderwidth=2, padx=15, pady=5,
            command=self.start_action
        )
        start_button.pack(side='left', padx=10)
        
        # Nút Input
        input_button = tk.Button(
            functions_frame, text="Input", font=('Arial', 11, 'bold'),
            bg='#bbdefb', fg='#0d47a1',
            activebackground='#64b5f6', activeforeground='#0d47a1',
            relief='raised', borderwidth=2, padx=15, pady=5,
            command=self.input_action
        )
        input_button.pack(side='left', padx=10)
        
        # Nút Cancel
        cancel_button = tk.Button(
            functions_frame, text="Cancel", font=('Arial', 11, 'bold'),
            bg='#ffcdd2', fg='#b71c1c',
            activebackground='#ef9a9a', activeforeground='#b71c1c',
            relief='raised', borderwidth=2, padx=15, pady=5,
            command=self.cancel_action
        )
        cancel_button.pack(side='left', padx=10)
        
        # Nút History
        history_button = tk.Button(
            functions_frame, text="History", font=('Arial', 11, 'bold'),
            bg='#e1bee7', fg='#4a148c',
            activebackground='#ce93d8', activeforeground='#4a148c',
            relief='raised', borderwidth=2, padx=15, pady=5,
            command=self.show_history
        )
        history_button.pack(side='left', padx=10)
        
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
                font=('Arial', 12, 'bold'),
                bg='#e1f5fe',  # Xanh dương rất nhạt
                fg='#0277bd',  # Xanh dương đậm
                activebackground='#81d4fa',  # Xanh dương nhạt khi hover
                activeforeground='#0277bd',  # Giữ màu chữ khi hover
                relief='raised',
                borderwidth=2,
                padx=10,
                pady=5,
                width=20,  # Cố định chiều rộng
                command=lambda g=group_name: self.show_algorithms(g)
            )
            btn.grid(row=i, column=0, pady=5, sticky="ew")
            self.group_buttons[group_name] = btn
        
        # Tạo bảng trạng thái puzzle
        self.create_board(board_frame)
        
        # Nút reset
        reset_btn = tk.Button(
            main_frame,
            text="Reset",
            font=('Arial', 11, 'bold'),
            bg='#ffccbc',  # Đỏ cam nhạt
            fg='#d84315',  # Cam đậm
            activebackground='#ffab91',  # Đỏ cam nhạt khi hover
            activeforeground='#bf360c',  # Cam đậm khi hover
            relief='raised',
            borderwidth=2,
            padx=8,
            pady=5,
            command=self.reset_puzzle
        )
        reset_btn.grid(row=4, column=0, columnspan=3, pady=(20, 5))
        
        # Nhãn hiển thị thông tin
        self.info_label = ttk.Label(main_frame, text="", font=('Arial', 11))
        self.info_label.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        # Cấu hình grid cho co giãn
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=2)
        main_frame.rowconfigure(1, weight=1)

    def create_board(self, parent):
        self.board_frame = ttk.Frame(parent, padding="10")
        self.board_frame.grid(row=0, column=0)

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
                    height=2,  # Cố định chiều cao
                    bg="#ffffff" if val != 0 else "#f5f5f5",  # Trắng cho số, xám nhạt cho ô trống
                    fg="#37474f",  # Xám đậm cho chữ
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

    def update_board(self, state):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                label = self.tiles[i][j]
                label.config(
                    text=str(val) if val != 0 else "",
                    bg="#ffffff" if val != 0 else "#f5f5f5",  # Trắng cho số, xám nhạt cho ô trống
                    fg="#37474f"  # Xám đậm cho chữ
                )

    def show_algorithms(self, group_name):
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
                font=('Arial', 11),
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
        # Kiểm tra trạng thái hiện tại
        if self.is_animating:
            messagebox.showwarning("Cảnh báo", "Vui lòng đợi animation hiện tại kết thúc!")
            return
        # Xử lý đặc biệt cho các thuật toán có giao diện riêng
        if algo_name == 'Partial Observed':
            self.open_partial_observation_window()
            return
        elif algo_name == 'Non Observed':
            self.open_no_observation_window()
            return
        elif algo_name == 'Backtracking':
            # Reset các trạng thái
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
            # Reset các trạng thái
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
            self.solution = algo_func(self.current_state, self.goal_state)
            
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

    def update_algorithm_buttons(self, selected_algo):
        """Cập nhật trạng thái các nút thuật toán"""
        for btn in self.algorithm_buttons.values():
            btn.configure(
                bg='#d0f0c0',
                fg='#33691e'
            )
        
        self.algorithm_buttons[selected_algo].configure(
            bg='#558b2f',
            fg='white'
        )

    def start_action(self):
        """Xử lý khi nhấn nút Start"""
        if not self.solution:
            messagebox.showinfo("Thông báo", "Vui lòng chọn thuật toán trước!")
            return
            
        if self.is_animating:
            messagebox.showinfo("Thông báo", "Animation đang chạy!")
            return
            
        if self.stop_flag:
            self.step = 0
            self.stop_flag = False
            
        self.animation_start_time = time.time()
        self.is_animating = True
        self.animate_solution()

    def animate_solution(self):
        """Animation lời giải"""
        if self.step < self.total_steps and not self.stop_flag:
            # Cập nhật trạng thái
            self.current_state = self.solution[self.step]
            self.update_board(self.current_state)
            self.step += 1
            
            # Cập nhật thời gian
            if self.animation_start_time:
                self.animation_elapsed_time = time.time() - self.animation_start_time
            
            # Cập nhật thông tin
            self.info_label.configure(
                text=f"Algorithm: {self.current_algorithm}\n"
                     f"Step: {self.step}/{self.total_steps}\n"
                     f"Execution time: {self.execution_time:.2f}s\n"
                     f"Animation time: {self.animation_elapsed_time:.2f}s"
            )

            # Tiếp tục animation
            self.root.after(800, self.animate_solution)
        else:
            self.complete_animation()

    def complete_animation(self):
        """Hoàn thành animation"""
        self.is_animating = False
        self.stop_flag = True
        self.info_label.configure(
            text=f"{self.current_algorithm} completed\n"
                 f"Execution time: {self.execution_time:.2f}s\n"
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
                f"{entry['time']:.2f}"
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
        
        # Cập nhật thông tin
        self.info_label.configure(text="Reset completed. Please select an algorithm.")

    def handle_successful_solution(self, algo_name):
        """Xử lý khi tìm thấy lời giải"""
        self.current_algorithm = algo_name
        self.total_steps = len(self.solution)
        
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
                 f"Time to find solution: {self.execution_time:.2f}s\n"
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
        initial_state = self.current_state
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
