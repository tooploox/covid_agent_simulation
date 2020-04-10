from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
import random

from .agents import CoronavirusAgent, InteriorAgent, CoronavirusAgentState, InteriorType


class CoronavirusModel(Model):
    def __init__(self, num_agents=10,
                 config=None, scenario='park', going_out_prob_mean=0.5):

        self.config = config
        np.random.RandomState(config['common']['random_seed'])

        grid_map = self.load_gridmap(scenario)
        self.num_agents = num_agents
        self.grid = MultiGrid(grid_map.shape[0], grid_map.shape[1], False)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            model_reporters={"Infected": all_infected,
                             "Healthy": all_healthy,
                             "Recovered": all_recovered}
        )
        self.going_out_prob_mean = going_out_prob_mean
        self.global_max_index = 0
        self.house_colors = {}
        self.infection_probabilities = self.config['common']['infection_probabilities']

        self.setup_interiors(grid_map)
        self.setup_agents()
        self.setup_common_area_entrance(self.config['environment'][scenario]['entrance_cells'])

        self.running = True
        self.datacollector.collect(self)

    def load_gridmap(self, scenario):
        path = self.config['environment'][scenario]['map_path']
        grid_map = np.load(path)

        return grid_map

    @staticmethod
    def clipped_normal_dist_prob(mu):
        prob = np.random.normal(mu, mu/2)
        prob = np.clip(prob, 0, 1)

        return prob

    def get_unique_id(self):
        unique_id = self.global_max_index
        self.global_max_index += 1

        return unique_id

    def setup_agents(self):

        home_coors = []
        for info in self.grid.coord_iter():
            contents = info[0]
            coors = info[1:]
            for object in contents:
                if object.interior_type == InteriorType.INSIDE:
                    home_coors.append(coors)

        if self.num_agents > len(home_coors):
            self.num_agents = len(home_coors)
            print(f'Too many agents, they cannot fit into homes. Creating just: {self.num_agents}')

        for i in range(self.num_agents):
            ind = np.random.randint(0, len(home_coors), 1)[0]
            x, y = home_coors[ind]
            del home_coors[ind]  # make sure agents are not placed in the same cell

            home_id = [a.home_id for a in self.grid.get_cell_list_contents((x, y)) if type(a) == InteriorAgent]
            state = CoronavirusAgentState.HEALTHY
            if np.random.rand() < self.config['common']['initially_infected_population']:
                state = CoronavirusAgentState.INFECTED
            a = CoronavirusAgent(self.get_unique_id(), self, state, home_id=home_id,
                                 config=self.config,
                                 going_out_prob=self.clipped_normal_dist_prob(self.going_out_prob_mean))
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))
            a.set_home_address((x, y))


    def setup_interior(self, row, column, agent_id, interior_type, home_id=None, color="white", shape=None):
            interior = InteriorAgent(agent_id, self, color, shape, interior_type, home_id)
            # origin of grid here is at left bottom, not like in opencv left top, so we need to flip y axis
            row = self.grid.height - row - 1
            self.grid.place_agent(interior, (column, row))


    def setup_interiors(self, grid_map):
        self.generate_house_colors(grid_map)
        for r in range(grid_map.shape[0]):
            for c in range(grid_map.shape[1]):
                if grid_map[r, c] == 0:
                    self.setup_interior(r, c, self.get_unique_id(), grid_map[r, c], color="white")
                else:
                    self.setup_interior(r, c, self.get_unique_id(), InteriorType.INSIDE, grid_map[r, c],
                                        color=self.house_colors[grid_map[r, c]])

    def setup_common_area_entrance(self, entrance_cell=[(0, 0)]):
        self.common_area_entrance = entrance_cell

    def generate_house_colors(self, grid_map):
        house_num = int(grid_map.max())
        for i in range(1, house_num + 1):
            self.house_colors[i] = "#%06x" % random.randint(0, 0xFFFFFF)

    def get_cell_id(self, pos):
        agents_in_cell = self.grid.get_cell_list_contents(pos)
        for a in agents_in_cell:
            if type(a) == InteriorAgent:
                return a.home_id
        raise RuntimeError('Cell without inferior agent found')

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


def all_infected(model):
    return get_all_in_state(model, CoronavirusAgentState.INFECTED)


def all_healthy(model):
    return get_all_in_state(model, CoronavirusAgentState.HEALTHY)


def all_recovered(model):
    return get_all_in_state(model, CoronavirusAgentState.RECOVERED)


def get_all_in_state(model, state):
    return len([1 for agent in model.schedule.agents
                if type(agent) == CoronavirusAgent and agent.state == state])
