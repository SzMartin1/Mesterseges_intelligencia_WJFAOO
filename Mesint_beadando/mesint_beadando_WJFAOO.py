import csv  # a csv fájlok beolvasásához szükséges
import random  # random számok generálásához szükséges


def start_the_main_program(machines, jobs, max_iterations, generations, job_list):

    best_found_time = float('inf')  # a legjobbb talált időt tárolja el
    base_list = [] # alaplista, melyet legenerálok

    for i in range(jobs):
        base_list += [i]
    best_list = base_list.copy()  # a best_list tárolja a legjobb megoldást

    file_output = open("log.txt", "a")  # a fájl, amibe a megoldást fogom eltárolni
    file_output.write("Base: " + str(base_list) + "\n")
    print("The genetic algorithm:")

# szimuláció megismétlése minden egyes iterációnál
    for i in range(max_iterations):
        base_temporary_list, time = get_new_genetic(machines, jobs, job_list,
                                                    base_list, generations)
# itt igazábol azt ellenőrzöm, hogy ha az újonnan talált idő jobb-e mint a régi, és ha igen akkor felülírom
# a best_found_time-ot valamint a best_list-et is
        if best_found_time > time:
            best_found_time = time
            best_list = base_temporary_list.copy()
            base_list = base_temporary_list.copy()

# a megoldás kiíratása
    file_output.write("Best found solution: " + str(best_list) + "\nTime: " + str(best_found_time))
    print("Best found solution: ", str(best_list), "\nTime: ", best_found_time)
    file_output.close()

# ezzel a fügvénnyel olvasom be a base.csv fájlból az adatokat, természetesen az első sor kihagyásával.
# Egy listában lévő listát viszek tovább.
def file_reader(file_name):
    data_list = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        for count, row in enumerate(reader):
            if count != 0:
                data_list.append(row)

    return data_list

# ezzel a függvénnyel a gépek és a munkák által meghatározott random mátrixxal feltöltöm a log.txt fáljt
def randomizejobs(machines, jobs):
    file_output = open("log.txt", "a")
    job_list = [[0 for _ in range(machines)] for _ in range(jobs)]

    for i in range(machines):  # random számok generálása a job_list-nek
        for k in range(jobs):
            job_list[k][i] = random.randint(1, 100)
            file_output.write(str(job_list[k][i]) + "\t")
        file_output.write("\n")
    file_output.close()
    return job_list  # lista visszaadása

# Ez maga a genetikus algoritmus
# Itt a függvénynek átadom a korábban már legenerált adatokat
# lista létrehozás ---> új generációk tárolása
def get_new_genetic(machines, jobs, job_list, base_list, generations):
    current_data = [[0 for _ in range(jobs)] for _ in range(generations)]
    time = []
    order_of_lists = []

# az előre legenerált adatokat kimásolom az előbbi listámba (order_of_lists ---> sorrend számontartása)
    for i in range(generations):
        for k in range(jobs):
            current_data[i][k] = base_list[k]
        time += [0]
        order_of_lists += [i]

# a genetic_mutation függvény használata (lentebb megtalálható a függvény kommentekkel ellátva)
    for i in range(generations):
        current_data[i] = genetic_mutation(current_data[i], jobs)

# a genetic_recombination függvény használata (lentebb megtalálható a függvény kommentekkel ellátva)
    for i in range(generations - 1):
        current_data[i] = genetic_recombination(current_data[i], current_data[i + 1], jobs)

    current_data[generations - 1] = genetic_recombination(current_data[generations - 1], current_data[0], jobs)

# a fitness_calculation függvény használata (lentebb megtalálható a függvény kommentekkel ellátva)
    for i in range(generations):
        time[i] = fitness_calculation(machines, jobs, job_list, current_data[i])

    time, order_of_lists = sorting_list_by_time(time, order_of_lists, generations) # lista időszerint való rendezése

    probability = 0.42  # probability of surviving, a túlélés valószínűsége

    random_number = random.random()  # 0.0 és 1.0 közötti random szám generálása

    for i in range(generations):
        if i == 0:
            if random_number < probability:
                return current_data[order_of_lists[i]], time[i]
            else:
                random_number -= probability
        else:
            if random_number < (pow(1 - probability, i) * probability):
                return current_data[order_of_lists[i]], time[i]
            else:
                random_number -= (pow(1 - probability, i) * probability)

    return current_data[order_of_lists[generations - 1]], time[generations - 1]

