import geopandas as gpd
import pandas as pd
import os
import random
import re

def population_bootstrapper(init_individuals,seed = None):
    """
    Bootstraps population data by resampling predictors and weights.

    Each of the predictor and weight datasets is resampled with replacement
    to create a population of synthetic agents.

    Args:
        init_individuals (int): Number of synthetic agents to generate.
        seed (int, optional): Seed for random number generator. If None, a random seed is used.

    Returns:
        tuple: Three pandas.DataFrames containing resampled predictors, weights, and media weights.
    """

    # Select random number for seed
    if seed is None:
        rand_int = random.randint(1, 1000000)

    # load survey data
    predictors_df = pd.read_csv("regression models/reg_results_FINAL/preditor_data.csv")
    weights = pd.read_csv("regression models/reg_results_FINAL/weights.csv")
    media_weights = pd.read_csv("regression models/reg_results_FINAL/media_weights.csv")

    # Remove the first colum which got added when saving the data
    predictors_df.drop(columns=predictors_df.columns[0],inplace=True)
    weights.drop(columns=weights.columns[0], inplace=True)
    media_weights.drop(columns=media_weights.columns[0], inplace=True)

    # Resample init_individuals agents with bootstrap
    resampled_factors = predictors_df.sample(n=init_individuals,replace=True,random_state=rand_int).reset_index(drop=True)
    resampled_weights = weights.sample(n=init_individuals, replace=True, random_state=rand_int).reset_index(drop=True)
    resampled_media_weights = media_weights.sample(n=init_individuals, replace=True, random_state=rand_int).reset_index(drop=True)
    return resampled_factors, resampled_weights, resampled_media_weights

def shift_watch_warning(warning_list, timing=0, gap=0, fill_value=0):
    """
    Shifts 'watch' and 'warning' signals in a timeline.

    Shifts both the watch (0.5) and warning (1) together in time (timing).
    Additionally, shifts the watch earlier by 'gap' time steps relative to the warning.
    Handles filling and preserves timeline length.

    Parameters:
        warning_list (list of float): Timeline containing warning (1), watch (0.5), or neutral (0) values.
        timing (int): Time shift for both watch and warning (positive is later).
        gap (int): Steps to place watch before warning.
        fill_value (float): Value to use for padding (default: 0).

    Returns:
        list of float: Modified timeline with shifted watch and warning events.
    """
    timing = -timing
    timing = timing +1
    if gap != 0:
        timing +=1
    gap = gap + 3
    import copy
    result = copy.deepcopy(warning_list)

    # Find first warning
    try:
        first_warning = result.index(1)
    except ValueError:
        return shift_warnings(result, timing, fill_value)

    # Remove existing watch (0.5)
    result = [v for v in result if v != 0.5]

    # Insert watch `gap` steps before the warning
    watch_time = first_warning - gap
    if watch_time < 0:
        # Pad beginning if needed
        result = [fill_value] * (-watch_time) + result
        watch_time = 0

    # Ensure list is long enough
    if watch_time >= len(result):
        result += [fill_value] * (watch_time - len(result) + 1)

    # Place the watch
    result[watch_time] = 0.5

    # Apply global timing shift
    result = shift_warnings(result, timing, fill_value)

    # Trim or pad to original length
    if len(result) > len(warning_list):
        result = result[:len(warning_list)]
    elif len(result) < len(warning_list):
        result += [fill_value] * (len(warning_list) - len(result))

    return result

def shift_warnings(warning_list, shift_steps, fill_value=0):
    """
    Shifts a warning timeline forward or backward.

    Args:
        warning_list (list): Original warning timeline.
        shift_steps (int): Positive value shifts forward; negative shifts backward.
        fill_value (float): Value used for padding when shifting.

    Returns:
        list: The shifted timeline, of the same length as original.
    """
    if shift_steps > 0:
        return [fill_value] * shift_steps + warning_list[:-shift_steps]
    elif shift_steps < 0:
        return warning_list[-shift_steps:] + [fill_value] * (-shift_steps)
    else:
        return warning_list.copy()

def retrieve_wind_cue(model):
    """
    Calculates the mean wind cue among agents within the model. Used by the
    datacollector in the model class
    """
    values = model.agents.get("wind_cue")
    return sum(values)/len(values)

