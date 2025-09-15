#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.utils.combo_delegate import ComboDelegate

#################################################################
#################################################################

class ScatterTab(QWidget):

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
        self.color_dict = color_dict

        # own attributes
        self.tab_is_built = False

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "scatter_tab.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        return

    #----------------------------------------------#

    def buildTab(self, dataframe):

        # save the df
        self.dataframe = dataframe

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # plot data at init
        self.plotData()

        # update boolean
        self.tab_is_built = True

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
        self.verticalLayout_stack.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_stack.setSpacing(0)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # create frame for the plots
        self.frame_plots = QFrame(self.frame_holder)
        self.frame_plots.setFrameShape(QFrame.NoFrame)
        self.frame_plots.setFrameShadow(QFrame.Plain)
        self.frame_plots.setObjectName("frame_plots")

        # scroll size handling
        self.frame_plots.setMinimumHeight(270)
        self.frame_plots.setMinimumWidth(480)

        # layout of the frame for the plots
        self.verticalLayout_frame_plots = QVBoxLayout(self.frame_plots)
        self.verticalLayout_frame_plots.setObjectName("verticalLayout_frame_plots")
        self.verticalLayout_frame_plots.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout_stack.addWidget(self.frame_plots)

        # convenience widget composed of both GraphicsView and GraphicsLayout
        self.graphics_layout_widget = pg.GraphicsLayoutWidget(parent = self.frame_holder, title = "2D Scatter")
        self.graphics_layout_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self.graphics_layout_widget.setAspectLocked(True)
        self.graphics_layout_widget.setAntialiasing(True)
        self.graphics_layout_widget.setBackground(self.color_dict["color_background"])

        # plot item
        self.plot_item = self.graphics_layout_widget.addPlot(title="2D Scatter", row=0, col=0)
        self.plot_item.disableAutoRange()
        self.plot_item.setAutoVisible()
        self.plot_item.showButtons()
        self.plot_item.showGrid(x=False, y=False, alpha=0.3)

        # add the scatter item
        self.scatter_item = pg.ScatterPlotItem(size=10, symbol="o", pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255, 180))

        # add the item to the plot view (remember we need a plot view inserted into a layout)
        self.plot_item.addItem(self.scatter_item)

        # manual auto range
        self.plot_item.autoRange()

        # add to the layout
        self.verticalLayout_frame_plots.addWidget(self.graphics_layout_widget)

        # show the view
        self.graphics_layout_widget.show()

        # frame for the toolbar at the bottom of the plot
        self.frame_bottom_of_the_plot = QFrame(self.frame_holder)
        self.frame_bottom_of_the_plot.setFrameShape(QFrame.NoFrame)
        self.frame_bottom_of_the_plot.setFrameShadow(QFrame.Plain)
        self.frame_bottom_of_the_plot.setObjectName("frame_bottom_of_the_plot")

        # layout of the frame for the toolbar at the bottom of the plot
        self.horizontalLayout_frame_bottom_of_the_plot = QHBoxLayout(self.frame_bottom_of_the_plot)
        self.horizontalLayout_frame_bottom_of_the_plot.setObjectName("horizontalLayout_frame_bottom_of_the_plot")
        self.horizontalLayout_frame_bottom_of_the_plot.setContentsMargins(15, 0, 15, 15)
        self.horizontalLayout_frame_bottom_of_the_plot.setSpacing(8)
        self.verticalLayout_stack.addWidget(self.frame_bottom_of_the_plot)

        # label for the x axis selector
        self.label_x = QLabel(text="x-axis", parent=self.frame_bottom_of_the_plot)
        self.label_x.setObjectName("label_x")
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.label_x)

        # add a combobox for the y axis
        self.comboBox_x = QComboBox(self.frame_bottom_of_the_plot)
        self.comboBox_x.setObjectName("comboBox_x")    
        self.model_comboBox_x = self.comboBox_x.model()
        self.delegate_x = ComboDelegate(self.frame_bottom_of_the_plot)
        self.hash_x = {}
        for counter_row, row in enumerate(self.dataframe.columns.astype(str)):
            self.model_comboBox_x.appendRow(QStandardItem("var_{}".format(counter_row)))
            self.hash_x[counter_row] = "{}".format(row)
        self.delegate_x.setHash(self.hash_x)
        self.comboBox_x.setModel(self.model_comboBox_x)
        self.comboBox_x.setItemDelegate(self.delegate_x)
        self.comboBox_x.view().setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in self.dataframe.columns.astype(str)]))
        self.comboBox_x.setCurrentIndex(0)
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.comboBox_x)

        # label for the x axis selector
        self.label_y = QLabel(text="y-axis", parent=self.frame_bottom_of_the_plot)
        self.label_y.setObjectName("label_y")
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.label_y)
        
        # add a combobox for the y axis
        self.comboBox_y = QComboBox(self.frame_bottom_of_the_plot)
        self.comboBox_y.setObjectName("comboBox_y")    
        self.model_comboBox_y = self.comboBox_y.model()
        self.delegate_y = ComboDelegate(self.frame_bottom_of_the_plot)
        self.hash_y = {}
        for counter_row, row in enumerate(self.dataframe.columns.astype(str)):
            self.model_comboBox_y.appendRow(QStandardItem("var_{}".format(counter_row)))
            self.hash_y[counter_row] = "{}".format(row)
        self.delegate_y.setHash(self.hash_y)
        self.comboBox_y.setModel(self.model_comboBox_y)
        self.comboBox_y.setItemDelegate(self.delegate_y)
        self.comboBox_y.view().setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in self.dataframe.columns.astype(str)]))
        self.comboBox_y.setCurrentIndex(0)
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.comboBox_y)

        # separator 1
        self.separator_line_1 = QVSeparationLine()
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.separator_line_1)

        # informative label for zeros
        self.label_for_zeros = QLabel(text="All-zeros-nans: Ø", parent=self.frame_bottom_of_the_plot)
        self.label_for_zeros.setObjectName("label_for_zeros")
        tooltip = "<html><head/><body><p>Curves that are marked with a Ø° character represent all-zero or all-nans arrays.</p></body></html>"
        self.label_for_zeros.setToolTip(tooltip)
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.label_for_zeros)

        # disable all labels and combox at init (except the selector)
        self.enableBottomSelectionBar(False)

        # spacer to move everything to the left
        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_frame_bottom_of_the_plot.addItem(self.spacerItem)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # bindings for the comboboxes
        self.comboBox_x.currentIndexChanged.connect(lambda combobox_index, what_changed="x_axis": self.plotData(combobox_index, what_changed))
        self.comboBox_y.currentIndexChanged.connect(lambda combobox_index, what_changed="y_axis": self.plotData(combobox_index, what_changed))

        return

    #----------------------------------------------#

    def plotData(self, combobox_index = None, what_changed = None, verbose = True):

        # get column vectors
        idx_x = int(self.comboBox_x.currentText().split("_")[-1])
        data_x = self.dataframe.iloc[:, idx_x]
        idx_y = int(self.comboBox_y.currentText().split("_")[-1])
        data_y = self.dataframe.iloc[:,idx_y]

        # set the data
        self.scatter_item.setData(x=data_x, y=data_y)

        # set init axis labels
        x_label = str(self.dataframe.columns.to_numpy()[idx_x])
        y_label =  str(self.dataframe.columns.to_numpy()[idx_y])
        self.modifyAxisLabels(x_label = x_label, y_label = y_label)

        # for debugging
        if verbose:
            print("Displaying scatter plot for {} and {}!".format(x_label, y_label))

        # show the graph
        self.plot_item.show()

        # update viewbox limits
        self.plot_item.autoRange()
        self.plot_item.enableAutoRange()

        # enable all combos
        self.enableBottomSelectionBar(True)

        return

    #----------------------------------------------#

    def enableBottomSelectionBar(self, enable = True):

        # enable or disable all
        self.label_for_zeros.setEnabled(enable)

        return

    #----------------------------------------------#

    def modifyAxisLabels(self, x_label = "0", y_label = "0"):

        # modify axis labels
        self.plot_item.setLabel(axis='left', text="y = {}".format(y_label))
        self.plot_item.setLabel(axis='bottom', text="x = {}".format(x_label))

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################