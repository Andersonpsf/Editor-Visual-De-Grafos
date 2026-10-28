import tkinter as tk
from gui import GraphEditor

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()