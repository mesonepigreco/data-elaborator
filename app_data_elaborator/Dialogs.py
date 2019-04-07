import wx, sys, os
import wx.lib.intctrl as lib
import Options
import numpy as np

# Some default units used in data analisys
UNITS = ["cm^-1", "eV", "THz"]
EV_TO_CM = 8065.54429
THZ_TO_CM = 33.35641

class InsertText(wx.Dialog):
    """ A class for a dialog window that allows you to set multiple text variabile
    This is used for such things like set columns name in a grid"""

    def __init__(self, parent, title, text=""):
        """ the text is the default text to show in the textctrl"""
        wx.Dialog.__init__(self, None, -1, title=title, size=(300, 250))

        # Append the controltext and the two buttons
        self.text = wx.TextCtrl(self)
        self.text.SetValue(text)
        self.b_ok = wx.Button(self, wx.ID_ANY, "Ok")
        self.b_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        # Event Binding
        self.Bind(wx.EVT_BUTTON, self.OnOk, self.b_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.b_cancel)

        # Sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.button_sizer.Add(self.b_cancel,0 , wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.SHAPED)
        self.button_sizer.AddStretchSpacer(1)
        self.button_sizer.Add(self.b_ok, 0, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.SHAPED)

        self.sizer.Add(self.text, 0, wx.TOP | wx.EXPAND)

        self.sizer.AddStretchSpacer(1)
        self.sizer.Add(self.button_sizer, 1, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND)

        self.SetSizer(self.sizer)

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


class ColumnProprieties(wx.Dialog):
    def __init__(self, parent, column_proprieties, current_column_id):
        # Draw a dialog with Cancel and OK buttons
        wx.Dialog.__init__(self, parent, title="Set column proprieties", size=(600, 300))
        
        # Setup The first Combo box
        lbl1 = wx.StaticText(self, label="Choose if the column represents a value, or a error:")
        self.first_choice = ["Value", "Error"]
        self.CmbValueError = wx.ComboBox(self, choices=self.first_choice, style=wx.CB_DROPDOWN| wx.CB_READONLY)

        # the names of the columns (we remove the current column)
        
        self.ColumnNames = [col[Options.NAME] for col in column_proprieties]
        self.ColumnNames.pop(current_column_id)
        
        # Setup the second combo box
        self.lbl2 = wx.StaticText(self, label="Choose the referred column:")
        self.CmbOtherColumns = wx.ComboBox(self, choices=self.ColumnNames, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        # This combo box is disable by default
        self.CmbOtherColumns.Enable(False)

        # Setup the third combo box (in which you choose if the column has to be an axis in the graph)
        self.third_choice = ["None", "X", "Y"]

        # Check if there is some selected $Y$ axis 
                
        self.CmbAxisColumns = wx.ComboBox(self, choices=self.third_choice, style=wx.CB_DROPDOWN| wx.CB_READONLY)
        self.lbl3 = wx.StaticText(self, label="Choose the role of the column:")

        # Setup the sizer

        self.FirstSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.FirstSizer.Add(lbl1, 0, wx.ALIGN_LEFT)
        self.FirstSizer.AddStretchSpacer(1)
        self.FirstSizer.Add(self.CmbValueError, 1)

        self.SecondSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SecondSizer.Add(self.lbl2, 0, wx.ALIGN_LEFT)
        self.SecondSizer.AddStretchSpacer(2)
        self.SecondSizer.Add(self.CmbOtherColumns, 1)


        self.ThirdSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ThirdSizer.Add(self.lbl3, 0, wx.ALIGN_LEFT)
        self.ThirdSizer.AddStretchSpacer(1)
        self.ThirdSizer.Add(self.CmbAxisColumns, 1)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.FirstSizer, 1, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
        self.sizer.Add(self.SecondSizer, 1, wx.LEFT| wx.RIGHT| wx.EXPAND | wx.TOP)
        self.sizer.Add(self.ThirdSizer, 1, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.TOP)
        self.sizer.AddStretchSpacer(1)

        # Buttons
        self.b_ok = wx.Button(self, wx.ID_ANY, "Ok")
        self.b_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.b_cancel,0 , wx.ALIGN_LEFT | wx.ALIGN_BOTTOM | wx.SHAPED)
        self.button_sizer.AddStretchSpacer(1)
        self.button_sizer.Add(self.b_ok, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.SHAPED)

        self.sizer.Add(self.button_sizer, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND)

        
        self.SetSizer(self.sizer)
        self.sizer.Layout()

        # Setup the events
        self.Bind(wx.EVT_COMBOBOX, self.OnFirstComboBox, self.CmbValueError)
        self.Bind(wx.EVT_BUTTON, self.OnOk, self.b_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.b_cancel)

        # Set the box as default choice
        cp = column_proprieties[current_column_id]

        value = self.first_choice[cp[Options.IS_ERROR]]
        self.CmbValueError.SetStringSelection(value)
        id = cp[Options.ASSOCIATED_ERROR]
        if id > current_column_id:
            id -= 1
        value = self.ColumnNames[id]
        self.CmbOtherColumns.SetStringSelection(value)
        value = cp[Options.GRAPH_RULE]
        self.CmbAxisColumns.SetStringSelection(value)

    def OnFirstComboBox(self, event):
        """ If the user choose Error, enable the second combo box to specify which column is the value
        Of which the given column is referred"""

        if self.CmbValueError.GetValue() == self.first_choice[1]:
            self.CmbOtherColumns.Enable(True)
            self.lbl2.SetLabel("Choose the referred column for the errors:")
            
    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)        


        
