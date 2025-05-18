import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class AndOrTreeNode:
    def __init__(self, state, node_type='OR', children=None, parent=None, depth=0, node_id=None, label=None):
        self.state = state
        self.node_type = node_type
        self.children = children if children is not None else []
        self.parent = parent
        self.depth = depth
        self.x = 0
        self.y = 0
        self.node_id = node_id
        self.label = label
        self.image = None
        
    def get_state_image(self, size=60):
        if not self.state:
            return None
            
        # Create puzzle board image
        img = Image.new('RGB', (size, size), color='white')
        cell_size = size // 3
        
        for i in range(3):
            for j in range(3):
                val = self.state[i][j]
                x = j * cell_size
                y = i * cell_size
                # Draw cell border
                img.paste('lightgray', [x, y, x+cell_size, y+cell_size])
                # Draw number if not empty
                if val != 0:
                    # Center number in cell
                    pass
        return ImageTk.PhotoImage(img)

class AndOrTreeVisualizer(tk.Toplevel):
    def __init__(self, root, tree_root, solution_path=None):
        super().__init__(root)
        self.title("AND-OR Tree Visualization")
        self.geometry("1200x800")
        
        # Initialize visualization parameters first
        self.zoom_factor = 1.0
        self.node_radius = 32
        self.edge_style = tk.StringVar(value="straight")  # Default edge style
        self.level_gap = 100
        self.sibling_gap = 60
        self.node_positions = {}
        self._node_counter = 0
        self.max_depth = tk.IntVar(value=4)  # Moved here
        
        # Create the main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top control area
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0,10))
        
        # Input area 
        input_frame = ttk.LabelFrame(self.control_frame, text="Input State", padding=5)
        input_frame.pack(side=tk.LEFT, padx=10)
        self.input_board = self.create_board_display(input_frame)
        # Show initial state 123456708
        self.update_board([
            [1,2,3],
            [4,5,6], 
            [7,0,8]
        ])
        input_board_btn = ttk.Button(input_frame, text="Show AND-OR", 
                                   command=self.visualize_tree)
        input_board_btn.pack(pady=5)
        
        # Middle status area
        status_frame = ttk.Frame(self.control_frame)
        status_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH, expand=True)
        
        self.status_label = ttk.Label(status_frame, text="Creating AND-OR Tree...")
        self.status_label.pack(side=tk.TOP)
        
        # Canvas for tree visualization
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=1200, 
                              height=700, scrollregion=(0,0,2000,2000))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(canvas_frame, orient="vertical", 
                               command=self.canvas.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        
        scroll_x = ttk.Scrollbar(canvas_frame, orient="horizontal",
                               command=self.canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.canvas.configure(xscrollcommand=scroll_x.set,
                          yscrollcommand=scroll_y.set)
        # Pan with mouse drag
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Button-1>", self._start_drag)        
        self._drag_data = None
        
        # Store tree data
        self.tree_root = tree_root
        self.solution_path = solution_path or []
        
        # Initial tree setup
        self._assign_node_ids(self.tree_root)
        self.draw_tree()
        
        # Add control buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Level controls
        level_frame = ttk.LabelFrame(button_frame, text="Tree Depth", padding=5)
        level_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(level_frame, text="Max Level:").pack(side=tk.LEFT)
        level_spinbox = ttk.Spinbox(level_frame, from_=1, to=10, width=3,
                                  textvariable=self.max_depth,
                                  command=self.redraw_tree)
        level_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        zoom_frame = ttk.LabelFrame(button_frame, text="Zoom", padding=5)
        zoom_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(zoom_frame, text="🔍+", width=3,
                  command=lambda: self.zoom(1.2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="🔍-", width=3,
                  command=lambda: self.zoom(0.8)).pack(side=tk.LEFT, padx=2)
        
        # Edge style controls
        edge_frame = ttk.LabelFrame(button_frame, text="Edge Style", padding=5)
        edge_frame.pack(side=tk.LEFT, padx=5)
        
        self.edge_style = tk.StringVar(value="straight")
        ttk.Radiobutton(edge_frame, text="Straight", value="straight",
                       variable=self.edge_style, 
                       command=self.redraw_tree).pack(side=tk.LEFT)
        ttk.Radiobutton(edge_frame, text="Curved", value="curved",
                       variable=self.edge_style,
                       command=self.redraw_tree).pack(side=tk.LEFT)
                       
        # Node spacing controls
        spacing_frame = ttk.LabelFrame(button_frame, text="Spacing", padding=5)
        spacing_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(spacing_frame, text="↔️+", width=3,
                  command=lambda: self.adjust_spacing("horizontal", 1.2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(spacing_frame, text="↔️-", width=3,
                  command=lambda: self.adjust_spacing("horizontal", 0.8)).pack(side=tk.LEFT, padx=2)
        ttk.Button(spacing_frame, text="↕️+", width=3,
                  command=lambda: self.adjust_spacing("vertical", 1.2)).pack(side=tk.LEFT, padx=2)        
        ttk.Button(spacing_frame, text="↕️-", width=3,
                  command=lambda: self.adjust_spacing("vertical", 0.8)).pack(side=tk.LEFT, padx=2)
                  
        # Configure canvas
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
    def _assign_node_ids(self, tree_root):
        """Assign unique IDs to each node using an iterative approach."""
        if not tree_root:
            return

        self._node_counter = 0
        stack = [tree_root]
        visited = set()

        while stack:
            node = stack.pop()

            # Use node object as key for visited set
            if node in visited:
                continue

            visited.add(node)

            node.node_id = f"N{self._node_counter}"
            self._node_counter += 1

            # Push children onto the stack (order might affect visualization slightly, but ensures all are visited)
            # Reversing children list makes it behave like a recursive pre-order traversal
            for child in reversed(node.children):
                stack.append(child)

    def draw_tree(self):
        """Draw the complete AND-OR tree"""
        if not self.tree_root:
            return
            
        # Clear canvas and reset positions
        self.node_positions = {}
        # The node counter is reset inside _assign_node_ids now
        
        # Calculate initial positions and draw
        # We need to assign node IDs before calculating layout
        self._assign_node_ids(self.tree_root)
        
        # Ensure the layout starts from the actual tree root and is centered
        center_x = self.canvas.winfo_width() / 2
        root_y = 50 # Y-coordinate for the root node
        self._layout_tree(self.tree_root, center_x, root_y)
        
        # Draw tree elements up to max_depth
        current_depth = 0
        self._draw_edges(self.tree_root)
        self._draw_nodes(self.tree_root)
        
        # Add legend
        self._draw_legend()
        
        # Ensure all content is visible
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _layout_tree(self, node, x, y, visited=None):
        """Calculate positions for all nodes in the tree"""
        if visited is None:
            visited = set()

        # Check if the node has already been visited
        if node in visited:
            return x, x

        # Mark the node as visited
        visited.add(node)

        node.x = x
        node.y = y
        self.node_positions[node] = (x, y)

        if not node.children:
            return x, x

        # Calculate positions for children
        min_x = x
        max_x = x
        
        # Calculate total width needed for this level based on child spacing
        # Use self.sibling_gap directly for the base spacing
        effective_child_spacing = self.sibling_gap # Use the adjusted sibling_gap
        total_width = (len(node.children) - 1) * effective_child_spacing
        
        # Calculate the starting x position for the leftmost child
        child_x = x - total_width / 2

        # Process all children at the same level
        for child in node.children:
            # Keep y-coordinate the same for all children at this level
            child_y = y + self.level_gap
            
            # Assign x-coordinate for this child
            child_x_pos = child_x
            
            # Move to the next child position
            child_x += effective_child_spacing
            
            # Update min/max x for this level (this is mostly for calculating overall tree width if needed, but keep it)
            min_x = min(min_x, child_x_pos)
            max_x = max(max_x, child_x_pos)
            
            # Store child position
            # Note: The recursive call below might update child.x and child.y again
            # We need to ensure layout propagates correctly.
            # For now, let's store it, the recursive call will refine for its subtree root
            child.x = child_x_pos
            child.y = child_y
            self.node_positions[child] = (child_x_pos, child_y)
            
            # Recursively layout the subtree rooted at this child
            # Pass the calculated position as the starting point for the child's subtree layout
            self._layout_tree(child, child_x_pos, child_y, visited)

        # The min_x and max_x returned here represent the extent of the current node's children
        # This might not be the total extent of the subtree rooted at 'node'.
        # A more sophisticated layout algorithm (like Reingold-Tilford) is needed for perfect symmetry.
        # For this approach, returning the min/max of direct children positions is sufficient for basic centering.
        return min_x, max_x

    def zoom(self, factor):
        """Zoom in or out of the tree with limits and centering"""
        # Define zoom limits
        min_zoom, max_zoom = 0.5, 3.0

        # Calculate new zoom factor
        new_zoom_factor = self.zoom_factor * factor

        # Enforce zoom limits
        if new_zoom_factor < min_zoom or new_zoom_factor > max_zoom:
            return

        # Update zoom factor and related sizes
        self.zoom_factor = new_zoom_factor
        # Recalculate node and spacing sizes based on the new zoom factor
        # This ensures consistency when redrawing
        self.node_radius = max(10, 32 * self.zoom_factor) # Base node_radius was 32
        self.level_gap = max(10, 100 * self.zoom_factor)   # Base level_gap was 100
        self.sibling_gap = max(10, 60 * self.zoom_factor)  # Base sibling_gap was 60

        # Redraw the tree with updated parameters
        self.redraw_tree()

    def adjust_spacing(self, direction, factor):
        """Adjust spacing between nodes"""
        # Update spacing values based on factor
        if direction == "horizontal":
            self.sibling_gap = max(10, self.sibling_gap * factor)
        else:
            self.level_gap = max(10, self.level_gap * factor)
            
        # Redraw the tree with new spacing
        self.redraw_tree()

    def redraw_tree(self):
        """Redraw the tree with updated settings"""
        self.canvas.delete("all") # Clear everything before redrawing
        self.draw_tree()

    def _draw_legend(self):
        """Draw legend explaining node types and colors"""
        # Position legend in top-right corner
        x = self.canvas.winfo_width() - 150
        y = 20
        padding = 25

        # Background
        self.canvas.create_rectangle(x-10, y-10, x+140, y+120,
                                   fill="white", outline="#CCCCCC")

        # OR Node example
        self.canvas.create_oval(x, y, x+20, y+20,
                              fill="white", outline="#1976d2", width=2)
        self.canvas.create_text(x+60, y+10,
                              text="OR Node", anchor="w",
                              font=("Arial", 9))
        
        # AND Node example
        y += padding
        self.canvas.create_rectangle(x, y, x+20, y+20,
                                   fill="white", outline="#388e3c", width=2)
        self.canvas.create_text(x+60, y+10,
                              text="AND Node", anchor="w",
                              font=("Arial", 9))

        # Start state
        y += padding
        self.canvas.create_oval(x, y, x+20, y+20,
                              fill="#E3F2FD", outline="#1976d2", width=2)
        self.canvas.create_text(x+60, y+10,
                              text="Start State", anchor="w",
                              font=("Arial", 9))

        # Goal state
        y += padding
        self.canvas.create_oval(x, y, x+20, y+20,
                              fill="#E8F5E9", outline="#1976d2", width=2)
        self.canvas.create_text(x+60, y+10,
                              text="Goal State", anchor="w",
                              font=("Arial", 9))

    def _draw_edges(self, tree_root):
        """Draw connections between nodes using an iterative approach with depth limit."""
        if not tree_root:
            return

        stack = [(tree_root, 0)] # Stack stores (node, depth)
        visited_edges = set() # To prevent drawing duplicate edges in case of shared nodes

        while stack:
            node, current_depth = stack.pop()

            # Stop traversing if depth exceeds max_depth
            if current_depth >= self.max_depth.get():
                continue

            # Push children onto the stack for traversal first
            for child in reversed(node.children):
                stack.append((child, current_depth + 1))

            # Now process the current node to draw edges to its children
            if current_depth + 1 <= self.max_depth.get():
                for child in node.children:
                    # Use node object as key for visited set
                    edge_key = (node, child)
                    if edge_key in visited_edges:
                        continue
                    visited_edges.add(edge_key)

                    # Different styling for AND/OR nodes
                    dash_pattern = (6, 4) if node.node_type == 'AND' else None
                    edge_color = "#388e3c" if node.node_type == 'AND' else "#1976d2"

                    # Get node positions (should be available after _layout_tree)
                    if node not in self.node_positions or child not in self.node_positions:
                        print(f"Warning: Edge between {node.node_id} and {child.node_id} cannot be drawn, node position missing.")
                        continue
                        
                    start_x, start_y_center = self.node_positions[node]
                    end_x, end_y_center = self.node_positions[child]

                    # Adjust start/end points to edge of node shapes
                    start_y = start_y_center + self.node_radius
                    end_y = end_y_center - self.node_radius

                    if self.edge_style.get() == "curved":
                        points = self._calculate_edge_path(start_x, start_y,
                                                       end_x, end_y, True)
                        self.canvas.create_line(points, smooth=True,
                                           fill=edge_color, width=2,
                                           dash=dash_pattern, tags="edge")
                    else:
                        self.canvas.create_line(start_x, start_y,
                                           end_x, end_y,
                                           fill=edge_color, width=2,
                                           dash=dash_pattern, tags="edge")

                    # Draw movement direction labels
                    if node.node_type == 'AND' and child.label:
                         # Only draw labels for action nodes (children of AND nodes)
                         if any(direction in str(child.label) for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']):
                             mid_x = (start_x + end_x) / 2
                             mid_y = (start_y + end_y) / 2 - 15
                             self.canvas.create_text(mid_x, mid_y,
                                               text=child.label,
                                               font=("Arial", 8, "bold"),
                                               fill="#1976d2",
                                               tags="edge")

    def _draw_nodes(self, tree_root):
        """Draw nodes with puzzle state visualization using an iterative approach."""
        if not tree_root:
            return

        stack = [(tree_root, 0)] # Stack stores (node, depth)
        visited = set() # To handle potential cycles or shared nodes if necessary

        while stack:
            node, current_depth = stack.pop()

            if node in visited:
                continue
            visited.add(node)
            
            # Stop drawing if depth exceeds max_depth
            if current_depth > self.max_depth.get():
                continue

            # Get calculated position (should be available after _layout_tree)
            if node not in self.node_positions:
                # This should not happen if _layout_tree ran correctly before _draw_nodes
                print(f"Warning: Node {node.node_id} not found in node_positions")
                continue
                
            x, y = self.node_positions[node]

            # Background and outline colors based on node type and label
            bg_color = "white"
            outline_color = "#1976d2" # Default blue for OR
            if node.node_type == 'AND':
                outline_color = "#388e3c" # Green for AND

            if node.label == 'START':
                bg_color = "#e3f2fd"  # Light blue for start
                outline_color = "#1976d2" # Blue outline for start
            elif node.label == 'GOAL':
                bg_color = "#e8f5e9"  # Light green for goal
                outline_color = "#388e3c" # Green outline for goal
            elif node.label == 'FAIL':
                bg_color = "#ffebee"  # Light red for fail
                outline_color = "#e53935" # Red outline for fail
            # Add condition for 'Lặp' (Loop) and 'Giới hạn' (Limit)
            elif node.label == 'Lặp':
                 bg_color = "#ffebee" # Light red
                 outline_color = "#e53935" # Red outline
            elif node.label == 'Giới hạn':
                 bg_color = "#fffde7" # Light yellow
                 outline_color = "#fbc02d" # Darker yellow outline

            # Draw node shape
            if node.node_type == 'AND':
                # Rectangle for AND nodes
                self.canvas.create_rectangle(x-self.node_radius, y-self.node_radius,
                                        x+self.node_radius, y+self.node_radius,
                                        fill=bg_color, outline=outline_color, width=2,
                                        tags=f"node_{node.node_id}")
            else:
                # Circle for OR nodes
                self.canvas.create_oval(x-self.node_radius, y-self.node_radius,
                                    x+self.node_radius, y+self.node_radius,
                                    fill=bg_color, outline=outline_color, width=2,
                                    tags=f"node_{node.node_id}")

            # Draw node labels
            self._draw_node_label(node, x, y)

            # Draw 8-puzzle state
            if node.state:
                board_size = self.node_radius * 1.5
                cell_size = board_size / 3
                start_x = x - board_size/2
                start_y = y - board_size/2

                for i in range(3):
                    for j in range(3):
                        val = node.state[i][j]
                        cell_x = start_x + j * cell_size
                        cell_y = start_y + i * cell_size

                        # Draw cell background
                        bg_color_cell = "#e3f2fd" if val != 0 else "white"
                        border_width = 2 if node.label == 'START' else 1
                        self.canvas.create_rectangle(cell_x, cell_y,
                                                cell_x + cell_size, cell_y + cell_size,
                                                fill=bg_color_cell, outline="#1976d2",
                                                width=border_width)

                        # Draw number
                        if val != 0:
                            # Use bold font for initial state
                            font_weight = "bold" if node.label == 'START' else "normal"
                            font_size = int(cell_size/2)
                            self.canvas.create_text(cell_x + cell_size/2,
                                               cell_y + cell_size/2,
                                               text=str(val),
                                               font=("Arial", font_size, font_weight))

            # Push children onto the stack for traversal
            # Add children with incremented depth
            for child in reversed(node.children):
                 stack.append((child, current_depth + 1))

    def create_board_display(self, parent):
        """Create a 3x3 grid for displaying puzzle state"""
        frame = ttk.Frame(parent)
        frame.pack(padx=5, pady=5)
        
        self.board_cells = []  # Change to instance variable
        for i in range(3):
            row = []
            for j in range(3):
                cell = ttk.Label(frame, text="", width=3,
                               style="Board.TLabel",
                               relief="solid", borderwidth=1)
                cell.grid(row=i, column=j, padx=1, pady=1)
                row.append(cell)
            self.board_cells.append(row)
            
        # Create custom style for board cells
        style = ttk.Style()
        style.configure("Board.TLabel", 
                       font=("Arial", 14, "bold"),
                       padding=8,
                       anchor="center",
                       background="white")
                       
        return self.board_cells

    def update_board(self, state):
        """Update the board display with a new state"""
        if not hasattr(self, 'board_cells') or not self.board_cells:
            return
            
        for i in range(3):
            for j in range(3):
                if isinstance(state[0], list):  # 2D array
                    value = state[i][j]
                else:  # flat list
                    value = state[i * 3 + j]
                    
                cell = self.board_cells[i][j]
                if value == 0:
                    cell.configure(text="")
                else:
                    cell.configure(text=str(value))

    def visualize_tree(self):
        """Handle the Show AND-OR button click"""
        if not self.tree_root:
            self.status_label.config(text="No tree data available")
            return
            
        # Clear any previous visualization
        self.canvas.delete("all")
        
        # Update status
        self.status_label.config(text="Visualizing AND-OR Tree...")
        
        # Layout and draw the tree
        self._assign_node_ids(self.tree_root)
        self.draw_tree()
        
        # Update status
        self.status_label.config(text="Tree visualization complete")

    def _start_drag(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _on_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _calculate_edge_path(self, start_x, start_y, end_x, end_y, curved=False):
        """Calculate the path for an edge between two nodes"""
        if not curved:
            return [start_x, start_y, end_x, end_y]
            
        # Calculate control point for curved path
        mx = (start_x + end_x) / 2  # midpoint x
        cy = (start_y + end_y) / 2 - 30  # control point y (shifted up)
        
        # Generate points for smooth curve
        points = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve
            px = (1-t)**2 * start_x + 2*(1-t)*t*mx + t**2*end_x
            py = (1-t)**2 * start_y + 2*(1-t)*t*cy + t**2*end_y
            points.extend([px, py])
        return points
        
    def _draw_edge_label(self, x, y, label, is_and=False):
        """Draw a label for an edge"""
        if is_and:
            self.canvas.create_text(x, y - 15, 
                                  text=f"AND-Node\n{label}",
                                  font=("Arial", 8),
                                  fill="#4CAF50",
                                  justify=tk.CENTER)
        else:
            self.canvas.create_text(x, y + 15,
                                  text=label,
                                  font=("Arial", 9, "bold"),
                                  fill="#FF5722" if "FAIL" in label else "#4CAF50")    
    def _draw_node_label(self, node, x, y):
        """Draw label for a node"""
        # Do not draw default type label if a special label (START, GOAL, FAIL, Lặp, Giới hạn) exists
        if node.label in ['START', 'GOAL', 'FAIL', 'Lặp', 'Giới hạn']:
             # Special state labels are handled below or not needed based on the image
             pass # No default type label needed for these
        else:
            # Draw node type label (AND/OR) - positioned below the state image based on the sample
            type_label_y = y + self.node_radius + 15 # Position below node
            type_color = "#388e3c" if node.node_type == "AND" else "#1976d2"
            type_text = f"{node.node_type}-Node"
            self.canvas.create_text(x, type_label_y,
                                text=type_text,
                                font=("Arial", 8),
                                fill=type_color,
                                tags=f"node_{node.node_id}")
            
        # Draw special state labels (START/GOAL/FAIL, Lặp, Giới hạn)
        if node.label in ['START', 'GOAL', 'FAIL']:
            # In the sample image, these labels appear inside or just below the node, without a separate background
            # Let's draw them centered within or below the node as text directly
            label_color = "#FF5722" if node.label == "FAIL" else "#388e3c" # Red for FAIL, Green for START/GOAL
            label_y = y + self.node_radius + 5 # Position slightly below the node
            if node.label == 'START' or node.label == 'GOAL':
                 label_y = y + self.node_radius + 5 # Adjust position if needed
            elif node.label == 'FAIL':
                 label_y = y + self.node_radius + 5 # Adjust position if needed
                 
            self.canvas.create_text(x, label_y,
                                text=node.label,
                                font=("Arial", 9, "bold"),
                                fill=label_color,
                                tags=f"node_{node.node_id}")
        elif node.label in ['Lặp', 'Giới hạn']:
             # These labels appear below the node in the sample
             label_color = "#e53935" if node.label == "Lặp" else "#fbc02d" # Red for Lặp, Orange/Yellow for Giới hạn
             label_y = y + self.node_radius + 15 # Position below the node
             self.canvas.create_text(x, label_y,
                                text=node.label,
                                font=("Arial", 9),
                                fill=label_color,
                                tags=f"node_{node.node_id}")

def build_andor_tree(initial_state=None, goal_state=None, steps=None):
    """
    Build AND-OR tree for 8-puzzle: always use steps (from controller/algorithm) to build the tree.
    If steps is None or empty, return a minimal node.
    
    Args:
        initial_state: The initial state of the puzzle
        goal_state: The goal state to reach 
        steps: List of steps from the AND-OR search algorithm
    """
    if steps and len(steps) > 0:
        return build_andor_tree_from_steps(steps, initial_state, goal_state)
    # If no steps, create a minimal tree with initial state
    init_state = initial_state or [
        [1, 2, 3],
        [4, 5, 6],
        [7, 0, 8]
    ]
    return AndOrTreeNode(state=init_state, node_type='OR', depth=0, label='START')

def build_andor_tree_from_steps(steps, initial_state, goal_state=None):
    """
    Build an AND-OR tree from the search steps provided by the controller.
    Each step has:
    - type (or/and): Node type 
    - state: Current puzzle state
    - chosen_action: Selected move (UP/DOWN/LEFT/RIGHT)
    - next_states: List of resulting states after applying actions
    - success: Whether this branch leads to a solution
    - explanation: Text description of the step
    """
    from collections import defaultdict
    
    # Maps to store nodes and track relationships
    node_map = {}  # (state_tuple, type) -> node
    children_map = defaultdict(list)  # Temporary storage for child nodes
    label_count = defaultdict(int)  # Counter for generating unique node labels
    
    # Debug output
    print(f"\nBuilding AND-OR tree:")
    print(f"Number of steps: {len(steps)}")
    print(f"Initial state: {initial_state}")
    print(f"Goal state: {goal_state}")
    
    def state_to_tuple(state):
        """Convert a 2D state array to a tuple for dictionary keys"""
        return tuple(tuple(row) for row in state)
    
    # First pass: Create all nodes
    for idx, step in enumerate(steps):
        # Extract and normalize state data
        state = step['state'] 
        state_tuple = state_to_tuple(state)
        node_type = step['type'].upper()
        
        # Special handling for initial state: ensure the first node uses the provided initial_state
        if idx == 0 and initial_state is not None:
            state = initial_state # Use the provided initial_state for the root node
            state_tuple = state_to_tuple(state)
        
        # Generate node label
        label = None
        if idx == 0:
            label = 'START'
        elif goal_state is not None and state_tuple == state_to_tuple(goal_state):
            label = 'GOAL'
            state = goal_state
        elif step.get('chosen_action'):
            label = step['chosen_action'].upper()
        elif step.get('success') is True:
            label = 'GOAL'
        elif step.get('success') is False and step.get('type').lower() == 'or':
            label = 'FAIL'
        else:
            label_count[node_type] += 1
            label = f"{node_type}{label_count[node_type]}"
            
        # Create new node if not exists
        key = (state_tuple, node_type)
        if key not in node_map:
            print(f"\nCreating node:")
            print(f"  Label: {label}")
            print(f"  Type: {node_type}")
            print(f"  State: {state}")
            node = AndOrTreeNode(
                state=state,
                node_type=node_type,
                depth=0,  # Will be updated when linking nodes
                label=label
            )
            node_map[key] = node
            
    # Second pass: Link nodes
    for step in steps:
        state = step['state']
        state_tuple = state_to_tuple(state)
        node_type = step['type'].upper()
        node_key = (state_tuple, node_type)
        
        if node_key not in node_map:
            continue
            
        parent_node = node_map[node_key]
        
        # Link to child nodes
        for next_state in step.get('next_states', []):
            next_tuple = state_to_tuple(next_state)
            child_type = 'OR' if node_type == 'AND' else 'AND'
            child_key = (next_tuple, child_type)
            
            if child_key in node_map:
                child_node = node_map[child_key]
                if child_node not in parent_node.children:
                    print(f"\nLinking nodes:")
                    print(f"  Parent: {parent_node.label}")
                    print(f"  Child: {child_node.label}")
                    child_node.parent = parent_node
                    child_node.depth = parent_node.depth + 1
                    parent_node.children.append(child_node)
    
    # Find and return root (START) node
    # Prioritize finding a node with label 'START'
    root = None
    for node in node_map.values():
        if node.label == 'START':
            root = node
            break

    if not root:
        # Fallback to the first created node if no START found (should not happen in typical AND-OR search)
        print("Warning: 'START' node not found. Using the first created node as root.")
        root = next(iter(node_map.values()))
    
    print(f"\nTree built successfully:")
    print(f"Root node: {root.label}")
    print(f"Total nodes: {len(node_map)}")
    
    return root
