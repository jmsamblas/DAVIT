#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *

#################################################################
#################################################################

class PlotDataAxesPanel(QDialog):

    #----------------------------------------------#

    def __init__(self, dataframe, app, app_root_path, parent):

        # inherit from QDialog
        QDialog.__init__(self)

        # main attributes
        self.dataframe = dataframe
        self.app = app
        self.app_root_path = app_root_path
        self.parent = parent

        # own attributes
        self.axis_index_dict = collections.OrderedDict()

        # load ui file
        uic.loadUi(os.path.join(self.app_root_path, "resources", "uis", "plot_data_axes_panel.ui"), self)

        # title and icon
        self.setWindowTitle("Axes & Variables")
        self.setWindowIcon(qta.icon("mdi.form-select"))

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # init default axis
        self.addNewAxis()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # listview models
        self.model_listView_axis = QStandardItemModel()
        self.model_listView_variables = QStandardItemModel()
        self.listView_axis.setModel(self.model_listView_axis)
        self.listView_variables.setModel(self.model_listView_variables)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # binding for the add button
        self.pushButton_add.clicked.connect(self.addNewAxis)

        # binding for click events on the axis listview
        self.listView_axis.clicked.connect(self.updateVariableListView)

        # accept and reject
        self.pushButton_yes.clicked.connect(self.acceptOverride)
        self.pushButton_no.clicked.connect(self.rejectOverride)

        return

    #----------------------------------------------#

    def updateVariableListView(self, index):

        # get axis name
        axis_name = self.model_listView_axis.itemFromIndex(index).text()

        # get variables
        variables = self.axis_index_dict[axis_name]

        # populate the listview
        self.model_listView_variables.clear()
        for var in variables:
            item = QStandardItem(str(var))
            self.model_listView_variables.appendRow(item)

        return

    #----------------------------------------------#

    def addNewAxis(self):

        # init axis name
        axis_name = f'y_{len(self.axis_index_dict)+1}'

        # init item
        item = QStandardItem(axis_name)

        # add item to the model
        self.model_listView_axis.appendRow(item)

        # update dict
        self.axis_index_dict[axis_name] = []
        self.axis_index_dict[axis_name] = [0,1,2,3,4,5,6]

        return

    #----------------------------------------------#

    def acceptOverride(self):

        # finally send the accept event with the output information
        self.accept()

        return

    #----------------------------------------------#

    def rejectOverride(self):

        # just reject and close window
        self.reject()

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # go to the reject function
        self.rejectOverride()

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################