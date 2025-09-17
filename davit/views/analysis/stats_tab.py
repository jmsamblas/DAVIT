#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *

# SPECIFIC IMPORTS

from davit.utils.hdf5_save_dataframe import HDF5DataFrameHandler

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

class StatsOptionsDialog(QDialog):

    #----------------------------------------------#

    def __init__(self, parent=None, global_parent=None, default_plot_type="Bean Plot", default_analysis_type="Per Column", default_column_names="Ascending Numeric"):

        # init and attributes
        super().__init__(parent)
        self.global_parent = global_parent
        self.default_plot_type = default_plot_type
        self.default_analysis_type = default_analysis_type
        self.default_column_names = default_column_names

        # set title and icon
        self.setWindowTitle("Stats Options Dialog")
        self.setWindowIcon(qta.icon("fa5s.calculator"))

        # fixed size
        self.setFixedSize(420, 180)

        # build
        self.buildCodeWidgets()
        self.bindWidgets()

        # force plot type
        self._plotTypeChanged(self.default_plot_type)

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

        # plot type option
        self.label_plot_type = QLabel("Plot Type", parent=self.options_group)
        self.label_plot_type.setStyleSheet("font-weight: normal; color: black;")
        self.combobox_plot_type = QComboBox(self.options_group)
        self.combobox_plot_type.setStyleSheet("font-weight: normal;")
        self.combobox_plot_type.addItems(["Bean Plot", "Evolution", "None"])
        self.combobox_plot_type.setCurrentText(self.default_plot_type)
        self.grid_layout.addWidget(self.label_plot_type, 0, 0)
        self.grid_layout.addWidget(self.combobox_plot_type, 0, 1)

        # analysis type option
        self.label_analysis_type = QLabel("Analysis Type", parent=self.options_group)
        self.label_analysis_type.setStyleSheet("font-weight: normal; color: black;")
        self.combobox_analysis_type = QComboBox(self.options_group)
        self.combobox_analysis_type.setStyleSheet("font-weight: normal;")
        self.combobox_analysis_type.addItems(["Per Column", "All Columns"])
        self.combobox_analysis_type.setCurrentText(self.default_analysis_type)
        self.grid_layout.addWidget(self.label_analysis_type, 1, 0)
        self.grid_layout.addWidget(self.combobox_analysis_type, 1, 1)

        # column names option
        self.label_column_names = QLabel("Column Names", parent=self.options_group)
        self.label_column_names.setStyleSheet("font-weight: normal; color: black;")
        self.combobox_column_names = QComboBox(self.options_group)
        self.combobox_column_names.setStyleSheet("font-weight: normal;")
        self.combobox_column_names.addItems(["Ascending Numeric", "Original Names"])
        self.combobox_column_names.setCurrentText(self.default_column_names)
        self.grid_layout.addWidget(self.label_column_names, 2, 0)
        self.grid_layout.addWidget(self.combobox_column_names, 2, 1)

        # combo widths
        self.combobox_plot_type.setMinimumWidth(260)
        self.combobox_analysis_type.setMinimumWidth(260)
        self.combobox_column_names.setMinimumWidth(260)

        # vertical spacer
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

        # typical accept and reject bindings
        self.btn_yes.clicked.connect(self.accept)
        self.btn_no.clicked.connect(self.reject)

        # when "Evolution" is selected, disable analysis type and force "Per Column"
        self.combobox_plot_type.currentTextChanged.connect(self._plotTypeChanged)

        return

    #----------------------------------------------#

    def _plotTypeChanged(self, text):
        if text == "Evolution":
            self.combobox_analysis_type.setCurrentText("Per Column")
            self.combobox_analysis_type.setEnabled(False)
        else:
            self.combobox_analysis_type.setEnabled(True)
        return

    #----------------------------------------------#

    def accept(self):
        options = {
            "plot_type": self.combobox_plot_type.currentText(),
            "analysis_type": self.combobox_analysis_type.currentText(),
            "column_names": self.combobox_column_names.currentText()
        }
        if self.global_parent:
            self.global_parent.runStatsAfterDialog(options)
        super().accept()
        return

    #----------------------------------------------#

#################################################################
#################################################################

