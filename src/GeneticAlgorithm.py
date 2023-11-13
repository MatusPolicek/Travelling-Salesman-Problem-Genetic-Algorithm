import random
from math import sqrt
from random import randrange, random
import random


def shuffle_cities(cities_length):
    shuffled_cities = []
    shuffled_cities.extend(range(0, cities_length))
    random.shuffle(shuffled_cities)
    return shuffled_cities


class TSP:
    def __init__(self, gui):
        self.main_gui = gui

    def parse_args(self, args):
        self.TSP_cities = Cities(args['cities'])
        self.TSP_population = Population(self.TSP_cities, args['population_size'])
        self.TSP_breed = Breed(args['parent_method'], args['mutation_method'], 0.1)
        self.generations = args['generations']
        self.population_size = args['population_size']
        self.solve(args['simulate'])


    def solve(self, simulate):
        i = 0
        fitness_history = []
        while i < self.generations:
            # New population
            new_population = []

            if len(fitness_history) == 5:
                are_all_equal = all(x == fitness_history[0] for x in fitness_history)
                if are_all_equal:
                    if self.TSP_breed.mutation_rate < 0.5:
                        self.TSP_breed.mutation_rate += 0.05
                    fitness_history.clear()
                    # New blood
                    new_population.append(
                        Individual(shuffle_cities(self.TSP_cities.get_number_of_cities()), self.TSP_cities))
                else:
                    fitness_history.clear()
            # Elitism
            new_population.append(self.TSP_population.get_fittest())
            fitness_history.append(self.TSP_population.get_fittest().get_fitness())

            while len(new_population) < self.population_size:
                parents = self.TSP_breed.parent_choice_method(self.TSP_population)
                chromosome = self.TSP_breed.crossover(parents)
                self.TSP_breed.mutate(chromosome)
                is_unique = True
                for individual in new_population:
                    if individual.chromosome == chromosome:
                        is_unique = False
                        break
                if is_unique:
                    new_population.append(Individual(chromosome, self.TSP_cities))
            # Population replacement
            if simulate:
                self.main_gui.update_grid(self.TSP_population.get_fittest().chromosome)
            self.TSP_population.update_population(new_population)
            i += 1

        self.main_gui.update_grid(self.TSP_population.get_fittest().chromosome)



class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_distance(self, city):
        return sqrt((abs(self.x - city.x) ** 2) + abs(self.y - city.y) ** 2)


class CitiesGenerator:
    def __init__(self, number_of_cities):
        self.cities = set()
        while len(self.cities) < number_of_cities:
            x, y = randrange(20, 600), randrange(20, 500)
            new_city = City(x, y)
            if not any(
                    abs(new_city.get_x() - city.get_x()) <= 10 and abs(new_city.get_y() - city.get_y()) <= 10 for city
                    in self.cities):
                self.cities.add(new_city)

        self.cities = list(self.cities)

    def get_cities(self):
        return self.cities


class Cities:
    def __init__(self, number_of_cities):
        self.cities = None
        self.generate_cities(number_of_cities)

    def generate_cities(self, number_of_cities):
        generator = CitiesGenerator(number_of_cities)
        self.cities = generator.get_cities()

    def get_city(self, index):
        if self.cities is None:
            raise ValueError("Cities have not been generated yet.")
        return self.cities[index]

    def get_number_of_cities(self):
        if self.cities is None:
            raise ValueError("Cities have not been generated yet.")
        return len(self.cities)


class Individual:
    def __init__(self, chromosome, cities):
        self.chromosome = chromosome
        self.fitness = self.calculate_fitness(cities)

    def calculate_fitness(self, cities):
        total_distance = 0

        for i in range(0, len(self.chromosome) - 1):
            total_distance += cities.get_city(self.chromosome[i]).get_distance(cities.get_city(self.chromosome[i + 1]))
        total_distance += cities.get_city(self.chromosome[0]).get_distance(
            cities.get_city(self.chromosome[len(self.chromosome) - 1]))
        return total_distance

    def get_fitness(self):
        return self.fitness


