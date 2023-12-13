# Tutaj bedzie nasz skrypcik pythonowy do przeprowadzenia algorytmu

# bardzo skrotowy sugerowany przebieg
# 1. pobranie danych z bazy
# 2. wykonanie algorytmu
# 3. zworcenie danych (albo do bazy albo wstawic na stronke)

import numpy as np
import dbconnector
import matplotlib.pyplot as plt
from typing import List
import random


class Truck:
    def __init__(self, data, service: int):
        self.id = data[0]
        self.brand = data[1]
        self.model = data[2]
        self.burning = data[3]
        self.cargo = data[4]
        self.service = service

    def count_consumption(self, distance):
        return distance * self.burning / 100

    def __str__(self):
        return self.brand + " " + self.model + ", burning: " + str(self.burning) + ", cargo: " + str(
            self.cargo) + ", service: " + str(self.service)

    def __repr__(self):
        return str(self.id) + " " + self.brand + " " + self.model + " " + str(self.service)


class Task:
    """
    parametry algorytmu
    """

    # fixme te parametry mozna ustawiac w aplikacji (na stronce)
    def __init__(self, trucks_length, connections_length):
        self.population_size = 50
        self.selection_size = 15
        self.crossover_rate = 0.95
        self.mutation_rate = 0.001
        self.pay_rate = 5
        self.trucks_limit = 2
        self.visited_cities_limit = 3
        self.no_of_cities_connections = connections_length
        self.no_of_trucks = trucks_length
        self.genome_size = trucks_length + trucks_length * connections_length


class Genome:
    def __init__(self, genome, mutation_rate, length):
        self.mutation_rate = mutation_rate
        self.genome = genome
        self.fitness = 0
        self.trucks_length = length

    def __len__(self):
        return len(self.genome)

    def __getitem__(self, item):
        return self.genome[item]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.genome):
            self.index += 1
            return self.genome[self.index - 1]

        raise StopIteration

    def mutate(self, trucks: List[Truck], trucks_limit):
        index = np.random.randint(1, self.trucks_length - 1, int(np.ceil(self.trucks_length * self.mutation_rate)))
        if np.random.randint(1, 10) <= 6:
            for i in index:
                toggle(i, self.genome)
        else:
            if self.genome[index[0]] == 0:
                self.genome[index[0]] = 1
            change_service(index[0], trucks, trucks_limit)

    def evaluate(self):
        # todo sprawdzanie jakosci osobnika, sprawdzanie ograniczen oraz przypisywanie dopaaowania 0 albo karanie
        raise NotImplementedError


class Population:
    def __init__(self, task: Task):
        self.population = []
        self.selection_size = task.selection_size
        self.crossover_rate = task.crossover_rate
        self.no_of_trucks = task.no_of_trucks
        self.no_of_cities_connections = task.no_of_cities_connections
        genomes = np.random.choice([0, 1], size=(task.population_size, task.genome_size))
        for genome in genomes:
            self.population.append(Genome(genome, task.mutation_rate, task.no_of_trucks))

    def selection(self):
        # todo czy usuwac osobnika jak nie spelnia ograniczen
        # losowac osobniki z calej populacji i dla nich przeprowadzic truniej
        # czy przeprowadzic turniej dla calej populacji
        # mozna tez wybierac kilka najlepszych osobnikow i ich rozmnazac
        tournaments = random.choices(self.population, k=self.selection_size)
        evaluations = [genome.evaluate() for genome in tournaments]
        index_best_genome = evaluations.index(max(evaluations))
        return tournaments[index_best_genome]

    def crossover(self, parent1: Genome, parent2: Genome):
        # obecnie dziala to na zasdzie wymiany polowy genow, mozna dodac nowe metody np do wymiany czesci genotypu
        if np.random.random() < self.crossover_rate:
            if parent1[0:self.no_of_trucks] == parent2[0:self.no_of_trucks]:
                child1_genome = parent1[0:self.no_of_trucks]
                child2_genome = parent2[0:self.no_of_trucks]
                child_helper1 = []
                child_helper2 = []
                for truck_index in range(self.no_of_trucks):
                    split_min = self.no_of_trucks + self.no_of_cities_connections * truck_index
                    split_point = split_min + int(self.no_of_cities_connections / 2)
                    split_max = split_min + self.no_of_cities_connections
                    child_helper1 = np.concatenate(
                        (child_helper1, parent1[split_min:split_point], parent2[split_point:split_max]))
                    child_helper2 = np.concatenate(
                        (child_helper2, parent1[split_point:split_max], parent2[split_min:split_point]))
                child1_genome = np.concatenate((child1_genome, child_helper1))
                child2_genome = np.concatenate((child2_genome, child_helper2))
                child1 = Genome(child1_genome, parent1.mutation_rate, parent1.trucks_length)
                child2 = Genome(child2_genome, parent2.mutation_rate, parent2.trucks_length)
            else:
                # todo przemyslec jeszcze czy zwracac tu tylko rodzicow czy cos innego
                # todo mozna by modyfikowac trase, mutujac ja
                raise NotImplementedError
        else:
            child1 = parent1
            child2 = parent2

        return child1, child2