# az x és y változók kapnak egy random számot, utána egy egyszerű helycserés támadásba kezdek
# magyarán megcserélem a listában ezeket a random számokat
def genetic_mutation(current_data, jobs):
    x = random.randint(0, jobs - 1)
    y = random.randint(0, jobs - 1)

    temp = current_data[y]
    current_data[y] = current_data[x]
    current_data[x] = temp

    return current_data

# Egyed keresztezés történek ebben a függvényben
def genetic_recombination(current_data1, current_data2, jobs):
    first_section = random.randint(0, int(jobs / 2) - 1)  # első szekció meghatározása

    second_section = random.randint(int(jobs / 2) + 1, jobs - 1)  # második szekció meghatározása

    intersection = current_data1[first_section:second_section]  # az első és a második szekció keresztmetszetének a meghatározása

    recombinated_list = []  # az eremdényt ebbe eltárolom

    index = 0

    for i in range(jobs):
        if first_section <= index < second_section:
            for k in intersection:
                recombinated_list.append(k)
            index = second_section
        if current_data2[i] not in intersection:
            recombinated_list.append(current_data2[i])
            index += 1
    return recombinated_list # rekombinált adatokat tartalmaz, ezzel térünk vissza

# Fitness érték számítás
# számoljuk az időt amig van hátralévő munkák, majd ezt az értéket fogjuk vissza adni (time)
def fitness_calculation(machines, jobs, job_list, order_of_jobs):

    remaining_jobs = [-1 for _ in range(machines)]  # hátralévő munkák listája
    already_done_jobs = [0 for _ in range(machines)]  # a már kész munkák listája
    for i in range(machines):
        remaining_jobs[i] = job_list[order_of_jobs[0]][i]

    time = -1

    while already_done_jobs[machines - 1] != jobs:  # az egész while ciklus addig megy, amig a kész munka nem egyenlő a munkák számával
        time += 1  # time növelése eggyel
        for i in range(machines):
            if remaining_jobs[i] != 0:  # ha a hátralévő munka értéke nem egyenlő nullával
                if i != 0:
                    if already_done_jobs[i] < already_done_jobs[i - 1]:
                        remaining_jobs[i] -= 1  # csökkentjük a hátralévő munkák számát
                else:
                    remaining_jobs[i] -= 1
            else:  # ha a munkát megcsináltuk, növeljük az értékét eggyel
                already_done_jobs[i] += 1
                if jobs <= already_done_jobs[i]:
                    remaining_jobs[i] = -1
                    already_done_jobs[i] = jobs
                else:
                    remaining_jobs[i] = job_list[order_of_jobs[already_done_jobs[i]]][i]
                    if i != 0:
                        if already_done_jobs[i - 1] > already_done_jobs[i]:
                            remaining_jobs[i] -= 1
                    else:
                        remaining_jobs[i] -= 1

    return time

#  itt rendezem a listát idő szerint
def sorting_list_by_time(time_base, list_base, generations):
    time = time_base.copy()
    _list = list_base.copy()
    for i in range(generations - 1):
        for k in range(i + 1, generations):
            if time[i] > time[k]:
                temp = time[i]
                time[i] = time[k]
                time[k] = temp
                temp = _list[i]
                _list[i] = _list[k]
                _list[k] = temp
    return time, _list

# maga a main függvény
def main():
    file_name = 'base_data.csv' # a csv fájl neve, amelyből az adatokat fogom kiolvasni
    data_list = file_reader(file_name)
# iterálás a fájlból legenerált listákon ---> adatok átadása a main függvénynek
    for data in data_list:
        machines = int(data[0])
        max_iterations = int(data[1])
        jobs = int(data[2])
        generations = int(data[3])
        seed_of_the_generation = int(data[4])
        random.seed(seed_of_the_generation)  # magérték megadása

        job_list = randomizejobs(machines, jobs)
# a start_the_main_program elindítása
        start_the_main_program(machines, jobs, max_iterations, generations, job_list)


if __name__ == "__main__":
    main()
