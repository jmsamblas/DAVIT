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

class CustomStandardItemModel(QStandardItemModel):

    def __init__(self, *args, **kwargs):
        super(CustomStandardItemModel, self).__init__(*args, **kwargs)

    def flags(self, index):
        default_flags = super(CustomStandardItemModel, self).flags(index)
        if not index.isValid():
            return default_flags
        if index.column() != 0:
            return default_flags | Qt.ItemIsEditable
        else:
            return default_flags & ~Qt.ItemIsEditable

    def set_data(self, row, column, value):
        index = self.index(row, column)
        self.setData(index, value, Qt.EditRole)

class ComboBoxDelegate(QStyledItemDelegate):

    combo_box_changed = pyqtSignal(int, str)

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            combo_box = QComboBox(parent)
            combo_box.setMinimumHeight(16)
            combo_box.addItems(["y{}".format(i) for i in range(1,10)])
            combo_box.currentIndexChanged.connect(lambda: self.combo_box_changed.emit(index.row(), combo_box.currentText()))
            return combo_box
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox) and index.column() == 1:
            text = index.data()
            combo_index = editor.findText(text)
            if combo_index >= 0:
                editor.setCurrentIndex(combo_index)
        else:
            super().setEditorData(editor, index)

    def sizeHint(self, option, index):
        original_size = super(ComboBoxDelegate, self).sizeHint(option, index)
        custom_height = 24
        return QSize(original_size.width(), custom_height)

#################################################################
#################################################################

