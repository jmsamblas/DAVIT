#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.utils.big_data_table import BigDataFrameModel, BigDataTableView

#################################################################
#################################################################

class TableTab(QWidget):

    #----------------------------------------------#

    def __init__(self, app, dataframe, attributes, init_build, app_root_path = None, window_icon_path = None, parent = None, global_parent = None, min_big_data_sample_size = 1_000_000, chunk_size = 100_000, big_data_mode = False):

        # inherit from QWidget
        QWidget.__init__(self)

        # main attributes
        self.app = app
        self.dataframe = dataframe
        self.attributes = attributes
        self.init_build = init_build
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.parent = parent
        self.global_parent = global_parent
        self.min_big_data_sample_size = min_big_data_sample_size
        self.chunk_size = chunk_size
        self.big_data_mode = big_data_mode

        # own attributes
        self.tab_is_built = False
        self.use_big_data_table = True

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "table_tab.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        return

    #----------------------------------------------#

    def buildTab(self, dataframe):

        # copy or save the df
        if self.big_data_mode:
            self.dataframe = dataframe
        else:
            self.dataframe = dataframe.copy()

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # update boolean
        self.tab_is_built = True

        return

    #----------------------------------------------#

    def rebuildBigDataTable(self):

        # remove tableview from layout
        self.verticalLayout_stack.removeWidget(self.tableView)
        self.tableView.deleteLater()
        self.tableView = None

        # init table
        self.tableView = BigDataTableView(self.dataframe, chunk_size=self.chunk_size, parent=self.frame_holder)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.horizontalHeader().setMinimumSectionSize(50)
        self.verticalLayout_stack.addWidget(self.tableView)

        # update the view
        self.tableView.update()
        self.tableView.show()

        # scroll size handling
        self.tableView.setMinimumHeight(270)
        self.tableView.setMinimumWidth(480)

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # set scroll area (to make widget resizable)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # layout of the form
        self.verticalLayout_frame_holder = QVBoxLayout(self)
        self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
        self.verticalLayout_frame_holder.setContentsMargins(0, 0, 0, 0)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Raised)
        self.frame_holder.setObjectName("frame_holder")

        # set the main frame as the widget of the QScrollArea
        self.scroll_area.setWidget(self.frame_holder)

        # add the QScrollArea to the layout
        self.verticalLayout_frame_holder.addWidget(self.scroll_area)

        # main layout
        self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
        self.verticalLayout_stack.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_stack.setSpacing(0)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # CASE 1 (with big data table)
        if self.big_data_mode and self.use_big_data_table:

            # init table
            self.tableView = BigDataTableView(self.dataframe, chunk_size=self.chunk_size, parent=self.frame_holder)
            self.tableView.setObjectName("tableView")
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.horizontalHeader().setMinimumSectionSize(50)
            self.verticalLayout_stack.addWidget(self.tableView)

        # CASE 2 (typical table)
        else:

            # opts for performance
            if self.big_data_mode:
                include_error_list = False
                enable_column_options = False
                auto_resizing = False
            else:
                include_error_list = True
                enable_column_options = True
                auto_resizing = True

            # init table
            self.tableView = DataFrameWidget(parent=self.frame_holder, df=pd.DataFrame([]), include_error_list=include_error_list, enable_column_options=enable_column_options, auto_resizing=auto_resizing)
            self.tableView.setObjectName("tableView")
            self.tableView.horizontalHeader().setVisible(True)
            self.tableView.horizontalHeader().setMinimumSectionSize(50)
            self.verticalLayout_stack.addWidget(self.tableView)

            # set the dataframe
            self.tableView.setDataFrame(df=self.dataframe)

        # update the view
        self.tableView.update()
        self.tableView.show()

        # scroll size handling
        self.tableView.setMinimumHeight(270)
        self.tableView.setMinimumWidth(480)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################