class SingleService:
    def __init__(self, data):
        self.city = data['city']
        self.products = data['products']
        self.weight: str = data['weight']
        if data['deadline'] == 0:
            self.deadline = None
        else:
            self.deadline = data['deadline']
            self.deadline = int(self.deadline.replace(' days', ''))

        self.weight = int(self.weight.replace(' t', ''))


class Services:
    def __init__(self, services):
        self.services: List[SingleService] = []
        for service in services:
            self.services.append(SingleService(service))
        self.cities_connections = []
        city_helper = ["Warszawa"] + [service.city for service in self.services]
        for origin_city in city_helper:
            for destination_city in city_helper:
                if not origin_city == destination_city:
                    self.cities_connections.append((origin_city, destination_city))


def toggle(index, genome):
    if genome[index] == 1:
        genome[index] = 0
    else:
        genome[index] = 1


def change_service(index, trucks, trucks_limit):
    old_service = trucks[index].service
    new_service = np.random.randint(1, trucks_limit)
    while new_service == old_service:
        new_service = np.random.random_integers(1, trucks_limit, 1)
    trucks[index].service = new_service


def find_solution(services):
    # ustawianie polaczenia z baza oraz pobranie listy ciezarowek oraz produktow
    con = dbconnector.conncect_to_db()
    trucks_data = dbconnector.dbGetQuery(con, "SELECT * FROM trucks")
    trucks = []
    for truck in trucks_data:
        trucks.append(Truck(truck, 0))

    temp_data = [{'city': 'Rzeszów', 'products': ['cheese'], 'weight': '10 t', 'deadline': '7 days'},
                 {'city': 'Gdynia', 'products': ['tomatoes'], 'weight': '50 t', 'deadline': '3 days'},
                 {'city': 'Wrocław', 'products': ['pepper'], 'weight': '5 t', 'deadline': '12 days'}]

    myservices = Services(temp_data)
    task = Task(len(trucks), len(myservices.cities_connections))
    population = Population(task)

    for index in range(len(trucks) + len(myservices.cities_connections)):
        if population.population[0][index] == 1:
            if index < len(trucks):
                print(trucks[index])
            else:
                print(myservices.cities_connections[index - len(trucks)])

    dbconnector.close_connection(con)


find_solution(None)

# ------------------
# SZYBKIE TESTY

temp = Population(Task(2, 4))

t1, t2 = temp.crossover(Genome([1, 1, 1, 0, 0, 1, 1, 1, 0, 0], 0.01, 2),
                        Genome([1, 0, 0, 1, 1, 0, 0, 0, 1, 1], 0.01, 2))

t3 = temp.selection()
print("IDK")
