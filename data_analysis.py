'''
This code functions to normalise the data around each timestamp grouped by timestamp type into seperate CSVs
'''
import pandas as pd
import os 
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


print('Please input path to settings file: ')
output_file_path = input()
settings_path = (f'{output_file_path}/settings.xlsx')
settings = pd.read_excel(settings_path)

#loop through settings file to extract directories for treatment and subjects.
treatments = list(set(settings['treatment_name']))
setup_A = list(set(settings['setup_a']))
setup_B = list(set(settings['setup_b']))
setup_A.extend(setup_B)
subjects = [x for x in setup_A if x == x]
subjects = [str(i) for i in subjects]


print(f"Exporting timestamps \nSubjects: {subjects} \nTreatments: {treatments}")

for treatment in treatments:
    treatment_path = os.path.join(output_file_path, treatment)
    for subject in subjects:
        #setting paths to timestamps and normalised data
        subject_path = os.path.join(treatment_path, subject)
        data_path = os.path.join(subject_path,'data/normalised_data.csv')
        ts_path = os.path.join(subject_path, 'timestamps.csv')

        if os.path.exists(subject_path) == False:
            continue
        else:

            #open timestamps.csv and normalised data
            timestamps = pd.read_csv(ts_path, index_col = 0)
            data = pd.read_csv(data_path, index_col = 0)

            #create new directory called timestamped data
            ts_dir = os.path.join(subject_path, 'timestamped_data')
            if os.path.exists(ts_dir) == False:
                os.mkdir(ts_dir)

            #down sample the normalised data for ease of import into GraphPad.
            shortened_data = pd.DataFrame(columns = ['time', 'dF_F', 'zscore'])

            for i in range(0, len(data), 10):
                lst = data[:][i:i+9]
                lst = pd.DataFrame(lst.mean())
                lst = lst.transpose()
                shortened_data = pd.concat([shortened_data, lst], ignore_index = True)

            #add timestamps to the shortened data
            length = len(shortened_data['time'])
            events = np.zeros(shape = ((length),2))
            events = pd.DataFrame(events, columns = ['event_name', 'event_index'])

            for x in range(0,len(timestamps['ts'])):
                for y in range (0, len(shortened_data['time'])):
                    if (round(timestamps['ts'][x],2) == round(shortened_data['time'][y],2)):
                        events.loc[y, 'event_name'] = timestamps.loc[x,'notes']
                        events.loc[y, 'event_index'] = timestamps.loc[x,'index']
                        break

            timestamped_data = pd.concat([shortened_data, events], axis = 1)

            #create a dictionary of indices in the shortened data for each event type.
            lookup = set()
            names = [x for x in timestamps.notes if x not in lookup and lookup.add(x) is None]

            timestamp_index = {
                names[0]:timestamped_data.loc[timestamped_data['event_index'] == 1].index.tolist(),
                names[1]:timestamped_data.loc[timestamped_data['event_index'] == 2].index.tolist(),
                names[2]:timestamped_data.loc[timestamped_data['event_index'] == 3].index.tolist()
            }

            for name in names:
                output_path = os.path.join(ts_dir, f'{name}.csv')
                #creating data frame
                zero_time = timestamped_data.loc[(timestamp_index[name][0]), 'time']
                timestamp_window_init = timestamped_data.loc[(timestamped_data['time'] > zero_time - 20)]
                timestamp_window_init = timestamp_window_init.loc[(timestamp_window_init['time'] < zero_time + 60)]
                timestamp_window_init.loc[:,'time'] = timestamp_window_init.loc[:,'time'] - zero_time
                timestamp_window_init.reset_index(inplace = True)
                timestamp_window_init = timestamp_window_init.drop(columns = ['event_name','event_index','index'])
                timestamp_window_init.columns = pd.MultiIndex.from_tuples([
                    ('time', 'time'),
                    (f'{name}_0', 'dF_F'),
                    (f'{name}_0', 'zscore')
                ])

                for x in range(1,len(timestamp_index[name])):
                    zero_time = timestamped_data.loc[(timestamp_index[name][x]), 'time']
                    timestamp_window = timestamped_data.loc[(timestamped_data['time'] > zero_time - 20)]
                    timestamp_window = timestamp_window.loc[(timestamp_window['time'] < zero_time + 60)]
                    timestamp_window.loc[:,'time'] = timestamp_window.loc[:,'time'] - zero_time
                    timestamp_window.reset_index(inplace = True)
                    timestamp_window = timestamp_window.drop(columns = ['event_name','event_index', 'time','index'])
                    timestamp_window.columns = pd.MultiIndex.from_tuples([
                        (f'{name}_{x}','dF_F'),
                        (f'{name}_{x}','zscore')
                    ])
                    timestamp_window_init = pd.concat([timestamp_window_init, timestamp_window], axis = 1)

                timestamp_window_init.to_csv(output_path)

        print(f"ID: {subject} from treatment: {treatment} exported")
print(f"Timestamps {names} exported as csv files")