class ComboDialog(wx.Dialog):
    def __init__(self, parent, title, label, choose_list):
        wx.Dialog.__init__(self, parent, title=title)

        # Setup 
        lbl = wx.StaticText(self, label=label)
        self.cmb = wx.ComboBox(self, choices=choose_list, style =  wx.CB_DROPDOWN | wx.CB_READONLY)

        b_ok = wx.Button(self, wx.ID_ANY, "Ok")
        b_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer_button.Add(b_cancel, 0, wx.LEFT)
        sizer_button.AddStretchSpacer(1)
        sizer_button.Add(b_ok, 0, wx.RIGHT)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(lbl, 0, wx.TOP)
        sizer.Add(self.cmb, 0, wx.TOP)
        sizer.AddStretchSpacer(1)
        sizer.Add(sizer_button, 0, wx.BOTTOM | wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnOk, b_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, b_cancel)
        
        self.SetSizer(sizer)
        sizer.Layout()

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)        
        

        
class FlagsDialog(wx.Dialog):
    def __init__(self, parent, title, label, choose_list1, choose_list2):
        wx.Dialog.__init__(self, parent, title=title, size=(800, 600))

        # Setup 
        lbl = wx.StaticText(self, label=label)

        b_ok = wx.Button(self, wx.ID_ANY, "Ok")
        b_cancel = wx.Button(self, wx.ID_ANY, "Cancel")

        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer_button.Add(b_cancel, 0, wx.LEFT)
        sizer_button.AddStretchSpacer(1)
        sizer_button.Add(b_ok, 0, wx.RIGHT)
        
        # Create a list of cmbs each for a different flag
        self.cmbs = [] 
        lbls = []
        sizers = []
        for i in range(0, len(choose_list1)):
            self.cmbs.append( wx.ComboBox(self, choices = choose_list2, style =  wx.CB_DROPDOWN | wx.CB_READONLY))
            lbls.append( wx.StaticText(self, label=choose_list1[i]))
            
            self.cmbs[i].SetValue(str(Options.GetFlagsByName(choose_list1[i])))
            if i % 2 == 0:
                sizers.append( wx.BoxSizer(wx.HORIZONTAL) )
            sizers[i/2].Add(lbls[i], 0, wx.ALIGN_CENTER)
            sizers[i/2].AddStretchSpacer(1)
            sizers[i/2].Add(self.cmbs[i], 5, wx.ALIGN_CENTER)
            sizers[i/2].AddStretchSpacer(1)
            

        FinalSizer = wx.BoxSizer(wx.VERTICAL)
        FinalSizer.Add(lbl, 0, wx.TOP)
        
        # Add all the combo box
        for i in range(0, len(sizers)):            
            FinalSizer.Add(sizers[i], 5, wx.TOP | wx.ALIGN_CENTER | wx.EXPAND)
            FinalSizer.AddStretchSpacer(1)
            
        FinalSizer.Add(sizer_button, 0, wx.BOTTOM | wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnOk, b_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, b_cancel)
        
        self.SetSizer(FinalSizer)
        FinalSizer.Layout()

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)        

class TwoIntMenu(wx.Dialog):
    """ A dialog with two text entries (used for example when you have to create a new table) """
    
    def __init__(self, parent, text1, text2, title):
        wx.Dialog.__init__(self, parent, title=title)

        # Draw the window
        lbl1 = wx.StaticText(self, label=text1)
        lbl2 = wx.StaticText(self, label=text2)

        self.txt1 = lib.IntCtrl(self, value=10, min = 2, max=30, limited = False, oob_color=wx.Colour(255, 50, 50))
        self.txt2 = lib.IntCtrl(self, value=3, min = 2, max=30, limited = False, oob_color=wx.Colour(255, 50, 50))

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(lbl1, 0, wx.ALIGN_LEFT)
        sizer1.AddStretchSpacer(1)
        sizer1.Add(self.txt1, 1, wx.TOP | wx.ALIGN_RIGHT)

        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(lbl2, 0, wx.ALIGN_LEFT)
        sizer2.AddStretchSpacer(1)
        sizer2.Add(self.txt2, 1, wx.TOP | wx.ALIGN_RIGHT)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sizer1, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND)
        sizer.AddStretchSpacer(1)
        sizer.Add(sizer2, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
        
        ok = wx.Button(self, label="Ok")
        cancel = wx.Button(self, label="Cancel")

        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3.AddStretchSpacer(1)
        sizer3.Add(cancel, 0, wx.ALIGN_RIGHT)
        sizer3.Add(ok, 0, wx.ALIGN_RIGHT)

        sizer.Add(sizer3, 0, wx.ALIGN_RIGHT)

        self.Bind(wx.EVT_BUTTON, self.OnOk, ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancel)

        self.SetSizer(sizer)
        sizer.Layout()

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)        

