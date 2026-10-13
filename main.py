import tkinter as tk

from modern_gui import ModernApp

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Vinilo")
    root.geometry("1060x900")
    root.minsize(720, 650)
    ModernApp(root)
    root.mainloop()
