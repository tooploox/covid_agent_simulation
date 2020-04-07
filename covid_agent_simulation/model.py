from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from .agents import CoronavirusAgent, InteriorAgent, CoronavirusAgentState


class CoronavirusModel(Model):
    def __init__(self, num_agents=10, width=10, height=10):
        self.num_agents = num_agents
        self.grid = MultiGrid(height, width, False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Infected": all_infected, "Healthy": all_healthy, "Recovered": all_recovered}
        )
        self.global_max_index = 0

        self.setup_interiors()
        self.setup_agents()

        self.running = True
        self.datacollector.collect(self)

    def get_unique_id(self):
        unique_id = self.global_max_index
        self.global_max_index += 1

        return unique_id

    def setup_agents(self):

        choices = [CoronavirusAgentState.HEALTHY, CoronavirusAgentState.INFECTED]
        for i in range(self.num_agents):
            a = CoronavirusAgent(self.get_unique_id(), self, self.random.choice(choices))
            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def setup_interior(self, init_row, init_column, width=3, height=4):
        for x in range(init_column, init_column + width):
            for y in range(init_row, init_row + height):
                home = InteriorAgent(self.get_unique_id(), self, "yellow")
                self.grid.place_agent(home, (x, y))

    def setup_interiors(self):
        homes_coor = [
            (0, 0),
            (0, 10),
            (0, 30)
        ]
        for coor in homes_coor:
            self.setup_interior(coor[0], coor[1])

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


def all_infected(model):
    return get_all_in_state(model, CoronavirusAgentState.INFECTED)


def all_healthy(model):
    return get_all_in_state(model, CoronavirusAgentState.RECOVERED)


def all_recovered(model):
    return get_all_in_state(model, CoronavirusAgentState.HEALTHY)


def get_all_in_state(model, state):
    return len([1 for agent in model.schedule.agents if agent.state == state])
