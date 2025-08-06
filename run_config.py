
"""
This file is used to quickly change the data the datacollector needs to save.
"""
from helper_functions import *

def data_collection_attributes(setting):
    if setting == "SingleRun":
        agent_attributes = {
                          "phase": "phase",
                          "wind_cue":"wind_cue",
                          "rain_cue":"rain_cue",
                          "media_cue": "media_cue",
                          "risk_perception":"risk_perception",
                          "immediacy": "immediacy",
                          "storm_surge_state": "storm_surge_state",
                            }
        model_attributes = {
                          "wind_cue": retrieve_wind_cue,
                          "rain_cue": retrieve_rain_cue,
                          "phase_0": "phase_0",
                          "phase_1": "phase_1",
                          "phase_2": "phase_2",
                          "evac_agents": "evaced_agents",
                          "average_evac_time": "average_evac_time",
                          "hotel_choice": "hotel_choice",
                          "friends_choice": "friends_choice",
                          "shelter_choice": "shelter_choice",
                          "stay_choice": "stay_choice",
                      }
    if setting == "verf":
        agent_attributes = {
                      "phase": "phase",
                      "wind_cue":"wind_cue",
                      "rain_cue":"rain_cue",
                      "media_cue": "media_cue",
                      "risk_perception":"risk_perception",
                      "immediacy": "immediacy",
                      "storm_surge_state": "storm_surge_state",
                      }
        model_attributes = {
                            # "wind_cue": retrieve_wind_cue,
                            # "rain_cue": retrieve_rain_cue,
                          "phase_0": "phase_0",
                          "phase_1": "phase_1",
                          "phase_2": "phase_2",
                          "evac_agents": "evaced_agents",
                          "average_evac_time": "average_evac_time",
                          "hotel_choice": "hotel_choice",
                          "friends_choice": "friends_choice",
                          "shelter_choice": "shelter_choice",
                          "stay_choice": "stay_choice",
                      }
    elif setting == "convergence":
        agent_attributes = {
                      # "phase": "phase",
                      # "wind_cue":"wind_cue",
                      "rain_cue":"rain_cue",
                      # "media_cue": "media_cue",
                      # "risk_perception":"risk_perception",
                      # "immediacy": "immediacy"
                      }
        model_attributes = {
                            # "wind_cue": retrieve_wind_cue,
                            # "rain_cue": retrieve_rain_cue,
                          "evac_agents": "evaced_agents",
                          "average_evac_time": "average_evac_time",
                          "hotel_choice": "hotel_choice",
                          "friends_choice": "friends_choice",
                          "shelter_choice": "shelter_choice",
                          "stay_choice": "stay_choice",
                      }
    elif setting == "all_agent":
        agent_attributes = {
            "cue_perception": "cue_perception",
            "risk_perception": "risk_perception",
            "media_cue": "media_cue",
            "rain_cue": "rain_cue",
            "wind_cue": "wind_cue",
            "storm_surge_state": "storm_surge_state",
            "evac_friends": "evac_friends",
            "evac_hotel": "evac_hotel",
            "evac_shelter": "evac_shelter",
            "stay": "stay",
            "phase": "phase",
            "immediacy": "immediacy_cum",
        }
        model_attributes = {
        "evac_agents": "evaced_agents",
        "average_evac_time": "average_evac_time",
        "hotel_choice": "hotel_choice",
        "friends_choice": "friends_choice",
        "shelter_choice": "shelter_choice",
        "stay_choice": "stay_choice",
        }

    return agent_attributes, model_attributes