def retrieve_rain_cue(model):
    """
    Calculates the mean rain cue among agents within the model. Used by the
    datacollector in the model class
    """
    values = model.agents.get("rain_cue")
    return sum(values)/len(values)

def agent_init_data(state, county):
    """
    Loads geospatial demographic data for a specified state and county. It must be noted that
    the final code does only use the geographical locations and tract population densities.

    If dedicated data exists for the provided state and county, loads it directly.
    Otherwise, processes a general dataset, extracting relevant areas, normalizing features,
    and saving the result for future use.

    Args:
        state (str or list of str): State abbreviation(s).
        county (str or list of str): County name(s) or code(s).

    Returns:
        geopandas.GeoDataFrame: GeodataFrame of processed agent initialization data.
    """
    # If data already exits, then load that
    if os.path.isdir(f"./ACSDATA/{state}{county}"):
        # print("ja")
        return gpd.read_file(f"./ACSDATA/{state}{county}/data.gpkg", layer='Data')
    else:
        # Open ACS data for the whole United States
        final_gdf = gpd.read_file("./ACSDATA/ASC_data.gpkg", layer='Data')
        # Combine education levels
        some_highschool =final_gdf[final_gdf.columns[7:14]].sum(1)
        final_gdf = final_gdf.drop(columns=final_gdf.columns[7:14])
        final_gdf.insert(7,"some_highschool",some_highschool)
        # Select The tracts within the required State and county
        gdf_AOI = final_gdf[final_gdf["County"].isin(county)]
        gdf_AOI = gdf_AOI[gdf_AOI["State"].isin(state)]

        indexes_to_remove = []
        # If the value of a tract is zero, then remove them
        for i in [[6, 16], [17, 33], [34, 53], [55, 70]]:
            a = gdf_AOI[gdf_AOI.columns[i[0]:i[1]]].sum(axis=1)
            zero_in_series = a[a == 0]
            # print(list(zero_in_series.index))
            [indexes_to_remove.append(j) for j in zero_in_series.index]
        indexes_to_remove = set(indexes_to_remove)
        df_indexed_removed = gdf_AOI.drop(indexes_to_remove)
        # Calculate proportions for every demographic
        for i in [[6, 16], [17, 33], [34, 53], [55, 70]]:
            a = df_indexed_removed[df_indexed_removed.columns[i[0]:i[1]]].sum(axis=1)
            df_indexed_removed[df_indexed_removed.columns[i[0]:i[1]]] = df_indexed_removed[
                df_indexed_removed.columns[i[0]:i[1]]].div(a, axis=0)
        df_indexed_removed["PopDense"] = df_indexed_removed["AgeTotal"] / df_indexed_removed["AgeTotal"].sum()
        os.makedirs(f"./ACSDATA/{state}{county}")
        df_indexed_removed.to_file(f"./ACSDATA/{state}{county}/data.gpkg", driver='GPKG', layer='Data')
    return df_indexed_removed




def parse_np_float_string(val):
    """
    Parses a string containing numpy float representations and returns a list of floats.
    Quite a lazy approach, but storing the strings correctly somehow was more difficult.

    Useful for converting serialized numpy float lists to native Python floats.

    Args:
        val (str): String formatted as numpy float array, e.g., '[np.float64(1.2), np.float64(3.4)]'

    Returns:
        list of float: Parsed float values.
    """
    # Remove the wrapping quotes if present
    if isinstance(val, str) and val.startswith("'") and val.endswith("'"):
        val = val[1:-1]

    # Replace np.float64(...) with just the number inside
    cleaned = re.sub(r'np\.float64\(([^)]+)\)', r'\1', val)

    # Split into individual float values and convert
    return [float(x.strip()) for x in cleaned.strip('[]').split(',') if x.strip()]


def closest_neighbours(model, id,nn):
    """
    Finds the nearest neighbors for a given agent
    by unique id using KD-tree defined in the model.

    Args:
        model: A model object, must have 'pos_dict', 'tree', and 'tree.data'.
        id (int): Unique ID of the agent whose neighbors are to be found.
        nn (int): Number of neighbors to find.

    Returns:
        list: List of agent objects for the nearest neighbors, excluding the agent itself.
    """
    a = [list(model.pos_dict.keys())[uq_id] for uq_id in
         model.tree.query(model.tree.data[list(model.pos_dict.keys())[id-1].unique_id - 1], k=nn + 1)[1]]
    return [i for i in a if i.unique_id != id]