def is_valid_puzzle(state):
    """Kiểm tra tính hợp lệ của trạng thái puzzle"""
    if not state or len(state) != 3:
        return False
        
    numbers = set()
    for row in state:
        if len(row) != 3:
            return False
        for num in row:
            if not isinstance(num, int) or num < 0 or num > 8:
                return False
            if num in numbers:
                return False
            numbers.add(num)
            
    return len(numbers) == 9

def is_solvable(state):
    """Kiểm tra xem trạng thái có giải được không"""
    if not is_valid_puzzle(state):
        return False
        
    # Chuyển ma trận thành mảng 1 chiều
    flat_state = [num for row in state for num in row]
    
    # Đếm số nghịch thế
    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i + 1, len(flat_state)):
            if flat_state[i] != 0 and flat_state[j] != 0 and flat_state[i] > flat_state[j]:
                inversions += 1
                
    # Tìm vị trí của số 0
    blank_row = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                blank_row = i
                break
                
    # Nếu kích thước lẻ, số nghịch thế phải chẵn
    # Nếu kích thước chẵn, số nghịch thế + vị trí hàng của ô trống phải lẻ
    return (inversions % 2 == 0) if (blank_row % 2 == 0) else (inversions % 2 == 1) 