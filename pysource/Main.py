import os, sys, wx
import Options
import TableWindow
import Dialogs
import TimeResolvedWindow

# Creating the main window class
class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Scientific data-elaborator " + str(Options.GetVersion()))
        # Start adding the status bar and the menu bar to the window
        self.CreateStatusBar()
        Menu = wx.MenuBar()
        self.dirname = ""
        self.filename = ""

        # File menu
        self.filemenu = wx.Menu()
        AboutMenu = self.filemenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
        self.filemenu.AppendSeparator()
        OpenPrj = self.filemenu.Append(wx.ID_OPEN, "&Open", "Open a project from file")
        SavePrj = self.filemenu.Append(wx.ID_SAVE, "&Save", "Save the project to file")
        self.filemenu.AppendSeparator()
        ImportData = self.filemenu.Append(wx.ID_ANY, "Import from data...", "Import a table from data file")
        ExportData = self.filemenu.Append(wx.ID_ANY, "Export data", "Export the selected table into a text file")
        self.filemenu.AppendSeparator()
        Quit = self.filemenu.Append(wx.ID_EXIT, "Quit", "Close the program")
        Menu.Append(self.filemenu, "&File")

        # Toolbar Menu
        self.toolbarmenu = wx.Menu()
        CreateTable = self.toolbarmenu.Append(wx.ID_ANY, "Create Table", "Make a new grid with given dimention")
        OpenTimeDelay = self.toolbarmenu.Append(wx.ID_ANY, "Time-Resolved Spectrum Analisys", "Open a new window to perform data analisys of time resolved signal.")
        Menu.Append(self.toolbarmenu, "&Toolbar")
        
        # Bind the file menu actions OnEvent
        self.Bind(wx.EVT_MENU, self.OnAbout, AboutMenu)
        self.Bind(wx.EVT_MENU, self.OnOpenPrj, OpenPrj)
        self.Bind(wx.EVT_MENU, self.OnSavePrj, SavePrj)
        self.Bind(wx.EVT_MENU, self.OnImportData, ImportData)
        self.Bind(wx.EVT_MENU, self.OnExportData, ExportData)
        self.Bind(wx.EVT_MENU, self.OnQuit, Quit)
        
        self.Bind(wx.EVT_MENU, self.OnCreateTable, CreateTable)
        self.Bind(wx.EVT_MENU, self.OnOpenTRAnal, OpenTimeDelay)

        # Create the log text
        self.LogText = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        
        self.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.Sizer.Add(self.LogText, 1, wx.EXPAND)
        self.SetSizer(self.Sizer)
        self.Sizer.Layout()


        self.SetMenuBar(Menu)
        self.Show(True)

    def OnAbout(self, event):
        # Show a short dialog that includes the description of the program
        dlg = wx.MessageDialog(self,  Options.GetAbout(), "About data-elaborator " + str(Options.GetVersion()), wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnOpenPrj(self, event):
        pass

    def OnSavePrj(self, event):
        pass

    def OnImportData(self, event):
        self.dirname = ""
        dlg  = wx.FileDialog(self, "Choose a text file to import", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            table = TableWindow.TableFrame(self.filename)
            print self.dirname, self.filename
            #path = os.path.join(self.dirname, self.filename)
            #print "Path1: ", path
            path =dlg.GetPath()
            print "Path2: ", path
            table.LoadData(path)
        dlg.Destroy()


    def OnExportData(self, event):
        pass

    def OnQuit(self, event):
        # Quit the program
        self.Close(True)

    def  OnCreateTable(self, event):
        dlg = Dialogs.TwoIntMenu(self, "N of rows:", "N of columns:", "Setup the grid")
        if dlg.ShowModal() == wx.ID_OK:
            table = TableWindow.TableFrame("default")
            table.CreateGrid(int(dlg.txt1.GetValue()), int(dlg.txt2.GetValue()))
        dlg.Destroy()
        
    def OnOpenTRAnal(self, event):
        NewFrame = TimeResolvedWindow.Frame(self)
        NewFrame.Show()
        

app = wx.App(False)
frame = MainWindow(None)
app.SetTopWindow(frame)
app.MainLoop()
