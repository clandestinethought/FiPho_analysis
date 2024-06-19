"""
This code functions to open the tank data and export it to a readable format for preprocessing and finally analysis
"""
import tdt
import numpy as np
import os
import matplotlib.pyplot as plt
import sys
import pandas as pd

## This function opens the tank and confirms the tank path, setup and camera
def open_tank(PATH, OFFSET, ID_A, ID_B, REGION, SENSOR):

    data = tdt.read_block(PATH, t1 = OFFSET)
    print(f"Mouse IDs: {ID_A} = Setup A, {ID_B} = Setup B \nBrain Region: {REGION} \nSensor: {SENSOR}")


    if ID_A != 'nan':
        #Extracts Data for Setup A
        ISOS_A = data.streams._405A.data
        signal_A = data.streams._465A.data
        #Creating a timeseries the same size as the data using the sampling rate.
        ISOS_ts_A = OFFSET + np.linspace(1, len(ISOS_A), len(ISOS_A))/data.streams._405A.fs
        signal_ts_A = OFFSET + np.linspace(1, len(signal_A), len(signal_A))/data.streams._465A.fs
        #Extracting timestamps for setup A (Camera 2) if camera setup changes alter this to Cam1
        TIMESTAMPS_A = data.epocs.Cam2.notes
        TIMESTAMPS_A.ts = TIMESTAMPS_A.ts + OFFSET
        SAMPLING_RATE_A = data.streams._465A.fs

    else:
        ISOS_A = 0
        TIMESTAMPS_A = 0
        SAMPLING_RATE_A = 0

    if ID_B != 'nan':
        #Extracts data for Setup B
        ISOS_B = data.streams._415A.data
        signal_B = data.streams._475A.data

        #Creating a timeseries the same size as the data using the sampling rate.
        ISOS_ts_B = OFFSET + np.linspace(1, len(ISOS_B), len(ISOS_B))/data.streams._415A.fs
        signal_ts_B = OFFSET + np.linspace(1, len(signal_B), len(signal_B))/data.streams._475A.fs

        #Extracting timestamps for setup B (Camera 1) if camera setup changes alter this to Cam2
        TIMESTAMPS_B = data.epocs.Cam1.notes
        TIMESTAMPS_B.ts = TIMESTAMPS_B.ts + OFFSET
        SAMPLING_RATE_B = data.streams._475A.fs

    else:
        ISOS_B = 0
        TIMESTAMPS_B = 0
        SAMPLING_RATE_B = 0

    if ID_A != 'nan':
        INFO_A = {
            'Mouse ID' : ID_A,
            'Brain Region' : REGION,
            'Sensor': SENSOR,
            'Setup' : 'Setup A',
            'Camera' : '2',
            'Sampling Rate': SAMPLING_RATE_A
        }
    else:
        INFO_A = 0

    if ID_B != 'nan':
        INFO_B = {
            'Mouse ID' : ID_B,
            'Brain Region' : REGION,
            'Sensor': SENSOR,
            'Setup' : 'Setup B',
            'Camera' : '1',
            'Sampling Rate': SAMPLING_RATE_B
        }
    else:
        INFO_B = 0
    
    if ID_A != 'nan':
        OUTPUTS_A = { 
            'ISOS': ISOS_A,
            'ISOS_ts' : ISOS_ts_A,
            'signal': signal_A,
            'signal_ts' : signal_ts_A,
        }
    else:
        OUTPUTS_A = 0

    if ID_B != 'nan':
        OUTPUTS_B = { 
            'ISOS': ISOS_B,
            'ISOS_ts' : ISOS_ts_B,
            'signal': signal_B,
            'signal_ts' : signal_ts_B,
        }
    else:
        OUTPUTS_B = 0
    
    if ID_A != 'nan':    
        #Graph for Setup A
        #Creating a graph of the raw data and time stamps for reference
        RAW_FIGURE_A, ax1=plt.subplots()
        plot1=ax1.plot(signal_ts_A, signal_A, 'g', label='Signal')
        ax2=plt.twinx()
        plot2=ax2.plot(ISOS_ts_A, ISOS_A, 'y', label='Isosbestic') 

        timestamp_ticks = ax1.plot(TIMESTAMPS_A.ts, np.full(np.size(TIMESTAMPS_A.ts), max(signal_A)), label='Timestamps', color='w', marker="|", mec = "k")

        ax1.set_ylim(min(signal_A) - 20, max(signal_A)+ 10)
        ax2.set_ylim(min(ISOS_A)-10 , max(signal_A)-20)
        ax1.set_xlabel('Time (milliseconds)')
        ax1.set_ylabel('Signal (mV)', color='g')
        ax2.set_ylabel('Isosbestic (mV)', color='y')
        ax1.set_title('Raw signals')

        lines = plot1 + plot2 + timestamp_ticks #line handle for legend
        labels = [l.get_label() for l in lines]  #get legend labels
        legend = ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.98, 0.50)) #add legend
        plt.close()
    else:
        RAW_FIGURE_A = 0

    if ID_B != 'nan':
        #Graph for Setup B
        #Creating a graph of the raw data and time stamps for reference
        RAW_FIGURE_B, ax1=plt.subplots()  # create a plot to allow for dual y-axes plotting
        plot1=ax1.plot(signal_ts_B, signal_B, 'g', label='Signal') #plot dLight on left y-axis
        ax2=plt.twinx()# create a right y-axis, sharing x-axis on the same plot
        plot2=ax2.plot(ISOS_ts_B, ISOS_B, 'y', label='Isosbestic') # plot TdTomato on right y-axis

        # Plot epochs as lines.
        timestamp_ticks = ax1.plot(TIMESTAMPS_B.ts, np.full(np.size(TIMESTAMPS_B.ts), max(signal_B)), label='Timestamps', color='w', marker="|", mec = "k")

        ax1.set_ylim(min(signal_B) - 20, max(signal_B)+ 10)
        ax2.set_ylim(min(ISOS_B)-10 , max(signal_B)-20)
        ax1.set_xlabel('Time (milliseconds)')
        ax1.set_ylabel('Signal (mV)', color='g')
        ax2.set_ylabel('Isosbestic (mV)', color='y')
        ax1.set_title('Raw signals')

        lines = plot1 + plot2 + timestamp_ticks #line handle for legend
        labels = [l.get_label() for l in lines]  #get legend labels
        legend = ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.98, 0.50)) #add legend
        plt.close()
    else:
        RAW_FIGURE_B = 0


    return ID_A, ID_B, INFO_A, INFO_B, OUTPUTS_A, OUTPUTS_B, TIMESTAMPS_A, TIMESTAMPS_B, SAMPLING_RATE_A, SAMPLING_RATE_B, RAW_FIGURE_A, RAW_FIGURE_B