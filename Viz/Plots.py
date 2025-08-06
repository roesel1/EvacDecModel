"""
Visualization module for creating various plots and charts related to evacuation simulation data.
Includes functionality for comparing model results with real data, plotting evacuation patterns,
phase distributions, population density, and environmental cues.
"""

import contextily as ctx
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import timedelta, datetime
import pandas as pd

def compare_real_data(data_model):
    """
    Compare model results with real evacuation data from Hurricane Irma.
    
    Args:
        data_model (dict): Dictionary containing model results with 'evac_agents' key
        
    Returns:
        None: Displays a matplotlib plot comparing model and real data histograms
    """
    # Define simulation start time and time step interval
    start_time = pd.Timestamp("2017-09-03 00:00:00")
    step_hours = 2
    # Extract evacuation agents data from model
    evac_agents = data_model["evac_agents"]

    # Create DataFrame with evacuation data and convert steps to datetime
    df_model = pd.DataFrame({
        "evac_agents": evac_agents,
    })
    # Calculate datetime for each step by adding time intervals to start time
    df_model["datetime"] = start_time + pd.to_timedelta(df_model.index * step_hours, unit="h")

    # Create list of datetime values repeated by evacuation count for histogram
    hist_values = []
    for idx, count in enumerate(evac_agents):
        # Repeat datetime value for each evacuee at that timestep
        hist_values.extend([df_model.loc[idx, "datetime"]] * count)

    # --- Real data section unchanged, except its datetime also lands in 'datetime' column ---
    df_irma = pd.read_csv(r"C:\Users\roelo\Downloads\times_irma.csv").reset_index()
    df_clean = df_irma.dropna()
    df_clean['last_9_chars'] = df_clean['Column81;Column82'].str[-10:]

    def convert_custom_datetime_column(series, year=2017, month=9):
        def parse_date(val):
            try:
                # Replace semicolon and parse
                val = val.replace(";", " ")
                partial_dt = datetime.strptime(val, "%d %I:%M %p")
                return datetime(year=year, month=month, day=partial_dt.day, hour=partial_dt.hour, minute=partial_dt.minute)
            except:
                return None
        return series.apply(parse_date)

    df_clean["datetime"] = convert_custom_datetime_column(df_clean["last_9_chars"])
    start = pd.Timestamp("2017-09-03 00:00:00")
    end = pd.Timestamp("2017-09-10 23:59:00")

    mask = (df_clean["datetime"] >= start) & (df_clean["datetime"] <= end)
    df_filtered = df_clean.loc[mask]

    fig, ax = plt.subplots(figsize=(15, 6))

    sns.histplot(x=df_filtered["datetime"], ax=ax, bins=50, kde=True, label='Survey Results')
    sns.histplot(x=hist_values, ax=ax, bins=50, kde=True, label='Model Results')
    ax.legend()
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    ax.tick_params(axis='x', rotation=90)
    ax.set_ylabel("Evacuees")
    ax.set_xlim(start, end)

    plt.show()

def evac_plot(data):
    """
    Create a bar plot showing evacuation decisions over time with important event markers.
    
    Args:
        data (pd.DataFrame): DataFrame containing evacuation data with evac_agents column
        
    Returns:
        None: Displays a matplotlib bar plot showing evacuation patterns over time
    """
    # Create working copy of data to avoid modifying original
    df = data
    # Define simulation start time and timestep interval
    start_time = pd.Timestamp("2017-09-03 00:00:00")
    step_hours = 2

    df['datetime'] = start_time + pd.to_timedelta(df.index * step_hours, unit='h')
    # Step 2: Plot histogram
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(df['datetime'], df['evac_agents'], width=pd.Timedelta(hours=2), align='center', color='cornflowerblue',
           edgecolor='black')

    # Step 3: Add vertical lines
    events = {
        'Hurricane Watch\n1000': pd.Timestamp('2017-08-23 10:00:00'),
        'Hurricane Warning\n0400': pd.Timestamp('2017-08-24 04:00:00'),
        'Landfall\n2200': pd.Timestamp('2017-08-25 22:00:00')
    }

    for label, event_time in events.items():
        ax.axvline(event_time, color='red', linestyle='--')
        ax.text(event_time, ax.get_ylim()[1] * 0.95, label, rotation=90, verticalalignment='top', color='red',
                fontsize=10)

    # Step 4: Formatting
    ax.set_xlabel('Date and time of evacuation decision')
    ax.set_ylabel('Frequency')
    ax.set_title('Simple Histogram of Date and Time of Evacuation Decision')

    # Formatting x-axis dates
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y\n%H:%M'))

    fig.autofmt_xdate()
    ax.tick_params(axis='x', rotation=90)
    plt.tight_layout()
    plt.show()

