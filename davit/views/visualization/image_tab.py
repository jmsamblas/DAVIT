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

class ImageTab(QWidget):

    #----------------------------------------------#

    def __init__(self, app, dataframe, attributes, init_build, app_root_path = None, window_icon_path = None, parent = None, global_parent = None, color_dict = None):

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
        self.tab_is_built = False
        self.color_dict = color_dict

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "image_tab.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        return

    #----------------------------------------------#

    def buildTab(self, dataframe):

        # save the df
        self.dataframe = dataframe

        # create the dataframe for the table
        self.image_data = self.createImageData(self.dataframe)

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # update boolean
        self.tab_is_built = True

        return

    #----------------------------------------------#

    def createImageData(self, data):

        # instantiate data
        if not self.dataframe.empty:
            image_data = self.dataframe.to_numpy().T
        else:
            image_data = np.array([])

        return image_data

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

        # convenience widget composed of both GraphicsView and GraphicsLayout
        self.graphics_layout_widget = pg.GraphicsLayoutWidget(parent = self.frame_holder, title = "Image")
        self.graphics_layout_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self.graphics_layout_widget.setAspectLocked(True)
        self.graphics_layout_widget.setAntialiasing(True)
        self.graphics_layout_widget.setBackground(self.color_dict["color_background"])

        # scroll size handling
        self.graphics_layout_widget.setMinimumHeight(270)
        self.graphics_layout_widget.setMinimumWidth(480)

        # image item
        self.image_plot = self.graphics_layout_widget.addPlot(title="2D Matrix", row=0, col=0)
        self.image_plot.disableAutoRange()
        self.image_plot.setAutoVisible()
        self.image_plot.showButtons()
        self.image_plot.showGrid(x=False, y=False, alpha=0.3)

        # get the x and y axes of the plot
        x_axis = self.image_plot.getAxis('bottom')
        y_axis = self.image_plot.getAxis('left')

        # set the axis names
        x_axis.setLabel('columns')
        y_axis.setLabel('rows')

        # add the image item
        self.image_item = pg.ImageItem(self.image_data)

        # add the item to the plot view (remember we need a plot view inserted into a layout)
        self.image_plot.addItem(self.image_item)

        # invert y axis so that the image makes sense (wrt the table)
        self.image_plot.getViewBox().invertY(True)

        # manual auto range
        self.image_plot.autoRange()

        # histogram item
        self.hist_item = pg.HistogramLUTItem(self.image_item)
        self.graphics_layout_widget.addItem(self.hist_item, row=0, col=1)

        # add to the layout
        self.verticalLayout_stack.addWidget(self.graphics_layout_widget)

        # show the view
        self.graphics_layout_widget.show()

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