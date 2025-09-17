#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.utils.nxcals_tree_view_model import NXCALSTreeViewModel
from davit.views.general.waiting_widget_nxcals import WaitingWidgetNXCALS
from davit.views.general.nxcals_threads_panel import NXCALSThreadsPanel
from davit.utils.nxcals_query_thread import NXCALSQueryThread

#################################################################
#################################################################

class UnclickablePushButton(QPushButton):
    def mousePressEvent(self, event):
        pass

    def event(self, e):
        if e.type() == QEvent.HoverEnter or e.type() == QEvent.HoverLeave or e.type() == QEvent.HoverMove:
            return True
        return super().event(e)

#################################################################
#################################################################

class NXCALSTreeView(QFrame):

    #----------------------------------------------#

    def __init__(self, parent = None, global_parent = None):

        # inheritance
        super().__init__(parent)

        # attributes
        self.parent = parent
        self.global_parent = global_parent

        # own attributes
        self.logging_in_progress = False
        self.pytimber_initialized = False
        self.treeView_model = None

        # main widgets
        self.waiting_widget = None
        self.threads_panel = None

        # create list of example dates
        self.example_dates = []
        for year in range(2000, 2101):
            date = datetime(year, 1, 1)
            self.example_dates.append(date.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        # build the tree
        self.buildTree()

        # bind the widgets
        self.bindWidgets()

        # create threads panel but do not show
        self.threads_panel = NXCALSThreadsPanel(app=self.global_parent.app, app_root_path=self.global_parent.app_root_path, parent=self)
        self.threads_panel.setVisible(False)

        return

    #----------------------------------------------#

    def buildTree(self):

        # get current date
        current_date = QDateTime.currentDateTime()
        previous_current_date = current_date.addDays(-1)

        # disable borders
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # main holder layout
        self.verticalLayout_holder = QVBoxLayout(self)
        self.verticalLayout_holder.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_holder.setSpacing(0)
        self.verticalLayout_holder.setObjectName("verticalLayout_holder")

        # create the tree view
        self.treeView = QTreeView(self)
        self.treeView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.treeView.setFrameShape(QFrame.Shape.NoFrame)
        self.treeView.setFrameShadow(QFrame.Shadow.Plain)
        self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeView.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.treeView.setIndentation(10)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(False)
        self.treeView.setMinimumWidth(200)
        self.verticalLayout_holder.addWidget(self.treeView)

        # frame for the search queries
        self.frame_holder_search = QFrame(self)
        self.frame_holder_search.setObjectName("frame_holder_search")
        self.verticalLayout_holder.addWidget(self.frame_holder_search)

        # set scroll area (to make widget resizable)
        self.scroll_area = QScrollArea(self.frame_holder_search)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #A6A6A6; border-top: 0px;} ")

        # layout of the form
        self.verticalLayout_frame_holder_search = QVBoxLayout(self.frame_holder_search)
        self.verticalLayout_frame_holder_search.setObjectName("verticalLayout_frame_holder_search")
        self.verticalLayout_frame_holder_search.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_frame_holder_search.setSpacing(0)

        # frame for the search queries
        self.frame_search = QFrame(self.frame_holder_search)
        self.frame_search.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_search.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_search.setObjectName("frame_search")

        # set the main frame as the widget of the QScrollArea
        self.scroll_area.setWidget(self.frame_search)

        # add the QScrollArea to the layout
        self.verticalLayout_frame_holder_search.addWidget(self.scroll_area)

        # layout for the frame search
        self.verticalLayout_frame_search = QVBoxLayout(self.frame_search)
        self.verticalLayout_frame_search.setContentsMargins(8, 16, 8, 16)
        self.verticalLayout_frame_search.setSpacing(16)
        self.verticalLayout_frame_search.setObjectName("verticalLayout_frame_search")

        # first frame for the lineedits
        self.frame_search_edits = QFrame(self.frame_search)
        self.frame_search_edits.setObjectName("frame_search_edits")
        self.verticalLayout_frame_search.addWidget(self.frame_search_edits)

        # layout for the first frame
        self.gridLayout_frame_search_edits = QGridLayout(self.frame_search_edits)
        self.gridLayout_frame_search_edits.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_frame_search_edits.setSpacing(8)
        self.gridLayout_frame_search_edits.setObjectName("gridLayout_frame_search_edits")

        # set font
        font = QFont()
        font.setBold(True)
        font.setWeight(75)

        # label for the queries
        self.label_query = QLabel(self.frame_search_edits)
        self.label_query.setObjectName("label_query")
        self.label_query.setText("Query")
        self.label_query.setFont(font)
        self.label_query.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_frame_search_edits.addWidget(self.label_query, 0, 0)

        # create lineedit for the queries
        self.lineEdit_query = QLineEdit(self.frame_search_edits)
        self.lineEdit_query.setObjectName("lineEdit_query")
        self.lineEdit_query.setPlaceholderText("DEVICE:PROPERTY:FIELD")
        self.gridLayout_frame_search_edits.addWidget(self.lineEdit_query, 0, 1)

        # label for the ts1
        self.label_ts_start = QLabel(self.frame_search_edits)
        self.label_ts_start.setObjectName("label_ts_start")
        self.label_ts_start.setText("TS1")
        self.label_ts_start.setFont(font)
        self.label_ts_start.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_frame_search_edits.addWidget(self.label_ts_start, 1, 0)

        # create date edit for the ts1
        self.dateEdit_ts_start = QDateTimeEdit(previous_current_date, parent=self.frame_search_edits)
        self.dateEdit_ts_start.setObjectName("dateEdit_ts_start")
        self.dateEdit_ts_start.setDisplayFormat('yyyy-MM-dd HH:mm:ss.z')
        self.gridLayout_frame_search_edits.addWidget(self.dateEdit_ts_start, 1, 1)

        # create button for the calendar
        self.pushButton_calendar_ts_start = QPushButton(self.frame_search_edits)
        self.pushButton_calendar_ts_start.setObjectName("pushButton_calendar_ts_start")
        self.pushButton_calendar_ts_start.setText("")
        self.pushButton_calendar_ts_start.setIcon(qta.icon("fa.calendar"))
        self.pushButton_calendar_ts_start.setFixedSize(22,22)
        self.gridLayout_frame_search_edits.addWidget(self.pushButton_calendar_ts_start, 1, 2)

        # label for the ts2
        self.label_ts_end = QLabel(self.frame_search_edits)
        self.label_ts_end.setObjectName("label_ts_end")
        self.label_ts_end.setText("TS2")
        self.label_ts_end.setFont(font)
        self.label_ts_end.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gridLayout_frame_search_edits.addWidget(self.label_ts_end, 2, 0)

        # create date edit for the ts2
        self.dateEdit_ts_end = QDateTimeEdit(current_date, parent=self.frame_search_edits)
        self.dateEdit_ts_end.setObjectName("dateEdit_ts_end")
        self.dateEdit_ts_end.setDisplayFormat('yyyy-MM-dd HH:mm:ss.z')
        self.gridLayout_frame_search_edits.addWidget(self.dateEdit_ts_end, 2, 1)

        # create button for the calendar
        self.pushButton_calendar_ts_end = QPushButton(self.frame_search_edits)
        self.pushButton_calendar_ts_end.setObjectName("pushButton_calendar_ts_end")
        self.pushButton_calendar_ts_end.setText("")
        self.pushButton_calendar_ts_end.setIcon(qta.icon("fa.calendar"))
        self.pushButton_calendar_ts_end.setFixedSize(22,22)
        self.gridLayout_frame_search_edits.addWidget(self.pushButton_calendar_ts_end, 2, 2)

        # second frame for the accept button
        self.frame_search_accept = QFrame(self.frame_search)
        self.frame_search_accept.setObjectName("frame_search_accept")
        self.verticalLayout_frame_search.addWidget(self.frame_search_accept)

        # layout for the accept frame
        self.horizontalLayout_frame_search_accept = QHBoxLayout(self.frame_search_accept)
        self.horizontalLayout_frame_search_accept.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_search_accept.setSpacing(4)
        self.horizontalLayout_frame_search_accept.setObjectName("horizontalLayout_frame_search_accept")

        # spacer item
        self.spacer_item_search_accept = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_search_accept.addItem(self.spacer_item_search_accept)

        # threads panel button
        self.button_threads_panel = QPushButton(self.frame_search_accept)
        self.button_threads_panel.setObjectName("button_threads_panel")
        self.button_threads_panel.setText("Threads")
        self.horizontalLayout_frame_search_accept.addWidget(self.button_threads_panel)

        # hide button for threads
        self.button_threads_panel.setVisible(False)

        # create button for checking initialization
        self.pushButton_pytimber_init = UnclickablePushButton(self.frame_search_accept)
        self.pushButton_pytimber_init.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pushButton_pytimber_init.setObjectName("pushButton_pytimber_init")
        self.pushButton_pytimber_init.setText("NX")
        self.pushButton_pytimber_init.setFixedWidth(24)
        self.pushButton_pytimber_init.setToolTip("NXCALS Login: PyTimber has not been initialized yet!")
        self.pushButton_pytimber_init.setStyleSheet("QPushButton{background-color:#ff9999;}")
        self.horizontalLayout_frame_search_accept.addWidget(self.pushButton_pytimber_init)

        # autocomplete button
        self.button_autocomplete = QPushButton(self.frame_search_accept)
        self.button_autocomplete.setObjectName("button_autocomplete")
        self.button_autocomplete.setText(" Autocomplete ")
        self.button_autocomplete.setCheckable(True)
        self.button_autocomplete.setChecked(False)
        self.button_autocomplete.setToolTip("When autocomplete is enabled, a dropdown list of possible queries will appear every time the user types something in the edit fields. Please note that enabling autocomplete could affect performance.")
        self.button_autocomplete.setStyleSheet("QPushButton{background-color:#FF9A9A;}")
        self.horizontalLayout_frame_search_accept.addWidget(self.button_autocomplete)

        # example button
        self.button_example = QPushButton(self.frame_search_accept)
        self.button_example.setObjectName("button_example")
        self.button_example.setText(" Example ")
        self.button_example.setIcon(qta.icon('mdi6.book-open-variant'))
        self.horizontalLayout_frame_search_accept.addWidget(self.button_example)

        # accept button
        self.button_accept = QPushButton(self.frame_search_accept)
        self.button_accept.setObjectName("button_accept")
        self.button_accept.setText(" Search ")
        self.button_accept.setIcon(qta.icon('fa.search'))
        self.horizontalLayout_frame_search_accept.addWidget(self.button_accept)

        # final stretches
        self.verticalLayout_frame_search.setStretch(0, 90)
        self.verticalLayout_frame_search.setStretch(1, 10)

        # final stretches
        self.verticalLayout_holder.setStretch(0, 75)

        # init the tree view
        self.initTreeModel()

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # binding for the search query
        self.button_accept.clicked.connect(lambda: self.searchQuery())

        # binding for opening the threads panel
        self.button_threads_panel.clicked.connect(lambda: self.showThreadsPanel())

        # binding for the examples
        self.button_example.clicked.connect(lambda: self.fillExampleQuery())

        # binding for the autocomplete option
        self.button_autocomplete.clicked.connect(self.enableAutocomplete)

        # bindings for timestamps
        self.pushButton_calendar_ts_start.clicked.connect(lambda: self.showCalendar(dateEdit = self.dateEdit_ts_start))
        self.pushButton_calendar_ts_end.clicked.connect(lambda: self.showCalendar(dateEdit = self.dateEdit_ts_end))
        self.dateEdit_ts_start.dateChanged.connect(lambda date: self.validateDate(date, self.dateEdit_ts_start))
        self.dateEdit_ts_end.dateChanged.connect(lambda date: self.validateDate(date, self.dateEdit_ts_end))

        return

    #----------------------------------------------#

    def showCalendar(self, dateEdit):

        def updateDate(date, dateEdit, dialog):
            dateEdit.setDate(date)
            dialog.close()
            return

        # modal dialog
        self.dialog_calendar = QDialog(self)
        self.dialog_calendar.setWindowTitle('Calendar')

        # init layout
        self.layout_dialog_calendar = QVBoxLayout(self.dialog_calendar)

        # create calendar object
        self.calendar = QCalendarWidget(self.dialog_calendar)
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(dateEdit.date())
        self.calendar.clicked[QDate].connect(lambda date: updateDate(date, dateEdit = dateEdit, dialog = self.dialog_calendar))
        self.layout_dialog_calendar.addWidget(self.calendar)

        # run dialog
        self.dialog_calendar.exec()

        return

    #----------------------------------------------#

    def validateDate(self, date, dateEdit):

        # invalid date (future date not allowed) (reset to current date)
        current_date = QDate.currentDate()
        if date > current_date:
            dateEdit.setDate(current_date)

        return

    #----------------------------------------------#

    def fillExampleQuery(self):

        # just fill edits with the example data
        self.lineEdit_query.setText('SP.BA4.BLMDIAMOND.2:Capture:rawBuf%')

        # fill the date times
        self.dateEdit_ts_start.setDate(QDate(2023, 2, 20))
        self.dateEdit_ts_start.setTime(QTime(0, 0, 0, 0))
        self.dateEdit_ts_end.setDate(QDate(2023, 2, 20))
        self.dateEdit_ts_end.setTime(QTime(0, 1, 0, 0))

        return

    #----------------------------------------------#

    def showThreadsPanel(self):

        # show the panel and resize its columns
        if self.pytimber_initialized:
            self.threads_panel.show()
            self.threads_panel.forceResize()
        else:
            message_title = "Error"
            message_text = ("Please, initialize PyTimber and run a valid query in order to open the NXCALS Threads panel.")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.threads_panel.window_icon_path))
            message_box.exec()
            return

        return

    #----------------------------------------------#

    def closeWaitingWidget(self):

        # only if waiting widget is opened
        if self.waiting_widget:

            # update booleans
            self.logging_in_progress = False
            self.pytimber_initialized = True

            # close the waiting animation widget
            self.waiting_widget.can_be_closed = True
            self.waiting_widget.close()
            self.waiting_widget = None
            self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

            # enable autocomplete
            self.lineEdit_query.textChanged.connect(self.updateAutocomplete)

            # change init color
            self.pushButton_pytimber_init.setToolTip("NXCALS Login: PyTimber has been successfully initialized!")
            self.pushButton_pytimber_init.setStyleSheet("QPushButton{background-color:#80ff80;}")

        return

    #----------------------------------------------#

    def enableAutocomplete(self):

        # toggle the button or not
        if self.button_autocomplete.isChecked():
            self.button_autocomplete.setStyleSheet("QPushButton{background-color:#9AFFA8;}")
            if not self.pytimber_initialized:
                self.initPyTimber()
        else:
            self.button_autocomplete.setStyleSheet("QPushButton{background-color:#FF9A9A;}")

        # init completer
        self.setQCompleter([])

        return

    #----------------------------------------------#

    def updateAutocomplete(self, text, min_number_of_chars = 5, max_number_of_dropdown_elements = 250):

        # only update if autocomplete button is checked
        if self.button_autocomplete.isChecked():

            # search in nxcals
            if len(text) > min_number_of_chars:
                results = self.threads_panel.ldb.search(text + "%")
            else:
                results = []

            # cut maximum number of elements
            if len(results) > max_number_of_dropdown_elements:
                results = results[:max_number_of_dropdown_elements]

            # set the completer
            self.setQCompleter(results)

        return

    #----------------------------------------------#

    def setQCompleter(self, list_to_inject, ts_completers = True):

        # completer for the lineedit
        self.search_completer = QCompleter(list_to_inject, self)
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        self.lineEdit_query.setCompleter(self.search_completer)

        return

    #----------------------------------------------#

    def initPyTimber(self):

        # update boolean
        self.logging_in_progress = True

        # open waiting widget
        self.waiting_widget = WaitingWidgetNXCALS(app=self.global_parent.app, app_root_path=self.global_parent.app_root_path, parent=self)
        self.waiting_widget.setModal(True)
        self.waiting_widget.show()
        self.waiting_widget.repaint()
        self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        # update label
        self.waiting_widget.updateLabel(" Connecting to NXCALS...")
        self.waiting_widget.repaint()
        self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        # init pytimber on threads panel
        self.threads_panel.initPyTimber()

        return

    #----------------------------------------------#

    def searchQuery(self, verbose = False):

        # wait for pytimber to initialize
        if self.logging_in_progress:
            return

        # message for the first time
        if not self.pytimber_initialized:
            self.initPyTimber()

        # get strings
        query = self.lineEdit_query.text()
        ts1 = self.dateEdit_ts_start.dateTime().toString('yyyy-MM-dd HH:mm:ss.z')
        ts2 = self.dateEdit_ts_end.dateTime().toString('yyyy-MM-dd HH:mm:ss.z')

        # first of all check if query makes sense
        format_is_correct = self.checkQueryFormatting(query, ts1, ts2)

        # start query in new thread
        if format_is_correct:
            self.threads_panel.addThread(query, ts1, ts2)
        else:
            # show message
            message_title = "Error"
            message_text = ("Query format is not valid!")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.threads_panel.window_icon_path))
            message_box.exec()

        return

    #----------------------------------------------#

    def checkQueryFormatting(self, query, ts1, ts2):

        # function to check dates
        def validate_date_format(date_string):
            try:
                datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
                return True
            except ValueError:
                return False

        # function to check if ts2 is newer
        def is_date2_more_recent(date1_str, date2_str):
            format_str = '%Y-%m-%d %H:%M:%S.%f'
            date1 = datetime.strptime(date1_str, format_str)
            date2 = datetime.strptime(date2_str, format_str)
            return date2 > date1

        # check fields are not empty
        if not query or not ts1 or not ts2:
            return False

        # check 1st date
        valid = validate_date_format(ts1)
        if not valid:
            return False

        # check 2nd date
        valid = validate_date_format(ts2)
        if not valid:
            return False

        # check 2nd date is more recent that 1st date
        valid = is_date2_more_recent(ts1, ts2)
        if not valid:
            return False

        return True

    #----------------------------------------------#

    def bindWidgetsTreeView(self, model):

        # reset all connections first
        try:
            self.treeView.disconnect()
        except Exception as xcp:
            print("Exception: {}".format(xcp))

        # binding for changing colors at expansion
        self.treeView.expanded.connect(model.handle_expanded)

        # binding for the click or selection
        self.treeView.selectionModel().selectionChanged.connect(lambda: self.itemFromTreeviewSelectionChanged(model=model))

        # set up the right click menu handler
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(lambda position: self.openRightClickTreeMenu(position = position, model = model))

        return

    #----------------------------------------------#

    def openRightClickTreeMenu(self, position, model, verbose = False):

        # get the clicked element
        indexes = self.treeView.selectedIndexes()

        # skip if we have no selection
        if not indexes:
            return

        # init lists
        index_list = []
        level_list = []
        selected_text_list = []
        query_finished_list = []

        # if there is at least one item
        if len(indexes) > 0:

            # iterate over selected indexes
            for index in indexes:

                # only take into account first column
                if index.column() != 0:
                    continue

                # init level
                level = 0

                # get only first column
                index = index.siblingAtColumn(0)

                # save index to index list
                index_list.append(index)

                # get selected text
                selected_text = str(index.model().itemFromIndex(index).text())
                selected_text_list.append(selected_text)

                # check if query is ongoing
                index_elapsed_time = index.siblingAtColumn(3)
                elapsed_time = str(index_elapsed_time.model().itemFromIndex(index_elapsed_time).text())
                if elapsed_time == "DONE" or elapsed_time == "":
                    query_finished_list.append(True)
                else:
                    query_finished_list.append(False)

                # keep iterating
                while index.parent().isValid():
                    index = index.parent()
                    level += 1

                # save level
                level_list.append(level)

        # for debugging
        if verbose:
            print(f"Index List: {index_list}")
            print(f"Level List: {level_list}")
            print(f"Selected Text List: {selected_text_list}")

        # create the menu
        menu = QMenu()

        # init dict
        self.menu_right_click_dict = {}

        # CASE 1: QUERIES ARE STILL ONGOING
        if not np.all(np.array(query_finished_list) == True):

            # empty action
            self.menu_right_click_dict["queries_ongoing"] = menu.addAction(qta.icon("ei.error"), self.tr("Queries are still ongoing!"))
            self.menu_right_click_dict["queries_ongoing"].setEnabled(False)

        # CASE 2: ALL QUERIES DID FINISH
        else:

            # actions for expanding and collapsing
            self.menu_right_click_dict["expand_all"] = menu.addAction(qta.icon("mdi.arrow-expand-right"), self.tr("Expand all"))
            self.menu_right_click_dict["expand_all"].triggered.connect(lambda: self.expand_all(self.treeView, index_list))
            self.menu_right_click_dict["collapse_all"] = menu.addAction(qta.icon("mdi.arrow-expand-left"), self.tr("Collapse all"))
            self.menu_right_click_dict["collapse_all"].triggered.connect(lambda: self.collapse_all(self.treeView, index_list))

            # action for selection cart
            if not self.global_parent.dict_for_settings["setting_disable_selection_cart"]:
                self.menu_right_click_dict["add_to_selection_cart"] = menu.addAction(qta.icon("ei.shopping-cart"), self.tr("Add to selection cart"))
                self.menu_right_click_dict["add_to_selection_cart"].triggered.connect(lambda: self.callAddSelectionToCart())
                self.menu_right_click_dict["add_to_selection_cart"].setEnabled(True)
            else:
                self.menu_right_click_dict["add_to_selection_cart"] = menu.addAction(qta.icon("ei.error"), self.tr("Add to selection cart"))
                self.menu_right_click_dict["add_to_selection_cart"].triggered.connect(lambda: self.callAddSelectionToCart())
                self.menu_right_click_dict["add_to_selection_cart"].setEnabled(False)

            # action for opening new windows
            if np.all(np.array(level_list) == 2):
                if len(index_list) > 1:
                    self.menu_right_click_dict["open_visualization_in_single_window_merge"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in single window (merge)"))
                    self.menu_right_click_dict["open_visualization_in_single_window_merge"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindowFromNXCALS(index_list, self.treeView.model(), merge=True, auto_multiple_axes=False))
                    self.menu_right_click_dict["open_visualization_in_single_window_merge"].setEnabled(True)
                    self.menu_right_click_dict["open_visualization_in_single_window_merge_multiple_axes"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in single window (merge along multiple axes)"))
                    self.menu_right_click_dict["open_visualization_in_single_window_merge_multiple_axes"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindowFromNXCALS(index_list, self.treeView.model(), merge=True, auto_multiple_axes=True))
                    self.menu_right_click_dict["open_visualization_in_single_window_merge_multiple_axes"].setEnabled(True)
                    self.menu_right_click_dict["open_visualization_in_multiple_windows"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in multiple windows"))
                    self.menu_right_click_dict["open_visualization_in_multiple_windows"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindowFromNXCALS(index_list, self.treeView.model()))
                    self.menu_right_click_dict["open_visualization_in_multiple_windows"].setEnabled(True)
                    self.menu_right_click_dict["open_analysis_in_multiple_windows"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open analysis in multiple windows"))
                    self.menu_right_click_dict["open_analysis_in_multiple_windows"].triggered.connect(lambda: self.global_parent.openNewAnalysisWindowFromNXCALS(index_list, self.treeView.model()))
                    self.menu_right_click_dict["open_analysis_in_multiple_windows"].setEnabled(True)
                else:
                    self.menu_right_click_dict["open_visualization_in_new_window"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in new window"))
                    self.menu_right_click_dict["open_visualization_in_new_window"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindowFromNXCALS(index_list, self.treeView.model()))
                    self.menu_right_click_dict["open_visualization_in_new_window"].setEnabled(True)
                    self.menu_right_click_dict["open_analysis_in_new_window"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open analysis in new window"))
                    self.menu_right_click_dict["open_analysis_in_new_window"].triggered.connect(lambda: self.global_parent.openNewAnalysisWindowFromNXCALS(index_list, self.treeView.model()))
                    self.menu_right_click_dict["open_analysis_in_new_window"].setEnabled(True)

            # action for removing query
            if np.all(np.array(level_list) == 0):
                self.menu_right_click_dict["remove_query"] = menu.addAction(qta.icon("mdi.delete"), self.tr("Remove query"))
                self.menu_right_click_dict["remove_query"].triggered.connect(lambda: self.removeQueryFromTree(index_list))
                self.menu_right_click_dict["remove_query"].setEnabled(True)
            else:
                self.menu_right_click_dict["remove_query"] = menu.addAction(qta.icon("ei.error"), self.tr("Remove query"))
                self.menu_right_click_dict["remove_query"].triggered.connect(lambda: self.removeQueryFromTree(index_list))
                self.menu_right_click_dict["remove_query"].setEnabled(False)

        # update view
        menu.exec(self.treeView.viewport().mapToGlobal(position))

        return

    #----------------------------------------------#

    def callAddSelectionToCart(self):

        # just call add selected
        if self.global_parent:
            if self.global_parent.selection_tab:
                if self.global_parent.selection_tab.isEnabled():
                    self.global_parent.selection_tab.addSelected()

        return

    #----------------------------------------------#

    def removeQueryFromTree(self, index_list):

        # reverse list (to avoid problems when deleting rows)
        sorted_indexes = sorted(index_list, key=lambda index: index.row(), reverse=True)

        # remove the queries
        for index in sorted_indexes:
            if index.isValid():
                self.treeView.model().removeRow(index.row(), index.parent())

        return

    #----------------------------------------------#

    def headerProcessing(self):

        # header changes
        self.treeView.setHeaderHidden(False)
        self.treeView.header().setVisible(True)

        # set meta columns hidden
        headers_visible_length = len(self.treeView_model.header_labels)

        # set header widths
        for column in range(0, headers_visible_length):
            self.treeView.setColumnWidth(column, getPixelWidthFromQLabel(self.treeView_model.header_labels[column]))

        return

    #----------------------------------------------#

    def initTreeModel(self):

        # declare treeview model
        self.treeView_model = NXCALSTreeViewModel(parent=self, global_parent=self.global_parent)

        # set the model
        self.treeView.setModel(self.treeView_model)

        # bindings for the tree
        self.bindWidgetsTreeView(self.treeView_model)

        # adjust headers
        self.headerProcessing()

        # show tree
        self.treeView.update()
        self.treeView.show()

        return

    #----------------------------------------------#

    def clearTreeView(self):

        # only clear if there are no threads running
        if not self.threads_panel.query_threads:

            # clear model
            self.treeView.model().clear()

            # init variables
            self.treeView_model = None

            # reset all connections
            try:
                self.treeView.disconnect()
            except Exception as xcp:
                print("Exception: {}".format(xcp))

            # init model
            self.initTreeModel()

        # message error if threads are running
        else:

            # show message
            message_title = "Error"
            message_text = ("Unable to init the NXCALS treeview as there are threads still running!")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.threads_panel.window_icon_path))
            message_box.exec()

        return

    #----------------------------------------------#

    def refreshTreeView(self, item, query, response_dict, error):

        # add the query to the tree
        self.treeView_model.add_results_to_query(item, query, response_dict, error)

        # bindings for the tree
        self.bindWidgetsTreeView(self.treeView_model)

        # show tree
        self.treeView.update()
        self.treeView.show()

        return

    #----------------------------------------------#

    def itemFromTreeviewSelectionChanged(self, model, verbose = True):

        # get selected indexes
        indexes = self.treeView.selectedIndexes()

        # discard case 1: indexes is none
        if not indexes:
            self.global_parent.hideRightPanel(from_top_node=True, model=model)
            return

        # discard case 2: more than one item is selected
        if len(self.treeView.selectedIndexes()) / (len(self.treeView_model.header_labels)) > 1:
            self.global_parent.hideRightPanel(from_top_node=True, model=model)
            return

        # get true index (first column)
        index = indexes[0]

        # update in case everything is OK
        self.global_parent.updateRightPanel(index, model=model, tree_type="nxcals")

        return

    #----------------------------------------------#

    def iterateModelFromNode(self, model, parent=QModelIndex()):

        # iterate over rows
        for row in range(model.rowCount(parent)):

            # get first column
            index = model.index(row, 0, parent)
            item = model.itemFromIndex(index)

            # determine if it should be added
            self.appendToSelectionList(model, index)

        return

    #----------------------------------------------#

    def appendToSelectionList(self, model, index):

        # does it have children?
        does_it_have_children = model.hasChildren(index)

        # if it has no children then it is a bottom node
        if not does_it_have_children:

            # get data
            data = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)

            # get display name
            display_name = model.itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)

            # get full path made of display names
            full_path = self.get_parent_display_names(model, index)

            # if there is no data just skip
            if data.size == 0:
                return

            # get dataframe and attributes
            dataframe, attributes, chunk_size = self.global_parent.createDfFromNXCALS(data)

            # append the important stuff
            self.df_list_to_selection.append(dataframe)
            self.metadata_list_to_selection.append([display_name, str(dataframe.shape), None, str(dataframe.shape), full_path, "NXCALS", get_index_type(attributes = attributes, df = dataframe, return_dtype_otherwise = True)])
            self.chunk_size_list.append(chunk_size)

        # keep iterating
        else:

            # iterate over model
            self.iterateModelFromNode(model, index)

        return

    #----------------------------------------------#

    def getItemsForSelectionPanel(self):

        # init output lists
        self.df_list_to_selection = []
        self.metadata_list_to_selection = []
        self.chunk_size_list = []

        # get the model
        model = self.treeView_model

        # get selected indexes
        indexes = self.treeView.selectedIndexes()

        # check if we have selected at least one item
        if indexes:

            # get number of items
            n_items = round(len(self.treeView.selectedIndexes()) / (len(self.treeView_model.header_labels)))

            # iterate over items
            for n in range(0, n_items):

                # get true index
                i = n * (len(self.treeView_model.header_labels))

                # get index
                index = indexes[i]

                # guarantee that model is loaded
                expanded_indexes = self.expand_all_tracking(self.treeView, [index])
                self.collapse_all_tracking(self.treeView, [index], expanded_indexes)

                # determine if it should be added
                self.appendToSelectionList(model, index)

        return self.df_list_to_selection, self.metadata_list_to_selection, self.chunk_size_list

    #----------------------------------------------#

    def expand_all(self, tree_view, indexes):
        for index in indexes:
            tree_view.expand(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.more_children(child_index.model(), child_index):
                    self.expand_all(tree_view, [child_index])

    def expand_all_tracking(self, tree_view, indexes, expanded_indexes=None):
        if expanded_indexes is None:
            expanded_indexes = set()
        for index in indexes:
            if not tree_view.isExpanded(index):
                tree_view.expand(index)
                expanded_indexes.add(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.more_children(child_index.model(), child_index):
                    self.expand_all_tracking(tree_view, [child_index], expanded_indexes)
        return expanded_indexes

    #----------------------------------------------#

    def collapse_all(self, tree_view, indexes):
        for index in indexes:
            tree_view.collapse(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.more_children(child_index.model(), child_index):
                    self.collapse_all(tree_view, [child_index])

    def collapse_all_tracking(self, tree_view, indexes, expanded_indexes):
        for index in indexes:
            if index in expanded_indexes:
                tree_view.collapse(index)
                expanded_indexes.remove(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.more_children(child_index.model(), child_index):
                    self.collapse_all_tracking(tree_view, [child_index], expanded_indexes)

    #----------------------------------------------#

    def more_children(self, model, index):
        return model.rowCount(index) == 0

    #----------------------------------------------#

    def get_parent_display_names(self, model, index, exclude_root=True):
        current_index = index
        display_names = []
        while current_index.isValid():
            item = model.itemFromIndex(current_index)
            display_name = item.data(Qt.ItemDataRole.DisplayRole)
            parent_index = current_index.parent()
            if exclude_root and not parent_index.isValid():
                break
            display_names.insert(0, display_name)
            current_index = parent_index
        return '/'.join(display_names)

    #----------------------------------------------#

#################################################################
#################################################################