#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.views.visualization.plot_data_selector import PlotDataSelector
from davit.utils.big_data_plot import BigDataPlot, PlotDataClass

#################################################################
#################################################################

class DateAxisItem(pg.AxisItem):

    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S') for value in values]

class StringAxisItem(pg.AxisItem):

    def __init__(self, labels, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.labels = labels

    def tickStrings(self, values, scale, spacing):
        tick_labels = []
        threshold = 0.01 * spacing
        for val in values:
            if abs(val - round(val)) < threshold:
                idx = int(round(val))
                if 0 <= idx < len(self.labels):
                    tick_labels.append(str(self.labels[idx]))
                else:
                    tick_labels.append("")
            else:
                tick_labels.append("")
        return tick_labels

#################################################################
#################################################################

class PlotTab(QWidget):

    #----------------------------------------------#

    def __init__(self, app, dataframe, attributes, init_build, app_root_path = None, window_icon_path = None, parent = None, global_parent = None, color_dict = {}, mouse_mode_1_button = False, pyqtgraph_default_downsample = False, sticky_options = True, display_strings_on_x_axis = False, ncurves_at_init = 10, min_big_data_sample_size = 1_000_000, chunk_size = 100_000, big_data_mode = False, qta_str_icon = "", auto_multiple_axes = False, build_scroll_area = True, plot_at_init = True):

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
        self.display_strings_on_x_axis = display_strings_on_x_axis
        self.ncurves_at_init = ncurves_at_init
        self.min_big_data_sample_size = min_big_data_sample_size
        self.chunk_size = chunk_size
        self.big_data_mode = big_data_mode
        self.qta_str_icon = qta_str_icon
        self.auto_multiple_axes = auto_multiple_axes
        self.build_scroll_area = build_scroll_area
        self.plot_at_init = plot_at_init

        # sticky opts
        self.persist_sticky = bool(sticky_options)

        # own attributes
        self.legend = None
        self.fft_mode = False
        self.remove_mean_mode = False
        self.log10_mode = False
        self.symlog_mode = False
        self.tab_is_built = False

        # for hover
        self.mouse_moved_connection = None
        self.data_bounds = []
        self.is_datetime = False
        self.mouseHoverFirstTime = False
        self.targetItem = None
        self.infiniteLine = None

        # saves for plot updates
        self.saved_selected_indexes = None
        self.saved_names = None
        self.saved_axis_list = None
        self.var_axis_dict = None

        # saving original plot params
        self.original_selected_indexes = None
        self.original_names = None
        self.original_axis_list = None

        # for axis stuff
        self.y_axis_viewboxes = collections.OrderedDict()
        self.y_axis_items = collections.OrderedDict()

        # init axis labels
        self.x_label = "x"
        self.y_label = "y"

        # init axis items
        self.y_axis_items = collections.OrderedDict()

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "plot_tab.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        return

    #----------------------------------------------#

    def buildTab(self, dataframe):

        # save the df
        self.dataframe = dataframe

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # generate color palette
        self.makeColorPaletteForLegendAndPlot(list(self.dataframe.columns))

        # plot data at init
        if self.plot_at_init:
            self.plotAtInit()

        # update boolean
        self.tab_is_built = True

        return

    #----------------------------------------------#

    def plotAtInit(self):

        # plot data at init
        if self.dataframe.shape[1] < self.ncurves_at_init:
            self.ncurves_at_init = self.dataframe.shape[1]
        selected_indexes = list(np.arange(0, self.ncurves_at_init))
        names = list(self.dataframe.columns.astype(str))[0:self.ncurves_at_init]
        axis_list = ["y1"] * len(selected_indexes)
        if self.auto_multiple_axes:
            axis_list = self.autoMultipleAxes(axis_list, names)

        # backup the original selections
        self.original_selected_indexes = selected_indexes.copy()
        self.original_names = names.copy()
        self.original_axis_list = axis_list.copy()

        # if sticky flag is set, use effective (filtered) selection
        if self.persist_sticky:
            effective_indexes, effective_names, effective_axis = self._get_effective_selection(selected_indexes, names, axis_list)
            if effective_indexes:
                self.plotData(effective_indexes, effective_names, effective_axis)
        else:
            self.plotData(selected_indexes, names, axis_list)

        # sticky zooming
        if self.isSaveZoomEnabled() and getattr(self.global_parent, "saved_zoom", None):
            z = self.global_parent.saved_zoom
            if z.get("df_shape") == self.dataframe.shape:
                for vb in self.y_axis_viewboxes.values():
                    vb.setXRange(*z["x"], padding=0)
                self.plot_item.setYRange(*z["y"], padding=0)

        return

    #----------------------------------------------#

    def autoMultipleAxes(self, axis_list, names):

        # modify the axes automatically
        if len(axis_list) > 9:
            message_title = "Error"
            message_text = ("Unable to automatically set axes if the number of plots is larger than 9. Current number of selected plots: {}".format(len(axis_list)))
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec()
        else:
            axis_list = [f"y{i}" for i in range(1, len(axis_list)+1)]
            if not self.var_axis_dict:
                self.var_axis_dict = collections.OrderedDict()
                for i, name in enumerate(names):
                    self.var_axis_dict[name] = axis_list[i]

        return axis_list

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # build scroll area
        if self.build_scroll_area:

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
            self.verticalLayout_stack.setContentsMargins(0, 0, 0, 0)
            self.verticalLayout_stack.setSpacing(0)
            self.verticalLayout_stack.setObjectName("verticalLayout_stack")

            # create frame for the plots
            self.frame_plots = QFrame(self.frame_holder)
            self.frame_plots.setFrameShape(QFrame.Shape.NoFrame)
            self.frame_plots.setFrameShadow(QFrame.Shadow.Plain)
            self.frame_plots.setObjectName("frame_plots")

            # scroll size handling
            self.frame_plots.setMinimumHeight(270)
            self.frame_plots.setMinimumWidth(480)

        # do not build scroll area
        else:

            # layout of the form
            self.verticalLayout_frame_holder = QVBoxLayout(self)
            self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
            self.verticalLayout_frame_holder.setContentsMargins(0, 0, 0, 0)

            # holder of the form
            self.frame_holder = QFrame(self)
            self.frame_holder.setFrameShape(QFrame.Shape.NoFrame)
            self.frame_holder.setFrameShadow(QFrame.Shadow.Raised)
            self.frame_holder.setObjectName("frame_holder")

            # add the frame directly to the layout
            self.verticalLayout_frame_holder.addWidget(self.frame_holder)

            # main layout
            self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
            self.verticalLayout_stack.setContentsMargins(0, 0, 0, 0)
            self.verticalLayout_stack.setSpacing(0)
            self.verticalLayout_stack.setObjectName("verticalLayout_stack")

            # create frame for the plots
            self.frame_plots = QFrame(self.frame_holder)
            self.frame_plots.setFrameShape(QFrame.Shape.NoFrame)
            self.frame_plots.setFrameShadow(QFrame.Shadow.Plain)
            self.frame_plots.setObjectName("frame_plots")

        # layout of the frame for the plots
        self.verticalLayout_frame_plots = QVBoxLayout(self.frame_plots)
        self.verticalLayout_frame_plots.setObjectName("verticalLayout_frame_plots")
        self.verticalLayout_frame_plots.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout_stack.addWidget(self.frame_plots)

        # the plot view will be made of two subplots
        self.plot_view = pg.GraphicsView(parent = self.frame_plots)
        self.plot_view.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self.plot_view.setAspectLocked(True)
        self.plot_view.setAntialiasing(True)
        self.plot_view.setBackground(self.color_dict["color_background"])

        # we need a layout for the three subplots
        self.plot_layout = pg.GraphicsLayout()
        self.plot_layout.setSpacing(10)

        # attach the layout to the plot view
        self.plot_view.setCentralItem(self.plot_layout)

        # viewbox subplot
        self.plot_viewbox = self.plot_layout.addViewBox(row=0, col=0)
        self.plot_viewbox.setAspectLocked(True)
        self.plot_viewbox.disableAutoRange()

        # subplot
        self.plot_item = self.plot_layout.addPlot(title="2D Plot", row=0, col=1)
        self.plot_item.disableAutoRange()
        self.plot_item.setAutoVisible()
        self.plot_item.showButtons()
        self.plot_item.showGrid(x=False, y=False, alpha=0.3)

        # save bottom axis
        self.initial_bottom_axis = self.plot_item.getAxis("bottom")

        # remove downsampling menu (and operations like fft menu)
        # self.plot_item.ctrlMenu.removeAction(self.plot_item.ctrlMenu.actions()[0])
        # self.plot_item.ctrlMenu.removeAction(self.plot_item.ctrlMenu.actions()[0])

        # adjust the subplot layout
        self.plot_layout.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self.plot_layout.layout.setColumnMinimumWidth(0,50)
        self.plot_layout.layout.setColumnMinimumWidth(1,200)
        self.plot_layout.layout.setColumnStretchFactor(0,1)
        self.plot_layout.layout.setColumnStretchFactor(1,99)
        self.plot_layout.layout.setContentsMargins(8,8,16,8)

        # add the plot view to the frame layout
        self.verticalLayout_frame_plots.addWidget(self.plot_view)

        # set plot titles
        self.plot_item.setTitle(title="2D Plot")

        # set init axis labels
        self.modifyAxisLabels()

        # clear and init variables
        self.plot_item.clear()
        self.curve_items = []
        self.curve_items_names = []

        # show everything
        self.plot_view.show()

        # frame for the toolbar at the bottom of the plot
        self.frame_bottom_of_the_plot = QFrame(self.frame_holder)
        self.frame_bottom_of_the_plot.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_bottom_of_the_plot.setFrameShadow(QFrame.Shadow.Plain)
        self.frame_bottom_of_the_plot.setObjectName("frame_bottom_of_the_plot")

        # layout of the frame for the toolbar at the bottom of the plot
        self.horizontalLayout_frame_bottom_of_the_plot = QHBoxLayout(self.frame_bottom_of_the_plot)
        self.horizontalLayout_frame_bottom_of_the_plot.setObjectName("horizontalLayout_frame_bottom_of_the_plot")
        self.horizontalLayout_frame_bottom_of_the_plot.setContentsMargins(15, 0, 15, 15)
        self.horizontalLayout_frame_bottom_of_the_plot.setSpacing(8)
        self.verticalLayout_stack.addWidget(self.frame_bottom_of_the_plot)

        # push button to apply visualization
        self.pushButton_select_curves = QPushButton(parent=self.frame_bottom_of_the_plot)
        self.pushButton_select_curves.setText(" Axes && Variables ")
        self.pushButton_select_curves.setObjectName("pushButton_select_curves")
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.pushButton_select_curves)

        # separator 1
        self.separator_line_1 = QVSeparationLine()
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.separator_line_1)

        # checkbox for hover
        self.checkBox_hover = QCheckBox(parent=self.frame_bottom_of_the_plot)
        self.checkBox_hover.setText("Hover")
        self.checkBox_hover.setObjectName("checkBox_hover")
        tooltip = "<html><head/><body><p>When this checkbox is checked, a helpful tooltip will be displayed on the graph containing all the relevant curve data.</p></body></html>"
        self.checkBox_hover.setToolTip(tooltip)
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.checkBox_hover)

        # checkbox for removing all-zero curves
        self.checkBox_remove_all_zero_curves = QCheckBox("Remove all-zero curves", parent=self.frame_bottom_of_the_plot)
        self.checkBox_remove_all_zero_curves.setToolTip("When checked, curves with all zero or NaN values will be removed from the plot.")
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.checkBox_remove_all_zero_curves)

        # checkbox for the zooming
        self.checkBox_save_zoom = QCheckBox("Save zooming", parent=self.frame_bottom_of_the_plot)
        self.checkBox_save_zoom.setToolTip("Remember the current zoom level and restore it the next time you open the plot viewer.")
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.checkBox_save_zoom)

        # checkbox for downsampling
        self.checkBox_downsampling = QCheckBox(parent=self.frame_bottom_of_the_plot)
        self.checkBox_downsampling.setText("Downsample (native)")
        self.checkBox_downsampling.setObjectName("checkBox_downsampling")
        tooltip = "<html><head/><body><p>Downsampling can help to increase the performance when displaying data with many points (medium-size arrays). Note that this is different from the custom big data downsampling defined at the settings menu.</p></body></html>"
        self.checkBox_downsampling.setToolTip(tooltip)
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.checkBox_downsampling)

        # add a combobox to select the fft
        self.comboBox_fft = QComboBox(self.frame_bottom_of_the_plot)
        self.comboBox_fft.setObjectName("comboBox_fft")
        self.model_comboBox_fft = self.comboBox_fft.model()
        for row in ["Mode: NORMAL", "Mode: NORMAL - MEAN", "Mode: FFT", "Mode: FFT - MEAN"]:
            self.model_comboBox_fft.appendRow(QStandardItem(str(row)))
        self.comboBox_fft.setModel(self.model_comboBox_fft)
        self.comboBox_fft.setItemDelegate(QStyledItemDelegate())
        self.comboBox_fft.setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in ["Mode: NORMAL", "Mode: FFT"]]))
        self.comboBox_fft.setCurrentIndex(0)
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.comboBox_fft)

        # downsampling and fft do not work simultaneously so disable all at start
        self.checkBox_downsampling.setEnabled(False)
        self.checkBox_downsampling.setChecked(False)
        self.comboBox_fft.setEnabled(False)
        self.comboBox_fft.setCurrentIndex(0)

        # set fft modes to false
        self.fft_mode = False
        self.remove_mean_mode = False

        # combobox for scaling
        self.comboBox_scale = QComboBox(self.frame_bottom_of_the_plot)
        self.comboBox_scale.setObjectName("comboBox_scale")
        self.model_comboBox_scale = self.comboBox_scale.model()
        for row in ["Scale: LINEAR", "Scale: LOG10", "Scale: SYMLOG"]:
            self.model_comboBox_scale.appendRow(QStandardItem(str(row)))
        self.comboBox_scale.setModel(self.model_comboBox_scale)
        self.comboBox_scale.setItemDelegate(QStyledItemDelegate())
        self.comboBox_scale.setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in ["Scale: LINEAR", "Scale: LOG10", "Scale: SYMLOG"]]))
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.comboBox_scale)

        # separator 2
        self.separator_line_2 = QVSeparationLine()
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.separator_line_2)

        # information button
        self.button_bottom_info = QPushButton("", parent=self.frame_bottom_of_the_plot)
        self.button_bottom_info.setObjectName("button_bottom_info")
        self.button_bottom_info.setIcon(QIcon(qta.icon('fa.info-circle')))
        self.button_bottom_info.setToolTip("Click to open information about the toolbar options.")
        self.horizontalLayout_frame_bottom_of_the_plot.addWidget(self.button_bottom_info)

        # persistence (hover)
        if self.persist_sticky and self.global_parent is not None:
            prev_hover = getattr(self.global_parent, "hover_state", False)
        else:
            prev_hover = False
        self.checkBox_hover.setChecked(prev_hover)

        # persistence (zero curves)
        if self.persist_sticky and self.global_parent is not None:
            prev_zero = getattr(self.global_parent, "remove_all_zero_curves_state", False)
        else:
            prev_zero = False
        self.checkBox_remove_all_zero_curves.setChecked(prev_zero)

        # persistence (zooming)
        if self.persist_sticky and self.global_parent is not None:
            prev_zoom = getattr(self.global_parent, "save_zoom_state", False)
        else:
            prev_zoom = False
        self.checkBox_save_zoom.setChecked(prev_zoom)

        # persistence (scaling)
        if self.persist_sticky and self.global_parent is not None:
            prev_scale = getattr(self.global_parent, "scale_state", "LINEAR")
        else:
            prev_scale = "LINEAR"
        index_map = {"LINEAR": 0, "LOG10": 1, "SYMLOG": 2}
        self.comboBox_scale.setCurrentIndex(index_map.get(prev_scale, 0))
        self.log10_mode = (prev_scale == "LOG10")
        self.symlog_mode = (prev_scale == "SYMLOG")

        # spacer to move everything to the left
        self.spacerItem = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_bottom_of_the_plot.addItem(self.spacerItem)

        # to enable or not 1 button mouse mode by default
        if self.mouse_mode_1_button:
            self.plot_item.getViewBox().setMouseMode(pg.ViewBox.RectMode)
        else:
            self.plot_item.getViewBox().setMouseMode(pg.ViewBox.PanMode)

        # enable zoom saving
        self._init_zoom_persistence()

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # binding for selecting and plotting the data
        self.pushButton_select_curves.clicked.connect(self.dataSelectorFromPushButton)

        # binding for downsampling
        self.checkBox_downsampling.clicked.connect(self.setDownsampling)

        # binding for the hover functionality
        self.checkBox_hover.clicked.connect(self.clearDatapointsFromHover)

        # fft mode was changed
        self.comboBox_fft.currentIndexChanged.connect(lambda combobox_index, what_changed="mode": self.changedComboboxSelection(combobox_index, what_changed))

        # persistence bindings
        self.checkBox_remove_all_zero_curves.stateChanged.connect(self.removeAllZeroCurves)
        self.checkBox_save_zoom.stateChanged.connect(self.toggleSaveZoom)
        self.checkBox_hover.stateChanged.connect(self._saveHoverState)
        self.comboBox_scale.currentIndexChanged.connect(self.changedScaleCombobox)

        # info button
        self.button_bottom_info.clicked.connect(self._showBottomBarInfo)

        return

    #----------------------------------------------#

    def toggleSaveZoom(self):
        if self.persist_sticky and self.global_parent is not None:
            self.global_parent.save_zoom_state = self.checkBox_save_zoom.isChecked()

    def toggleSaveZoom(self):
        save_on = self.checkBox_save_zoom.isChecked()
        if self.persist_sticky and self.global_parent is not None:
            self.global_parent.save_zoom_state = save_on
        if save_on:
            self._remember_zoom()
        else:
            if hasattr(self.global_parent, "saved_zoom"):
                del self.global_parent.saved_zoom

    #----------------------------------------------#

    def isSaveZoomEnabled(self):
        """Convenience wrapper used in several places."""
        return getattr(self, "checkBox_save_zoom", None) and self.checkBox_save_zoom.isChecked()

    #----------------------------------------------#

    def setDownsampling(self):

        # set the downsampling
        if self.checkBox_downsampling.isEnabled() and self.checkBox_downsampling.isChecked():
            self.plot_item.setDownsampling(auto=True, mode="peak")
            self.comboBox_fft.blockSignals(True)
            self.comboBox_fft.setEnabled(False)
            self.comboBox_fft.setCurrentIndex(0)
            self.comboBox_fft.blockSignals(False)
        else:
            self.plot_item.setDownsampling(False)
            self.comboBox_fft.blockSignals(True)
            self.comboBox_fft.setEnabled(True)
            self.comboBox_fft.blockSignals(False)

        return

    #----------------------------------------------#

    def changedScaleCombobox(self, combobox_index):

        # update flag
        txt = self.comboBox_scale.currentText()
        self.log10_mode = (txt == "Scale: LOG10")
        self.symlog_mode = (txt == "Scale: SYMLOG")

        # remember state so it persists
        if self.persist_sticky and self.global_parent is not None:
            self.global_parent.scale_state = ("LOG10" if self.log10_mode else "SYMLOG" if self.symlog_mode else "LINEAR")

        # refresh the current plot (reuse cached selection)
        if self.saved_selected_indexes and self.saved_names:
            self.plotData(self.saved_selected_indexes, self.saved_names, self.saved_axis_list, first_time=False)

    #----------------------------------------------#

    def changedComboboxSelection(self, combobox_index, what_changed):

        # update fft variable
        if what_changed == "mode":
            if "FFT" in self.comboBox_fft.currentText():
                self.fft_mode = True
            else:
                self.fft_mode = False
            if "MEAN" in self.comboBox_fft.currentText():
                self.remove_mean_mode = True
            else:
                self.remove_mean_mode = False

        # disable downsampling
        if self.fft_mode or self.remove_mean_mode:
            self.checkBox_downsampling.setEnabled(False)
        else:
            self.checkBox_downsampling.setEnabled(True)

        # update plots
        if self.saved_selected_indexes and self.saved_names:
            self.plotData(self.saved_selected_indexes, self.saved_names, self.saved_axis_list, first_time=False)

        return

    #----------------------------------------------#

    def dataSelectorFromPushButton(self):

        # clean up hover functions
        self.clearDatapointsFromHover(from_on_mouse_moved=True)

        # run data selector dialog
        self.plot_data_selector = PlotDataSelector(self.dataframe, self.app, self.app_root_path, self, self.saved_selected_indexes, self.saved_names, self.saved_axis_list, self.var_axis_dict, x_label=self.x_label, y_label=self.y_label)
        self.plot_data_selector.exec()

        return

    #----------------------------------------------#

    def selectionOutput(self, selected_indexes, names, axis_list, x_label, y_label):

        # save labels
        self.x_label = x_label
        self.y_label = y_label

        # update backups with the new full selection
        self.original_selected_indexes = selected_indexes.copy()
        self.original_names = names.copy()
        self.original_axis_list = axis_list.copy()

        # get the effective selection (filtered if checkbox is active) and plot the data
        effective_indexes, effective_names, effective_axis = self._get_effective_selection(selected_indexes, names, axis_list)
        if effective_indexes:
            self.plotData(effective_indexes, effective_names, effective_axis, first_time=False)

        return

    #----------------------------------------------#

    def makeColorPaletteForLegendAndPlot(self, input_array):

        # init color palette based on the input length
        palette_name = self.color_dict["color_foreground_palette_name"]
        try:
            self.color_palette = sns.color_palette(palette_name, len(input_array))
        except Exception as xcp:
            self.color_palette = sns.color_palette(None, len(input_array))
            print("Using the default palette as {} threw the following exception: {}".format(palette_name, xcp))

        # convert palette to rgb
        new_color_palette = []
        for tup in self.color_palette:
            new_color_palette.append(tuple([x * 255 for x in tup]))

        # save palette
        self.color_palette_global = np.array(new_color_palette)

        return new_color_palette

    #----------------------------------------------#

    def removeAllZeroCurves(self):

        # store the current state in the global_parent so it persists
        if self.persist_sticky and self.global_parent is not None:
            self.global_parent.remove_all_zero_curves_state = self.checkBox_remove_all_zero_curves.isChecked()

        # check state
        if self.checkBox_remove_all_zero_curves.isChecked():

            # plot filtered data
            effective_indexes, effective_names, effective_axis = self._filter_zero_curves(self.original_selected_indexes, self.original_names, self.original_axis_list)
            if effective_indexes:
                self.plotData(effective_indexes, effective_names, effective_axis, first_time=False)
            else:
                message_title = "Error"
                message_text = "No curves to plot after all-zero removal."
                message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
                message_box.setWindowIcon(QIcon(self.window_icon_path))
                message_box.exec()

                # set back checkbox
                QTimer.singleShot(0, lambda: self.checkBox_remove_all_zero_curves.setChecked(False))
                if self.global_parent is not None:
                    self.global_parent.remove_all_zero_curves_state = False

        # plot original data
        else:
            self.plotData(self.original_selected_indexes, self.original_names, self.original_axis_list, first_time=False)

    #----------------------------------------------#

    def plotData(self, selected_indexes, names, axis_list, first_time = True, bindMouseMovedSignal = True, offset_width = 20, maximum_legend_width = 500):

        # big file detected?
        big_file_detected = False

        # reset mouse hover
        self.data_bounds = []
        self.mouseHoverFirstTime = False

        # clear viewboxes and axis items
        self.clearViewboxes()
        self.clearYAxisItems()

        # init all
        self.plot_item.clear()
        self.curve_items = []
        self.curve_items_names = []

        # init axis item
        if not first_time:
            self.plot_item.setAxisItems({'bottom': self.initial_bottom_axis})

        # determine whether the data belongs to a specific type (e.g. TIMESTAMP or TIMESTEP SERIES)
        index_type = get_index_type(attributes = self.attributes, df = self.dataframe, return_dtype_otherwise = False)

        # save for hover
        if index_type == "datetime":
            self.is_datetime = True
        else:
            self.is_datetime = False

        # also needed for hover
        self.x_is_string = False
        self.string_labels = []

        # get labels
        if self.attributes:
            if "index" in self.attributes.keys():
                if self.attributes["index"]:
                    if "unit" in self.attributes["index"].keys():
                        self.x_label = str(fromBytesToString(self.attributes["index"]["unit"]))
            if "data" in self.attributes.keys():
                if self.attributes["data"]:
                    if "unit" in self.attributes["data"].keys():
                        self.y_label = str(fromBytesToString(self.attributes["data"]["unit"]))

        # change stretch based on legend widths
        if names:
            max_width = max([getPixelWidthFromQLabel(str_name) for str_name in names])
            if max_width + offset_width >= maximum_legend_width:
                self.plot_layout.layout.setColumnMinimumWidth(0, maximum_legend_width)
            else:
                self.plot_layout.layout.setColumnMinimumWidth(0, max_width + offset_width)

        # reset clip to view to avoid errors
        self.plot_item.setClipToView(False)

        # disable auto range
        self.plot_item.enableAutoRange(False, False)

        # get color palette
        self.color_palette = self.color_palette_global[selected_indexes]

        # init axis viewboxes
        self.y_axis_viewboxes = collections.OrderedDict()
        self.y_axis_viewboxes[axis_list[0]] = self.plot_item.vb

        # init axis items
        self.y_axis_items = collections.OrderedDict()
        self.y_axis_items[axis_list[0]] = self.plot_item.getAxis("left")

        # if we have more than 1 y axis
        if len(np.unique(axis_list)) > 1:

            # iterate over y axes
            for c_axis_name, axis_name in enumerate(axis_list):

                # ignore first axis (as it is already set)
                if c_axis_name > 0:

                    # no need to add if it is already there
                    if axis_name not in self.y_axis_viewboxes.keys():

                        # init viewbox and axis
                        self.y_axis_viewboxes[axis_name] = pg.ViewBox()
                        self.y_axis_items[axis_name] = pg.AxisItem("left")

                        # add to the layout
                        self.plot_layout.addItem(self.y_axis_items[axis_name], row=0, col=c_axis_name+1)
                        self.plot_layout.scene().addItem(self.y_axis_viewboxes[axis_name])

                    # link axis with viewbox
                    self.y_axis_items[axis_name].linkToView(self.y_axis_viewboxes[axis_name])

                    # set the axis name
                    self.y_axis_items[axis_name].setLabel(axis_name)

            # link viewboxes
            sorted_vbs = list(self.y_axis_viewboxes.values())
            for vb_id in range(1, len(sorted_vbs)):
                sorted_vbs[vb_id].setXLink(sorted_vbs[vb_id-1])

        # set init axis labels
        self.modifyAxisLabels(self.x_label, self.y_label, init_y = axis_list[0])

        # iterate over all indexes or curves
        for counter, index in enumerate(selected_indexes):

            # get the data
            data_y = self.dataframe.iloc[:, index].to_numpy()

            # get the index
            data_x = np.array([])
            try:
                if index_type == "datetime":
                    if not self.fft_mode:
                        data_x = pd.to_datetime(self.dataframe.index, format='%Y-%m-%dT%H:%M:%S.%f000').tz_localize('Etc/GMT-2').astype(int) // 10**9
                        data_x = data_x.to_numpy()
                        self.plot_item.setAxisItems({'bottom': DateAxisItem(orientation='bottom')})
                elif index_type == "timestep":
                    data_x = self.dataframe.index.to_numpy().astype(float)
                elif self.display_strings_on_x_axis and pd.api.types.is_string_dtype(self.dataframe.index):
                    self.x_is_string = True
                    self.string_labels = list(self.dataframe.index)
                    data_x = np.arange(len(self.dataframe.index))
                    self.plot_item.setAxisItems({'bottom': StringAxisItem(labels=self.string_labels, orientation='bottom')})
            except Exception as xcp:
                print("Exception when converting dataframe index: {}".format(xcp))

            # default index case
            if not data_x.any():
                if self.big_data_mode:
                    pass # data_x is not used for big data mode in order to save up memory space
                elif self.dataframe.index.equals(pd.RangeIndex(start=0, stop=self.dataframe.shape[0])):
                    data_x = self.dataframe.index.to_numpy()
                else:
                    data_x = np.arange(0, len(data_y))

            # get the formatted name
            formatted_name = names[counter]

            # look for zeros
            if np.all(data_y == 0) or np.all(data_y == np.nan):
                formatted_name = deepcopy(formatted_name) + " Ø°"

            # fft conversion
            if self.fft_mode:
                data_x, data_y = self.convertArrayToFFTArray(data_y, remove_dc_offset=self.remove_mean_mode)
                if self.log10_mode:
                    data_y = self.computeLog10Array(data_y)
                elif self.symlog_mode:
                    data_y = self.computeSymlogArray(data_y)
            elif self.log10_mode:
                data_y = self.computeLog10Array(data_y)
            elif self.symlog_mode:
                data_y = self.computeSymlogArray(data_y)
            elif self.remove_mean_mode:
                data_y = self.subtractMeanFromArray(data_y)

            # convert y to int64 if overflow detected
            data_y = self.safe_convert_to_int64_if_overflow(data_y)

            # get key (name) for the axis
            axis_key = axis_list[counter]

            # CASE 1 - SMALL DATA (USE NORMAL PLOT WITH OR WITHOUT DEFAULT DOWNSAMPLING)
            if not self.big_data_mode:

                # create curve
                plot_item = pg.PlotCurveItem(x=data_x, y=data_y, pen=self.color_palette[counter], name=formatted_name)

                # add the item to the viewbox
                self.y_axis_viewboxes[axis_key].addItem(plot_item)

            # CASE 2 - BIG DATA (USE CUSTOM BIG DATA PLOT WITH CUSTOM DOWNSAMPLING AND CHUNKING)
            else:

                # init big data curve
                plot_item = BigDataPlot(pen=self.color_palette[counter], name=formatted_name)
                plot_item.setPlotData(PlotDataClass(x=None, y=data_y, cache="auto", chunk_size = self.chunk_size, app = self.app, name = names[counter]))

                # add the item to the viewbox
                self.y_axis_viewboxes[axis_key].addItem(plot_item)

                # manually range the x axis to update all the points
                # self.plot_item.setXRange(0, data_y.shape[0])
                self.y_axis_viewboxes[axis_key].setXRange(0, data_y.shape[0])

                # disable pyqtgraph menus (e.g. default downsampling menu)
                # self.plot_item.ctrlMenu = None
                self.y_axis_viewboxes[axis_key].ctrlMenu = None

                # update boolean
                big_file_detected = True

            # plot the data
            self.curve_items.append(plot_item)
            self.curve_items_names.append(formatted_name)

            # for hover
            self.data_bounds.append(plot_item.dataBounds(ax=0))

        # this is used for the Ctrl mute hack
        self.items_dict = {}
        for count_it1, it1 in enumerate(self.curve_items):
            lbl = self.curve_items_names[count_it1]
            self.items_dict[lbl] = {}
            self.items_dict[lbl]["visible"] = True
            self.items_dict[lbl]["items"] = (it1,)

        # remove the legend in case it was already created
        if self.legend:
            self.plot_viewbox.removeItem(self.legend)

        # recreate the legend
        self.legend = CustomMultiPlotLegendItem(horSpacing=20, verSpacing=0, pen=(255,255,255), brush='k', frame=False, labelTextSize='8pt', colCount=1)
        self.legend.addAllItems(self.items_dict)
        self.legend.setParentItem(self.plot_viewbox)
        self.legend.anchor((0.5, 0.5), (0.5, 0.5))
        for index, item_alias in enumerate(self.curve_items):
            self.legend.addItem(item_alias, self.curve_items_names[index], additional_linked_items=[])

        # some adjustments
        self.plot_item.show()

        # CASE NOT BIG DATA
        if not big_file_detected:

            # some adjustments
            self.plot_item.setClipToView(True)
            self.plot_item.setDownsampling(False)
            self.plot_item.autoRange()
            self.plot_item.enableAutoRange()

            # first time stuff
            if first_time:
                self.checkBox_downsampling.setEnabled(True)
                self.checkBox_downsampling.setChecked(self.pyqtgraph_default_downsample)
            else:
                self.plot_item.setAutoVisible(True)
                self.plot_item.setAutoVisible(False)

            # set the downsampling
            self.setDownsampling()

        # CASE BIG DATA
        else:

            # first time stuff
            if first_time:
                self.checkBox_downsampling.setEnabled(False)
                self.comboBox_fft.setEnabled(True)

            # some adjustments
            self.plot_item.autoRange()

        # set visibility states
        self.legend.setVisibilityStateForAllItems()

        # saves for plot updates
        self.saved_selected_indexes = selected_indexes
        self.saved_names = names
        self.saved_axis_list = axis_list

        # bind mouse moved signals
        if bindMouseMovedSignal:
            try:
                if self.mouse_moved_connection:
                    self.plot_item.scene().sigMouseMoved.disconnect(self.mouse_moved_connection)
            except:
                pass
            self.mouse_moved_connection = lambda point: self.onMouseMoved(point=point, plot=self.plot_item, curve_items=self.curve_items, verbose=True)
            self.plot_item.scene().sigMouseMoved.connect(self.mouse_moved_connection)

        # autorange once to fit views at start
        for axis_name in self.y_axis_viewboxes.keys():
            self.y_axis_viewboxes[axis_name].enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

        # update views when resizing (axis)
        try:
            self.plot_item.vb.sigResized.disconnect(self.updateViewsGivenAxis)
        except:
            pass
        self.plot_item.vb.sigResized.connect(self.updateViewsGivenAxis)
        self.updateViewsGivenAxis()

        return

    #----------------------------------------------#

    def clearYAxisItems(self):

        # clear all axis items
        c = 0
        for axis_name, axis in self.y_axis_items.items():
            if c > 0:
                self.plot_layout.removeItem(axis)
                vb_to_del = pg.ViewBox()
                axis.linkToView(vb_to_del)
                del vb_to_del
            c += 1

        # delete dict elements (but the first one)
        if len(self.y_axis_items) > 1:
            keys = deepcopy(list(self.y_axis_items.keys())[1:])
            for key in keys:
                del self.y_axis_items[key]

        return

    #----------------------------------------------#

    def clearViewboxes(self):

        # clear all viewboxes
        c = 0
        for viewbox_name, viewbox in self.y_axis_viewboxes.items():
            viewbox.clear()
            if c > 0:
                self.plot_layout.scene().removeItem(viewbox)
                viewbox.setXLink(None)
            c += 1

        # delete dict elements (but the first one)
        if len(self.y_axis_viewboxes) > 1:
            keys = deepcopy(list(self.y_axis_viewboxes.keys())[1:])
            for key in keys:
                del self.y_axis_viewboxes[key]

        return

    #----------------------------------------------#

    def updateViewsGivenAxis(self):

        # update views when resizing (axis)
        sorted_vbs = list(self.y_axis_viewboxes.values())
        for vb_id in range(1, len(sorted_vbs)):
            sorted_vbs[vb_id].setGeometry(sorted_vbs[0].sceneBoundingRect())

        return

    #----------------------------------------------#

    def modifyAxisLabels(self, x_label = "x", y_label = "y", init_x = "x1", init_y = "y1"):

        # modify axis labels
        if self.fft_mode and self.log10_mode:
            self.plot_item.setLabel('left', f"{init_y} = log\u2081\u2080(amplitude)")
        elif self.fft_mode and self.symlog_mode:
            self.plot_item.setLabel('left', f"{init_y} = symlog(amplitude)")
        elif self.fft_mode:
            y_label = "amplitude"
            x_label = "{}<sup>-1</sup> (step = 1/2n_{})".format(x_label, x_label)
            self.plot_item.setLabel(axis='left', text="{} = {}".format(init_y, y_label))
            self.plot_item.setLabel(axis='bottom', text="{} = {}".format(init_x, x_label))
        elif self.log10_mode:
            self.plot_item.setLabel(axis='left', text=f"{init_y} = log\u2081\u2080({y_label})")
            self.plot_item.setLabel(axis='bottom', text=f"{init_x} = {x_label}")
        elif self.symlog_mode:
            self.plot_item.setLabel(axis='left', text=f"{init_y} = symlog({y_label})")
            self.plot_item.setLabel(axis='bottom', text=f"{init_x} = {x_label}")
        else:
            self.plot_item.setLabel(axis='left', text="{} = {}".format(init_y, y_label))
            self.plot_item.setLabel(axis='bottom', text="{} = {}".format(init_x, x_label))

        return

    #----------------------------------------------#

    def onMouseMoved(self, point, plot, curve_items, verbose = True):

        # only if checkbox is enabled
        if self.checkBox_hover.isChecked():

            # get the cursor
            p = plot.vb.mapSceneToView(point)

            # round the x coordinate where the cursor is
            x_cursor = p.x()

            # get the y coordinate
            y_cursor = p.y()

            # a while loop in case first item is muted
            bounds_set = False
            curve_index = 0
            while not bounds_set:

                # this happens when there are no visible items
                if curve_index >= len(curve_items):
                    break

                # get first curve
                first_curve = curve_items[curve_index]

                # lower and upper bounds of the cursor
                first_curve_data_bounds = self.data_bounds[0]

                # only if curve exists
                if first_curve_data_bounds[0] != None and first_curve_data_bounds[1] != None:
                    if x_cursor >= first_curve_data_bounds[1]:
                        x_cursor_limited = first_curve_data_bounds[1]
                    elif x_cursor <= first_curve_data_bounds[0]:
                        x_cursor_limited = first_curve_data_bounds[0]
                    else:
                        x_cursor_limited = x_cursor
                    bounds_set = True
                else:
                    bounds_set = False
                    curve_index += 1
                    continue

                # check if target item should be removed (only if it is outside of the limits)
                remove_target_item = False
                total_range = first_curve_data_bounds[1] - first_curve_data_bounds[0]
                if x_cursor > first_curve_data_bounds[1] + 0.1*total_range:
                    remove_target_item = True
                elif x_cursor < first_curve_data_bounds[0] - 0.1*total_range:
                    remove_target_item = True

            # skip all the hover functionality if there are no available curves
            if not bounds_set:
                self.clearDatapointsFromHover(from_on_mouse_moved=True)
                return

            # init list
            vals_at_x_cursor = []

            # iterate over all the curves and get the y values at the x cursor position
            true_x_val, true_x_idx = None, None
            at_least_one_element_is_visible = False
            idx_curve = 0
            for curve in curve_items:

                # only if curve is visible
                if self.items_dict[curve.name()]["visible"]:

                    # get original array
                    array = curve.getData()

                    # get true x
                    if idx_curve == 0:
                        true_x_val, true_x_idx = numpy_find_nearest(array[0], x_cursor_limited)

                    # append the value at the x cursor position
                    val = array[1][true_x_idx]
                    if math.isnan(val):
                        vals_at_x_cursor.append(-math.inf)
                    else:
                        vals_at_x_cursor.append(val)

                    # update boolean
                    at_least_one_element_is_visible = True

                    # update index only if item was visible
                    idx_curve += 1

                # otherwise update with infinite value
                else:

                    # append infinite value
                    vals_at_x_cursor.append(-math.inf)

            # only if at least one element is visible
            if at_least_one_element_is_visible:

                # get final x
                if true_x_val != None:
                    final_x_val = true_x_val
                else:
                    final_x_val = x_cursor_limited

                # get color from palette and modify labels
                color = self.invert_color(self.color_dict["color_background"])
                label_opts = {'fill': self.color_dict["color_background"], 'border': color, 'color': color, 'offset': QPoint(0, 20)}

                # format the strings
                if self.display_strings_on_x_axis and self.x_is_string:
                    string_idx = int(round(final_x_val))
                    if 0 <= string_idx < len(self.string_labels):
                        final_x_val_formatted = self.string_labels[string_idx]
                    else:
                        final_x_val_formatted = ""
                elif self.is_datetime and not self.fft_mode:
                    final_x_val_formatted = datetime.utcfromtimestamp(final_x_val).strftime('%Y-%m-%dT%H:%M:%S.%f000')
                else:
                    final_x_val_formatted = "{}".format(final_x_val)

                # if remove target item
                if remove_target_item:
                    if self.targetItem:
                        plot.removeItem(self.targetItem)
                        self.targetItem = None
                    if self.infiniteLine:
                        plot.removeItem(self.infiniteLine)
                        self.infiniteLine = None
                    self.mouseHoverFirstTime = False

                # if not remove target item
                else:

                    # create box label with all curves information
                    box_label = ""
                    for item_id in range(0, len(curve_items)):
                        if vals_at_x_cursor[item_id] != -math.inf:
                            x_formatted = "{}".format(final_x_val_formatted)
                            y_formatted = "{}".format(vals_at_x_cursor[item_id])
                            name_formatted = curve_items[item_id].name()
                            box_label += "\u2022 {} (x:{}, y:{})".format(name_formatted, x_formatted, y_formatted)
                            box_label += "\n"

                    # remove last line break
                    if box_label:
                        box_label = box_label[0:-2]

                    # first time check
                    if not self.mouseHoverFirstTime:

                        # add to the plot
                        self.mouseHoverFirstTime = True
                        self.targetItem = pg.TargetItem(movable=False, pos=(final_x_val, y_cursor), label=box_label, symbol="x", size=0, pen=color, labelOpts=label_opts)
                        plot.addItem(self.targetItem)
                        self.infiniteLine = pg.InfiniteLine(angle=90, movable=False, pen=color)
                        self.infiniteLine.setPos(final_x_val)
                        plot.addItem(self.infiniteLine)

                    # if it is not the first time
                    else:

                        # update the cursor
                        if self.targetItem:
                            self.targetItem.setPos((final_x_val, y_cursor))
                            self.targetItem.setLabel(box_label, labelOpts=label_opts)
                            self.infiniteLine.setPos(final_x_val)

            # if nothing is visible then remove target item
            else:
                if self.targetItem:
                    plot.removeItem(self.targetItem)
                    self.targetItem = None
                if self.infiniteLine:
                    plot.removeItem(self.infiniteLine)
                    self.infiniteLine = None
                self.mouseHoverFirstTime = False

        return

    #----------------------------------------------#

    def clearDatapointsFromHover(self, from_on_mouse_moved = False):

        # remove hover when unchecked
        if not self.checkBox_hover.isChecked() or from_on_mouse_moved:
            if self.mouseHoverFirstTime:
                if self.targetItem:
                    self.plot_item.removeItem(self.targetItem)
                    self.targetItem = None
                if self.infiniteLine:
                    self.plot_item.removeItem(self.infiniteLine)
                    self.infiniteLine = None
                self.mouseHoverFirstTime = False

        return

    #----------------------------------------------#

    def subtractMeanFromArray(self, array):

        # simply remove the mean
        array = array - np.nanmean(array)

        return array

    #----------------------------------------------#

    def computeLog10Array(self, array: np.ndarray) -> np.ndarray:
        """
        Return log10(array) while skipping non-positive samples.
        Points ≤ 0 become NaN so they simply disappear from the plot.
        """
        with np.errstate(divide='ignore', invalid='ignore'):
            array = np.where(array <= 0, np.nan, array)
            return np.log10(array)

    #----------------------------------------------#

    def computeSymlogArray(self, arr: np.ndarray, linthresh: float = 1.0, base: float = 10.0) -> np.ndarray:
        """
        Symmetric log transform (like Matplotlib’s *symlog*).
        • |x| ≤ linthresh  →  linear region  (preserves sign)
        • otherwise        →  sign(x) * (log_base(|x|/linthresh) + 1)
        """
        sign = np.sign(arr)
        abs_x = np.abs(arr)
        out = np.empty_like(arr, dtype=float)

        lin_mask = abs_x <= linthresh
        log_mask = ~lin_mask

        out[lin_mask] = sign[lin_mask] * abs_x[lin_mask] / linthresh
        out[log_mask] = sign[log_mask] * (1.0 + np.log(abs_x[log_mask] / linthresh) / np.log(base))

        # handle zeros and negatives gracefully -> NaN disappears from plot
        out = np.where(arr == 0, 0, out)
        return out

    #----------------------------------------------#

    def convertArrayToFFTArray(self, array, remove_dc_offset = True):

        # handle nan values by replacing them with the mean of non-nan values
        if np.any(np.isnan(array)):
            array = np.where(np.isnan(array), np.nanmean(array), array)

        # subtract the mean
        if remove_dc_offset:
            array = self.subtractMeanFromArray(array)

        # get number of time points
        n = len(array)

        # obtain the fft
        array_fft = (1/n) * scipy_compute_rfft(array)

        # get sample spacing (assume uniform sampling)
        d = 1.0

        # scale x axis so that it goes from 0 to 0.5
        x = scipy_compute_rfftfreq(n,d)

        # scale y axis so that we only have positive values
        y = np.abs(array_fft)

        return x,y

    #----------------------------------------------#

    def closeEvent(self, evt):

        # remove and delete curve items
        try:
            if hasattr(self, 'curve_items'):
                for item in self.curve_items:
                    self.plot_item.removeItem(item)
                    del item
                self.curve_items.clear()
        except Exception as xcp:
            pass

        # remove and delete legend
        try:
            if self.legend:
                if self.legend.scene():
                    self.plot_viewbox.removeItem(self.legend)
                del self.legend
        except Exception as xcp:
            pass

        # manage y-axes and viewboxes correctly
        try:
            if hasattr(self, 'y_axis_items'):
                for axis in self.y_axis_items.values():
                    if axis.scene():
                        axis.scene().removeItem(axis)
                    del axis
                self.y_axis_items.clear()
            if hasattr(self, 'y_axis_viewboxes'):
                for viewbox in self.y_axis_viewboxes.values():
                    if viewbox.scene():
                        self.plot_layout.scene().removeItem(viewbox)
                    del viewbox
                self.y_axis_viewboxes.clear()
        except Exception as xcp:
            pass

        # clean up GraphicsView and GraphicsLayout
        try:
            if self.plot_view and self.plot_view.scene():
                self.plot_layout.clear()
                self.frame_plots.layout().removeWidget(self.plot_view)
                self.plot_view.deleteLater()
        except Exception as xcp:
            pass

        # clear and delete layouts and widgets
        try:
            clearLayout(self.verticalLayout_frame_holder)
            if hasattr(self, 'scroll_area'):
                self.scroll_area.takeWidget()
                self.scroll_area.deleteLater()
            if hasattr(self, 'frame_holder'):
                self.frame_holder.deleteLater()
        except Exception as xcp:
            pass

        # call the garbage collector manually to clean up any residual memory
        gc.collect()

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

    def find_key_by_index(self, dictionary, index):
        for key, value in dictionary.items():
            if index in value:
                return key
        return None

    #----------------------------------------------#

    def invert_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        r_inv, g_inv, b_inv = 255 - r, 255 - g, 255 - b
        inverted_hex_color = "#{:02x}{:02x}{:02x}".format(r_inv, g_inv, b_inv)
        return inverted_hex_color

    #----------------------------------------------#

    def safe_convert_to_int64_if_overflow(self, data_y):
        if np.issubdtype(data_y.dtype, np.integer):
            dtype_info = np.iinfo(data_y.dtype)
            int_min = dtype_info.min
            int_max = dtype_info.max
            if np.any(data_y <= int_min) or np.any(data_y >= int_max):
                return data_y.astype(np.int64)
        return data_y

    #----------------------------------------------#

    def _filter_zero_curves(self, indexes, names, axis_list):
        """Return only curves that are not all zeros or all NaNs."""
        filtered_indexes = []
        filtered_names = []
        filtered_axis = []
        for i, index in enumerate(indexes):
            data_y = self.dataframe.iloc[:, index].to_numpy()
            if not (np.all(data_y == 0) or np.all(np.isnan(data_y))):
                filtered_indexes.append(index)
                filtered_names.append(names[i])
                filtered_axis.append(axis_list[i])
        return filtered_indexes, filtered_names, filtered_axis

    #----------------------------------------------#

    def _get_effective_selection(self, indexes, names, axis_list):
        """Return filtered selection if the checkbox is checked, otherwise return full selection."""
        if self.checkBox_remove_all_zero_curves.isChecked():
            return self._filter_zero_curves(indexes, names, axis_list)
        else:
            return indexes, names, axis_list

    #----------------------------------------------#

    def _init_zoom_persistence(self):
        """Attach a debounced listener that stores the current view-range."""
        if not (self.persist_sticky and self.isSaveZoomEnabled()):
            return
        self._zoom_timer = QTimer(self)
        self._zoom_timer.setSingleShot(True)
        self._zoom_timer.setInterval(500) # ms debounce
        self._zoom_timer.timeout.connect(self._remember_zoom)
        self.plot_item.vb.sigRangeChanged.connect(lambda *_: self._zoom_timer.start())

    #----------------------------------------------#

    def _remember_zoom(self):
        """Store current view-ranges and the dataframe shape."""
        if not self.isSaveZoomEnabled() or self.global_parent is None:
            return
        x_rng, y_rng = self.plot_item.vb.viewRange()
        self.global_parent.saved_zoom = {
            "x": tuple(x_rng),
            "y": tuple(y_rng),
            "df_shape": self.dataframe.shape
        }

    #----------------------------------------------#

    def _saveHoverState(self):
        if self.persist_sticky and self.global_parent is not None:
            self.global_parent.hover_state = self.checkBox_hover.isChecked()

    #----------------------------------------------#

    def _showBottomBarInfo(self) -> None:
        """Explain the meaning of every control on the bottom toolbar."""
        html = (
            "<h2>Plot Toolbar</h2>"
            "<p>The plot tab is a <b>PyQtGraph-based</b> widget designed to handle very large arrays interactively. "
            "The toolbar offers the following options:</p>"
            "<ul>"
            "<li><b>Axes &amp; Variables selector</b> – choose which columns to plot and on which Y-axis.</li>"
            "<li><b>Hover *</b> – when enabled, moving the cursor shows the X/Y value of every visible curve.</li>"
            "<li><b>Remove all-zero curves *</b> – hides curves that are entirely zeros or NaNs. "
            "Such curves carry the marker <span style='color:red;'>Ø°</span> in their legend entry and are drawn in red when this option is <i>disabled</i>.</li>"
            "<li><b>Save zooming *</b> – remembers the current view range so it is restored the next time you open the plot.</li>"
            "<li><b>Downsample (native)</b> – lets PyQtGraph decimate the data for smoother interaction on medium-sized series. "
            "<i>Recommendation:</i> leave this disabled and use DAVIT’s built-in down-sampling (configurable in the app settings).</li>"
            "<li><b>Mode combobox</b> – data-domain transforms: FFT and/or mean subtraction.</li>"
            "<li><b>Scale combobox *</b> – linear, base-10 logarithmic or symlog Y-axis.</li>"
            "</ul>"
            "<p>Controls marked with an asterisk (*) are <b>sticky</b>: their state is remembered across plot sessions.</p>"
        )
        QMessageBox.information(
            self,
            "Plot Toolbar Information",
            html,
            QMessageBox.StandardButton.Ok
        )

    #----------------------------------------------#

#################################################################
#################################################################
