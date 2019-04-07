# DATA ELABORATOR 0.2

This is a graphic version for the Scientific Data Elaborator 0.1

To run the program you need to have installed python language
 (version 2) with these libraries:
- wx python 
- numpy
- scipy
- matplotlib

You can easily find them on the web.

## Installation guide

Just type on the terminal
```
python setup.py install --user
```

This will install the data-elaborator just for the current user, without need to access as a superuser. 

## How to use data-elaborator

Scientific data-elaborator is compleately based on Tables. To start a project you nead to import a table or
create a new one. To create a new table, go to the Toolbar menu, and click on "Create Table". 
A window dialog will appear, in which you have to insert the number of rows and columns of the new table.

You can also create a table from an existing data file. The format supported is the following:
"#" is the comment comand
Floating number must use the american notation for the dot "."
Different columns have to be separated by one or more spaces

If the file is correctly formatted a new window will appear with the given data.

From the 0.2 it is possible to extend the functionality of the program using the scripting language python2.
See the section on costum action for more information.

### Manage tables
You can add columns or rows to an existing table, using the appropriate tools in the File menu of the Table window.
Every new column will have a default name with an uppercase letter, in order to avoid existing names. You can
easily modify the column name: right click on the column label, and select "Set Column Name" option.

An useful option is to associate an error to a given column, you can do this: 
right click on the column label, click on "Edit Column Proprieties", A dialog will appear.
In this dialog window you can choose if the selected column represent an error or a value. If you set "Error"
the second Box indicates  wich column value the error is referred to. 
The last option indicates the role that the column will have in the plot and in the fit (x assis, y assis or None)

Other options are avable, like sorting data, delete columns, set column values.

### Error propagation
You can easily calculate new values using the data into the table. Add one or two columns (two if you want to extimate
the error over the new value calculated), then left click on the new column's label, and select "Set Column Values".

Insert in the dialog that will appear the math formula, you have to refer to other column with their name. When you
have done a new question dialog will appear asking if you want to do error propagation (you need to have selected an
error column for the columns choosen in your expression). Select then the column in which you want to save errors.

If a column has a constant error, you need to create an error column which contain the same value in all the rows. 
This can easily be done with right-click on the column label, "Set Column Value", and choose the value for the error.

### Copy and paste
You can copy a whole column, right click on the column label, and choose "Copy Column".
Then right click on the empty column in which you want to paste the column values and select "Paste".
Pay attention! The data contained in the last column will be overwritten, and there is no possibility to undo
this operation.

### Export data
You can save the table, go tu "Options" menu, and select "Save".

You can generate latex code for the column, well formatted, putting error in tiny way (value +- error),
using the correct number of digits, and when necessary using scientific notation. The generated file can be directly compiled,
or you can copy the text easily in your relations.

### Plot data
To plot the data of the table you need to choose which column represents X axis and which the Y.
Select the column, right click on the label, and choose "Edit Column Proprieties".
The last box is the role, you can set it in "X", "Y" or "None".

You can select the error of the column at the same way (as explained in MANAGE TABLE section).
When you have correctly setted your data, click on the "Plot and Analyze" menu, and select the "Plot data" options.

If there is no error selected for your data, probably you will not see anything. Click on the V button, 
and choose the proprieties of the plot, you can select the "Curve" file, and "Maker" Style to something different
from "nothing".

To setup name of the plot, the scale of the axis (log or linear), the name of the axis, marker style and other options,
click on the V button.

You can save it with the corrispondent button as image.
If you want to display the fit on your plot, run the plot AFTER the fitting process.

### Non-linear regressions and fit
You can fit data easily. First you need to tell the program which column represent the X axis an wich one
the Y. Choose the error column for the Y axis (see MANAGE TABLE section). When you are ready, select
"Plot and Analyze" menu -> "Non linear Fit".
As soon as possible other kind of analytical fit will be added.

In the dialog that will appear, write the fitting function:
Use "x" as variable, "A", "B", "C", ... as parameters.
You can use common analitical function, as:
sin() cos() tan() sqrt() exp() abs() tanh() sinh() cosh() arcsin() arccos() arctan() ...
And others.

When you have insert the expression the Fit Wizard will be shown:
Select the start values for the parameters, the x interval.

The default minimizing algorithm is the Nelder-Mean.

The result of the fit will be report in the main windows log. If you have selected an error over Y this may take some second.
If the result has not an error over Y, you will not display error over parameters, and the chi^2 displayed is that one envaluated
like every "y" value has sigma as 1 (so it is almost non sense).

After you have compleated a Fit, you can see the risult simply plotting your data, the fitting curve will be displayed over data.

### Scripting and plugin
It is possible to costumize the data-elaborator with the new scripting function.
On the Data menu of the table window there is a comand to execute python scripts.
A costum script is the executed by the program.
The script must have a main function that accepts two arguments, the first is the complete data of the table stored as a numpy array, the second contains the column names.
It can be usefull for user defined plot, as the plotting wizard is still incomplete.

## Time resolver analyzer
The time resolved analyzer is a tool that allows the user to easily 
analyze time resolved periodic signal.
The analyzer has been written for analyze data coming from Impulsive 
Vibrational Spectroscopy (IVS) Optical experiments.

The time resolved periodic signal in this kind of experiment is 
superposed with slowly decayng background (usually called Transient 
Absorption). The program uses a polynomial fit on the data to remove the 
slowly decaing background and introducing some artifact on the low 
frequency region of the spectrum.

This kind of filter can be disabled in the Flag Options menu (from the 
drop down menu) setting to FALSE the SUBTRACT_TA flag.

The source data files must be matrices having as rows the data as 
function of time. The first row must contain the time information, and 
the first column the respective information of the mesure.
In the IVS the first column contains the probe wavelength (we have a 
different set of data in time for each wavelength of the detection).

The 'analyze data' function applies some filters to the data and perform a fourier 
analysys of the signals. Then the results are shown in the two graphs in 
the right side of the panel. 
The results are averaged on all given data to reduce the noise (better results can be obtained discarding noisier 
data acquisitions).

Using the left-bottom coltrols the user can have a single fourier signal
averaging in the selected spectrum (or other) region.

Using the Setup Model menu from the data analisys menu vertical lines can be added to the plot, to
show expected modes.

