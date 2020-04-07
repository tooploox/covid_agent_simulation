from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from enum import Enum


MAX_INFECTION_STEPS = 14


class BoundaryPatch(Agent):
    def __init__(self, unique_id, pos, model):
        '''
        Creates a new patch of boundary

        '''
        super().__init__(unique_id, model)

    def step(self):
        return


class CoronavirusModel(Model):
    def __init__(self, N=10, width=10, height=10):
        self.num_agents = N
        self.grid = MultiGrid(height, width, False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Infected": all_infected, "Healthy": all_healthy, "Recovered": all_recovered}
        )

        i = 0
        # Create boundaries
        vert_bound = [(N//3,b) for b in range(N)]
        horizontal_bound = [(a,N//2) for a in range(N//3)]
        boundaries = vert_bound+horizontal_bound
        for x,y in boundaries:
            i += 1
            patch = BoundaryPatch(i, (x, y), self)
            self.grid.place_agent(patch, (x, y))

        # Create agents
        choices = [CoronavirusAgentState.HEALTHY, CoronavirusAgentState.INFECTED]
        for j in range(self.num_agents):
            i += 1
            a = CoronavirusAgent(i, self, self.random.choice(choices))
            self.schedule.add(a)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)

            if (x,y) not in boundaries:
                self.grid.place_agent(a, (x, y))

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
        new_position = self.random.choice(possible_steps)
        this_cell = self.model.grid.get_cell_list_contents([new_position])
        types = [type(obj) for obj in this_cell]
        if BoundaryPatch  in types:
            print(types)
        else:
            self.model.grid.move_agent(self, new_position)

    def infect(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            if type(other) is CoronavirusAgentState and other.state == CoronavirusAgentState.HEALTHY:
                other.state = CoronavirusAgentState.INFECTED

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