class PlotDataSelector(QDialog):

    #----------------------------------------------#

    def __init__(self, dataframe, app, app_root_path, parent, previous_selected_indexes = [], previous_names = [], previous_axis_list = [], var_axis_dict = None, x_label = "", y_label = ""):

        # inherit from QDialog
        QDialog.__init__(self)

        # main attributes
        self.dataframe = dataframe
        self.app = app
        self.app_root_path = app_root_path
        self.parent = parent
        self.previous_selected_indexes = previous_selected_indexes
        self.previous_names = previous_names
        self.previous_axis_list = previous_axis_list
        self.x_label = x_label
        self.y_label = y_label

        # own attributes
        if var_axis_dict:
            self.var_axis_dict = var_axis_dict
        else:
            self.var_axis_dict = collections.OrderedDict()

        # load ui file
        uic.loadUi(os.path.join(self.app_root_path, "resources", "uis", "plot_data_selector.ui"), self)

        # title and icon
        self.setWindowTitle("Variable Selector")
        self.setWindowIcon(qta.icon("mdi.form-select"))

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # get columns
        self.columns = list(self.dataframe.columns.astype(str))

        # fill treeview with columns
        self.model_treeView = CustomStandardItemModel(0,2)
        self.model_treeView.setHorizontalHeaderLabels(['Variable', 'Y-axis'])

        # set edit triggers
        self.treeView.setEditTriggers(QTreeView.DoubleClicked | QTreeView.EditKeyPressed)

        # add children items (columns) to the parent item
        for row in self.columns:
            variable_item = QStandardItem(str(row))
            y_axis_item = QStandardItem("y1")
            self.model_treeView.appendRow([variable_item, y_axis_item])
            if str(row) not in self.var_axis_dict.keys():
                self.var_axis_dict[str(row)] = "y1"

        # create delegate
        self.treeView_delegate = ComboBoxDelegate()
        self.treeView_delegate.combo_box_changed.connect(self.comboChanged)

        # set models
        self.treeView.setModel(self.model_treeView)
        self.treeView.setItemDelegateForColumn(1, self.treeView_delegate)

        # timer for resizing hack
        self.hack_timer = QTimer(self)
        self.hack_timer.setInterval(20)
        self.hack_timer.setSingleShot(True)
        self.hack_timer.timeout.connect(self.hackColumnResize)
        self.hack_timer.start()

        # set init state
        self.setInitState()

        # set initial labels
        self.lineEdit_x_axis_label.setText(self.x_label)
        self.lineEdit_y_axis_label.setText(self.y_label)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # accept and reject
        self.pushButton_yes.clicked.connect(self.acceptOverride)
        self.pushButton_no.clicked.connect(self.rejectOverride)

        # Ctrl+A to select all
        self.shorcut_Key_CtrlA_select_all = QShortcut(QKeySequence("Ctrl+A"), self.treeView, context=Qt.WidgetShortcut, activated = lambda: self.selectAll())

        # button to select all
        self.pushButton_select_all.clicked.connect(self.selectAll)

        # binding for the regex filter
        self.lineEdit_regex.textChanged.connect(self.filterSelectionList)
        self.lineEdit_regex.returnPressed.connect(self.filterSelectionList)

        return

    #----------------------------------------------#

    def setInitState(self):

        # update axis comboboxes for current plotted variables
        def select_rows(tree_view, rows_to_select):
            model = tree_view.model()
            selection_model = tree_view.selectionModel()
            for row in rows_to_select:
                index = model.index(row, 0)
                selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        select_rows(self.treeView, self.previous_selected_indexes)

        # select current plotted variables
        def set_combobox_value(tree_view, var_axis_dict, column):
            model = tree_view.model()
            for c_row, row in enumerate(list(var_axis_dict.keys())):
                model.set_data(c_row, column, var_axis_dict[row])
        set_combobox_value(self.treeView, self.var_axis_dict, 1)

        return

    #----------------------------------------------#

    def comboChanged(self, row, text):

        # save into the dict
        self.var_axis_dict[str(self.columns[row])] = text

        return

    #----------------------------------------------#

    def selectAll(self):

        # just select all the items
        try:
            self.treeView.expandAll()
            self.treeView.selectAll()
        except:
            pass

        return

    #----------------------------------------------#

    def selectionHasChanged(self):

        # uncheck select all button
        if self.checkBox_select_all.isChecked():
            self.checkBox_select_all.blockSignals(False)
            self.checkBox_select_all.setChecked(False)
            self.checkBox_select_all.blockSignals(True)

        return

    #----------------------------------------------#

    def searchAndRetrieve(self, search_string):

        # retrieve the axis value
        for row in range(self.model_treeView.rowCount()):
            index = self.model_treeView.index(row, 0)
            value = index.data(Qt.DisplayRole)
            if value == search_string:
                index_second_col = self.model_treeView.index(row, 1)
                second_col_value = index_second_col.data(Qt.DisplayRole)
                return second_col_value
                break

        return None

    #----------------------------------------------#

    def filterSelectionList(self):

        # filter the list
        try:
            pattern = self.lineEdit_regex.text()
            re_object = re.compile("{}".format(pattern))
            self.filtered_names = list(filter(re_object.match, self.columns))
        except Exception as xcp:
            print("Exception at the regex expression: {}".format(xcp))
            return

        # retrieve the set axis values for filtered names
        if self.filtered_names:
            self.filtered_axes = []
            for var_name in self.filtered_names:
                self.filtered_axes.append(self.var_axis_dict[var_name])

        # clear list
        self.treeView.model().clear()
        self.treeView.model().setHorizontalHeaderLabels(['Variable', 'Y-axis'])

        # add columns directly to the model
        for counter_row, row in enumerate(self.filtered_names):
            variable_item = QStandardItem(str(row))
            if self.filtered_axes[counter_row]:
                y_axis_item = QStandardItem(self.filtered_axes[counter_row])
            else:
                y_axis_item = QStandardItem("y1")
            self.model_treeView.appendRow([variable_item, y_axis_item])

        # resize
        self.hackColumnResize()

        return

    #----------------------------------------------#

    def acceptOverride(self):

        # get selection
        selected_indexes = self.treeView.selectedIndexes()

        # if no selection
        if not selected_indexes:
            self.rejectOverride()
            return

        # get 1st column
        selected_indexes = [index for index in selected_indexes if index.column() == 0]

        # fill output lists
        selected_column_indexes = []
        names = []
        axis_list = []
        for pyqt_index in selected_indexes:
            name = pyqt_index.data()
            index_sel = self.columns.index(name)
            selected_column_indexes.append(index_sel)
            names.append(name)
            axis_list.append(self.var_axis_dict[name])

        # get x and y labels
        self.x_label = "{}".format(self.lineEdit_x_axis_label.text())
        self.y_label = "{}".format(self.lineEdit_y_axis_label.text())

        # check zero cases
        if self.x_label == "":
            self.x_label = "x"
        if self.y_label == "":
            self.y_label = "y"

        # finally send the accept event with the output information
        self.accept()
        if selected_indexes:
            if self.parent:
                self.parent.var_axis_dict = self.var_axis_dict
                self.parent.selectionOutput(selected_column_indexes, names, axis_list, self.x_label, self.y_label)

        return

    #----------------------------------------------#

    def rejectOverride(self):

        # just reject and close window
        self.reject()

        return

    #----------------------------------------------#

    def hackColumnResize(self):

        # resize the columns to equal width
        width_frame = self.treeView.frameGeometry().width()
        for column in range(0, self.model_treeView.columnCount()):
            self.treeView.setColumnWidth(column, 0.98*(width_frame / 2))

        # delete the timer
        try:
            self.hack_timer.stop()
            del self.hack_timer
        except:
            pass

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