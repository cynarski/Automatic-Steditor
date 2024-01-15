# skrypcik pythonowy do przeprowadzenia algorytmu
import numpy as np
import matplotlib.pyplot as plt

from typing import List, Tuple, Dict, Union
import random
import copy

import dbconnector
import nointernethelpers

# fixme to musi byc inaczej liczone albo jako inf czy nan
incorrect_fitness = 30000  # niepoprawna wartosc dopasowania


class Truck:
    """
    Klasa reprezentujaca pojedyncza ciezarowke
    """

    def __init__(self, data: List):
        """
        Klasa reprezentujaca pojedyncza ciezarowke
        :param data: dane pobrane z bazy danych przewoujace parametry ciezarowki
        """
        self.id = data[0]  # id ciezarowki
        self.brand = data[1]  # marka
        self.model = data[2]  # model
        self.burning = data[3]  # spalanie na 100 km
        self.cargo = data[4]  # ladownosc
        self.velocity = get_velocity(self.cargo)  # srednia predkosc

    def __str__(self):
        return str(self.id) + " " + self.brand + " " + self.model + ", burning: " + str(
            self.burning) + ", cargo: " + str(self.cargo)

    def __repr__(self):
        return str(self.id) + " " + self.brand + " " + self.model


class SingleService:
    """
    Klasa reprezentuja pojeddynczy kurs (zamownienie)
    """

    def __init__(self, data: Dict):
        """
        Klasa reprezentuja pojeddynczy kurs (zamownienie)
        :param data: dane pobrane z js
        """
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
    """
    Klasa przechowujaca informacje o wszystkich zamowieniach
    """

    def __init__(self, services: Dict):
        """
        Klasa przechowujaca informacje o wszystkich zamowieniach
        :param services: lista wszystkich zamowien
        """
        self.services: List[SingleService] = []

        for service in services:
            self.services.append(SingleService(service))

        self.cities_connections = []

        city_helper = ["Warszawa"] + [service.city for service in self.services]
        all_connections = get_city_connections()  # pobranie z bazy danych wszytkich polaczen

        for origin_city in city_helper:
            for destination_city in city_helper:
                if not origin_city == destination_city:
                    distance = all_connections[
                        (origin_city, destination_city)]  # znajdowanie odpowiedniego dystansu pomiedzy miastami
                    self.cities_connections.append((origin_city, destination_city, distance))

    def get_service(self, city: str) -> SingleService:
        """
        Metoda zwracajaca szukane na podstaiwe miasta pojedyncze zamowienie
        :param city: miasto
        :return: obiekt klasy SingleService
        """
        for service in self.services:
            if service.city == city:
                return service

        raise ValueError


class Task:
    """
    Klasa przechowujaca parametry algorytmu oraz wartosci ograniczen
    """

    def __init__(self, parameters: Dict, trucks_length: int, connections_length: int, no_of_cities: int):
        """
        Klasa przechowujaca parametry algorytmu oraz wartosci ograniczen
        :param parameters: parametry algorytmu
        :param trucks_length: ilosc wszystkich ciezarowek
        :param connections_length: ilosc wszystkich polaczen miedzy miastami
        :param no_of_cities: ilosc miast jakie nalezy odwiedzic (wynika to z ilosci zamowien)
        """
        self.population_size = parameters['population_size']  # rozmiar populacji
        self.selection_size = parameters['selection_size']  # rozmiar selekcji
        self.crossover_rate = parameters['crossover_rate']  # prawdopodobienstwo krzyzowania
        self.mutation_rate = parameters['mutation_rate']  # prawdopodoobienstwo mutowania
        self.pay_rate = parameters['pay_rate']  # stawka za godzine jazdy
        self.visited_cities_limit = parameters['visited_cities_limit']  # maksymalna liczba odwiedzonych miast
        self.no_of_cities_connections = connections_length
        self.no_of_cities = no_of_cities
        self.no_of_trucks = trucks_length
        self.genome_size = trucks_length + trucks_length * connections_length  # rozmiar rozwiazania (genomu)


