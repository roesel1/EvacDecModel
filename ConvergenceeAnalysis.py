"""ConvergenceeAnalysis.py

This script runs a batch of simulations for an evacuation decision model using the Mesa framework,
performs convergence analysis on key agent decision metrics, and visualizes the results.
"""
from mesa import batch_run
import pandas as pd
from Model import EvacuationDec
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Set simulation parameters for the model runs
    params = {"init_individuals":[1000],         # Initial agent population
              "outcome_collection":"convergence" # Specify the outcome collection mode
              }
    # Run batch simulations using mesa's batch_run
    result_batch = batch_run(
        EvacuationDec,
        parameters=params,
        iterations=500,
        max_steps=88,
        number_processes= None,
        data_collection_period=1,
        display_progress=True,
    )
    # Transform the batch run results into a DataFrame
    df = pd.DataFrame(result_batch)
    # Filter to only the final step of each run
    df = df[df["Step"] == df["Step"].max()]
    df = df.reset_index()

    # List of metrics to plot
    metrics = ['average_evac_time', 'hotel_choice', 'friends_choice', 'stay_choice']

    # Calculate running mean and standardize for each metric
    for metric in metrics:
        df[f'{metric}_running_mean'] = df[metric].expanding().mean()
        mean = df[f'{metric}_running_mean'].mean()
        std = df[f'{metric}_running_mean'].std()
        df[f'{metric}_standardized'] = (df[f'{metric}_running_mean'] - mean) / std
    df = df.reset_index()
    df_correct =df[['average_evac_time', 'hotel_choice', 'friends_choice', 'stay_choice', "iteration","AgentID"]].groupby("iteration").mean()

    metrics = ['average_evac_time', 'hotel_choice', 'friends_choice', 'stay_choice']

    # Plotting on 2x2 subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    axs = axs.flatten()

    for idx, metric in enumerate(metrics):
        axs[idx].plot(df_correct.index + 1, df_correct[f'{metric}_standardized'], label=f'Std Running Mean: {metric}')
        # Add the 0.5 and -0.5 red reference lines with one shared label
        axs[idx].axhline(1, color="red", linestyle="--", linewidth=1)
        axs[idx].axhline(-1, color="red", linestyle="--", linewidth=1, label="One standardevation threshold")
        axs[idx].set_title(f'Convergence: {metric}')
        axs[idx].set_xlabel('Model Run')
        axs[idx].set_ylabel('Standardized Running Mean')
        axs[idx].grid(True)

        # Add both plot and reference line to the legend
        axs[idx].legend()

    plt.tight_layout()
    plt.show()
