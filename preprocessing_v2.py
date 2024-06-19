"""
This code defines functions to preprocess the data.
1. Low Pass - Zero Phase Filter to 'denoise' the signal.
2. Photobleaching Correction (either High Pass Filtering or Double Exponential Fitting)
3. Motion Correction
4. Normalisation (both dF/F or z-Score)
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy

def zero_phase_filter(outputs, sampling_rate, timestamps):
    b, a = scipy.signal.butter(2, 10, btype = 'low', fs = sampling_rate)
    filtered_signal = scipy.signal.filtfilt(b, a, outputs['signal'] )
    filtered_ISOS = scipy.signal.filtfilt(b, a, outputs['ISOS'])

    filtered_data = {
        'filtered_signal' : filtered_signal,
        'signal_ts': outputs['signal_ts'],
        'filtered_ISOS': filtered_ISOS,
        'ISOS_ts': outputs['ISOS_ts']
    }

    #Creating a graph of the raw data and time stamps for reference
    #Plot signals
    filtered_figure,ax1=plt.subplots()  # create a plot to allow for dual y-axes plotting
    plot1=ax1.plot(outputs['signal_ts'], filtered_signal, 'g', label='Signal')
    ax2=plt.twinx()# create a right y-axis, sharing x-axis on the same plot
    plot2=ax2.plot(outputs['ISOS_ts'], filtered_ISOS, 'y', label='ISOS')
    plot3= ax1.plot(outputs['signal_ts'], outputs['signal'], 'g', alpha = 0.3, label = 'Signal Raw' )
    plot4= ax2.plot(outputs['ISOS_ts'], outputs['ISOS'], 'y', alpha = 0.3, label = 'ISOS Raw' )

    # Plot epochs as lines.
    timestamp_ticks = ax1.plot(timestamps.ts, np.full(np.size(timestamps.ts), max(filtered_signal)), label='Timestamps', color='w', marker="|", mec = "k")


    ax1.set_ylim(min(filtered_signal) - 20, max(filtered_signal)+ 10)
    ax2.set_ylim(min(filtered_ISOS)-10 , max(filtered_signal)-20)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Filtered Signal (mV)', color='g')
    ax2.set_ylabel('Filtered ISOS (mV)', color='y')
    ax1.set_title('Zero Phase Filtered signals')

    lines = plot1 + plot2 + plot3 + plot4 + timestamp_ticks #line handle for legend
    labels = [l.get_label() for l in lines]  #get legend labels
    legend = ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.98, 0.50)) #add legend
    plt.close()

    #ax1.set_xlim(1000, 1010) #Optional setting of a smaller window for the plot

    return filtered_data, filtered_figure


def photo_bleach_correction(filtered_data, timestamps):
    #Fitting a double exponential curve to the filtered data, adapted from Thomas Akam's Github
    def double_exponential(t, const, amp_fast, amp_slow, tau_slow, tau_multiplier):
    #Compute a double exponential function with constant offset
    #Parameters:
    #t       : Time vector in seconds.
    #const   : Amplitude of the constant offset. 
    #amp_fast: Amplitude of the fast component.  
    #amp_slow: Amplitude of the slow component.  
    #tau_slow: Time constant of slow component in seconds.
    #tau_multiplier: Time constant of fast component relative to slow. 
        tau_fast = tau_slow*tau_multiplier
        return const+amp_slow*np.exp(-t/tau_slow)+amp_fast*np.exp(-t/tau_fast)
    
    # Fit curve to signal.
    max_sig = np.max(filtered_data['filtered_signal'])
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
            [max_sig, max_sig, max_sig, 36000, 1])
    signal_parms, parm_cov = scipy.optimize.curve_fit(double_exponential,
                                                      filtered_data['signal_ts'],
                                                      filtered_data['filtered_signal'],
                                                      p0=inital_params,
                                                      bounds=bounds,
                                                      maxfev=1000
                                                      )
    signal_expfit = double_exponential(filtered_data['signal_ts'], *signal_parms)

    # Fit curve to ISOS signal.
    max_sig = np.max(filtered_data['filtered_ISOS'])
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
            [max_sig, max_sig, max_sig, 36000, 1])
    ISOS_parms, parm_cov = scipy.optimize.curve_fit(double_exponential,
                                      filtered_data['ISOS_ts'],
                                      filtered_data['filtered_ISOS'],
                                      p0=inital_params,
                                      bounds=bounds,
                                      maxfev=1000
                                      )
    ISOS_expfit = double_exponential(filtered_data['ISOS_ts'], *ISOS_parms)

    #plot fits over filtered data
    exponential_fit_figure,ax1=plt.subplots()  
    plot1=ax1.plot(filtered_data['signal_ts'], filtered_data['filtered_signal'], color = 'g', label='Signal')
    plot3=ax1.plot(filtered_data['signal_ts'], signal_expfit, color='k', linewidth=1.5, label='Exponential fit') 
    ax2=plt.twinx()
    plot2=ax2.plot(filtered_data['ISOS_ts'], filtered_data['filtered_ISOS'], color='y', label='ISOS') 
    plot4=ax2.plot(filtered_data['ISOS_ts'], ISOS_expfit, color='k', linewidth=1.5) 


    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Signal (mV)', color='g')
    ax2.set_ylabel('ISOS (mV)', color='y')
    ax1.set_title('Filtered signals with double exponential fits')

    lines = plot1 + plot2 + plot3 + plot4
    labels = [l.get_label() for l in lines]  
    legend = ax1.legend(lines, labels, loc='upper right')

    ax1.set_ylim(min(filtered_data['filtered_signal']) - 20, max(filtered_data['filtered_signal'])+ 10)
    ax2.set_ylim(min(filtered_data['filtered_ISOS'])-10 , max(filtered_data['filtered_signal'])-20)
    plt.close()

    #Creacting a dictionary with the detrended data
    detrended_data = {
        'detrended_signal': filtered_data['filtered_signal'] - signal_expfit,
        'signal_ts': filtered_data['ISOS_ts'],
        'detrended_ISOS': filtered_data['filtered_ISOS'] - ISOS_expfit,
        'ISOS_ts': filtered_data['ISOS_ts']
    }

    #saving the exponential fit data
    exponential_fit = {
        'signal_expfit': signal_expfit,
        'ISOS_expfit': ISOS_expfit
    }

    #creating a plot of the detrended data
    detrended_figure,ax1= plt.subplots()  # create a plot to allow for dual y-axes plotting
    plot1=ax1.plot(detrended_data['signal_ts'], detrended_data['detrended_signal'], 'g', label='Signal')
    ax2=plt.twinx()# create a right y-axis, sharing x-axis on the same plot
    plot2=ax2.plot(detrended_data['ISOS_ts'], detrended_data['detrended_ISOS'], 'y', label='ISOS')

    # Plot epochs as lines.
    timestamp_ticks = ax1.plot(timestamps.ts, np.full(np.size(timestamps.ts), max(detrended_data['detrended_signal'])), label='Timestamps', color='w', marker="|", mec = "k")

    ax1.set_ylim(min(detrended_data['detrended_signal']) - 20, max(detrended_data['detrended_signal'])+ 10)
    ax2.set_ylim(min(detrended_data['detrended_ISOS'])-10 , max(detrended_data['detrended_ISOS'])+20)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Filtered Signal (mV)', color='g')
    ax2.set_ylabel('Filtered ISOS (mV)', color='y')
    ax1.set_title('Detrended signals')

    lines = plot1 + plot2 + timestamp_ticks #line handle for legend
    labels = [l.get_label() for l in lines]  #get legend labels
    legend = ax2.legend(lines, labels, loc='lower right', bbox_to_anchor=(0.98, 0.50)) #add legend
    plt.close()

    return detrended_data, exponential_fit_figure, detrended_figure, exponential_fit


def motion_correction(detrended_data, timestamps):
    #using the ISOS signal to predict the motion in the signal.
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x= detrended_data['detrended_signal'], y= detrended_data['detrended_ISOS'])

    motion_figure, (correlation_plot, motion_plot) = plt.subplots(nrows = 2)
    
    correlation_plot.scatter(detrended_data['detrended_ISOS'][::5], detrended_data['detrended_signal'][::5],alpha=0.1, marker='.')
    x = np.array(plt.xlim())
    correlation_plot.plot(x, intercept+slope*x)
    correlation_plot.set_xlabel('ISOS')
    correlation_plot.set_ylabel('Signal')
    correlation_plot.set_title('ISOS - Signal correlation.')

    correlation_plot.annotate('Slope    : {:.3f}'.format(slope), (-7.5,25))
    correlation_plot.annotate('R-squared: {:.3f}'.format(r_value**2), (-7.5,23))

    #Estimating motion from the ISOS signal and correcting the signal for this.
    signal_est_motion = intercept + slope * detrended_data['detrended_ISOS']
    signal_corrected = detrended_data['detrended_signal'] - signal_est_motion

    plot1= motion_plot.plot(detrended_data['signal_ts'],detrended_data['detrended_signal'], 'b' , label='Signal - pre motion correction', alpha=0.3)
    plot3= motion_plot.plot(detrended_data['signal_ts'], signal_corrected, 'g', label='Signal - motion corrected')
    plot4= motion_plot.plot(detrended_data['signal_ts'], signal_est_motion - 0.05, 'y', label='estimated motion')
    timestamp_ticks = motion_plot.plot(timestamps.ts, np.full(np.size(timestamps.ts), max(detrended_data['detrended_signal'])), label='Timestamps', color='w', marker="|", mec = "k")

    motion_plot.set_xlabel('Time (seconds)')
    motion_plot.set_ylabel('Signal (mV)', color='g')
    motion_plot.set_title('Motion Correction')

    lines = plot1+plot3+plot4+ timestamp_ticks
    labels = [l.get_label() for l in lines]  
    legend = motion_plot.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.95, 0.7))
    plt.close()


    #creating a dictionary with motion corrected data.
    motion_corrected_data = {
        'signal_corrected': signal_corrected,
        'signal_ts': detrended_data['signal_ts']
    }
    return motion_corrected_data, motion_figure

def normalisation(motion_corrected_data, exponential_fit, timestamps):

    #dF/F 
    dF_F = 100*motion_corrected_data['signal_corrected']/exponential_fit['signal_expfit']

    #plot dF/F
    dF_F_plot,ax1=plt.subplots()  
    plot1=ax1.plot(motion_corrected_data['signal_ts'], dF_F, 'g', label='dF/F')
    timestamp_ticks = ax1.plot(timestamps.ts, np.full(np.size(timestamps.ts), max(dF_F)), label='Timestamps', color='w', marker="|", mec = "k")
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('dF/F (%)')
    ax1.set_title('dF/F')

    lines = plot1+ timestamp_ticks
    labels = [l.get_label() for l in lines]  
    legend = ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.95, 0.98))
    plt.close()

    #ZScore
    zscore = (motion_corrected_data['signal_corrected']-np.mean(motion_corrected_data['signal_corrected']))/np.std(motion_corrected_data['signal_corrected'])

    zscore_plot,ax1=plt.subplots()  
    plot1=ax1.plot(motion_corrected_data['signal_ts'], zscore, 'g', label='z-score')
    timestamp_ticks = ax1.plot(timestamps.ts, np.full(np.size(timestamps.ts), max(dF_F)), label='Timestamps', color='w', marker="|", mec = "k")

    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('z-score')
    ax1.set_title('z-scored')

    lines = plot1+ timestamp_ticks
    labels = [l.get_label() for l in lines]  
    legend = ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.95, 0.98))
    plt.close()

    normalised_data = {
        'time': motion_corrected_data['signal_ts'],
        'dF_F': dF_F,
        'zscore': zscore
    }

    return normalised_data, dF_F_plot, zscore_plot