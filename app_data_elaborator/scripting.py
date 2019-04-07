# -*- coding: utf-8 -*-
"""
Created on Tue May  3 15:51:40 2016

@author: pione
"""

# This is the the scrpitting code, it lets you to extend the functionality of the program usign scripting facilities from python lenguage

import sys, os
import shutil, imp

def TwoArgumentPythonScript(filename, argument1, argument2):
    """ This method passes to the filename script, and call the function main inside the scrpit, that requires the given argument.\n
    This function returns the same thing that the source script returned. """
    
    # Load the scrpit
    print filename
    if os.path.exists(filename):
        print "Exists"
    foo = imp.load_source("costum_source", filename)
    
    # Now the script is executed
    return foo.main(argument1, argument2)