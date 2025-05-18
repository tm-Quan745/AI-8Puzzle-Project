# AI 8-Puzzle Solver

## 1. Mục tiêu
Dự án này nhằm giải quyết bài toán 8-puzzle bằng cách sử dụng các thuật toán trí tuệ nhân tạo. Mục tiêu chính là:
- Xây dựng các thuật toán tìm kiếm và học tăng cường để giải bài toán.
- So sánh hiệu suất của các thuật toán.
- Cung cấp giao diện trực quan để hiển thị cây AND-OR và các trạng thái.

## 2. Nội dung

### 2.1. Các thuật toán Tìm kiếm không có thông tin

#### Thành phần chính của bài toán tìm kiếm
- **Trạng thái ban đầu**: Vị trí các ô số trong bảng 8-puzzle.
- **Mục tiêu**: Đưa bảng về trạng thái đích (thường là 1-2-3-4-5-6-7-8-0).
- **Hành động**: Di chuyển ô trống (0) lên, xuống, trái, phải.
- **Solution**: Một chuỗi các hành động đưa trạng thái ban đầu về trạng thái mục tiêu.

#### Các thuật toán
- **BFS (Breadth-First Search)**: Duyệt theo chiều rộng.
- **DFS (Depth-First Search)**: Duyệt theo chiều sâu.
- **Uniform Cost Search**: Tìm kiếm chi phí đồng nhất.

#### Hình ảnh minh họa
- **GIF**: Hình ảnh động minh họa từng bước thực hiện của các thuật toán.

#### So sánh hiệu suất
- **Biểu đồ**: So sánh số lượng trạng thái đã duyệt, thời gian thực thi, và độ dài đường đi.

#### Nhận xét
- Các thuật toán không có thông tin thường duyệt nhiều trạng thái hơn và mất nhiều thời gian hơn so với các thuật toán có thông tin.

### 2.2. Các thuật toán Tìm kiếm có thông tin

#### Thành phần chính của bài toán tìm kiếm
- **Trạng thái ban đầu, mục tiêu, hành động**: Tương tự như phần 2.1.
- **Hàm đánh giá (Heuristic)**: Sử dụng các hàm như Manhattan Distance hoặc Số ô sai vị trí để đánh giá trạng thái.

#### Các thuật toán
- **A***: Tìm kiếm tối ưu với hàm heuristic.
- **Greedy Best-First Search**: Tìm kiếm tham lam dựa trên heuristic.

#### Hình ảnh minh họa
- **GIF**: Hình ảnh động minh họa từng bước thực hiện của các thuật toán.

#### So sánh hiệu suất
- **Biểu đồ**: So sánh hiệu suất của các thuật toán có thông tin với các thuật toán không có thông tin.

#### Nhận xét
- Các thuật toán có thông tin thường hiệu quả hơn nhờ sử dụng hàm heuristic để dẫn đường.

### 2.3. Các thuật toán học tăng cường

#### Q-Learning
- **Mô tả**: Áp dụng thuật toán Q-Learning để học cách giải bài toán 8-puzzle thông qua thử nghiệm và sai lầm.
- **Công thức cập nhật Q-value**:
  ```
  Q(s, a) = Q(s, a) + α * [r + γ * max(Q(s', a')) - Q(s, a)]
  ```
- **Hình ảnh minh họa**: Quá trình học và kết quả đạt được sau khi huấn luyện.

## 3. Kết luận
- **Kết quả đạt được**: Dự án đã xây dựng thành công các thuật toán giải bài toán 8-puzzle và cung cấp giao diện trực quan để hiển thị cây AND-OR và các trạng thái.
- **So sánh hiệu suất**: Các thuật toán có thông tin vượt trội hơn về hiệu suất so với các thuật toán không có thông tin.
- **Ứng dụng**: Dự án có thể được mở rộng để giải quyết các bài toán tương tự hoặc làm nền tảng cho các nghiên cứu sâu hơn về trí tuệ nhân tạo.