def phase_plot(data):
    """
    Create a stacked area plot showing the distribution of agents across different phases over time.
    
    Args:
        data (pd.DataFrame): DataFrame containing agent phase data with Step and phase columns
        
    Returns:
        None: Displays a matplotlib stacked area plot showing phase distribution
    """
    # Aggregate data to get count of agents in each phase at each timestep
    data_grouped = data.groupby(by=["Step", "phase"]).count()

    # start_time = datetime(2023, 8, 18, 0, 0, 0)
    start_time = pd.Timestamp("2017-09-03 00:00:00")
    df = data.copy()
    df['time'] = [start_time + timedelta(hours=2 * i) for i in df["Step"]]

    # Reshape the grouped data
    df_unstacked = data_grouped.unstack(level=1).fillna(0)
    df_unstacked = df_unstacked.sort_index(axis=1)

    # Map Step index to actual time
    step_to_time = df.set_index("Step")["time"].to_dict()
    # print(step_to_time)
    time_index = df_unstacked.index.map(step_to_time)
    # print(df_unstacked)
    # Prepare data for stackplot
    steps = time_index
    phase_values = [df_unstacked[('AgentID', phase)] for phase in df_unstacked.columns.levels[1]]

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.stackplot(steps, phase_values, labels=[f'Phase {p}' for p in df_unstacked.columns.levels[1]])
    ax.legend(loc='upper left')
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=24))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    ax.tick_params(axis='x', rotation=90)
    plt.ylabel('Number of Agents')
    ax.set_title('Phase Distribution per Step')
    plt.tight_layout()
    plt.show()


def kde2d_pop_plot(data):
    """
    Create a 2D kernel density estimation plot of population distribution with a base map.
    Shows spatial density of population using kernel density estimation overlaid on OpenStreetMap.
    
    Args:
        data (GeoDataFrame): GeoDataFrame containing population location data and geometries
        
    Returns:
        None: Displays a matplotlib plot with KDE overlay on OpenStreetMap base layer
    """

    fig, ax = plt.subplots(figsize=(10, 6))
    # data.plot(ax=ax, column=data[data.columns[2]], alpha=
    # print(type(data[data.columns[5]]))
    data = data.set_geometry(data.columns[5])
    data["point"]=data[data.columns[5]].centroid

    # Add basemap
    sns.kdeplot(x=data["point"].x, y=data["point"].y, levels=10, thresh=0.05, gridsize=500, fill=True,
                cmap="PuBu", ax=ax, alpha=0.8, legend=True)
    # ax.legend(title="Legend")
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)  # Change provider as needed

    # Show plot
    plt.show()

