import tkinter as tk

class AndOrTreeNode:
    def __init__(self, state, node_type='OR', children=None, parent=None, depth=0, node_id=None, label=None):
        self.state = state  # 2D list or tuple
        self.node_type = node_type  # 'AND' or 'OR'
        self.children = children if children is not None else []
        self.parent = parent
        self.depth = depth
        self.x = 0
        self.y = 0
        self.node_id = node_id  # For display/debug
        self.label = label  # Custom label for display

class AndOrTreeVisualizer(tk.Toplevel):
    def __init__(self, root, tree_root, solution_path=None):
        super().__init__(root)
        self.title("AND-OR Tree Visualization")
        self.geometry("1200x700")
        # Canvas and scrollbars
        self.canvas = tk.Canvas(self, bg="#fafafa", width=1200, height=700, scrollregion=(0,0,2000,2000))
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scroll_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scroll_y.pack(side="right", fill="y")
        self.canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        # Pan with mouse drag
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Button-1>", self._start_drag)
        self._drag_data = None
        self.tree_root = tree_root
        self.solution_path = solution_path or []
        self.node_radius = 32
        self.level_gap = 100
        self.sibling_gap = 60
        self.node_positions = {}
        self._node_counter = 0
        self._assign_node_ids(self.tree_root)
        self.draw_tree()

    def _assign_node_ids(self, node):
        node.node_id = f"N{self._node_counter}"
        self._node_counter += 1
        for child in node.children:
            self._assign_node_ids(child)

    def draw_tree(self):
        self.node_positions = {}
        self.canvas.delete("all")
        self._layout_tree(self.tree_root, 600, 50)
        self._draw_edges(self.tree_root)
        self._draw_nodes(self.tree_root)

    def _layout_tree(self, node, x, y):
        node.x = x
        node.y = y
        self.node_positions[node] = (x, y)
        if not node.children:
            return x, x
        min_x = x
        max_x = x
        child_x = x - (len(node.children)-1)*self.sibling_gap//2
        for child in node.children:
            left, right = self._layout_tree(child, child_x, y + self.level_gap)
            child_x += self.sibling_gap
            min_x = min(min_x, left)
            max_x = max(max_x, right)
        return min_x, max_x

    def _draw_edges(self, node):
        for child in node.children:
            self.canvas.create_line(node.x, node.y, child.x, child.y, fill="#888", width=2)
            self._draw_edges(child)

    def _draw_nodes(self, node):
        # Use different shapes for AND/OR nodes
        fill = "#90caf9" if node.node_type == 'OR' else "#a5d6a7"
        outline = "#1976d2" if node.node_type == 'OR' else "#388e3c"
        if node in self.solution_path:
            fill = "#ffd54f"
            outline = "#fbc02d"
        x, y = node.x, node.y
        if node.node_type == 'AND':
            # Draw rectangle for AND node
            self.canvas.create_rectangle(x-self.node_radius, y-self.node_radius, x+self.node_radius, y+self.node_radius, fill=fill, outline=outline, width=3)
        else:
            # Draw oval for OR node
            self.canvas.create_oval(x-self.node_radius, y-self.node_radius, x+self.node_radius, y+self.node_radius, fill=fill, outline=outline, width=3)
        # Draw node id and depth
        self.canvas.create_text(x, y - self.node_radius - 10, text=f"{node.node_id} D{node.depth}", font=("Arial", 8), fill="gray")
        # Draw state as compact string (or label if present)
        if node.label:
            state_str = node.label
        else:
            state_str = '\n'.join(''.join(str(cell) for cell in row) for row in node.state)
        self.canvas.create_text(x, y, text=state_str, font=("Arial", 10, "bold"), fill="#263238")
        # Draw node type label
        self.canvas.create_text(x, y+self.node_radius+12, text=node.node_type, font=("Arial", 9, "italic"), fill=outline)
        for child in node.children:
            self._draw_nodes(child)

    def _start_drag(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _on_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

def build_andor_tree(initial_state=None, goal_state=None, max_depth=5, steps=None):
    """
    Build AND-OR tree for 8-puzzle: always use steps (from controller/algorithm) to build the tree.
    If steps is None or empty, return a minimal node.
    """
    if steps and len(steps) > 0:
        return build_andor_tree_from_steps(steps, initial_state)
    # Nếu không có steps, trả về node rỗng
    return AndOrTreeNode(state=initial_state or [[0,0,0],[0,0,0],[0,0,0]], node_type='OR', depth=0, label='EMPTY')

def build_andor_tree_from_steps(steps, initial_state, goal_state=None):
    """
    Xây dựng cây AND-OR từ danh sách các bước tìm kiếm (steps) của controller.
    Mỗi bước có 'type' (or/and), 'state', 'chosen_action', 'next_states', 'success', 'explanation'.
    Luôn gán đúng initial_state cho node START và goal_state cho node GOAL nếu có.
    """
    from collections import defaultdict
    node_map = {}  # (state_tuple, type) -> node
    children_map = defaultdict(list)
    label_count = defaultdict(int)

    def state_to_tuple(state):
        return tuple(tuple(row) for row in state)

    # Tạo node cho mỗi bước
    for idx, step in enumerate(steps):
        state = step['state']
        state_tuple = state_to_tuple(state)
        node_type = step['type'].upper()
        label = None
        # Gán nhãn đặc biệt cho node đầu tiên
        if idx == 0:
            label = 'START'
            state = initial_state if initial_state is not None else state
            state_tuple = state_to_tuple(state)
        elif step.get('success') is True and goal_state is not None and state_to_tuple(state) == state_to_tuple(goal_state):
            label = 'GOAL'
            state = goal_state
            state_tuple = state_to_tuple(state)
        elif step.get('chosen_action'):
            label = step['chosen_action'].upper()
        elif step.get('success') is True:
            label = 'GOAL'
        elif step.get('success') is False and step.get('type') == 'or':
            label = 'FAIL'
        else:
            label_count[node_type] += 1
            label = f"{node_type}{label_count[node_type]}"
        key = (state_tuple, node_type)
        if key not in node_map:
            node = AndOrTreeNode(state=state, node_type=node_type, depth=0, label=label)
            node_map[key] = node

    # Liên kết các node cha-con dựa trên next_states
    for idx, step in enumerate(steps):
        state = step['state']
        state_tuple = state_to_tuple(state)
        node_type = step['type'].upper()
        key = (state_tuple, node_type)
        node = node_map[key]
        # Tìm các node con
        for next_state in step.get('next_states', []):
            next_tuple = state_to_tuple(next_state)
            # Loại node con theo loại AND/OR
            if node_type == 'AND':
                child_type = 'OR'
            else:
                child_type = 'AND'
            child_key = (next_tuple, child_type)
            if child_key in node_map:
                child = node_map[child_key]
                child.parent = node
                child.depth = node.depth + 1
                if child not in node.children:
                    node.children.append(child)

    # Trả về node gốc (START)
    for node in node_map.values():
        if node.label == 'START':
            return node
    # Nếu không có, trả về node đầu tiên
    return next(iter(node_map.values()))
