from tkinter import *
from cell import Cell
from random import randint
from time import sleep


class MazeGenerator:
    def __init__(self):
        root = Tk()
        root.title("Maze generator")
        root.state('zoomed')

        self.size = root.winfo_screenheight() - 100
        self.delay = 0.05

        self.canvas = Canvas(root, height=self.size, width=self.size)
        self.canvas.grid(column=0, padx=50, pady=15, rowspan=9)
        self.__clear_canvas()

        label = Label(root, text="Podaj rozmiar labiryntu (od 2 do 100):")
        label.grid(column=1, row=0)

        self.maze_size_entry = Entry(root)
        self.maze_size_entry.grid(column=1, row=1)
        self.maze_size_entry.insert(0, 20)

        self.label_text = StringVar()
        self.label_text.set("")
        label = Label(root, textvariable=self.label_text, foreground="red")
        label.grid(column=1, row=2)

        self.generate_button = Button(root, text="GENERUJ LABIRYNT", command=self.__initialize)
        self.generate_button.grid(column=1, row=3)

        self.faster_button = Button(root, text="PRZYSPIESZ", command=self.__faster, state=DISABLED)
        self.faster_button.grid(column=1, row=4)

        self.slower_button = Button(root, text="ZWOLNIJ", command=self.__slower, state=DISABLED)
        self.slower_button.grid(column=1, row=5)

        self.button_text = StringVar()
        self.button_text.set("ZATRZYMAJ")
        self.pause_button = Button(root, textvariable=self.button_text, command=self.__abort, state=DISABLED)
        self.pause_button.grid(column=1, row=6)

        self.reset_button = Button(root, text="RESETUJ", command=self.__reset, state=DISABLED)
        self.reset_button.grid(column=1, row=7)

        self.show_path_button = Button(root, text="POKAŻ ŚCIEŻKĘ", command=self.__show_path, state=DISABLED)
        self.show_path_button.grid(column=1, row=8)

        root.mainloop()

    def __initialize(self):
        self.generate_button.config(state=DISABLED)
        self.show_path_button.config(state=DISABLED)
        error_text = "Podano nieprawidłowy rozmiar labiryntu."

        try:
            self.maze_size = int(self.maze_size_entry.get())
        except ValueError:
            self.generate_button.config(state=NORMAL)
            self.label_text.set(error_text)
        else:
            self.label_text.set("")
            if self.maze_size < 2 or self.maze_size > 100:
                self.generate_button.config(state=NORMAL)
                self.label_text.set(error_text)
            else:
                self.cell_size = self.size / self.maze_size
                self.canvas.config(height=self.size + 1, width=self.size + 1)
                self.aborted = False
                self.visited_cells = list()

                self.__prepare_canvas()

                self.available_cells = [Cell(0, 0)]
                self.pause_button.config(state=NORMAL)
                self.reset_button.config(state=NORMAL)
                if self.delay > 0.:
                    self.faster_button.config(state=NORMAL)
                if self.delay < 0.2:
                    self.slower_button.config(state=NORMAL)
                self.__generate_maze()

    def __abort(self):
        self.aborted = True
        self.button_text.set("WZNÓW")
        self.pause_button.config(command=self.__resume)

    def __resume(self):
        self.aborted = False
        self.button_text.set("ZATRZYMAJ")
        self.pause_button.config(command=self.__abort)
        self.__generate_maze()

    def __reset(self):
        self.aborted = True
        self.generate_button.config(state=NORMAL)
        self.pause_button.config(state=DISABLED)
        self.reset_button.config(state=DISABLED)
        self.show_path_button.config(state=DISABLED)
        self.button_text.set("ZATRZYMAJ")
        self.__clear_canvas()

    def __faster(self):
        delay = self.delay - 0.01
        if delay < 0.:
            self.delay = 0
            self.faster_button.config(state=DISABLED)
        else:
            self.delay = delay
            self.slower_button.config(state=NORMAL)

    def __slower(self):
        delay = self.delay + 0.01
        if delay > 0.2:
            self.delay = 0.2
            self.slower_button.config(state=DISABLED)
        else:
            self.delay = delay
            self.faster_button.config(state=NORMAL)

    def __prepare_canvas(self):
        for i in range(self.maze_size):
            for j in range(self.maze_size):
                self.canvas.create_rectangle(i * self.cell_size + 2, j * self.cell_size + 2,
                                             (i + 1) * self.cell_size + 2, (j + 1) * self.cell_size + 2, fill="#a6a6a6")

    def __clear_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(2, 2, self.size, self.size, fill="white")

    def __generate_maze(self):
        self.canvas.create_line(2, 3, 2, self.cell_size + 2, fill="white")
        while len(self.available_cells) != 0:
            if self.aborted:
                break

            cell = self.available_cells[randint(0, len(self.available_cells) - 1)]
            self.__visit(cell)
            self.available_cells.remove(cell)
            neighbours = self.__get_visited_neighbours(cell)
            if len(neighbours) != 0:
                self.__connect(cell, neighbours[randint(0, len(neighbours) - 1)])
            neighbours = self.__get_unvisited_neighbours(cell)
            for _cell in neighbours:
                if _cell not in self.available_cells:
                    self.__draw_cell(_cell, "#ff3333")
                    self.available_cells.append(_cell)
                    self.canvas.update()

        if not self.aborted:
            self.generate_button.config(state=NORMAL)
            self.show_path_button.config(state=NORMAL)
            self.pause_button.config(state=DISABLED)
            self.faster_button.config(state=DISABLED)
            self.slower_button.config(state=DISABLED)

    def __visit(self, cell):
        self.__draw_cell(cell, "#66c2ff")
        self.visited_cells.append(cell)
        self.canvas.update()
        sleep(self.delay)

    def __draw_cell(self, cell, color):
        if not self.aborted or color == "white":
            x_position = cell.x * self.cell_size + 2
            y_position = cell.y * self.cell_size + 2
            self.canvas.create_rectangle(x_position + 1, y_position + 1, x_position + self.cell_size,
                                         y_position + self.cell_size, fill=color, width=0)

    def __get_visited_neighbours(self, cell):
        neighbours = list()
        if cell.x - 1 >= 0:
            _cell = next((c for c in self.visited_cells if c == Cell(cell.x - 1, cell.y)), None)
            if _cell is not None:
                neighbours.append(_cell)
        if cell.x + 1 < self.maze_size:
            _cell = next((c for c in self.visited_cells if c == Cell(cell.x + 1, cell.y)), None)
            if _cell is not None:
                neighbours.append(_cell)
        if cell.y - 1 >= 0:
            _cell = next((c for c in self.visited_cells if c == Cell(cell.x, cell.y - 1)), None)
            if _cell is not None:
                neighbours.append(_cell)
        if cell.y + 1 < self.maze_size:
            _cell = next((c for c in self.visited_cells if c == Cell(cell.x, cell.y + 1)), None)
            if _cell is not None:
                neighbours.append(_cell)

        return neighbours

    def __get_unvisited_neighbours(self, cell):
        neighbours = list()
        if cell.x - 1 >= 0:
            _cell = Cell(cell.x - 1, cell.y)
            if _cell not in self.visited_cells:
                neighbours.append(_cell)
        if cell.x + 1 < self.maze_size:
            _cell = Cell(cell.x + 1, cell.y)
            if _cell not in self.visited_cells:
                neighbours.append(_cell)
        if cell.y - 1 >= 0:
            _cell = Cell(cell.x, cell.y - 1)
            if _cell not in self.visited_cells:
                neighbours.append(_cell)
        if cell.y + 1 < self.maze_size:
            _cell = Cell(cell.x, cell.y + 1)
            if _cell not in self.visited_cells:
                neighbours.append(_cell)

        return neighbours

    def __connect(self, first_cell, second_cell):
        self.__draw_cell(first_cell, "white")
        self.__draw_cell(second_cell, "white")
        if first_cell.x == self.maze_size - 1 and first_cell.y == self.maze_size - 1:
            self.canvas.create_line(self.maze_size * self.cell_size + 2, (self.maze_size - 1) * self.cell_size + 3,
                                    self.maze_size * self.cell_size + 2, self.maze_size * self.cell_size + 2,
                                    fill="white")

        if first_cell.x == second_cell.x:
            if first_cell.y < second_cell.y:
                first_cell.down = second_cell
                second_cell.up = first_cell
                self.canvas.create_line(second_cell.x * self.cell_size + 3, second_cell.y * self.cell_size + 2,
                                        (second_cell.x + 1) * self.cell_size + 2, second_cell.y * self.cell_size + 2,
                                        fill="white")
            else:
                first_cell.up = second_cell
                second_cell.down = first_cell
                self.canvas.create_line(first_cell.x * self.cell_size + 3, first_cell.y * self.cell_size + 2,
                                        (first_cell.x + 1) * self.cell_size + 2, first_cell.y * self.cell_size + 2,
                                        fill="white")
        else:
            if first_cell.x < second_cell.x:
                first_cell.right = second_cell
                second_cell.left = first_cell
                self.canvas.create_line(second_cell.x * self.cell_size + 2, second_cell.y * self.cell_size + 3,
                                        second_cell.x * self.cell_size + 2, (second_cell.y + 1) * self.cell_size + 2,
                                        fill="white")
            else:
                first_cell.left = second_cell
                second_cell.right = first_cell
                self.canvas.create_line(first_cell.x * self.cell_size + 2, first_cell.y * self.cell_size + 3,
                                        first_cell.x * self.cell_size + 2, (first_cell.y + 1) * self.cell_size + 2,
                                        fill="white")
        self.canvas.update()

    def __show_path(self):
        self.show_path_button.config(state=DISABLED)
        self.path = list()
        self.__find_path(self.visited_cells[0])

        size = self.cell_size / 2 + 2
        line_size = self.cell_size / 3
        self.canvas.create_line(0, size, size, size, fill="red", width=line_size, capstyle=PROJECTING)
        for i in range(len(self.path) - 1):
            first_cell = self.path[i]
            second_cell = self.path[i + 1]
            self.canvas.create_line(first_cell.x * self.cell_size + size, first_cell.y * self.cell_size + size,
                                    second_cell.x * self.cell_size + size, second_cell.y * self.cell_size + size,
                                    fill="red", width=line_size, capstyle=PROJECTING)
        self.canvas.create_line((self.maze_size - 1) * self.cell_size + size,
                                (self.maze_size - 1) * self.cell_size + size, self.maze_size * self.cell_size + size,
                                (self.maze_size - 1) * self.cell_size + size, fill="red", width=line_size,
                                capstyle=PROJECTING)

    def __find_path(self, cell):
        if cell is not None and cell not in self.path:
            self.path.append(cell)
            if cell.x == self.maze_size - 1 and cell.y == self.maze_size - 1:
                return True

            if self.__find_path(cell.down):
                return True

            if self.__find_path(cell.right):
                return True

            if self.__find_path(cell.up):
                return True

            if self.__find_path(cell.left):
                return True

            self.path.remove(cell)
            return False
        else:
            return False


if __name__ == "__main__":
    MazeGenerator()