class Genome:
    """
    Klasa reprezentujaca rozwiazanie
    """

    def __init__(self, genome: Union[np.ndarray, List], mutation_rate: float, no_of_trucks: int):
        """
        Klasa reprezentujaca rozwiazanie
        :param genome: wektor binarny
        :param mutation_rate: prawdopodobienstwo mutacji
        :param no_of_trucks: liczba wszystkich ciezarowek
        """
        self.mutation_rate = mutation_rate
        self.genome = genome
        self.fitness = incorrect_fitness  # ocena (dopasowanie) rozwiazania
        self.no_of_trucks = no_of_trucks
        self.is_correct = True  # flaga czy rozwiazanie jest dopuszczalne

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

    def mutate(self, task: Task):
        """
        Operator mutowania
        :param task: Obiekt klasy Task
        """
        # sprawdzanie warunku mutowania
        if np.random.random_sample() < self.mutation_rate:
            # losowanie liczby z zakresu 0 - no_of_trucks
            index = np.random.randint(0, self.no_of_trucks - 1)

            # aktywacja/dezaktywacja wylosowanej ciezarowki
            toggle(index, self.genome)

            start_index = self.no_of_trucks + index * task.no_of_cities_connections
            if self.genome[index] == 1:
                # generowanie trasy dla aktywowanej ciezarowki
                self.genome[start_index:start_index + task.no_of_cities_connections] = generate_part_genome(task)
            else:
                # zerowanie trasy dla dezaktywowanej ciezarowki
                self.genome[start_index:start_index + task.no_of_cities_connections] = \
                    np.repeat(0, task.no_of_cities_connections)

    def check_correctness(self, task: Task, services: Services, trucks: List[Truck]) -> None:
        """
        Metoda sprawdza poprawnosc rozwiazania
        :param task: obiekt klasy Task
        :param services: obiekt klast Services
        :param trucks: lista obiektow klasy Truck
        :return: None
        """

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
                        superposition += 1

                # sprawdzanie czy wyjezdza do wiecej niz 1 miasto jednoczesnie
                if superposition > 1:
                    self.is_correct = False
                    return

            # budowanie trasy
            track, has_end, used_cities = build_track(part_genome, services)
            track = track.split('-')

            # sprawdzanie czy wraca do warszawy
            if not has_end:
                self.is_correct = False
                return

            # sprawdzanie czy nie odwiedza wiecej miast niz jest limit
            if len(track) - 2 > task.visited_cities_limit:
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

        # fixme to ograniczenie jest lekko popsute albo mega trudno znalezc dopuszczalne rozwiazanie
        # sprawdzanie czy niepotrzebine puszcza jeszcze raz ciezarowke do miasta ktore zostalo odwiedzone
        if len(all_cities) <= int(task.no_of_cities / 2) + 1:
            self.is_correct = False
            return

        self.is_correct = True
        return

    def evaluate(self, task: Task, services: Services, trucks: List[Truck]) -> float:
        """
        Funckja oceny rozwiazania
        :param task: obiekt klasy Task
        :param services: obiekt klasy Services
        :param trucks: lista obiektow klasy Truck
        :return: ocena (dopasowanie) rozwiazania
        """

        # sprawdzanie czy rozwaizanie jest dopuszczlane
        if not self.is_correct:
            self.fitness = incorrect_fitness
            return self.fitness

        # stworzenie list z calkowita droga dla danej ciezarowki
        distances = get_distances(self.genome, task, services)

        # obliczanie oceny
        total_evaluation = 0
        for i in range(task.no_of_trucks):
            if self.genome[i] == 0:
                continue
            truck = trucks[i]
            distance = distances[i]
            total_evaluation += (distance / truck.velocity) * (
                    distance * truck.burning / 100 + task.pay_rate) + 0.25 * truck.cargo

        self.fitness = total_evaluation

        # sprawdzanie czy nie zaszedl blad
        # fixme w przyszlosci usunac
        if total_evaluation == 0:
            self.fitness = incorrect_fitness

        return self.fitness


