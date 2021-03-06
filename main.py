import tkinter as tk
import time
import random


## CONSTANTS

# PLAY MODES, will add more later
MODE_MANUAL = 0
MODE_AUTO_RANDOM = 1

MODE = MODE_AUTO_RANDOM

# FIELD SETTINGS
ROWS = 4
COLS = 4
SIZE = 64
TEXT_COL_SPACE = 4

# RUN SETTINGS
WAIT_AFTER_STEP = 0
WAIT_AFTER_TERMINATE = 0
MAX_ITERATIONS = 10000


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

policies = [[[0,0,0,0] for _ in range(COLS)] for _ in range(ROWS)]


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
    def __init__(self, parent, rows=ROWS, cols=COLS, size=SIZE, text_col_space=TEXT_COL_SPACE, grid=GRID):
        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.rows = rows
        self.cols = cols
        self.size = size
        self.grid = grid if grid is not None else [[1 for _ in range(cols)] for _ in range(rows)]
        self.lock = False  # Used to block input when system is busy, used for both modes
        self.slipping = False
        self.terminated = False
        self.iterations = 0
        self.steps = []

        self.score = 0
        self.scores = []

        for i in range(len(self.grid)):
            if START in self.grid[i]:
                self.start_location = [i, self.grid[i].index(START)]
        try:
            self.start_location
        except:
            print("no start in grid")
            exit()
        self.current_location = self.start_location

        canvas_width = cols * size + text_col_space*size
        canvas_height = rows * size

        self.parent.resizable(False, False)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=canvas_width, height=canvas_height, background="bisque")
        self.canvas.pack(side="top", expand=True, padx=2, pady=2)

        self.text = tk.Text(self.canvas, height=canvas_height, width=text_col_space*cols*2)
        self.canvas.create_window((text_col_space*size,0), window=self.text, anchor='nw')
        self.add_text("SCORE: 0 (last: 0)")

        self.do_start()

        if MODE == MODE_MANUAL:
            self.canvas.bind("<Button-1>", lambda e: self.focus_force())
            # Define keybindings:
            self.bind('<Enter>', lambda e : self.do_start)
            self.bind('<Up>',    lambda e : self.move_player(UP))
            self.bind('<Right>', lambda e : self.move_player(RIGHT))
            self.bind('<Down>',  lambda e : self.move_player(DOWN))
            self.bind('<Left>',  lambda e : self.move_player(LEFT))
            self.focus_force()
        elif MODE == MODE_AUTO_RANDOM:
            self.generate_auto_random()

    def do_start(self):
        self.draw_grid(self.grid)
        self.place_player(self.start_location)
        self.current_location = self.start_location
        self.score = 0


    def draw_grid(self, grid):
        for row_i, row_cont in enumerate(grid):
            for cell_i, cell_cont in enumerate(row_cont):
                x1 = (cell_i * self.size)
                y1 = (row_i * self.size)
                x2 = x1 + self.size
                y2 = y1 + self.size
                color = GRID_COLORS[cell_cont]
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")


    def place_player(self, location):
        r, c = location
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
        # self.

    def move_player_only(self, dir):
        new_location = self.get_new_location(self.current_location, dir)
        if self.is_in_bounds(new_location):
            self.current_location = new_location  # store new location
            self.place_player(self.current_location)  # place on new location


    def move_player(self, dir):
        if MODE == MODE_MANUAL:
            if self.lock and not self.slipping:
                return
            self.lock = True

        new_location = self.get_new_location(self.current_location, dir)
        if self.is_in_bounds(new_location):
            self.current_location = new_location  # store new location
            self.place_player(self.current_location)  # place on new location

            cur_place_type = self.get_location_type(self.current_location)

            if cur_place_type == GOAL or cur_place_type == CRACK:  # if we reached goal or crack
                self.terminated = True
                self.clear_text()

                score = self.update_score()
                self.scores.append(score)  # added score to list of achieved scores
                self.add_text(f'{"WIN" if cur_place_type == GOAL else "FAIL"} | Score:{self.score} Best:{max(self.scores)}')

                return score

            elif cur_place_type == ICE:
                if self.slipping or random.random() < 0.05:
                    if not self.slipping:
                        self.add_text("Slipped!")
                    self.slipping = True
                    return self.move_player(dir)
                else:
                    return self.update_score()

            else:  # when on ship
                if self.slipping:
                   return self.move_player(dir)
                else:
                    return self.update_score()
        else:  # When at an edge
            self.slipping = False
            return self.update_score()



    def update_score(self):
        cur_place_type = self.get_location_type(self.current_location)
        cur_score = GRID_SCORES[cur_place_type]

        self.score += cur_score
        self.print_score(self.score, cur_score)

        if MODE == MODE_MANUAL:
            self.lock = False

        return cur_score

    def get_new_location(self, current, dir):
        if type(dir) == type(UP):
            return [current[0] + DIRECTIONS[dir][0], current[1] + DIRECTIONS[dir][1]]
        elif type(dir) == list:
            return [current[0] + dir[0], current[1] + dir[1]]
        else:
            return None

    def get_location_type(self, location):
        return GRID[location[0]][location[1]]

    def is_in_bounds(self, location):
        return 0 <= location[0] < self.rows and 0 <= location[1] < self.cols

    def print_score(self, total, recent):
        self.add_text(f"SCORE:{total} [{recent}]")

    def add_text(self, text):
        if int(self.text.index('end-1c').split('.')[0]) > self.rows*4:
            # if rows are filled: clear screen. Haven't worked out scrolling yet
            self.clear_text()

        self.text.insert(tk.END, f'{text}\n')

    def clear_text(self):
        self.text.delete(1.0, tk.END)

    def generate_auto_random(self):
        possible_dirs = []
        for dir in DIRECTIONS:
            if self.is_in_bounds(self.get_new_location(self.current_location, dir)):
                possible_dirs.append(dir)
        self.move_player(random.choice(possible_dirs))
        if self.terminated:
            self.iterations += 1
            self.do_start()
            self.terminated = False
            if self.iterations % 1000 == 0:
                print(f'{self.iterations} iterations')
            if self.iterations < MAX_ITERATIONS:
                self.after(WAIT_AFTER_TERMINATE, self.generate_auto_random)
            else:
                self.after_max_iterations()
        else:
            self.after(WAIT_AFTER_STEP, self.generate_auto_random)

    def after_max_iterations(self):
        print(f'Terminating after {MAX_ITERATIONS} iterations.')
        print(f'Best score: {max(self.scores)}')


if __name__ == "__main__":
    root = tk.Tk()
    board = GameBoard(root)
    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    root.mainloop()
