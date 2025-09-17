#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.utils.selection_cart_table_model import SelectionCartTableModel
from davit.views.visualization.main_visualization import MainVisualization

# SPECIFIC IMPORTS

from davit.utils.hdf5_save_dataframe import HDF5DataFrameHandler

#################################################################
#################################################################

class OptionsCell(QWidget):

    def __init__(self, key, global_parent):
        super().__init__()
        self.setStyleSheet("""
            QPushButton { text-align: center; }
            #button1 { background-color: #C2C8EC; }
            #button2 { background-color: #C2ECEC; }
            #button3 { background-color: #C8ECC2; }
            #button4 { background-color: #ECC2C2; }
        """)
        self.key = key
        self.global_parent = global_parent
        self.button_icons = ["transpose.png", 'mdi.code-brackets', 'mdi.magnify', 'mdi.delete']
        self.button_funcs = [self.transpose, self.slice, self.visualize, self.remove]
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        for i in range(4):
            button = self.create_button(i)
            button.setObjectName(f'button{i+1}')
            layout.addWidget(button)
        self.setLayout(layout)

    def create_button(self, idx):
        button = QPushButton('')
        button.setFixedSize(20, 20)
        if idx == 0:
            button.setIcon(QIcon(os.path.join(self.global_parent.app_root_path, "resources", "icons", self.button_icons[idx])))
        else:
            button.setIcon(qta.icon(self.button_icons[idx]))
        button.clicked.connect(lambda: self.button_funcs[idx](self.key))
        return button

    def transpose(self, key):
        self.global_parent.transposeDf(key_list=[key])

    def slice(self, key):
        self.global_parent.sliceDf(key=key)

    def visualize(self, key):
        self.global_parent.visualizeDf(df=None, key=key)

    def remove(self, key):
        self.global_parent.removeDf(key_list=[key])

#################################################################
#################################################################

class SliceDialog(QDialog):

    def __init__(self, key, row, df, df_before_slicing, parent=None, global_parent=None):
        super().__init__(parent)
        self.key = key
        self.row = row
        self.global_parent = global_parent
        if df_before_slicing:
            self.df, row_from, row_to, row_step, col_from, col_to, col_step, reset_index = df_before_slicing
        else:
            self.df = df
            row_from, row_to, row_step = 0, self.df.shape[0], 1
            col_from, col_to, col_step = 0, self.df.shape[1], 1
            reset_index = True
        self.setWindowTitle("Slice Panel")
        self.setWindowIcon(qta.icon("mdi.code-brackets"))
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel(""), 0, 0)
        grid_layout.addWidget(QLabel("<b>From</b>", self), 0, 1)
        grid_layout.addWidget(QLabel("<b>To</b>", self), 0, 2)
        grid_layout.addWidget(QLabel("<b>Step</b>", self), 0, 3)
        grid_layout.addWidget(QLabel("<b>Rows</b>", self), 1, 0)
        self.row_from_spinbox = self.create_spinbox(0, self.df.shape[0] - 1, row_from)
        self.row_to_spinbox = self.create_spinbox(0, self.df.shape[0], row_to)
        self.row_step_spinbox = self.create_spinbox(1, self.df.shape[0], row_step)
        grid_layout.addWidget(self.row_from_spinbox, 1, 1)
        grid_layout.addWidget(self.row_to_spinbox, 1, 2)
        grid_layout.addWidget(self.row_step_spinbox, 1, 3)
        grid_layout.addWidget(QLabel("<b>Cols</b>", self), 2, 0)
        self.col_from_spinbox = self.create_spinbox(0, self.df.shape[1] - 1, col_from)
        self.col_to_spinbox = self.create_spinbox(0, self.df.shape[1], col_to)
        self.col_step_spinbox = self.create_spinbox(1, self.df.shape[1], col_step)
        grid_layout.addWidget(self.col_from_spinbox, 2, 1)
        grid_layout.addWidget(self.col_to_spinbox, 2, 2)
        grid_layout.addWidget(self.col_step_spinbox, 2, 3)
        grid_layout.addWidget(QLabel(""), 3, 0)
        self.rebuild_index_checkbox = QCheckBox("Reset index", self)
        self.rebuild_index_checkbox.setChecked(reset_index)
        grid_layout.addWidget(self.rebuild_index_checkbox, 3, 1)
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(self.reject)
        grid_layout.addWidget(cancel_button, 3, 2)
        slice_button = QPushButton("Slice", self)
        slice_button.setDefault(True)
        slice_button.clicked.connect(self.slice_dataframe)
        grid_layout.addWidget(slice_button, 3, 3)
        self.setLayout(grid_layout)
        self.setFixedSize(self.sizeHint())

    def create_spinbox(self, minimum, maximum, default_value):
        spinbox = QSpinBox(self)
        spinbox.setMinimum(minimum)
        spinbox.setMaximum(maximum)
        spinbox.setValue(default_value)
        return spinbox

    def slice_dataframe(self):
        row_from = self.row_from_spinbox.value()
        row_to = self.row_to_spinbox.value()
        row_step = self.row_step_spinbox.value()
        col_from = self.col_from_spinbox.value()
        col_to = self.col_to_spinbox.value()
        col_step = self.col_step_spinbox.value()
        if row_from >= row_to or col_from >= col_to or row_step <= 0 or col_step <= 0:
            QMessageBox.warning(self, "Error", "Invalid slice parameters!")
            return
        config_tuple_to_save = (self.df.copy(), row_from, row_to, row_step, col_from, col_to, col_step, self.rebuild_index_checkbox.isChecked())
        self.global_parent.table_model_cart.update_data(self.row, self.global_parent.column_names_cart.index("DfBeforeSlicing"), config_tuple_to_save)
        sliced_df = self.df.iloc[row_from:row_to:row_step, col_from:col_to:col_step]
        if self.rebuild_index_checkbox.isChecked():
            sliced_df.reset_index(drop=True, inplace=True)
        self.global_parent.table_model_cart.update_data(self.row, self.global_parent.column_names_cart.index("New Shape"), str(sliced_df.shape))
        self.global_parent.table_model_cart.update_data(self.row, self.global_parent.column_names_cart.index("Df"), sliced_df)
        self.accept()
        return

