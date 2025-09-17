#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.utils.nxcals_query_thread import NXCALSQueryThread
from davit.utils.nxcals_threads_panel_table_model import NXCALSThreadsPanelTableModel

# SPECIFIC IMPORTS

import time as native_time

#################################################################
#################################################################

class NXCALSThreadsPanel(QDialog):

    #----------------------------------------------#

    def __init__(self, app, app_root_path = None, window_icon_path = None, parent = None, qta_str_icon = "mdi.spider-thread"):

        # inherit from QWidget
        QDialog.__init__(self)

        # main attributes
        self.app = app
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.parent = parent
        self.qta_str_icon = qta_str_icon

        # own attributes
        self.selected_row = None
        self.id_counter = 0
        self.row_height = 25
        self.max_threads = 25
        self.column_names = ["Query", "TS1", "TS2", "Elapsed Time"]
        self.last_stored_width = 0
        self.menu_right_click_dict = {}

        # main widgets
        self.tableView = None

        # pytimber session
        self.ldb = None

        # important variables
        self.query_threads = []
        self.data = []
        self.init_timestamps = []
        self.ids = []
        self.tree_items = []

        # get widths
        self.header_labels_widths = [getPixelWidthFromQLabel(i, offset=35) for i in self.column_names]

        # set title and icon
        self.setWindowTitle("NXCALS Query Threads Panel")
        if self.window_icon_path:
            self.setWindowIcon(QIcon(self.window_icon_path))
        else:
            self.setWindowIcon(qta.icon(self.qta_str_icon))

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "nxcals_threads_panel.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # size of the widget
        self.setMinimumSize(600, 400)
        self.setMaximumSize(1000, 800)

        # init qtimer for the timers of the table
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateTableGivenTimer)
        self.timer.start()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # layout of the form
        self.verticalLayout_frame_holder = QVBoxLayout(self)
        self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
        self.verticalLayout_frame_holder.setContentsMargins(15, 25, 15, 15)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_holder.setObjectName("frame_holder")
        self.verticalLayout_frame_holder.addWidget(self.frame_holder)

        # main layout
        self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
        self.verticalLayout_stack.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_stack.setSpacing(20)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # info label
        self.label_info = QLabel(self.frame_holder)
        self.label_info.setObjectName("label_info")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label_info.setWordWrap(True)
        self.label_info.setText("In this panel you can find all the NXCALS running threads for the introduced queries. Note that you can stop/quit queries by right-clicking on the table.")
        self.verticalLayout_stack.addWidget(self.label_info)

        # bottom frame
        self.frame_bottom = QFrame(self.frame_holder)
        self.frame_bottom.setObjectName("frame_bottom")
        self.verticalLayout_stack.addWidget(self.frame_bottom)

        # bottom layout
        self.horizontalLayout_frame_bottom = QHBoxLayout(self.frame_bottom)
        self.verticalLayout_stack.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_stack.setSpacing(10)
        self.horizontalLayout_frame_bottom.setObjectName("horizontalLayout_frame_bottom")
        
        # create table
        self.tableView = QTableView(self.frame_bottom)
        self.tableView.setFrameShape(QFrame.Shape.StyledPanel)
        self.tableView.setWordWrap(False)
        self.tableView.setFrameShadow(QFrame.Shadow.Plain)
        self.tableView.setDragEnabled(False)
        self.tableView.setAlternatingRowColors(False)
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setShowGrid(True)
        self.tableView.setGridStyle(Qt.PenStyle.SolidLine)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setFixedHeight(self.row_height)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setHighlightSections(False)
        self.tableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.verticalHeader().setStretchLastSection(False)
        self.tableView.verticalHeader().setMinimumSectionSize(self.row_height)
        self.tableView.verticalHeader().setDefaultSectionSize(self.row_height)
        self.horizontalLayout_frame_bottom.addWidget(self.tableView)

        # init the table
        self.initTable()

        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def bindWidgetsTable(self, enable_menu = False, enable_sel_rows = False):

        # just in case we have menu
        if enable_menu:

            # reset all connections first
            try:
                self.tableView.disconnect()
            except Exception as xcp:
                print("Exception: {}".format(xcp))

            # create binding for the menu
            self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tableView.customContextMenuRequested.connect(lambda pos: self.tableMenuHandler(pos, table=self.tableView))

        # this helps with the timer UI bugs
        if enable_sel_rows:

            # create binding for the selection
            self.tableView.selectionModel().selectionChanged.connect(lambda selected: self.updateSelectedRow(selected))

        return

    #----------------------------------------------#

    def updateSelectedRow(self, selected):

        # get selected indexes
        selected_indexes = selected.indexes()

        # update row
        if selected_indexes:
            self.selected_row = selected_indexes[0].row()
        else:
            self.selected_row = None

        return

    #----------------------------------------------#

    def trueIndexFromSelectedIndexes(self, selected_indexes):

        # this variable turns true if an empty row is selected
        discard_selection = False

        # get number of items
        n_items = round(len(selected_indexes) / len(self.column_names))

        # iterate over items
        for n in range(0, n_items):

            # get true index
            i = n * len(self.column_names)

            # get index
            index = selected_indexes[i]

            # get row
            row = index.row()

            # check selection
            if self.table_model._data[row] == [""]*len(self.column_names):
                discard_selection = True
                return None, discard_selection

        return row, discard_selection

    #----------------------------------------------#

    def tableMenuHandler(self, pos, table = None):

        # get indexes
        selected_indexes = table.selectedIndexes()

        # only if at least one row is selected
        if selected_indexes:

            # create menu for actions
            menu = QMenu()

            # get the true index
            id, discard_selection = self.trueIndexFromSelectedIndexes(selected_indexes)

            # action for quitting the threads
            if not discard_selection:
                self.menu_right_click_dict["quit"] = menu.addAction(qta.icon("mdi.delete"), self.tr("Quit"))
                self.menu_right_click_dict["quit"].triggered.connect(lambda: self.removeThread(self.ids[id]))

            # get global position
            globalPos = table.viewport().mapToGlobal(pos)

            # get the selected item
            selectedItem = menu.exec(globalPos)

        return

    #----------------------------------------------#

    def initTable(self):

        # init data
        data = []
        for i in range(0,self.max_threads):
            data.append([""]*len(self.column_names))

        # set model
        self.table_model = NXCALSThreadsPanelTableModel(data = data, header_labels = self.column_names)
        self.tableView.setModel(self.table_model)
        self.tableView.update()

        # show the table
        self.tableView.show()

        return

    #----------------------------------------------#

    def ensure_nxcals_dependencies(self):
        import sys
        import subprocess
        subprocess.run([sys.executable, "-m", "cmmnbuild_dep_manager", "resolve"], check=True)
        return

    #----------------------------------------------#

    def initPyTimber(self):

        # set up the pytimber environment
        if not self.ldb:
            try:
                self.ldb = pytimber.LoggingDB(source="nxcals")
                self.parent.closeWaitingWidget()
            except Exception as xcp:
                print("Exception at initPyTimber: {}".format(xcp))
                print("Trying to run cmmnbuild_dep_manager..")
                self.ensure_nxcals_dependencies()
                self.parent.closeWaitingWidget()
                self.parent.global_parent.show_java_error()

        return

    #----------------------------------------------#

    def addThread(self, query, ts1, ts2):

        # first check if we have too many threads
        if len(self.query_threads) >= self.max_threads:

            # show error message
            message_title = "Error"
            message_text = ("The maximum number of threads has been reached. Please wait for some queries to finish.")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec()
            return

        # start query in new thread
        thread = NXCALSQueryThread(self.ldb, query, ts1, ts2, self.id_counter)

        # add thread to the list
        self.query_threads.append(thread)

        # update the data
        self.data.append([query, ts1, ts2, "00:00:00"])

        # store init timestamp
        self.init_timestamps.append(native_time.time())

        # store the id
        self.ids.append(self.id_counter)

        # bindings for the thread
        thread.finished.connect(self.handleQueryResult)

        # UPDATE TABLE AND TREE
        if True:

            # update the tree with new query
            self.tree_items.append(self.parent.treeView_model.add_query(query, ts1, ts2, "00:00:00"))

            # update the table with new thread
            self.updateTable()

        # update the id counter
        self.id_counter += 1

        # start the thread
        thread.start()

        return

    #----------------------------------------------#

    def updateTable(self):

        # init data
        data = []
        for i in range(0,self.max_threads):
            if i < len(self.query_threads):
                data.append(self.data[i])
            else:
                data.append([""]*len(self.column_names))

        # set model
        self.table_model = NXCALSThreadsPanelTableModel(data = data, header_labels = self.column_names)
        self.tableView.setModel(self.table_model)
        self.tableView.update()

        # show the table
        self.tableView.show()

        # update bindings
        self.bindWidgetsTable()

        # fix visual bug due to UI changes
        if self.selected_row is not None:
            self.tableView.selectRow(self.selected_row)

        return

    #----------------------------------------------#

    def updateTableGivenTimer(self):

        # only if we have at least one thread
        if self.query_threads:

            # get current time
            current_time = native_time.time()

            # init data
            for i in range(0,self.max_threads):
                if i < len(self.query_threads):
                    elapsed_time = current_time - self.init_timestamps[i]
                    self.data[i][-1] = self.formatElapsedTime(elapsed_time)
                else:
                    break

            # UPDATE TABLE AND TREE
            if True:

                # update tree
                if self.tree_items and self.ids:
                    for id in self.ids:
                        true_index = self.ids.index(id)
                        self.parent.treeView_model.update_query(self.tree_items[true_index], self.data[true_index][-1])

                # update table with new timestamps
                self.updateTable()

        return

    #----------------------------------------------#

    def formatElapsedTime(self, elapsed_time):

        # hours:minutes:seconds formatting
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return time_str

    #----------------------------------------------#

    def handleQueryResult(self, result, verbose = False):

        # disentangle the result
        response_dict, query, ts1, ts2, id, error = result

        # for debugging
        if verbose:
            print("QUERY = {}, TS1 = {}, TS2 = {}".format(query, ts1, ts2))
            print(response_dict)

        # UPDATE TABLE AND TREE
        if True:

            # just a check
            if id in self.ids:

                # refresh the treeview based on the result
                self.parent.refreshTreeView(self.tree_items[self.ids.index(id)], query, response_dict, error)

                # remove the thread
                self.removeThread(id)

        return

    #----------------------------------------------#

    def removeThread(self, id, terminate_thread = False):

        # retrieve index
        try:
            index = self.ids.index(id)
        except:
            return

        # retrieve thread
        thread = self.query_threads[index]

        # stop the thread and delete it permanently
        if terminate_thread:
            self.query_threads[index].terminate()
            self.query_threads[index].wait()
        else:
            self.query_threads[index].quit()
            self.query_threads[index].wait()
            self.query_threads[index].deleteLater()

        # delete thread
        del self.query_threads[index]

        # delete the rest
        del self.data[index]
        del self.init_timestamps[index]
        del self.ids[index]
        del self.tree_items[index]

        # update table
        self.updateTable()

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

    def forceResize(self):

        # get width
        stored_width = self.frame_bottom.frameGeometry().width()

        # force the resizing
        self.resizeTable(self.tableView, self.column_names, self.header_labels_widths, stored_width, parent=self.frame_bottom)
        self.tableView.show()
        self.last_stored_width = stored_width

        return

    #----------------------------------------------#

    def resizeEvent(self, event):

        # resize table when resizing the widget
        if self.tableView:
            stored_width = self.frame_bottom.frameGeometry().width()
            if np.abs(stored_width - self.last_stored_width) > 0:
                self.resizeTable(self.tableView, self.column_names, self.header_labels_widths, stored_width, parent=self.frame_bottom)
                self.tableView.show()
                self.last_stored_width = stored_width

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