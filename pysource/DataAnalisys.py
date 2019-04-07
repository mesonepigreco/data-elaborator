from numpy import *
import scipy, scipy.optimize, scipy.interpolate
#from matplotlib.pyplot import figure, title, show, plot, xlabel, ylabel, imshow, colorbar
import DataElaboration
import  Options, TableWindow
import wx


# Cut for the FFT MODULUS (To better show low intensity modes) - NOTE MUST BE ENABLED IN BOOLEAN
CUT = 0.2
BORDER = 1 # remove the border after the interpolation (an artifact arise)

# DISCARD TIME
DISCARD_FIRST_N_TIME = 10 # This is usefull to do when first times are not equally spaced

# CUTTING OF THE CA time
"""
cut_ca_time = 0.4 # Time in which the last CA disappears
cut_off_time = 3 # Last time to use (set tue cut_off_index variable
set_total_time = 3 # 2 ps this time is used only when REMOVE_CA is true, otherwise all the time is shown


# FFT on data starting from time and lambda window
lambda_min = 500
lambda_max = 600
#lambda_min_i = 450
#lambda_max_i = 1140

# Get the time the frist CA is shown (To perform an fft of the noise and catch the artifact of the laser)
starting_t0 = 80

time_label="ps"

# Set the zero padding length (IF ZERO PADDING IS FALSE this is used directly inside the fft)
zero_padding_length = 10

# Show single signal at selected wavelength 
lambda_signal = 505
"""
# Set the extra time after the max of the CA to be removed when removing manually the CA
remove_ca_extra_time = 0.1 # ps
lambda_resolution = 200
w_max = 700 #cm^-1
w_resolution = 500


# Boolean variables
"""
DEBUGGING = True
ENABLE_CUTTING_FFT = False # Enable the cutting on the FFT modulus (CUT variable)
SHOW_FFT_BEFORE_CA = False # Show fft before CA (see the artifact given by 50 Hz laser modulation)
OVERPLOT_EVALUATED_CA = False # Overplot on the colormap with the CA the evaluated ca
CUT_LAST_DATA_LINE = True # Cut the last line - usefull for raw data
SUBTRACT_MEAN = True # Avoid a zero frequency in the fft
REMOVE_CA = False #This slide all the data of the CA

# Fitting CA rules
FIT_CA_WITH_LINE = False #Fit the CA with line
FIT_CA_WITH_POLY = False # This choose if fit the CA with a polynomial function to smooth the result

SUBTRACT_TA = True #Used to correctly subtract the Transient absortion, the window is setted below
PLOT_TA = False # Dont plot the ta
"""

# SUBTRACT_TA mode
EXPONENTIAL = 0
POLY_6 = 1
POLY_4 = 2

S_FUNCTION = POLY_6


# Other params
#ta_window = (390, 1800) # Window for the TA in nm (used if SUBTRACT_TA is True)


# THz to cm-1 conversion factor
THzToCm = 33.35641


