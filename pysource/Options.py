import sys, os
import wx

"""
In this file all options datas are contained
"""
import numpy as np

VERSION = 0.2


# Setup some IDs
IS_ERROR = 1
NAME = 2
ASSOCIATED_ERROR = 3
ASSOCIATED_VALUE = 4
GRAPH_RULE = 5

flags = {"DEBUGGING": True,  
         "ENABLE_CUTTING_FFT": False, # Enable the cutting on the FFT modulus (CUT variable)
         "SHOW_FFT_BEFORE_CA": False, # Show fft before CA (see the artifact given by 50 Hz laser modulation)
         "OVERPLOT_EVALUATED_CA": False, # Overplot on the colormap with the CA the evaluated ca
         "CUT_LAST_DATA_LINE": True, # Cut the last line - usefull for raw data
         "SUBTRACT_MEAN": True, # Avoid a zero frequency in the fft
         "REMOVE_CA": False, #This slide all the data of the CA
         # Fitting CA rules
         "FIT_CA_WITH_LINE": False ,#Fit the CA with line
         "FIT_CA_WITH_POLY": False, # This choose if fit the CA with a polynomial function to smooth the result
         "ANALYZE_CA": False, # This flag choose if analyze the CA
         
         "SUBTRACT_TA": True, #Used to correctly subtract the Transient absortion, the window is setted below
         "PLOT_TA": False, # Dont plot the ta
         "INTERPOLATE_WL": False # Dont interpolate on the wl axis (this will give an error if the selected file doesn't share the same wl axis)
         }
         
COLORS = ["blue", "green", "red", "cyan", "magenta", "yellow", "black", "white"]
MARKERS = [".", ",", "o", "v", "<", ">", "1", "2", "3", "4", "8", "s", "p", "*", "h", "H", "+", "x", "D", "d"]
LINESIZE = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 24]
LEGEND_LOC = ["best", "upper right", "upper left", "lower right", "lower left", "lower right", "right" "center left", "center right", "lower center" "upper center", "center"]
LINESTYLE = ["solid", "dashed", "dashdot", "dotted", "None"]

def GetFlagsByName(name):
    return flags[name]

def GetFlagsNames():
    return flags.keys()

def SetFlagByName(name, value):
    flags[name] = value
    

def GetVersion():
    return VERSION

def GetAbout():
    """ This method get the text showed by the about window """
    text = "I'm the Scientific data-elaborator, graphical version.\nMy owner, Lorenzo Monacelli, makes me live.\n Good Data analisys!"
    return text

def ToFloatNumber(str_n):
    """ Convert the string to a float number, and shows an error if the conversion fails"""
    # Convert the number to a float number, and show an error if it is not a number
    try:
        n = float(str_n)
        return n
    except:
        dlg_error = wx.MessageDialog(None, "Error while tring to convert the number %s, this is not a number.", "Error", wx.ICON_ERROR | wx.OK)
        dlg_error.ShowModal()
        return 0

def ToIntNumber(str_n):
    """ Convert the string to a float number, and shows an error if the conversion fails"""
    # Convert the number to a float number, and show an error if it is not a number
    try:
        n = int(str_n)
        return n
    except:
        dlg_error = wx.MessageDialog(None, "Error while tring to convert to Integer the number %s.", "Error", wx.ICON_ERROR | wx.OK)
        dlg_error.ShowModal()
        return 0

def ScientificNotation(float_number, error=0):
    """ Get a number and change it in a latex math string of scientific notation """
    # If it is bigger than 10^3 or lesser than 10^-3 change it, otherwise return the number itself
    exponent = 0
    base_number = float_number
    if np.abs(float_number) < 10**-2 or np.abs(float_number) > 10**3:
        exponent = np.log10(np.abs(float_number))
        base_number = float_number / 10**(int(exponent))
        if exponent < 0:
            exponent -= 1
            base_number = float_number / 10**(int(exponent))
            

    if not error:
        if np.abs(float_number) > 10**-2 and np.abs(float_number) < 10**3:
            return str(float_number)
        return "%.3lf \cdot 10^{%d}" % (base_number, int(exponent))
        

    # If there is an error
    # Setup the format string
    base_error = error / 10**(int(exponent))
    
    # If the base error is lesser than 1, cut the significative digit at the right point
    format_string = "%.1lf"
    if float(base_error) < 1:
        format_string = "%." + str(int(1 - int(np.log10(base_error)) + .5)) + "lf"

    line =   format_string + " \pm " + format_string 
    if exponent:
        line += ")\cdot 10^{" + str(int(exponent)) + "}"
        line = "".join(["(", line]) # Put a ( before the line
    return line % (base_number, base_error)



# This is a column used when you have to copy the content of a given column
CopyColumnData = np.zeros(0)

def CopyColumn(array):
    """ Take the numpy array and save it """
    global CopyColumnData
    CopyColumnData = array.copy()

def PasteColumn():
    """ Return the coped array (if nothing return an array with only one zeros) """
    global CopyColumnData
    return CopyColumnData.copy()
    
# TIME Resolved Options
TITLE = "Time Resolved Data Analizer"
SIZE = (1400, 850)

DEFAULT_LAMBDA_PROBE = (450, 650)
DEFAULT_TIME = (0.3, 3)
DEFAULT_ZERO_PADDING = 4
DEFAULT_KAISER_BESSEL = 12
FILE_BAR = "/"
W_RANGE = (0, 800) # cm^-1
N_W_DEFAULT = 200
N_LAMBDA_PROBE_DEFAULT = 200

def GetTitle():
    return TITLE


def GetSize():
    return SIZE

def GetDefaultLambdaProbe():
    return DEFAULT_LAMBDA_PROBE

def GetDefaultTime():
    return DEFAULT_TIME

def GetDefaultZP():
    return DEFAULT_ZERO_PADDING

def GetDefaultKW():
    return DEFAULT_KAISER_BESSEL

def GetFileBar():
    return FILE_BAR

def GetWRange():
    return W_RANGE

def GetNWDefault():
    return N_W_DEFAULT

def GetDefaultNLambdaProbe():
    return N_LAMBDA_PROBE_DEFAULT


