
# README Master thesis Roelof Kooijman

This README file was last motified on: 31-07-2025

### Author & Contact:
Created by: Roelof Kooijman

All questions about the code, thesis, or anything else can be sent to the following email:
[roelofkooijman@gmail.com](mailto:roelofkooijman@gmail.com)
## Institution: 

Delft University of Technology : Faculty Technology, Policy and Management.

### Purpose:

The project aims to provide insight into how psychosocial factors, environmental factors and evacuation warning 
communication influence evacuation decision making in the case of a hurricane

### Technologies used

The code is written and tested for Python 3.11.11. The specific packages used are given in the requirement.txt file. To
use the code an environment for Python should be created and the packages stated in the requirements.txt should be 
installed. The data used is stored in .xlsx and .csv formats, so a viewer that can read this format is required if only 
interested in data.
## WARNING
The code is based on large data files that could not be included on GitHub. It only contains the data required to run the ABM part. If access to the large data files is needed, a request can be sent to my email. The tables underneath do include files, which are not present in this repository.

### Purpose code files
Various Python files or jupyter notebooks are included. The code files are divided in separate folders based on their 
purpose. The overall structure of the directory is given underneath. The purpose of each folder will be discussed 
individually. It must be noted that the main files of the ABM are located in the root directory itself.


    Thesis/
        ├── ['Texas']['Harris County']/
        ├── ACSData/                                          
        ├── archives/
        ├── prullenbak/
        ├── RainData/
        ├── regression models/
        ├── Viz/
        ├── Weather/
        ├── Agent.py
        ├── BaseCaseRun.ipynb
        ├── ConvergenceeAnalysis.py
        ├── helper_functions.py
        ├── main.py
        ├── Model.py
        ├── PolicyRun.ipynb
        ├── README.md
        ├── Representative_sample_elements.ipynb
        ├── run_config.py
        ├── ScenarioRun.ipynb
        ├── SensitivityAnalysis.ipynb
        └── Verification.ipynb

| Folder            | Code file                                                  | Purpose                                                                                                                                                                                                                                                         |
|-------------------|------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACSData           | [ACS_cleaning.py](ACSData/ACS_cleaning.py)                 | This script processes American Community Survey (ACS) data by cleaning and transforming  the data from Excel and GDB files into CSV format.                                                                                                                     |
|                   | [ACS_merging.py](ACSData/ACS_merging.py)                   | This script processes and merges American Community Survey (ACS) data files.It combines demographic data (education, income, age, race, vehicle ownership) with geographic boundaries and creates a standardized file for analysis.                             |
| regression models | [Statistics1.ipynb](regression%20models/Statistics1.ipynb) | This notebook provides the first part of the survey analysis. It contains the CFA, EFA and Correlation analysis for evacuation intention                                                                                                                        |
|                   | [Statistics2.ipynb](regression%20models/Statistics2.ipynb) | This notebook is the second part of the survey analysis. It contains the correlation analysis for destination choice, the multinominal logistic regression model and the additional analyses for the Agent-based model.                                         |
| Weather           | [Laplace_inter.py](Weather/Laplace_inter.py)               | Contains the laplace interpolation methode                                                                                                                                                                                                                      |
|                   | [NHC_data_retrieve.py](Weather/NHC_data_retrieve.py)       | This script retrieves and processes hurricane data from the National Hurricane Center (NHC).It downloads various types of hurricane-related data (storm surge, forecast, best track, wind speed) and converts them into shapefile formats for further analysis. |
|                   | [RainWindCues.ipynb](Weather/RainWindCues.ipynb)           | Computes the wind and rain cues for the tract areas of Miami-Dade county and adds them to [data.gpkg](ACSData/%5B%27Texas%27%5D%5B%27Harris%20County%27%5D/data.gpkg)                                                                                           |
|                   | [storm.ipynb](Weather/storm.ipynb)                         | Computes the storm surge watch/warning for the tract areas of Miami-Dade county and adds them to [data.gpkg](ACSData/%5B%27Texas%27%5D%5B%27Harris%20County%27%5D/data.gpkg)                                                                                    |
| Root folder       | [Agent.py](Agent.py)                                       | Defines the `Individual` agent class for use in an agent-based model (ABM) simulation.                                                                                                                                                                          |
|                   | [BaseCaseRun.ipynb](BaseCaseRun.ipynb)                     | This notebook is used to run the model for the base case results. Here, all the default parameter values have been used.                                                                                                                                        |
|                   | [ConvergenceeAnalysis.py](ConvergenceeAnalysis.py)         | This script runs a batch of simulations for an evacuation decision model using the Mesa framework, performs convergence analysis on key agent decision metrics, and visualizes the results.                                                                     |
|                   | [helper_functions.py](helper_functions.py)                 | Contains function used in the ABM model                                                                                                                                                                                                                         |
|                   | [main.py](main.py)                                         | Used to run model once and show some plots. Main purpose to check if code still works after making changes                                                                                                                                                      |
|                   | [Model.py](Model.py)                                       | Module for implementing an evacuation decision model.                                                                                                                                                                                                           |
|                   | [PolicyRun.ipynb](PolicyRun.ipynb)                         | Policy run This notebook is used to run the policy analysis.                                                                                                                                                                                                    |
|                   | [run_config.py](run_config.py)                             | This file is used to quickly change the data the datacollector needs to save.                                                                                                                                                                                   |
|                   | [ScenarioRun.ipynb](ScenarioRun.ipynb)                     | This notebook is used to run the scenario analysis. The cell below contains the different values for each experiments.                                                                                                                                          |
|                   | [SensitivityAnalysis.ipynb](SensitivityAnalysis.ipynb)     |   This notebook is used to do the sensitivity analysis.                                                                                                                                                                                                                                                              |
|                   | [Verification.ipynb](Verification.ipynb)                   | This notebook contains extra code used for verification.                                                                                                                                                                                                                                                       |

