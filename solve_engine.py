# Tutaj bedzie nasz skrypcik pythonowy do przeprowadzenia algorytmu


import numpy as np
import dbconnector
import matplotlib.pyplot as plt

from typing import List, Tuple
import random
import copy

import nointernethelpers

incorrect_fitness = 100000


class Truck:
    def __init__(self, data, service: int):
        self.id = data[0]
        self.brand = data[1]
        self.model = data[2]
        self.burning = data[3]
        self.cargo = data[4]
        self.velocity = get_velocity(self.cargo)
        self.service = service

    def count_consumption(self, distance):
        return distance * self.burning / 100

    def __str__(self):
        return str(self.id) + " " + self.brand + " " + self.model + ", burning: " + str(
            self.burning) + ", cargo: " + str(self.cargo) + ", service: " + str(self.service)

    def __repr__(self):
        return str(self.id) + " " + self.brand + " " + self.model + " " + str(self.service)


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

        self.weight = int(self.weight.replace(' t', '')) * 1000


class Services:
    def __init__(self, services):
        self.services: List[SingleService] = []
        for service in services:
            self.services.append(SingleService(service))
        self.cities_connections = []
        city_helper = ["Warszawa"] + [service.city for service in self.services]
        all_connections = get_city_connections()
        for origin_city in city_helper:
            for destination_city in city_helper:
                if not origin_city == destination_city:
                    distance = all_connections[(origin_city, destination_city)]
                    self.cities_connections.append((origin_city, destination_city, distance))

    def get_service(self, city: str):
        for service in self.services:
            if service.city == city:
                return service

        raise ValueError


class Task:
    """
    parametry algorytmu
    """

    def __init__(self, parameters, trucks_length, connections_length, no_of_cities):
        self.population_size = parameters['population_size']
        self.selection_size = parameters['selection_size']
        self.crossover_rate = parameters['crossover_rate']
        self.mutation_rate = parameters['mutation_rate']
        self.pay_rate = parameters['pay_rate']
        self.visited_cities_limit = parameters['visited_cities_limit']
        self.no_of_cities_connections = connections_length
        self.no_of_cities = no_of_cities
        self.no_of_trucks = trucks_length
        self.genome_size = trucks_length + trucks_length * connections_length


