# 8-Puzzle Solver

A Python application implementing various search algorithms to solve the classic 8-puzzle problem, featuring a modern graphical user interface and interactive visualizations.

## Overview

This application provides an interactive way to solve 8-puzzle problems using multiple search algorithms. It includes both informed and uninformed search strategies, along with local search techniques and reinforcement learning approaches.

## Features

### Search Algorithms
- **Uninformed Search**
  - Breadth-First Search (BFS)
  - Depth-First Search (DFS)
  - Uniform Cost Search (UCS)
  - Iterative Deepening DFS (IDDFS)

- **Informed Search**
  - Greedy Best-First Search
  - A* Search
  - IDA* Search

- **Local Search**
  - Hill Climbing (Simple)
  - Hill Climbing (Steepest Ascent)
  - Stochastic Hill Climbing
  - Simulated Annealing
  - Genetic Algorithm
  - Beam Search

- **Advanced Techniques**
  - AND-OR Search
  - Constraint Satisfaction
  - Reinforcement Learning (Q-Learning, TD Learning)

### Interface Features
- Interactive GUI with puzzle board visualization
- Real-time solution animation
- Custom puzzle state input
- Algorithm performance history
- Step-by-step execution
- Solution path visualization

## Requirements

- Python 3.x
- tkinter (included in Python standard library)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 8-puzzle-solver
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Using the Application

1. **Start Screen**
   - The application opens with a default 8-puzzle configuration
   - The interface shows algorithm groups on the left and the puzzle board on the right

2. **Solving a Puzzle**
   - Select an algorithm group from the left panel
   - Choose a specific algorithm
   - Click "Start" to begin the solution animation
   - Use "Cancel" to stop the current execution

3. **Custom Input**
   - Click "Input" to enter your own puzzle configuration
   - Enter numbers 0-8 (0 represents the empty space)
   - The system validates the input for solvability

4. **History and Analysis**
   - View solution history with the "History" button
   - Compare algorithm performance metrics
   - Track execution time and number of moves

## Project Structure

```
project/
├── algorithms/        # Search algorithm implementations
│   ├── __init__.py
│   └── solvers.py
├── models/           # Data structures and state representations
│   ├── __init__.py
│   └── puzzle_state.py
├── ui/              # User interface components
│   ├── __init__.py
│   └── main_window.py
├── utils/           # Helper functions and utilities
│   ├── __init__.py
│   └── validators.py
├── __init__.py
├── main.py          # Application entry point
├── README.md
└── requirements.txt
```

## Project Report

### 1. Mục tiêu

Xây dựng một ứng dụng trực quan hóa và so sánh các thuật toán giải bài toán 8-puzzle (8 ô chữ), bao gồm các thuật toán tìm kiếm không có thông tin, có thông tin, tìm kiếm trong môi trường phức tạp (AND-OR, partial observation, no-observation), tìm kiếm ràng buộc, và học tăng cường. Ứng dụng hỗ trợ nhập trạng thái, quan sát từng bước giải, so sánh hiệu suất và trực quan hóa cây tìm kiếm.

### 2. Nội dung

#### 2.1. Các thuật toán Tìm kiếm không có thông tin

- **Các thành phần chính của bài toán tìm kiếm:**
  - Trạng thái (State): Ma trận 3x3 biểu diễn vị trí các ô số và ô trống.
  - Hành động (Action): Di chuyển ô trống lên/xuống/trái/phải.
  - Trạng thái khởi đầu (Initial State): Ma trận ban đầu do người dùng nhập hoặc mặc định.
  - Trạng thái đích (Goal State): Ma trận đích (thường là [1,2,3],[4,5,6],[7,8,0]).
  - Solution: Dãy các trạng thái từ khởi đầu đến đích, thể hiện đường đi lời giải.

- **Thuật toán đã triển khai:**
  - BFS (Breadth-First Search)
  - DFS (Depth-First Search)
  - UCS (Uniform Cost Search)
  - IDDFS (Iterative Deepening DFS)

