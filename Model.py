"""Module for implementing an evacuation decision model."""
import warnings
import pickle
import mesa
import networkx as nx
import numpy as np
from mesa import Model
from mesa.space import NetworkGrid
from scipy.spatial import KDTree
from Agent import Individual
from helper_functions import *
from run_config import *

warnings.filterwarnings("ignore")


class EvacuationDec(Model):
    """An agent-based model for simulating evacuation decisions."""

    def __init__(
            self,
             state = "Florida",             # Lost functionality, do not change
             county = "Miami-Dade County",  # Lost functionality, do not change
             number_of_steps = 88,          # Number of steps, one step is 2 hours
             init_individuals = 1000,       # Number of Individuals in the model
             node_connectivity=6,           # Determines the number of acquaintances
             n_neighbors=10,                # Determines the number of physical neighbors
             min_probability_threshold=0.0, # threshold Individual must reach before even considering implementing
             comm_watch_value_risk=0.05,    # The influence of a government watch order on risk perception
             comm_warning_value_risk=0.1,   # The influence of a government warning order on risk perception

             comm_watch_value_imm=0.01,     # The influence of a government watch order on immediacy
             comm_warning_value_imm=0.05,   # The influence of a government watch order on immediacy,

             coeff_risk_perception=1,       # Strength of risk perception influence between individuals
             ceiling = 0.4,                 # Defines what the maximum value of the base immediacy value can become

             coeff_action_comm = 1,         #   Communication influence on protective action

             grow_factor=30,                # Controls how fast the base value of immediacy increases
             phase_change_factor=0.1,       # Effect on social_perception when a phase is changed

             action_comm_value_imm=0.01,    # The influence an Individual has on the immediacy acquaintances
             action_comm_value =0.1,        # The influence an Individual has on the decision of neighbors
             seed=None,                     # Determines if the model is stochastic or deterministic
             watch_shift=0,                 # Determines with how many steps the watch and warning are advanced
             communication_timing = 0,      # Determines the time added between watch and warning
             evac_watch_step = 55,          # The initial time of the watch
             evac_warning_step = 60,        # The initial time of the warning
             media_weight_trust = 0.04,     # Adjusts the survey value for media trust
             media_weight_perc = 0.2,       # Adjusts the influence of the media cua un risk perception
             RA_base = 0.5,                 # The base value for the threshold to move out the risk assessment phase
             RI_base = 0.2,                 # The threshold value to move out the risk identification
             threshold_strength_RA = 0.4,   # Influence of the survey RA value on RA_base
             env_strength = 0.18 ,          # Influence of the environmental cues on risk perception
             outcome_collection="phase_1"): # Determines what data the collector will collect

        super().__init__(seed=seed)

        # Creates a Watts Strogatz Graph simulating a small world network
        self.G = nx.watts_strogatz_graph(init_individuals, node_connectivity, 0.7, seed=None, create_using=None)
        self.grid = NetworkGrid(self.G)

        # Loads the logistic model used to calculate probabilities for destination options
        self.logistic_model = pickle.load(open('regression models/reg_results_FINAL/finalized_model.sav', 'rb'))
        self.media_weight_trust = media_weight_trust
        self.media_weight_perc = media_weight_perc

        # Value meanings are explained line above
        self.RI_base = RI_base
        self.RA_base = RA_base
        self.threshold_strength_RA = threshold_strength_RA
        self.env_strength = env_strength
        self.coeff_risk_perception = coeff_risk_perception
        self.coeff_action_comm = coeff_action_comm
        self.comm_watch_value_risk = comm_watch_value_risk
        self.comm_warning_value_risk = comm_warning_value_risk
        self.comm_watch_value_imm = comm_watch_value_imm
        self.comm_warning_value_imm = comm_warning_value_imm
        self.grow_factor = grow_factor
        self.ceiling = ceiling
        self.number_of_steps = number_of_steps
        self.phase_change_factor = phase_change_factor
        # Determines the timings for the watch and warning for both the hurricane as the storm surge
        self.trop_warning_step = evac_watch_step - watch_shift - communication_timing
        self.evac_warning_step = evac_warning_step - communication_timing
        self.action_comm_value = action_comm_value
        self.action_comm_value_imm = action_comm_value_imm
        self.coeff_dict = {
            "risk_perception": coeff_risk_perception,
            "evac_friends": coeff_action_comm,
            "evac_hotel": coeff_action_comm,
            "evac_shelter": coeff_action_comm,
            "stay": coeff_action_comm
        }
        self.min_probability_threshold = min_probability_threshold # Not used

        # Required to make model stop at the right time
        self.running = True

        # Attributes required for output metrics
        self.evaced_agents = 0
        self.average_evac_time = 0
        self.hotel_choice = 0
        self.friends_choice = 0
        self.shelter_choice = 0
        self.stay_choice = 0


        # Retrieves the living areas, rain cues, wind cues and areas affected by the storm surge
        init_data = agent_init_data([state], [county])
        pos_probs = init_data["geometry"].centroid
        pos_idx = list(pos_probs)

        # Splits the values in init_data to separate variables
        wind_list = init_data["WindCat"].apply(parse_np_float_string)
        rain_list = init_data["RainCat"].apply(parse_np_float_string)
        surge_list = init_data["storm_Surge"].apply(parse_np_float_string)

        # Required for KDE-tree, which is needed for neighbor calculation
        self.pos_dict = {}

        # Loads the bootstrapped data from the survey
        factor_data, weight_data, media_weight = population_bootstrapper(len(self.G.nodes))

        # Loops over network nodes and creates an agent for every node
        for node_id in range(len(self.G.nodes)):
            # Determines living location of agent using the population densities
            population_idx = np.random.choice(len(init_data), p=init_data["PopDense"])
            # Assigns the correct data for living area and bootstrapped survey data
            agent_attributes = {
                "factor_values": factor_data.iloc[[node_id]], # Factor values for logistic model
                "weight_values": weight_data.iloc[node_id],   # Weights RA threshold and environmental cues perception
                "media_values": media_weight.iloc[[node_id]], # Trust and frequency values for media cue
                'wind': wind_list[population_idx], # Wind cue values
                'rain': rain_list[population_idx], # Rain cue values
                # Timing for storm surge watch and warning
                "storm_surge": shift_watch_warning(surge_list[population_idx],
                                                   timing=int(communication_timing/3),
                                                   gap=int(watch_shift/3)),
            }
            # Initiate agent
            agent = Individual(self, **agent_attributes)
            # Add agent to dictionary for KDE-tree
            self.pos_dict[agent] = pos_idx[population_idx]
            # Add agent to model schedule
            self.grid.place_agent(agent, node_id)

        # Defines KDE-Tree
        coords = np.array([(pt.x, pt.y) for pt in self.pos_dict.values()])
        self.tree = KDTree(coords)
        # Defines closest neighbours
        for agent in self.agents:
            agent.neigh_individuals = closest_neighbours(agent.model, agent.unique_id, n_neighbors)

        # Defines datacollector
        self.datacollector = mesa.DataCollector(
            agent_reporters=data_collection_attributes(outcome_collection)[0],
            model_reporters=data_collection_attributes(outcome_collection)[1])

        # Required to make the model stop at the correct time
        self.run_model()

    def government_warning_communication(self, comm_value_risk: float, comm_value_immediacy: float) -> None:
        """Update agents' perceptions based on government communications.
    
        Args:
            comm_value_risk: Risk communication value
            comm_value_immediacy: Propensity communication value
        """
        for agent in self.agents:
            agent.social_perception += comm_value_risk
            agent.immediacy_cum += comm_value_immediacy

    def step(self):

        # Counts how many agents are in each phase
        self.phase_0 =self.agents.get("phase").count(0)
        self.phase_1 =self.agents.get("phase").count(1)
        self.phase_2 =self.agents.get("phase").count(2)

        # Randomizes order schedule and cycle over agent step function
        self.agents.shuffle_do("step")
        # Caluclates final metrics at the last model step and stops model
        if self.steps == self.number_of_steps:

            print("Finished simulation")
            evac_agents = self.datacollector.get_model_vars_dataframe()
            evacs_per_step =evac_agents["evac_agents"]
            numerator = sum((t + 1) * n for t, n in enumerate(evacs_per_step))
            denominator = sum(evacs_per_step)
            self.average_evac_time = numerator / denominator if denominator > 0 else None

            self.running = False # Stops model

        # Issues Hurricane watch and warning at correct steps
        if self.steps == self.trop_warning_step:  # Tropical warning
            self.government_warning_communication(self.comm_watch_value_risk,self.comm_watch_value_risk)
        elif self.steps == self.evac_warning_step:  # Evacuation order
            self.government_warning_communication(self.comm_warning_value_risk,self.comm_warning_value_imm)

        # Saves the correct data
        self.datacollector.collect(self)

        # Resets the evacuated agents per step metric
        self.evaced_agents = 0
