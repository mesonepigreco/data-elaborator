# Load graphical and numerical libraries
import wx
import numpy as np
import scipy
import scipy.optimize

# Load matplotlib modules and their wx backend
import matplotlib as mpl

mpl.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

# Load misc modules
import Options, DataAnalisys, Dialogs
import TableWindow
import sys, os

beta = u"\u03B2"
PYTHON_EXECUTABLE = "python2"
DATALOG_PROGRAM = "/home/pione/Dropbox/LaboratorioScopigno/EsperimentoFinale/Scripts/ShowRawDatas.py"
PROBE_DATA = "/home/pione/Dropbox/LaboratorioScopigno/EsperimentoFinale/01_IVS_chexPon-Poff1.dat"



class Frame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title=Options.GetTitle(), size = Options.GetSize())
        # Define all the most important variable to be stored here
        self.DataFiles = []
        self.ProbeData = PROBE_DATA
        self.DatalogProgram = DATALOG_PROGRAM
        self.Data = None
        self.ModelModes = [] 

        # Add a menu bar
        menuBar = wx.MenuBar()

        # Setup the file menu
        menu = wx.Menu()
        menuBar.Append(menu, "&File")
        file_import_data = menu.Append(wx.ID_ANY, "Import data...", "Load data to be analyzed")
        file_exit = menu.Append(wx.ID_ANY, "Exit")
        data_menu = wx.Menu()
        
        # Now build the menu for the data elaboration
        menuBar.Append(data_menu, "&Data Elaboration")
        DM_load_probe_file = data_menu.Append(wx.ID_ANY, "Import Probe Spectrum", "Load the spectrum of the probe")
        DM_set_analyzer_script = data_menu.Append(wx.ID_ANY, "Set analyzer script", "Set the script to be runned when analizing a single data file.")
        DM_setup_model = data_menu.Append(wx.ID_ANY, "Setup molecule model", "Set the expected frequency to be shown in the figures")
        
        data_menu.AppendSeparator()
        DM_GetProbeDataTable = data_menu.Append(wx.ID_ANY, "Get Probe Spectrum Table", "Build the table for the selected probe specrum file")
        DM_analyze_mode_dependence = data_menu.Append(wx.ID_ANY, "Analyze mode intensity",  "Mean in a region of the signal spectrum and show the dependence of the signal intensity on the other variable (usually the probe spectrum)")
        DM_setup_flags = data_menu.Append(wx.ID_ANY, "Setup Analisys' flags", "Setup the flags to be used into the analisys")        
        DM_GetCAFromData = data_menu.Append(wx.ID_ANY, "Get Coherent Artifact from data", "Get a table with the chirp evaluated using CA")        
        DM_GetLambdaAnalisys = data_menu.Append(wx.ID_ANY, "Get Spectrum Analisys", "Perform a spectrum analisys at each small probe range")        
        self.SetMenuBar(menuBar)

        # Binding menu events
        self.Bind(wx.EVT_MENU, self.OnClose, file_exit)
        self.Bind(wx.EVT_MENU, self.OnAddFile, file_import_data)
        self.Bind(wx.EVT_MENU, self.OnLoadProbeFile, DM_load_probe_file)
        self.Bind(wx.EVT_MENU, self.OnSetupMoleculeModel, DM_setup_model)
        self.Bind(wx.EVT_MENU, self.OnSetAnalyzerScript, DM_set_analyzer_script)
        self.Bind(wx.EVT_MENU, self.OnGetProbeDataTable, DM_GetProbeDataTable)        
        self.Bind(wx.EVT_MENU, self.OnAnalyzeModeDependence, DM_analyze_mode_dependence)
        self.Bind(wx.EVT_MENU, self.OnSetupFlags, DM_setup_flags)
        self.Bind(wx.EVT_MENU, self.OnGetCAFromData, DM_GetCAFromData)
        self.Bind(wx.EVT_MENU, self.OnGetLambdaAnalisys, DM_GetLambdaAnalisys)
        

        self.main_panel = wx.Panel(self)
        self.options_panel = wx.Panel(self.main_panel)
        self.results_panel = wx.Panel(self.main_panel)

        
        # Setup the options panel
        # Select the probe lambda selection
        probe_lambda_label = wx.StaticText(self.options_panel, label="Probe wavelength window:")
        lambda_0 = wx.StaticText(self.options_panel, label=u"\u03BB_0")
        lambda_1 = wx.StaticText(self.options_panel, label=u"\u03BB_1")
        N_lambda = wx.StaticText(self.options_panel, label=u"N_\u03BB")

        self.probe_wl_start_txt = wx.TextCtrl(self.options_panel)
        self.probe_wl_end_txt = wx.TextCtrl(self.options_panel)
        self.probe_wl_start_txt.SetValue("%d" % (Options.GetDefaultLambdaProbe()[0]))
        self.probe_wl_end_txt.SetValue("%d" % (Options.GetDefaultLambdaProbe()[1]))
        self.probe_N_wl = wx.TextCtrl(self.options_panel)
        self.probe_N_wl.SetValue("%d" % Options.GetDefaultNLambdaProbe())

        
        # The starting time and the ending time of the simulation
        time_label = wx.StaticText(self.options_panel, label="Time window (ps):")
        t_0_label = wx.StaticText(self.options_panel, label="t_0")
        T_label = wx.StaticText(self.options_panel, label="Total time")

        self.t0_txt = wx.TextCtrl(self.options_panel)
        self.T_txt = wx.TextCtrl(self.options_panel)
        self.t0_txt.SetValue("%.2f" % (Options.GetDefaultTime()[0]))
        self.T_txt.SetValue("%.2f" % (Options.GetDefaultTime()[1]))
        
        # Add Options Flag button
        # TODO

        # Zero padding - Kaiser Window
        zp_label = wx.StaticText(self.options_panel, label="Zero padding length  x ")
        self.zp_txt = wx.TextCtrl(self.options_panel)
        self.zp_txt.SetValue("%d" % Options.GetDefaultZP())

        kw_label = wx.StaticText(self.options_panel, label=u"Kaiser-Bessel window \u03B2 = " )
        self.kw_txt = wx.TextCtrl(self.options_panel)
        self.kw_txt.SetValue("%.2f" %  Options.GetDefaultKW())

        
        # Select files to be analyzed
        FileList_label = wx.StaticText(self.options_panel, label="Files to be analyzed")
        self.FileList = wx.ListBox(self.options_panel, style=wx.LB_EXTENDED | wx.LB_NEEDED_SB)
        self.FileList.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopupMenu) # bind the menu
        AddButton = wx.Button(self.options_panel, label="Add data file")
        DeleteButton = wx.Button(self.options_panel, label="Delete data file")

        # Add the Analyze button
        AnalButton = wx.Button(self.options_panel, label="Analyze data")
        

        # Now prepare the figure on the results panel
        self.figure_top = mpl.figure.Figure()
        self.figure_bottom = mpl.figure.Figure()

        self.axes_top = self.figure_top.add_subplot(111)
        self.axes_bottom = self.figure_bottom.add_subplot(111)

        # Get the correct size of the panel
        FigureWidth = Options.GetSize()[0] / 2
        FigureHeight = int(Options.GetSize()[1] * 3 / 10.)
        FigureSize = (FigureWidth, FigureHeight)
        PFigureSize = (FigureWidth, FigureHeight * 4 / 3) # The panel needs also the toolbar (it must be bigger than the figure)
        
        self.c_panel_top = wx.Panel(self.results_panel, size = PFigureSize)
        self.c_panel_bottom = wx.Panel(self.results_panel, size = PFigureSize)
        self.canvas_top = FigureCanvas(self.c_panel_top, wx.ID_ANY, self.figure_top)
        self.canvas_bottom = FigureCanvas(self.c_panel_bottom, wx.ID_ANY, self.figure_bottom)

        #self.canvas_top.SetSize(FigureSize)
        #self.canvas_bottom.SetSize(FigureSize)

        toolbar_top = NavigationToolbar2Wx(self.canvas_top)
        toolbar_bottom = NavigationToolbar2Wx(self.canvas_bottom)
        toolbar_top.Realize()
        toolbar_bottom.Realize()

        # Add the toolbar to the figure panel
        CPTSizer = wx.BoxSizer(wx.VERTICAL)
        CPBSizer = wx.BoxSizer(wx.VERTICAL)
        CPTSizer.Add(self.canvas_top, 1,  wx.GROW)
        CPTSizer.Add(toolbar_top, 0, wx.GROW)
        CPBSizer.Add(self.canvas_bottom, 1,  wx.GROW)
        CPBSizer.Add(toolbar_bottom, 0, wx.GROW)

        self.c_panel_top.SetSizer(CPTSizer)
        self.c_panel_bottom.SetSizer(CPBSizer)
        toolbar_top.update()
        toolbar_bottom.update()

        

        # Select range of probe wavelength in which see the mean
        wl0_mean_lb = wx.StaticText(self.results_panel, label=u"Mean: \u03BB_0")
        wl1_mean_lb = wx.StaticText(self.results_panel, label=u"\u03BB_1")
        self.wl0_mean_txt = wx.TextCtrl(self.results_panel)
        self.wl0_mean_txt.SetValue("%d" % Options.GetDefaultLambdaProbe()[0])
        self.wl1_mean_txt = wx.TextCtrl(self.results_panel)
        self.wl1_mean_txt.SetValue("%d" % Options.GetDefaultLambdaProbe()[1])
        ApplyButton = wx.Button(self.results_panel, label="Apply")

        # Select the w range for the fft spectrum to be shown
        w0_zoom_lb = wx.StaticText(self.results_panel, label=u"FFT zoom (cm^-1): \u03C9_0")
        w1_zoom_lb = wx.StaticText(self.results_panel, label=u"\u03C9_1")
        Nw_lb = wx.StaticText(self.results_panel, label=u"\u03C9 subdivision")
        self.w0_zoom_txt = wx.TextCtrl(self.results_panel)
        self.w0_zoom_txt.SetValue("%d" % Options.GetWRange()[0])
        self.w1_zoom_txt = wx.TextCtrl(self.results_panel)
        self.w1_zoom_txt.SetValue("%d" % Options.GetWRange()[1])
        self.Nw_txt =  wx.TextCtrl(self.results_panel)
        self.Nw_txt.SetValue("%d" % Options.GetNWDefault())
        SetWRangeBtn = wx.Button(self.results_panel, label=u"Set \u03C9 range")
        
    
        
        # SETUP SIZERS
        # Place the lambda probe into a sizer
        LambdaProbeSizer = wx.BoxSizer(wx.HORIZONTAL)
        LambdaProbeSizer.Add(probe_lambda_label, 5, wx.ALIGN_LEFT | wx.LEFT)
        LambdaProbeSizer.AddStretchSpacer(1)
        LambdaProbeSizer.Add(lambda_0, 0, wx.ALIGN_RIGHT | wx.RIGHT)
        LambdaProbeSizer.Add(self.probe_wl_start_txt, 3,  wx.RIGHT | wx.ALIGN_RIGHT)
        LambdaProbeSizer.AddStretchSpacer(1)
        LambdaProbeSizer.Add(lambda_1, 0, wx.ALIGN_RIGHT | wx.RIGHT)
        LambdaProbeSizer.Add(self.probe_wl_end_txt, 3,   wx.RIGHT | wx.ALIGN_RIGHT)
        LambdaProbeSizer.AddStretchSpacer(1)
        LambdaProbeSizer.Add(N_lambda, 0, wx.ALIGN_RIGHT)
        LambdaProbeSizer.Add(self.probe_N_wl, 3, wx.ALIGN_RIGHT)

        
        TimeSizer = wx.BoxSizer(wx.HORIZONTAL)
        TimeSizer.Add(time_label, 5, wx.ALIGN_LEFT | wx.LEFT)
        TimeSizer.AddStretchSpacer(1)
        TimeSizer.Add(t_0_label, 1, wx.ALIGN_RIGHT | wx.RIGHT)
        TimeSizer.Add(self.t0_txt, 3, wx.RIGHT | wx.ALIGN_RIGHT)
        TimeSizer.AddStretchSpacer(1)
        TimeSizer.Add(T_label, 2, wx.ALIGN_RIGHT | wx.RIGHT)
        TimeSizer.Add(self.T_txt, 2,  wx.RIGHT | wx.ALIGN_RIGHT)

        
        AdvancedOptionsSizer = wx.BoxSizer(wx.HORIZONTAL)
        AdvancedOptionsSizer.Add(zp_label, 4, wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_BOTTOM)
        AdvancedOptionsSizer.Add(self.zp_txt, 3, wx.LEFT | wx.ALIGN_LEFT | wx.ALIGN_BOTTOM)
        AdvancedOptionsSizer.AddStretchSpacer(1)
        AdvancedOptionsSizer.Add(kw_label, 4, wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
        AdvancedOptionsSizer.Add(self.kw_txt, 3, wx.RIGHT | wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)

        
        FileListButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        FileListButtonSizer.Add(AddButton, 1, wx.ALIGN_LEFT)
        FileListButtonSizer.AddStretchSpacer(4)
        FileListButtonSizer.Add(DeleteButton, 1, wx.ALIGN_RIGHT)

        FileListSizer = wx.BoxSizer(wx.VERTICAL)
        FileListSizer.Add(FileList_label, 1, wx.ALIGN_TOP)
        FileListSizer.Add(self.FileList, 5, wx.EXPAND)
        FileListSizer.Add(FileListButtonSizer, 1, wx.EXPAND)
        

        # Setup the Options Sizer
        OptionsPanelSizer = wx.BoxSizer(wx.VERTICAL)
        OptionsPanelSizer.Add(LambdaProbeSizer, 1, wx.ALIGN_TOP | wx.TOP| wx.EXPAND)
        OptionsPanelSizer.Add(TimeSizer, 1, wx.ALIGN_TOP | wx.TOP | wx.EXPAND)
        OptionsPanelSizer.Add(AdvancedOptionsSizer, 1, wx.ALIGN_TOP | wx.TOP | wx.EXPAND)
        
        OptionsPanelSizer.Add(wx.StaticLine(self.options_panel), 1, wx.EXPAND)
        OptionsPanelSizer.Add(FileListSizer, 5, wx.EXPAND)
        OptionsPanelSizer.AddStretchSpacer(1)
        OptionsPanelSizer.Add(AnalButton, 1, wx.ALIGN_LEFT | wx.ALIGN_BOTTOM)


        # Setup the sizer in the results sizer region
        # Setup the figure canvas sizer
        FigureSizer = wx.BoxSizer(wx.VERTICAL)
        FigureSizer.Add(self.c_panel_top, 10, wx.TOP | wx.EXPAND)
        #FigureSizer.Add(wx.StaticLine(self.results_panel), 0)
        FigureSizer.Add(self.c_panel_bottom, 10, wx.TOP | wx.EXPAND)

        # Setup the lambda mean sizer
        LambdaMeanSizer = wx.BoxSizer(wx.HORIZONTAL)
        LambdaMeanSizer.Add(wl0_mean_lb, 0, wx.ALIGN_LEFT)
        LambdaMeanSizer.Add(self.wl0_mean_txt, 2, wx.ALIGN_LEFT)
        LambdaMeanSizer.AddStretchSpacer(1)
        LambdaMeanSizer.Add(wl1_mean_lb, 0, wx.ALIGN_RIGHT)
        LambdaMeanSizer.Add(self.wl1_mean_txt, 2, wx.ALIGN_LEFT)
        LambdaMeanSizer.Add(ApplyButton, 0, wx.ALIGN_RIGHT | wx.RIGHT)

        # Setup the w setting
        WSettingSizer = wx.BoxSizer(wx.HORIZONTAL)
        WSettingSizer.Add(w0_zoom_lb, 0, wx.ALIGN_LEFT)
        WSettingSizer.Add(self.w0_zoom_txt, 5 , wx.ALIGN_LEFT)
        WSettingSizer.AddStretchSpacer(1)
        WSettingSizer.Add(w1_zoom_lb, 0, wx.ALIGN_RIGHT)
        WSettingSizer.Add(self.w1_zoom_txt, 5, wx.ALIGN_LEFT)
        WSettingSizer.AddStretchSpacer(1)
        WSettingSizer.Add(Nw_lb, 0, wx.ALIGN_RIGHT)
        WSettingSizer.Add(self.Nw_txt, 4, wx.ALIGN_LEFT)
        WSettingSizer.Add(SetWRangeBtn, 0, wx.ALIGN_RIGHT | wx.RIGHT)
        

        
        # Setup the Results Sizer
        ResultsPanelSizer = wx.BoxSizer(wx.VERTICAL)
        ResultsPanelSizer.Add(FigureSizer, 1, wx.TOP | wx.EXPAND)
        ResultsPanelSizer.Add(LambdaMeanSizer, 0, wx.BOTTOM | wx.ALIGN_BOTTOM | wx.EXPAND)
        ResultsPanelSizer.Add(WSettingSizer, 0, wx.BOTTOM | wx.ALIGN_BOTTOM | wx.EXPAND)
        self.options_panel.SetSizer(OptionsPanelSizer)
        self.results_panel.SetSizer(ResultsPanelSizer)
        self.results_panel.Layout()
        
        # Setup the main panel
        FirstBox = wx.BoxSizer(wx.HORIZONTAL)
        FirstBox.Add(self.options_panel, 1, wx.ALIGN_LEFT | wx.LEFT | wx.EXPAND)
        #FirstBox.Add(wx.StaticLine(self.main_panel, style = wx.LI_VERTICAL), 1, wx.TOP)
        FirstBox.Add(self.results_panel, 1, wx.ALIGN_RIGHT | wx.RIGHT| wx.EXPAND)
        self.main_panel.SetSizer(FirstBox)
        self.main_panel.Layout()
        
        # Event binding
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, self.OnAddFile, AddButton)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteFile, DeleteButton)
        self.Bind(wx.EVT_BUTTON, self.OnAnalyzeData, AnalButton)
        self.Bind(wx.EVT_BUTTON, self.OnMeanLambda, ApplyButton)
        self.Bind(wx.EVT_BUTTON, self.OnSetWRange, SetWRangeBtn)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnClose(self, event):
        del self.Data
        self.Destroy()

    def OnShowPopupMenu(self, event):
        # Build the popup menu
        menu = wx.Menu()
        show_single_data = wx.MenuItem(menu, wx.NewId(), "Show whole datalog")
        menu.AppendItem(show_single_data)
        
        self.Bind(wx.EVT_MENU, self.OnShowWholeDatalog, show_single_data)
        self.PopupMenu(menu)
        menu.Destroy()

    def OnShowWholeDatalog(self, event):
        # Get the datafile
        indices = list(self.FileList.GetSelections())
        if len(indices) != 1:
            # Show an error message that ask the user to select only one file
            msg = wx.MessageDialog(self, "Error, you must select one and only one file to analyze.", "Error", wx.ICON_ERROR)
            msg.ShowModal()
            msg.Destroy()
            event.Skip()
            return

        # Select the index
        index = indices[0]

        # Now get the correct filename
        filename = self.DataFiles[index]

        # Call the datalog program
        os.system("%s %s %s %s" % (PYTHON_EXECUTABLE, self.DatalogProgram, filename, self.ProbeData))
        event.Skip()

    def OnAddFile(self, event):
        """ 
        Add a data file inside the file list 
        """

        # Show a file reader message
        LoadFileDialog = wx.FileDialog(self, "Load",
                                       "", "", "all (*.*) |*.*",
                                       wx.FD_OPEN | wx.FD_MULTIPLE)
        if LoadFileDialog.ShowModal() == wx.ID_OK:
            filepaths = LoadFileDialog.GetPaths()

            # If the selected files are more than one
            for filepath in filepaths:
                # Add the choosen file in the file list
                self.DataFiles.append(filepath)
                index = len(self.DataFiles) - 1
            
            
                # Now get the a shorter version of the name of the data file to be shown in the list
                first_dir = filepath.rfind(Options.GetFileBar())
                second_dir = filepath.rfind(Options.GetFileBar(), 0, first_dir)
                show_path = "..." + filepath[second_dir : ]
            
            
                # Add the text on the combo list
                
                self.FileList.InsertItems([show_path], index)
        LoadFileDialog.Destroy()
        event.Skip()

    def OnDeleteFile(self, event):
        # Choose the indices to be deleted
        indices = list(self.FileList.GetSelections())

        # Sort the indices from the maximum to the minimum
        indices.sort()
        indices.reverse()

        # Now delete all the given indices
        for i in indices:
            # Delete from the file list
            self.DataFiles.pop(i)
            # Delete from the listbox
            self.FileList.Delete(i)

        print self.DataFiles
        event.Skip()

    def OnAnalyzeData(self, event):
        # Check if data is filled with something
        if self.Data:
            dialog = wx.MessageDialog(self, "Some data are already been analized, do you want to cancel them?", "Attention", wx.NO_DEFAULT | wx.YES_NO)
            if dialog.ShowModal() == wx.ID_NO:
                event.Skip()
                dialog.Destroy()
                return
            dialog.Destroy()

        # Now create the data
        t0 = float(self.t0_txt.GetValue())
        T = float(self.T_txt.GetValue())
        wl0 = float(self.probe_wl_start_txt.GetValue())
        wl1 = float(self.probe_wl_end_txt.GetValue())
        N_wl = float(self.probe_N_wl.GetValue())
        ZP_len = int(self.zp_txt.GetValue())
        KW_beta = Options.ToFloatNumber(self.kw_txt.GetValue())
        
        # Create progress bar dialog
        pb_dlg = wx.ProgressDialog(title="Progress information", message="Data analisys initialized...", maximum = len(self.DataFiles), parent = self, style= wx.PD_CAN_ABORT)
        
        self.Data = DataAnalisys.Data(self.DataFiles, t0, t0 + T, wl0, wl1, N_wl, ZP_len, pb_dlg, KW_beta)
        # Now destroy the dialog
        pb_dlg.Destroy()

        # Check if the data are been correctly evaluated
        
        # Select the mean lambda window
        wl0_mean = float(self.wl0_mean_txt.GetValue())
        wl1_mean = float(self.wl1_mean_txt.GetValue())
        w0 = Options.ToFloatNumber(self.w0_zoom_txt.GetValue())
        w1 = Options.ToFloatNumber(self.w1_zoom_txt.GetValue())

        # Clear existing figures
        self.axes_top.clear()
        self.axes_bottom.clear()
        
        self.Data.PlotColorMap(self.axes_top, wl0_mean, wl1_mean, w0, w1)
        self.Data.PlotMeanLambda(wl0_mean, wl1_mean, w0, w1, self.axes_bottom)

        for mode in self.ModelModes:
            self.axes_bottom.axvline(mode, color="r", ls="dashed")
            self.axes_top.axvline(mode, color="k", ls="dashed")
            
        # Draw all
        self.canvas_top.draw()
        self.canvas_bottom.draw()

    def OnMeanLambda(self, event):
        # If data is not filled show an error message
        if not self.Data:
            dialog = wx.MessageDialog(self, "Error, you nead to analyze some data before mean on lambda.", "Error", wx.ICON_ERROR)
            dialog.ShowModal()
            dialog.Destroy()
            return

        # Replot the last mean graphics
        wl0_mean = Options.ToFloatNumber(self.wl0_mean_txt.GetValue())
        wl1_mean = Options.ToFloatNumber(self.wl1_mean_txt.GetValue())
        
        w0 = Options.ToFloatNumber(self.w0_zoom_txt.GetValue())
        w1 = Options.ToFloatNumber(self.w1_zoom_txt.GetValue())

        self.axes_bottom.clear()
        self.Data.PlotMeanLambda(wl0_mean, wl1_mean, w0, w1, self.axes_bottom)

        # Draw model lines
        for mode in self.ModelModes:
            self.axes_bottom.axvline(mode, color="r", ls="dashed")
            
        # Set limits
        self.axes_bottom.set_xlim((w0, w1))
        self.canvas_bottom.draw()
        
    def OnLoadProbeFile(self, event):
        # Change the probe file
        dialog = wx.FileDialog(self, "Load the probe file",
                                       "", "", "all (*.*) |*.*",
                                       wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            # Now load the file
            self.ProbeData = dialog.GetPath()
        dialog.Destroy()

    def OnSetAnalyzerScript(self, event):
        # Change the analyzer script
        dialog = wx.FileDialog(self, "Load the probe file",
                                       "", "", "all (*.*) |*.*",
                                       wx.FD_OPEN)
        dialog.SetPath(self.DatalogProgram)
        if dialog.ShowModal() == wx.ID_OK:
            # Now load the file
            self.ProbeData = dialog.GetPath()
        dialog.Destroy()

    def OnSetupMoleculeModel(self, event):
        model_dlg = Dialogs.ModelDialog(self, model_modes = self.ModelModes)
        
        if model_dlg.ShowModal() == wx.ID_OK:
            self.ModelModes = model_dlg.Modes
        print self.ModelModes

        model_dlg.Destroy()
        event.Skip()
        
    def OnSetWRange(self, event):
        # Get the new w range
        try:
            w0 = float(self.w0_zoom_txt.GetValue())
            w1 = float(self.w1_zoom_txt.GetValue())
            N_w = int(self.Nw_txt.GetValue())
        except:
            dlg = wx.MessageDialog(self, u"Error, you must specify correctly both the \u03C9 range (floating point numbers) and the \u03C9 sampling (integer).", "Error", wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Check that some data already exists
        if not self.Data:
            dlg = wx.MessageDialog(self, u"Error, before setting the \u03C9 range you must analyze some data.", "Error", wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Reanalize data
        print (w0, w1, N_w)
        self.Data.MeanAnalyzedData(w0, w1, N_w)
        # Now plot the new data
        # Clear existing figures
        self.axes_top.clear()
        self.axes_bottom.clear()
        
        # Select the mean lambda window
        wl0_mean = Options.ToFloatNumber(self.wl0_mean_txt.GetValue())
        wl1_mean = Options.ToFloatNumber(self.wl1_mean_txt.GetValue())
        
        # Set the correct w range (and lambda)
        l0 = Options.ToFloatNumber(self.probe_wl_start_txt.GetValue())
        l1 = Options.ToFloatNumber(self.probe_wl_end_txt.GetValue())
        
        self.axes_top.set_xlim(w0, w1)
        self.axes_top.set_ylim(l0, l1)
        self.axes_bottom.set_xlim(w0, w1)
        
        self.Data.PlotMeanLambda(wl0_mean, wl1_mean, w0, w1, self.axes_bottom)
        self.Data.PlotColorMap(self.axes_top, l0, l1, w0, w1)

        for mode in self.ModelModes:
            self.axes_bottom.axvline(mode, color="r", ls="dashed")
            self.axes_top.axvline(mode, color="k", ls="dashed")

            
        # Draw all
        self.canvas_top.draw()
        self.canvas_bottom.draw()
        
    def OnGetProbeDataTable(self, evnet):
        """ This method create a table using the data present in the spectrum file passed throught the analysys.
        Only the first two line of the spectrum are read, the first is supposed to contain the wavelength, while the second 
        is supposed to contain the probe spectrum intensity"""
        
        # Load the probe data file
        if not self.ProbeData:
            # Error, you must specify a correct probe
            error_dlg = wx.MessageDialog(self, "Error, you must specify a probe file", "Error", wx.ICON_ERROR)
            error_dlg.ShowModal()
            error_dlg.Destroy()
            
            # Load the probe data
            self.OnLoadProbeFile(None)
        
        # Check if the selected file exists
        if not os.path.exists(self.ProbeData):
            # Error, the selected file doesn't exists
            error_dlg = wx.MessageDialog(self, "Error, the specified probe file doesn't exists. Chose an other", "Error", wx.ICON_ERROR)
            error_dlg.ShowModal()
            error_dlg.Destroy()
            
            # Load the probe data
            self.OnLoadProbeFile(None)
            
        try:
            ProbeSpectrum = np.loadtxt(self.ProbeData)
        except:
            error_dlg = wx.MessageDialog(self, "Error while loading the selected file.", "Error", wx.ICON_ERROR)
            error_dlg.ShowModal()
            error_dlg.Destroy()
            return 

        # Check that the file has at least two columns
        shape = np.shape(ProbeSpectrum)
        if shape[1] < 2:
            error_dlg = wx.MessageDialog(self, "Error the selected probe file must have at least two columns", "Error", wx.ICON_ERROR)
            error_dlg.ShowModal()
            error_dlg.Destroy()
            return 
        
        # Now everithing should work, load the two columns
        wl = ProbeSpectrum[:, 0]
        spectrum = ProbeSpectrum[:, 1]
        
        # Now create a table with the given array
        tlb = TableWindow.TableFrame("Probe spectrum")
        tlb.CreateGrid(len(wl), 2)
        tlb.SetColumnFromArray(0, wl)
        tlb.SetColumnFromArray(1, spectrum)
            
        
    def OnAnalyzeModeDependence(self, event):
        """ This method creates a new window that let you choose the selected region of the spectrum in which perform the
        analisys, and then creates a table with the resulting data"""
        print "Ciao"
        # Check if some data is already been analyzed.
        if not self.Data:
            # Error
            err_dlg = wx.MessageDialog(self, "Error, no data has been analyzed.", "Error", wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
            return
        
        # Get the range to performe the analysys
        range_dlg = Dialogs.GetRangeDialog(self)
        if range_dlg.ShowModal() == wx.ID_OK:
            start_freq = range_dlg.start_wl
            end_freq = range_dlg.end_wl
            
            # Take the analyzed data in the selected region
            freq_index_start = np.argmin( np.abs(self.Data.mean_freq - start_freq) )
            freq_index_end = np.argmin( np.abs(self.Data.mean_freq - end_freq))
            
            # Get the reshaped data
            fft_data = np.abs( self.Data.mean_fft_data[:, freq_index_start : freq_index_end])
            probe_wl = np.copy(self.Data.mean_wl)
            
            # Mean the fft data on the first row
            fft_data = np.mean(fft_data, axis=1)
            
            # Now create a table with probe wl and fft data
            tlb = TableWindow.TableFrame("Intensity of the %d cm-1 mode." % ( (start_freq + end_freq) / 2))
            tlb.CreateGrid(len(fft_data), 2)
            tlb.SetColumnFromArray(0, probe_wl)
            tlb.SetColumnFromArray(1, fft_data)
            
    def OnSetupFlags(self, event):
        """ This method creates a dialog in which flag can be selected and fixed in value, usefull to setup flags inside
        the data-analisys script """
        
        SetupFlagsDlg = Dialogs.FlagsDialog(self, "Select Flag value", "All the analisys flags are listed above, set them value at your whishes", Options.GetFlagsNames(), ["True", "False"])
        if SetupFlagsDlg.ShowModal() == wx.ID_OK:
            # Take the value from the selected flag
            flags = Options.GetFlagsNames()
            for i in range(0, len(flags)):
                value = SetupFlagsDlg.cmbs[i].GetValue()
                
                # Check that all the values are correctly setted
                if not (value in ["True", "False"]):
                    err_dlg = wx.MessageDialog(self, "Error, all the flags must have a valid value", "Error", wx.ICON_ERROR)
                    err_dlg.ShowModal()
                    err_dlg.Destroy()
                    return
                
                Options.SetFlagByName(flags[i], value)
        
        SetupFlagsDlg.Destroy()
        
    def OnGetCAFromData(self, event):
        """ Get the CA from the data analized """
        
        # Check if some data is already been analyzed.
        if not self.Data:
            # Error
            err_dlg = wx.MessageDialog(self, "Error, no data has been analyzed.", "Error", wx.ICON_ERROR)
            err_dlg.ShowModal()
            err_dlg.Destroy()
            return
            
        # Now get the CA
        tlb = TableWindow.TableFrame("CA time data")
        tlb.CreateGrid(len(self.Data.mean_wl), 2)
        tlb.SetColumnFromArray(0, self.Data.mean_wl)
        tlb.SetColumnFromArray(1, self.Data.mean_t_ca)
    
    def OnGetLambdaAnalisys(self, event):
        """ This method call a window to setup the lambda analisys and then creates a table with the analisys at each choosen lambda. """
        # Call the dialog
        dlg = Dialogs.LambdaAnalyzerDialog(self, lambda_min = Options.ToFloatNumber(self.probe_wl_start_txt.GetValue()), lambda_max = Options.ToFloatNumber(self.probe_wl_end_txt.GetValue()))
        if dlg.ShowModal() == wx.ID_OK:
            # Take the correct starting and ending lambda values
            wl0 = dlg.wl_start
            wl1 = dlg.wl_end
            N_wl = dlg.wl_N
            
            # Obtain the division
            wl_steps = np.linspace(wl0, wl1, N_wl + 1)
            data = []
            freq_axis = self.Data.mean_freq
            for i in range(0, N_wl):
                start_wl = wl_steps[i]
                end_wl = wl_steps[i+1]
                
                data.append(self.Data.GetMeanLambda(start_wl, end_wl))


            # Ask if the user wants the errors
            new_dlg = wx.MessageDialog(self, "Do you want to add errors?", "Ask", wx.YES_NO)
            errors = False
            if new_dlg.ShowModal() == wx.ID_YES:
                errors = True
                # Add the errors inside the descriptions
                for i  in range(0, N_wl):
                    start_wl = wl_steps[i]
                    end_wl = wl_steps[i+1]
                    
                    data.append(self.Data.GetMeanLambdaError(start_wl, end_wl))
            new_dlg.Destroy()
                    
            
            # Now create a table
            tlb = TableWindow.TableFrame("Lambda analisys of the time-resolved signal")
            tlb.CreateGrid(len(freq_axis), len(data) + 1)
            tlb.SetColumnFromArray(0, freq_axis)
            tlb.ColumnProprieties[0][Options.NAME] = "$\omega$ [cm$^{-1}$]"
            tlb.ColumnProprieties[0][Options.GRAPH_RULE] = "X"
            
            # Setup all the other columns
            for i in range(0, N_wl):
                spectrum = data[i]
                tlb.SetColumnFromArray(i + 1, spectrum)
                tlb.ColumnProprieties[i + 1][Options.NAME] = "$ %.1f < \lambda < %.1f$" % (wl_steps[i], wl_steps[i+1])
                tlb.ColumnProprieties[i + 1][Options.GRAPH_RULE] = "Y"
                tlb.plot_colors.append( Options.COLORS[i % len(Options.COLORS)] )
                tlb.plot_linesize.append( 1 )
                tlb.plot_linestyle.append( "solid" )
                tlb.plot_styles.append( "." )

                if errors:
                    # Setup the correct error for the selected dataset
                    tlb.ColumnProprieties[i + 1][Options.ASSOCIATED_ERROR] = i + 1 + N_wl
                    tlb.ColumnProprieties[i + 1 + N_wl][Options.ASSOCIATED_VALUE] = i + 1
                    tlb.ColumnProprieties[i + 1 + N_wl][Options.IS_ERROR] = True
                    tlb.SetColumnFromArray(i + 1 + N_wl, data[i + N_wl])
            
            # Update the labels
            tlb.UpdateLabels()
        
        dlg.Destroy()
                                
        
"""
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = Frame().Show()
    app.MainLoop()
    sys.exit(0)
"""
