"""
Agent.py

Defines the `Individual` agent class for use in an agent-based model (ABM) simulation.
Agents represent individuals responding to environmental threats, social cues, and risk communication.
The simulation models decision-making with respect to evacuation and protective actions.

Dependencies:
    - mesa.Agent: agent-based modeling framework
    - numpy: numerical operations
    - warnings: suppresses unnecessary warnings for simulation clarity
"""

from mesa import Agent
import numpy as np
import warnings

warnings.filterwarnings("ignore")


class Individual(Agent):
    def __init__(self, model,factor_values,weight_values,media_values,wind, rain,storm_surge):  # ,pos):
        super().__init__(model)

        self.factor_values = factor_values # Factors used as input for logistic model
        self.weight_values = weight_values # Weights used for determinign RA threshold

        # Survey data for Usage frequency and trust of media, used for media cue
        self.media_values = media_values
        self.media_trust = np.array([self.model.media_weight_trust * x for x in media_values.iloc[:, :-5].values[0]])
        self.media_freq = media_values.iloc[:, :5].values[0]

        # Gets acquaintances for Watts Strogatz graph
        self.acquaintances = self.model.grid.get_neighbors(self.unique_id - 1)

        self.rain = rain # Rain cue list
        self.wind = wind # Wind cue list
        self.storm_surge = storm_surge # Storm surge state list

        self.rain_cue = rain[self.model.steps] # Current wind cue value
        self.wind_cue = wind[self.model.steps] # Current rain cue value
        self.storm_surge_state = storm_surge[self.model.steps] # Current Storm surge cue value

       # Starting values for attributes, without errors occur due communication methods
        self.risk_perception = 0
        self.evac_friends = 0
        self.evac_hotel = 0
        self.evac_shelter = 0
        self.stay = 0
        self.phase = 0
        self.immediacy_cum = 0
        self.immediacy_base = 0
        self.neigh_individuals = None # Gets assigned in model.py
        self.media_cue = 0
        self.cue_perception = 0
        self.social_perception = 0

        self.RI_thresh = self.model.RI_base # Threshold for risk identification phase

        # Calculates the threshold for the risk assessment phase
        self.RA_thresh = self.model.RA_base + weight_values[0] * self.model.threshold_strength_RA
        self.env_weight = weight_values[2] * self.model.env_strength


    def __str__(self):
        return f"{self.age} old, {self.edu}, {self.income}, {self.car}, {self.race}"


    def general_communication(self, attribute):
        """
        Update own attribute (e.g., risk perception) by averaging with acquaintances.
       The value in coeff_dict determines the strength of acquaintances.
        """
        if len(self.acquaintances) != 0:
            comm_sum = sum([getattr(self, attribute) for i in self.acquaintances]) / len(self.acquaintances)
            own = getattr(self, attribute)
            avg = (own + comm_sum) / 2
            diff = own - avg
            result = own + (diff * self.model.coeff_dict[attribute])
            setattr(self, attribute, result)

    def action_communication(self):
        """
         Communicate evacuation decisions for all evacuation options and risk perception
         with acquaintances to influence their decisions.
         """
        for action in ["evac_friends", "evac_hotel", "evac_shelter", "stay","risk_perception"]:
            self.general_communication(action)



    def phase_change_communication(self, phase):
        """
        Increase social perception (part of risk perception) for acquaintances to reflect a communicated phase
        change (heightened risk awareness or action signal).
        """
        # print(f"Agent{self.unique_id}")
        if len(self.acquaintances) != 0:
            # print(f"Agent {self.unique_id} reaches out to: Agent {[x.unique_id for x in self.acquaintances]}")
            for agent in self.acquaintances:
                # print(f"Perception Agent {agent.unique_id} before: {agent.social_perception}")
                agent.social_perception += self.model.phase_change_factor
                # print(f"Perception Agent {agent.unique_id} after: {agent.social_perception}")



    def calc_risk_perception(self):
        """
        Calculate the current cue perception (part of risk perception) as a weighted combination of environmental
        cues (wind, rain), media cues.
        """
        self.cue_perception = self.env_weight * (self.wind_cue + self.rain_cue) + self.model.media_weight_perc *self.media_cue #+ self.storm_surge_state * self.model.gov_surge_coeff


    def calc_media_cue(self):
        """
        Update the agent's media cue variable based on frequency and trust toward media.
        Increments media_cue if exposed at this timestep.
        """
        media_comm = [1 if self.model.steps % medium == 0 else 0 for medium in self.media_freq]
        # print(media_comm)
        raw_increment = sum(self.media_trust * media_comm) / 5
        if self.media_cue + raw_increment < 1:
            self.media_cue += raw_increment
        else:
            self.media_cue = 1


    def risk_identification(self):
        """
        Phase 0: Determine whether risk perception exceeds the identification threshold.
        If so, notify acquaintances and move to the next phase.
        """
        self.calc_risk_perception()
        if self.risk_perception >= self.RI_thresh:
            # print(f"Agent {self.unique_id} communicates phase {self.phase} change!")
            self.phase_change_communication(1)
            self.phase = 1
            # print(f"Agent {self.unique_id} new phase is {self.phase}! \n")

    def risk_assessment(self):
        """
        Phase 1: Assess whether risk exceeds the risk assessment threshold.
        If so, notify, search for the best action, and proceed to the action phase.
        Otherwise, continue social communication.
        """
        self.calc_risk_perception()
        if self.risk_perception > self.RA_thresh:
            # print(f"Agent {self.unique_id} communicates phase {self.phase} change!")
            self.phase_change_communication(2)
            self.protective_action_search()
            self.phase = 2
            # print(f"Agent {self.unique_id} new phase is {self.phase}! \n")
        else:
            self.general_communication("risk_perception")


    def protective_action_search(self):
        """
        Use the multinominal logistic regression determined in regression models/Statistics1.ipynb to determine the
        probabilities of each protective action and record the preferred option.
        """
        self.evac_friends, self.evac_hotel, self.evac_shelter, self.stay = self.model.logistic_model.predict_proba(self.factor_values)[0]
        self.evac_values = {
            'evac_friends': self.evac_friends,
            'evac_hotel': self.evac_hotel,
            'evac_shelter': self.evac_shelter,
            'stay': self.stay}
        self.preferred_evac = max(self.evac_values, key=self.evac_values.get)


    def protective_action_assessment(self):
        """
        Phase 2: Determine propensity (Called immediacy in code or imm) for implementing the protective action.
        If probability exceeds the model minimum (Default has no minimum),the agent may act with some randomness.
        Communicate choice with the network and remove itself if evacuation occurs.
        """
        self.immediacy = self.immediacy_cum + self.immediacy_base
        self.immediacy = min(1,self.immediacy)
        self.calc_risk_perception()
        prob_action = 0
        prob_action = min(1, prob_action)
        prob_action += self.immediacy
        if prob_action > self.model.min_probability_threshold:
            if self.random.random() < prob_action:
              # print(f"Agent {self.unique_id} will implement the {self.preferred_evac} action!")
                self.Protective_Action_Implementation_communication()
                self.phase = 3
                self.model.evaced_agents += 1
                if self.preferred_evac == "evac_hotel":
                    self.model.hotel_choice += 1
                if self.preferred_evac == "evac_friends":
                    self.model.friends_choice += 1
                if self.preferred_evac == "evac_shelter":
                    self.model.shelter_choice += 1
                if self.preferred_evac == "stay":
                    self.model.stay_choice += 1
                self.remove()
            else:
                self.action_communication()
        else:
            self.action_communication()



    def Protective_Action_Implementation_communication(self):
        """
        Communicate protective action implementation to acquaintances and neighbors,
        influencing their action preference, propensity, and risk perceptions.
        """
        # print(f"Agent {self.unique_id} reaches out to acquaintances: Agent {[x.unique_id for x in self.acquaintances]}")
        for agent in self.acquaintances:
          # print(f"Attitude towards {self.preferred_evac} action for Agent {round(agent.unique_id,5)} before: {round(getattr(agent, self.preferred_evac),5)}")
          # print(f"Propensity value of Agent {agent.unique_id} before: {round(agent.immediacy_cum,5)}")
            setattr(agent, self.preferred_evac, getattr(agent, self.preferred_evac) + self.model.action_comm_value)
            agent.immediacy_cum += self.model.action_comm_value_imm
          # print(f"Attitude towards {self.preferred_evac} action for Agent {agent.unique_id} after: {round(getattr(agent, self.preferred_evac),5)}")
          # print(f"Propensity value of Agent {agent.unique_id} after: {round(agent.immediacy_cum,5)}")
        if self.preferred_evac in ["evac_hotel", "evac_friends", "evac_shelter"]:
          # print(f"Agent {self.unique_id} seen by neighbours: Agent {[x.unique_id for x in self.neigh_individuals]}")
            for agent in self.neigh_individuals:
              # print(f"Attitude and propensity values of Agent {agent.unique_id} before: {agent.evac_friends,agent.evac_hotel,agent.evac_shelter,agent.immediacy_cum}")
                agent.evac_friends += self.model.action_comm_value
                agent.evac_hotel += self.model.action_comm_value
                agent.evac_shelter += self.model.action_comm_value
                agent.immediacy_cum += self.model.action_comm_value_imm

    def step(self):
        """
        Primary timestep update function for the agent, orchestrating transitions between
        risk perception, social communication, and action phases based on model and environment.
        Updates environmental cues, checks for state transitions, and applies influence.
        """
        """Method called by main model class through the agent schedule. Calculates values for 
        propensity and risk perception. Updates the current values for media, wind, rain cue and the 
        storm surge watch/warning state. At last, calls the method corresponding o the phase the agent
        is in and communicate risk perception.
        """
        self.risk_perception = min(self.cue_perception + self.social_perception, 1)
        self.immediacy_base = self.model.ceiling * ((self.model.steps + 1) * (1 / self.model.number_of_steps)) / (
                    1 + self.model.grow_factor * (1 - (self.model.steps + 1) * (1 / self.model.number_of_steps)))
        n_steps = self.model.steps

        self.rain_cue = self.rain[n_steps-1]
        self.calc_media_cue()
        if n_steps % 3 == 0:

            old_value = self.storm_surge_state
            self.storm_surge_state = self.storm_surge[int(n_steps / 3)+1]
            if old_value == 0:
                if  self.storm_surge_state == 0.5:
                    self.social_perception += self.model.comm_watch_value_risk
                    self.immediacy_cum += self.model.comm_warning_value_imm
                elif self.storm_surge_state == 1:
                    self.social_perception += self.model.comm_watch_value_risk
                    self.immediacy_cum += self.model.comm_warning_value_imm
            elif old_value == 0.5:
                if self.storm_surge_state == 1:
                    self.social_perception += self.model.comm_watch_value_risk
                    self.immediacy_cum += self.model.comm_warning_value_imm
        if n_steps % 3 == 0:
            self.wind_cue = self.wind[(int(n_steps / 3))-1]
        phase_methods = {
            0: self.risk_identification,
            1: self.risk_assessment,
            2: self.protective_action_assessment,
        }
        # Get the method for the current phase and call it
        method = phase_methods.get(self.phase)
        if method:
            method()
        self.general_communication("risk_perception")