class Population:
    """
    Klasa reprezentujaca populacje osobnikow (zbior rozwiazan)
    """

    def __init__(self, task: Task, create: bool = True):
        """
        Klasa reprezentujaca populacje osobnikow (zbior rozwiazan)
        :param task: obiekt klasy Task
        :param create: czy stworzyc populacje poczatkowa
        """
        self.evaluations = None  # lista ocen wszystkch rozwizan
        self.population = []  # populacja
        self.selection_size = task.selection_size
        self.crossover_rate = task.crossover_rate
        self.no_of_trucks = task.no_of_trucks
        self.no_of_cities_connections = task.no_of_cities_connections
        self.no_of_cities = task.no_of_cities

        # tworzenie populacji poczatkowej
        if create:
            genomes = generate_population(task)
            for gen in genomes:
                self.population.append(Genome(gen, task.mutation_rate, task.no_of_trucks))

    def __len__(self):
        return len(self.population)

    def selection(self, task: Task, services: Services, trucks: List[Truck]) -> Genome:
        """
        Operator selekcji (metoda turniejowa)
        :param task: obiekt klasy Task
        :param services: obiekt klasy Services
        :param trucks: lista obiektow klasy Truck
        :return: najlepsze rozwiazanie (obiekt klasy Genome)
        """
        # stworzenie listy turniejowej (wybor losowy)
        tournaments = random.choices(self.population, k=self.selection_size)

        # ocena kazdego rozwiazania w turnieju
        evaluations = [genome.evaluate(task, services, trucks) for genome in tournaments]

        # indeks najlepszego rozwiazania
        index_best_genome = evaluations.index(min(evaluations))

        return tournaments[index_best_genome]

    def crossover(self, parent1: Genome, parent2: Genome) -> Tuple[Genome, Genome]:
        """
        Operator krzyzowania
        :param parent1: pierwsze rozwiazanie (pierwszy rodzic)
        :param parent2: drugie rozwiazanie (drugi rodzic)
        :return: 2 nowe rozwiazania (para potomkow) (krotka 2-elementowa obiektu Genome)
        """
        # sprawdzanie warunku krzyzowania
        if np.random.random() <= self.crossover_rate:
            # pobranie listy wybranych ciezarowek dla pierwszego i drugiego rodzica
            trucks1 = parent1.genome[0:self.no_of_trucks]
            trucks2 = parent2.genome[0:self.no_of_trucks]

            # sprawdzanie czy sa aktywne te same ciezarowki
            if is_same(trucks1, trucks2):
                child1_genome = parent1[0:self.no_of_trucks]
                child2_genome = parent2[0:self.no_of_trucks]
                child_helper1 = []
                child_helper2 = []

                # rodzielanie tras na pol i przypisywanie do nowych potomkow
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
                child1 = Genome(child1_genome, parent1.mutation_rate, parent1.no_of_trucks)
                child2 = Genome(child2_genome, parent2.mutation_rate, parent2.no_of_trucks)
            else:
                # tworzenie kopii rodzicow
                child1 = copy.deepcopy(parent1)
                child2 = copy.deepcopy(parent2)

                # losowanie miasta ktore nalezy dodac do/usunac z trasy
                random_value = np.random.randint(0, self.no_of_cities_connections // self.no_of_cities, 2)

                try:
                    # wybieranie ciezarowki na podstawie aktywnych ciezarowek pierwszego rodzica
                    truck_index = choose_truck(parent1.genome, self.no_of_trucks)
                    index = self.no_of_trucks + self.no_of_cities_connections * truck_index
                    part_genome1 = child1.genome[index:index + self.no_of_cities_connections]

                    # dodawanie/usuwanie miasta do/z trasy pierwszego potomka
                    child1.genome[index:index + self.no_of_cities_connections] = \
                        toggle_part_genome(part_genome1, random_value[0], self.no_of_cities)
                except ValueError:
                    # lekkie zabezpieczenie przed sytuacja kiedy nie jest aktywna zadna ciezarowka
                    print(end='')  # nic nie ma robic

                try:
                    # wybieranie ciezarowki na podstawie aktywnych ciezarowek drugiego rodzica
                    truck_index = choose_truck(parent2.genome, self.no_of_trucks)
                    index = self.no_of_trucks + self.no_of_cities_connections * truck_index
                    part_genome2 = child2.genome[index:index + self.no_of_cities_connections]

                    # dodawanie/usuwanie miasta do/z trasy drugiego potomka
                    child2.genome[index:index + self.no_of_cities_connections] = \
                        toggle_part_genome(part_genome2, random_value[1], self.no_of_cities)
                except ValueError:
                    # lekkie zabezpieczenie przed sytuacja kiedy nie jest aktywna zadna ciezarowka
                    print(end='')  # nic nie ma robic

        else:
            # przypisanie tych samych rozwiazan
            child1 = parent1
            child2 = parent2

        return child1, child2

    def best_genome(self) -> Union[Genome, List[Genome]]:
        """
        Metoda zwracajace najlepsze rozwiazanie
        :return: najlepsze rozwiazanie
        """
        best_genome_index = self.evaluations.index(min(self.evaluations))
        return self.population[best_genome_index]

    def evaluate(self, task: Task, services: Services, trucks: List[Truck]) -> List[float]:
        """
        Metoda przeprowadza ocene dla kazdego rozwiazania w populacji
        :param task: obiekt klasy Task
        :param services: obiekt klasy Service
        :param trucks: lista obiektow klasy Truck
        :return: lista ocen kazdego rozwiazania w populacji
        """
        self.evaluations = [genome.evaluate(task, services, trucks) for genome in self.population]
        return self.evaluations


class Solver:
    """
    Klasa w ktorej jest przeprowadzany algorytm
    """

    def __init__(self, algorythm_parameters: Dict, services: Dict):
        """
        Klasa w ktorej jest przeprowadzany algorytm
        :param algorythm_parameters: parametry algorytmu
        :param services: wszystkie zamowienia
        """
        self.population = None
        self.services = Services(services)
        self.trucks: List[Truck] = []

        # pobieranie infomracji na temat wszystkich ciezarowek z bazy danych
        try:
            con = dbconnector.conncect_to_db()
            trucks_db = dbconnector.dbGetQuery(con, "SELECT * FROM trucks")
            dbconnector.close_connection(con)
        except dbconnector.OperationalError as e:
            print(f"Error: No internet connection {e.pgerror}")
            trucks_db = nointernethelpers.db_trucks

        for truck_params in trucks_db:
            self.trucks.append(Truck(truck_params))

        self.task = Task(algorythm_parameters, len(self.trucks), len(self.services.cities_connections), len(services))

    def fit(self, iterations: int) -> Dict:
        """
        Przebieg algorytmu
        :param iterations: liczba iteracji (generacji)
        :return:
        """
        print("Zaczynam algorytm")
        # towrzenie populacji poczatkowej
        self.population = Population(self.task)
        for genome in self.population.population:
            # sprawdzanie poprawnosci rozwiazania
            genome.check_correctness(self.task, self.services, self.trucks)

        best_evaluation_history = []  # historia najlepszej ewaluacji
        best_genome_history = []  # historia najlepszego genomu
        mean_evaluation_history = []  # historia sredniej ewaluacji
        the_best_genome = None  # najlepszy genom
        the_best_evaluation = incorrect_fitness  # najlepsza ewaluacja
        the_best_genome_population = []  # najlepszy genom w populacji
        best_counter = 0  # zliczanie przez ile generacji dany genom (rozwiazanie) jest najlepszy

        # glowna petla algorytmu
        for iteration in range(iterations):
            # sprawdzanie czy nowe najlepsze rozwiazanie jest takie samo jak stare
            if iteration > 1 and best_genome_history[iteration - 1] is best_genome_history[iteration - 2]:
                best_counter += 1

            if (iteration + 1) % 25 == 0:
                print("Iteracja: {}".format(iteration + 1))

            # mechanizm dywersyfikacji (jezeli nie znajduje lepszego rozwiazanie przez 25% iteracji to
            # generuje na nowo populacje)
            if best_counter >= int(iterations * 0.25):
                best_counter = 0
                new_population = Population(self.task)
                self.population = new_population
                for genome in self.population.population:
                    genome.check_correctness(self.task, self.services, self.trucks)
            else:
                # przyszla populacja
                new_population = Population(self.task, False)

                # zapelnianie populacji
                n = len(self.population) // 2
                for population_iter in range(n):
                    # mechanizm elitaryzmu
                    if population_iter < 3:
                        # wybieranie najlepszego rozwiazania w populacji i dodawnaie do nowej populacji
                        parent1 = self.population.selection(self.task, self.services, self.trucks)
                        parent2 = self.population.selection(self.task, self.services, self.trucks)
                        new_population.population.append(parent1)
                        new_population.population.append(parent2)
                    else:
                        # wybieranie poprzez selekcje najlepszych rodzicow
                        parent1 = self.population.selection(self.task, self.services, self.trucks)
                        parent2 = self.population.selection(self.task, self.services, self.trucks)

                        # krzyzowanie na podstawie wybranych rodzicow
                        child1, child2 = self.population.crossover(parent1, parent2)

                        # sprawdzanie poprawnosci nowo uzyskanych potomkow
                        child1.check_correctness(self.task, self.services, self.trucks)
                        child2.check_correctness(self.task, self.services, self.trucks)

                        # mutowanie a nastepnie sprawdzanie poprwanosci potomkow
                        child1.mutate(self.task)
                        child1.check_correctness(self.task, self.services, self.trucks)
                        child2.mutate(self.task)
                        child2.check_correctness(self.task, self.services, self.trucks)

                        # dodanie do populacji nowych potomkow
                        new_population.population.append(child1)
                        new_population.population.append(child2)

            # przeprawadzenie oceny dla rozwaizan w aktualnej populacji
            self.population.evaluate(self.task, self.services, self.trucks)

            # wybranie najlepszego rozwaizania
            best_genome = self.population.best_genome()

            # sprawdzanie czy nowe rozwiazanie jest lepsze niz najlepsze ogolnie
            if best_genome.fitness < the_best_evaluation:
                the_best_genome = best_genome
                the_best_evaluation = best_genome.fitness

            # aktualizowanie danych do wykresow
            best_evaluation_history.append(the_best_evaluation)
            best_genome_history.append(the_best_genome)
            the_best_genome_population.append(best_genome.fitness)
            mean_evaluation_history.append(np.mean(self.population.evaluations))

            # przypisanie do aktualnej populacji nowej populacji
            self.population = new_population

        plots = [best_evaluation_history, the_best_genome_population, mean_evaluation_history]

        # generowanie raportu
        report = generate_result(the_best_genome, self.trucks, self.services, plots)

        return report


def toggle(index: int, genome: Union[np.ndarray, List]):
    """
    Funckja odwraca wartosc na zadanym miescu
    :param index: indeks odwrazania
    :param genome: rozwiazanie w postaci wektora
    :return: None
    """
    if genome[index] == 1:
        genome[index] = 0
    else:
        genome[index] = 1


def toggle_part_genome(part_genome: Union[np.ndarray, List], index: int, no_of_cities: int) -> Union[np.ndarray, List]:
    """
    Funckja dodaje lub usuwa miasto do/z trasy
    :param part_genome: czesc wektora rozwiazania odpowiadajaca danej ciezarowce
    :param index: indeks miasta
    :param no_of_cities: liczba miast
    :return: zmodifikowany wektor trasy
    """
    start = index * no_of_cities
    part_genome_city = part_genome[start:start + no_of_cities]
    ones = np.count_nonzero(part_genome_city)
    if ones == 1:
        for i in range(no_of_cities):
            part_genome[start + i] = 0
    else:
        new_index = np.random.randint(0, no_of_cities - 1)
        part_genome[start + new_index] = 1

    return part_genome


def choose_truck(genome: Union[np.ndarray, List], number_of_trucks: int) -> int:
    """
    Funkcja wybiera jedna ciezarowke na podstawie wszystkich aktywnych ciezarowek
    :param genome: rozwiazanie w postaci wektora
    :param number_of_trucks: ilosc wszystkich ciezarowek
    :return: indeks ciezarowki
    """
    used_trucks = []
    for i in range(number_of_trucks):
        if genome[i] == 1:
            used_trucks.append(i)

    return np.random.choice(used_trucks)


def is_same(array1: Union[np.ndarray, List], array2: Union[np.ndarray, List]) -> bool:
    """
    Funkcja sprawdza czy dwie listy sa takie same
    :param array1: pierwsza lista
    :param array2: druga lista
    :return: czy sa takie same
    """
    for i in range(len(array1)):
        if array1[i] != array2[i]:
            return False
    return True


def build_track(array: np.ndarray, services: Services) -> Tuple[str, bool, int]:
    """
    Funkcja buduje trasne na podstawie czesciowego wektora rozwiazania
    :param array: czesciowy wektor rozwiazania
    :param services: obiekt klasy Services
    :return: krotka (zbudowana trasa, czy wraca do Warszawy, ilosc miast odwiedzanych w zbudowanej trasie)
    """
    track = []
    has_end = False

    for i in range(len(array)):
        if array[i] == 1:
            track.append(services.cities_connections[i])

    result = "Warszawa"
    city = result
    for _ in range(len(track)):
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


def find_distance(origin_city: str, destination_city: str, city_connections: List) -> float:
    """
    Funkcja odnajduje dystans pomiedzy dwoma miastami
    :param origin_city: miasto poczatkowe
    :param destination_city: miasto koncowe
    :param city_connections: lista polaczen miedzy miastami
    :return: odleglosc miedzy miastami
    """
    for i in range(len(city_connections)):
        if city_connections[i][0] == origin_city and city_connections[i][1] == destination_city:
            return city_connections[i][2]

    raise ValueError


def get_distances(genome: Union[np.ndarray, List], task: Task, services: Services) -> List[float]:
    """
    Funckja liczaca dlugosc trasy dla kazdej ciezarowki (sprowadza sie to do tego ze jezeli
    ciezarowka jest aktywna to wylicza jej trase a jezeli nie to jest 0)
    :param genome: rozwiazanie w postaci wektora
    :param task: obiekt klasy Task
    :param services: obiekt klasy Services
    :return: lista dlugosci tras
    """
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


def generate_part_genome_city(task: Task) -> List[int]:
    """
    Funckja potrzebna do generowania populacji poczatkowej. Generuje czesc rozwiazania a mianowicie
    czy ciezarowka bedzie odwiedziala dane miasto czy nie
    :param task: obiekt klasy Task
    :return: lista wybranego polaczenia dla miasta (wektor binarny)
    """
    cities = []
    has_one = False
    for i in range(task.no_of_cities):
        if has_one:
            break

        value = np.random.random_sample()

        # prawdopodobienswto wygenerowania polaczenia miedzy miastami
        if value <= 0.2:
            cities.append(1)
            has_one = True
        else:
            cities.append(0)

    for i in range(task.no_of_cities - len(cities)):
        cities.append(0)

    return cities


def generate_part_genome(task: Task) -> List[int]:
    """
    Funckja potrzebna do generowania populacji poczatkowej. Generuje czesc rozwiazania a mianowicie
    trase jednej ciezarowki
    :param task: obiekt klasy Task
    :return: lista trasy (wektor binarny)
    """
    part_genome = []
    for i in range(task.no_of_cities_connections // task.no_of_cities):
        part_genome_city = generate_part_genome_city(task)
        part_genome += part_genome_city

    return part_genome


def generate_population(task: Task) -> List[List[int]]:
    """
    Funkcja generuje populacje poczatkowa
    :param task: obiekt klasy Task
    :return: populacja poczatkowa
    """
    genomes = []
    for i in range(task.population_size):
        genome = []
        for j in range(task.no_of_trucks):
            value = np.random.random_sample()
            # prawdopodobienstwo wygenerowania aktywnej ciezarowki
            if value <= 0.1:
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


def get_velocity(cargo: int) -> int:
    """
    Funckja wylicza srednia predkosc na podstawie maksymalnej ladownosci
    :param cargo: maksymalna ladownosc ciezarowki
    :return: srednia predkosc
    """
    if cargo < 1500:
        return 80
    elif cargo < 5000:
        return 75
    elif cargo < 18000:
        return 70
    else:
        return 60


def get_city_connections() -> Dict[Tuple[str, str], float]:
    """
    Funckja pobieraajace dane odnoscie wszyskich mozliwych polaczen miedzy miastami z bazy danych
    :return: slownik wszystkiich polaczen z odlegloscmami
    """
    city_connections = {}
    try:
        con = dbconnector.conncect_to_db()
        db_city_connections = dbconnector.dbGetQuery(con, "SELECT * FROM citiesconnections")
        dbconnector.close_connection(con)
    except dbconnector.OperationalError as e:
        print(f"Error: No internet connection {e.pgerror}")
        db_city_connections = nointernethelpers.db_city_connections

    for _, connection, distance in db_city_connections:
        connection = connection.split('-')
        city_connections[(connection[0], connection[1])] = distance

    return city_connections


def generate_result(genome: Genome, trucks: List[Truck], services: Services, plots: List) -> Dict:
    """
    Funckja generuje raport na podstawie rozwiazania
    :param genome: rozwiazanie (obiekt klasy Genome)
    :param trucks: lista obiektow klasy Truck
    :param services: obiekt klasy Services
    :param plots: lista danych do wygenerowania wykresow
    :return: raport w postaci slownika
    """
    result = {}
    service_code = 0
    for i in range(genome.no_of_trucks):
        helper = {}
        if genome.genome[i] == 0:
            continue
        truck = trucks[i]
        truck.service = service_code

        start = genome.no_of_trucks + i * len(services.cities_connections)
        track, _, _ = build_track(genome.genome[start:start + len(services.cities_connections)], services)
        helper['truck'] = str(truck)
        helper['route'] = track
        result[f'service-{service_code}'] = helper
        service_code += 1

    result['evaluations'] = str(genome.fitness)

    plt.plot(plots[0])
    plt.plot(plots[1])
    plt.plot(plots[2])
    plt.legend(["Najlepsze rozwiazanie", "Najlepsze rozwiazanie w populacji", "Srednia ocen w populacji"])
    plt.title("Raport przebiegu")
    plt.xlabel("Generacja")
    plt.ylabel("Ocena jakości")
    plt.grid(True)
    plt.savefig("images/raport.png")
    plt.show()

    return result


def find_solution(services: Dict, parameters: Dict) -> Dict:
    """
    Funckja uruchamiajaca algorytm
    :param services: zamowienia (kursy)
    :param parameters: parametry algorytmu
    :return: raport
    """
    solution = Solver(parameters, services)
    report = solution.fit(parameters['iterations'])

    return report
