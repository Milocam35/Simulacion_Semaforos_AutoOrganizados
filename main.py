import tkinter as tk
from gui.traffic_simulation_gui import TrafficSimulationGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulationGUI(root)
    root.mainloop()
