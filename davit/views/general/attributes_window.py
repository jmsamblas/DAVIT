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

class AttributesWindow(QWidget):

    #----------------------------------------------#

    def __init__(self, app, attributes, display_path, app_root_path = None, window_icon_path = None, parent = None, global_parent = None, popup_window = False, qta_str_icon = ""):

        # inherit from QWidget
        QWidget.__init__(self)

        # main attributes
        self.app = app
        self.attributes = attributes
        self.display_path = display_path
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.parent = parent
        self.global_parent = global_parent
        self.popup_window = popup_window
        self.qta_str_icon = qta_str_icon

        # own attributes
        self.win_id = None
        self.data = pd.DataFrame([])

        # minimum size
        if self.popup_window:
            self.setMinimumSize(320, 180)

        # only if it is a popup
        if popup_window:
            self.setWindowTitle("Attributes Window (Popup)")
            self.setWindowIcon(QIcon(self.window_icon_path))
            self.windowAdjustmentAndResizing()

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "attributes_window.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # convert the attributes to a legit table format
        self.createDataForTable()

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def createDataForTable(self):

        # convert the attributes to a pandas dataframe
        self.data = pd.DataFrame(list(dict(self.attributes).items()), columns=['Key', 'Value'])

        return

    #----------------------------------------------#

    def windowAdjustmentAndResizing(self):

        # get the current screen size of the user
        screen_object = self.app.primaryScreen()
        screen_size = screen_object.size()
        screen_rect = screen_object.availableGeometry()

        # resize main window
        self.resize(screen_rect.width() * 3.5/10, screen_rect.height() * 2.5/10)

        # center main window
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(screen_rect.center())
        self.move(frame_geometry.topLeft())

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # set scroll area (to make widget resizable)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # layout of the form
        self.verticalLayout_frame_holder = QVBoxLayout(self)
        self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
        self.verticalLayout_frame_holder.setContentsMargins(0, 0, 0, 0)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Shadow.Raised)
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

        # create a frame to hold the label
        self.label_frame = QFrame(self.frame_holder)
        self.label_frame.setObjectName("label_frame")
        self.label_frame_layout = QVBoxLayout(self.label_frame)
        self.label_frame_layout.setObjectName("label_frame_layout")

        # Ccate and configure the label
        self.display_label = QLabel(self.label_frame)
        self.display_label.setObjectName("display_label")
        self.display_label.setText(self.display_path)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setWordWrap(True)

        # add the label to the frame's layout
        self.label_frame_layout.addWidget(self.display_label)

        # add the frame to the main layout
        self.verticalLayout_stack.insertWidget(0, self.label_frame)

        # some opts
        include_error_list = True
        enable_column_options = True
        auto_resizing = True

        # init table
        self.tableView = DataFrameWidget(parent=self.frame_holder, df=pd.DataFrame([]), include_error_list=include_error_list, enable_column_options=enable_column_options, auto_resizing=auto_resizing)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.horizontalHeader().setMinimumSectionSize(50)
        self.verticalLayout_stack.addWidget(self.tableView)

        # set the data
        self.tableView.setDataFrame(df=self.data)

        # update the view
        self.tableView.update()
        self.tableView.show()

        # scroll size handling
        self.tableView.setMinimumHeight(180)
        self.tableView.setMinimumWidth(320)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # only for popups
        if self.win_id != None:

            # print
            print("Closing attributes_window with id={}...".format(self.win_id))

            # manually deleting the key
            if self.parent:
                try:
                    del self.parent.attributes_table_new_windows[self.win_id]
                except Exception as xcp:
                    print(xcp)

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################