class FitWizard(wx.Dialog):
    def __init__(self, parent, expression, n_par, x_min, x_max, algorithms=[]):
        # This wizard Dialog is made to choose initial condition for parameters
        wx.Dialog.__init__(self, parent, title="Fit wizard", size = (800, 600))

        TotalSizer = wx.BoxSizer(wx.VERTICAL)
 
        # Display at the top of the window the given formula
        lbl_Formula = wx.StaticText(self, label="Formula: ")
        lbl_Expression = wx.StaticText(self, label=expression)
        formula_sizer = wx.BoxSizer(wx.HORIZONTAL)
        formula_sizer.Add(lbl_Formula, 0, wx.ALIGN_LEFT)
        formula_sizer.AddStretchSpacer(1)
        formula_sizer.Add(lbl_Expression, 0, wx.ALIGN_RIGHT)
        TotalSizer.Add(formula_sizer, 0, wx.TOP | wx.LEFT|wx.RIGHT|wx.EXPAND)

        lbl_Descriptions = wx.StaticText(self, label="Set up the start conditions for given parameters:")
        TotalSizer.Add(lbl_Descriptions, 1, wx.TOP | wx.ALIGN_CENTRE)
        
        # Setup the number of parameters
        self.starts = []
        for i in range(0, n_par):
            lbl = wx.StaticText(self, label=chr(ord("A")+i) + ": ")
            self.starts.append(wx.TextCtrl(self))
            self.starts[i].SetValue("0")
            tmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
            tmp_sizer.Add(lbl, 0, wx.ALIGN_LEFT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(self.starts[i], 0, wx.ALIGN_RIGHT | wx.TOP)
            TotalSizer.Add(tmp_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

        # Setup the x range value for fitting data
        TotalSizer.AddStretchSpacer(1)
        TotalSizer.Add(wx.StaticText(self, label="Choose the x range of the fit"), 0, wx.ALIGN_CENTRE)

        
        range_sizer = wx.BoxSizer(wx.HORIZONTAL)
        range_sizer.Add(wx.StaticText(self, label="From x = "), 0)
        self.FromTxt = wx.TextCtrl(self)
        self.FromTxt.SetValue(str(x_min))
        range_sizer.Add(self.FromTxt, 0, wx.TOP)
        range_sizer.AddStretchSpacer(1)
        range_sizer.Add(wx.StaticText(self, label=" To x = "), 0)
        self.ToTxt = wx.TextCtrl(self)
        self.ToTxt.SetValue(str(x_max))
        range_sizer.Add(self.ToTxt, 0, wx.TOP)
        TotalSizer.Add(range_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
        TotalSizer.AddStretchSpacer(1)


        # Choose the optimization algorithm
        TotalSizer.AddStretchSpacer(1)
        alg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        alg_sizer.Add(wx.StaticText(self, label="Choose the optimization algorithm:"), 0)
        self.AlgCmb = wx.ComboBox(self, wx.ID_ANY, choices=algorithms, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        alg_sizer.AddStretchSpacer(1)
        alg_sizer.Add(self.AlgCmb, 0, wx.RIGHT | wx.TOP)
        TotalSizer.Add(alg_sizer, 0, wx.TOP |wx.LEFT | wx.RIGHT | wx.EXPAND)


        # Setup final button
        b_fit = wx.Button(self, label="&Fit")
        b_cancel = wx.Button(self, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(b_cancel, 0, wx.ALIGN_RIGHT)
        button_sizer.Add(b_fit, 0, wx.ALIGN_RIGHT)
        TotalSizer.Add(button_sizer, 0, wx.BOTTOM | wx.ALIGN_BOTTOM | wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnOk, b_fit)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, b_cancel)

        self.SetSizer(TotalSizer)
        TotalSizer.Layout()

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)        


class PlotWizard(wx.Dialog):
    """ This class is used to set the plotting informations"""
    def __init__(self, parent, title = "", xlab="", ylab="", plotting_columns_names = [], plotting_columns_styles = [], plotting_columns_colors=[], plotting_columns_linewidth=[], plotting_columns_linesyles=[]):
        # This wizard Dialog is made to choose initial condition for parameters
        wx.Dialog.__init__(self, parent, title="Plot wizard", size=(800, 600))

        TotalSizer = wx.BoxSizer(wx.VERTICAL)
 
        lbl_Formula = wx.StaticText(self, label="Plotting Info")
        TotalSizer.Add(lbl_Formula, 0, wx.TOP | wx.LEFT|wx.RIGHT|wx.EXPAND)

        
        # Setup the plot info:
        lbl_title = wx.StaticText(self, label="Title:")
        self.title_text = wx.TextCtrl(self)
        self.title_text.SetValue(title)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(lbl_title, 0, wx.ALIGN_LEFT)
        title_sizer.AddStretchSpacer(1)
        title_sizer.Add(self.title_text, 0, wx.ALIGN_RIGHT | wx.TOP)
        TotalSizer.Add(title_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)
       
        lbl_xlabel = wx.StaticText(self, label="x label:")
        xlabel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.xlabel_text = wx.TextCtrl(self)
        self.xlabel_text.SetValue(xlab)
        xlabel_sizer.Add(lbl_xlabel, 0, wx.ALIGN_LEFT)
        xlabel_sizer.AddStretchSpacer(1)
        xlabel_sizer.Add(self.xlabel_text, 0, wx.ALIGN_RIGHT | wx.TOP)
        TotalSizer.Add(xlabel_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)


        lbl_ylabel = wx.StaticText(self, label="y label:")
        ylabel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ylabel_text = wx.TextCtrl(self)
        self.ylabel_text.SetValue(ylab)
        ylabel_sizer.Add(lbl_ylabel, 0, wx.ALIGN_LEFT)
        ylabel_sizer.AddStretchSpacer(1)
        ylabel_sizer.Add(self.ylabel_text, 0, wx.ALIGN_RIGHT | wx.TOP)
        TotalSizer.Add(ylabel_sizer, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND)

        # An horizontal line
        TotalSizer.AddStretchSpacer(1)
        TotalSizer.Add(wx.StaticLine(self, style= wx.LI_HORIZONTAL), 0, wx.EXPAND)
        TotalSizer.AddStretchSpacer(1)
        
        # Now setup the single plot info
        self.Colors = []
        self.LineSizes = []
        self.Markers = []
        self.LineStyles = []
        for i in range(0, len(plotting_columns_names)):
            col_name = plotting_columns_names[i]
            label_name = wx.StaticText(self, label="Plot %s" % col_name)
            label_color = wx.StaticText(self, label="Color")
            label_style = wx.StaticText(self, label="Marker")
            label_linewidth = wx.StaticText(self, label="Line size")
            lbl_linesyle = wx.StaticText(self, label="Line style")
            
            self.Colors.append(wx.ComboBox(self, wx.ID_ANY, choices = Options.COLORS, style = wx.CB_DROPDOWN | wx.CB_READONLY))
            self.LineSizes.append(wx.ComboBox(self, wx.ID_ANY, choices = [str(item) for item in Options.LINESIZE], style = wx.CB_DROPDOWN | wx.CB_READONLY))
            self.Markers.append(wx.ComboBox(self, wx.ID_ANY, choices = Options.MARKERS, style = wx.CB_DROPDOWN | wx.CB_READONLY))
            self.LineStyles.append(wx.ComboBox(self, wx.ID_ANY, choices = Options.LINESTYLE, style = wx.CB_DROPDOWN | wx.CB_READONLY))


            # Setup the default values
            print "Marker:", plotting_columns_styles[i]
            self.Colors[i].SetValue(plotting_columns_colors[i])
            self.Markers[i].SetValue(plotting_columns_styles[i])
            self.LineSizes[i].SetValue(str(plotting_columns_linewidth[i]))
            self.LineStyles[i].SetValue(str(plotting_columns_linesyles[i]))

            # Create a sizer
            tmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
            tmp_sizer.Add(label_name, 0, wx.ALIGN_LEFT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(label_color, 0, wx.ALIGN_LEFT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(self.Colors[i], 5, wx.ALIGN_RIGHT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(label_style, 0, wx.ALIGN_LEFT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(self.Markers[i], 5, wx.ALIGN_RIGHT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(label_linewidth, 0, wx.ALIGN_LEFT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(self.LineSizes[i], 5, wx.ALIGN_RIGHT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(lbl_linesyle, 0, wx.ALIGN_LEFT)
            tmp_sizer.AddStretchSpacer(1)
            tmp_sizer.Add(self.LineStyles[i], 5, wx.ALIGN_RIGHT)

            # Append the sizer of the line to the total sizer
            TotalSizer.Add(tmp_sizer, 0, wx.EXPAND)
            TotalSizer.AddStretchSpacer(1)

        # Add Another horizontal line
        TotalSizer.Add(wx.StaticLine(self, style= wx.LI_HORIZONTAL), 0, wx.EXPAND)
        TotalSizer.AddStretchSpacer(1)

        # Now setup the legend menu
        lbl_legend = wx.StaticText(self, wx.ID_ANY, label="Legend options:")
        self.cmb_legend = wx.ComboBox(self, wx.ID_ANY, choices=["True", "False"], style = wx.CB_DROPDOWN | wx.CB_READONLY)
        self.cmb_legend_loc =  wx.ComboBox(self, wx.ID_ANY, choices=Options.LEGEND_LOC, style = wx.CB_DROPDOWN | wx.CB_READONLY)

        legend_sizer = wx.BoxSizer(wx.HORIZONTAL)
        legend_sizer.Add(lbl_legend, 0, wx.ALIGN_RIGHT)
        legend_sizer.AddStretchSpacer(1)
        legend_sizer.Add(self.cmb_legend, 4, wx.ALIGN_LEFT)
        legend_sizer.AddStretchSpacer(1)
        legend_sizer.Add(self.cmb_legend_loc,4,  wx.ALIGN_RIGHT)

        TotalSizer.Add(legend_sizer, 1, wx.EXPAND)
        TotalSizer.AddStretchSpacer(2)
        
        # Setup final button
        b_ok = wx.Button(self, label="&Ok")
        b_cancel = wx.Button(self, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(1)
        button_sizer.Add(b_cancel, 0, wx.ALIGN_RIGHT)
        button_sizer.Add(b_ok, 0, wx.ALIGN_RIGHT)
        TotalSizer.Add(button_sizer, 0, wx.BOTTOM | wx.ALIGN_BOTTOM | wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnOk, b_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, b_cancel)

        self.SetSizer(TotalSizer)
        TotalSizer.Layout()

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


class SmoothDialog(wx.Dialog):
    def __init__(self, parent, columns_names, title="Smooth wizard"):
        wx.Dialog.__init__(self, parent, title=title)

        # Setup 
        lbl_filter = wx.StaticText(self, label="Smoothing filter")
        self.cmb_filter = wx.ComboBox(self, choices=["Savitzky-Golay", "Gaussian"], style =  wx.CB_DROPDOWN | wx.CB_READONLY)
        
        lbl_window = wx.StaticText(self, label="Window's size")
        self.txt_window = wx.TextCtrl(self)
        self.txt_window.SetValue("51")
        
        lbl_polyorder = wx.StaticText(self, label="Poly order")
        self.txt_poly_order = wx.TextCtrl(self)
        self.txt_poly_order.SetValue("3")
        
        # Chose the column in which save the result
        lbl_columns = wx.StaticText(self, label="Results to be written in")
        self.cmb_dest_column = wx.ComboBox(self, choices=columns_names, style= wx.CB_DROPDOWN | wx.CB_READONLY)
        lbl_source = wx.StaticText(self, label="Data to filter")
        self.cmb_source_column = wx.ComboBox(self, choices=columns_names, style= wx.CB_DROPDOWN | wx.CB_READONLY)
        
        # Button to check if cancel or proceed
        btn_ok = wx.Button(self, label="Ok")
        btn_cancel = wx.Button(self, label="Cancel")
        
        # Setup Layout
        FilterSizer = wx.BoxSizer(wx.HORIZONTAL)
        FilterSizer.Add(lbl_filter, 0, wx.ALIGN_CENTER)
        FilterSizer.AddStretchSpacer(2)
        FilterSizer.Add(self.cmb_filter, 5, wx.ALIGN_CENTER)
        
        FilterSetupSizer = wx.BoxSizer(wx.HORIZONTAL)
        FilterSetupSizer.Add(lbl_window, 0, wx.ALIGN_CENTER)
        FilterSetupSizer.AddStretchSpacer(1)
        FilterSetupSizer.Add(self.txt_window, 5, wx.ALIGN_CENTER)
        FilterSetupSizer.AddStretchSpacer(2)
        FilterSetupSizer.Add(lbl_polyorder, 0, wx.ALIGN_CENTER)
        FilterSetupSizer.AddStretchSpacer(1)
        FilterSetupSizer.Add(self.txt_poly_order, 5, wx.ALIGN_CENTER)
        
        ColSizer = wx.BoxSizer(wx.HORIZONTAL)
        ColSizer.Add(lbl_source, 0, wx.ALIGN_CENTER)
        ColSizer.AddStretchSpacer(2)
        ColSizer.Add(self.cmb_source_column, 5, wx.ALIGN_CENTER)
        ColSizer.Add(lbl_columns, 0, wx.ALIGN_CENTER)
        ColSizer.AddStretchSpacer(2)
        ColSizer.Add(self.cmb_dest_column, 5, wx.ALIGN_CENTER)
        
        BtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        BtnSizer.Add(btn_ok, 5, wx.ALIGN_CENTER)
        BtnSizer.AddStretchSpacer(2)
        BtnSizer.Add(btn_cancel, 5, wx.ALIGN_CENTER)
        
        # Final sizer layoit
        FinalSizer = wx.BoxSizer(wx.VERTICAL)
        FinalSizer.Add(FilterSizer, 2, wx.EXPAND| wx.ALIGN_CENTER)
        FinalSizer.AddStretchSpacer(1)
        FinalSizer.Add(FilterSetupSizer, 2, wx.EXPAND| wx.ALIGN_CENTER)
        FinalSizer.AddStretchSpacer(2)
        FinalSizer.Add(ColSizer, 2, wx.EXPAND | wx.ALIGN_CENTER)
        FinalSizer.AddStretchSpacer(3)
        FinalSizer.Add(BtnSizer, 2, wx.EXPAND | wx.ALIGN_CENTER)
        
        self.SetSizer(FinalSizer)
        self.Layout()
        
        # Now bind the events
        self.Bind(wx.EVT_BUTTON, self.OnOk, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btn_cancel)
        
    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        


class ModelDialog(wx.Dialog):
    def __init__(self, parent, title="Molecule Model", size = (600, 480), model_modes = []):
        wx.Dialog.__init__(self, parent, title=title, size = size)

        # Now setup the molecule aspect
        self.Modes = []
        
        # Setup the control panel
        self.ModeList = wx.ListBox(self, style = wx.LB_EXTENDED | wx.LB_NEEDED_SB)
        self.ModeTxt = wx.TextCtrl(self)
        self.ModeUnit = wx.ComboBox(self, wx.ID_ANY, choices=UNITS, style = wx.CB_DROPDOWN)
        self.ModeUnit.SetStringSelection(UNITS[0])
        self.AddButton = wx.Button(self, label="Add mode")
        self.OkBtn = wx.Button(self, label="Ok")
        self.CancelBtn = wx.Button(self, label = "Cancel")
        DeleteAllBtn = wx.Button(self, label="Delete all")
        
        # Open and Save buttons
        btnOpen = wx.Button(self, label="Load")
        btnSave = wx.Button(self, label="Save")

        # Label
        lbl_explain = wx.StaticText(self, label = "Mode active in the current molecule:")
        lbl_setup = wx.StaticText(self, label = "Set a new mode")

        # Sizers
        # Save and Load sizer
        SaveLoadSizer = wx.BoxSizer(wx.VERTICAL)
        SaveLoadSizer.Add(btnOpen)
        SaveLoadSizer.Add(btnSave)
        
        # Show Defined Modes
        DefModesSizer = wx.BoxSizer(wx.HORIZONTAL)
        DefModesSizer.Add(self.ModeList, 10, wx.EXPAND | wx.ALIGN_CENTER | wx.LEFT)
        DefModesSizer.AddStretchSpacer(1)
        DefModesSizer.Add(SaveLoadSizer, 3, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT)
        
        CurrentModeSizer = wx.BoxSizer(wx.VERTICAL)
        CurrentModeSizer.Add(lbl_explain, 1, wx.TOP | wx.ALIGN_CENTER)
        CurrentModeSizer.Add(DefModesSizer, 5, wx.BOTTOM | wx.EXPAND)

        AddModeSizer = wx.BoxSizer(wx.HORIZONTAL)
        AddModeSizer.Add(self.ModeTxt, 4, wx.LEFT | wx.ALIGN_LEFT)
        AddModeSizer.AddStretchSpacer(1)
        AddModeSizer.Add(self.ModeUnit, 3, wx.RIGHT | wx.ALIGN_RIGHT)

        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer.AddStretchSpacer(1)
        ButtonSizer.Add(self.CancelBtn, 0, wx.ALIGN_RIGHT | wx.RIGHT)
        ButtonSizer.Add(self.OkBtn, 0, wx.ALIGN_RIGHT |wx.RIGHT)
        ButtonSizer.Add(DeleteAllBtn, 0, wx.ALIGN_RIGHT | wx.RIGHT)

        NewModeSizer = wx.BoxSizer(wx.VERTICAL)
        NewModeSizer.Add(lbl_setup, 1, wx.ALIGN_CENTER)
        NewModeSizer.Add(AddModeSizer, 1, wx.ALIGN_CENTER | wx.RIGHT)
        NewModeSizer.Add(self.AddButton, 1, wx.ALIGN_CENTER | wx.RIGHT)
        NewModeSizer.AddStretchSpacer(1)
        NewModeSizer.Add(ButtonSizer, 1, wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.BOTTOM | wx.RIGHT)

        TotalSizer = wx.BoxSizer(wx.HORIZONTAL)
        TotalSizer.Add(CurrentModeSizer, 1, wx.ALIGN_LEFT | wx.LEFT | wx.EXPAND)
        TotalSizer.Add(NewModeSizer, 1, wx.ALIGN_RIGHT | wx.RIGHT)
        
        self.SetSizer(TotalSizer)
        self.Layout()

        # Add already known models
        modes_txt = ["%.2f cm^-1" % mode for mode in model_modes]
        if modes_txt:
            self.ModeList.InsertItems(modes_txt, 0)


        self.Bind(wx.EVT_BUTTON, self.OnOk, self.OkBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.CancelBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAddMode, self.AddButton)
        self.Bind(wx.EVT_BUTTON, self.OnLoad, btnOpen)
        self.Bind(wx.EVT_BUTTON, self.OnSave, btnSave)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteAll, DeleteAllBtn)

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def OnLoad(self, event):
        # Load from file
        LoadDlg = wx.FileDialog(self, "Load the file containing the modes", style = wx.FD_OPEN)
        if LoadDlg.ShowModal() == wx.ID_OK:
            # Get the filename
            filename = LoadDlg.GetPath()
            
            # Now open the file using numpy
            try:
                modes_data = np.loadtxt(filename)
            except:
                err_dlg = wx.MessageDialog(self, "Error, the selected file must contain one column of the numerica data of the mode (without unit of measures)", "Errror", style = wx.ICON_ERROR)
                err_dlg.ShowModal()
                err_dlg.Destroy()
                LoadDlg.Destroy()
                event.Skip()
                return
            if Options.flags["DEBUGGING"]:
                print "[DEBUG] opening a mode file, the shape is ", np.shape(modes_data)
                
            # Delete all the previous modes
            for i in range(0, self.ModeList.GetCount()):
                self.ModeList.Delete(0)
            
            # Insert the new modes
            unit =  UNITS[self.ModeUnit.GetCurrentSelection()] 
            self.Modes = list(modes_data)
            
            # Perform the conversion to have the modes expressed in the wanted units
            if unit == "eV":
                modes_data /= EV_TO_CM
            elif unit == "THz":
                modes_data /= THZ_TO_CM
                
            
            self.ModeList.InsertItems([str(item) + " " +  unit  for item in list(modes_data)], 0)
        LoadDlg.Destroy()
    
    def OnSave(self, event):
        """ Save the modes on file """
        
        SaveDlg = wx.FileDialog(self, "Save the current modes", style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if SaveDlg.ShowModal() == wx.ID_OK:
            np.savetxt(SaveDlg.GetPath(), self.Modes)
        
        SaveDlg.Destroy()
        
    def OnDeleteAll(self, event = None):       
        """ Delete all the mode in the current window """
        for i in range(0, self.ModeList.GetCount()):
            self.ModeList.Delete(0)
        self.Modes = []
            
    def OnAddMode(self, event):
        # Add the mode on the list text
        mode_txt = "%s %s" % (self.ModeTxt.GetValue(), UNITS[self.ModeUnit.GetCurrentSelection()])

        try:
            mode = float(self.ModeTxt.GetValue())
        except:
            msg = wx.MessageDialog(self, "You must inser a correct number in the text box", "Error", wx.ICON_ERROR)
            msg.ShowModal()
            msg.Destroy()
            return
            
        self.ModeList.InsertItems([mode_txt], 0)

        # Now transpose the mode in cm^-1
        unit = UNITS[self.ModeUnit.GetCurrentSelection()]

        if unit == "cm^-1":
            self.Modes.append(mode)
        elif unit == "eV":
            self.Modes.append(mode * EV_TO_CM)
        elif unit == "THz":
            self.Modes.append(mode * THZ_TO_CM)
            
        

class GetRangeDialog(wx.Dialog):
    def __init__(self, parent, title="Single mode analysis", text= "Set the frequency range in which perform the analysys", size = (800, 320), current_wavelength=400):
        wx.Dialog.__init__(self, parent, title=title, size = size)

        # Setup the analisys region
        self.start_wl = current_wavelength - 5
        self.end_wl = current_wavelength + 5
        
        # Setup the GUI
        lbl_help = wx.StaticText(self, label=text)
        lbl_wl_range = wx.StaticText(self, label="Set the range")
        self.txt_wl_start = wx.TextCtrl(self)
        self.txt_wl_start.SetValue(str(self.start_wl))
        self.txt_wl_end = wx.TextCtrl(self)
        self.txt_wl_end.SetValue(str(self.end_wl))
        
        
        btn_apply = wx.Button(self, label="Apply")
        btn_cancel = wx.Button(self, label="Cancel")
        
        # Setup the sizer aspect of the window dialog
        data_sizer = wx.BoxSizer(wx.HORIZONTAL)
        data_sizer.Add(lbl_wl_range, 0, wx.ALIGN_LEFT | wx.LEFT)
        data_sizer.AddStretchSpacer(1)
        data_sizer.Add(self.txt_wl_start, 4, wx.LEFT)
        data_sizer.AddStretchSpacer(1)
        data_sizer.Add(self.txt_wl_end, 4, wx.RIGHT)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_apply, 3, wx.ALIGN_LEFT | wx.LEFT)
        btn_sizer.AddStretchSpacer(3)
        btn_sizer.Add(btn_cancel, 3, wx.ALIGN_RIGHT| wx.RIGHT)
        
        FinalSizer = wx.BoxSizer(wx.VERTICAL)
        FinalSizer.Add(lbl_help, 2, wx.EXPAND| wx.ALIGN_CENTER)
        FinalSizer.AddStretchSpacer(2)
        FinalSizer.Add(data_sizer, 2, wx.EXPAND)
        FinalSizer.AddStretchSpacer(1)
        FinalSizer.Add(btn_sizer, 2, wx.EXPAND)
        
        self.SetSizer(FinalSizer)
        self.Layout()
        
        
        # Now bind the events to the pressing of the buttons
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btn_cancel)
        self.Bind(wx.EVT_BUTTON, self.OnApply, btn_apply)
        
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        
    def OnApply(self, event):
        # Now simply return the text inside the CtrlTxt of the dialog
        try:
            self.start_wl= float(self.txt_wl_start.GetValue())
            self.end_wl = float(self.txt_wl_end.GetValue())
        except:
            err_dlg = wx.MessageDialog(self, "Error while converting to a float number one of the two text in the textboxes.", "Error", wx.ICON_ERROR)
            err_dlg.ShowModal()
            event.Skip()
            return
            
        self.EndModal(wx.ID_OK)
        
class LambdaAnalyzerDialog(wx.Dialog):
    def __init__(self, parent, title="Detailed analisys on the spectrum wavelength", lambda_min = 450, lambda_max = 450, N = 12, size=(800, 320)):
        wx.Dialog.__init__(self, parent, title=title, size = size)
        
        lbl_min_lambda = wx.StaticText(self, label="Start wl")
        lbl_max_lambda = wx.StaticText(self, label="End wl")
        lbl_counts = wx.StaticText(self, label="Intervals")
        
        self.txt_sw = wx.TextCtrl(self)
        self.txt_ew = wx.TextCtrl(self)
        self.txt_N = wx.TextCtrl(self)
        
        self.txt_sw.SetValue(str(lambda_min))
        self.txt_ew.SetValue(str(lambda_max))
        self.txt_N.SetValue(str(N))
        
        self.wl_start = lambda_min
        self.wl_end = lambda_max
        self.wl_N = N
        
        btn_ok = wx.Button(self, label="Ok")
        btn_cancel = wx.Button(self, label="Cancel")
        
        # Setuo sizer layout
        SingleSizer = wx.BoxSizer(wx.HORIZONTAL)
        SingleSizer.Add(lbl_min_lambda, 0, wx.ALIGN_LEFT)
        SingleSizer.AddStretchSpacer(1)
        SingleSizer.Add(self.txt_sw, 5)
        SingleSizer.AddStretchSpacer(1)
        SingleSizer.Add(lbl_max_lambda, 0, wx.ALIGN_LEFT)
        SingleSizer.AddStretchSpacer(1)
        SingleSizer.Add(self.txt_ew, 5)
        SingleSizer.AddStretchSpacer(1)
        SingleSizer.Add(lbl_counts, 0, wx.ALIGN_LEFT)
        SingleSizer.AddStretchSpacer(1)
        SingleSizer.Add(self.txt_N, 4)
        
        BtnSizer = wx.BoxSizer(wx.HORIZONTAL)
        BtnSizer.Add(btn_cancel)
        BtnSizer.AddStretchSpacer(1)
        BtnSizer.Add(btn_ok)
        
        TotalSizer= wx.BoxSizer(wx.VERTICAL)
        TotalSizer.Add(SingleSizer, 1, wx.EXPAND)
        TotalSizer.Add(BtnSizer, 1, wx.EXPAND)
        
        self.SetSizer(TotalSizer)
        self.Layout()
        
        # Event Handling
        self.Bind(wx.EVT_BUTTON, self.OnOk, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, btn_cancel)
        
    def OnOk(self, event):
        # Return the wanted results
        self.wl_start = Options.ToFloatNumber(self.txt_sw.GetValue())
        self.wl_end = Options.ToFloatNumber(self.txt_ew.GetValue())
        self.wl_N = Options.ToIntNumber(self.txt_N.GetValue())
        self.EndModal(wx.ID_OK)
        
    def OnCancel(self, event):
        self.EndModal(wx.ID_ABORT)
        
        