#################################################################
#################################################################

class MainSelection(QWidget):

    #----------------------------------------------#

    def __init__(self, app, app_root_path = None, window_icon_path = None, qta_str_icon = "", parent = None, global_parent = None):

        # inherit from QWidget
        QWidget.__init__(self)

        # main attributes
        self.app = app
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.qta_str_icon = qta_str_icon
        self.parent = parent
        self.global_parent = global_parent

        # VERY IMPORTANT!
        # IF YOU WANT TO ADD A METADATA VARIABLE IN THE TABLE (A VARIABLE THAT IS IN THE MODEL BUT NOT DISPLAYED)
        # YOU HAVE TO UPDATE BOTH: self.number_of_metadata_columns AND self.column_names_cart

        # own attributes
        self.row_height = 25
        self.minimum_column_width = 110
        self.n_populated_rows = 0
        self.init_n_rows = 100
        self.number_of_metadata_columns = 4
        self.column_names_cart = ["Dataset Name", "Original Shape", "Options", "New Shape", "Path", "Source", "Index Type", "Key", "Df", "DfBeforeSlicing", "ChunkSize"]
        self.column_names_result = ["Name",  "Shape", "Index Type"]
        self.last_stored_width_cart = 0
        self.last_stored_width_result = 0
        self.menu_right_click_dict = {}

        # very important variables
        self.result_df = pd.DataFrame([])

        # main widgets
        self.tableView_cart = None
        self.tableView_result = None

        # get widths
        self.header_labels_widths_cart = [getPixelWidthFromQLabel(i, offset=35) for i in self.column_names_cart]
        self.header_labels_widths_result = [getPixelWidthFromQLabel(i, offset=35) for i in self.column_names_result]

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "main_selection.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # set scroll area (to make widget resizable)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.Box)
        self.scroll_area.setFrameShadow(QFrame.Shadow.Sunken)

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
        self.horizontalLayout_stack = QHBoxLayout(self.frame_holder)
        self.horizontalLayout_stack.setContentsMargins(8, 8, 8, 8)
        self.horizontalLayout_stack.setSpacing(8)
        self.horizontalLayout_stack.setObjectName("horizontalLayout_stack")

        # frame for the selection
        self.frame_1 = QFrame(self.frame_holder)
        self.frame_1.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_1.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_1.setObjectName("frame_1")
        self.horizontalLayout_stack.addWidget(self.frame_1)

        # frame for the options
        self.frame_2 = QFrame(self.frame_holder)
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_stack.addWidget(self.frame_2)

        # vertical layout for the selection
        self.verticalLayout_frame_1 = QVBoxLayout(self.frame_1)
        self.verticalLayout_frame_1.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_frame_1.setSpacing(0)
        self.verticalLayout_frame_1.setObjectName("verticalLayout_frame_1")

        # vertical layout for the options
        self.verticalLayout_frame_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_frame_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_frame_2.setSpacing(0)
        self.verticalLayout_frame_2.setObjectName("verticalLayout_frame_2")

        # groupbox for the table or selection panel
        self.groupbox_selection_panel = QGroupBox(self.frame_1)
        self.groupbox_selection_panel.setObjectName("groupbox_selection_panel")
        self.groupbox_selection_panel.setTitle("Selection Cart")
        self.groupbox_selection_panel.setStyleSheet("QGroupBox{font-weight: bold;}")
        self.verticalLayout_frame_1.addWidget(self.groupbox_selection_panel)

        # layout for the selection panel
        self.verticalLayout_selection_panel = QVBoxLayout(self.groupbox_selection_panel)
        self.verticalLayout_selection_panel.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_selection_panel.setSpacing(8)
        self.verticalLayout_selection_panel.setObjectName("verticalLayout_selection_panel")

        # create table
        self.tableView_cart = QTableView(self.groupbox_selection_panel)
        self.tableView_cart.setFrameShape(QFrame.Shape.StyledPanel)
        self.tableView_cart.setWordWrap(False)
        self.tableView_cart.setFrameShadow(QFrame.Shadow.Plain)
        self.tableView_cart.setDragEnabled(False)
        self.tableView_cart.setAlternatingRowColors(False)
        self.tableView_cart.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView_cart.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tableView_cart.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView_cart.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_cart.setShowGrid(True)
        self.tableView_cart.setGridStyle(Qt.PenStyle.SolidLine)
        self.tableView_cart.setObjectName("tableView_cart")
        self.tableView_cart.horizontalHeader().setVisible(True)
        self.tableView_cart.horizontalHeader().setHighlightSections(False)
        self.tableView_cart.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_cart.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tableView_cart.horizontalHeader().setStretchLastSection(True)
        self.tableView_cart.horizontalHeader().setMinimumSectionSize(self.minimum_column_width)
        self.tableView_cart.horizontalHeader().setFixedHeight(self.row_height)
        self.tableView_cart.verticalHeader().setVisible(True)
        self.tableView_cart.verticalHeader().setHighlightSections(False)
        self.tableView_cart.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_cart.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView_cart.verticalHeader().setStretchLastSection(False)
        self.tableView_cart.verticalHeader().setMinimumSectionSize(self.row_height)
        self.tableView_cart.verticalHeader().setDefaultSectionSize(self.row_height)
        self.verticalLayout_selection_panel.addWidget(self.tableView_cart)

        # add separation line
        self.separation_line = QHSeparationLine()
        self.verticalLayout_selection_panel.addWidget(self.separation_line)

        # create table
        self.tableView_result = QTableView(self.groupbox_selection_panel)
        self.tableView_result.setMinimumHeight(2.3*self.row_height)
        self.tableView_result.setFrameShape(QFrame.Shape.StyledPanel)
        self.tableView_result.setWordWrap(False)
        self.tableView_result.setFrameShadow(QFrame.Shadow.Plain)
        self.tableView_result.setDragEnabled(False)
        self.tableView_result.setAlternatingRowColors(False)
        self.tableView_result.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView_result.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tableView_result.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView_result.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_result.setShowGrid(True)
        self.tableView_result.setGridStyle(Qt.PenStyle.SolidLine)
        self.tableView_result.setObjectName("tableView_result")
        self.tableView_result.horizontalHeader().setVisible(True)
        self.tableView_result.horizontalHeader().setHighlightSections(False)
        self.tableView_result.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_result.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tableView_result.horizontalHeader().setStretchLastSection(True)
        self.tableView_result.horizontalHeader().setMinimumSectionSize(self.minimum_column_width)
        self.tableView_result.horizontalHeader().setFixedHeight(self.row_height)
        self.tableView_result.verticalHeader().setVisible(False)
        self.tableView_result.verticalHeader().setHighlightSections(False)
        self.tableView_result.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView_result.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView_result.verticalHeader().setStretchLastSection(False)
        self.tableView_result.verticalHeader().setMinimumSectionSize(self.row_height)
        self.tableView_result.verticalHeader().setDefaultSectionSize(self.row_height)
        self.verticalLayout_selection_panel.addWidget(self.tableView_result)

        # final stretches
        self.verticalLayout_selection_panel.setStretch(0, 99)
        self.verticalLayout_selection_panel.setStretch(1, 1)
        self.verticalLayout_selection_panel.setStretch(2, 1)

        # frame for the options
        self.groupbox_frame_options = QGroupBox(self.frame_2)
        self.groupbox_frame_options.setTitle("Options")
        self.groupbox_frame_options.setStyleSheet("QGroupBox{font-weight: bold;}")
        self.groupbox_frame_options.setObjectName("frame_options")
        self.verticalLayout_frame_2.addWidget(self.groupbox_frame_options)

        # layout for the options
        self.verticalLayout_frame_options = QVBoxLayout(self.groupbox_frame_options)
        self.verticalLayout_frame_options.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_frame_options.setSpacing(8)
        self.verticalLayout_frame_options.setObjectName("verticalLayout_frame_options")

        # groupbox foor the selection options
        self.groupbox_selection_options = QGroupBox(self.groupbox_frame_options)
        self.groupbox_selection_options.setObjectName("groupbox_selection_options")
        self.groupbox_selection_options.setTitle("Selection")
        self.groupbox_selection_options.setStyleSheet("QGroupBox{font-weight: bold;}")
        self.verticalLayout_frame_options.addWidget(self.groupbox_selection_options)

        # layout for the groupbox
        self.gridLayout_groupbox_selection_options = QGridLayout(self.groupbox_selection_options)
        self.gridLayout_groupbox_selection_options.setContentsMargins(8, 8, 8, 8)
        self.gridLayout_groupbox_selection_options.setSpacing(6)
        self.gridLayout_groupbox_selection_options.setObjectName("gridLayout_groupbox_selection_options")

        # button for adding the selected items from the tree view
        self.button_add_selected = QPushButton(self.groupbox_selection_options)
        self.button_add_selected.setObjectName("button_add_selected")
        self.button_add_selected.setText("Add Selected Items")
        self.button_add_selected.setStyleSheet("QPushButton{ background-color: #A9DEAE; text-align: center;}")
        self.gridLayout_groupbox_selection_options.addWidget(self.button_add_selected, 0, 0)

        # button for transposing all elements
        self.button_transpose_all = QPushButton(self.groupbox_selection_options)
        self.button_transpose_all.setObjectName("button_transpose_all")
        self.button_transpose_all.setText("Transpose All Items")
        self.button_transpose_all.setStyleSheet("QPushButton{ background-color: #C2C8EC; text-align: center;}")
        self.gridLayout_groupbox_selection_options.addWidget(self.button_transpose_all, 1, 0)

        # button for removing all the cart
        self.button_clean_up_selection = QPushButton(self.groupbox_selection_options)
        self.button_clean_up_selection.setObjectName("button_clean_up_selection")
        self.button_clean_up_selection.setText("Clean Up Selection")
        self.button_clean_up_selection.setStyleSheet("QPushButton{ background-color: #DEB8A9; text-align: center;}")
        self.gridLayout_groupbox_selection_options.addWidget(self.button_clean_up_selection, 2, 0)

        # groupbox foor the merging options
        self.groupbox_merging_options = QGroupBox(self.groupbox_frame_options)
        self.groupbox_merging_options.setObjectName("groupbox_merging_options")
        self.groupbox_merging_options.setTitle("Merging")
        self.groupbox_merging_options.setStyleSheet("QGroupBox{font-weight: bold;}")
        self.verticalLayout_frame_options.addWidget(self.groupbox_merging_options)

        # layout for the groupbox
        self.gridLayout_groupbox_merging_options = QGridLayout(self.groupbox_merging_options)
        self.gridLayout_groupbox_merging_options.setContentsMargins(8, 8, 8, 8)
        self.gridLayout_groupbox_merging_options.setSpacing(6)
        self.gridLayout_groupbox_merging_options.setObjectName("gridLayout_groupbox_merging_options")

        # label for the method
        self.label_merging_method = QLabel(self.groupbox_merging_options)
        self.label_merging_method.setObjectName("label_merging_method")
        self.label_merging_method.setText("Method")
        self.label_merging_method.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_groupbox_merging_options.addWidget(self.label_merging_method, 0, 0)

        # combobox for the method
        self.combobox_merging_method = QComboBox(self.groupbox_merging_options)
        self.combobox_merging_method.setObjectName("combobox_merging_method")
        self.model_combobox_merging_method = self.combobox_merging_method.model()
        for row in ["pd.concat"]:
            self.model_combobox_merging_method.appendRow(QStandardItem(str(row)))
        self.combobox_merging_method.setModel(self.model_combobox_merging_method)
        self.combobox_merging_method.setItemDelegate(QStyledItemDelegate())
        self.combobox_merging_method.setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in ["pd.concat"]]))
        self.combobox_merging_method.setCurrentIndex(0)
        self.gridLayout_groupbox_merging_options.addWidget(self.combobox_merging_method, 0, 1)

        # label for the axis
        self.label_merging_axis = QLabel(self.groupbox_merging_options)
        self.label_merging_axis.setObjectName("label_merging_axis")
        self.label_merging_axis.setText("Axis")
        self.label_merging_axis.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_groupbox_merging_options.addWidget(self.label_merging_axis, 1, 0)

        # combobox for the axis
        self.combobox_merging_axis = QComboBox(self.groupbox_merging_options)
        self.combobox_merging_axis.setObjectName("combobox_merging_axis")
        self.model_combobox_merging_axis = self.combobox_merging_axis.model()
        for row in ["0 : rows", "1 : columns"]:
            self.model_combobox_merging_axis.appendRow(QStandardItem(str(row)))
        self.combobox_merging_axis.setModel(self.model_combobox_merging_axis)
        self.combobox_merging_axis.setItemDelegate(QStyledItemDelegate())
        self.combobox_merging_axis.setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in ["0 : rows", "1 : columns"]]))
        self.combobox_merging_axis.setCurrentIndex(1)
        self.gridLayout_groupbox_merging_options.addWidget(self.combobox_merging_axis, 1, 1)

        # label for the ignore index
        self.label_merging_ignore_index = QLabel(self.groupbox_merging_options)
        self.label_merging_ignore_index.setObjectName("label_merging_ignore_index")
        self.label_merging_ignore_index.setText("Ignore Index")
        self.label_merging_ignore_index.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_groupbox_merging_options.addWidget(self.label_merging_ignore_index, 2, 0)

        # combobox for the ignore index
        self.combobox_merging_ignore_index = QComboBox(self.groupbox_merging_options)
        self.combobox_merging_ignore_index.setObjectName("combobox_merging_ignore_index")
        self.model_combobox_merging_ignore_index = self.combobox_merging_ignore_index.model()
        for row in ["False", "True"]:
            self.model_combobox_merging_ignore_index.appendRow(QStandardItem(str(row)))
        self.combobox_merging_ignore_index.setModel(self.model_combobox_merging_ignore_index)
        self.combobox_merging_ignore_index.setItemDelegate(QStyledItemDelegate())
        self.combobox_merging_ignore_index.setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in ["False", "True"]]))
        self.combobox_merging_ignore_index.setCurrentIndex(0)
        self.gridLayout_groupbox_merging_options.addWidget(self.combobox_merging_ignore_index, 2, 1)

        # label for the join argument
        self.label_merging_join_arg = QLabel(self.groupbox_merging_options)
        self.label_merging_join_arg.setObjectName("label_merging_join_arg")
        self.label_merging_join_arg.setText("Join")
        self.label_merging_join_arg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_groupbox_merging_options.addWidget(self.label_merging_join_arg, 3, 0)

        # combobox for the join argument
        self.combobox_merging_join_arg = QComboBox(self.groupbox_merging_options)
        self.combobox_merging_join_arg.setObjectName("combobox_merging_join_arg")
        self.model_combobox_merging_join_arg = self.combobox_merging_join_arg.model()
        for row in ["outer", "inner"]:
            self.model_combobox_merging_join_arg.appendRow(QStandardItem(str(row)))
        self.combobox_merging_join_arg.setModel(self.model_combobox_merging_join_arg)
        self.combobox_merging_join_arg.setItemDelegate(QStyledItemDelegate())
        self.combobox_merging_join_arg.setMinimumWidth(max([getPixelWidthFromQLabel(i, offset=30) for i in ["outer", "inner"]]))
        self.combobox_merging_join_arg.setCurrentIndex(0)
        self.gridLayout_groupbox_merging_options.addWidget(self.combobox_merging_join_arg, 3, 1)

        # button to apply the merging
        self.button_apply_merging = QPushButton(self.groupbox_merging_options)
        self.button_apply_merging.setObjectName("button_apply_merging")
        self.button_apply_merging.setText("Apply")
        self.button_apply_merging.setStyleSheet("QPushButton{ background-color: #A9DEAE; text-align: center;}")
        self.gridLayout_groupbox_merging_options.addWidget(self.button_apply_merging, 4, 1)

        # spacer item
        self.spacer_frame_options_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_frame_options.addItem(self.spacer_frame_options_2)

        # final stretches
        self.horizontalLayout_stack.setStretch(0, 95)
        self.horizontalLayout_stack.setStretch(1, 5)

        # init the tables
        self.initTables()

        return

    #----------------------------------------------#

    def addSelected(self):

        # only if global parent exists
        if self.global_parent:

            # get current index
            tab_index = self.global_parent.tabWidget_left.currentIndex()

            # CASE 1: HDF5
            if tab_index == 0:

                # get the items
                df_list, metadata_list, chunk_size_list = self.global_parent.treeView_hdf5.getItemsForSelectionPanel()
                self.addRows(df_list, metadata_list, chunk_size_list)

            # CASE 2: NXCALS
            elif tab_index == 1:

                # get the items
                df_list, metadata_list, chunk_size_list = self.global_parent.treeView_nxcals.getItemsForSelectionPanel()
                self.addRows(df_list, metadata_list, chunk_size_list)

            # CASE 3: PostMortem
            elif tab_index == 2:

                # get the items
                df_list, metadata_list, chunk_size_list = self.global_parent.treeView_postmortem.getItemsForSelectionPanel()
                self.addRows(df_list, metadata_list, chunk_size_list)

        return

    #----------------------------------------------#

    def addRows(self, df_list, metadata_list, chunk_size_list):

        # get the data
        data = self.table_model_cart._data

        # iterate over dfs
        for c_df, df in enumerate(df_list):
            if self.n_populated_rows < self.init_n_rows:
                data[self.n_populated_rows] = metadata_list[c_df] + [self.n_populated_rows, df, None, chunk_size_list[c_df]]
            else:
                data.append(metadata_list[c_df] + [self.n_populated_rows, df, None, chunk_size_list[c_df]])
            self.n_populated_rows += 1

        # set model
        self.table_model_cart = SelectionCartTableModel(data = data, header_labels = self.column_names_cart, result_table = False, number_of_metadata_columns = self.number_of_metadata_columns)
        self.tableView_cart.setModel(self.table_model_cart)
        self.tableView_cart.update()
        self.tableView_cart.show()

        # DRAWING OPTIONS BUTTON IS VERY INEFFICIENT (DELEGATES ARE BETTER BUT WAY MORE GOOFY)
        i_opts = self.column_names_cart.index("Options")
        i_key = self.column_names_cart.index("Key")
        for row in range(len(data)):
            if data[row][1] != "":
                self.tableView_cart.setIndexWidget(self.table_model_cart.index(row, i_opts), OptionsCell(self.table_model_cart.index(row, i_key).data(), global_parent=self))
            else:
                break

        return

    #----------------------------------------------#

    def resizeTable(self, tableView, header_labels, header_labels_widths, width, parent = None, stretch_last_column = False, offset = 50):

        # resize columns
        minimum_width = round((width-offset) / len(header_labels))
        for c in range(0, len(header_labels)):
            if header_labels_widths[c] > minimum_width:
                width_to_set = header_labels_widths[c]
            else:
                width_to_set = minimum_width
            tableView.setColumnWidth(c, width_to_set)

        return

    #----------------------------------------------#

    def initTables(self):

        # init data
        data = []
        for i in range(0,self.init_n_rows):
            data.append([""]*(len(self.column_names_cart)-self.number_of_metadata_columns) + [None, pd.DataFrame(), None, None])

        # set model
        self.table_model_cart = SelectionCartTableModel(data = data, header_labels = self.column_names_cart, result_table = False, number_of_metadata_columns = self.number_of_metadata_columns)
        self.tableView_cart.setModel(self.table_model_cart)
        self.tableView_cart.update()

        # show the table
        self.tableView_cart.show()

        # hide meta columns
        self.tableView_cart.hideColumn(self.column_names_cart.index("Key"))
        self.tableView_cart.hideColumn(self.column_names_cart.index("Df"))
        self.tableView_cart.hideColumn(self.column_names_cart.index("DfBeforeSlicing"))
        self.tableView_cart.hideColumn(self.column_names_cart.index("ChunkSize"))

        # set model
        self.table_model_result = SelectionCartTableModel(data=[[""]*len(self.column_names_result)], header_labels=self.column_names_result, result_table = True)
        self.tableView_result.setModel(self.table_model_result)
        self.tableView_result.update()

        # show the table
        self.tableView_result.show()

        return

    #----------------------------------------------#

    def applyMerging(self):

        # retrieve df list
        i = self.column_names_cart.index("Df")
        df_list = [row[i] for row in self.table_model_cart._data if not row[i].empty]

        # only if we have some dfs
        if df_list:

            # get method
            pandas_method = self.combobox_merging_method.currentText()

            # get axis
            axis = int(self.combobox_merging_axis.currentText().split(":")[0].strip())

            # get ignore index
            if self.combobox_merging_ignore_index.currentText() == "True":
                ignore_index = True
            else:
                ignore_index = False

            # get join argument
            join_arg = self.combobox_merging_join_arg.currentText()

            # try to get the result dataframe
            try:
                self.result_df = eval(pandas_method)(df_list, axis=axis, ignore_index=ignore_index, join=join_arg)
            except NotImplementedError  as xcp:
                message_title = "Error"
                message_text = ("Unable to perform {} operation because this merging is not implemented in pandas yet.".format(pandas_method))
                message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
                message_box.setWindowIcon(QIcon(self.window_icon_path))
                message_box.exec_()
                return
            except Exception  as xcp:
                message_title = "Error"
                message_text = ("Unable to perform {} operation due to the following exception: {}".format(pandas_method, xcp))
                message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
                message_box.setWindowIcon(QIcon(self.window_icon_path))
                message_box.exec_()
                return

            # update the table
            self.updateResultTable(df = self.result_df)

        # message error
        else:

            # show error
            message_title = "Error"
            message_text = ("Dataset list is empty!")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()

        return

    #----------------------------------------------#

    def updateResultTable(self, df, data = []):

        # get df shape
        shape = df.shape

        # set data
        if df.empty:
            data = [[""]*len(self.column_names_result)]
        elif not data:
            data = [["result_df", "{}".format(shape), get_index_type(attributes = None, df = df, return_dtype_otherwise = True)]]

        # set model
        self.table_model_result = SelectionCartTableModel(data = data, header_labels = self.column_names_result, result_table = True)
        self.tableView_result.setModel(self.table_model_result)
        self.tableView_result.update()
        self.tableView_result.show()

        # send message to the main to create the visualization and analysis tabs
        self.global_parent.createVisualizationAndAnalysisTabs(self.result_df, display_name="result_df")

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # binding for adding the selected dataframes
        self.button_add_selected.clicked.connect(self.addSelected)

        # binding for transposing all
        self.button_transpose_all.clicked.connect(self.transposeAll)

        # binding for deleting all
        self.button_clean_up_selection.clicked.connect(self.removeAll)

        # binding for applying the merging
        self.button_apply_merging.clicked.connect(self.applyMerging)

        # create binding for the right clicks
        self.tableView_cart.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_cart.customContextMenuRequested.connect(lambda pos: self.tableMenuHandler(pos, table = self.tableView_cart, table_type = "cart"))

        # create binding for the right clicks
        self.tableView_result.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView_result.customContextMenuRequested.connect(lambda pos: self.tableMenuHandler(pos, table = self.tableView_result, table_type = "result"))

        # hack for resizing problems
        self.resizing_hack_timer_one_shot = QTimer(self)
        self.resizing_hack_timer_one_shot.setInterval(10)
        self.resizing_hack_timer_one_shot.timeout.connect(self.resizingHack)
        self.resizing_hack_timer_one_shot.setSingleShot(True)
        self.resizing_hack_timer_one_shot.start()

        return

    #----------------------------------------------#

    def resizingHack(self):

        # force table resizing
        self.resizeTable(self.tableView_cart, self.column_names_cart[0:-self.number_of_metadata_columns], self.header_labels_widths_cart[0:-self.number_of_metadata_columns], self.groupbox_selection_panel.frameGeometry().width(), parent=self.groupbox_selection_panel)
        self.resizeTable(self.tableView_result, self.column_names_result, self.header_labels_widths_result, self.groupbox_selection_panel.frameGeometry().width(), parent=self.groupbox_selection_panel)

        # delete timer
        self.resizing_hack_timer_one_shot.stop()
        del self.resizing_hack_timer_one_shot

        return

    #----------------------------------------------#

    def keyListFromSelectedIndexes(self, selected_indexes):

        # this variable turns true if an empty row is selected
        discard_selection = False

        # get number of items
        n_items = round(len(selected_indexes) / (len(self.column_names_cart)-self.number_of_metadata_columns))

        # init list
        key_list = []

        # index of meta column
        col = self.column_names_cart.index("Key")

        # iterate over items
        for n in range(0, n_items):

            # get true index
            i = n * (len(self.column_names_cart)-self.number_of_metadata_columns)

            # get index
            index = selected_indexes[i]

            # get row
            row = index.row()

            # check selection
            if self.table_model_cart._data[row][0:-self.number_of_metadata_columns] == [""]*len(self.column_names_cart[0:-self.number_of_metadata_columns]):
                discard_selection = True
                return [], discard_selection

            # append the metadata
            key_list.append(self.table_model_cart.index(row, col).data())

        return key_list, discard_selection

    #----------------------------------------------#

    def tableMenuHandler(self, pos, table = None, table_type = ""):

        # get indexes
        selected_indexes = table.selectedIndexes()

        # only if at least one row is selected
        if selected_indexes:

            # create menu for actions
            menu = QMenu()

            # create submenus
            if table_type == "cart":
                key_list, discard_selection = self.keyListFromSelectedIndexes(selected_indexes)
                if not discard_selection:
                    self.menu_right_click_dict["transpose"] = menu.addAction(qta.icon("fa.exchange"), self.tr("Transpose"))
                    self.menu_right_click_dict["transpose"].triggered.connect(lambda: self.transposeDf(key_list))
                    self.menu_right_click_dict["slice"] = menu.addAction(qta.icon("mdi.code-brackets"), self.tr("Slice"))
                    self.menu_right_click_dict["slice"].triggered.connect(lambda: self.sliceDf(key = key_list[0]))
                    self.menu_right_click_dict["visualize"] = menu.addAction(qta.icon("mdi.magnify"), self.tr("Visualize"))
                    self.menu_right_click_dict["visualize"].triggered.connect(lambda: self.visualizeDf(df = None, key = key_list[0]))
                    self.menu_right_click_dict["remove"] = menu.addAction(qta.icon("mdi.delete"), self.tr("Remove"))
                    self.menu_right_click_dict["remove"].triggered.connect(lambda: self.removeDf(key_list))
                    self.menu_right_click_dict["save_hdf5"] = menu.addAction(qta.icon("fa5.save"), self.tr("Save (HDF5)"))
                    self.menu_right_click_dict["save_hdf5"].triggered.connect(lambda: self.saveDf(df=None, key=key_list[0], type="hdf5"))
                    self.menu_right_click_dict["save_csv"] = menu.addAction(qta.icon("fa5.save"), self.tr("Save (CSV)"))
                    self.menu_right_click_dict["save_csv"].triggered.connect(lambda: self.saveDf(df=None, key=key_list[0], type="csv"))
                    if len(key_list) > 1:
                        self.menu_right_click_dict["slice"].setEnabled(False)
                        self.menu_right_click_dict["visualize"].setEnabled(False)
                        self.menu_right_click_dict["save_hdf5"].setEnabled(False)
                        self.menu_right_click_dict["save_csv"].setEnabled(False)
            else:
                if not self.table_model_result._data[0] == [""]*len(self.column_names_result):
                    self.menu_right_click_dict["visualize"] = menu.addAction(qta.icon("mdi.magnify"), self.tr("Visualize"))
                    self.menu_right_click_dict["visualize"].triggered.connect(lambda: self.visualizeDf(df = self.result_df, key = None))
                    self.menu_right_click_dict["save_hdf5"] = menu.addAction(qta.icon("fa5.save"), self.tr("Save (HDF5)"))
                    self.menu_right_click_dict["save_hdf5"].triggered.connect(lambda: self.saveDf(df = self.result_df, type = "hdf5"))
                    self.menu_right_click_dict["save_csv"] = menu.addAction(qta.icon("fa5.save"), self.tr("Save (CSV)"))
                    self.menu_right_click_dict["save_csv"].triggered.connect(lambda: self.saveDf(df = self.result_df, type = "csv"))

            # get global position
            globalPos = table.viewport().mapToGlobal(pos)

            # get the selected item
            selectedItem = menu.exec_(globalPos)

        return

    #----------------------------------------------#

    def getDataKeys(self):
        i = self.column_names_cart.index("Key")
        return [row[i] for row in self.table_model_cart._data]

    #----------------------------------------------#

    def removeAll(self):

        # remove all
        data_keys = self.getDataKeys()
        self.removeDf(key_list = [x for x in data_keys if x is not None], data_keys = data_keys)

        # remove result df
        self.result_df = pd.DataFrame([])

        # update the table
        self.updateResultTable(df=self.result_df)

        # update right tab colors
        if self.global_parent:
            self.global_parent.changeRightTabColors(color = "#000000")

        return

    #----------------------------------------------#

    def removeDf(self, key_list, data_keys = [], fix_gui_bugs = True):

        # save scrollbar status
        if fix_gui_bugs:
            self.tableView_cart.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            current_scroll_position_v = self.tableView_cart.verticalScrollBar().value()
            current_scroll_position_h = self.tableView_cart.horizontalScrollBar().value()

        # get table data keys
        if not data_keys:
            data_keys = self.getDataKeys()

        # iterate over keys to remove
        for key in key_list:

            # first find the key
            row = data_keys.index(key)

            # then remove the row
            self.table_model_cart.remove_row(row)
            del data_keys[row]

            # update populated rows
            self.n_populated_rows -= 1

            # add an empty row if number of populated rows is too small
            if self.n_populated_rows < 100:
                empty_row = [""] * (len(self.column_names_cart) - self.number_of_metadata_columns) + [None, pd.DataFrame(), None]
                self.table_model_cart.add_row(empty_row)

        # restore scrollbar status
        if fix_gui_bugs:
            self.tableView_cart.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            self.tableView_cart.verticalScrollBar().setValue(current_scroll_position_v)
            self.tableView_cart.horizontalScrollBar().setValue(current_scroll_position_h)

        return

    #----------------------------------------------#

    def transposeAll(self):

        # transpose all
        data_keys = self.getDataKeys()
        self.transposeDf(key_list = [x for x in data_keys if x is not None], data_keys = data_keys)

        return

    #----------------------------------------------#

    def transposeDf(self, key_list, data_keys = []):

        # get table data keys
        if not data_keys:
            data_keys = self.getDataKeys()

        # column indices
        col_new_shape = self.column_names_cart.index("New Shape")
        col = self.column_names_cart.index("Df")
        col_df_before_slicing = self.column_names_cart.index("DfBeforeSlicing")

        # iterate over keys
        for key in key_list:

            # first find the key
            row = data_keys.index(key)

            # get df for that row
            df = self.table_model_cart.index(row, col).data()

            # transpose the df
            df_transposed = df.T

            # get new shape
            new_shape = df_transposed.shape

            # make the update
            self.table_model_cart.update_data(row, col_new_shape, str(new_shape))
            self.table_model_cart.update_data(row, col, df_transposed)

            # we also have to update the sliced df
            df_before_slicing_tuple = self.table_model_cart.index(row, col_df_before_slicing).data()
            if df_before_slicing_tuple:
                first_element, row_from, row_to, row_step, col_from, col_to, col_step, reset_index = df_before_slicing_tuple
                transposed_first_element = first_element.T
                t_row_from, t_row_to, t_row_step, t_col_from, t_col_to, t_col_step = col_from, col_to, col_step, row_from, row_to, row_step
                new_tuple = (transposed_first_element, t_row_from, t_row_to, t_row_step, t_col_from, t_col_to, t_col_step, reset_index)
                self.table_model_cart.update_data(row, col_df_before_slicing, new_tuple)

        return

    #----------------------------------------------#

    def sliceDf(self, key, data_keys = []):

        # get table data keys
        if not data_keys:
            data_keys = self.getDataKeys()

        # retrieve dataframes
        row = data_keys.index(key)
        df = self.table_model_cart.index(row, self.column_names_cart.index("Df")).data()
        df_before_slicing = self.table_model_cart.index(row, self.column_names_cart.index("DfBeforeSlicing")).data()

        # open the dialog
        self.slice_dialog = SliceDialog(key, row, df, df_before_slicing, parent=self, global_parent=self)
        self.slice_dialog.exec_()

        return

    #----------------------------------------------#

    def visualizeDf(self, df, key = None, data_keys = []):

        # get table data keys
        if not data_keys:
            data_keys = self.getDataKeys()

        # retrieve the df
        display_name = "result_df"
        chunk_size = None
        if key is not None:
            row = data_keys.index(key)
            col = self.column_names_cart.index("Df")
            df = self.table_model_cart.index(row, col).data()
            display_name = self.table_model_cart.index(row, self.column_names_cart.index("Dataset Name")).data()
            chunk_size = self.table_model_cart.index(row, self.column_names_cart.index("ChunkSize")).data()

        # only if global parent exists
        if self.global_parent:

            # set the window id
            try:
                win_id = str(self.global_parent.random_id_sequence_list[self.global_parent.random_id_sequence_counter])
            except:
                print("No more windows can be opened because the maximum number of windows has already been reached...")

            # get color dict
            color_dict = {}
            color_dict["color_background"] = self.global_parent.dict_for_settings["color_background"]
            color_dict["color_foreground_palette_name"] = self.global_parent.dict_for_settings["color_foreground_palette_name"]

            # open new visualization
            self.global_parent.visualization_tab_new_windows[win_id] = MainVisualization(self.app, df, {}, display_name, True, last_selected_sub_tab=0, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.global_parent, global_parent=None, popup_window=True, color_dict=color_dict, mouse_mode_1_button=self.global_parent.dict_for_settings["setting_enable_1_button_mouse_mode"], pyqtgraph_default_downsample=self.global_parent.dict_for_settings["setting_enable_downsampling_plots"], sticky_options=self.global_parent.dict_for_settings["setting_sticky_options"], display_strings_on_x_axis=self.global_parent.dict_for_settings["setting_display_strings_on_x_axis"], ncurves_at_init=self.global_parent.dict_for_settings["ncurves_at_init"], min_big_data_sample_size=self.global_parent.dict_for_settings["min_big_data_sample_size"], chunk_size=chunk_size, max_n_columns=self.global_parent.dict_for_settings["max_n_columns"])

            # save window id in the window
            self.global_parent.visualization_tab_new_windows[win_id].win_id = win_id

            # change window title
            self.global_parent.visualization_tab_new_windows[win_id].setWindowTitle("Visualization Window (Popup) [id={}]".format(win_id))

            # open as pop up
            self.global_parent.visualization_tab_new_windows[win_id].show()

            # update the global counter
            self.global_parent.random_id_sequence_counter += 1

        return

    #----------------------------------------------#

    def saveDf(self, df, key=None, data_keys=[], type="csv", qta_icon="fa5.save", verbose=True):

        # typical try except workflow
        try:

            # init save name
            save_name = ""

            # if df is None we should get it from the keys
            if df is None and key is not None:

                # get table data keys
                if not data_keys:
                    data_keys = self.getDataKeys()

                # retrieve the df
                if key is not None:
                    row = data_keys.index(key)
                    col = self.column_names_cart.index("Df")
                    df = self.table_model_cart.index(row, col).data()
                    save_name = self.table_model_cart.index(row, self.column_names_cart.index("Dataset Name")).data()

            # csv case
            if type == "csv":

                # default save name?
                if not save_name:
                    save_name = "result_df.csv"
                else:
                    save_name += ".csv"

                # get name
                name, _ = QFileDialog.getSaveFileName(self, "Save file as CSV", save_name, filter="CSV(*.csv)")

                # return and exit if user did not introduce any name
                if not name:
                    return

                # add .csv in case user did not add it
                if name[-4:].lower() != ".csv":
                    name = name + ".csv"

                # for debugging
                if verbose:
                    print("Saving to CSV...")

                # save dataframe to csv
                df.to_csv(name)

            # hdf5 case
            elif type == "hdf5":

                # default save name?
                if not save_name:
                    save_name = "result_df.hdf5"
                else:
                    save_name += ".hdf5"

                # get name
                name, _ = QFileDialog.getSaveFileName(self, "Save file as HDF5", save_name, filter="HDF5(*.hdf5)")

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
                handler = HDF5DataFrameHandler(name)
                handler.save_dataframe_to_hdf5(df)

            # show success message
            message_title = "Success"
            message_text = ("Dataframe has been successfully saved to the following path: {}".format(name))
            message_box = QMessageBox(QMessageBox.Icon.Information, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon(qta_icon))
            message_box.exec_()

        # throw some error
        except Exception as xcp:

            # show error message
            message_title = "Error"
            message_text = ("Unable to save dataframe due to: {}".format(xcp))
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon(qta_icon))
            message_box.exec_()

        return

    #----------------------------------------------#

    def resizeEvent(self, event):

        # resize table when resizing the widget
        if self.tableView_cart:
            stored_width = self.groupbox_selection_panel.frameGeometry().width()
            if np.abs(stored_width - self.last_stored_width_cart) > 0:
                self.resizeTable(self.tableView_cart, self.column_names_cart[0:-self.number_of_metadata_columns], self.header_labels_widths_cart[0:-self.number_of_metadata_columns], stored_width, parent = self.groupbox_selection_panel)
                self.tableView_cart.show()
                self.last_stored_width_cart = stored_width

        # resize table when resizing the widget
        if self.tableView_result:
            stored_width = self.groupbox_selection_panel.frameGeometry().width()
            if np.abs(stored_width - self.last_stored_width_result) > 0:
                self.resizeTable(self.tableView_result, self.column_names_result, self.header_labels_widths_result, stored_width, parent = self.groupbox_selection_panel)
                self.tableView_result.show()
                self.last_stored_width_result = stored_width

        # set event
        QMainWindow.resizeEvent(self, event)

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################
