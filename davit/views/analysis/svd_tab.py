#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.views.visualization.plot_tab import PlotTab
from bida_bpm.denoise import SvdAnalysis

#################################################################
#################################################################

class NonInteractiveLegendItem(pg.LegendItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def mouseClickEvent(self, ev):
        pass
    def mouseDoubleClickEvent(self, ev):
        pass
    def mousePressEvent(self, ev):
        pass
    def mouseReleaseEvent(self, ev):
        pass
    def mouseDragEvent(self, ev):
        pass

#################################################################
#################################################################

class OptionsDialog(QDialog):

    #----------------------------------------------#

    def __init__(self, max_shape=999, unit="mm", options_dialog_info=(0,0), parent=None, global_parent=None, max_n_modes_to_display=20):

        # init from parent
        super().__init__(parent)

        # own attributes
        self.max_shape = max_shape
        self.unit = unit
        self.global_parent = global_parent
        self.max_n_modes_to_display = max_n_modes_to_display
        self.options_dialog_info = options_dialog_info

        # set title and icon
        self.setWindowTitle("SVD Options Dialog")
        self.setWindowIcon(qta.icon("fa5s.play-circle"))

        # set the fixed sie
        self.setFixedSize(500, 220)

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):
        
        # main layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # group box for the options
        self.options_group = QGroupBox(parent=self)
        self.options_group.setTitle("Options")
        self.options_group.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(self.options_group)

        # grid layout with options
        self.grid_layout = QGridLayout(self.options_group)
        self.options_group.setLayout(self.grid_layout)

        # n_modes_method label with combobox
        self.label_n_modes_method = QLabel(text="n_modes_method ", parent=self.options_group)
        self.label_n_modes_method.setStyleSheet("font-weight: normal;")
        self.combobox_n_modes_method = QComboBox(self.options_group)
        self.combobox_n_modes_method.setStyleSheet("font-weight: normal;")
        self.combobox_n_modes_method.addItems(["auto-derivatives-method (recommended)", "auto-variance-percentage-method", "fixed"])
        self.combobox_n_modes_method.setCurrentIndex(self.options_dialog_info[0])
        self.grid_layout.addWidget(self.label_n_modes_method, 0, 0)
        self.grid_layout.addWidget(self.combobox_n_modes_method, 0, 1)

        # n_modes_fixed label with spinbox
        self.label_n_modes_fixed = QLabel(text="n_modes ", parent=self.options_group)
        self.label_n_modes_fixed.setStyleSheet("font-weight: normal;")
        self.spinbox_n_modes_fixed = QSpinBox(self.options_group)
        self.spinbox_n_modes_fixed.setStyleSheet("font-weight: normal;")
        self.spinbox_n_modes_fixed.setMinimum(1)
        self.spinbox_n_modes_fixed.setMaximum(self.max_shape)
        self.spinbox_n_modes_fixed.setValue(self.options_dialog_info[1])
        self.grid_layout.addWidget(self.label_n_modes_fixed, 1, 0)
        self.grid_layout.addWidget(self.spinbox_n_modes_fixed, 1, 1)

        # enable or disable the n_modes widgets
        self.toggle_n_modes_fixed(text=self.combobox_n_modes_method.currentText())

        # max_n_modes_to_display label with spinbox
        self.label_max_n_modes_to_display = QLabel(text="max_n_modes_to_display ", parent=self.options_group)
        self.label_max_n_modes_to_display.setStyleSheet("font-weight: normal;")
        self.spinbox_max_n_modes_to_display = QSpinBox(self.options_group)
        self.spinbox_max_n_modes_to_display.setStyleSheet("font-weight: normal;")
        self.spinbox_max_n_modes_to_display.setMinimum(1)
        self.spinbox_max_n_modes_to_display.setMaximum(self.max_shape)
        self.spinbox_max_n_modes_to_display.setValue(self.max_n_modes_to_display)
        self.grid_layout.addWidget(self.label_max_n_modes_to_display, 2, 0)
        self.grid_layout.addWidget(self.spinbox_max_n_modes_to_display, 2, 1)

        # unit label with line edit
        self.label_unit = QLabel(text="unit ", parent=self.options_group)
        self.label_unit.setStyleSheet("font-weight: normal;")
        self.lineedit_unit = QLineEdit(text=self.unit, parent=self.options_group)
        self.lineedit_unit.setStyleSheet("font-weight: normal;")
        self.lineedit_unit.setMaxLength(20)
        self.grid_layout.addWidget(self.label_unit, 3, 0)
        self.grid_layout.addWidget(self.lineedit_unit, 3, 1)

        # vertical spacer between yes and no layout and options
        self.v_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addSpacerItem(self.v_spacer)

        # confirmation panel
        self.confirmation_frame = QFrame(self)
        self.confirmation_layout = QHBoxLayout(self.confirmation_frame)
        self.confirmation_layout.setContentsMargins(0, 0, 0, 0)
        self.confirmation_frame.setLayout(self.confirmation_layout)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.label_question = QLabel(text="Do you want to run the analysis? ", parent=self.confirmation_frame)
        self.btn_yes = QPushButton(text="Yes", parent=self.confirmation_frame)
        self.btn_no = QPushButton(text="No", parent=self.confirmation_frame)
        self.confirmation_layout.addSpacerItem(spacer)
        self.confirmation_layout.addWidget(self.label_question)
        self.confirmation_layout.addWidget(self.btn_no)
        self.confirmation_layout.addWidget(self.btn_yes)
        self.main_layout.addWidget(self.confirmation_frame)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # connect accept and reject buttons
        self.btn_yes.clicked.connect(self.accept)
        self.btn_no.clicked.connect(self.reject)

        # bindings for the comboboxes
        self.combobox_n_modes_method.currentTextChanged.connect(self.toggle_n_modes_fixed)

        return

    #----------------------------------------------#

    def toggle_n_modes_fixed(self, text):

        # enable or disable based on combobox value
        if text == "fixed":
            self.label_n_modes_fixed.setEnabled(True)
            self.spinbox_n_modes_fixed.setEnabled(True)
        else:
            self.label_n_modes_fixed.setEnabled(False)
            self.spinbox_n_modes_fixed.setEnabled(False)

        return

    #----------------------------------------------#

    def accept(self):

        # 1st check
        if int(self.spinbox_n_modes_fixed.value()) > int(self.spinbox_max_n_modes_to_display.value()):
            message_title = "Warning"
            message_text = ("n_modes cannot be larger than max_n_modes_to_display!")
            message_box = QMessageBox(QMessageBox.Icon.Warning, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.play-circle"))
            message_box.exec()
            return

        # retrieve options
        method = self.combobox_n_modes_method.currentText().replace(" ", "").replace("(recommended)", "")
        if method == "fixed":
            n_modes = int(self.spinbox_n_modes_fixed.value())
        else:
            n_modes = method
        max_n_modes_to_display = int(self.spinbox_max_n_modes_to_display.value())
        unit = self.lineedit_unit.text()

        # run analysis
        if self.global_parent:
            self.global_parent.runAnalysisAfterDialog(n_modes, max_n_modes_to_display, unit, (self.combobox_n_modes_method.currentIndex(), int(self.spinbox_n_modes_fixed.value())))

        # accept if there are no errors
        super().accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################

class SingularValuesHistogram(QWidget):

    #----------------------------------------------#

    def __init__(self, parent=None, global_parent=None, max_singular_values_to_show = 20):

        # init the widget
        super().__init__(parent)

        # own attributes
        self.global_parent = global_parent
        self.max_singular_values_to_show = max_singular_values_to_show

        # init colors
        self.on_color = "#12C453"
        self.on_color_pen = "#008330"
        self.off_color = "#D1D1D1"
        self.off_color_pen = "#7E7E7E"

        # init variables
        self.legend = None
        self.bars = []
        self.values = []
        self.states = []

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # set holder layout
        self.holder_layout = QVBoxLayout(self)
        self.holder_layout.setContentsMargins(0, 0, 0, 0)
        self.holder_layout.setSpacing(0)
        self.setLayout(self.holder_layout)

        # frame for plots
        self.frame_plots = QFrame(parent=self)
        self.frame_plots.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_plots.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_plots.setObjectName("frame_plots")

        # layout of the frame for the plots
        self.verticalLayout_frame_plots = QVBoxLayout(self.frame_plots)
        self.verticalLayout_frame_plots.setObjectName("verticalLayout_frame_plots")
        self.verticalLayout_frame_plots.setContentsMargins(15, 15, 15, 15)
        self.holder_layout.addWidget(self.frame_plots)

        # initialize the graphics view and layout
        self.view = pg.GraphicsView(self.frame_plots)
        self.layout = pg.GraphicsLayout()
        self.view.setCentralItem(self.layout)

        # create a plot item within the layout for bar graph
        self.plot_item = self.layout.addPlot()

        # set the title and axis labels
        self.plot_item.setTitle("First {} Singular Values (Modes)".format(self.max_singular_values_to_show))
        self.plot_item.setLabel('left', "Singular Value")
        self.plot_item.setLabel('bottom', "Index")

        # add the plot
        self.verticalLayout_frame_plots.addWidget(self.view)

        # frame for the info
        self.frame_bottom = QFrame(self)
        self.frame_bottom.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_bottom.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_bottom.setObjectName("frame_bottom")

        # layout of the frame for the info
        self.horizontalLayout_frame_bottom = QHBoxLayout(self.frame_bottom)
        self.horizontalLayout_frame_bottom.setObjectName("horizontalLayout_frame_bottom")
        self.horizontalLayout_frame_bottom.setContentsMargins(15, 0, 15, 15)
        self.horizontalLayout_frame_bottom.setSpacing(8)

        # informative label
        self.label_n_modes = QLabel(text="Number of selected modes: {}".format(0), parent=self.frame_bottom)
        self.label_n_modes.setObjectName("label_n_modes")
        self.horizontalLayout_frame_bottom.addWidget(self.label_n_modes)

        # invisible button to keep relative height
        self.invisible_button = QPushButton(text="empty", parent=self.frame_bottom)
        self.horizontalLayout_frame_bottom.addWidget(self.invisible_button)

        # make button invisible
        sp_retain = self.invisible_button.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.invisible_button.setSizePolicy(sp_retain)
        self.invisible_button.hide()

        # spacer to move everything to the left
        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_bottom.addItem(self.spacerItem)

        # add the frame
        self.holder_layout.addWidget(self.frame_bottom)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # connect click event
        self.view.scene().sigMouseClicked.connect(self.onClick)

        return

    #----------------------------------------------#

    def initLegend(self):

        # create the legend with the anchor at the top-right
        self.legend = NonInteractiveLegendItem(offset=(0, 30), anchor=('right', 'top'))
        self.legend.setParentItem(self.plot_item)

        # create sample items for the legend
        self.on_sample = pg.BarGraphItem(x=[0], height=[0], width=0.8, brush=self.on_color)
        self.off_sample = pg.BarGraphItem(x=[0], height=[0], width=0.8, brush=self.off_color)

        # add items to the legend
        self.legend.addItem(self.on_sample, 'Non-subtracted modes')
        self.legend.addItem(self.off_sample, 'Subtracted modes')

        return

    #----------------------------------------------#

    def createBars(self, values):

        # create individual bars and store them
        self.bars = []
        for idx, value in enumerate(values):
            color = self.on_color if self.states[idx] == 'ON' else self.off_color
            bar = pg.BarGraphItem(x=[idx], height=[value], width=0.8, brush=color)
            self.bars.append(bar)
            self.plot_item.addItem(bar)

        return

    #----------------------------------------------#

    def updatePlot(self, values, n_optimal_modes):

        # clear all bars
        for bar in self.bars:
            self.plot_item.removeItem(bar)

        # clear the legend (just in case)
        if self.legend:
            self.legend.clear()

        # update max number of singular values
        if n_optimal_modes >= self.max_singular_values_to_show:
            self.max_singular_values_to_show = n_optimal_modes

        # update title
        self.plot_item.setTitle("First {} Singular Values (Modes)".format(self.max_singular_values_to_show))

        # update data
        self.values = values[:self.max_singular_values_to_show]
        self.states = ['ON' if i < n_optimal_modes else 'OFF' for i in range(len(self.values))]

        # create bars
        self.createBars(self.values)

        # init the legend after the plot is updated
        self.initLegend()

        # manual auto range
        self.plot_item.autoRange()

        # update label
        self.label_n_modes.setText("Number of selected modes: {}".format(n_optimal_modes))

        return

    #----------------------------------------------#

    def onClick(self, event):
        mousePoint = self.plot_item.vb.mapSceneToView(event.scenePos())
        x_val = int(round(mousePoint.x()))
        if 0 <= x_val < len(self.values):
            self.toggle_state(x_val)

    #----------------------------------------------#

    def toggle_state(self, idx):

        # check states
        if self.states[idx] == 'ON':
            self.states[idx] = 'OFF'
            self.bars[idx].setOpts(brush=self.off_color)
        else:
            self.states[idx] = 'ON'
            self.bars[idx].setOpts(brush=self.on_color)

        # get mode indices
        mode_indices = [i for i, state in enumerate(self.states) if state == 'ON']

        # recompute everything
        if self.global_parent:
            self.global_parent.modeFiltering(mode_indices)
            self.global_parent.updatePlots()

        # update label
        self.label_n_modes.setText("Number of selected modes: {}".format(len(mode_indices)))

        return

    #----------------------------------------------#

#################################################################
#################################################################

class ResidualsHistogram(QWidget):

    #----------------------------------------------#

    def __init__(self, parent=None, unit = "mm", bins=100):

        # init the widget
        super().__init__(parent)

        # own attributes
        self.unit = unit
        self.bins = bins

        # init variables
        self.residuals = []
        self.bar_graph = None

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # initialize the graphics view and layout
        self.view = pg.GraphicsView(self)
        self.layout = pg.GraphicsLayout()
        self.view.setCentralItem(self.layout)

        # create a plot item within the layout for bar graph
        self.plot_item = self.layout.addPlot()

        # set the title and axis labels
        self.plot_item.setTitle("Histogram of Residuals (Subtracted)")
        self.plot_item.setLabel('left', "Count")
        self.plot_item.setLabel('bottom', "Residual Value ({})".format(self.unit))

        # set layout and add graphics view
        self.holder_layout = QVBoxLayout(self)
        self.holder_layout.setContentsMargins(15, 8, 8, 8)
        self.holder_layout.setSpacing(0)
        self.holder_layout.addWidget(self.view)
        self.setLayout(self.holder_layout)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def updatePlot(self, residuals):

        # clear previous stuff
        if self.bar_graph:
            self.plot_item.removeItem(self.bar_graph)

        # update residuals
        self.residuals = residuals

        # update axis label
        self.plot_item.setLabel('bottom', "Residual Value ({})".format(self.unit))

        # update only if array is not empty
        if self.residuals.any():

            # get histogram data
            hist_vals, hist_bins = np.histogram(self.residuals.flatten(), bins=self.bins)

            # create new bar graph
            self.bar_graph = pg.BarGraphItem(x=hist_bins[:-1], height=hist_vals, width=hist_bins[1]-hist_bins[0], brush='#4DB6FF', pen='#0097FF')

            # add the bar graph to the plot
            self.plot_item.addItem(self.bar_graph)

            # manual auto range
            self.plot_item.autoRange()

        return

    #----------------------------------------------#

#################################################################
#################################################################

class ResidualsHeatmap(QWidget):

    #----------------------------------------------#

    def __init__(self, parent=None, unit = "mm"):

        # init the widget
        super().__init__(parent)

        # own attributes
        self.unit = unit

        # init variables
        self.residuals = []
        self.image_item = None
        self.hist_item = None

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # initialize the graphics view and layout
        self.view = pg.GraphicsView(self)
        self.layout = pg.GraphicsLayout()
        self.view.setCentralItem(self.layout)

        # image item
        self.plot_item = self.layout.addPlot(title="Heatmap of Residuals (Subtracted)", row=0, col=0)
        self.plot_item.disableAutoRange()
        self.plot_item.setAutoVisible()
        self.plot_item.showButtons()
        self.plot_item.showGrid(x=False, y=False, alpha=0.3)

        # get the x and y axes of the plot
        x_axis = self.plot_item.getAxis('bottom')
        y_axis = self.plot_item.getAxis('left')

        # set the axis names
        x_axis.setLabel('X')
        y_axis.setLabel('Y')

        # show the view
        self.layout.show()

        # set layout and add graphics view
        self.holder_layout = QVBoxLayout(self)
        self.holder_layout.setContentsMargins(8, 8, 15, 8)
        self.holder_layout.setSpacing(0)
        self.holder_layout.addWidget(self.view)
        self.setLayout(self.holder_layout)
        
        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def updatePlot(self, residuals):

        # clear previous stuff
        if self.image_item:
            try:
                self.plot_item.removeItem(self.image_item)
            except:
                pass
        if self.hist_item:
            try:
                self.layout.removeItem(self.hist_item)
            except:
                pass

        # update residuals
        self.residuals = residuals

        # update only if array is not empty
        if self.residuals.any():

            # add the image item
            self.image_item = pg.ImageItem(self.residuals.T)

            # add the item to the plot view (remember we need a plot view inserted into a layout)
            self.plot_item.addItem(self.image_item)

            # manual auto range
            self.plot_item.autoRange()

            # histogram item
            self.hist_item = pg.HistogramLUTItem(self.image_item)
            self.layout.addItem(self.hist_item, row=0, col=1)

        return

    #----------------------------------------------#

#################################################################
#################################################################

class SvdTab(QWidget):

    #----------------------------------------------#

    def __init__(self, app, dataframe, attributes, init_build, app_root_path = None, window_icon_path = None, parent = None, global_parent = None, color_dict = {}, mouse_mode_1_button = False, pyqtgraph_default_downsample = False, sticky_options = True, display_strings_on_x_axis = False, ncurves_at_init = 10, min_big_data_sample_size = 1_000_000, chunk_size = 100_000, big_data_mode = False, qta_str_icon = "", auto_multiple_axes = False, display_name = ""):

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
        self.mouse_mode_1_button = mouse_mode_1_button
        self.pyqtgraph_default_downsample = pyqtgraph_default_downsample
        self.sticky_options = sticky_options
        self.display_strings_on_x_axis = display_strings_on_x_axis
        self.ncurves_at_init = ncurves_at_init
        self.min_big_data_sample_size = min_big_data_sample_size
        self.chunk_size = chunk_size
        self.big_data_mode = big_data_mode
        self.qta_str_icon = qta_str_icon
        self.auto_multiple_axes = auto_multiple_axes
        self.display_name = display_name

        # own attributes
        self.tab_is_built = False

        # analysis variables
        self.svd_analysis = None
        self.unit = "mm"
        self.max_n_modes_to_display = 20
        self.options_dialog_info = (0,0)
        self.singular_values = None
        self.n_optimal_modes = None
        self.mode_indices = None
        self.matrix_denoised = np.array([])
        self.residuals = np.array([])
        self.resolution = 0.0
        self.offset = 0.0
        self.snr = 0.0

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "svd_tab.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        return

    #----------------------------------------------#

    def buildTab(self, dataframe):

        # save the df
        self.dataframe = dataframe

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # update boolean
        self.tab_is_built = True

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
        self.verticalLayout_stack.setContentsMargins(15, 15, 15, 8)
        self.verticalLayout_stack.setSpacing(0)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # frame N1 for the opts and running analysis
        self.frame_opts = QFrame(self.frame_holder)
        self.frame_opts.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_opts.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_opts.setObjectName("frame_opts")

        # layout N1 for frame_opts
        self.horizontalLayout_frame_opts = QHBoxLayout(self.frame_opts)
        self.horizontalLayout_frame_opts.setContentsMargins(0, 0, 15, 0)
        self.horizontalLayout_frame_opts.setSpacing(14)
        self.horizontalLayout_frame_opts.setObjectName("horizontalLayout_frame_opts")
        self.verticalLayout_stack.addWidget(self.frame_opts)

        # button for running the svd
        self.button_run_svd = QPushButton(" Run SVD Analysis", self.frame_opts)
        self.button_run_svd.setObjectName("button_run_svd")
        self.button_run_svd.setIcon(QIcon(qta.icon("fa5s.play-circle")))
        self.horizontalLayout_frame_opts.setAlignment(self.button_run_svd, Qt.AlignmentFlag.AlignCenter)
        
        # button for saving the results
        self.button_save_results = QPushButton(" Save Results", self.frame_opts)
        self.button_save_results.setObjectName("button_save_results")
        self.button_save_results.setIcon(QIcon(qta.icon("fa5.save")))
        self.horizontalLayout_frame_opts.setAlignment(self.button_save_results, Qt.AlignmentFlag.AlignCenter)

        # add buttons to the layout
        self.spacer_opts_labels_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_opts.addItem(self.spacer_opts_labels_1)
        self.horizontalLayout_frame_opts.addWidget(self.button_run_svd)
        self.horizontalLayout_frame_opts.addWidget(self.button_save_results)
        self.spacer_opts_labels_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_opts.addItem(self.spacer_opts_labels_2)

        # info button (new addition)
        self.button_svd_info = QPushButton("", self.frame_opts)
        self.button_svd_info.setObjectName("button_svd_info")
        self.button_svd_info.setIcon(QIcon(qta.icon("fa.info-circle")))
        self.horizontalLayout_frame_opts.addWidget(self.button_svd_info)

        # frame N2 for the singular values and visualization
        self.frame_singular_values = QFrame(self.frame_holder)
        self.frame_singular_values.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_singular_values.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_singular_values.setObjectName("frame_singular_values")

        # layout N2 for frame_opts
        self.horizontalLayout_frame_singular_values = QHBoxLayout(self.frame_singular_values)
        self.horizontalLayout_frame_singular_values.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_singular_values.setSpacing(0)
        self.horizontalLayout_frame_singular_values.setObjectName("horizontalLayout_frame_singular_values")
        self.verticalLayout_stack.addWidget(self.frame_singular_values)

        # create the plots
        self.plot_singular_values = SingularValuesHistogram(parent=self.frame_singular_values, global_parent=self, max_singular_values_to_show=self.max_n_modes_to_display)
        self.plot_visualization = PlotTab(self.app, self.dataframe, self.attributes, True, app_root_path = self.app_root_path, window_icon_path = self.window_icon_path, parent = self.frame_singular_values, global_parent = self.global_parent, color_dict = self.color_dict, mouse_mode_1_button = self.mouse_mode_1_button, pyqtgraph_default_downsample = self.pyqtgraph_default_downsample, sticky_options = self.sticky_options, display_strings_on_x_axis = self.display_strings_on_x_axis, ncurves_at_init = self.ncurves_at_init, min_big_data_sample_size = self.min_big_data_sample_size, chunk_size = self.chunk_size, big_data_mode = self.big_data_mode, qta_str_icon=self.qta_str_icon, auto_multiple_axes=self.auto_multiple_axes, build_scroll_area = False, plot_at_init = False)
        self.horizontalLayout_frame_singular_values.addWidget(self.plot_singular_values)
        self.horizontalLayout_frame_singular_values.addWidget(self.plot_visualization)

        # adjust stretchs
        self.horizontalLayout_frame_singular_values.setStretchFactor(self.plot_singular_values, 50)
        self.horizontalLayout_frame_singular_values.setStretchFactor(self.plot_visualization, 50)

        # frame N3 for the residuals
        self.frame_residuals = QFrame(self.frame_holder)
        self.frame_residuals.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_residuals.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_residuals.setObjectName("frame_residuals")

        # layout N3 for frame_opts
        self.horizontalLayout_frame_residuals = QHBoxLayout(self.frame_residuals)
        self.horizontalLayout_frame_residuals.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_residuals.setSpacing(0)
        self.horizontalLayout_frame_residuals.setObjectName("horizontalLayout_frame_residuals")
        self.verticalLayout_stack.addWidget(self.frame_residuals)

        # create the plots
        self.plot_hist_residuals = ResidualsHistogram(parent=self.frame_residuals, unit=self.unit)
        self.plot_heatmap_residuals = ResidualsHeatmap(parent=self.frame_residuals, unit=self.unit)
        self.horizontalLayout_frame_residuals.addWidget(self.plot_hist_residuals)
        self.horizontalLayout_frame_residuals.addWidget(self.plot_heatmap_residuals)

        # adjust stretchs
        self.horizontalLayout_frame_residuals.setStretchFactor(self.plot_hist_residuals, 50)
        self.horizontalLayout_frame_residuals.setStretchFactor(self.plot_heatmap_residuals, 50)

        # frame N4 for the info
        self.frame_info = QFrame(self.frame_holder)
        self.frame_info.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_info.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_info.setObjectName("frame_info")

        # layout N4 for frame_opts
        self.horizontalLayout_frame_info = QHBoxLayout(self.frame_info)
        self.horizontalLayout_frame_info.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_info.setSpacing(22)
        self.horizontalLayout_frame_info.setObjectName("horizontalLayout_frame_info")
        self.verticalLayout_stack.addWidget(self.frame_info)

        # create the labels
        self.label_resolution = QLabel("Resolution = {:.6f} {}".format(self.resolution, self.unit), self.frame_info)
        self.label_resolution.setToolTip("Resolution = {} {}".format(self.resolution, self.unit))
        self.label_resolution.setObjectName("label_resolution")
        self.label_orbit_offset = QLabel("Offset = {:.6f} {}".format(self.offset, self.unit), self.frame_info)
        self.label_orbit_offset.setToolTip("Offset = {} {}".format(self.offset, self.unit))
        self.label_orbit_offset.setObjectName("label_orbit_offset")
        self.label_SNR = QLabel("SNR = {:.6f} {}".format(self.snr, "dB"), self.frame_info)
        self.label_SNR.setToolTip("SNR = {} dB".format(self.snr))
        self.label_SNR.setObjectName("label_SNR")

        # add labels to the layout (with spacers)
        self.spacer_info_labels_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_info.addItem(self.spacer_info_labels_1)
        self.horizontalLayout_frame_info.addWidget(self.label_resolution)
        self.horizontalLayout_frame_info.addWidget(self.label_orbit_offset)
        self.horizontalLayout_frame_info.addWidget(self.label_SNR)
        self.spacer_info_labels_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_info.addItem(self.spacer_info_labels_2)

        # set stretch factors
        self.verticalLayout_stack.setStretchFactor(self.frame_opts, 1)
        self.verticalLayout_stack.setStretchFactor(self.frame_singular_values, 99)
        self.verticalLayout_stack.setStretchFactor(self.frame_residuals, 99)
        self.verticalLayout_stack.setStretchFactor(self.frame_info, 1)

        # change some layout stuff
        self.plot_singular_values.verticalLayout_frame_plots.setContentsMargins(15, 15, 8, 8)
        self.plot_singular_values.horizontalLayout_frame_bottom.setContentsMargins(15, 0, 8, 8)
        self.plot_visualization.verticalLayout_frame_plots.setContentsMargins(8, 15, 15, 8)
        self.plot_visualization.horizontalLayout_frame_bottom_of_the_plot.setContentsMargins(8, 0, 15, 8)

        # disable visualizer opts at init
        self.plot_visualization.frame_bottom_of_the_plot.setEnabled(False)

        # change plot visualization title
        self.plot_visualization.plot_item.setTitle(title="Reconstructed Data (Denoised)")

        # set minimum widths
        QTimer.singleShot(0, self.updateWidthsAndHeights)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # binding for running the analysis
        self.button_run_svd.clicked.connect(self.runAnalysis)

        # binding for saving the analysis
        self.button_save_results.clicked.connect(lambda: self.saveAnalysis())

        # bind info button
        self.button_svd_info.clicked.connect(self.showSvdInfo)

        return

    #----------------------------------------------#

    def showSvdInfo(self):
        info_text = (
            "<h2>SVD Analysis Information</h2>"
            "<p>This analysis uses Singular Value Decomposition (SVD) to decompose the data into its principal components or modes. "
            "The analysis provides several plots to help you interpret both the decomposition and its quality. </p>"
            "<h3>Plot Features</h3>"
            "<ul>"
            "<li><b>Top Left (Singular Values Histogram):</b> This plot displays the magnitude of the singular values (modes) in descending order. "
            "It shows which modes capture the most variance in the dataset. You can interact with the bars to toggle individual modes on or off for the reconstruction.</li>"
            "<li><b>Top Right (Data Reconstruction Visualization):</b> This panel shows the reconstructed (denoised) version of your data based on the selected modes. "
            "It provides a visual comparison with the original data, highlighting the effect of mode filtering on data fidelity.</li>"
            "<li><b>Bottom Left (Residuals Histogram):</b> This histogram visualizes the distribution of residuals, which are the differences between the original "
            "data and the reconstructed data. It gives you an overview of the reconstruction error and helps in assessing the overall performance of the SVD filtering.</li>"
            "<li><b>Bottom Right (Residuals Heatmap):</b> The heatmap provides a detailed spatial view of the residuals, allowing you to identify areas where the "
            "reconstruction deviates significantly from the original data. It is particularly useful for identifying localized regions of higher error.</li>"
            "</ul>"
        )
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("SVD Analysis Information")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(info_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStyleSheet("QLabel { min-width: 800px; }")
        msg_box.exec()

    #----------------------------------------------#

    def updateWidthsAndHeights(self, minimum_frame_height = 240):

        # get minimum width
        minimum_frame_width = self.plot_visualization.frame_bottom_of_the_plot.width()

        # set minimum widths
        self.plot_hist_residuals.setMinimumWidth(minimum_frame_width)
        self.plot_heatmap_residuals.setMinimumWidth(minimum_frame_width)
        self.plot_singular_values.setMinimumWidth(minimum_frame_width)
        self.plot_visualization.setMinimumWidth(minimum_frame_width)

        # set minimum heights
        self.plot_hist_residuals.setMinimumHeight(minimum_frame_height)
        self.plot_heatmap_residuals.setMinimumHeight(minimum_frame_height)
        self.plot_singular_values.setMinimumHeight(minimum_frame_height)
        self.plot_visualization.setMinimumHeight(minimum_frame_height)

        return

    #----------------------------------------------#

    def runAnalysis(self):

        # open the dialog
        self.options_dialog = OptionsDialog(max_shape=self.dataframe.shape[1], unit=self.unit, options_dialog_info=self.options_dialog_info, parent=self, global_parent=self, max_n_modes_to_display=self.max_n_modes_to_display)
        self.options_dialog.exec()

        return

    #----------------------------------------------#

    def runAnalysisAfterDialog(self, n_modes, max_n_modes_to_display, unit, options_dialog_info):

        # init svd object
        self.svd_analysis = SvdAnalysis(self.dataframe.to_numpy())

        # save some of the info
        self.options_dialog_info = options_dialog_info

        # update unit
        self.unit = unit
        self.svd_analysis.unit = unit
        self.plot_hist_residuals.unit = unit
        self.plot_heatmap_residuals.unit = unit

        # update max number of modes to display
        self.max_n_modes_to_display = max_n_modes_to_display
        self.plot_singular_values.max_singular_values_to_show = max_n_modes_to_display

        # run analysis
        try:
            self.matrix_denoised, self.residuals, self.resolution, self.offset, self.snr = self.svd_analysis.run_svd(n_modes=n_modes, verbose=False, visualize=False)
        except Exception as xcp:
            message_title = "Error"
            message_text = ("Unable to run analysis due to the following exception: {}".format(xcp))
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.play-circle"))
            message_box.exec()
            return

        # retrieve singular values and number of modes
        self.singular_values = self.svd_analysis.S
        self.n_optimal_modes = self.svd_analysis.n_optimal_modes
        self.mode_indices = list(range(self.n_optimal_modes))

        # update the plot for singular values
        self.plot_singular_values.updatePlot(self.singular_values, self.n_optimal_modes)

        # if at least 1 mode
        if self.n_optimal_modes >= 1:
            
            # update the rest of the plots
            self.updatePlots(first_time=True)
        
        return

    #----------------------------------------------#

    def modeFiltering(self, mode_indices):

        # save indices
        self.mode_indices = mode_indices

        # recompute stuff based on the mode indices
        self.matrix_denoised, self.residuals, self.resolution, self.offset, self.snr = self.svd_analysis.compute_denoised_matrix_and_metrics(mode_indices=self.mode_indices)

        return

    #----------------------------------------------#

    def updatePlots(self, first_time=False):

        # update dataframe on the visualizer
        if self.matrix_denoised.any():
            self.plot_visualization.dataframe = pd.DataFrame(self.matrix_denoised, index=self.dataframe.index, columns=self.dataframe.columns)
        else:
            self.plot_visualization.dataframe = self.dataframe * 0

        # update the visualizer
        if first_time:
            self.plot_visualization.plotAtInit()
        else:
            if self.plot_visualization.saved_selected_indexes and self.plot_visualization.saved_names:
                self.plot_visualization.plotData(self.plot_visualization.saved_selected_indexes, self.plot_visualization.saved_names, self.plot_visualization.saved_axis_list, first_time=False)
            else:
                self.plot_visualization.plotAtInit()

        # enable visualizer opts
        if self.mode_indices:
            self.plot_visualization.frame_bottom_of_the_plot.setEnabled(True)
        else:
            self.plot_visualization.frame_bottom_of_the_plot.setEnabled(False)

        # update the residuals histogram
        self.plot_hist_residuals.updatePlot(self.residuals)

        # update the residuals heatmap
        self.plot_heatmap_residuals.updatePlot(self.residuals)

        # update info labels
        self.label_resolution.setText("Resolution = {:.6f} {}".format(self.resolution, self.unit))
        self.label_resolution.setToolTip("Resolution = {} {}".format(self.resolution, self.unit))
        self.label_orbit_offset.setText("Offset = {:.6f} {}".format(self.offset, self.unit))
        self.label_orbit_offset.setToolTip("Offset = {} {}".format(self.offset, self.unit))
        self.label_SNR.setText("SNR = {:.6f} {}".format(self.snr, "dB"))
        self.label_SNR.setToolTip("SNR = {} dB".format(self.snr))
        
        return

    #----------------------------------------------#

    def saveAnalysis(self, qta_icon="fa5.save", verbose=True):

        # we need an analysis first
        if not self.svd_analysis:
            message_title = "Error"
            message_text = ("No analysis found!")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec()
            return

        # typical try except workflow
        try:

            # default save name?
            save_name = ""
            if self.display_name:
                save_name = self.display_name + "_svd_analysis_results.hdf5"

            # get name
            name, _ = QFileDialog.getSaveFileName(self, "Save analysis in HDF5 file", save_name, filter="HDF5(*.hdf5)")

            # return and exit if user did not introduce any name
            if not name:
                return

            # add .hdf5 in case user did not add it
            if name[-5:].lower() != ".hdf5":
                name = name + ".hdf5"

            # for debugging
            if verbose:
                print("Saving to HDF5...")

            # save to hdf5
            self.svd_analysis.save_analysis_to_hdf5(filename = name)

            # show success message
            message_title = "Success"
            message_text = ("The analysis has been successfully saved to the following path: {}".format(name))
            message_box = QMessageBox(QMessageBox.Icon.Information, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon(qta_icon))
            message_box.exec()

        # throw some error
        except Exception as xcp:

            # show error message
            message_title = "Error"
            message_text = ("Unable to save the analysis due to: {}".format(xcp))
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon(qta_icon))
            message_box.exec()

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################
