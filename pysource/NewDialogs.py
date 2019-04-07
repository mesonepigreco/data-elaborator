import wx

UNITS = ["cm^-1", "eV", "THz"]
EV_TO_CM = 8065.54429
THZ_TO_CM = 33.35641

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

        # Label
        lbl_explain = wx.StaticText(self, label = "Mode active in the current molecule:")
        lbl_setup = wx.StaticText(self, label = "Set a new mode")

        # Sizers
        CurrentModeSizer = wx.BoxSizer(wx.VERTICAL)
        CurrentModeSizer.Add(lbl_explain, 1, wx.TOP | wx.ALIGN_LEFT)
        CurrentModeSizer.Add(self.ModeList, 5, wx.BOTTOM | wx.EXPAND)

        AddModeSizer = wx.BoxSizer(wx.HORIZONTAL)
        AddModeSizer.Add(self.ModeTxt, 4, wx.LEFT | wx.ALIGN_LEFT)
        AddModeSizer.AddStretchSpacer(1)
        AddModeSizer.Add(self.ModeUnit, 3, wx.RIGHT | wx.ALIGN_RIGHT)

        ButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        ButtonSizer.AddStretchSpacer(1)
        ButtonSizer.Add(self.CancelBtn, 0, wx.ALIGN_RIGHT | wx.RIGHT)
        ButtonSizer.Add(self.OkBtn, 0, wx.ALIGN_RIGHT |wx.RIGHT)

        NewModeSizer = wx.BoxSizer(wx.VERTICAL)
        NewModeSizer.Add(lbl_setup, 1, wx.ALIGN_CENTER)
        NewModeSizer.Add(AddModeSizer, 1, wx.ALIGN_CENTER | wx.RIGHT)
        NewModeSizer.Add(self.AddButton, 1, wx.ALIGN_CENTER | wx.RIGHT)
        NewModeSizer.AddStretchSpacer(1)
        NewModeSizer.Add(ButtonSizer, 1, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT)

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

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)
    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

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
        