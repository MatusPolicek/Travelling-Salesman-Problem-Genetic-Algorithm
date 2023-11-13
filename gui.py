import tkinter as tk
from random import randrange
import GeneticAlgorithm


class MainGui:
    def __init__(self, root):
        self.root_canvases = []
        self.root = root
        self.tsp = GeneticAlgorithm.TSP(self)
        self.init_window(self.root)
        self.create_canvases()

    def init_window(self, window):
        self.screen_width = window.winfo_screenwidth()
        self.screen_height = window.winfo_screenheight()
        self.window_width = int(0.75 * self.screen_width)
        self.window_height = int(0.75 * self.screen_height)
        window.geometry(
            f"{self.window_width}x{self.window_height}+{int((self.screen_width - self.window_width) / 2)}+{int((self.screen_height - self.window_height) / 2)}")
        window.title("Travelling Salesman Problem in Genetic Algorithm")

    def update_grid(self, individual):
        for canvas in self.root_canvases:
            if canvas['canvas_type'] == 'grid':
                self.create_visual_grid(canvas['canvas'], individual)

    def create_canvases(self):
        grid = tk.Canvas(self.root, width=self.window_width / 8 * 5, height=self.window_height, bg='white')
        self.create_visual_grid(grid)
        info = tk.Canvas(self.root, width=self.window_width / 8 * 3, height=self.window_height, bg='white')
        self.create_interactive_menu(info)
        grid.pack(side="left", expand=True)
        info.pack(side="right", expand=True)

        self.root_canvases.append({
            'canvas': grid,
            'canvas_type': 'grid',
        })
        self.root_canvases.append({
            'canvas': info,
            'canvas_type': 'info'
        })

    def create_interactive_menu(self, canvas):
        canvas.delete("all")

        settings = tk.Label(canvas, text="Genetic Algorithm settings", font=("Arial", 12), bg='white')
        settings.place(x=self.window_width / 8 * 3 / 2 - 100, y=25)

        self.generations_field = tk.Entry(canvas, width=8, fg='black', bg='white')
        self.generations_field.place(x=50, y=100)
        self.generations_field.insert(0, 500)
        generations_label = tk.Label(canvas, text="Number of generations", font=("Arial", 10), bg='white')
        generations_label.place(x=125, y=95)

        self.number_of_cities_field = tk.Entry(canvas, width=8, fg='black', bg='white')
        self.number_of_cities_field.place(x=50, y=150)
        self.number_of_cities_field.insert(0, randrange(20, 40))
        number_of_cities_label = tk.Label(canvas, text="Number of cities", font=("Arial", 10), bg='white')
        number_of_cities_label.place(x=125, y=145)

        self.number_of_population_field = tk.Entry(canvas, width=8, fg='black', bg='white')
        self.number_of_population_field.place(x=50, y=200)
        self.number_of_population_field.insert(0, 20)
        number_of_population_label = tk.Label(canvas, text="Max size of population", font=("Arial", 10), bg='white')
        number_of_population_label.place(x=125, y=195)

        parent_choice = ["Roulette", "Tournament", "Rank selection", "Combination"]
        self.parent_choice_var = tk.StringVar(value=parent_choice[0])
        parent_dropdown = tk.OptionMenu(canvas, self.parent_choice_var, *parent_choice)
        parent_dropdown.place(x=50, y=250)
        parent_choice_label = tk.Label(canvas, text="Parent choice method", font=("Arial", 10), bg='white')
        parent_choice_label.place(x=200, y=250)

        mutation_choice = ["Swap", "Displacement"]
        self.mutation_choice_var = tk.StringVar(value=mutation_choice[0])
        mutation_dropdown = tk.OptionMenu(canvas, self.mutation_choice_var, *mutation_choice)
        mutation_dropdown.place(x=50, y=300)
        mutation_choice_label = tk.Label(canvas, text="Mutation method", font=("Arial", 10), bg='white')
        mutation_choice_label.place(x=200, y=300)

        self.simulate = tk.IntVar()
        check_simulate = tk.Checkbutton(canvas, text="Show simulation", variable=self.simulate, bg='white', fg='black')
        check_simulate.place(x=50, y=350)

        solve_button = tk.Button(canvas, text="Solve", font=("Arial", 12), fg='black', bg='white',
                                 command=lambda: self.parse_args())

        solve_button.place(x=150, y=425)
        test_button.place(x=250, y=425)

    def create_visual_grid(self, canvas, individual=None):
        canvas.delete("all")

        offset = 50
        graph_color = 'black'
        canvas.create_line(offset, offset, (self.window_width / 8 * 5) - offset, offset, fill=graph_color, width=3)
        canvas.create_line(offset, offset, offset, self.window_height - offset, fill=graph_color, width=3)
        canvas.create_line(offset, self.window_height - offset, (self.window_width / 8 * 5 - offset),
                           self.window_height - offset, fill=graph_color, width=3)
        canvas.create_line((self.window_width / 8 * 5) - offset, self.window_height - offset,
                           (self.window_width / 8 * 5) - offset, offset, fill=graph_color, width=3)
        grid_width_offset = ((self.window_width / 8 * 5) - (offset * 2)) / 20
        grid_height_offset = (self.window_height - (offset * 2)) / 20

        grid_color = 'grey'
        for _ in range(1, 20):
            canvas.create_line(offset + (grid_width_offset * _), self.window_height - offset,
                               offset + (grid_width_offset * _), offset, fill=grid_color, width=0.5)
            canvas.create_line(offset, offset + (grid_height_offset * _), (self.window_width / 8 * 5) - offset,
                               offset + (grid_height_offset * _), fill=grid_color, width=0.5)

        if individual is not None:
            for city in self.tsp.TSP_cities.cities:
                canvas.create_oval(city.get_x() - 3 + offset, city.get_y() - 3 + offset, city.get_x() + 3 + offset,
                                   city.get_y() + 3 + offset, width=2, fill='blue')
            for index in range(0, len(individual) - 1):
                canvas.create_line(self.tsp.TSP_cities.get_city(individual[index]).get_x() + offset,
                                   self.tsp.TSP_cities.get_city(individual[index]).get_y() + offset,
                                   self.tsp.TSP_cities.get_city(individual[index + 1]).get_x() + offset,
                                   self.tsp.TSP_cities.get_city(individual[index + 1]).get_y() + offset, width=2,
                                   fill='red')
            canvas.create_line(self.tsp.TSP_cities.get_city(individual[0]).get_x() + offset,
                               self.tsp.TSP_cities.get_city(individual[0]).get_y() + offset,
                               self.tsp.TSP_cities.get_city(individual[len(individual) - 1]).get_x() + offset,
                               self.tsp.TSP_cities.get_city(individual[len(individual) - 1]).get_y() + offset, width=2,
                               fill='red')

        canvas.pack(side="left", expand=True)
        self.root.update()

    def parse_args(self):
        number_of_generations = self.generations_field.get()
        number_of_cities = self.number_of_cities_field.get()
        population_size = self.number_of_population_field.get()
        simulation = True if self.simulate.get() == 1 else False

        parent_choice = self.parent_choice_var.get()
        mutation_type = self.mutation_choice_var.get()

        if not number_of_generations:
            number_of_generations = 500
        else:
            number_of_generations = int(self.generations_field.get())

        if not number_of_cities:
            number_of_cities = randrange(20, 40)
        else:
            number_of_cities = int(self.number_of_cities_field.get())

        if not population_size:
            population_size = 20
        else:
            population_size = int(self.number_of_population_field.get())

        self.tsp.parse_args({
            'generations': number_of_generations,
            'cities': number_of_cities,
            'population_size': population_size,
            'parent_method': parent_choice,
            'mutation_method': mutation_type,
            'simulate': simulation,
            'testing': False
        })