- **Hình ảnh gif của từng thuật toán khi áp dụng lên trò chơi:**
  - (Chèn các gif minh họa animation từng thuật toán tại đây, ví dụ: `assets/bfs.gif`, `assets/dfs.gif`, ...)

- **Hình ảnh so sánh hiệu suất của các thuật toán:**
  - (Chèn biểu đồ so sánh số bước, số node duyệt, thời gian thực thi, ví dụ: `assets/compare_uninformed.png`)

- **Nhận xét:**
  - BFS luôn tìm được lời giải ngắn nhất nhưng tốn nhiều bộ nhớ.
  - DFS có thể nhanh nhưng dễ rơi vào vòng lặp, không đảm bảo tìm được lời giải tối ưu.
  - UCS đảm bảo tìm lời giải tối ưu nhưng tốc độ phụ thuộc vào hàm chi phí.
  - IDDFS kết hợp ưu điểm của DFS và BFS, tiết kiệm bộ nhớ hơn BFS nhưng có thể lặp lại node.

#### 2.2. Các thuật toán Tìm kiếm có thông tin

- **Các thành phần chính:**
  - Giống như trên, bổ sung thêm hàm heuristic (ước lượng chi phí đến đích).

- **Thuật toán đã triển khai:**
  - Greedy Best-First Search
  - A* Search
  - IDA* (Iterative Deepening A*)

- **Hình ảnh gif của từng thuật toán:**
  - (Chèn các gif minh họa animation từng thuật toán tại đây, ví dụ: `assets/astar.gif`, ...)

- **Hình ảnh so sánh hiệu suất:**
  - (Chèn biểu đồ so sánh hiệu suất, ví dụ: `assets/compare_informed.png`)

- **Nhận xét:**
  - A* thường cho kết quả tối ưu và nhanh nhất nếu heuristic tốt.
  - Greedy nhanh nhưng không đảm bảo tối ưu.
  - IDA* tiết kiệm bộ nhớ hơn A* nhưng có thể lặp lại node.

#### 2.3. Các thuật toán khác

- **Tìm kiếm trong môi trường phức tạp (AND-OR, Partial Observation, No-Observation):**
  - AND-OR Search: Giải bài toán khi môi trường có tính bất định, trạng thái có thể phân nhánh AND/OR.
  - Partial Observation: Chỉ quan sát được một phần trạng thái, thuật toán phải duy trì belief state.
  - No-Observation: Không quan sát được trạng thái, thuật toán phải duy trì tập hợp các belief state.
  - (Chèn các hình/cây minh họa, ví dụ: `assets/andor_tree.png`, `assets/partial_obs.gif`, ...)

- **Tìm kiếm ràng buộc (Constraint Search):**
  - Backtracking, Forward Checking, AC-3: Giải bài toán với các ràng buộc bổ sung, kiểm tra tính hợp lệ của trạng thái trước khi mở rộng.

- **Học tăng cường (Reinforcement Learning):**
  - Q-Learning, TD-Learning: Học chính sách giải bài toán thông qua trải nghiệm, không cần mô hình hóa toàn bộ không gian trạng thái.

### 3. Kết luận

- Ứng dụng đã xây dựng thành công giao diện trực quan, hỗ trợ nhập trạng thái, chọn thuật toán, xem từng bước giải và so sánh hiệu suất.
- Đã triển khai và trực quan hóa đa dạng các thuật toán từ cơ bản đến nâng cao, bao gồm cả môi trường bất định và học tăng cường.
- Việc trực quan hóa cây tìm kiếm (đặc biệt là AND-OR, partial/no-observation) giúp hiểu sâu hơn về bản chất các thuật toán.
- Kết quả cho thấy các thuật toán heuristic (A*, IDA*) thường hiệu quả nhất cho 8-puzzle, nhưng các thuật toán khác cũng có ưu điểm riêng trong từng trường hợp.

---

*Lưu ý: Để xem trực quan, hãy chạy `main.py`, chọn thuật toán và nhập trạng thái tùy ý. Các hình ảnh/gif minh họa cần được chụp lại từ giao diện thực tế và đặt vào thư mục `assets/` hoặc tương đương.*

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.