TITLE = "Time Resolved Data Analizer"
SIZE = (1400, 850)

DEFAULT_LAMBDA_PROBE = (450, 650)
DEFAULT_TIME = (0.3, 3)
DEFAULT_ZERO_PADDING = 4
DEFAULT_KAISER_BESSEL = 1
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
