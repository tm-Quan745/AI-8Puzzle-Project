"""
AND-OR search tree visualization window
"""
import tkinter as tk
from tkinter import ttk
import time
from algorithms.complex_search import and_or_search

class AndOrTreeNode:
    def __init__(self, canvas, x, y, state, node_type="or", text="", tag=""):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.state = state
        self.node_type = node_type
        self.text = text
        self.tag = tag
        
        # Node visualization properties
        self.radius = 35
        self.success_color = "#90EE90"  # Light green
        self.failure_color = "#FFB6C1"  # Light red
        self.or_color = "#F0F8FF"      # Light blue for OR nodes
        self.and_color = "#FFE4B5"     # Light orange for AND nodes
        
        # Create node shape (circle for OR nodes, rectangle for AND nodes)
        if node_type == "or":
            self.node = canvas.create_oval(
                x - self.radius, y - self.radius,
                x + self.radius, y + self.radius,
                fill=self.or_color,
                outline="black",
                tags=tag
            )
        else:  # AND node
            self.node = canvas.create_rectangle(
                x - self.radius, y - self.radius,
                x + self.radius, y + self.radius,
                fill=self.and_color,
                outline="black",
                tags=tag
            )
        
        # Create text label with state representation
        self.label = canvas.create_text(
            x, y - 10,
            text=self.format_state(state),
            font=("Arial", 8),
            width=self.radius * 2,
            tags=tag
        )
        
        # Create type label
        self.type_label = canvas.create_text(
            x, y + 15,
            text=node_type.upper(),
            font=("Arial", 8, "bold"),
            tags=tag
        )
        
    def format_state(self, state):
        """Format state matrix for display"""
        if not state or not isinstance(state, list):
            return "None"
        return "\\n".join([" ".join(str(x) for x in row) for row in state])
        
    def update_color(self, success=None):
        if success is True:
            color = self.success_color
        elif success is False:
            color = self.failure_color
        else:
            color = self.or_color if self.node_type == "or" else self.and_color
        self.canvas.itemconfig(self.node, fill=color)

class AndOrTreeWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("AND-OR Search Tree")
        self.window.geometry("1200x800")
        
        # Create main layout frames
        self.setup_frames()
        self.setup_canvas()
        self.setup_controls()
        
        # Initialize visualization state
        self.nodes = {}  # Store tree nodes
        self.edges = []  # Store edges between nodes
        self.current_step = -1
        self.tree_data = None
        self.animation_running = False
        
        # Visualization layout parameters
        self.level_height = 120  # Vertical space between levels
        self.node_spacing = 100  # Horizontal space between nodes
        
    def setup_frames(self):
        # Control panel at top
        self.control_frame = ttk.Frame(self.window, padding="5")
        self.control_frame.pack(side="top", fill="x")
        
        # Canvas in middle
        self.canvas_frame = ttk.Frame(self.window)
        self.canvas_frame.pack(side="top", fill="both", expand=True)
        
        # Info panel at bottom
        self.info_frame = ttk.Frame(self.window, padding="5")
        self.info_frame.pack(side="bottom", fill="x")
        
    def setup_canvas(self):
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg="white",
            width=1000,
            height=600
        )
        
        # Add scrollbars
        h_scroll = ttk.Scrollbar(
            self.canvas_frame,
            orient="horizontal",
            command=self.canvas.xview
        )
        v_scroll = ttk.Scrollbar(
            self.canvas_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Configure canvas scrolling
        self.canvas.configure(
            xscrollcommand=h_scroll.set,
            yscrollcommand=v_scroll.set,
            scrollregion=(0, 0, 2000, 1500)
        )
        
        # Pack scrollbars and canvas
        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
    def setup_controls(self):
        # Run button
        self.run_button = ttk.Button(
            self.control_frame,
            text="Start Search",
            command=self.run_search
        )
        self.run_button.pack(side="left", padx=5)
        
        # Navigation controls
        nav_frame = ttk.Frame(self.control_frame)
        nav_frame.pack(side="left", padx=20)
        
        self.prev_button = ttk.Button(
            nav_frame,
            text="← Previous",
            command=self.prev_step,
            state="disabled"
        )
        self.prev_button.pack(side="left", padx=5)
        
        self.next_button = ttk.Button(
            nav_frame,
            text="Next →",
            command=self.next_step,
            state="disabled"
        )
        self.next_button.pack(side="left", padx=5)
        
        # Animation controls
        anim_frame = ttk.Frame(self.control_frame)
        anim_frame.pack(side="left", padx=20)
        
        self.animate_var = tk.BooleanVar(value=False)
        self.animate_check = ttk.Checkbutton(
            anim_frame,
            text="Auto-animate",
            variable=self.animate_var,
            command=self.toggle_animation
        )
        self.animate_check.pack(side="left", padx=5)
        
        self.speed_scale = ttk.Scale(
            anim_frame,
            from_=0.1,
            to=2.0,
            orient="horizontal",
            length=100
        )
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side="left", padx=5)
        
        # Status display
        self.status_var = tk.StringVar(value="Ready to start search")
        self.status_label = ttk.Label(
            self.info_frame,
            textvariable=self.status_var
        )
        self.status_label.pack(side="left", padx=10)
        
        # Progress info
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(
            self.info_frame,
            textvariable=self.progress_var
        )
        self.progress_label.pack(side="right", padx=10)
        
    def run_search(self):
        """Run AND-OR search and initialize visualization"""
        self.status_var.set("Running AND-OR search...")
        self.window.update()
        
        # Get initial and goal states
        initial_state = [
            [1, 2, 3],
            [4, 0, 6],
            [7, 5, 8]
        ]
        goal_state = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 0, 8]
        ]
        
        # Run search
        solution, nodes, steps, exec_time, self.tree_data = and_or_search(initial_state, goal_state)
        
        # Update status
        if solution and steps > 0:
            self.status_var.set(f"Solution found! Steps: {steps}, Nodes: {nodes}, Time: {exec_time:.3f}s")
        else:
            self.status_var.set("No solution found")
            
        # Reset visualization state
        self.current_step = -1
        self.nodes.clear()
        self.edges.clear()
        self.canvas.delete("all")
        
        # Enable controls
        self.next_button.configure(state="normal")
        self.prev_button.configure(state="disabled")
        
        # Start animation if enabled
        if self.animate_var.get():
            self.start_animation()
            
    def create_node(self, state, node_type, x, y, tag=""):
        """Create a new tree node"""
        node_id = f"node_{len(self.nodes)}"
        node = AndOrTreeNode(
            self.canvas, x, y, state,
            node_type=node_type,
            tag=tag or node_id
        )
        self.nodes[node_id] = node
        return node_id
        
    def create_edge(self, from_node, to_node, edge_type="normal"):
        """Create an edge between nodes"""
        from_x = self.nodes[from_node].x
        from_y = self.nodes[from_node].y + self.nodes[from_node].radius
        
        to_x = self.nodes[to_node].x
        to_y = self.nodes[to_node].y - self.nodes[to_node].radius
        
        # Create edge
        edge = self.canvas.create_line(
            from_x, from_y, to_x, to_y,
            fill="black",
            width=2
        )
        
        # Add arrow for OR node connections
        if self.nodes[from_node].node_type == "or":
            self.canvas.create_polygon(
                to_x - 5, to_y - 5,
                to_x + 5, to_y - 5,
                to_x, to_y,
                fill="black"
            )
            
        self.edges.append(edge)
        
    def next_step(self):
        """Display next step in search process"""
        # Add error handling to ensure self.tree_data is initialized before use
        if not self.tree_data:
            self.status_var.set("Error: Tree data not initialized. Please check the algorithm.")
            return
            
        if not self.tree_data or self.current_step >= len(self.tree_data['steps']) - 1:
            return
            
        self.current_step += 1
        step = self.tree_data['steps'][self.current_step]
        
        # Update visualization based on step type
        self.visualize_step(step)
        
        # Update controls
        self.prev_button.configure(state="normal")
        if self.current_step >= len(self.tree_data['steps']) - 1:
            self.next_button.configure(state="disabled")
            
        # Update progress
        self.progress_var.set(f"Step {self.current_step + 1}/{len(self.tree_data['steps'])}")
        
    def prev_step(self):
        """Display previous step in search process"""
        # Add error handling to ensure self.tree_data is initialized before use
        if not self.tree_data:
            self.status_var.set("Error: Tree data not initialized. Please check the algorithm.")
            return
            
        if self.current_step <= 0:
            return
            
        self.current_step -= 1
        self.canvas.delete("all")
        self.nodes.clear()
        self.edges.clear()
        
        # Replay steps up to current
        for i in range(self.current_step + 1):
            self.visualize_step(self.tree_data['steps'][i])
            
        # Update controls
        self.next_button.configure(state="normal")
        if self.current_step == 0:
            self.prev_button.configure(state="disabled")
            
        # Update progress
        self.progress_var.set(f"Step {self.current_step + 1}/{len(self.tree_data['steps'])}")
        
    def visualize_step(self, step):
        """Visualize a single search step"""
        state = step['state']
        step_type = step['type']
        parent_id = None
        
        # Calculate position for new node
        level = len([n for n in self.nodes.values() if n.state == state])
        x = 100 + level * self.node_spacing
        y = 100 + level * self.level_height
        
        # Create node
        node_id = self.create_node(state, step_type, x, y)
        
        # Find parent node if exists
        for n_id, node in self.nodes.items():
            if node.state == state and node != self.nodes[node_id]:
                parent_id = n_id
                break
                
        # Create edge from parent
        if parent_id:
            self.create_edge(parent_id, node_id)
            
        # Update node color based on success/failure
        self.nodes[node_id].update_color(step['success'])
        
        # Update explanation
        if step['explanation']:
            self.status_var.set(step['explanation'])
            
    def toggle_animation(self):
        """Toggle automatic animation"""
        if self.animate_var.get():
            self.start_animation()
        else:
            self.animation_running = False
            
    def start_animation(self):
        """Start automatic animation"""
        if not self.animation_running and self.current_step < len(self.tree_data['steps']) - 1:
            self.animation_running = True
            self.animate_step()
            
    def animate_step(self):
        """Animate a single step"""
        if not self.animation_running or self.current_step >= len(self.tree_data['steps']) - 1:
            self.animation_running = False
            return
            
        self.next_step()
        delay = int(1000 / self.speed_scale.get())
        self.window.after(delay, self.animate_step)
