import wx, wx.grid
import sys, os
import numpy as np
import scipy, scipy.optimize, scipy.signal
from numpy import sqrt, fabs, abs, exp, log, log10, cos, sin, tan, arctan, arcsin, arccos, sinh, tanh, cosh
from scipy.special import j0, j1, y0, y1, i0, i1, k0, k1, gamma, erf, binom, zeta, sindg, cosdg, tandg, cotdg, round

import matplotlib.pyplot as plt
import Dialogs
import Options, scripting
""" This file is made to manage table window"""


class TableFrame(wx.Frame):
    def __init__(self, title, dirname="", filename=""):
        wx.Frame.__init__(self, wx.GetApp().TopWindow, title=title, size=(600, 480))
        self.dirname = dirname
        self.filename = filename
        self.CurrentCol = 0
        self.CurrentRow = 0
        #self.RelatedGraph = 0 # A link to the frame that is the graph related to this table
        self.ColumnProprieties = [] # This is a list of dictionary wich contains the information of the columns
        self.fit_expression = "f(x)   (Use A, B, C ... as par.)"
        self.fit_pars = []
        self.fit_success = False
        # Used for fits
        self.x = 0
        self.y = 0

        # Plotting options
        self.plot_title = title
        self.plot_xlabel="$x$"
        self.plot_ylabel="$y = f(x)$"
        self.plot_colors = []
        self.plot_styles = []
        self.plot_linesize = []
        self.plot_legend = True
        self.plot_legend_position = "best" # Legend location inside the loc argument of the legend method of matplotlib
        self.plot_linestyle = []

        # Setup the menu for the table
        MenuBar = wx.MenuBar()
        #self.CreateStatusBar()

        OptionsMenu = wx.Menu()
        
       
        AddColumnMenu = OptionsMenu.Append(wx.ID_ANY, "Add column", "Add a new column")
        AddRowsMenu = OptionsMenu.Append(wx.ID_ANY, "Add rows", "Add new rows in the bottom")
        OptionsMenu.AppendSeparator()
        SaveMenu = OptionsMenu.Append(wx.ID_SAVE, "&Save", "Save the datas as text file")
        ExportLatexModeMenu = OptionsMenu.Append(wx.ID_ANY, "&Export LaTeX code", "Generate the latex code for the given table")
        OptionsMenu.AppendSeparator()
        CloseMenu = OptionsMenu.Append(wx.ID_ANY, "&Close", "Delete the table")

        # Add Graph Menu
        GraphMenu = wx.Menu()
        PlotWizardMenu = GraphMenu.Append(wx.ID_ANY, "Setup plot", "")
        PlotMenu = GraphMenu.Append(wx.ID_ANY, "Plot data", "")
        NonLinearFitMenu = GraphMenu.Append(wx.ID_ANY, "Non linear fit", "")
        GraphMenu.AppendSeparator()
        SmoothMenu = GraphMenu.Append(wx.ID_ANY, "Smooth column", "Smooth the data in the selected column using a choosen filter")
        ExecuteScriptMenu = GraphMenu.Append(wx.ID_ANY, "Execute costum script", "Execute a costum script to perform costum analisys")
        

        # Options Menu Binding
        self.Bind(wx.EVT_MENU, self.OnAddColumnMenu, AddColumnMenu)
        self.Bind(wx.EVT_MENU, self.OnAddRowsMenu, AddRowsMenu)
        self.Bind(wx.EVT_MENU, self.OnSaveMenu, SaveMenu)
        self.Bind(wx.EVT_MENU, self.OnExportLatexMenu, ExportLatexModeMenu)
        self.Bind(wx.EVT_MENU, self.OnExit, CloseMenu)
        
        self.Bind(wx.EVT_MENU, self.OnPlotMenu, PlotMenu) 
        self.Bind(wx.EVT_MENU, self.OnPlotWizardMenu, PlotWizardMenu)
        self.Bind(wx.EVT_MENU, self.OnNonLinearFitMenu, NonLinearFitMenu)
        self.Bind(wx.EVT_MENU, self.OnSmoothDataMenu, SmoothMenu)
        self.Bind(wx.EVT_MENU, self.OnExecuteScript, ExecuteScriptMenu)

        MenuBar.Append(OptionsMenu, "&Options")
        MenuBar.Append(GraphMenu, "&Plots and Analyze")

        self.Table = wx.grid.Grid(self)

        # Grid Event Binding
        self.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelLeftClick, self.Table)
        
        # Place the table all over the window
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.Table, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.sizer.Layout()

        self.data = np.empty([1,1])

        self.SetMenuBar(MenuBar)
        self.Show()

    def CreateGrid(self, n_rows, n_cols):
        """ Create the grid in the frame with given rows and columns"""
        self.ColumnProprieties = []
        self.Table.CreateGrid(n_rows, n_cols)

        # Update columns's names
        for i in range(0, self.Table.GetNumberCols()):
            # Setup the column information
            self.ColumnProprieties.append({Options.IS_ERROR:False, Options.ASSOCIATED_ERROR:-1, Options.ASSOCIATED_VALUE:-1, Options.NAME:"", Options.GRAPH_RULE:"None"})
            self.ColumnProprieties[i][Options.NAME] = self.Table.GetColLabelValue(i)

    def SetColumnFromArray(self, col_index, array):
        """ This method fill the column specified by col_index variable with the value found in the array. 
        If the array dimension mismatched the number of rows the result will be truncated. """
        
        for x in range(0, self.Table.GetNumberRows()):
            value = 0
            # Check that the array has the correct number of elements
            if x < len(array):
                value = array[x]
                
            # Now write the value in the correct position
            self.Table.SetCellValue(x, col_index, str(value))

    def GetArrayFromColumn(self, col_index):
        """ This method returns a numpy array from the column index selected """

        N = self.Table.GetNumberRows()
        array = np.zeros(N)
        for i in range(0, N):
            array[i] = self.Table.GetCellValue(i, col_index)
        
        return array
        
    def GetColumnIndexFromName(self, name):
        """ This method return  the index of the column with the given name"""
        for i in range(0, self.Table.GetNumberCols()):
            if name == self.ColumnProprieties[i][Options.NAME]:
                return i
        
        return -1


    def LoadData(self, filename):
        """ This method takes datas from a textfile  and put them into the gird """
        try:
            self.data = np.loadtxt(filename)
        except:
            with open(filename) as f:
                lines = (line for line in f if not line.strip().startswith('#'))
                self.data = np.loadtxt(lines, skiprows=1)

        self.ColumnProprieties = [] # Reset Column proprieties

        # Setup the gird
        # TODO: Destroy the previous grid if exists
        self.Table.CreateGrid(self.data.shape[0], self.data.shape[1])
        for y in range(0, self.data.shape[1]):
            for x in range(0, self.data.shape[0]):
                self.Table.SetCellValue(x, y, str(self.data[x][y]))



        # Update column name
        for i in range(0, self.Table.GetNumberCols()):
            # Setup the column information
            self.ColumnProprieties.append({Options.IS_ERROR:False, Options.ASSOCIATED_ERROR:-1, Options.ASSOCIATED_VALUE:-1, Options.NAME:"", Options.GRAPH_RULE:"None"})
            self.ColumnProprieties[i][Options.NAME] = self.Table.GetColLabelValue(i)


        
    def OnLabelLeftClick(self, event):
        menu = wx.Menu()
        if event.GetRow() != -1:
            # Make a popup menu for the row
            self.CurrentRow = event.GetRow()
            DeleteRow = menu.Append(wx.ID_ANY, "Delete row", "")

            self.Bind(wx.EVT_MENU, self.OnPopupMenuDeleteRow, DeleteRow)
        else:
            # Make a popup menu for the column
            self.CurrentCol = event.GetCol()

            # Generate the popup menu
            menu = wx.Menu()
            SetColumnName = menu.Append(wx.ID_ANY, "Set column name", "Modify the name of the column")
            SetColumnProprieties = menu.Append(wx.ID_ANY, "Edit column proprieties", "Useful if you want to give set the column as error datas")
            SetColumnValues = menu.Append(wx.ID_ANY, "Set column values", "Set the column value using a given formula")
            menu.AppendSeparator()
            CopyColumn = menu.Append(wx.ID_ANY, "Copy the column values", "")
            PasteColumn = menu.Append(wx.ID_ANY, "Paste column", "")
            menu.AppendSeparator()
            SortCrescent = menu.Append(wx.ID_ANY, "Sort by this column (crescent)")
            SortDecrescent = menu.Append(wx.ID_ANY, "Sort by this column (decrescent)")
            menu.AppendSeparator()
            DeleteColumn = menu.Append(wx.ID_ANY, "Delete", "Delete the current column...")

            # Event binding menu
            self.Bind(wx.EVT_MENU, self.OnPopupMenuSetColumnName, SetColumnName)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuSetColumnProprieties, SetColumnProprieties)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuDeleteColumn, DeleteColumn)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuSetColumnValues, SetColumnValues)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuCopyColumn, CopyColumn)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuPasteColumn, PasteColumn)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuSortCrescent, SortCrescent)
            self.Bind(wx.EVT_MENU, self.OnPopupMenuSortDecrescent, SortDecrescent) # still todo!


        # Show the menu
        self.PopupMenu(menu, event.GetPosition())
        menu.Destroy()


    def OnPopupMenuSetColumnName(self, event):
        self.SetColumnName()

    def OnPopupMenuDeleteColumn(self, event):
        # Ask a confirmation
        dlg = wx.MessageDialog(self, "Are you sure to delete the current column?", "Warning", wx.YES_NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.Table.DeleteCols(self.CurrentCol)
            self.ColumnProprieties.pop(self.CurrentCol)
        dlg.Destroy()

    def OnPopupMenuDeleteRow(self, event):
        dlg = wx.MessageDialog(self, "Are you sure to delete the current row?", "Warning", wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Table.DeleteRows(self.CurrentRow)
        dlg.Destroy()

    def OnPopupMenuSetColumnProprieties(self, event):
        # Show the proprieties dialog
        dlg = Dialogs.ColumnProprieties(self, self.ColumnProprieties, self.CurrentCol)
        if dlg.ShowModal() == wx.ID_OK:
            is_error = dlg.CmbValueError.GetValue() == dlg.first_choice[1]
            self.ColumnProprieties[self.CurrentCol][Options.IS_ERROR] = is_error

            # If the column is error, find the column of wich the error is related for
            if is_error:

                # Delete the error if other columns point the error to this one
                for i in range(0, self.Table.GetNumberCols()):
                    if self.ColumnProprieties[i][Options.ASSOCIATED_ERROR] == self.CurrentCol:
                        self.ColumnProprieties[i][Options.ASSOCIATED_ERROR] = -1

                id_owner = 0
                while self.ColumnProprieties[id_owner][Options.NAME] != dlg.CmbOtherColumns.GetValue():
                    id_owner += 1

                self.ColumnProprieties[id_owner][Options.ASSOCIATED_ERROR] = self.CurrentCol
                self.ColumnProprieties[self.CurrentCol][Options.ASSOCIATED_VALUE] = id_owner

                # Check if other column points the error to the selected column
                for i in range(0, self.Table.GetNumberCols()):
                    if self.ColumnProprieties[i][Options.ASSOCIATED_VALUE] == id_owner and i != self.CurrentCol:
                        # Show an alert message
                        #dlg = wx.MessageDialog(self, "The column %s is a conflicting error, associated to %s, will be disabled." % (self.ColumnProprieties[i][Options.NAME], self.ColumnProprieties[id_owner][Options.NAME]) , "Alert", wx.ICON_EXCLAMATION | wx.OK)
                        #dlg.ShowModal()
                        #dlg.Destroy()
                        self.ColumnProprieties[i][Options.ASSOCIATED_VALUE] = -1
                        self.ColumnProprieties[i][Options.IS_ERROR] = False

            else:
                # Set the type of axis for graph
                # Check before if there is any other axis with the same value, and put it to None
                # Search Also if there is a column that think that this is an error
                for i in range(0, self.Table.GetNumberCols()):
                    if self.ColumnProprieties[i][Options.ASSOCIATED_ERROR] == self.CurrentCol:
                        self.ColumnProprieties[i][Options.ASSOCIATED_ERROR] = -1
                    if self.ColumnProprieties[i][Options.GRAPH_RULE] == dlg.CmbAxisColumns.GetValue():
                        # Avoid double x axis but allow doble y axis
                        if self.ColumnProprieties[i][Options.GRAPH_RULE] == "X":
                            self.ColumnProprieties[i][Options.GRAPH_RULE] = "None"
                            
                self.ColumnProprieties[self.CurrentCol][Options.GRAPH_RULE] = dlg.CmbAxisColumns.GetValue()

        self.UpdateLabels()
        dlg.Destroy()

        # Coumt how many columns have plots and setup graphical uses
        plot_counts = 0
        for i in range(0, self.Table.GetNumberCols()):
            if self.ColumnProprieties[i][Options.GRAPH_RULE] == "Y":
                plot_counts += 1
        
        # Check how many plot are defined
        while plot_counts < len(self.plot_colors):
            self.plot_colors.pop(-1)
            self.plot_linesize.pop(-1)
            self.plot_styles.pop(-1)
            self.plot_linestyle.pop(-1)

        # Add the plotting informations for new plotting axes
        while plot_counts > len(self.plot_colors):
            self.plot_colors.append("red")
            self.plot_linesize.append(4)
            self.plot_styles.append("o")
            self.plot_linestyle.append("dashed")
            

    def OnPopupMenuSetColumnValues(self, event):
        # Get the expression
        dlg = Dialogs.InsertText(self, "Insert Expression", "Insert the expression for column " + self.ColumnProprieties[self.CurrentCol][Options.NAME])
        expression =""
        if dlg.ShowModal() == wx.ID_OK:
            expression = dlg.text.GetValue()
        else:
            dlg.Destroy()
            return

        dlg.Destroy()

        # Ask if you want to set a column to save error generated during error propagations
        dlg = wx.MessageDialog(self, "Do you want to choose another column in wich put errors?", "Questions", wx.ICON_QUESTION | wx.YES_NO)
        ep_1 = dlg.ShowModal()
        dlg.Destroy()

        # Get column names
        names = []
        for col in self.ColumnProprieties:
            names.append(col[Options.NAME])

        error_col_id = -1

        if ep_1 == wx.ID_YES:
            # Ask the column in wich save errors

            dlg = Dialogs.ComboDialog(self, "Error column", "Choose a column in wich save errors propagated using the given expression.", names)
            ep_2 = dlg.ShowModal()
            if ep_2 == wx.ID_OK and dlg.cmb.GetValue():
                error_col_id = names.index(dlg.cmb.GetValue())

        # Boolean variable that memorize if the program needs to propagate the error
        ep = ep_1 == wx.ID_YES and ep_2 == wx.ID_OK and dlg.cmb.GetValue()


        # Recognize the column name into the expression
        cols = []
        errs = []

        # Memorize the column to be skipped
        skip_index = []
        for i in range(0, self.Table.GetNumberCols()):
            tmp = []
            err = np.zeros(self.Table.GetNumberRows())
            tmp_skip = []
            for j in range(0, self.Table.GetNumberRows()):
                value = self.Table.GetCellValue(j, i)
                if value: 
                    # Check if the value is a number
                    v = Options.ToFloatNumber(value)
                    try: float(value)
                    except: return
                    tmp.append(v)
                else: 
                    tmp_skip.append(j)
                    tmp.append(1e-8) # This value is set to avoid most popular division by zero errors 
                if self.ColumnProprieties[i][Options.ASSOCIATED_ERROR] != -1:
                    err[j] = self.Table.GetCellValue(j, self.ColumnProprieties[i][Options.ASSOCIATED_ERROR])
                
            cols.append(np.array(tmp))
            errs.append(err)

            # Identify if the current column is involved in the calculations
            if expression.find(self.ColumnProprieties[i][Options.NAME]) != -1:
                [skip_index.append(index) for index in tmp_skip]

            # Sobstitute the column name with cols[index] into the expression
            expression = expression.replace(self.ColumnProprieties[i][Options.NAME], "cols[" + str(i) + "]")

        # Now full the column
        try:
            results = eval(expression + " + 0*cols[0]")
        except:
            dlg = wx.MessageDialog(self, "Not a good expression! control the name of the columns, and the syntax.\n" + expression, "Error", \
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Extimate the error
        if ep:
            dx = 1e-8
            d_res = []
            Error = np.zeros(self.Table.GetNumberRows())
            for i in range(0, self.Table.GetNumberCols()):
                tmp = cols[i].copy()
                cols[i] = cols[i] + dx
                # Compute the differenziation
                d_res = eval(expression+ " + 0*cols[0]") - results
                
                Error += (d_res*errs[i]/dx)**2
                cols[i] = tmp.copy()
            Error = np.sqrt(Error)
            
        # Print results into the new columns
        for i in range(0, self.Table.GetNumberRows()):
            # Check if the column exists
            if i in skip_index:
                continue
            self.Table.SetCellValue(i, self.CurrentCol, str(results[i]))
            if ep:
                self.Table.SetCellValue(i, error_col_id, str(Error[i]))
        
        # Set the info about the error column
        if ep:
            self.ColumnProprieties[error_col_id][Options.IS_ERROR] = 1
            self.ColumnProprieties[error_col_id][Options.ASSOCIATED_VALUE] = self.CurrentCol
            self.ColumnProprieties[self.CurrentCol][Options.ASSOCIATED_ERROR] = error_col_id

        
        self.UpdateLabels()

    def OnPopupMenuCopyColumn(self, event):
        """ Copy in ram the column values """
        datas = np.zeros(self.Table.GetNumberRows())
        for i in range(0, len(datas)):
            datas[i] = self.Table.GetCellValue(i, self.CurrentCol)
        Options.CopyColumn(datas)
    
    def OnPopupMenuPasteColumn(self, event):
        """ Read the value from copy column """
        datas = Options.PasteColumn()
        if not len(datas):
            # Show an alert
            dlg = wx.MessageDialog(self, "There is no data to Paste (you have to copy a column before)", "Alert", wx.ICON_EXCLAMATION | wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Check if the number of rows are enaugh
        if len(datas) > self.Table.GetNumberRows() :
            # Add other rows
            n = len(datas) - self.Table.GetNumberRows()
            self.Table.AppendRows(n)
            

        # Paste the column
        for i in range(0, len(datas)):
            self.Table.SetCellValue(i, self.CurrentCol, str(datas[i]))

    def OnPopupMenuSortCrescent(self, event):
        #Take Date
        n_rows = self.Table.GetNumberRows()
        col_datas = np.zeros(n_rows)
        for i in range(0, n_rows):
            tmp  = self.Table.GetCellValue(i, self.CurrentCol)

            # The column is not full, we cant sort
            if not tmp:
                dlg = wx.MessageDialog(self, "Error, there are some empty cells in the given column", "Error", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return

            # Check if the given data is a number
            tmp_number = Options.ToFloatNumber(tmp)
            try: 
                float(tmp)
            except:
                return

            # Append Datas
            col_datas[i] = tmp_number
            
        # Save the permutation array during sorting
        permutation = col_datas.argsort()

        # Apply the current permutation to all arrays
        datas = []
        for i in range(0, self.Table.GetNumberCols()):
            tmp_array = np.zeros(n_rows)
            for j in range(0, n_rows):
                tmp = self.Table.GetCellValue(j, i)

                # Empty values will be considered as 0
                if not tmp:
                    tmp = "0"

                # Check if the given data is a number
                tmp_number = Options.ToFloatNumber(tmp)
                try: 
                    float(tmp)
                except:
                    return

                tmp_array[j] = tmp_number

            # Apply the permutation
            datas.append(tmp_array[permutation])

        # Rewrite all the cell
        for i in range(0, self.Table.GetNumberCols()):
            for j in range(0, n_rows):
                self.Table.SetCellValue(j, i, str(datas[i][j]))
            
            
    def OnPopupMenuSortDecrescent(self, event):
        # Same as the previous
        # TODO
        pass
                
            

    def UpdateLabels(self):
        # Update the column labels
        for i in range(0, self.Table.GetNumberCols()):
            label = self.ColumnProprieties[i][Options.NAME] 
            if self.ColumnProprieties[i][Options.IS_ERROR]:
                label += " [error of " + self.ColumnProprieties[self.ColumnProprieties[i][Options.ASSOCIATED_VALUE]][Options.NAME]
                label += "]"
            else:
                error_id = self.ColumnProprieties[i][Options.ASSOCIATED_ERROR]
                if error_id != -1:
                    label += "[+- " + self.ColumnProprieties[error_id][Options.NAME] + "]"
                if self.ColumnProprieties[i][Options.GRAPH_RULE] != "None":
                    label += " [" + self.ColumnProprieties[i][Options.GRAPH_RULE]+ "]"
                        
            self.Table.SetColLabelValue(i, label)
        self.Table.AutoSize()

    def SetColumnName(self):
        # Show the change name dialog
        dlg = Dialogs.InsertText(self, "Set the column name", self.ColumnProprieties[self.CurrentCol][Options.NAME])
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            #print dlg.text.GetValue()
            self.ColumnProprieties[self.CurrentCol][Options.NAME] =  dlg.text.GetValue()
            self.UpdateLabels()
        dlg.Destroy()

    def OnAddColumnMenu(self, event):
        """ Add a white column to the grid """
        # Choose a new name
        names = []
        for i in range(0, self.Table.GetNumberCols()):
            names.append(self.ColumnProprieties[i][Options.NAME])

        self.Table.AppendCols()
        
        # Select the first letter from alphabetic not in use (A has 65 ascii code)
        char = 65
        while chr(char) in names: char += 1
        name = chr(char)

        

        self.ColumnProprieties.append({Options.IS_ERROR:0, Options.ASSOCIATED_ERROR:-1, Options.ASSOCIATED_VALUE:-1, Options.NAME:name, Options.GRAPH_RULE:"None"})

        self.UpdateLabels()
        
    def OnAddRowsMenu(self, event):
        """ Ask how many rows to append"""
        dlg = Dialogs.InsertText(self, "How many rows append?", "How many (enter a natural number)?")
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            # Check if the given text is a natural number
            n_ = dlg.text.GetValue()
            #print n_
            if n_.isdigit():
                n = int(n_)
            else:
                n = 0
            self.Table.AppendRows(n)
        dlg.Destroy()
        self.UpdateLabels()

    def OnSaveMenu(self, event):
        # Open the dialog to choose the file in wich you want to save
        dlg = wx.FileDialog(self, "Save the table as text file", self.dirname, "", "*.*", wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetDirectory()
            self.filename = dlg.GetFilename()
            
            # Get the data from the table
            columns = []
            headers = []
            fmt = []
            for i in range(0, self.Table.GetNumberCols()):
                tmp = []
                headers.append(self.Table.GetColLabelValue(i))
                for j in range(0, self.Table.GetNumberRows()):
                    string = self.Table.GetCellValue(j, i)
                    if not string:
                        string = "0"
                    x = float(string)
                    tmp.append(x)
                columns.append(np.array(tmp))
                fmt.append("%g")

            
            # Save the file
            np.savetxt(os.path.join(self.dirname, self.filename), np.transpose(columns), fmt=fmt, header=" ".join(headers))

        dlg.Destroy()
            
    def OnExportLatexMenu(self, event):
        # Choose the file in wich you want to save the text
        dlg = wx.FileDialog(self, "Export the latex file", self.dirname, "", "*.tex", wx.SAVE)

        if dlg.ShowModal() != wx.ID_OK:
            return

        self.dirname = dlg.GetDirectory()
        self.filename = dlg.GetFilename()
        dlg.Destroy()

        filename = os.path.join(self.dirname, self.filename)

        # Export Latex Table

        number_cols = self.Table.GetNumberCols()
        # Pop the error columns
        for p in self.ColumnProprieties:
            if p[Options.IS_ERROR]: number_cols -= 1
        
        
        # Create the preamble of the latex document
        document = ""
        document += "\documentclass[a4paper]{article}\n"
        document += "\\thispagestyle{empty}\n"
        document += "\\begin{document}\n"
        document += "\\begin{table}[hbtp]\n"
        document += "\centering\n"
        document += "\\begin{tabular}{|"
        for i in range(0, number_cols): document += "|c|"
        document += "|}\n"
        document += "\hline\n" 
        document += "\hline\n"

        # Write column Names in bold font
        for i in range(0, number_cols):
            if i:
                document += " & "
            
            # Skip errors
            ids = range(0, self.Table.GetNumberCols())
            k = 0
            while k < number_cols:
                if self.ColumnProprieties[ids[k]][Options.IS_ERROR]: ids.pop(k)
                else: k += 1
            current_id = ids[i]

            document += "\\bfseries %s" % (self.ColumnProprieties[current_id][Options.NAME])
        document += "\\\\\n"

        document += "\hline\n"

        # Write the correct misure value with the relative errors
        for j in range(0, self.Table.GetNumberRows()):
            #print "NewRow:", j
            for i in range(0, number_cols):
                #Skip the error column
                ids = range(0, self.Table.GetNumberCols())
                k = 0
                while k < number_cols:
                    if self.ColumnProprieties[ids[k]][Options.IS_ERROR]: ids.pop(k)
                    else: k += 1
                current_id = ids[i]

                # Separate datas
                if i:
                    document += " & "

                # Detect the error
                error_id = self.ColumnProprieties[current_id][Options.ASSOCIATED_ERROR]
                if error_id == -1:
                    if not j:
                        # No error detected, show a warning message
                        dlg = wx.MessageDialog(self, "No error detected for column " + self.ColumnProprieties[current_id][Options.NAME], "Warning", wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()

                    value = self.Table.GetCellValue(j, current_id)
                    if not value: value = "0"
                    value = Options.ScientificNotation(Options.ToFloatNumber(value))
                    document += "$" + value + "$"
                else:
                    # Error detected
                    error = self.Table.GetCellValue(j, error_id)
                    value = self.Table.GetCellValue(j, current_id)

                    if not error: error= "0"
                    if not value: value = "0"

                    if error == "0":
                        value = Options.ScientificNotation(Options.ToFloatNumber(value))
                        document += "$" + value + "$"
                        continue
                    
                    #print line, value, error, "pos = (", j, ",", current_id,")"
                    document += "$"+ Options.ScientificNotation(Options.ToFloatNumber(value), Options.ToFloatNumber(error))+"$"
            document +=  "\\\\\n"
            document += "\hline\n"
        document += "\hline\n"

        document += "\end{tabular}\n"
        document += "\end{table}\n"
        document += "\end{document}\n"

        f = file(filename, "w")
        f.write(document)
        f.close()

    def OnExit(self, event):
        # Ask for a confirmation
        dlg = wx.MessageDialog(self, "Do you really want to close this table?", "Question", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()

    def OnPlotMenu(self, event):
        self.PlotData()    
    
    def OnSmoothDataMenu(self, event):
        """ This method smooth the data in the selected column """

        # Get the column names
        col_names = []
        for i in range(0, self.Table.GetNumberCols()):
            col_names.append(self.ColumnProprieties[i][Options.NAME])

        # Create a dialog to choose the alghorithm and the window
        smooth_dlg = Dialogs.SmoothDialog(self, col_names, "Smooth wizard")
        if smooth_dlg.ShowModal() == wx.ID_OK:
            # Take the method
            method = smooth_dlg.cmb_filter.GetValue()
            source_col = smooth_dlg.cmb_source_column.GetValue()
            save_col = smooth_dlg.cmb_dest_column.GetValue()
            window_size = Options.ToFloatNumber(smooth_dlg.txt_window.GetValue())
            poly_order = Options.ToFloatNumber(smooth_dlg.txt_poly_order.GetValue())
            
            # Get the correct column index
            col_source_index = self.GetColumnIndexFromName(source_col)
            col_dest_index = self.GetColumnIndexFromName(save_col)
            
            # Check if the user selected correctly the columns
            if col_source_index == -1 or col_dest_index == -1:
                err_dlg = wx.MessageDialog(self, "Error, you must select a valid column for the source and the destination.", "Error", wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                return
            
            # Now collect the source array
            data = self.GetArrayFromColumn(col_source_index)
            
            # Apply the filter
            if method == "Savitzky-Golay":
                # Check that the window is an odd number
                new_window = int(window_size + 0.5)
                
                # Print some debugging information
                if Options.GetFlagsByName("DEBUGGING"):
                    print "Window size:", window_size, "Converted size:", new_window
                    print "Modulus of the division:", new_window % 2
                
                if (new_window % 2) == 0:   # Check if the window is even (the filter requires an odd window)
                    err_dlg = wx.MessageBox(self, "Error, the Savitzky-Golay filter requires an odd window.", "Error", wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return
                
                new_data = scipy.signal.savgol_filter(data, new_window, poly_order)
            elif method == "Gaussian":
                # This method uses a gaussian kernel
                N = self.Table.GetNumberRows()
                gaussian_kernel = scipy.signal.gaussian(N, window_size)

                # Apply the gaussian kernel to a convolution
                new_data = scipy.signal.convolve(data, gaussian_kernel, mode="same")
                
                # After the convolution the data are no more at the same height, they need to be rescaled
                new_data *= np.max(data) / np.max(new_data)
            else:
                # No correct method has been selected
                err_dlg = wx.MessageDialog(self, "Error, you must select a valid smoothing filter.", "Error", wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                return
            
            # Now apply the smoothed data in the selected column
            self.SetColumnFromArray(col_dest_index, new_data)
            print "Done, col_dest_index : ", col_dest_index, "col_source:", col_source_index
            
        
        # Destroy the dialog
        smooth_dlg.Destroy()
        event.Skip()
            

    def GetDataWithErrors(self):
        # Check the column that represent x axis
        x_id = -1
        error_x_id = -1
        y_ids = []
        error_y_ids = []

        for i in range(0, len(self.ColumnProprieties)):
            if self.ColumnProprieties[i][Options.GRAPH_RULE] == "X":
                x_id = i
                error_x_id = self.ColumnProprieties[i][Options.ASSOCIATED_ERROR]
            elif self.ColumnProprieties[i][Options.GRAPH_RULE] == "Y":
                y_ids.append(i)
                error_y_ids.append(self.ColumnProprieties[i][Options.ASSOCIATED_ERROR])

        # Check if the user has defined X and Y
        if x_id == -1 or not y_ids:
            dlg = wx.MessageDialog(self, "Error, to draw a plot you must select wich column is the X or Y.\n(Right click on the column label and Modify Column Proprieties)", "Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Create datas
        x = np.zeros(self.Table.GetNumberRows())
        y = []
        error_y = []
        error_x = []
        
        
        if error_x_id != -1:
            error_x =  np.zeros(len(x))
            
        # Get an array for the y-ons
        for j in range(0, len(y_ids)):
            y_id = y_ids[j]
            error_y_id = error_y_ids[j]
            
            y_tmp = np.zeros(len(x))
            error_y_tmp = np.zeros(len(x))
            
            for i in range(0, self.Table.GetNumberRows()):
                y_str = self.Table.GetCellValue(i, y_id)
                if not y_str:
                    # Error
                    err_dlg = wx.MessageBox(self, "Error, found a white space inside the %s column" % self.ColumnProprieties[y_id][Options.NAME], "Error", wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return
                y_tmp[i] = Options.ToFloatNumber(y_str)
                
                # Check if there is an associated error
                if error_y_id != -1:
                    error_y_tmp[i] = Options.ToFloatNumber(self.Table.GetCellValue(i, error_y_id))
                    
            y.append(y_tmp)
            if error_y_id != -1:
                error_y.append(error_y_tmp)
            else:
                error_y.append([])

        # Get data on the x-axis
        for i in range(0, self.Table.GetNumberRows()):
            x_str = self.Table.GetCellValue(i, x_id)

            if not x_str:
                # Error
                err_dlg = wx.MessageBox(self, "Error, found a white space inside the %s column" % self.ColumnProprieties[x_id][Options.NAME], "Error", wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                return

            x[i] = Options.ToFloatNumber(x_str)
            
            if error_x_id != -1:
                error_x[i] = Options.ToFloatNumber(self.Table.GetCellValue(i, error_x_id))
                
        
        return x, y, error_x, error_y

    def PlotData(self):
        # Setup the title of the plot
        plt.title(self.plot_title)
        plt.xlabel(self.plot_xlabel)
        plt.ylabel(self.plot_ylabel)

        x, ys, error_x, error_ys = self.GetDataWithErrors()
        
        # Get the y_id for the labels of the plot
        y_ids = []
        plot_names = []
        for i in range(0, len(self.ColumnProprieties)):  
            if self.ColumnProprieties[i][Options.GRAPH_RULE] == "Y":
                y_ids.append(i)         
                plot_names.append(self.ColumnProprieties[i][Options.NAME])
        
        # Perform a different plot for each selected y axis
        for i in range(0, len(ys)):
            y = ys[i]
            error_y = error_ys[i]
            both_error = (len(error_x)) and(len(error_y))

            if both_error:
                plt.errorbar(x, y, xerr=error_x, yerr=error_y, capsize=0, ls=self.plot_linestyle[i] ,lw=self.plot_linesize[i], color=self.plot_colors[i], marker=self.plot_styles[i], markersize=4, label=plot_names[i])
            elif len(error_x):
                plt.errorbar(x, y, xerr=error_x, capsize=0, ls=self.plot_linestyle[i], lw=self.plot_linesize[i], color=self.plot_colors[i], marker=self.plot_styles[i], markersize=4, label=plot_names[i])
            elif len(error_y):
                plt.errorbar(x, y, yerr=error_y, capsize=0, ls=self.plot_linestyle[i], lw=self.plot_linesize[i], color=self.plot_colors[i], marker=self.plot_styles[i], markersize=4, label=plot_names[i])
            else:
                plt.plot(x, y, self.plot_styles[i], ls=self.plot_linestyle[i], lw=self.plot_linesize[i], color=self.plot_colors[i], label=plot_names[i])

        # If there is a fit, plot the fit
        if self.fit_success:
            _x_ = np.r_[np.min(x):np.max(x):((np.max(x) - np.min(x))/100.)]
            plt.plot(_x_, self.eval_fit(_x_), color="blue", label="Fit result")
        
        if self.plot_legend:        
           plt.legend(loc = self.plot_legend_position)
           
        plt.show()

    def UpdatePlot(self):
        pass

    def eval_fit(self, x):
        expression = self.fit_expression
        # Get the parameters used
        n_pars = 0
        while expression.find(chr(ord("A") + n_pars)) != -1:
            n_pars += 1
        
        # Fit the expression
        par = np.zeros(n_pars)
        for i in range(0, n_pars):
            expression = expression.replace(chr(ord("A") + i), "self.fit_pars[%d]" % i)

        return eval(expression)
        

    def FitData(self):
        # The parameter of the fit has to be indicated with uppercase letters A, B, C,...
        # Get the expression
        dlg = Dialogs.InsertText(self, "Expression", self.fit_expression)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        expression = dlg.text.GetValue()
        self.fit_expression = expression
        dlg.Destroy()

        # Get the parameters used
        n_pars = 0
        while expression.find(chr(ord("A") + n_pars)) != -1:
            n_pars += 1
        
        # Fit the expression
        par = np.zeros(n_pars)
        for i in range(0, n_pars):
            expression = expression.replace(chr(ord("A") + i), "par[%d]" % i)
        

        # Get Datas
        x, ys, error_x, error_ys = self.GetDataWithErrors()
        y = ys[0]
        error_y = error_ys[0]
        
        # Setup the start conditions
        algorithms = ["Nelder-Mead", "Powell", "CG", "BFGS", "Anneal"]
        dlg = Dialogs.FitWizard(self, self.fit_expression, n_pars, np.min(x), np.max(x), algorithms)
        algorithm = dlg.AlgCmb.GetValue()
        if not algorithm:
            algorithm = algorithms[0]
        if dlg.ShowModal() != wx.ID_OK:
            return

        # Get values
        x_min = Options.ToFloatNumber(dlg.FromTxt.GetValue())
        try:
            float(dlg.FromTxt.GetValue())
        except:
            return

        x_max = Options.ToFloatNumber(dlg.ToTxt.GetValue())
        try:
            float(dlg.ToTxt.GetValue())
        except:
            return
        
        for i in range(0, n_pars):
            par[i] = Options.ToFloatNumber(dlg.starts[i].GetValue())
            try: 
                float(dlg.starts[i].GetValue())
            except:
                return
        
        mask = (x >= x_min) & (x <= x_max)
        self.x = x[mask]
        self.y = y[mask]
        x = self.x.copy()
        y = self.y.copy()
            
        # Create the Least-Square function
        
        def f(par):
            x = self.x
            y = self.y
            if len(error_y):
                return np.sum(((y - eval(expression.strip()))/error_y[mask])**2)
            return np.sum((y - eval(expression.strip()))**2)

        
        summary = scipy.optimize.minimize(f, par, method=algorithm, tol=1e-4)

        # If there is an error over the x, transform it in an error over y, and redo the fit
        par = summary.x
        if len(error_x):
            y1 = eval(expression)
            x = x + 1e-8
            y2 = eval(expression)
            x = self.x.copy()
            dydx = (y2 - y1)/(1e-8)
            new_error_y = dydx * error_x
            error_y = sqrt(error_y**2 + new_error_y**2)
            summary = scipy.optimize.minimize(f, par, method=algorithm, tol=1e-4)


        self.fit_pars = summary.x
        self.fit_success = summary.success

        
        # Extimate residual
        res = y - eval(expression)

        # if there is an error over y extimate the error over parameters.
        N = 100
        pars = np.zeros((len(par), N))
        if len(error_y):
            for i in range(0, N):
                # Extract new values
                self.y = np.random.normal(y, error_y[mask])
                sumry =  scipy.optimize.minimize(f, summary.x, method=algorithm, tol=1e-4)
                
                pars[:,i] = sumry.x
                

        parent_window = self.GetParent()
        text = "-------------------------------\n"
        text += "Fit function: " + self.fit_expression + "\n"
        text += "Fit result for table " + self.GetTitle() + " is " + str(summary.success) + "\nThe found parameters are: "
        for i in range(0, len(self.fit_pars)):
            if len(error_y):
                text += "\n" + chr(ord("A") + i) + ": " + str(np.mean(pars[i,:])) + " +- " + str(np.std(pars[i,:]))
            else:
                text += "\n" + chr(ord("A") + i) + ": " + str(self.fit_pars[i]) + " +- 0"


        text += "\nResidual Mean: %g\tResidual Std. Dev: %g\n" % (np.mean(res), np.std(res))
        
        if len(error_y):
            res = res / error_y[mask]
        # Return chi^2
        text += "Chi^2 = %g\tdof=%d\n" % (np.sum(res**2), len(x) - len(par))
        text += "Reduced chi square: %g\n" % (np.sum(res**2)/(len(x) - len(par)))
        
        
        parent_window.LogText.AppendText(text + "\n")
        if not summary.success:
            print summary

    def OnNonLinearFitMenu(self, event):
        self.FitData()

    def OnPlotWizardMenu(self, event):
        # Open the dialog to set the plotting options
        # THe function PlotWizard in dialog is already done (to be tested)
        title = self.plot_title
        xlab = self.plot_xlabel
        ylab = self.plot_ylabel
        col_names = []

        for i in range(0, self.Table.GetNumberCols()):
            if self.ColumnProprieties[i][Options.GRAPH_RULE] == "Y":
                col_names.append(self.ColumnProprieties[i][Options.NAME])
        
        dialog = Dialogs.PlotWizard(self, title, xlab, ylab, col_names, self.plot_styles,  self.plot_colors, self.plot_linesize, self.plot_linestyle)
        
        # Setup the dialogs legend values
        dialog.cmb_legend.SetValue(str(self.plot_legend))
        dialog.cmb_legend_loc.SetValue(self.plot_legend_position)
        
        if dialog.ShowModal() == wx.ID_OK:
            self.plot_title = dialog.title_text.GetValue()
            self.plot_xlabel = dialog.xlabel_text.GetValue()
            self.plot_ylabel = dialog.ylabel_text.GetValue()

            for i in range(0, len(col_names)):
                self.plot_colors[i] = dialog.Colors[i].GetValue()
                self.plot_styles[i] = dialog.Markers[i].GetValue()
                self.plot_linesize[i] = Options.ToIntNumber(dialog.LineSizes[i].GetValue())
                self.plot_linestyle[i] = dialog.LineStyles[i].GetValue()

            self.plot_legend = bool(dialog.cmb_legend.GetValue())
            self.plot_legend_position = dialog.cmb_legend_loc.GetValue()
        
    def OnExecuteScript(self, event):
        """ This method execute the script passing to its main function the data array containing all the table """
        
        # Create the array
        data = np.zeros(( self.Table.GetNumberCols() ,self.Table.GetNumberRows() ))
        col_names = []
        
        for i in range(0, self.Table.GetNumberCols()):
            data[i, :] = self.GetArrayFromColumn(i)
            col_names.append(self.ColumnProprieties[i][Options.NAME])
            
        # Get the scripting filename
        dlg = wx.FileDialog(self, "Select a python2 script (it must have a main function)", style = wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            # Now we have all the data and can execute the script
            filename =dlg.GetPath()
            scripting.TwoArgumentPythonScript(filename, data, col_names)
        
        dlg.Destroy()
        
