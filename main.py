import tkinter as tk
from ui.main_window import PuzzleSolverApp

def main():
    root = tk.Tk()
    app = PuzzleSolverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()