# def phase_1_viz(data):
def cum_evac(data):
    """
    Create a line plot showing cumulative number of evacuated people over time.
    Visualizes the total evacuation progress by summing evacuees at each timestep.
    
    Args:
        data (pd.DataFrame): DataFrame containing evacuation data with evac_agents column counting evacuees per timestep
        
    Returns:
        None: Displays a matplotlib line plot showing cumulative evacuation totals
    """
    # 1. Copy and calculate cumulative sum
    df = data.copy()
    df['cumulative_evacuated'] = df['evac_agents'].cumsum()

    # 2. Create a proper 'time' column
    start_time = pd.Timestamp("2017-09-03 23:00:00")
    df['time'] = [start_time + timedelta(hours=2 * i) for i in df.index]

    # 3. Plot
    sns.set(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    sns.lineplot(data=df, x='time', y='cumulative_evacuated', marker='o', ax=ax1)

    # 4. Format x-axis for better date display
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=24))  # tick every 24 hours
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    ax1.tick_params(axis='x', rotation=90)

    # 5. Labels and title
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Total Evacuated')
    ax1.set_title('Total Number of People Evacuated Over Time')

    plt.tight_layout()
    plt.show()


def plot_environmental_and_social_cues(df):
    """
    Create a multi-line plot showing various environmental and social cues over time.
    Visualizes how different factors (weather, media, risk perception) change during evacuation period.
    Includes vertical markers for key events like storm watches and warnings.
    
    Args:
        df (pd.DataFrame): DataFrame containing cue data including:
            - risk_perception: Agent's perceived risk level
            - wind_cue: Wind intensity factor
            - rain_cue: Rainfall intensity factor
            - media_cue: Media coverage intensity
            - immediacy: Urgency factor
    
    Returns:
        None: Displays a matplotlib line plot with multiple cues plotted over time
        
    Notes:
        - Each index step represents 2 hours in simulation time
        - Starting time is set to 2017-09-03 00:00:00
        - X-axis shows datetime labels every 6 hours for readability
        - Includes vertical markers for storm watch/warning events
    """
    # Create datetime index
    start_time = pd.Timestamp("2017-09-03 00:00:00")
    df = df.copy()
    df['time'] = [start_time + timedelta(hours=2 * i) for i in df["Step"]]
    print(df['time'])
    # Academic font & layout
    mpl.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'Computer Modern Roman'],
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'legend.fontsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10
    })

    sns.set(style="whitegrid", palette="muted")

    fig, ax1 = plt.subplots(figsize=(14, 5))
    # Media cue plot (left)
    # ax1 = fig.add_subplot(gs[0, 0])
    sns.lineplot(x='time', y='risk_perception', data=df, ax=ax1, label='Risk perception', color='dimgray')
    sns.lineplot(x='time', y='wind_cue', data=df, ax=ax1, label='Wind Cue', color='steelblue')
    sns.lineplot(x='time', y='rain_cue', data=df, ax=ax1, label='Rain Cue', color='seagreen')
    sns.lineplot(x='time', y='media_cue', data=df, ax=ax1, label='Media Cue', color='red')
    sns.lineplot(x='time', y='immediacy', data=df, ax=ax1, label='Immediacye', color='pink')

    ax1.axvline(df.loc[df["Step"] == 55, "time"].values[0], color='orange', linestyle='--', linewidth=2)
    ax1.text(
        df.loc[df["Step"] == 55, "time"].values[0],
        ax1.get_ylim()[1] * 0.95,
        "Storm watch",
        color='orange',
        rotation=90,
        verticalalignment='top',
        fontsize=11
    )

    ax1.axvline(df.loc[df["Step"] == 60, "time"].values[0], color='green', linestyle='--', linewidth=2)
    ax1.text(
        df.loc[df["Step"] == 60, "time"].values[0],
        ax1.get_ylim()[1] * 0.95,
        "Storm warning",
        color='green',
        rotation=90,
        verticalalignment='top',
        fontsize=11
    )

    ax1.set_title("Cues")
    ax1.set_xlabel("Date-Time")
    ax1.set_ylabel("Cue Intensity")
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=24))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    ax1.tick_params(axis='x', rotation=90)
    events = {
        'Hurricane Watch\n1000': pd.Timestamp('2017-08-23 10:00:00'),
        'Hurricane Warning\n0400': pd.Timestamp('2017-08-24 04:00:00'),
        'Landfall\n2200': pd.Timestamp('2017-08-26 22:00:00')
    }
    plt.show()
    
    