class Population:
    def __init__(self, cities, population_size):
        unique_population = self.initialize_population(cities, population_size)
        self.population = [Individual(list(chromosome), cities) for chromosome in unique_population]

    def initialize_population(self, cities, population_size):
        unique_population = []
        while len(unique_population) < population_size:
            generated_chromosome = shuffle_cities(cities.get_number_of_cities())
            if generated_chromosome not in unique_population:
                unique_population.append(generated_chromosome)
        return unique_population

    def get_individual(self, index):
        return self.population[index]

    def update_population(self, individuals):
        self.population = list(individuals)

    def get_fittest(self):
        return min(self.population, key=lambda individual: individual.get_fitness())


class Breed:
    def __init__(self, parent_choice, mutation, mutation_rate):
        if parent_choice == "Roulette":
            self.parent_choice_method = self.roulette
        elif parent_choice == "Tournament":
            self.parent_choice_method = self.tournament
        elif parent_choice == "Rank selection":
            self.parent_choice_method = self.rank_selection
        elif parent_choice == "Combination":
            self.parent_choice_method = self.combination

        if mutation == "Swap":
            self.mutate = self.swap_mutation
        elif mutation == "Displacement":
            self.mutate = self.displacement_mutation

        self.mutation_rate = mutation_rate

    def roulette(self, population):
        fitness_sum = sum(individual.get_fitness() for individual in population.population)
        probabilities = [1 - (individual.get_fitness() / fitness_sum) for individual in population.population]
        total_prob = sum(probabilities)
        probabilities = [prob / total_prob for prob in probabilities]

        parents = []
        while len(parents) < 2:
            chance = random.uniform(0, total_prob)
            sum_prob = 0
            for index, probability in enumerate(probabilities, 0):
                sum_prob += probability
                if sum_prob >= chance:
                    is_unique = True
                    for parent in parents:
                        if parent.chromosome == population.get_individual(index).chromosome:
                            is_unique = False
                    if is_unique:
                        parents.append(population.get_individual(index))
                        break

        return parents

    def tournament(self, population, tournament_size=4):
        participants = random.sample(population.population, tournament_size)
        participants.sort(key=lambda x: x.get_fitness())
        parents = participants[:2]
        return parents

    def rank_selection(self, population):
        pop = sorted(population.population, key=lambda individual: individual.get_fitness())
        total_rank = sum((len(pop) - index) for index, _ in enumerate(pop))
        parents = []
        while len(parents) < 2:
            chance = random.uniform(0, total_rank)
            cumulative_prob = 0
            for index, individual in enumerate(pop):
                cumulative_prob += (len(pop) - index)
                if cumulative_prob >= chance:
                    is_unique = True
                    for parent in parents:
                        if parent.chromosome == individual.chromosome:
                            is_unique = False
                    if is_unique:
                        parents.append(individual)
                    break
        return parents

    def combination(self, population):
        parents = []
        parents.extend(self.roulette(population))
        parents.extend(self.tournament(population))
        parents.extend(self.roulette(population))
        random.shuffle(parents)

        parents = parents[0:2]

        return parents

    def crossover(self, parents):
        parent1, parent2 = parents
        num_cities = len(parent1.chromosome)
        child = [-1] * num_cities
        start, end = sorted(random.sample(range(num_cities), 2))

        child[start:end + 1] = parent1.chromosome[start:end + 1]
        remaining_cities = [city for city in parent2.chromosome if city not in child]
        remaining_index = 0
        for i in range(num_cities):
            if child[i] == -1:
                child[i] = remaining_cities[remaining_index]
                remaining_index += 1

        return child

    def swap_mutation(self, chromosome):
        if random.random() < self.mutation_rate:
            x, y = randrange(0, len(chromosome)), randrange(0, len(chromosome))
            while x == y:
                y = randrange(0, len(chromosome))

            temp = chromosome[x]
            chromosome[x] = chromosome[y]
            chromosome[y] = temp
        return chromosome

    def displacement_mutation(self, chromosome):
        if random.random() < self.mutation_rate:
            segment_start = random.randint(0, len(chromosome) - 4)
            segment_end = segment_start + random.choice([1, 3])

            insert_position = random.randint(0, len(chromosome) - (segment_end - segment_start + 1))

            segment = chromosome[segment_start:segment_end]
            del chromosome[segment_start:segment_end]
            chromosome[insert_position:insert_position] = segment
        return chromosome
