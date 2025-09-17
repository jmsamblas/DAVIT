#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS
from davit.__imports__ import *
import h5py

# SPECIFIC IMPORTS

from davit.utils.hdf5_save_dataframe import HDF5DataFrameHandler
from scipy.stats import gaussian_kde

#################################################################
#################################################################

class HistogramOptionsDialog(QDialog):

    #----------------------------------------------#

    def __init__(self, parent=None, global_parent=None, column_list=[], default_bins=50, default_density=False, default_show_kde=True):

        # init and attributes
        super().__init__(parent)
        self.global_parent = global_parent
        self.column_list = column_list
        self.default_bins = default_bins
        self.default_density = default_density
        self.default_show_kde = default_show_kde

        # set title and icon
        self.setWindowTitle("Histogram Options Dialog")
        self.setWindowIcon(qta.icon("fa5s.chart-bar"))

        # fixed size
        self.setFixedSize(480, 360)

        # build and bind
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # main layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # group box for options
        self.options_group = QGroupBox("Options", parent=self)
        self.options_group.setStyleSheet("font-weight: bold;")
        self.main_layout.addWidget(self.options_group)

        # grid for options
        self.grid_layout = QGridLayout(self.options_group)
        self.options_group.setLayout(self.grid_layout)

        # column selection
        self.label_columns = QLabel("Select Columns", parent=self.options_group)
        self.label_columns.setStyleSheet("font-weight: normal; color: black;")
        self.list_widget_columns = QListWidget(self.options_group)
        self.list_widget_columns.setStyleSheet("font-weight: normal;")
        self.list_widget_columns.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget_columns.addItems(self.column_list)
        self.grid_layout.addWidget(self.label_columns, 0, 0)
        self.grid_layout.addWidget(self.list_widget_columns, 0, 1)

        # number of bins option
        self.label_bins = QLabel("Number of Bins", parent=self.options_group)
        self.label_bins.setStyleSheet("font-weight: normal; color: black;")
        self.spinbox_bins = QSpinBox(self.options_group)
        self.spinbox_bins.setStyleSheet("font-weight: normal;")
        self.spinbox_bins.setMinimum(1)
        self.spinbox_bins.setMaximum(1000)
        self.spinbox_bins.setValue(self.default_bins)
        self.grid_layout.addWidget(self.label_bins, 1, 0)
        self.grid_layout.addWidget(self.spinbox_bins, 1, 1)

        # density option (normalization)
        self.label_density = QLabel("Use Density (Normalize)", parent=self.options_group)
        self.label_density.setStyleSheet("font-weight: normal; color: black;")
        self.checkbox_density = QCheckBox(self.options_group)
        self.checkbox_density.setChecked(self.default_density)
        self.grid_layout.addWidget(self.label_density, 2, 0)
        self.grid_layout.addWidget(self.checkbox_density, 2, 1)

        # show KDE plot option
        self.label_kde = QLabel("Show KDE Plot", parent=self.options_group)
        self.label_kde.setStyleSheet("font-weight: normal; color: black;")
        self.checkbox_kde = QCheckBox(self.options_group)
        self.checkbox_kde.setChecked(self.default_show_kde)
        self.grid_layout.addWidget(self.label_kde, 3, 0)
        self.grid_layout.addWidget(self.checkbox_kde, 3, 1)

        # vertical spacer
        self.v_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.main_layout.addSpacerItem(self.v_spacer)

        # confirmation panel
        self.confirmation_frame = QFrame(self)
        self.confirmation_layout = QHBoxLayout(self.confirmation_frame)
        self.confirmation_layout.setContentsMargins(0, 0, 0, 0)
        self.confirmation_frame.setLayout(self.confirmation_layout)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.label_question = QLabel(text="Do you want to create the histogram? ", parent=self.confirmation_frame)
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

        # typical accept and reject bindings
        self.btn_yes.clicked.connect(self.accept)
        self.btn_no.clicked.connect(self.reject)
        return

    #----------------------------------------------#

    def accept(self):
        selected_items = self.list_widget_columns.selectedItems()
        if not selected_items:
            message_box = QMessageBox(QMessageBox.Icon.Warning, "No Selection", "Please select at least one column to plot.", parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.chart-bar"))
            message_box.exec_()
            return
        options = {
            "selected_columns": [item.text() for item in selected_items],
            "bins": self.spinbox_bins.value(),
            "density": self.checkbox_density.isChecked(),
            "show_kde": self.checkbox_kde.isChecked()
        }
        if self.global_parent:
            self.global_parent.runHistogramAfterDialog(options)
        super().accept()
        return

#################################################################
#################################################################

class HistogramTab(QWidget):

    #----------------------------------------------#

    def __init__(self, app, dataframe, attributes, init_build, app_root_path=None, window_icon_path=None, parent=None, global_parent=None, display_name=""):

        # init
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
        self.display_name = display_name

        # own attributes
        self.tab_is_built = False
        self.histogram_data = {}
        self.options = {"bins": 50, "density": False, "show_kde": True}
        self.current_legend = None

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        qss_path = os.path.join(self.app_root_path, "resources", "qss", "histogram_tab.qss")
        if qss_path and os.path.exists(qss_path):
            with open(qss_path, "r") as file_qss:
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
        self.verticalLayout_frame_holder.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.verticalLayout_frame_holder)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_holder.setObjectName("frame_holder")

        # set the main frame as the widget of the QScrollArea
        self.scroll_area.setWidget(self.frame_holder)

        # add the QScrollArea to the layout
        self.verticalLayout_frame_holder.addWidget(self.scroll_area)

        # main vertical layout
        self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
        self.verticalLayout_stack.setContentsMargins(15, 15, 15, 8)
        self.verticalLayout_stack.setSpacing(0)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # options frame
        self.frame_opts = QFrame(self.frame_holder)
        self.frame_opts.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_opts.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_opts.setObjectName("frame_opts")

        # layout for the options
        self.horizontalLayout_frame_opts = QHBoxLayout(self.frame_opts)
        self.horizontalLayout_frame_opts.setContentsMargins(0, 0, 0, 8)
        self.horizontalLayout_frame_opts.setSpacing(14)

        # left spacer
        self.spacer_opts_labels_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_opts.addItem(self.spacer_opts_labels_left)

        # run histogram button
        self.button_run_histogram = QPushButton(" Create Histogram", self.frame_opts)
        self.button_run_histogram.setObjectName("button_run_histogram")
        self.button_run_histogram.setIcon(QIcon(qta.icon("fa5s.chart-bar")))
        self.horizontalLayout_frame_opts.addWidget(self.button_run_histogram)

        # save results button
        self.button_save_results = QPushButton(" Save Results", self.frame_opts)
        self.button_save_results.setObjectName("button_save_results")
        self.button_save_results.setIcon(QIcon(qta.icon("fa5.save")))
        self.horizontalLayout_frame_opts.addWidget(self.button_save_results)

        # right spacer
        self.spacer_opts_labels_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_opts.addItem(self.spacer_opts_labels_right)

        # info button
        self.button_info = QPushButton("", self.frame_opts)
        self.button_info.setObjectName("button_info")
        self.button_info.setIcon(QIcon(qta.icon("fa.info-circle")))
        self.horizontalLayout_frame_opts.addWidget(self.button_info)

        # add the options frame to the vertical stack
        self.verticalLayout_stack.addWidget(self.frame_opts)

        # plot frame
        self.frame_plot = QFrame(self.frame_holder)
        self.frame_plot.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_plot.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_plot.setObjectName("frame_plot")
        self.verticalLayout_plot = QVBoxLayout(self.frame_plot)
        self.verticalLayout_plot.setContentsMargins(0, 8, 0, 0)
        self.verticalLayout_plot.setSpacing(8)

        # create a GraphicsLayoutWidget for the plot
        self.glw = pg.GraphicsLayoutWidget(parent=self.frame_plot)
        self.glw.setBackground('black')
        self.verticalLayout_plot.addWidget(self.glw)

        # add a PlotItem to the layout
        self.plot = self.glw.addPlot(row=0, col=0)
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setTitle("Histogram")
        self.plot.setLabel('bottom', 'Value')
        self.plot.setLabel('left', 'Count')

        # add to the layout
        self.verticalLayout_stack.addWidget(self.frame_plot, stretch=1)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # bindings
        self.button_run_histogram.clicked.connect(self.openOptionsDialog)
        self.button_save_results.clicked.connect(self.saveResults)
        self.button_info.clicked.connect(self.showHistogramInfo)

        return

    #----------------------------------------------#

    def showHistogramInfo(self):
        info_text = (
            "<h2>Histogram Plot Information</h2>"
            "<p>This tab allows for the creation of histograms to visualize the distribution of data in one or more columns.</p>"
            "<h3>Options</h3>"
            "<ul>"
            "<li><b>Select Columns:</b> Choose one or more numeric columns from your data to plot as histograms.</li>"
            "<li><b>Number of Bins:</b> Defines how many intervals (bars) the data range is divided into. More bins provide more detail but can be noisy.</li>"
            "<li><b>Use Density (Normalize):</b> If checked, the histogram is normalized to form a probability density. The area under the histogram will sum to 1. This is useful for comparing distributions of different sample sizes. If unchecked, the y-axis represents the raw count of values in each bin.</li>"
            "<li><b>Show KDE Plot:</b> If checked, a Kernel Density Estimate (KDE) line is plotted over the histogram. The KDE is a non-parametric way to estimate the probability density function of a random variable, providing a smoothed version of the distribution.</li>"
            "</ul>"
            "<h3>Interpreting the Plot</h3>"
            "<p>The histogram bars show the frequency of data points falling into specific ranges (bins). The overlaid KDE line, when enabled, provides a smooth curve that helps to visualize the underlying data distribution, making it easier to see patterns like skewness and modality. You can toggle the visibility of each plot by clicking its name in the legend.</p>"
        )
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Histogram Information")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(info_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStyleSheet("QLabel { min-width: 800px; }")
        msg_box.exec_()

    #----------------------------------------------#

    def openOptionsDialog(self):
        numeric_columns = self.dataframe.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_columns:
            QMessageBox.critical(self, "Error", "No numeric columns found in the dataframe to create a histogram.")
            return

        self.options_dialog = HistogramOptionsDialog(
            parent=self,
            global_parent=self,
            column_list=numeric_columns,
            default_bins=self.options.get("bins", 50),
            default_density=self.options.get("density", False),
            default_show_kde=self.options.get("show_kde", True)
        )
        self.options_dialog.exec_()
        return

    #----------------------------------------------#

    def runHistogramAfterDialog(self, options):
        self.options = options
        self.updatePlot()
        return

    #----------------------------------------------#

    def updatePlot(self):

        # clean up
        self.plot.clear()
        self.current_legend = self.plot.addLegend()
        self.histogram_data.clear()
        if not self.options or "selected_columns" not in self.options:
            return

        # get config
        selected_columns = self.options["selected_columns"]
        num_bins = self.options.get("bins", 50)
        is_density = self.options.get("density", False)
        show_kde = self.options.get("show_kde", False)

        # init colors
        colors = [
            (31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),
            (148, 103, 189), (140, 86, 75), (227, 119, 194), (127, 127, 127),
            (188, 189, 34), (23, 190, 207)
        ]

        # iterate over variables
        for i, col_name in enumerate(selected_columns):
            if col_name not in self.dataframe.columns: continue
            data = self.dataframe[col_name].dropna().values
            if data.size < 2: continue

            # run hist
            counts, bin_edges = np.histogram(data, bins=num_bins, density=is_density)
            self.histogram_data[col_name] = {'counts': counts, 'bin_edges': bin_edges}

            # config
            width = bin_edges[1] - bin_edges[0]
            color = colors[i % len(colors)]
            brush = pg.mkBrush(color=color + (150,))

            # bar graphs
            bar_item = pg.BarGraphItem(x=bin_edges[:-1], height=counts, width=width, brush=brush, name=col_name)
            self.plot.addItem(bar_item)

            # show kde line plot
            if show_kde:
                try:
                    kde = gaussian_kde(data)
                    x_vals = np.linspace(data.min(), data.max(), 500)
                    kde_vals = kde(x_vals)
                    if not is_density:
                        kde_vals = kde_vals * len(data) * width
                    kde_line_pen = pg.mkPen(color=color, width=2.5, style=Qt.PenStyle.SolidLine)
                    kde_name = f"KDE_{col_name}"
                    kde_item = pg.PlotDataItem(x=x_vals, y=kde_vals, pen=kde_line_pen, name=kde_name)
                    self.plot.addItem(kde_item)
                except Exception as e:
                    print(f"Could not compute KDE for column '{col_name}': {e}")

        # add to the plot
        y_label = "Density" if is_density else "Count"
        self.plot.setLabel('left', y_label)
        self.plot.setTitle(f"Histogram of Selected Columns (Bins: {num_bins})")
        self.plot.getViewBox().autoRange()
        self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        return

    #----------------------------------------------#

    def saveResults(self):

        # check data
        if not self.histogram_data:
            message_box = QMessageBox(QMessageBox.Icon.Critical, "Error", "No histogram data to save. Please run the analysis first.", parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            return

        # save the data
        try:
            save_name = f"{self.display_name}_histogram_results.hdf5" if self.display_name else "histogram_results.hdf5"
            name, _ = QFileDialog.getSaveFileName(self, "Save Histogram Data in HDF5 file", save_name, filter="HDF5 (*.hdf5)")
            if not name: return
            if not name.lower().endswith(".hdf5"): name += ".hdf5"
            with h5py.File(name, 'w') as hf:
                meta_group = hf.create_group("metadata")
                meta_group.attrs["bins"] = self.options.get("bins", 0)
                meta_group.attrs["density"] = self.options.get("density", False)

                data_group = hf.create_group("histogram_data")
                for col_name, data in self.histogram_data.items():
                    col_group = data_group.create_group(col_name)
                    col_group.create_dataset("counts", data=data['counts'])
                    col_group.create_dataset("bin_edges", data=data['bin_edges'])
            message_title = "Success"
            message_text = f"The histogram data has been successfully saved to:\n{name}"
            message_box = QMessageBox(QMessageBox.Icon.Information, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()

        # display error
        except Exception as xcp:
            message_title = "Error"
            message_text = f"Unable to save results due to the following exception:\n{xcp}"
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()

        return

    #----------------------------------------------#

    def closeEvent(self, evt):
        evt.accept()
        return

    #----------------------------------------------#

#################################################################
#################################################################