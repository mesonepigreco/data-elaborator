from numpy import *
import scipy, scipy.optimize
from matplotlib.pyplot import figure, plot, imshow, title, xlabel, ylabel, legend, colorbar



# SUBTRACT_TA mode
EXPONENTIAL = 0
POLY_6 = 1
POLY_4 = 2


poly_6_starting = (0, 1, 0, 0, 0, 0, 0)
poly_4_starting = (0, 1, 0, 0, 0)

"""
filename = "../01_IVS_cheximage_1.dat"

data1 = loadtxt(filename1)



# Get the timescale
timescale = data1[0, 1:] - data1[0, 1]
# Set the timescale in femtoseconds
timescale *= 1e+3

# Set the time space (to correctly evaluate the x range of the ft) 
dt = mean(diff(timescale)) * 1e-15
print "dt = ", dt
c = 3e8
"""

def AddZeroPadding(data, pad_length=4,axis = 1):
    """ This function adds zero padding to the time signal
    data is the data array with data[time , wavelength] structure
    pad_length is the length of the zero tail to add to the data respect to the whole data
    """
    if axis == 1:
        new_data = zeros((shape(data)[0], shape(data)[1]*pad_length))
    elif axis == 0:
        new_data = zeros((shape(data)[0]*pad_length, shape(data)[1]))

    new_data[data == data] = data.reshape(shape(data)[0] * shape(data)[1])
        
    return new_data

def AddKaiserBesselWindow(data, start_cut, end_cut):
    """ This function insert the KaiserBesselWindow to avoid ripples at the baseline of
    the spectrum """



def FindChirpWLC(t0,  data):
    """ Fit the chirp linear in 
    - t0 is an array containing the t0 slide on data
    - data is a 2d-matrix containg the data[w, t0] measure

     This method returns an array with the t0 of the CA 
    """
    # Check the max of the CA
    t0m = tile(t0, (len(data[:, 1]), 1))
    t_ca = sum(t0m * abs(data), axis = 1) / sum(abs(data), axis = 1)

    # Now we have the t0 for the CA as function of w
    return t_ca

def SmoothFitPolynomial(x, y, guess = None):
    """ Get the x and y array and fit the data with a polynomial curve of 4th order 
    the param guess must be a 5 elements array containing the initial guesses (otherwise all to 1)
    """
    # Define the fitting function
    def f(t, a, b, c, d, e):
        return a*t**4 + b*t**3 + c*t**2 + d*t + e

    # Select the initial guess
    if not guess:
        guess = [1,1,1,1,1]

    popt, pcov = scipy.optimize.curve_fit(f, x, y, guess)

    # Get the new data array
    return f(x, popt[0], popt[1], popt[2], popt[3], popt[4])

def RemoveCAFromData(data_matrix, time_axis, time_ca, time_window):
    """ This method shift each row of data_matrix to sincronize the oscillation.
    the time_window is how much time take after time_ca for each frequency. """

    # Create a time matrix
    N_wl, N_t = shape(data_matrix)
    tm = tile(time_axis, (N_wl, 1))
    tca_m = tile(time_ca, (N_t, 1)).transpose()

    print "RemoveCAFromData: tm, tca_m shape = ", shape(tm), shape(tca_m)
    
    # Select the new time length
    dt = time_axis[1] - time_axis[0]
    N_new = int(time_window / dt)

    # Now extract the correct data
    slice_start = argmin(abs(tm - tca_m), axis = 1)
    slice_end = slice_start + N_new

    new_data = zeros((N_wl, N_new))
    for i in range(0, N_wl):
        new_data[i, :] = data_matrix[i, slice_start[i] : slice_end[i]]

    return new_data
    

def SubtractTA(data, time, wl, wl_range=(0, 1000), function = 0, starting_par = (1,1,1), plot_ta = False) :
    """ 
    This method fits an exponential decay in time at differents wavelength, and returns a new
    data matrix with the subtraction exponential 

    The wl_range list contains the starting wavelength and the ending wavelength (usually in nm)

    The starting_par list contains the initial guess for the fitting procedure. 
    plot_ta specify if plot the transient absorbtion fitted signal
    """

    N_wl, N_t = shape(data)
    new_data = data.copy()

    # Only used to plot ta
    fitted_data = zeros(shape(data))

    #find the correct index for the wl_range
    wl_start_index = argmin(abs(wl - wl_range[0]))
    wl_end_index = argmin(abs(wl - wl_range[1]))

    #print shape(data), shape(wl), wl_start_index, wl_end_index
    # Overwrite the N_wl array
    N_wl = wl_end_index - wl_start_index

    # Define the exponential decay
    
    def f_exp(x, a, b, c):
        return a * exp(- b * x) + c
    
    def f_poly6(x, p0, p1, p2, p3, p4, p5, p6):
        return p0 + x * p1 + x**2 + p2 + x**3 * p3 + x**4 * p4 + x**5 * p5 + x**6 * p6
    
    def f_poly4(x, p0, p1, p2, p3, p4):
        return p0 + x * p1 + x**2 + p2 + x**3 * p3 + x**4 * p4 
    

    # Now start the fit for each wl in range
    param = []

    # Try polifit - always 6th order
    param = polyfit(time, transpose(data), 6).transpose()
    
    
    for wl_i in range(wl_start_index, wl_end_index):
        if function == EXPONENTIAL:
            popt, pcvar = scipy.optimize.curve_fit(f_exp, time, data[wl_i, :], starting_par)
            f = f_exp
            new_data [wl_i, :] -= f(time, popt[0], popt[1], popt[2])
            # Build the ta image
            if plot_ta:
                fitted_data[wl_i, :] = f(time, popt[0], popt[1], popt[2])
            
        elif function == POLY_6:
            p = param[wl_i, :]
            #print p
            fitted_data[wl_i, :] = p[0] * time**6 + p[1] * time**5 + p[2] * time**4 + p[3] * time**3 + p[4] * time**2 + p[5] * time + p[6]
            
            """
            popt, pcvar = scipy.optimize.curve_fit(f_poly6, time, data[wl_i, :], poly_6_starting)
            f = f_poly6
            new_data [wl_i, :] -= f(time, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], popt[6])
            # Build the ta image
            if plot_ta:
                fitted_data[wl_i, :] = f(time, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], popt[6])
            """

            
            
        elif function == POLY_4:
            f = f_poly4
            popt, pcvar = scipy.optimize.curve_fit(f_poly4, time, data[wl_i, :], poly_4_starting)
            new_data [wl_i, :] -= f(time, popt[0], popt[1], popt[2], popt[3], popt[4])
            # Build the ta image
            if plot_ta:
                fitted_data[wl_i, :] = f(time, popt[0], popt[1], popt[2], popt[3], popt[4])

    new_data -= fitted_data
    #param.append(popt)

    # Debugging plot of the transient absorption
    if plot_ta:
        figure()
        title("TA exponential fit")
        xlabel("time")
        ylabel("wavelength")
        imshow(fitted_data, extent=[time[0], time[-1], wl[0], wl[-1]], aspect="auto", origin="lower")
        colorbar()

    return new_data
    
