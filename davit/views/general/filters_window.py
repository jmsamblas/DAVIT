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

class FiltersWindow(QDialog):

    #----------------------------------------------#

    def __init__(self, app, app_root_path, parent, current_filters_preset = {}):

        # inherit from QDialog
        QDialog.__init__(self)

        # main attributes
        self.app = app
        self.app_root_path = app_root_path
        self.parent = parent
        self.current_filters_preset = current_filters_preset

        # own attributes
        self.filters = {}
        self.interval_filtering = False

        # init filters
        filters = {}
        filters["path"] = {}
        filters["path"]["dir"] = ""
        filters["path"]["hdf5"] = ""
        filters["attributes"] = {}
        filters["attributes"]["group"] = {}
        filters["attributes"]["dataset"] = {}

        # store filters
        self.filters = filters
        
        # own attributes
        self.max_number_of_rows = 250

        # load ui file
        uic.loadUi(os.path.join(self.app_root_path, "resources", "uis", "filters_window.ui"), self)

        # title and icon
        self.setWindowTitle("Filters")
        self.setWindowIcon(qta.icon("ri.play-list-add-fill"))

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#
    
    def initVariables(self):
        
        # init everything
        self.pushButtons_plus = {}
        self.pushButtons_minus = {}
        self.lineEdits = {}
        self.comboBoxes = {}
        self.spacerItems = {}
        
        return
    
    #----------------------------------------------#

    def buildFirstRow(self, init = False):

        # set font
        font = QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)

        # add all labels
        self.label_atr_bt = QLabel(self.scrollAreaContents)
        self.label_atr_bt.setFont(font)
        self.label_atr_bt.setAlignment(Qt.AlignCenter)
        self.label_atr_bt.setObjectName("label_atr_bt")
        self.gridLayout_scrollAreaContents.addWidget(self.label_atr_bt, 0, 0, 1, 1)
        self.label_atr_key = QLabel(self.scrollAreaContents)
        self.label_atr_key.setFont(font)
        self.label_atr_key.setAlignment(Qt.AlignCenter)
        self.label_atr_key.setObjectName("label_atr_key")
        self.gridLayout_scrollAreaContents.addWidget(self.label_atr_key, 0, 1, 1, 1)
        self.label_atr_val1 = QLabel(self.scrollAreaContents)
        self.label_atr_val1.setFont(font)
        self.label_atr_val1.setAlignment(Qt.AlignCenter)
        self.label_atr_val1.setObjectName("label_atr_val1")
        self.gridLayout_scrollAreaContents.addWidget(self.label_atr_val1, 0, 2, 1, 1)
        self.label_atr_val2 = QLabel(self.scrollAreaContents)
        self.label_atr_val2.setFont(font)
        self.label_atr_val2.setAlignment(Qt.AlignCenter)
        self.label_atr_val2.setObjectName("label_atr_val2")
        self.gridLayout_scrollAreaContents.addWidget(self.label_atr_val2, 0, 3, 1, 1)
        self.label_atr_type = QLabel(self.scrollAreaContents)
        self.label_atr_type.setFont(font)
        self.label_atr_type.setAlignment(Qt.AlignCenter)
        self.label_atr_type.setObjectName("label_atr_type")
        self.gridLayout_scrollAreaContents.addWidget(self.label_atr_type, 0, 4, 1, 1)
        self.gridLayout_scrollAreaContents.setColumnStretch(0, 10)
        self.gridLayout_scrollAreaContents.setColumnStretch(1, 100)
        self.gridLayout_scrollAreaContents.setColumnStretch(2, 100)
        self.gridLayout_scrollAreaContents.setColumnStretch(3, 100)
        self.gridLayout_scrollAreaContents.setColumnStretch(4, 100)

        # set texts
        self.label_atr_bt.setText("Button")
        self.label_atr_key.setText("Key")
        self.label_atr_val1.setText("Value1")
        self.label_atr_val2.setText("Value2")
        self.label_atr_type.setText("Type")

        # make invisible the button title
        self.label_atr_bt.setVisible(False)

        # disable or enable widgets depending on the checkbox
        if init:
            self.enableIntervalFiltering(state = 0)

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # init previous preset
        if self.current_filters_preset:
            self.loadPreset(json_data = self.current_filters_preset)
        else:
            self.initPreset(init_first_row=True, empty_paths=True, reset_checkbox=True)

        # set some icons
        self.pushButton_init.setIcon(qta.icon("mdi.delete-empty"))
        self.pushButton_load.setIcon(qta.icon("ri.save-2-fill"))
        self.pushButton_save.setIcon(qta.icon("ri.save-2-line"))

        return

    #----------------------------------------------#
    
    def addPushButtonPlus(self, row, col = 0):

        self.pushButtons_plus["row_{}_col_{}".format(row,col)] = QPushButton(self.scrollAreaContents)
        self.pushButtons_plus["row_{}_col_{}".format(row, col)].setObjectName("pushButtons_row_{}_col_{}".format(row, col))
        self.pushButtons_plus["row_{}_col_{}".format(row,col)].setIcon(qta.icon("fa.plus-square"))
        self.pushButtons_plus["row_{}_col_{}".format(row, col)].setStyleSheet("background-color: #e6ffb3;")
        self.pushButtons_plus["row_{}_col_{}".format(row, col)].setMaximumWidth(40)
        self.pushButtons_plus["row_{}_col_{}".format(row, col)].setFocusPolicy(Qt.NoFocus)
        self.pushButtons_plus["row_{}_col_{}".format(row, col)].clicked.connect(lambda: self.addAttrRow(row=row))
        self.gridLayout_scrollAreaContents.addWidget(self.pushButtons_plus["row_{}_col_{}".format(row,col)], row, col)

        return
    
    def removePushButtonPlus(self, row, col = 0):
        
        if "row_{}_col_{}".format(row, col) in list(self.pushButtons_plus.keys()):
            try:
                self.gridLayout_scrollAreaContents.removeWidget(self.pushButtons_plus["row_{}_col_{}".format(row, col)])
                self.pushButtons_plus["row_{}_col_{}".format(row, col)].setParent(None)
                self.pushButtons_plus["row_{}_col_{}".format(row, col)].deleteLater()
                self.pushButtons_plus["row_{}_col_{}".format(row, col)] = None
                del self.pushButtons_plus["row_{}_col_{}".format(row, col)]
            except Exception as xcp:
                print("Unable to remove widget (removePushButtonPlus) at row {} due to the following exception: {}".format(row, xcp))

        return

    #----------------------------------------------#

    def addPushButtonMinus(self, row, col = 0):

        self.pushButtons_minus["row_{}_col_{}".format(row,col)] = QPushButton(self.scrollAreaContents)
        self.pushButtons_minus["row_{}_col_{}".format(row, col)].setObjectName("pushButtons_row_{}_col_{}".format(row, col))
        self.pushButtons_minus["row_{}_col_{}".format(row,col)].setIcon(qta.icon("fa.minus-square"))
        self.pushButtons_minus["row_{}_col_{}".format(row, col)].setStyleSheet("background-color: #ffb3b3;")
        self.pushButtons_minus["row_{}_col_{}".format(row, col)].setMaximumWidth(40)
        self.pushButtons_minus["row_{}_col_{}".format(row, col)].setFocusPolicy(Qt.NoFocus)
        self.pushButtons_minus["row_{}_col_{}".format(row, col)].clicked.connect(lambda: self.removeAttrRow(row=row))
        self.gridLayout_scrollAreaContents.addWidget(self.pushButtons_minus["row_{}_col_{}".format(row,col)], row, col)

        return
    
    def removePushButtonMinus(self, row, col = 0):

        if "row_{}_col_{}".format(row, col) in list(self.pushButtons_minus.keys()):
            try:
                self.gridLayout_scrollAreaContents.removeWidget(self.pushButtons_minus["row_{}_col_{}".format(row, col)])
                self.pushButtons_minus["row_{}_col_{}".format(row, col)].setParent(None)
                self.pushButtons_minus["row_{}_col_{}".format(row, col)].deleteLater()
                self.pushButtons_minus["row_{}_col_{}".format(row, col)] = None
                del self.pushButtons_minus["row_{}_col_{}".format(row, col)]
            except Exception as xcp:
                print("Unable to remove widget (removePushButtonMinus) at row {} due to the following exception: {}".format(row, xcp))

        return
    
    #----------------------------------------------#

    def addSpacers(self, row):

        for col in range(self.gridLayout_scrollAreaContents.columnCount()):
            key = "row_{}_col_{}".format(row, col)
            item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            self.spacerItems[key] = item
            self.gridLayout_scrollAreaContents.addItem(item, row, col)

        return

    def removeSpacers(self, row):

        try:
            for col in range(self.gridLayout_scrollAreaContents.columnCount()):
                key = "row_{}_col_{}".format(row, col)
                if key in self.spacerItems:
                    item = self.spacerItems[key]
                    if item is not None:
                        self.gridLayout_scrollAreaContents.removeItem(item)
                    del self.spacerItems[key]
        except Exception as xcp:
            print("Unable to remove widget (removeSpacers) at row {} due to the following exception: {}".format(row, xcp))

        return
    
    #----------------------------------------------#

    def addLineEdit(self, row, col = 1, txt = ""):

        self.lineEdits["row_{}_col_{}".format(row, col)] = QLineEdit(self.scrollAreaContents)
        self.lineEdits["row_{}_col_{}".format(row, col)].setObjectName("lineEdits_row_{}_col_{}".format(row, col))
        self.lineEdits["row_{}_col_{}".format(row, col)].setText(txt)
        self.gridLayout_scrollAreaContents.addWidget(self.lineEdits["row_{}_col_{}".format(row, col)], row, col)

        if col == 3:
            if self.interval_filtering:
                self.lineEdits["row_{}_col_{}".format(row, col)].setEnabled(True)
            else:
                self.lineEdits["row_{}_col_{}".format(row, col)].setEnabled(False)

        return

    #----------------------------------------------#

    def addComboBox(self, row, col = 3, idx = 0):

        self.comboBoxes["row_{}_col_{}".format(row, col)] = QComboBox(self.scrollAreaContents)
        self.comboBoxes["row_{}_col_{}".format(row, col)].setObjectName("comboBoxes_row_{}_col_{}".format(row, col))
        self.comboBoxes["row_{}_col_{}".format(row, col)].addItem("Group")
        self.comboBoxes["row_{}_col_{}".format(row, col)].addItem("Dataset")
        self.comboBoxes["row_{}_col_{}".format(row, col)].setCurrentIndex(idx)
        self.gridLayout_scrollAreaContents.addWidget(self.comboBoxes["row_{}_col_{}".format(row, col)], row, col)

        return
    
    #----------------------------------------------#

    def addAttrRow(self, row = 0, lineEdit1_txt = "", lineEdit2_txt = "", lineEdit3_txt = "" , comboBox_index = 0):

        # max number of rows check
        if row < self.max_number_of_rows:

            # row 1
            self.removePushButtonPlus(row, col = 0)
            self.addPushButtonMinus(row, col = 0)
            self.addLineEdit(row, col = 1, txt = lineEdit1_txt)
            self.addLineEdit(row, col = 2, txt = lineEdit2_txt)
            self.addLineEdit(row, col = 3, txt = lineEdit3_txt)
            self.addComboBox(row, col = 4, idx = comboBox_index)

            # row 2
            self.removeSpacers(row+1)
            self.addPushButtonPlus(row+1, col = 0)

            # row 3
            self.addSpacers(row+2)

        # show message in case there are too many rows
        else:

            # show error message
            message_title = "Error"
            message_text = "You have reached the maximum number of allowed filters!"
            message_box = QMessageBox(QMessageBox.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("ri.play-list-add-fill"))
            message_box.exec_()

        return
    
    #----------------------------------------------#

    def removeAttrRow(self, row):

        # store all data in a list before destroying the layout
        row_data_list = []
        last_row = int(list(self.spacerItems.keys())[0].split("_")[1])
        for r in range(1, last_row - 1):
            if row == r:
                continue
            lineEdit1_txt = self.lineEdits["row_{}_col_{}".format(r, 1)].text()
            lineEdit2_txt = self.lineEdits["row_{}_col_{}".format(r, 2)].text()
            lineEdit3_txt = self.lineEdits["row_{}_col_{}".format(r, 3)].text()
            comboBox_index = self.comboBoxes["row_{}_col_{}".format(r, 4)].currentIndex()
            row_data_list.append(("-", lineEdit1_txt, lineEdit2_txt, lineEdit3_txt, comboBox_index))
        row_data_list.append(("+", "", "", 0))
        row_data_list.append(("scaler", "scaler", "scaler", "scaler"))

        # make sure we dont delete the first row
        if len(row_data_list) > 2:

            # init
            self.initPreset(init_first_row=False, empty_paths=False, reset_checkbox=False)

            # remake everything with one less row
            for r, data in enumerate(row_data_list):
                self.addAttrRow(row = r+1, lineEdit1_txt = data[1], lineEdit2_txt = data[2], lineEdit3_txt = data[3], comboBox_index = data[4])
                if r == len(row_data_list)-3:
                    break

        # show message in case there are not enough rows
        else:

            # show error message
            message_title = "Error"
            message_text = "At least one filter is needed!"
            message_box = QMessageBox(QMessageBox.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(qta.icon("ri.play-list-add-fill"))
            message_box.exec_()

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # accept and reject
        self.pushButton_yes.clicked.connect(self.acceptOverride)
        self.pushButton_no.clicked.connect(self.rejectOverride)

        # binding for enabling and disabling the intervals
        self.checkBox_enable_filtering_by_interval.stateChanged.connect(self.enableIntervalFiltering)

        # bindings for the presets
        self.pushButton_load.clicked.connect(lambda: self.loadPresetDialog())
        self.pushButton_save.clicked.connect(lambda: self.savePresetDialog())
        self.pushButton_init.clicked.connect(lambda: self.initPreset())

        return

    #----------------------------------------------#

    def savePreset(self, file_name = "", message_box = False):

        # init output dict
        json_dict = {}

        # store paths
        json_dict["path_files"] = self.lineEdit_dir.text()
        json_dict["path_hdf5"] = self.lineEdit_hdf5.text()

        # checkbox for intervals
        json_dict["enable_filtering_by_interval"] = self.checkBox_enable_filtering_by_interval.isChecked()

        # save attributes
        json_dict["attributes"] = {}
        last_row = int(list(self.spacerItems.keys())[0].split("_")[1])
        for r in range(1, last_row - 1):
            lineEdit1_txt = self.lineEdits["row_{}_col_{}".format(r, 1)].text()
            lineEdit2_txt = self.lineEdits["row_{}_col_{}".format(r, 2)].text()
            lineEdit3_txt = self.lineEdits["row_{}_col_{}".format(r, 3)].text()
            comboBox_idx = self.comboBoxes["row_{}_col_{}".format(r, 4)].currentIndex()
            json_dict["attributes"][str(r)] = {}
            json_dict["attributes"][str(r)]["Key"] = lineEdit1_txt
            json_dict["attributes"][str(r)]["Value1"] = lineEdit2_txt
            json_dict["attributes"][str(r)]["Value2"] = lineEdit3_txt
            json_dict["attributes"][str(r)]["Type"] = comboBox_idx

        # case 1 (save to json file)
        if file_name:

            # save json file
            with open(file_name, 'w') as json_file:
                json.dump(json_dict, json_file, indent=4)

            # show success message
            if message_box:
                message_title = "Success"
                message_text = ("Successfully saved preset: {}".format(file_name))
                message_box = QMessageBox(QMessageBox.Information, message_title, message_text, parent=self)
                message_box.setWindowIcon(qta.icon("ri.play-list-add-fill"))
                message_box.exec_()

        # save to parent
        else:

            # save in the main window
            self.parent.current_filters_preset = json_dict

        return

    #----------------------------------------------#

    def savePresetDialog(self):

        # open the preset via file explorer
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save preset", "", "JSON Files (*.json);;All Files (*)")
            file_name = str(file_name)
            if file_name:
                if not file_name.endswith(".json"):
                    file_name += ".json"
        except Exception as xcp:
            if verbose:
                print(xcp)
            return

        # check if file exists and save the preset
        if file_name:
            self.savePreset(file_name=file_name, message_box=True)

        return

    #----------------------------------------------#

    def initPreset(self, init_first_row = True, empty_paths = True, reset_checkbox = True):

        # clear everything
        clearLayout(self.gridLayout_scrollAreaContents)
        self.initVariables()
        self.buildFirstRow()

        # create first row
        if init_first_row:
            self.addAttrRow(row=1)

        # lineedits for the paths
        if empty_paths:
            self.lineEdit_dir.setText(".*")
            self.lineEdit_hdf5.setText(".*")

        # checkbox for intervals
        if reset_checkbox:
            self.checkBox_enable_filtering_by_interval.setChecked(False)
            self.enableIntervalFiltering(state = self.checkBox_enable_filtering_by_interval.isChecked())

        return

    #----------------------------------------------#

    def loadPreset(self, json_data):

        # proceed if dict exists
        if json_data:

            # init first row or not
            init_first_row = True
            if "attributes" in json_data.keys():
                if len(json_data["attributes"].keys()) > 0:
                    init_first_row = False

            # init
            self.initPreset(init_first_row=init_first_row, empty_paths=True, reset_checkbox=True)

            # set filters by path
            try:
                self.lineEdit_dir.setText(json_data["path_files"])
            except:
                self.lineEdit_dir.setText(".*")
            try:
                self.lineEdit_hdf5.setText(json_data["path_hdf5"])
            except:
                self.lineEdit_hdf5.setText(".*")

            # interval filtering
            try:
                if json_data.get("enable_filtering_by_interval") is True:
                    self.checkBox_enable_filtering_by_interval.setChecked(True)
                else:
                    self.checkBox_enable_filtering_by_interval.setChecked(False)
            except:
                self.checkBox_enable_filtering_by_interval.setChecked(False)

            # double check
            self.enableIntervalFiltering(state=self.checkBox_enable_filtering_by_interval.isChecked())

            # iterate over attributes
            if "attributes" in json_data.keys():
                for attr in json_data["attributes"]:
                    try:
                        self.addAttrRow(row=int(attr), lineEdit1_txt=str(json_data["attributes"][attr]["Key"]),
                                        lineEdit2_txt=str(json_data["attributes"][attr]["Value1"]),
                                        lineEdit3_txt=str(json_data["attributes"][attr]["Value2"]),
                                        comboBox_index=int(json_data["attributes"][attr]["Type"]))
                    except:
                        pass

        return

    #----------------------------------------------#

    def loadPresetDialog(self, verbose = True):

        # open the preset via file explorer
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open preset", "", "JSON Files (*.json)")
            file_name = str(file_name)
        except Exception as xcp:
            if verbose:
                print(xcp)
            return

        # debugging
        if verbose:
            print("file_name: ", file_name)

        # check if file exists and load the preset
        if file_name:

            # open json file
            try:
                with open(file_name, "r") as file:
                    json_data = json.load(file)
            except Exception as xcp:
                if verbose:
                    print(xcp)
                return

            # save current preset
            self.current_filters_preset = json_data

            # load the preset
            self.loadPreset(json_data = self.current_filters_preset)

        return

    #----------------------------------------------#

    def enableIntervalFiltering(self, state):

        # is disabled
        if state == 0:

            # proceed
            self.interval_filtering = False
            self.label_atr_val2.setEnabled(False)
            for i in range(self.gridLayout_scrollAreaContents.rowCount()):
                item = self.gridLayout_scrollAreaContents.itemAtPosition(i, 3)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        if isinstance(widget, QLineEdit):
                            widget.setText("")
                        widget.setEnabled(False)

        # is enabled
        else:

            # proceed
            self.interval_filtering = True
            self.label_atr_val2.setEnabled(True)
            for i in range(self.gridLayout_scrollAreaContents.rowCount()):
                item = self.gridLayout_scrollAreaContents.itemAtPosition(i, 3)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        if isinstance(widget, QLineEdit):
                            widget.setText("")
                        widget.setEnabled(True)

        return

    #----------------------------------------------#

    def acceptOverride(self):

        # init filters
        self.filters = {}
        self.filters["path"] = {}
        self.filters["path"]["dir"] = ""
        self.filters["path"]["hdf5"] = ""
        self.filters["attributes"] = {}
        self.filters["attributes"]["group"] = {}
        self.filters["attributes"]["dataset"] = {}

        # get line edit info
        self.filters["path"]["dir"] = self.lineEdit_dir.text()
        self.filters["path"]["hdf5"] = self.lineEdit_hdf5.text()

        # get attributes info
        last_row = int(list(self.spacerItems.keys())[0].split("_")[1])
        for r in range(1, last_row - 1):
            lineEdit1_txt = self.lineEdits["row_{}_col_{}".format(r, 1)].text()
            lineEdit2_txt = self.lineEdits["row_{}_col_{}".format(r, 2)].text()
            lineEdit3_txt = self.lineEdits["row_{}_col_{}".format(r, 3)].text()
            comboBox_txt = self.comboBoxes["row_{}_col_{}".format(r, 4)].currentText().lower()
            if lineEdit1_txt and (lineEdit2_txt or lineEdit3_txt):
                self.filters["attributes"][comboBox_txt][lineEdit1_txt] = (lineEdit2_txt, lineEdit3_txt)

        # finally send the accept event with the output information
        self.accept()
        if self.parent:
            self.savePreset()
            self.parent.applyFilters(self.filters)

        return

    #----------------------------------------------#

    def rejectOverride(self):

        # just reject and close window
        self.reject()

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # go to the reject function
        self.rejectOverride()

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

    def debugLayout(self, layout: QGridLayout):
        for i in range(layout.rowCount()):
            for j in range(layout.columnCount()):
                item = layout.itemAtPosition(i, j)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget_type = type(widget).__name__
                        print(f"Widget ({widget_type}) found at row {i}, column {j}.")

    #----------------------------------------------#

#################################################################
#################################################################