### Purpose data files
Besides the code files, various sources of data are used or created. The table below gives an overview and the purpose of 
the used data files. 

| Folder                                   | Code file                                                                                                                                               | Purpose                                                                                                                                                   |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| ACSData                                  | [['Florida']['Miami-Dade County']](ACSData/%5B%27Florida%27%5D%5B%27Miami-Dade%20County%27%5D)                                                          | Contains the combined data fir Miami-Dade county form the American community survey of which only the tract areas and population density is used.         |
|                                          | [['Texas']['Harris County']](ACSData/%5B%27Texas%27%5D%5B%27Harris%20County%27%5D)                                                                      | Contains the combined data fir Miami-Dade county form the American community survey, but not used                                                         |
|                                          | [ACS_layers.gdb](ACSData/ACS_layers.gdb)                                                                                                                | Database containing the American community survey data layers from ArcGIS Pro                                                                             |
|                                          | [ACS2023_Table_Shells.xlsx](ACSData/ACS2023_Table_Shells.xlsx)                                                                                          | Reference tabel for variable codes of American community survey                                                                                           |
|                                          | ACS_[1-4].csv                                                                                                                                           | Seperate csv files with understandable column names made out of [ACS_layers.gdb](ACSData/ACS_layers.gdb)                                                  |
|                                          | [ASC_data.gpkg](ACSData/ASC_data.gpkg)                                                                                                                  | Database containing merged result of the American community survey  data                                                                                  |
|                                          | [ColumnsToKeep](ACSData/ColumnsToKeep)                                                                                                                  | File storing the names of the columns required for the model. Only the geometry of the tracts and population density is used                              |
| archives                                 | [policy_runs](archives/policy_runs)                                                                                                                     | Folder storing csv files containing the results of one experiment used for policy analysis                                                                |
|                                          | [scenario_runs](archives/scenario_runs)                                                                                                                 | Folder storing csv files containing the results of one experiment used for scenario analysis                                                              |
|                                          | [senstivity_runs](archives/senstivity_runs)                                                                                                             | Folder storing csv files containing the results of one experiment used for sensitvity analysis                                                            |
|                                          | [media.csv](archives/media.csv)                                                                                                                         | Contains result of model experiment used for verfication                                                                                                  |
|                                          | [phase.csv](archives/phase.csv)                                                                                                                         | Contains result of model experiment used for verfication                                                                                                  |
|                                          | [rain.csv](archives/rain.csv)                                                                                                                           | Contains result of model experiment used for verfication                                                                                                  |
|                                          | [win.csv](archives/win.csv)                                                                                                                             | Contains result of model experiment used for verfication                                                                                                  |
| RainData                                 | [Miami](RainData/Miami)                                                                                                                                 | Folder containing image (tiff) containing rain data per half an hour per day                                                                              |
| regression models                        | [LABEL_PADM-PA Survey 2_July 18, 2025_20.24.xlsx](regression%20models/LABEL_PADM-PA%20Survey%202_July%2018%2C%202025_20.24.xlsx)                        | Raw data with label values. Excluded from github for privacy reasons. Contact [roelofkooijman@gmail.com](mailto:roelofkooijman@gmail.com) if essential    |
|                                          | [PADM-PA Survey 2_July 17, 2025_13.07_final.xlsx](regression%20models/PADM-PA%20Survey%202_July%2017%2C%202025_13.07_final.xlsx)[Miami](RainData/Miami) | Raw data with numbered values. Excluded from github for privacy reasons. Contact [roelofkooijman@gmail.com](mailto:roelofkooijman@gmail.com) if essential |
| regression models/<br/>reg_results_FINAL | [factor_scores.csv](regression%20models/reg_results_FINAL/factor_scores.csv)                                                                            | Factor score values for tht use of the logistic model in the ABM                                                                                          |
|                                          | [factor_scores.xlsx](regression%20models/reg_results_FINAL/factor_scores.xlsx)                                                                          | Factor values for training logistic model                                                                                                                 |
|                                          | [finalized_model.sav](regression%20models/reg_results_FINAL/finalized_model.sav)                                                                        | Contains a logistic regression model for destination choice. Used in the ABM                                                                              |
|                                          | [media_weights.csv](regression%20models/reg_results_FINAL/media_weights.csv)                                                                            | Media data for trust and frequency. Used in the ABM                                                                                                       |
|                                          | [preditor_data.csv](regression%20models/reg_results_FINAL/preditor_data.csv)                                                                            | Factor score values for tht use of the logistic model in the ABM                                                                                          |
|                                          | [weights.csv](regression%20models/reg_results_FINAL/weights.csv)                                                                                        | Weights for thee RA threshold and perception cues. Used in the ABM                                                                                        |
| Weather                                  | [Miami](Weather/Miami)                                                                                                                                  | Contains shapefiles for the wind data                                                                                                                     |
                                                                                                                                                      | 
