from Model import EvacuationDec
from Viz.Plots import *
"""
Used to run model once and show some plots. Main purpose to check if code still works after making changes
"""
model = EvacuationDec(init_individuals=1000,outcome_collection="SingleRun",watch_shift=0, communication_timing=0)


# Different plots of which code is located at Viz.py
data = model.datacollector.get_agent_vars_dataframe().reset_index()
phase_plot(data)
data_model = model.datacollector.get_model_vars_dataframe()
compare_real_data(data_model)
plot_environmental_and_social_cues(data)



