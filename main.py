import tkinter as tk

# GRID STUFF
START = 0
ICE   = 1
CRACK = 2
SHIP  = 3
GOAL  = 4

GRID_COLORS = {
    START: "blue",
    ICE: "white",
    CRACK: "red",
    SHIP: "yellow",
    GOAL: "green"
}

GRID_SCORES = {
    START:   0,
    ICE:     0,
    CRACK: -10,
    SHIP:   20,
    GOAL:  100
}

GRID = [
    [ICE,   ICE,   ICE,   GOAL],
    [ICE,   CRACK, ICE,   CRACK],
    [ICE,   ICE,   SHIP,  CRACK],
    [START, CRACK, CRACK, CRACK],
]

# DIRECTIONS
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

DIRECTIONS = {
    UP:    [-1,0],
    RIGHT: [0, 1],
    DOWN:  [1,0],
    LEFT:  [0, -1],
}

class GameBoard(tk.Frame):
    def __init__(self, parent, rows=4, cols=4, size=64, grid=GRID):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.rows = rows
        self.cols = cols
        self.size = size
        self.grid = grid if grid is not None else [[1 for _ in range(cols)] for _ in range(rows)]

        for i in range(len(self.grid)):
            if START in self.grid[i]:
                self.start_location = [i, self.grid[i].index(START)]
        try:
            self.start_location
        except:
            print("no start in grid")
            exit()
        self.current_location = self.start_location

        canvas_width = cols * size
        canvas_height = rows * size

        self.parent.resizable(False, False)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=canvas_width, height=canvas_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        self.do_start()
        self.bind('<Enter>', lambda e : self.do_start)
        self.bind('<Up>', lambda e : self.move_player(UP))
        self.bind('<Right>', lambda e : self.move_player(RIGHT))
        self.bind('<Down>', lambda e : self.move_player(DOWN))
        self.bind('<Left>', lambda e : self.move_player(LEFT))
        self.focus_force()


    def do_start(self):
        self.draw_grid(self.grid)
        self.place_player(*self.start_location)
        self.current_location = self.start_location


    def draw_grid(self, grid):
        for row_i, row_cont in enumerate(grid):
            for cell_i, cell_cont in enumerate(row_cont):
                x1 = (cell_i * self.size)
                y1 = (row_i * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                color = GRID_COLORS[cell_cont]
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")


    def place_player(self, r, c):
        self.canvas.delete("player")
        coords = [
            c * self.size + 0.25 * self.size,
            r * self.size + 0.25 * self.size,
            c * self.size + 0.75 * self.size,
            r * self.size + 0.50 * self.size,
            c * self.size + 0.25 * self.size,
            r * self.size + 0.75 * self.size,
        ]

        self.canvas.create_polygon(coords, outline="black", fill='orange', width=3, tags="player")

    def move_player(self, dir):
        new_direction = [self.current_location[0] + DIRECTIONS[dir][0], self.current_location[1]+DIRECTIONS[dir][1]]
        if 0 <= new_direction[0] < self.rows and 0 <= new_direction[1] < self.cols:
            self.current_location = new_direction
        self.place_player(*self.current_location)

if __name__ == "__main__":
    root = tk.Tk()
    board = GameBoard(root)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    root.mainloop()