class StatsTab(QWidget):

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
        self.stats_results = {}
        self.df_stats = pd.DataFrame([])
        self.current_legend = None
        self.selected_plot_type = "Bean Plot"
        self.selected_analysis_type = "Per Column"
        self.column_names_option = "Ascending Numeric"
        self.global_stats = False
        self.max_points = 1000
        self.max_n_columns = 100

        # define the statistic names (row labels)
        self.stat_names = [
            "Count", "Missing (%)", "Mean", "Std", "Min", "25%", "50% (Median)", "75%", "Max",
            "Mode", "Skew", "Skewness Category", "Kurtosis", "Kurtosis Type",
            "IQR", "Range", "Variance", "CV (%)"
        ]

        # build up the layouts only when required
        if self.init_build:
            self.buildTab(self.dataframe)

        # apply style
        qss_path = os.path.join(self.app_root_path, "resources", "qss", "stats_tab.qss")
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

        # vertical layout
        self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
        self.verticalLayout_stack.setContentsMargins(15+8, 15, 15+8, 8)
        self.verticalLayout_stack.setSpacing(0)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # options frame
        self.frame_opts = QFrame(self.frame_holder)
        self.frame_opts.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_opts.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_opts.setObjectName("frame_opts")

        # layour for the options
        self.horizontalLayout_frame_opts = QHBoxLayout(self.frame_opts)
        self.horizontalLayout_frame_opts.setContentsMargins(0, 0, 0, 8)
        self.horizontalLayout_frame_opts.setSpacing(14)

        # left spacer
        self.spacer_opts_labels_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_opts.addItem(self.spacer_opts_labels_left)

        # run stats button
        self.button_run_stats = QPushButton(" Calculate Stats", self.frame_opts)
        self.button_run_stats.setObjectName("button_run_stats")
        self.button_run_stats.setIcon(QIcon(qta.icon("fa5s.calculator")))
        self.horizontalLayout_frame_opts.addWidget(self.button_run_stats)

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

        # create a QSplitter (vertical) for the Plot and Table
        self.splitter = QSplitter(Qt.Orientation.Vertical, self.frame_holder)
        self.verticalLayout_stack.addWidget(self.splitter, stretch=1)

        # plot frame (top part of the splitter)
        self.frame_plot = QFrame(self.splitter)
        self.frame_plot.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_plot.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_plot.setObjectName("frame_plot")
        self.verticalLayout_plot = QVBoxLayout(self.frame_plot)
        self.verticalLayout_plot.setContentsMargins(0, 15-8, 0, 15)
        self.verticalLayout_plot.setSpacing(8)

        # create a GraphicsLayoutWidget that will serve as the GraphicsView
        self.glw = pg.GraphicsLayoutWidget(parent=self.frame_plot)
        self.glw.setBackground('black')
        self.verticalLayout_plot.addWidget(self.glw)

        # add a PlotItem to the layout
        self.plot = self.glw.addPlot(row=0, col=0)
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setTitle("Stats Plot (Bean or Evolution)")
        self.plot.setLabel('left', 'Value')
        self.plot.setLabel('bottom', 'Column')

        # table frame (bottom part of the splitter)
        self.frame_results = QFrame(self.splitter)
        self.frame_results.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_results.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_results.setObjectName("frame_results")
        self.verticalLayout_results = QVBoxLayout(self.frame_results)
        self.verticalLayout_results.setContentsMargins(0, 8, 0, 15)
        self.verticalLayout_results.setSpacing(0)

        # add a centered title above the table
        self.label_table_title = QLabel("Statistics Table", self.frame_results)
        self.label_table_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_table_title.setStyleSheet("font-weight: bold;")
        self.verticalLayout_results.addWidget(self.label_table_title)

        # add a small spacer between the title and the table
        self.verticalLayout_results.addSpacing(8)

        # some opts
        include_error_list = True
        enable_column_options = True
        auto_resizing = True

        # create the DataFrameWidget for displaying the stats
        self.tableView = DataFrameWidget(parent=self.frame_results, df=pd.DataFrame([]), include_error_list=include_error_list, enable_column_options=enable_column_options, auto_resizing=auto_resizing)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.horizontalHeader().setMinimumSectionSize(50)
        self.verticalLayout_results.addWidget(self.tableView)
        self.tableView.setMinimumHeight(180)
        self.tableView.setMinimumWidth(320)

        # create and save an empty DataFrame with the above rows and initialize with zeros
        empty_df = pd.DataFrame(0, index=self.stat_names, columns=["Columns"])
        self.tableView.setDataFrame(empty_df)
        self.tableView.update()

        # set initial splitter sizes
        totalInitialHeight = 500
        self.splitter.setSizes([int(totalInitialHeight * 0.8), int(totalInitialHeight * 0.2)])

        # finally add a stretch at the end of the vertical layout
        self.verticalLayout_stack.addStretch()

    #----------------------------------------------#

    def bindWidgets(self):

        # bindings
        self.button_run_stats.clicked.connect(self.openOptionsDialog)
        self.button_save_results.clicked.connect(self.saveAnalysis)
        self.button_info.clicked.connect(self.showStatsInfo)

        return

    #----------------------------------------------#

    def showStatsInfo(self):
        info_text = (
                "<h2>Plot Information</h2>"
                "<p>The application provides two types of plots for data visualization: "
                "<b>Bean Plot</b> and <b>Evolution Plot</b>.</p>"
                "<h3>Bean Plot</h3>"
                "<ul>"
                "<li><b>KDE Outline:</b> The bean plot computes a Kernel Density Estimation (KDE) to outline the data density. "
                "The outline is drawn as two curves (on the left and right of a central axis) with a filled area between them.</li>"
                "<li><b>Data Points:</b> Individual data points are plotted with slight horizontal jitter for clarity. "
                "A maximum of " + str(self.max_points) + " points are displayed to maintain readability.</li>"
                "<li><b>Mean and Median Lines:</b> Horizontal dashed lines indicate the mean and the median.</li>"
                "</ul>"
                "<h3>Evolution Plot</h3>"
                "<ul>"
                "<li><b>Mean and Median Evolution:</b> For each numeric column, the mean and median are plotted as evolution lines "
                "across the columns.</li>"
                "<li><b>Error Bars:</b> The standard deviation is represented by error bars centered on the mean values.</li>"
                "<li><b>Shaded Area:</b> The area between the 25th and 75th percentiles is shaded to illustrate the inter-quartile range (IQR), "
                "highlighting the central spread of the data.</li>"
                "</ul>"
                "<h2>Statistics Table Information</h2>"
                "<p>The table displays various metrics computed on your dataset. "
                "Below is a detailed explanation of each statistic:</p>"
                "<ul>"
                "<li><b>Count:</b> The number of non-missing (non-NA/null) observations in the dataset or column.</li>"
                "<li><b>Missing (%):</b> The percentage of missing values within the dataset or column.</li>"
                "<li><b>Mean:</b> The arithmetic average of the values.</li>"
                "<li><b>Std:</b> The standard deviation, a measure of dispersion around the mean.</li>"
                "<li><b>Min:</b> The smallest value in the dataset or column.</li>"
                "<li><b>25%:</b> The 25th percentile, indicating that 25% of the data lies below this value.</li>"
                "<li><b>50% (Median):</b> The middle value when the data is sorted.</li>"
                "<li><b>75%:</b> The 75th percentile, showing that 75% of the data falls below this value.</li>"
                "<li><b>Max:</b> The largest value in the dataset or column.</li>"
                "<li><b>Mode:</b> The most frequently occurring value.</li>"
                "<li><b>Skew:</b> A measure of the asymmetry of the distribution around its mean. "
                "Values near zero indicate a symmetric distribution.</li>"
                "<li><b>Skewness Category:</b> Categorizes the skewness as 'Symmetric', 'Positively Skewed', or 'Negatively Skewed'.</li>"
                "<li><b>Kurtosis:</b> A measure of the heaviness of the tails of the distribution relative to a normal distribution.</li>"
                "<li><b>Kurtosis Type:</b> Categorizes the kurtosis as 'Mesokurtic' (normal tails), 'Leptokurtic' (heavier tails), "
                "or 'Platykurtic' (lighter tails).</li>"
                "<li><b>IQR:</b> The Inter-Quartile Range; the difference between the 75th and 25th percentiles, showing the spread of the middle 50% of the data.</li>"
                "<li><b>Range:</b> The difference between the maximum and minimum values.</li>"
                "<li><b>Variance:</b> The square of the standard deviation, indicating the degree of spread in the data.</li>"
                "<li><b>CV (%):</b> The Coefficient of Variation (expressed as a percentage), or the ratio of the standard deviation to the mean.</li>"
                "</ul>"
        )
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Detailed Statistics and Plot Information")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(info_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStyleSheet("QLabel { min-width: 800px; }")
        msg_box.exec_()

    #----------------------------------------------#

    def openOptionsDialog(self):
        self.options_dialog = StatsOptionsDialog(
            parent=self, global_parent=self,
            default_plot_type=self.selected_plot_type,
            default_analysis_type=self.selected_analysis_type,
            default_column_names=self.column_names_option
        )
        self.options_dialog.exec_()
        return

    #----------------------------------------------#

    def calculate_stats(self, data, stat_names, is_global=False):
        if is_global:
            series = data.dropna()
            if series.empty:
                return pd.DataFrame({"Info": ["No numeric data available."]})
            desc = series.describe(percentiles=[0.25, 0.5, 0.75])
            try:
                mode_val = series.mode().iloc[0]
            except Exception:
                mode_val = np.nan
            iqr = desc["75%"] - desc["25%"]
            value_range = series.max() - series.min()
            variance = series.var()
            cv = (series.std() / series.mean() * 100) if series.mean() != 0 else np.nan
            missing_pct = self.dataframe.isna().sum().sum() / (self.dataframe.shape[0] * self.dataframe.shape[1]) * 100
            kurt = series.kurtosis()
            if abs(kurt) < 0.1:
                kurt_type = "Mesokurtic"
            elif kurt > 0.1:
                kurt_type = "Leptokurtic"
            else:
                kurt_type = "Platykurtic"
            skew = series.skew()
            if abs(skew) < 0.1:
                skew_type = "Symmetric"
            elif skew > 0.1:
                skew_type = "Positively Skewed"
            else:
                skew_type = "Negatively Skewed"
            global_stats = {
                "Count": series.count(),
                "Missing (%)": missing_pct,
                "Mean": series.mean(),
                "Std": series.std(),
                "Min": series.min(),
                "25%": desc["25%"],
                "50% (Median)": desc["50%"],
                "75%": desc["75%"],
                "Max": series.max(),
                "Mode": mode_val,
                "Skew": skew,
                "Skewness Category": skew_type,
                "Kurtosis": kurt,
                "Kurtosis Type": kurt_type,
                "IQR": iqr,
                "Range": value_range,
                "Variance": variance,
                "CV (%)": cv
            }
            return pd.DataFrame(global_stats, index=["All Columns Stats"]).T
        else:
            numeric_df = data
            if numeric_df.empty:
                return pd.DataFrame({"Info": ["No numeric data available."]})
            desc = numeric_df.describe(percentiles=[0.25, 0.5, 0.75]).T
            modes, skew_dict, skew_cat, kurt_dict, kurt_cat = {}, {}, {}, {}, {}
            iqr_dict, range_dict, var_dict, cv_dict, missing_dict = {}, {}, {}, {}, {}
            for col in numeric_df.columns:
                series = numeric_df[col]
                try:
                    mode_val = series.mode().iloc[0]
                except Exception:
                    mode_val = np.nan
                modes[col] = mode_val
                skew_val = series.skew()
                skew_dict[col] = skew_val
                skew_cat[col] = "Symmetric" if abs(skew_val) < 0.1 else ("Positively Skewed" if skew_val > 0.1 else "Negatively Skewed")
                kurt_val = series.kurtosis()
                kurt_dict[col] = kurt_val
                kurt_cat[col] = "Mesokurtic" if abs(kurt_val) < 0.1 else ("Leptokurtic" if kurt_val > 0.1 else "Platykurtic")
                iqr_dict[col] = desc.loc[col, "75%"] - desc.loc[col, "25%"]
                range_dict[col] = series.max() - series.min()
                var_dict[col] = series.var()
                cv_dict[col] = (series.std() / series.mean() * 100) if series.mean() != 0 else np.nan
                missing_dict[col] = series.isna().sum() / series.shape[0] * 100
            stats_results = {
                "Count": numeric_df.count(),
                "Missing (%)": pd.Series(missing_dict),
                "Mean": numeric_df.mean(),
                "Std": numeric_df.std(),
                "Min": numeric_df.min(),
                "25%": desc["25%"],
                "50% (Median)": desc["50%"],
                "75%": desc["75%"],
                "Max": numeric_df.max(),
                "Mode": pd.Series(modes),
                "Skew": pd.Series(skew_dict),
                "Skewness Category": pd.Series(skew_cat),
                "Kurtosis": pd.Series(kurt_dict),
                "Kurtosis Type": pd.Series(kurt_cat),
                "IQR": pd.Series(iqr_dict),
                "Range": pd.Series(range_dict),
                "Variance": pd.Series(var_dict),
                "CV (%)": pd.Series(cv_dict)
            }
            return pd.DataFrame(stats_results).transpose()

    #----------------------------------------------#

    def runStatsAfterDialog(self, options):

        # config
        self.selected_plot_type = options["plot_type"]
        self.selected_analysis_type = options["analysis_type"]
        self.column_names_option = options["column_names"]
        if self.selected_plot_type == "Evolution":
            self.global_stats = False
        else:
            self.global_stats = (options["analysis_type"] == "All Columns")

        # check for non-numeric columns
        non_numeric = self.dataframe.select_dtypes(exclude=[np.number])
        if not non_numeric.empty:
            message_title = "Error"
            message_text = "Unable to run analysis because non-numeric columns were found."
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.calculator"))
            message_box.exec_()
            return

        # for Bean Plot, do not allow if over max_n_columns numeric columns
        numeric_df = self.dataframe.select_dtypes(include=[np.number]).astype(np.float64)
        if self.selected_plot_type == "Bean Plot" and self.selected_analysis_type != "All Columns" and numeric_df.shape[1] > self.max_n_columns:
            message_title = "Error"
            message_text = "Cannot display Bean Plot when over {} columns are present.".format(self.max_n_columns)
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.calculator"))
            message_box.exec_()
            return

        # for Evolution Plot, require at least 2 numeric columns
        if self.selected_plot_type == "Evolution" and numeric_df.shape[1] < 2:
            message_title = "Error"
            message_text = "Evolution plot requires at least 2 numeric columns."
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.calculator"))
            message_box.exec_()
            return

        # compute statistics
        if self.global_stats:
            if not numeric_df.empty:
                global_series = pd.Series(numeric_df.values.ravel())
                self.df_stats = self.calculate_stats(global_series, stat_names=self.stat_names, is_global=True)
            else:
                self.df_stats = pd.DataFrame({"Info": ["No numeric data available."]})
        else:
            if numeric_df.empty:
                self.df_stats = pd.DataFrame({"Info": ["No numeric data available."]})
            else:
                self.df_stats = self.calculate_stats(numeric_df, stat_names=self.stat_names, is_global=False)

        # update column names
        self.updateResultsDisplay()

        # clear the legend (just in case)
        if self.current_legend:
            self.current_legend.clear()

        # remove any existing legend if present
        if self.current_legend is not None:
            self.plot.removeItem(self.current_legend)
            self.current_legend = None

        # evolution plot
        if self.selected_plot_type == "Evolution":
            self.updateEvolutionPlot()

            # create a new evolution legend
            self.current_legend = self.plot.addLegend(offset=(10, 10), anchor=('right', 'top'))
            self.current_legend.mouseClickEvent = lambda ev: None
            self.current_legend.mouseDoubleClickEvent = lambda ev: None
            self.current_legend.mousePressEvent = lambda ev: None
            self.current_legend.mouseReleaseEvent = lambda ev: None
            self.current_legend.mouseDragEvent = lambda ev: None
            evo_pen_mean = pg.mkPen(color=(155, 255, 0), width=2, style=Qt.PenStyle.SolidLine)  # Cyan
            evo_pen_median = pg.mkPen(color=(0, 197, 255), width=2, style=Qt.PenStyle.SolidLine)  # Hot pink
            evo_pen_error = pg.mkPen(color=(200, 200, 200), width=1, style=Qt.PenStyle.SolidLine)  # Light gray
            evo_pen_fill = pg.mkPen(color=(150, 255, 244), width=0)  # dummy for fill legend
            dummy_evo_mean = pg.PlotDataItem([0], [0], pen=evo_pen_mean)
            dummy_evo_median = pg.PlotDataItem([0], [0], pen=evo_pen_median)
            dummy_evo_error = pg.PlotDataItem([0], [0], pen=evo_pen_error)
            dummy_evo_fill = pg.PlotDataItem([0], [0], pen=evo_pen_fill)
            self.current_legend.addItem(dummy_evo_mean, "Mean Evolution")
            self.current_legend.addItem(dummy_evo_median, "Median Evolution")
            self.current_legend.addItem(dummy_evo_error, "Std Error")
            self.current_legend.addItem(dummy_evo_fill, "Fill: 25th-75th Percentiles")

        # bean plot
        elif self.selected_plot_type == "Bean Plot":

            # update bean plot
            if self.global_stats:
                if not numeric_df.empty:
                    global_series = pd.Series(numeric_df.values.ravel())
                    self.updateBeanPlot(global_series, global_flag=True)
                else:
                    self.plot.clear()
            else:
                self.updateBeanPlot()

            # create a new bean plot legend
            self.current_legend = self.plot.addLegend(offset=(10, 10), anchor=('right', 'top'))
            self.current_legend.mouseClickEvent = lambda ev: None
            self.current_legend.mouseDoubleClickEvent = lambda ev: None
            self.current_legend.mousePressEvent = lambda ev: None
            self.current_legend.mouseReleaseEvent = lambda ev: None
            self.current_legend.mouseDragEvent = lambda ev: None
            bean_pen_mean = pg.mkPen(color=(155, 255, 0), width=2, style=Qt.PenStyle.DashLine)
            bean_pen_median = pg.mkPen(color=(0, 197, 255), width=2, style=Qt.PenStyle.DashLine)
            bean_pen_kde = pg.mkPen(color=(150, 255, 244), width=2, style=Qt.PenStyle.SolidLine)
            dummy_bean_mean = pg.PlotDataItem([0], [0], pen=bean_pen_mean)
            dummy_bean_median = pg.PlotDataItem([0], [0], pen=bean_pen_median)
            dummy_bean_kde = pg.PlotDataItem([0], [0], pen=bean_pen_kde)
            dummy_bean_scatter = pg.ScatterPlotItem([0], [0], pen=pg.mkPen(color=(255, 255, 255, 0), width=0), brush=pg.mkBrush(255, 255, 255, 200), size=5)
            self.current_legend.addItem(dummy_bean_mean, "Mean")
            self.current_legend.addItem(dummy_bean_median, "Median")
            self.current_legend.addItem(dummy_bean_kde, "KDE Outline")
            self.current_legend.addItem(dummy_bean_scatter, "Data Points (max {} pts)".format(self.max_points))

        # other
        else:

            # just clear
            self.plot.clear()

        # range and refresh
        self.plot.getViewBox().autoRange()
        self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        return

    #----------------------------------------------#

    def updateResultsDisplay(self):
        if self.df_stats.empty:
            self.tableView.setDataFrame(pd.DataFrame({"Info": ["No statistics computed."]}))
        else:
            if self.column_names_option == "Ascending Numeric" and not self.global_stats:
                new_columns = list(range(self.df_stats.shape[1]))
                self.df_stats.columns = new_columns
            self.tableView.setDataFrame(self.df_stats)
        self.tableView.update()
        self.tableView.show()
        return

    #----------------------------------------------#

    def _drawBean(self, data, x_center):

        # gaussian kde
        try:
            kde = gaussian_kde(data)
        except Exception:
            return
        data_min, data_max = np.min(data), np.max(data)
        grid = np.linspace(data_min, data_max, 100)
        density = kde(grid)
        width = 0.8

        # scale density to fit nicely in the plot relative to the bean width
        scale = width / (np.max(density) * 2)
        density_scaled = density * scale
        x_right = x_center + density_scaled
        x_left = x_center - density_scaled

        # draw KDE outline as two curves
        line_outline_right = pg.PlotCurveItem(x=x_right, y=grid, pen=pg.mkPen(color=(150, 255, 244), width=0, style=Qt.PenStyle.SolidLine))
        line_outline_left = pg.PlotCurveItem(x=x_left, y=grid, pen=pg.mkPen(color=(150, 255, 244), width=0, style=Qt.PenStyle.SolidLine))
        self.plot.addItem(line_outline_right)
        self.plot.addItem(line_outline_left)

        # fill area between curves
        fill_between = pg.FillBetweenItem(curve1=line_outline_right, curve2=line_outline_left, brush=pg.mkBrush(150, 255, 244, 80))
        self.plot.addItem(fill_between)

        # scatter points (limit to self.max_points)
        if len(data) > self.max_points:
            indices = np.linspace(0, len(data) - 1, self.max_points, dtype=int)
            data_sample = data[indices]
        else:
            data_sample = data
        jitter = np.random.uniform(-0.05, 0.05, size=len(data_sample))
        scatter_x = x_center + jitter
        scatter = pg.ScatterPlotItem(x=scatter_x, y=data_sample, pen=pg.mkPen(color=(255, 255, 255, 0), width=0), brush=pg.mkBrush(255, 250, 250, 200), size=5)
        self.plot.addItem(scatter)

        # horizontal dashed lines for mean and median
        mean_val = np.mean(data)
        median_val = np.median(data)
        mean_line = pg.PlotDataItem(x=[x_center - 0.3, x_center + 0.3], y=[mean_val, mean_val], pen=pg.mkPen(color=(155, 255, 0), width=2, style=Qt.PenStyle.DashLine))
        median_line = pg.PlotDataItem(x=[x_center - 0.3, x_center + 0.3], y=[median_val, median_val], pen=pg.mkPen(color=(0, 197, 255), width=2, style=Qt.PenStyle.DashLine))
        self.plot.addItem(mean_line)
        self.plot.addItem(median_line)

        return

    #----------------------------------------------#

    def updateBeanPlot(self, global_series=None, global_flag=False):

        # random seed for jittering
        np.random.seed(42)

        # clear
        self.plot.clear()

        # reset tickers
        self.plot.getAxis("bottom").setTicks(None)

        # update bean plot
        if global_flag:
            data = global_series.dropna().values if global_series is not None else []
            if len(data) == 0:
                return
            self._drawBean(data, x_center=1)
            if self.column_names_option == "Original Names":
                self.plot.getAxis('bottom').setTicks([[(1, "Global Stats")]])
            self.plot.setTitle("Bean Plot (Global)")
        else:
            numeric_df = self.dataframe.select_dtypes(include=[np.number]).astype(np.float64)
            if numeric_df.empty:
                return
            xticks = []
            for i, col in enumerate(numeric_df.columns):
                data = numeric_df[col].dropna().values
                if len(data) == 0:
                    continue
                x_center = i + 1
                self._drawBean(data, x_center)
                if self.column_names_option == "Original Names":
                    label = str(col)
                    xticks.append((x_center, label))
            if self.column_names_option == "Original Names":
                self.plot.getAxis('bottom').setTicks([xticks])
            self.plot.setTitle("Bean Plot (Per Column)")
        self.plot.setLabel('left', 'Value')
        self.plot.getViewBox().autoRange()

        return

    #----------------------------------------------#

    def updateEvolutionPlot(self):

        # clear and checks
        self.plot.clear()
        numeric_df = self.dataframe.select_dtypes(include=[np.number]).astype(np.float64)
        if numeric_df.empty:
            return

        # column check
        if numeric_df.shape[1] < 2:
            message_title = "Error"
            message_text = "Evolution plot requires at least 2 numeric columns."
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("fa5s.calculator"))
            message_box.exec_()
            return

        # reset tickers
        self.plot.getAxis("bottom").setTicks(None)

        # init
        x_vals = np.arange(1, len(numeric_df.columns) + 1)
        means = []
        medians = []
        stds = []
        perc25 = []
        perc75 = []
        labels = []

        # calculations
        for idx, col in enumerate(numeric_df.columns):
            data = numeric_df[col].dropna().values
            if len(data) == 0:
                continue
            means.append(np.mean(data))
            medians.append(np.median(data))
            stds.append(np.std(data))
            perc25.append(np.percentile(data, 25))
            perc75.append(np.percentile(data, 75))
            if self.column_names_option == "Original Names":
                labels.append(str(col))

        # convert to arrays
        x_vals = np.array(x_vals[:len(means)])
        means = np.array(means)
        medians = np.array(medians)
        stds = np.array(stds)
        perc25 = np.array(perc25)
        perc75 = np.array(perc75)

        # plot evolution lines for mean and median
        mean_evo = pg.PlotCurveItem(x=x_vals, y=means, pen=pg.mkPen(color=(155, 255, 0), width=2, style=Qt.PenStyle.DashLine))
        median_evo = pg.PlotCurveItem(x=x_vals, y=medians, pen=pg.mkPen(color=(0, 197, 255), width=2, style=Qt.PenStyle.DashLine))
        self.plot.addItem(mean_evo)
        self.plot.addItem(median_evo)

        # plot error bars for std
        error_bars = pg.ErrorBarItem(x=x_vals, y=means, top=stds, bottom=stds, beam=0.2, pen=pg.mkPen(color=(200, 200, 200), width=1))
        self.plot.addItem(error_bars)

        # shade area between 25th and 75th percentiles
        perc25_curve = pg.PlotCurveItem(x=x_vals, y=perc25, pen=pg.mkPen(color=(150, 255, 244), width=0))
        perc75_curve = pg.PlotCurveItem(x=x_vals, y=perc75, pen=pg.mkPen(color=(150, 255, 244), width=0))
        self.plot.addItem(perc25_curve)
        self.plot.addItem(perc75_curve)
        fill_between = pg.FillBetweenItem(curve1=perc25_curve, curve2=perc75_curve, brush=pg.mkBrush(150, 255, 244, 80))
        self.plot.addItem(fill_between)

        # if Original Names are selected then apply custom tick labels
        if self.column_names_option == "Original Names":
            ticks = list(zip(x_vals, labels))
            self.plot.getAxis('bottom').setTicks([ticks])

        # otherwise do nothing so that the numeric axis displays auto-generated tick values
        self.plot.setTitle("Evolution Plot")
        self.plot.setLabel('left', 'Value')

        # auto range
        self.plot.getViewBox().autoRange()

        return

    #----------------------------------------------#

    def saveAnalysis(self):

        # check
        if self.df_stats.empty:
            message_title = "Error"
            message_text = "Unable to save analysis: No statistics computed."
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            return

        # try catch block
        try:

            # initialize default save name based on display_name if provided
            if self.display_name:
                save_name = self.display_name + "_stats_analysis_results.hdf5"
            else:
                save_name = "stats_analysis_results.hdf5"

            # ask the user for a save location and file name
            name, _ = QFileDialog.getSaveFileName(self, "Save analysis in HDF5 file", save_name, filter="HDF5(*.hdf5)")
            if not name:
                return
            if name[-5:].lower() != ".hdf5":
                name = name + ".hdf5"

            # use the HDF5DataFrameHandler approach to write the dataframe to HDF5
            handler = HDF5DataFrameHandler(name)
            with h5py.File(name, 'w') as h5_file:
                stats_group = h5_file.create_group("stats")
                stats_group.attrs["data_type"] = "DataFrame"
                cols_as_str = np.array([str(c) for c in self.df_stats.columns], dtype="S")
                stats_group.create_dataset("columns", data=cols_as_str)
                index = self.df_stats.index
                is_timestamp = False
                if isinstance(index, pd.DatetimeIndex):
                    index = handler.time_index_to_string(index)
                    is_timestamp = True
                else:
                    index = np.array([str(idx) for idx in index], dtype="S")
                idx_ds = stats_group.create_dataset("index", data=index)
                idx_ds.attrs["IS_TIMESTAMP"] = is_timestamp
                data_as_str = np.array(self.df_stats.values, dtype="S")
                stats_group.create_dataset("data", data=data_as_str)

            # show success message
            message_title = "Success"
            message_text = f"The analysis has been successfully saved to:\n{name}"
            message_box = QMessageBox(QMessageBox.Icon.Information, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()

        # error
        except Exception as xcp:
            message_title = "Error"
            message_text = "Unable to save analysis due to the following exception:\n{}".format(xcp)
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################