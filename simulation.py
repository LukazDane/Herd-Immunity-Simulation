from virus import Virus
from logger import Logger
from person import Person
import random
import sys
random.seed(42)


class Simulation(object):
    ''' Main class that will run the herd immunity simulation program.
    Expects initialization parameters passed as command line arguments when file is run.

    Simulates the spread of a virus through a given population.  The percentage of the
    population that are vaccinated, the size of the population, and the amount of initially
    infected people in a population are all variables that can be set when the program is run.
    '''

    def __init__(self, population_size, vacc_percentage, virus_name, mortality_rate, repro_rate, initial_infected=1):
        ''' Logger object logger records all events during the simulation.
        Population represents all Persons in the population.
        The next_person_id is the next available id for all created Persons,
        and should have a unique _id value.
        The vaccination percentage represents the total percentage of population
        vaccinated at the start of the simulation.
        You will need to keep track of the number of people currently infected with the disease.
        The total infected people is the running total that have been infected since the
        simulation began, including the currently infected people who died.
        You will also need to keep track of the number of people that have die as a result
        of the infection.

        All arguments will be passed as command-line arguments when the file is run.
        HINT: Look in the if __name__ == "__main__" function at the bottom.
        '''
        # TODO: Create a Logger object and bind it to self.logger.
        # Remember to call the appropriate logger method in the corresponding parts of the simulation.
        # TODO: Call self._create_population() and pass in the correct parameters.
        # Store the array that this method will return in the self.population attribute.
        # TODO: Store each newly infected person's ID in newly_infected attribute.
        # At the end of each time step, call self._infect_newly_infected()
        # and then reset .newly_infected back to an empty list.
        self.population_size = population_size
        self.vacc_percentage = vacc_percentage
        self.total_infected = initial_infected
        self.current_infected = initial_infected
        self.next_person_id = 0
        self.total_dead = 0

        self.virus = Virus(virus_name, mortality_rate, repro_rate)
        file_name = (f'{virus_name}_simulation_pop_{population_size}_vp_'
                     f'{vacc_percentage}_infected_{initial_infected}.txt')
        self.logger = Logger(file_name)

        self.newly_infected = []
        self.population = self._create_population(initial_infected)

    def _create_population(self, initial_infected):
        '''This method will create the initial population.
            Args:
                initial_infected (int): The number of infected people that the simulation
                will begin with.

            Returns:
                list: A list of Person objects.

        '''
        # TODO: Finish this method!  This method should be called when the simulation
        # begins, to create the population that will be used. This method should return
        # an array filled with Person objects that matches the specifications of the
        # simulation (correct number of people in the population, correct percentage of
        # people vaccinated, correct number of initially infected people).

        # Use the attributes created in the init method to create a population that has
        # the correct intial vaccination percentage and initial infected.
        population = []
        infected_count = 0
        while len(population) != self.population_size:
            if infected_count != initial_infected:
                population.append(Person(self.next_person_id,
                                         is_vaccinated=False,
                                         infection=self.virus))
                infected_count += 1
            else:
                is_vaccinated = random.random() < self.vacc_percentage
                population.append(Person(self.next_person_id, is_vaccinated))

            self.next_person_id += 1

        return population

    def _simulation_should_continue(self):
        ''' The simulation should only end if the entire population is dead
        or everyone is vaccinated.

            Returns:
                bool: True for simulation should continue, False if it should end.
        '''
        # TODO: Complete this helper method.  Returns a Boolean.
        return (self.current_infected > 0 and
                self.total_dead < self.population_size)

    def run(self):
        ''' This method should run the simulation until all requirements for ending
        the simulation are met.
        '''
        # TODO: Finish this method.  To simplify the logic here, use the helper method
        # _simulation_should_continue() to tell us whether or not we should continue
        # the simulation and run at least 1 more time_step.

        # TODO: Keep track of the number of time steps that have passed.
        # HINT: You may want to call the logger's log_time_step() method at the end of each time step.
        # TODO: Set this variable using a helper

        time_step_counter = 0

        while self._simulation_should_continue():
            (newly_infected_people, newly_dead_people) = self.time_step()
            self.logger.log_time_step(time_step_counter,
                                      newly_infected_people, newly_dead_people,
                                      self.total_infected, self.total_dead)
            time_step_counter += 1

        print(f'The simulation has ended after {time_step_counter} turns.')

    def time_step(self):
        ''' This method should contain all the logic for computing one time step
        in the simulation.

        This includes:
            1. 100 total interactions with a randon person for each infected person
                in the population
            2. If the person is dead, grab another random person from the population.
                Since we don't interact with dead people, this does not count as an interaction.
            3. Otherwise call simulation.interaction(person, random_person) and
                increment interaction counter by 1.
            '''
        # TODO: Finish this method.
        alive = list(filter(lambda p: p.is_alive, self.population))
        infected = list(filter(lambda p: p.infection, alive))
        for person in infected:
            for _ in range(100):
                self.interaction(person, random_person=random.choice(alive))

        newly_dead_people = 0
        for person in infected:
            if person.did_survive_infection():
                self.logger.log_infection_survival(
                    person, did_die_from_infection=False)
            else:
                self.logger.log_infection_survival(
                    person, did_die_from_infection=True)
                newly_dead_people += 1

        self.total_dead += newly_dead_people
        newly_infected_people = len(self.newly_infected)
        self._infect_newly_infected()

        return (newly_infected_people, newly_dead_people)

    def interaction(self, person, random_person):
        '''This method should be called any time two living people are selected for an
        interaction. It assumes that only living people are passed in as parameters.

        Args:
            person1 (person): The initial infected person
            random_person (person): The person that person1 interacts with.
        '''
        # Assert statements are included to make sure that only living people are passed
        # in as params
        assert person.is_alive == True
        assert random_person.is_alive == True

        # TODO: Finish this method.
        #  The possible cases you'll need to cover are listed below:
        # random_person is vaccinated:
        #     nothing happens to random person.
        # random_person is already infected:
        #     nothing happens to random person.
        # random_person is healthy, but unvaccinated:
        #     generate a random number between 0 and 1.  If that number is smaller
        #     than repro_rate, random_person's ID should be appended to
        #     Simulation object's newly_infected array, so that their .infected
        #     attribute can be changed to True at the end of the time step.
        # TODO: Call slogger method during this method.
        if random_person.is_vaccinated:

            self.logger.log_interaction(person, random_person,
                                        did_infect=False, random_person_vacc=True)
        elif (random_person.infection != None or
              random_person._id in self.newly_infected):

            self.logger.log_interaction(person, random_person,
                                        did_infect=False, random_person_sick=True)
        else:
            if random.random() <= person.infection.repro_rate:
                self.newly_infected.append(random_person._id)

                self.logger.log_interaction(person, random_person,
                                            did_infect=True)
            else:
                self.logger.log_interaction(person, random_person,
                                            did_infect=False)

    def _infect_newly_infected(self):
        ''' This method should iterate through the list of ._id stored in self.newly_infected
        and update each Person object with the disease. '''
        # TODO: Call this method at the end of every time step and infect each Person.
        # TODO: Once you have iterated through the entire list of self.newly_infected, remember
        # to reset self.newly_infected back to an empty list.
        infected_people = list(filter(lambda p: p._id in self.newly_infected,
                                      self.population))
        for person in infected_people:
            person.infection = self.virus

        self.current_infected = len(self.newly_infected)
        self.total_infected += self.current_infected
        self.newly_infected.clear()


if __name__ == "__main__":
    params = sys.argv[1:]
    virus_name = str(params[2])
    repro_rate = float(params[4])
    mortality_rate = float(params[3])

    pop_size = int(params[0])
    vacc_percentage = float(params[1])

    if len(params) == 6:
        initial_infected = int(params[5])
    else:
        initial_infected = 1

    sim = Simulation(pop_size, vacc_percentage, virus_name,
                     mortality_rate, repro_rate, initial_infected)

    sim.run()