class Data:
    def __init__(self, list_of_files, cut_ca_time, cut_off_time, lambda_min, lambda_max, N_lambda, zero_padding_length, progress_bar_dlg, kaiser_window_beta = 0):
        """ This class analyzes the given data in list_of_files array and stores the results """
        self.data = []
        self.reshaped_data = []
        self.reshaped_wl = []
        self.reshaped_t = []
        self.ca_data = [] # Stores the data regarding the coherent artifact (to be plotted if required)
        self.ca_timescale = []
        self.t_ca = [] # The time in which the coherent artifact is extimated to arrive

        self.fft_data = []
        self.fft_freq = []

        self.mean_wl = linspace(lambda_min, lambda_max, N_lambda)
        self.mean_freq = linspace(0, w_max, w_resolution) 
        self.mean_fft_data = zeros((len(self.mean_wl), len(self.mean_freq))) # The size of this array is modified at the end of the analysys if INTERPOLATION_WL flags is disabilitated
        self.mean_t_ca = zeros(len(self.mean_wl))

        counter = 0
        # Load and analyze all the data 
        for filename1 in list_of_files:
            # Set the progress bar
            abort, skip = progress_bar_dlg.Update(counter, "Loading the data files...")
            if not abort:
                # The user choose to abort
                return None
            counter += 1
            
            # Pay attention if the data file is not a perfect matrix
            try:
                data1 = loadtxt(filename1)
            except:
                # Manually load the data
                tmp_data = open(filename1, "r")
                lines = tmp_data.readlines()
                lines.pop(-1) # Get rid of the last line
                tmp_data.close()

                # Save a tmp file
                new_filename1 = filename1[: filename1.rfind(".dat")] + ".tmp"
                write_tmp = open(new_filename1, "w")
                write_tmp.writelines(lines)
                write_tmp.close()

                # Now open the new file
                data1 = loadtxt(new_filename1)

            # Append the data
            self.data.append(data1)

        counter = 0
        # Now for each data get the correct results -------------------------------------------------------------------------
        for data1 in self.data:
            # Set the progress bar
            abort, skip = progress_bar_dlg.Update(counter, "Analyzing the files...")
            if not abort:
                # The user choose to abort
                return None
            counter += 1

            
            # Get the timescale (Discard the first n time if some negative time are campioned with a different dt)
            dt = data1[0,  DISCARD_FIRST_N_TIME + 2] -data1[0, DISCARD_FIRST_N_TIME + 1]
            # Get the length of the time array
            N_t = shape(data1[1:, DISCARD_FIRST_N_TIME + 1:])[1] 
            timescale = linspace(0, dt *(N_t - 1), N_t)
            real_timescale = data1[0, DISCARD_FIRST_N_TIME + 1 :]

            if Options.GetFlagsByName("DEBUGGING"):
                print "dt = ", dt, "N_t = ", N_t, "Last_time = ", timescale[-1]


            # Get the cut off time indices
            cut_in_index = argmin(abs(timescale - cut_ca_time))
            cut_off_index = argmin(abs(timescale - cut_off_time))
            set_total_time = cut_off_time - cut_ca_time
            #cut_off_index = len(timescale) - 1

            # Get the wavelength scale
            wl = data1[1:, 0]


            # Cut the first n time data (if specified)
            data1 = data1[:, DISCARD_FIRST_N_TIME + 1 :]


            # Get the corresponding lambda in the window 
            lambda_min_i = argmin(abs(wl - lambda_min))
            lambda_max_i = argmin(abs(wl - lambda_max))
            #lambda_index = argmin(abs(wl - lambda_signal))

            """
            if DEBUGGING:
                #print "Debugging lambda finding:"
                print "lambda_min = %.2f, lambda_max = %.2f" % (wl[lambda_min_i], wl[lambda_max_i])
                print wl
            

            # Now reshape the data file
            if DEBUGGING:
                print "Check data1 and timescale before reshape data1:", shape(data1), shape(timescale)


             I think there is no need, when they are created the timescale array alread is setted correctly
            # Rescale the time cut_in and cut_off
            cut_in_index -= DISCARD_FIRST_N_TIME
            cut_off_index -= DISCARD_FIRST_N_TIME
            

            if DEBUGGING:
                print "cut_in_t =", cut_in_index, "cut_off_t=", cut_off_index, "N_t =", cut_off_index - cut_in_index
                print "Check data1 and timescale after the data1 reshape:", shape(data1), shape(timescale)
            """

            self.ca_data.append(data1[lambda_min_i: lambda_max_i,:cut_off_index])
            self.ca_timescale.append(timescale[ : cut_off_index])
            
            t_tmp = linspace(timescale[0], timescale[cut_in_index], cut_in_index)
            data_ca = data1[lambda_min_i:lambda_max_i, :cut_in_index]
    
            if Options.GetFlagsByName("DEBUGGING"):
                print "Shape of the CA in data:", shape(data_ca)
        
            t_ca = DataElaboration.FindChirpWLC(t_tmp, data_ca)
    
            if Options.GetFlagsByName("DEBUGGING"):
                print shape(t_ca), shape(wl[lambda_min_i: lambda_max_i])

    
            if Options.GetFlagsByName("FIT_CA_WITH_POLY"):
                fitted_t_ca = DataElaboration.SmoothFitPolynomial(wl[lambda_min_i: lambda_max_i], t_ca)
                #plot(fitted_t_ca, wl[lambda_min_i: lambda_max_i])
                t_ca = fitted_t_ca  # Erase the old point and sobstitute with interpolated ones
            elif Options.GetFlagsByName("FIT_CA_WITH_LINE"):
                # Linear regression
                param = polyfit(wl[lambda_min_i: lambda_max_i], t_ca, 1)

                # Obtain correct results
                fitted_t_ca = wl[lambda_min_i : lambda_max_i] * param[0] + param[1]
                #plot(fitted_t_ca, wl[lambda_min_i: lambda_max_i])
                t_ca = fitted_t_ca  # Erase the old point and sobstitute with interpolated ones
            
            self.t_ca.append(t_ca)

        

            # Reshape data1
            new_data1 = data1[lambda_min_i:lambda_max_i,:]
            wl1 = wl[lambda_min_i : lambda_max_i]
            # Wait to append them to the self data until all transformation are done

            # Now remove the CA from the new reshaped data
            if Options.GetFlagsByName("REMOVE_CA"):
                if Options.GetFlagsByName("DEBUGGING"):
                    print "Check new_data1 and timescale:", shape(new_data1), shape(timescale)
                new_data1 = DataElaboration.RemoveCAFromData(new_data1, timescale, t_ca + remove_ca_extra_time, set_total_time)
                #Now reset the time axis
                N_wl, N_t = shape(new_data1)
                t1 = timescale[:N_t]
            else:
                new_data1 = new_data1[:, cut_in_index : cut_off_index]
                t1 = timescale[cut_in_index : cut_off_index]
                N_t = cut_off_index - cut_in_index

            # Subtract exponential
            if Options.GetFlagsByName("SUBTRACT_TA"):
                if Options.GetFlagsByName("DEBUGGING"):
                    print "Data shape before exp subtraction:", shape(new_data1), "wl shape:", shape(wl1)
                #new_data1_new = DataElaboration.SubtractTA(new_data1, t1, wl1, ta_window, function = S_FUNCTION, plot_ta = PLOT_TA)
                new_data1_new = DataElaboration.SubtractTA(new_data1, t1, wl1, (lambda_min, lambda_max), function = S_FUNCTION, plot_ta = False)
                #plot(t1, new_data1[new_lambda_index, :] - new_data1_new[new_lambda_index, :], label="Fitted exponential")
                #legend()
                new_data1 = new_data1_new
            
            # FFT - setting  -----------------------
            # Avoid the zero frequency
            if Options.GetFlagsByName("SUBTRACT_MEAN"):
                m_value = mean( new_data1, axis = 1)
                m_value = tile(m_value, (N_t , 1)).transpose()
                new_data1 -= m_value

            # Now add the new reshaped data
            self.reshaped_data.append(new_data1)
            self.reshaped_wl.append(wl1)
            self.reshaped_t.append(t1)
    
            # Get the frequency axis
            n_pad = N_t
            n_pad *= zero_padding_length
            
            # Apply zero padding
            zero_padded_data = zeros((len(wl1), n_pad))
            zero_padded_data[:, :len(t1)] = new_data1
            
            # Apply the Kaiser window
            kaiser_window = scipy.signal.kaiser(n_pad * 2, kaiser_window_beta)    
            kaiser_window = kaiser_window[n_pad :] # Isolate only the second part of the window
            kaiser_window_m = tile(kaiser_window, (len(wl1), 1)) # Reply for all the signal
            zero_padded_data = kaiser_window_m * zero_padded_data# Apply the window to the data

            freq = fft.fftfreq(n_pad, dt) * THzToCm
            freq = fft.fftshift(freq)

            # FFT of the data
            fft_data =  fft.fftshift(fft.fft(zero_padded_data, n = n_pad, axis=1), axes=1)

            # Now avoid negative frequency
            rescaled = abs(fft_data)**2
            new_data_fft = rescaled[:, len(freq) / 2 + 1 :]
            new_freq = freq[len(freq) / 2 + 1 :]
            
            # Now save the results
            self.fft_data.append(new_data_fft)
            self.fft_freq.append(new_freq)



        # Now mean all the loaded data ------------------------------------------------------------------------------------------
        # Build the interpolation grid
        #interp_grid_wl = tile(self.mean_wl, (len(self.mean_freq), 1)).transpose()
        if not len(self.reshaped_wl):
            return None
            
        counter_wl = len(self.reshaped_wl[0])
        counter_freq = len(self.fft_freq[0])
       # interp_grid_freq = tile(self.mean_freq, (len(counter_wl), 1))
        
        # Redefine the mean_fft shape if interpolation is not selected
        if not Options.flags["INTERPOLATE_WL"]:
            self.mean_fft_data = zeros(( counter_wl, counter_freq ))
            self.mean_t_ca = zeros(shape(counter_wl))
            
            # Check if all the length are setted correctly
            for i in range(1, len(self.reshaped_wl)):
                if len(self.reshaped_wl[i]) != counter_wl or len(self.fft_freq[i]) != counter_freq:
                    err_dlg = wx.MessageDialog(self, "Error, the selected files have different sizes and cannot be averaged.\nTo solve the issue you can turn on the interpolation in the Flag Options Menu.", "Error", wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return None
                    
            # Overwrite also the axis
            self.mean_freq = self.fft_freq[0]
            self.mean_wl = self.reshaped_wl[0]
        
        for i in range(0, len(self.fft_data)):
            fft_data = self.fft_data[i]
            wl_now = self.reshaped_wl[i]
            freq_now = self.fft_freq[i]
            #grid_freq_now = tile(freq_now, (len(wl_now), 1) )

            t_ca_now = self.t_ca[i]
            

            if Options.GetFlagsByName("DEBUGGING"):
                print "Checking shapes before interpolation:", shape(fft_data), len(wl_now), len(freq_now)
                print "Check frequency: %.2f , %.2f - Check w: %.2f, %.2f" % (wl_now[0], wl_now[-1], freq_now[0], freq_now[-1])
            
            # Create the interpolation function
            Int_F = scipy.interpolate.interp2d(freq_now, wl_now, fft_data, "cubic")
            

            # Get the interpolated data
            if Options.flags["INTERPOLATE_WL"]:
                InterpolatedData = Int_F(self.mean_freq, self.mean_wl)
                self.mean_t_ca += scipy.interp(self.mean_wl, wl_now, t_ca_now)
            else:
                InterpolatedData = fft_data
                
                if Options.flags["ANALYZE_CA"]:
                    self.mean_t_ca += t_ca_now
                
            self.mean_fft_data += InterpolatedData
            # Analize data
            abort, skip = progress_bar_dlg.Update(i, "Averaging the results...")
            if not abort:
                # The user choose to abort
                return None
        self.mean_fft_data /= len(self.fft_data)
        self.mean_t_ca /= len(self.t_ca)


        # Now deleate the border information (an interpolation artifact)
        #self.mean_fft_data = self.mean_fft_data[BORDER : -BORDER, BORDER : -BORDER]
        #self.mean_wl = self.mean_wl[BORDER: -BORDER]
        #self.mean_freq = self.mean_freq[BORDER: -BORDER]

        """
        if Options.GetFlagsByName("DEBUGGING"):
            print "MEAN FFT DATA:"
            print self.mean_fft_data
        """
    def MeanAnalyzedData(self, w0, w1, N_w):
        """ Mean all the data from the analyzed files and evaluate the spectrum in the frequency region between w0 and w1.
        the result is then interpolated in N_w points"""
            
        
        counter_wl = len(self.reshaped_wl[0])
        counter_freq = len(self.fft_freq[0])
        
        # Override the mean freq array and the mean_fft_data
        if Options.flags["INTERPOLATE_WL"]:
            self.mean_freq = linspace(w0, w1, N_w)
            print "lambdas = ", self.mean_wl
            self.mean_fft_data = zeros((len(self.mean_wl), len(self.mean_freq)))
        else:  
            self.mean_freq = self.fft_freq[0]
            self.mean_wl = self.reshaped_wl[0]
        
        
        #interp_grid_wl = tile(self.reshaped_wl[0], (len(self.mean_freq), 1)).transpose()
        #interp_grid_freq = tile(self.fft_freq[0], (len(self.reshaped_wl[0]), 1))
        
        
        for i in range(0, len(self.fft_data)):
            fft_data = self.fft_data[i]
            wl_now = self.reshaped_wl[i]
            freq_now = self.fft_freq[i]
            #grid_freq_now = tile(freq_now, (len(wl_now), 1) )

            if Options.GetFlagsByName("DEBUGGING"):
                print "Checking shapes before interpolation:", shape(fft_data), len(wl_now), len(freq_now)
            

            # Get the interpolated data
            #InterpolatedData = Int_F(interp_grid_wl, interp_grid_freq).transpose()
            if Options.flags["INTERPOLATE_WL"]:
                # Create the interpolation function
                Int_F = scipy.interpolate.interp2d(freq_now, wl_now, fft_data, "cubic")
                InterpolatedData = Int_F(self.mean_freq, self.mean_wl)
            else:
                InterpolatedData = fft_data #scipy.interp(interp_grid_freq, grid_freq_now, fft_data)
            self.mean_fft_data += InterpolatedData
        self.mean_fft_data /= len(self.fft_data)


        # Now deleate the border information (an interpolation artifact)
        #self.mean_fft_data = self.mean_fft_data[BORDER : -BORDER, BORDER : -BORDER]
        #self.mean_wl = self.mean_wl[BORDER: -BORDER]
        #self.mean_freq = self.mean_freq[BORDER: -BORDER]


    def PlotColorMap(self, figure_axes, wl_min=0, wl_max=0, freq_min=0, freq_max=0):
        # Show the colormap in the selected figure 
        #figure_axes.imshow(self.mean_fft_data, extent=[min(self.mean_fft_data), max(self.mean_fft_data), min(self.mean_wl), max(self.mean_wl)], aspect = "auto", origin = "lower")
        # Get the indices
        wl_min_i = 0
        wl_max_i = -1
        freq_min_i = 0
        freq_max_i = -1
        if wl_min:
            wl_min_i = argmin(abs(wl_min - self.mean_wl))
        if wl_max:
            wl_max_i = argmin(abs(wl_max - self.mean_wl))
        if freq_min:
            freq_min_i = argmin(abs(freq_min - self.mean_freq))
        if freq_max:
            freq_max_i = argmin(abs(freq_max - self.mean_freq))
        
        if Options.flags["DEBUGGING"]:
            print "Plotting info: freq = %d, wl = %d, data shape = " % (len(self.mean_freq), len(self.mean_wl)), shape(self.mean_fft_data)
            
        figure_axes.pcolormesh(self.mean_freq[freq_min_i : freq_max_i], self.mean_wl[wl_min_i: wl_max_i], self.mean_fft_data[wl_min_i : wl_max_i, freq_min_i: freq_max_i])
        
        figure_axes.set_xlabel("$\\omega$ [$cm^{-1}$]")
        figure_axes.set_ylabel("$\\lambda$ [nm]")

    def PlotMeanLambda(self, lambda_min, lambda_max, freq_min, freq_max, figure_axes):
        # Get the lambda indices
        if Options.GetFlagsByName("DEBUGGING"):
            print "Check tipes:", type(lambda_min), type(self.mean_wl)
        lambda_min_i = argmin(abs(lambda_min - self.mean_wl))
        lambda_max_i = argmin(abs(lambda_max - self.mean_wl))
        freq_min_i = argmin(abs(freq_min - self.mean_freq))
        freq_max_i = argmin(abs(freq_max - self.mean_freq))

        # Mean the data
        new_graph = mean(self.mean_fft_data[lambda_min_i : lambda_max_i, freq_min_i: freq_max_i], axis = 0)

        figure_axes.plot(self.mean_freq[freq_min_i : freq_max_i], new_graph)
        figure_axes.set_xlabel("$\\omega$ [$cm^{-1}$]")
        
    def GetMeanLambda(self, lambda_min, lambda_max):
        """ This method returns the fft of the data mediated in the lambda_min, lambda_max region of the probe"""
        lambda_min_i = argmin(abs(lambda_min - self.mean_wl))
        lambda_max_i = argmin(abs(lambda_max - self.mean_wl))
        
        new_graph = mean(self.mean_fft_data[lambda_min_i : lambda_max_i, :], axis = 0)
        return new_graph
        

    def GetMeanLambdaError(self, lambda_min, lambda_max):
        lambda_min_i = argmin(abs(lambda_min - self.mean_wl))
        lambda_max_i = argmin(abs(lambda_max - self.mean_wl))

        new_graph = std(self.mean_fft_data[lambda_min_i : lambda_max_i, :], axis = 0) / sqrt(lambda_max_i - lambda_min_i)
        return new_graph
    
