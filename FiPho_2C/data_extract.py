import import_tank_v2
import preprocessing_v2
import pandas as pd
import os
import csv
import matplotlib.pyplot as plt
import matplotlib.figure as fig
from tqdm import tqdm
import numpy as np

#Change this path to the folder you want the outputs to be saved and put the settings excel file into this folder.
print("Please paste in the path to the output directory")
output_file_path = input()
settings_path = (f'{output_file_path}/settings.xlsx')
settings = pd.read_excel(settings_path)

for i in range(0,len(settings)):
    treatment = str(settings['treatment_name'][i])

    #creating treatment directory in output directory
    treatment_path = os.path.join(output_file_path, treatment)
    if os.path.exists(treatment_path) == False:
        os.mkdir(treatment_path)

    (ID_A, ID_B, INFO_A, INFO_B,
    OUTPUTS_A, OUTPUTS_B,
    TIMESTAMPS_A, TIMESTAMPS_B,
    SAMPLING_RATE_A, SAMPLING_RATE_B, RAW_FIGURE_A, RAW_FIGURE_B) = import_tank_v2.open_tank(
        PATH = settings['path'][i], 
        OFFSET = int(settings['offset'][i]),
        ID_A = str(settings['setup_a'][i]),
        ID_B = str(settings['setup_b'][i]),
        REGION = str(settings['region'][i]),
        SENSOR = str(settings['sensor'][i])
        )
    
    #creating output for setup A.
    if ID_A != 'nan':
        setup_A_path = os.path.join(treatment_path, ID_A)
        if os.path.exists(setup_A_path) == False:
            os.mkdir(setup_A_path)
        INFO_A = pd.DataFrame(INFO_A, index = [0])
        path = os.path.join(setup_A_path, 'info.csv')
        INFO_A.to_csv(path)
    else:
        print('Setup A is empty.')

    if ID_B != 'nan':
        #creating output for setup B
        setup_B_path = os.path.join(treatment_path, ID_B)
        if os.path.exists(setup_B_path) == False:
            os.mkdir(setup_B_path)

        INFO_B = pd.DataFrame(INFO_B, index = [0])
        path = os.path.join(setup_B_path, 'info.csv')
        INFO_B.to_csv(path)
    else:
        print('Setup B is empty')
    


    if ID_A != 'nan':
        #Runs the functions for setup A
        filtered_data, filtered_figure = preprocessing_v2.zero_phase_filter(OUTPUTS_A, SAMPLING_RATE_A, TIMESTAMPS_A)
        detrended_data, exponential_fit_figure, detrended_figure, exponential_fit = preprocessing_v2.photo_bleach_correction(filtered_data, TIMESTAMPS_A)
        motion_corrected_data, motion_figure = preprocessing_v2.motion_correction(detrended_data, TIMESTAMPS_A)
        normalised_data, dF_F_plot, zscore_plot = preprocessing_v2.normalisation(motion_corrected_data, exponential_fit, TIMESTAMPS_A)

        data_path = os.path.join(setup_A_path, 'data')
        os.mkdir(data_path)

        raw_data = pd.DataFrame(OUTPUTS_A)
        raw_data_path = os.path.join(data_path, 'raw_data.csv')
        raw_data.to_csv(raw_data_path)

        filtered_data = pd.DataFrame(filtered_data)
        filtered_data_path = os.path.join(data_path, 'filtered_data.csv')
        filtered_data.to_csv(filtered_data_path)

        detrended_data = pd.DataFrame(detrended_data)
        detrended_data_path = os.path.join(data_path, 'detrended_data.csv')
        detrended_data.to_csv(detrended_data_path)

        motion_corrected_data = pd.DataFrame(motion_corrected_data)
        motion_corrected_data_path = os.path.join(data_path, 'motion_corrected_data.csv')
        motion_corrected_data.to_csv(motion_corrected_data_path)

        normalised_data = pd.DataFrame(normalised_data)
        normalised_data_path = os.path.join(data_path, 'normalised_data.csv')
        normalised_data.to_csv(normalised_data_path)

        timestamps = pd.DataFrame(TIMESTAMPS_A)
        timestamps_path = os.path.join(setup_A_path, 'timestamps.csv')
        timestamps.to_csv(timestamps_path)

        #makes a directory for the figures
        figure_path = os.path.join(setup_A_path, 'figures')
        os.mkdir(figure_path)

        raw_figure_path = os.path.join(figure_path, 'raw_figure.png')
        RAW_FIGURE_A.savefig(raw_figure_path, dpi = 300)

        filtered_figure_path = os.path.join(figure_path, 'filtered_figure.png')
        filtered_figure.savefig(filtered_figure_path, dpi = 300)

        expfit_figure_path = os.path.join(figure_path, 'exp_fit_figure.png')
        exponential_fit_figure.savefig(expfit_figure_path, dpi = 300)

        detrended_figure_path = os.path.join(figure_path, 'detrended_figure.png')
        detrended_figure.savefig(detrended_figure_path, dpi = 300)

        motion_figure_path = os.path.join(figure_path, 'motion_figure.png')
        motion_figure.savefig(motion_figure_path, dpi = 300)

        dF_F_path = os.path.join(figure_path, 'dF_F.png')
        dF_F_plot.savefig(dF_F_path, dpi = 300)

        zscore_path = os.path.join(figure_path, 'zscore.png')
        zscore_plot.savefig(zscore_path, dpi = 300)

    #Runs the functions for setup B
    if ID_B != 'nan':
        filtered_data, filtered_figure = preprocessing_v2.zero_phase_filter(OUTPUTS_B, SAMPLING_RATE_B, TIMESTAMPS_B)
        detrended_data, exponential_fit_figure, detrended_figure, exponential_fit = preprocessing_v2.photo_bleach_correction(filtered_data, TIMESTAMPS_B)
        motion_corrected_data, motion_figure = preprocessing_v2.motion_correction(detrended_data, TIMESTAMPS_B)
        normalised_data, dF_F_plot, zscore_plot = preprocessing_v2.normalisation(motion_corrected_data, exponential_fit, TIMESTAMPS_B)

        data_path = os.path.join(setup_B_path, 'data')
        os.mkdir(data_path)

        raw_data = pd.DataFrame(OUTPUTS_B)
        raw_data_path = os.path.join(data_path, 'raw_data.csv')
        raw_data.to_csv(raw_data_path)

        filtered_data = pd.DataFrame(filtered_data)
        filtered_data_path = os.path.join(data_path, 'filtered_data.csv')
        filtered_data.to_csv(filtered_data_path)

        detrended_data = pd.DataFrame(detrended_data)
        detrended_data_path = os.path.join(data_path, 'detrended_data.csv')
        detrended_data.to_csv(detrended_data_path)

        motion_corrected_data = pd.DataFrame(motion_corrected_data)
        motion_corrected_data_path = os.path.join(data_path, 'motion_corrected_data.csv')
        motion_corrected_data.to_csv(motion_corrected_data_path)

        normalised_data = pd.DataFrame(normalised_data)
        normalised_data_path = os.path.join(data_path, 'normalised_data.csv')
        normalised_data.to_csv(normalised_data_path)

        timestamps = pd.DataFrame(TIMESTAMPS_B)
        timestamps_path = os.path.join(setup_B_path, 'timestamps.csv')
        timestamps.to_csv(timestamps_path)

        #makes a directory for the figures
        figure_path = os.path.join(setup_B_path, 'figures')
        os.mkdir(figure_path)

        raw_figure_path = os.path.join(figure_path, 'raw_figure.png')
        RAW_FIGURE_B.savefig(raw_figure_path, dpi = 300)

        filtered_figure_path = os.path.join(figure_path, 'filtered_figure.png')
        filtered_figure.savefig(filtered_figure_path, dpi = 300)

        expfit_figure_path = os.path.join(figure_path, 'exp_fit_figure.png')
        exponential_fit_figure.savefig(expfit_figure_path, dpi = 300)

        detrended_figure_path = os.path.join(figure_path, 'detrended_figure.png')
        detrended_figure.savefig(detrended_figure_path, dpi = 300)

        motion_figure_path = os.path.join(figure_path, 'motion_figure.png')
        motion_figure.savefig(motion_figure_path, dpi = 300)

        dF_F_path = os.path.join(figure_path, 'dF_F.png')
        dF_F_plot.savefig(dF_F_path, dpi = 300)

        zscore_path = os.path.join(figure_path, 'zscore.png')
        zscore_plot.savefig(zscore_path, dpi = 300)

print('Export Complete')
