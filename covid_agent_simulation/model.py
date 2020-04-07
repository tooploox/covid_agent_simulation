from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from enum import Enum
import math


MAX_INFECTION_STEPS = 14

class CoronavirusModel(Model):
    def __init__(self, N=10, width=10, height=10, infection_probabilities=[0.7, 0.4]):
        self.num_agents = N
        self.infection_probabilities = infection_probabilities
        self.grid = SingleGrid(height, width, False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Infected": all_infected, "Healthy": all_healthy, "Recovered": all_recovered}
        )

        choices = [CoronavirusAgentState.HEALTHY, CoronavirusAgentState.INFECTED]
        for i in range(self.num_agents):
            a = CoronavirusAgent(i, self, self.random.choice(choices))
            self.schedule.add(a)
            self.grid.position_agent(a, "random")

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


class CoronavirusAgentState(Enum):
    HEALTHY = 1
    INFECTED = 2
    RECOVERED = 3


class CoronavirusAgent(Agent):
    def __init__(self, unique_id, model, state):
        super().__init__(unique_id, model)
        self.state = state
        self.infected_steps = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        possible_steps = [p for p in possible_steps if p in self.model.grid.empties]
        if len(possible_steps) > 0:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def infect(self):
        neighbors = self.model.grid.get_neighbors(self.pos, True, False, len(self.model.infection_probabilities))
        for n in neighbors:
            if n.state == CoronavirusAgentState.HEALTHY and \
            self.random.uniform(0, 1) < self.model.infection_probabilities[moore_distance(self.pos, n.pos) - 1]:
                n.state = CoronavirusAgentState.INFECTED

    def step(self):
        self.move()
        if self.state == CoronavirusAgentState.INFECTED:
            if self.infected_steps >= MAX_INFECTION_STEPS:
                self.state = CoronavirusAgentState.RECOVERED
            else:
                self.infected_steps += 1
                self.infect()


def all_infected(model):
    return get_all_in_state(model, CoronavirusAgentState.INFECTED)


def all_healthy(model):
    return get_all_in_state(model, CoronavirusAgentState.RECOVERED)


def all_recovered(model):
    return get_all_in_state(model, CoronavirusAgentState.HEALTHY)


def get_all_in_state(model, state):
    return len([1 for agent in model.schedule.agents if agent.state == state])

def moore_distance(p1, p2):
    return math.floor(math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)) 