class Genome:
    def __init__(self, genome, mutation_rate, length):
        self.mutation_rate = mutation_rate
        self.genome = genome
        self.fitness = incorrect_fitness
        self.trucks_length = length
        self.is_correct = True

    def __str__(self):
        return str(self.genome) + " fitness: " + str(self.fitness)

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
        if np.random.random_sample() < self.mutation_rate:
            index = np.random.randint(0, self.trucks_length, int(self.trucks_length * self.mutation_rate))
            if np.random.randint(1, 11) <= 6:
                for i in index:
                    toggle(i, self.genome)
            else:
                if self.genome[index[0]] == 0:
                    self.genome[index[0]] = 1
                change_service(index[0], trucks, trucks_limit)

    def check_correctness(self, task: Task, services: Services, trucks: List[Truck]):
        all_cities = []

        # sprawdzanie czy jest wyslana choc jedna ciezarowka
        if np.count_nonzero(self.genome[0:task.no_of_trucks]) == 0:
            self.is_correct = False
            return

        for i in range(task.no_of_trucks):
            if self.genome[i] == 0:
                continue

            start = task.no_of_trucks + i * task.no_of_cities_connections
            part_genome = self.genome[start:start + task.no_of_cities_connections]
            visited_cities = 0

            for j in range(task.no_of_cities_connections // task.no_of_cities):
                start_index = j * task.no_of_cities
                superposition = 0

                # sprawdzanie czy miastem poczatkowym jest warszawa i czy wyjezdza do jednego miasta
                if j == 0:
                    start_cities = np.count_nonzero(part_genome[0:task.no_of_cities])
                    if start_cities == 0 or start_cities > 1:
                        self.is_correct = False
                        return
                    continue

                for k in range(0, task.no_of_cities):
                    if part_genome[start_index + k] == 1:
                        visited_cities += 1
                        superposition += 1

                # sprawdzanie czy wyjezdza do wiecej niz 1 miasto jednoczesnie
                if superposition > 1:
                    self.is_correct = False
                    return

            # sprawdzanie czy odwiedza wiecej miast niz jest limit
            if visited_cities > task.visited_cities_limit + 1:
                self.is_correct = False
                return

            # budowanie trasy
            track, has_end, used_cities = build_track(part_genome, services)
            track = track.split('-')

            # sprawdzanie czy wraca do warszawy
            if not has_end:
                self.is_correct = False
                return

            # sprawdzanie czy odwiedza wszystkie miasta ktore ma w trasie
            if len(track) != used_cities:
                self.is_correct = False
                return

            # sprawdzanie czy przekracza dopuszczala pojemnosc
            current_weight = 0
            for j in range(1, len(track) - 1):
                city = track[j]
                all_cities.append(city)
                service = services.get_service(city)
                current_weight += service.weight

            if current_weight > trucks[i].cargo:
                self.is_correct = False
                return

        # sprawdzanie czy niepotrzebine puszcza jeszcze raz ciezarowke do miasta ktore zostalo odwiedzone
        # if len(all_cities) != task.no_of_cities:
        #     self.is_correct = False
        #     return

        print("Oporowo")
        return

    def evaluate(self, task: Task, services: Services, trucks: List[Truck]):
        if not self.is_correct:
            self.fitness = incorrect_fitness
            return self.fitness

        distances = get_distances(self.genome, task, services)

        total_evaluation = 0
        for i in range(task.no_of_trucks):
            if self.genome[i] == 0:
                continue
            truck = trucks[i]
            distance = distances[i]
            total_evaluation += (distance / truck.velocity) * (distance * truck.burning / 100 + task.pay_rate)

        self.fitness = total_evaluation
        if total_evaluation == 0:
            self.fitness = incorrect_fitness

        return self.fitness


class Population:
    def __init__(self, task: Task, create: bool = True):
        self.evaluation = None
        self.population = []
        self.selection_size = task.selection_size
        self.crossover_rate = task.crossover_rate
        self.no_of_trucks = task.no_of_trucks
        self.no_of_cities_connections = task.no_of_cities_connections
        self.no_of_cities = task.no_of_cities
        if create:
            genomes = generate_population(task)
            for gen in genomes:
                self.population.append(Genome(gen, task.mutation_rate, task.no_of_trucks))

    def __len__(self):
        return len(self.population)

    def selection(self, task: Task, services: Services, trucks: List[Truck]):
        tournaments = random.choices(self.population, k=self.selection_size)
        evaluations = [genome.evaluate(task, services, trucks) for genome in tournaments]
        index_best_genome = evaluations.index(min(evaluations))
        return tournaments[index_best_genome]

    def crossover(self, parent1: Genome, parent2: Genome):
        if np.random.random() < self.crossover_rate:
            temp1 = parent1.genome[0:self.no_of_trucks]
            temp2 = parent2.genome[0:self.no_of_trucks]
            if is_same(temp1, temp2):
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
                child1 = copy.deepcopy(parent1)
                child2 = copy.deepcopy(parent2)
                for i in range(0, self.no_of_trucks):
                    random_value = np.random.randint(0, self.no_of_cities_connections // self.no_of_cities, 2)
                    index = self.no_of_trucks + self.no_of_cities_connections * i
                    part_genome1 = child1.genome[index:index + self.no_of_cities_connections]
                    part_genome2 = child2.genome[index:index + self.no_of_cities_connections]
                    child1.genome[index:index + self.no_of_cities_connections] = toggle_part_genome(part_genome1,
                                                                                                    random_value[0],
                                                                                                    self.no_of_cities)
                    child2.genome[index:index + self.no_of_cities_connections] = toggle_part_genome(part_genome2,
                                                                                                    random_value[1],
                                                                                                    self.no_of_cities)

        else:
            child1 = parent1
            child2 = parent2

        return child1, child2

    def best_genome(self):
        best_genome_index = self.evaluation.index(min(self.evaluation))
        return self.population[best_genome_index]

    def evaluate(self, task: Task, services: Services, trucks: List[Truck]) -> List:
        self.evaluation = [genome.evaluate(task, services, trucks) for genome in self.population]
        return self.evaluation


class Solver:
    def __init__(self, algorythm_parameters, services):
        self.population = None
        self.services = Services(services)
        self.trucks: List[Truck] = []
        try:
            con = dbconnector.conncect_to_db()
            trucks_db = dbconnector.dbGetQuery(con, "SELECT * FROM trucks")
            dbconnector.close_connection(con)
        except dbconnector.OperationalError as e:
            print("Error: {}".format(e.pgerror))
            trucks_db = nointernethelpers.db_trucks

        for truck in trucks_db:
            self.trucks.append(Truck(truck, np.random.randint(1, len(trucks_db))))

        self.task = Task(algorythm_parameters, len(self.trucks), len(self.services.cities_connections), len(services))

    def fit(self, iterations):
        print("Zaczynam algorytm")
        self.population = Population(self.task)
        for genome in self.population.population:
            genome.check_correctness(self.task, self.services, self.trucks)

        best_evaluation_history = []  # historia najlepszej ewaluacji
        best_genome_history = []  # historia najlepszego genomu
        mean_evaluation_history = []  # historia sredniej ewaluacji
        the_best_genome = None  # najlepszy genom
        the_best_evaluation = incorrect_fitness  # najlepsza ewaluacja
        the_best_genome_population = []  # najlepszy genom w populacji

        for iteration in range(iterations):
            if (iteration + 1) % 10 == 0:
                print("Iteracja: {}".format(iteration + 1))

            new_population = Population(self.task, False)

            n = len(self.population) // 2
            for __ in range(n):
                parent1 = self.population.selection(self.task, self.services, self.trucks)
                parent2 = self.population.selection(self.task, self.services, self.trucks)
                child1, child2 = self.population.crossover(parent1, parent2)
                child1.check_correctness(self.task, self.services, self.trucks)
                child2.check_correctness(self.task, self.services, self.trucks)
                child1.mutate(self.trucks, self.task.no_of_trucks)
                child1.check_correctness(self.task, self.services, self.trucks)
                child2.mutate(self.trucks, self.task.no_of_trucks)
                child2.check_correctness(self.task, self.services, self.trucks)
                new_population.population.append(child1)
                new_population.population.append(child2)

            self.population.evaluate(self.task, self.services, self.trucks)
            best_genome = self.population.best_genome()

            if best_genome.fitness < the_best_evaluation:
                the_best_genome = best_genome
                the_best_evaluation = best_genome.fitness

            best_evaluation_history.append(the_best_evaluation)
            best_genome_history.append(the_best_genome)

            the_best_genome_population.append(best_genome.fitness)
            mean_evaluation_history.append(np.mean(self.population.evaluation))

            self.population = new_population

        generate_result(the_best_genome, self.trucks, self.services)

        return the_best_genome, best_evaluation_history, best_genome_history, mean_evaluation_history, \
            the_best_genome_population


def toggle(index, genome):
    if genome[index] == 1:
        genome[index] = 0
    else:
        genome[index] = 1


def toggle_part_genome(part_genome, index, no_of_cities):
    start = index * no_of_cities
    part_genome_city = part_genome[start:start + no_of_cities]
    ones = np.count_nonzero(part_genome_city)
    if ones == 1:
        for i in range(no_of_cities):
            part_genome[start + i] = 0
    elif ones == 0:
        new_index = np.random.randint(0, no_of_cities)
        part_genome[start + new_index] = 1
    else:
        print("To nie powinno miec miesjca")
        raise ValueError
    return part_genome


def change_service(index, trucks, trucks_limit):
    old_service = trucks[index].service
    new_service = np.random.randint(1, trucks_limit)

    while new_service == old_service:
        new_service = np.random.randint(1, trucks_limit, 1)

    trucks[index].service = new_service


def is_same(array1, array2) -> bool:
    for i in range(len(array1)):
        if array1[i] != array2[i]:
            return False
    return True


def build_track(array: np.ndarray, services: Services) -> Tuple[str, bool, int]:
    track = []
    has_end = False

    for i in range(len(array)):
        if array[i] == 1:
            track.append(services.cities_connections[i])

    result = "Warszawa"
    city = result
    for _ in range(len(track) + 10):
        for i in range(len(track)):
            if track[i][0] == city:
                result += '-' + track[i][1]
                city = track[i][1]
                break
        if city == "Warszawa":
            break

    if city == "Warszawa":
        has_end = True

    if result == city:
        has_end = False

    return result, has_end, len(track) + 1


def find_distance(origin_city, destination_city, city_connections: List):
    for i in range(len(city_connections)):
        if city_connections[i][0] == origin_city and city_connections[i][1] == destination_city:
            return city_connections[i][2]

    raise ValueError


def get_distances(genome, task: Task, services: Services):
    distances = []
    for i in range(task.no_of_trucks):
        if genome[i] == 0:
            distances.append(0)
            continue
        start = task.no_of_trucks + i * task.no_of_cities_connections
        track, _, _ = build_track(genome[start:start + task.no_of_cities_connections], services)
        track = track.split('-')

        distance = 0
        for j in range(len(track) - 1):
            origin_city = track[j]
            destination_city = track[j + 1]
            distance += find_distance(origin_city, destination_city, services.cities_connections)

        distances.append(distance)

    return distances


def generate_part_genome_city(task: Task):
    cities = []
    has_one = False
    for i in range(task.no_of_cities):
        if has_one:
            break

        value = np.random.random_sample()

        if value <= 0.75:
            cities.append(0)
        else:
            cities.append(1)
            has_one = True

    for i in range(task.no_of_cities - len(cities)):
        cities.append(0)

    return cities


def generate_part_genome(task: Task):
    part_genome = []
    for i in range(task.no_of_cities_connections // task.no_of_cities):
        part_genome_city = generate_part_genome_city(task)
        part_genome += part_genome_city

    return part_genome


def generate_population(task: Task):
    genomes = []
    for i in range(task.population_size):
        genome = []
        for j in range(task.no_of_trucks):
            value = np.random.random_sample()
            if value <= 0.35:
                genome.append(1)
            else:
                genome.append(0)

        for j in range((task.genome_size - task.no_of_trucks) // task.no_of_cities_connections):
            if genome[j] == 1:
                part_genome = generate_part_genome(task)
            else:
                part_genome = [0] * task.no_of_cities_connections
            genome += part_genome
        genomes.append(genome)

    return genomes


def get_velocity(cargo):
    if cargo < 1500:
        return 80
    elif cargo < 5000:
        return 75
    elif cargo < 18000:
        return 70
    else:
        return 60


def get_city_connections():
    city_connections = {}
    try:
        con = dbconnector.conncect_to_db()
        db_city_connections = dbconnector.dbGetQuery(con, "SELECT * FROM citiesconnections")
        dbconnector.close_connection(con)
    except dbconnector.OperationalError as e:
        print("Error: {}".format(e.pgerror))
        db_city_connections = nointernethelpers.db_city_connections

    for _, connection, distance in db_city_connections:
        connection = connection.split('-')
        city_connections[(connection[0], connection[1])] = distance

    return city_connections


def generate_result(genome: Genome, trucks: List[Truck], services: Services):
    service_code = 0
    result = {}
    for i in range(genome.trucks_length):
        helper = {}
        if genome.genome[i] == 0:
            continue
        truck = trucks[i]
        truck.service = service_code
        print("Wybrana ciezarówka: {}".format(truck))
        print("Polaczenia: ")
        for j in range(len(services.cities_connections)):
            index = genome.trucks_length + (i * len(services.cities_connections)) + j
            if genome.genome[index] == 1:
                print(services.cities_connections[j])
        print("Koniec kursu", end='\n\n')

        start = genome.trucks_length + i * len(services.cities_connections)
        track, _, _ = build_track(genome.genome[start:start + len(services.cities_connections)], services)
        helper['truck'] = str(truck)
        helper['route'] = track
        result[f'service-{service_code}'] = helper
        service_code += 1

    result['evaluation'] = str(genome.fitness)

    return result


def find_solution(services, parameters):
    solution = Solver(parameters, services)
    the_best_genome, best_evaluation_history, best_genome_history, mean_evaluation_history, the_best_genome_population \
        = solution.fit(parameters['iterations'])

    print(best_evaluation_history[-5:], sep='\n')
    print("Uzyte ciezarówki: ", np.count_nonzero(the_best_genome.genome[0:12]))
    plt.plot(best_evaluation_history)
    plt.plot(the_best_genome_population)
    plt.plot(mean_evaluation_history)
    plt.legend(["Najlepsze rozwiazanie", "Najlepsze rozwiazanie w populacji", "Srednia ocen w populacji"])
    plt.title("Raport przebiegu")
    plt.xlabel("Generacja")
    plt.ylabel("Ocena jakości")
    plt.grid(True)
    plt.savefig("images/raport.png")
    plt.show()
    print()


# ------------------
# Testowanie
test_data = [{'city': 'Rzeszów', 'products': ['cheese'], 'weight': '10 t', 'deadline': '7 days'},
             {'city': 'Gdynia', 'products': ['tomatoes'], 'weight': '15 t', 'deadline': '3 days'},
             {'city': 'Kraków', 'products': ['pepper'], 'weight': '5 t', 'deadline': '12 days'}]

test_parameters = {'population_size': 300, 'selection_size': 250, 'crossover_rate': 0.95, 'mutation_rate': 0.1,
                   'pay_rate': 5, 'visited_cities_limit': 2, 'iterations': 500}

find_solution(test_data, test_parameters)

# ------------------
# Nieuzywane
#
# def get_coordinates(city_name):
#     geolocator = Nominatim(user_agent="my_geocoder")
#     location = geolocator.geocode(city_name)
#
#     return location.latitude, location.longitude
#
#
# def get_osrm_distance(coordinates):
#     base_url = f"http://router.project-osrm.org/route/v1/car/"
#
#     formatted_coordinates = f"{coordinates[0][1]},{coordinates[0][0]};{coordinates[1][1]},{coordinates[1][0]}"
#
#     params = {
#         'alternatives': 'false',
#         'steps': 'false',
#         'geometries': 'geojson',
#     }
#
#     response = requests.get(base_url + formatted_coordinates, params=params)
#     data = response.json()
#     route_distance = data['routes'][0]['distance'] / 1000
#
#     return route_distance
#
#
# plt.plot(best_evaluation_history)
# plt.plot(the_best_genome_population)
# plt.title("Raport przebiegu 2")
# plt.legend(["Najlepsze rozwiazanie", "Najlepsze rozwiazanie w populacji"])
# plt.grid(True)
# plt.show()

Zwracanie = {
    'service-0': {'route': 'Warszawa', 'truck': '9 Daf XF 450, burning: 22, cargo: 13820, service: 0'},
    'service-1': {'route': 'Warszawa-Rzeszów-Warszawa',
                  'truck': '11 MAN TGX 18.480, burning: 32, cargo: 28000, service: 1'},
    'evaluation': '2407.640813651147'
}
