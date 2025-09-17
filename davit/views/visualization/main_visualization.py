#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.views.visualization.table_tab import TableTab
from davit.views.visualization.image_tab import ImageTab
from davit.views.visualization.plot_tab import PlotTab
from davit.views.visualization.scatter_tab import ScatterTab

#################################################################
#################################################################

class MainVisualization(QWidget):

    #----------------------------------------------#

    def __init__(self, app, dataframe, attributes, display_name, init_build, last_selected_sub_tab = 0, app_root_path = None, window_icon_path = None, parent = None, global_parent = None, popup_window = False, qta_str_icon = "", color_dict = {}, mouse_mode_1_button = False, pyqtgraph_default_downsample = False, sticky_options = True, display_strings_on_x_axis = False, ncurves_at_init = 10, min_big_data_sample_size = 1_000_000, chunk_size = 100_000, max_n_columns = 20, auto_multiple_axes = False, use_progress_bar = True):

        # inherit from QWidget
        QWidget.__init__(self)

        # main attributes
        self.app = app
        self.dataframe = dataframe
        self.attributes = attributes
        self.display_name = display_name
        self.init_build = init_build
        self.last_selected_sub_tab = last_selected_sub_tab
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.parent = parent
        self.global_parent = global_parent
        self.popup_window = popup_window
        self.qta_str_icon = qta_str_icon
        self.color_dict = color_dict
        self.mouse_mode_1_button = mouse_mode_1_button
        self.pyqtgraph_default_downsample = pyqtgraph_default_downsample
        self.sticky_options = sticky_options
        self.display_strings_on_x_axis = display_strings_on_x_axis
        self.ncurves_at_init = ncurves_at_init
        self.min_big_data_sample_size = min_big_data_sample_size
        self.chunk_size = chunk_size
        self.max_n_columns = max_n_columns
        self.auto_multiple_axes = auto_multiple_axes
        self.use_progress_bar = use_progress_bar

        # scale max_n_columns
        self.max_n_columns = self.max_n_columns * 1000

        # should we rename rows and columns if they are equal?
        self.rename_equal_rows = True
        self.rename_equal_cols = True

        # own attributes
        self.tab_is_built = False
        self.too_many_columns = False
        self.win_id = None
        self.tab_names = ["Plot", "Table", "Image", "Scatter"]
        self.big_data_mode = False

        # main widgets
        self.tabWidget = None
        self.table_tab = None
        self.image_tab = None
        self.plot_tab = None
        self.scatter_tab = None

        # minimum size
        if self.popup_window:
            self.setMinimumSize(320, 180)

        # only if it is a popup
        if popup_window:
            self.setWindowTitle("Visualization Window (Popup)")
            self.setWindowIcon(QIcon(self.window_icon_path))
            self.windowAdjustmentAndResizing()

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "main_visualization.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # build up the layouts only when required
        if self.init_build:
            self.buildTab()

        return

    #----------------------------------------------#

    def buildTab(self):

        # 1st check (too many columns?)
        if self.dataframe.shape[1] >= self.max_n_columns and not (self.global_parent and self.global_parent.auto_transpose):
            message_title = "Error"
            message_text = "Current dataframe has too many columns. Please, try to transpose it (top-right corner button) in order to properly visualize the data."
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self.global_parent)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            self.too_many_columns = True
            self.setStyleSheet("QTabWidget{background-color: #F1A2A2;}")

        # initial checks
        self.initChecks()

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # should we transpose at init?
        if self.global_parent:
            if self.global_parent.auto_transpose:
                self.transposeDf(not_from_click=True)

        # update boolean
        self.tab_is_built = True

        # update progress bar
        if self.big_data_mode and self.use_progress_bar:
            self.progress_dialog.close()
            del self.progress_dialog

        return

    #----------------------------------------------#

    def initChecks(self):

        # too many cols?
        if not self.too_many_columns:

            # check if we should enter into big data mode
            self.checkAndSetBigDataMode(self.dataframe)

            # use progress bar for big data mode
            if self.big_data_mode and self.use_progress_bar:
                self.progress_dialog = QProgressDialog("Loading visualization tab...", None, 0, 6)
                self.progress_dialog.setMaximumHeight(300)
                self.progress_dialog.setMaximumWidth(1000)
                self.progress_dialog.setMinimumHeight(75)
                self.progress_dialog.setMinimumWidth(600)
                self.progress_dialog.setAutoClose(False)
                self.progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
                self.progress_dialog.closeEvent = closeEventIgnore
                self.progress_dialog.setWindowTitle("Progress")
                self.progress_dialog.setWindowIcon(qta.icon("mdi6.timer-sand"))
                self.progress_dialog.show()
                self.progress_dialog.repaint()
                self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                self.progress_dialog.setValue(0)
                self.progress_dialog.repaint()
                sleep(0.1)
                self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                sleep(0.025)

            # check column names make sense
            if self.rename_equal_cols:
                columnNameFormatting(self.dataframe)

            # update progress bar
            if self.big_data_mode and self.use_progress_bar:
                self.progress_dialog.setValue(1)
                self.progress_dialog.repaint()
                sleep(0.025)
                self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                sleep(0.025)

            # update progress bar
            if self.big_data_mode and self.use_progress_bar:
                self.progress_dialog.setValue(2)
                self.progress_dialog.repaint()
                sleep(0.025)
                self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                sleep(0.025)

        return

    #----------------------------------------------#

    def windowAdjustmentAndResizing(self):

        # get the current screen size of the user
        screen_object = self.app.primaryScreen()
        screen_size = screen_object.size()
        screen_rect = screen_object.availableGeometry()

        # resize main window
        self.resize(
            round(screen_rect.width() * 6 / 10),
            round(screen_rect.height() * 6 / 10),
        )

        # center main window
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(screen_rect.center())
        self.move(frame_geometry.topLeft())

        return

    #----------------------------------------------#

    def checkAndSetBigDataMode(self, df):

        # get the largest shape
        if df.shape[0] >= df.shape[1]:
            largest_shape = df.shape[0]
            largest_is = 0
        else:
            largest_shape = df.shape[1]
            largest_is = 1

        # use big data or not
        if largest_shape >= 1_000_000 * self.min_big_data_sample_size:
            self.big_data_mode = True
            if largest_is == 0:
                self.rename_equal_rows = False
            elif largest_is == 1:
                self.rename_equal_cols = False
        else:
            self.big_data_mode = False

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # layout of the form
        self.verticalLayout_frame_holder = QVBoxLayout(self)
        self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
        self.verticalLayout_frame_holder.setContentsMargins(10, 10, 10, 10)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_holder.setObjectName("frame_holder")
        self.verticalLayout_frame_holder.addWidget(self.frame_holder)

        # main layout
        self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
        self.verticalLayout_stack.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_stack.setSpacing(0)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # create the tab widget
        self.tabWidget = QTabWidget(self.frame_holder)
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout_stack.addWidget(self.tabWidget)

        # init tab widgets
        self.plot_tab = PlotTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path = self.app_root_path, window_icon_path = self.window_icon_path, parent = self.tabWidget, global_parent = self.global_parent, color_dict = self.color_dict, mouse_mode_1_button = self.mouse_mode_1_button, pyqtgraph_default_downsample = self.pyqtgraph_default_downsample, sticky_options = self.sticky_options, display_strings_on_x_axis = self.display_strings_on_x_axis, ncurves_at_init = self.ncurves_at_init, min_big_data_sample_size = self.min_big_data_sample_size, chunk_size = self.chunk_size, big_data_mode = self.big_data_mode, qta_str_icon=self.qta_str_icon, auto_multiple_axes=self.auto_multiple_axes)
        self.table_tab = TableTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path = self.app_root_path, window_icon_path = self.window_icon_path, parent = self.tabWidget, global_parent = self.global_parent, min_big_data_sample_size = self.min_big_data_sample_size, chunk_size = self.chunk_size, big_data_mode = self.big_data_mode)
        self.image_tab = ImageTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path = self.app_root_path, window_icon_path = self.window_icon_path, parent = self.tabWidget, global_parent = self.global_parent, color_dict = self.color_dict)
        self.scatter_tab = ScatterTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path = self.app_root_path, window_icon_path = self.window_icon_path, parent = self.tabWidget, global_parent = self.global_parent, color_dict = self.color_dict)

        # add tabs
        self.tabWidget.addTab(self.plot_tab, self.tab_names[0])
        self.tabWidget.addTab(self.table_tab, self.tab_names[1])
        self.tabWidget.addTab(self.image_tab, self.tab_names[2])
        self.tabWidget.addTab(self.scatter_tab, self.tab_names[3])

        # add the transpose button
        if self.global_parent:
            self.transpose_button = CustomCornerWidget(self.display_name, self.dataframe.shape[0], self.dataframe.shape[1], auto_transpose=self.global_parent.auto_transpose, parent=self.tabWidget)
        else:
            self.transpose_button = CustomCornerWidget(self.display_name, self.dataframe.shape[0], self.dataframe.shape[1], parent=self.tabWidget)
        self.tabWidget.setCornerWidget(self.transpose_button, Qt.Corner.TopRightCorner)

        # disable some tabs for big data mode
        if self.big_data_mode:
            self.enableOnlyTableAndPlot()

        # disable all tabs but the table in case we have string or byte types
        self.numericTypeCheck()

        # update progress bar
        if self.big_data_mode and self.use_progress_bar:
            self.progress_dialog.setValue(3)
            self.progress_dialog.repaint()
            sleep(0.025)
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            sleep(0.025)

        # init tab
        self.tabWidget.setCurrentIndex(self.last_selected_sub_tab)

        # get current tab widget
        current_tab_widget = self.tabWidget.widget(self.last_selected_sub_tab)

        # build tab only for the selected index
        if not self.too_many_columns:
            if current_tab_widget is not None:
                if hasattr(current_tab_widget, "tab_is_built"):
                    if not current_tab_widget.tab_is_built:
                        current_tab_widget.buildTab(self.dataframe)

        # update progress bar
        if self.big_data_mode and self.use_progress_bar:
            self.progress_dialog.setValue(4)
            self.progress_dialog.repaint()
            sleep(0.025)
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
            sleep(0.025)

        return

    #----------------------------------------------#

    def enableOnlyTableAndPlot(self, enable_function = False):

        # for the moment we disable this
        if enable_function:

            # disable the rest of tabs
            self.tabWidget.setTabEnabled(2, False)
            self.tabWidget.setTabEnabled(3, False)
            self.tabWidget.setTabToolTip(2, "Not implemented yet for big datasets!")
            self.tabWidget.setTabToolTip(3, "Not implemented yet for big datasets!")

            # update index
            if self.last_selected_sub_tab >= 2:
                self.last_selected_sub_tab = 0
                if self.global_parent:
                    self.global_parent.last_selected_sub_tab_visualization = 0

        return

    #----------------------------------------------#

    def numericTypeCheck(self):

        # numeric type check
        if not np.issubdtype(self.dataframe.to_numpy().dtype, np.number):

            # disable all tabs but the table
            self.tabWidget.setTabEnabled(0, False)
            self.tabWidget.setTabEnabled(2, False)
            self.tabWidget.setTabEnabled(3, False)
            self.tabWidget.setTabToolTip(0, "Data type is not numeric!")
            self.tabWidget.setTabToolTip(2, "Data type is not numeric!")
            self.tabWidget.setTabToolTip(3, "Data type is not numeric!")

            # update index
            if self.last_selected_sub_tab != 1:
                self.last_selected_sub_tab = 1
                if self.global_parent:
                    self.global_parent.last_selected_sub_tab_visualization = 1

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # signal that gets activated when the current tab changes
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # binding for transposing the dataframe
        self.transpose_button.clicked.connect(self.transposeDf)

        return

    #----------------------------------------------#

    def unbindWidgets(self):

        # disconnect all
        self.tabWidget.currentChanged.disconnect(self.tabChanged)
        self.transpose_button.clicked.disconnect(self.transposeDf)

        return

    #----------------------------------------------#

    def transposeDf(self, not_from_click=False):

        # 1st check (too many columns?)
        if self.dataframe.shape[0] >= self.max_n_columns:
            message_title = "Error"
            message_text = "Unable to transpose the dataframe as the resulting matrix would have too many columns."
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            if self.global_parent:
                self.global_parent.auto_transpose = False
                self.transpose_button.update_transpose_button_style(self.global_parent.auto_transpose)
            return

        # only if 1st check passed
        self.too_many_columns = False
        self.setStyleSheet("QTabWidget{background-color: #FFFFFF;}")

        # disconnect all signals
        self.unbindWidgets()

        # transpose
        self.dataframe = self.dataframe.T

        # initial checks with new shape
        self.initChecks()

        # remove all previous tabs
        self.tabWidget.clear()

        # init tab widgets
        self.plot_tab = PlotTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget, global_parent=self.global_parent, color_dict=self.color_dict, mouse_mode_1_button=self.mouse_mode_1_button, pyqtgraph_default_downsample=self.pyqtgraph_default_downsample, sticky_options = self.sticky_options, display_strings_on_x_axis = self.display_strings_on_x_axis, ncurves_at_init=self.ncurves_at_init, min_big_data_sample_size=self.min_big_data_sample_size, chunk_size=self.chunk_size, big_data_mode=self.big_data_mode, qta_str_icon=self.qta_str_icon, auto_multiple_axes=self.auto_multiple_axes)
        self.table_tab = TableTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget, global_parent=self.global_parent, min_big_data_sample_size=self.min_big_data_sample_size, chunk_size=self.chunk_size, big_data_mode=self.big_data_mode)
        self.image_tab = ImageTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget, global_parent=self.global_parent, color_dict=self.color_dict)
        self.scatter_tab = ScatterTab(self.app, pd.DataFrame([]), self.attributes, False, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget, global_parent=self.global_parent, color_dict=self.color_dict)

        # add tabs
        self.tabWidget.addTab(self.plot_tab, self.tab_names[0])
        self.tabWidget.addTab(self.table_tab, self.tab_names[1])
        self.tabWidget.addTab(self.image_tab, self.tab_names[2])
        self.tabWidget.addTab(self.scatter_tab, self.tab_names[3])

        # disable some tabs for big data mode
        if self.big_data_mode:
            self.enableOnlyTableAndPlot()

        # disable all tabs but the table in case we have string or byte types
        self.numericTypeCheck()

        # init tab
        self.tabWidget.setCurrentIndex(self.last_selected_sub_tab)

        # get current tab widget
        current_tab_widget = self.tabWidget.widget(self.last_selected_sub_tab)

        # build tab for the selected index
        if not self.too_many_columns:
            if not current_tab_widget.tab_is_built:
                current_tab_widget.buildTab(self.dataframe)

        # bind signals again
        self.bindWidgets()

        # update text in transpose widget
        self.transpose_button.label_shape.setText(f"({self.dataframe.shape[0]}, {self.dataframe.shape[1]})")

        # save auto transpose options for next visualizations
        if not not_from_click:
            if self.global_parent:
                self.global_parent.auto_transpose = not self.global_parent.auto_transpose
                self.transpose_button.update_transpose_button_style(self.global_parent.auto_transpose)

        # process events
        self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        return

    #----------------------------------------------#

    def tabChanged(self, tab_index):

        # update tab name and index
        current_tab_name = self.tab_names[tab_index]
        current_tab_index = tab_index

        # save selected sub tab
        self.last_selected_sub_tab = tab_index

        # update tab at the parent side
        if self.global_parent:
            self.global_parent.last_selected_sub_tab_visualization = tab_index

        # get current tab widget
        current_tab_widget = self.tabWidget.widget(current_tab_index)

        # build the tab
        if not self.too_many_columns:
            if current_tab_widget is not None:
                if not current_tab_widget.tab_is_built:
                    current_tab_widget.buildTab(self.dataframe)

        return

    #----------------------------------------------#
    
    def removeTabs(self):

        # remove tabs
        if self.tabWidget:
            self.tabWidget.blockSignals(True)
            for tab in range(0, self.tabWidget.count()):
                widget = self.tabWidget.widget(0)
                widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                widget.close()
                self.tabWidget.removeTab(0)
                del widget
            self.table_tab = None
            self.plot_tab = None
            self.image_tab = None
            self.scatter_tab = None
            self.tabWidget.blockSignals(False)

        return
    
    #----------------------------------------------#

    def closeEvent(self, evt):
                
        # manually close tabs
        self.removeTabs()

        # only for popups
        if self.win_id != None:

            # print
            print("Closing main_visualization window with id={}...".format(self.win_id))

            # manually deleting the key
            if self.parent:
                try:
                    del self.parent.visualization_tab_new_windows[self.win_id]
                except Exception as xcp:
                    print(xcp)

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################
