#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.views.visualization.main_visualization import MainVisualization
from davit.views.selection.main_selection import MainSelection
from davit.views.analysis.main_analysis import MainAnalysis
from davit.views.general.hdf5_tree_view import HDF5TreeView
from davit.views.general.nxcals_tree_view import NXCALSTreeView
from davit.views.general.postmortem_tree_view import PostMortemTreeView
from davit.views.general.filters_window import FiltersWindow
from davit.views.general.waiting_widget import WaitingWidget
from davit.views.general.waiting_widget_create_df import WaitingWidgetCreateDf
from davit.views.general.settings_preferences_view import SettingsPreferencesView
from davit.views.general.attributes_window import AttributesWindow
from davit.views.monitoring.system_monitor_window import SystemMonitorWindow

#################################################################
#################################################################

def obtain_real_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(os.path.dirname(__file__))))

#################################################################
#################################################################

class MainWindow(QMainWindow):

    #----------------------------------------------#

    def __init__(self, app, window_title = "DAVIT", window_icon_path = "", screen_resize_factor = 4/5, app_root_path = None, qsettings_company_name = "cern-martinja", qsettings_app_name = "davit", default_hdf5_path = "", qta_str_icon = "mdi.alpha-b-circle", startup_dir_to_open = ""):

        # inherit from QMainWindow
        QMainWindow.__init__(self)

        # accept drops for the hdf5 files
        self.setAcceptDrops(True)

        # set defaults
        self.default_settings = {
            "setting_disable_selection_cart": 0,
            "setting_auto_merge_group": 0,
            "min_big_data_sample_size": 2,
            "max_n_columns": 20,
            "setting_enable_1_button_mouse_mode": 0,
            "setting_enable_downsampling_plots": 0,
            "setting_sticky_options": 1, # always true (no configurable)
            "setting_display_strings_on_x_axis": 0,
            "ncurves_at_init": 10,
            "setting_enable_system_monitor": 0,
            "refresh_rate_system_monitor": 1,
            "color_background": "#000000",
            "color_foreground_palette_name": "colorblind",
        }

        # main attributes
        self.app = app
        self.app_root_path = app_root_path
        self.window_title = window_title
        self.window_icon_path = window_icon_path
        self.screen_resize_factor = screen_resize_factor
        self.qsettings_company_name = qsettings_company_name
        self.qsettings_app_name = qsettings_app_name
        self.default_hdf5_path = default_hdf5_path
        self.qta_str_icon = qta_str_icon
        self.startup_dir_to_open = startup_dir_to_open

        # own attributes
        self.last_index_tree_view_hdf5 = None
        self.last_index_tree_view_nxcals = None
        self.last_index_tree_view_postmortem = None
        self.last_selected_tab = 0
        self.last_selected_sub_tab_visualization = 0
        self.last_selected_sub_tab_analysis = 0
        self.random_id_sequence_counter = 0
        self.random_id_sequence_list = random.sample(range(0, 2 ** 16), 50000)
        self.file_path = ""
        self.current_filters_preset = {}
        self.auto_transpose = False

        # main widgets
        self.dialog_settings_preferences = None
        self.system_monitor = None
        self.selection_tab = None
        self.visualization_tab = None
        self.analysis_tab = None
        self.filters_window = None
        self.waiting_widget = None
        self.treeView_hdf5 = None
        self.treeView_nxcals = None
        self.treeView_postmortem = None
        self.visualization_tab_new_windows = {}
        self.analysis_tab_new_windows = {}
        self.attributes_table_new_windows = {}

        # set the real path
        self.real_path = obtain_real_path()
        if not self.app_root_path:
            self.app_root_path = self.real_path

        # get version name
        self.project_version = getVersionNameFromInit(self.app_root_path)

        # init QSettings
        self.dict_for_settings = {}
        self.qsettings = QSettings(self.qsettings_company_name, self.qsettings_app_name)
        self.retrieveSettings()

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # set some minimum widths
        self.setMinimumWidth(450)
        self.setMinimumHeight(250)
        self.frame_left.setMinimumWidth(150)
        self.frame_right.setMinimumWidth(300)

        # set icons
        self.setTabIcons()

        # update window icon path
        if self.window_icon_path:
            self.window_icon_path = os.path.join(self.app_root_path, "resources", "icons", self.window_icon_path)

        # set title and icon
        self.setWindowTitle(self.window_title)
        if self.window_icon_path:
            self.setWindowIcon(QIcon(self.window_icon_path))
        else:
            self.setWindowIcon(qta.icon(self.qta_str_icon))

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "main_window.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # rescale and adjust to the screen
        self.windowAdjustmentAndResizing()

        return

    #----------------------------------------------#

    def windowAdjustmentAndResizing(self):

        # get the current screen size of the user
        screen_object = self.app.primaryScreen()
        screen_size = screen_object.size()
        screen_rect = screen_object.availableGeometry()

        # minimum size for the main window
        self.setMinimumSize(320, 180)

        # resize main window
        self.resize(
            round(screen_rect.width() * self.screen_resize_factor),
            round(screen_rect.height() * self.screen_resize_factor),
        )

        # center main window
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(screen_rect.center())
        self.move(frame_geometry.topLeft())

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # create all menus and actions
        self.createTopMenus()

        # create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # main layout
        self.verticalLayout_central_widget = QVBoxLayout(self.central_widget)
        self.verticalLayout_central_widget.setContentsMargins(16, 16, 16, 16)
        self.verticalLayout_central_widget.setObjectName("verticalLayout_central_widget")

        # frame for the app
        self.frame_main_app = QFrame(self.central_widget)
        self.frame_main_app.setContentsMargins(0, 0, 0, 0)
        self.frame_main_app.setObjectName("frame_main_app")
        self.verticalLayout_central_widget.addWidget(self.frame_main_app)

        # main layout
        self.horizontalLayout_frame_main_app = QHBoxLayout(self.frame_main_app)
        self.horizontalLayout_frame_main_app.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_main_app.setObjectName("horizontalLayout_frame_main_app")

        # left side: qframe with a tree view (also a tab widget for the h5 and nxcals or postmortem)
        self.frame_left = QFrame(self.frame_main_app)
        self.frame_left.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_left.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_left.setObjectName("frame_left")
        self.verticalLayout_frame_left = QVBoxLayout(self.frame_left)
        self.verticalLayout_frame_left.setObjectName("verticalLayout_frame_left")
        self.verticalLayout_frame_left.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_main_app.addWidget(self.frame_left)

        # tab widget for the frame left
        self.tabWidget_left = QTabWidget(self.frame_left)
        self.tabWidget_left.setDocumentMode(False)
        self.tabWidget_left.setStyleSheet("QTabWidget::pane#tabWidget_left {}")
        self.tabWidget_left.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget_left.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget_left.setObjectName("tabWidget_left")
        self.verticalLayout_frame_left.addWidget(self.tabWidget_left)

        # create the tabs
        self.treeView_hdf5 = HDF5TreeView(parent = self.tabWidget_left, global_parent = self)
        self.treeView_nxcals = NXCALSTreeView(parent = self.tabWidget_left, global_parent = self)
        self.treeView_postmortem = PostMortemTreeView(parent = self.tabWidget_left, global_parent = self)

        # add the tabs
        self.tabWidget_left.addTab(self.treeView_hdf5, "HDF5")
        self.tabWidget_left.addTab(self.treeView_nxcals, "NXCALS")
        self.tabWidget_left.addTab(self.treeView_postmortem, "PostMortem")

        # init tab
        self.tabWidget_left.setCurrentIndex(0)

        # create button for the filters
        self.tabWidget_left_filters_hdf5_button = QPushButton(self.tabWidget_left)
        self.tabWidget_left_filters_hdf5_button.setObjectName("tabWidget_left_filters_hdf5_button")
        self.tabWidget_left_filters_hdf5_button.setText("F")
        self.tabWidget_left_filters_hdf5_button.setCheckable(True)
        self.tabWidget_left_filters_hdf5_button.setStyleSheet("QPushButton:checked{ background-color: #ffdf80;}")
        self.tabWidget_left_filters_hdf5_button.setFixedSize(22,22)
        self.tabWidget_left_filters_hdf5_button.setToolTip("")
        self.tabWidget_left.tabBar().setTabButton(0, self.tabWidget_left.tabBar().RightSide, self.tabWidget_left_filters_hdf5_button)

        # set stretch factors
        self.verticalLayout_frame_left.setStretch(0, 100)

        # right side: qframe with a tab widget
        self.frame_right = QFrame(self.frame_main_app)
        self.frame_right.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_right.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_right.setObjectName("frame_right")
        self.verticalLayout_frame_right = QVBoxLayout(self.frame_right)
        self.verticalLayout_frame_right.setObjectName("verticalLayout_frame_right")
        self.verticalLayout_frame_right.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_frame_main_app.addWidget(self.frame_right)

        # create the tab widget
        self.tabWidget_right = QTabWidget(self.frame_right)
        self.tabWidget_right.setDocumentMode(False)
        self.tabWidget_right.setStyleSheet("QTabWidget::pane#tabWidget_right {}")
        self.tabWidget_right.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget_right.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget_right.setObjectName("tabWidget_right")
        self.verticalLayout_frame_right.addWidget(self.tabWidget_right)

        # init right tabs
        self.initRightTabs(remove_tabs = False, update_last_tab_index = True, create_selection_tab = True)

        # set stretch factors
        self.horizontalLayout_frame_main_app.setStretch(0, 10)
        self.horizontalLayout_frame_main_app.setStretch(1, 90)

        # splitter to separate both panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.frame_left)
        self.splitter.addWidget(self.frame_right)
        self.splitter.setHandleWidth(10)
        self.splitter.setStretchFactor(0, 20)
        self.splitter.setStretchFactor(1, 80)
        self.splitter.setSizes([300,1000])
        self.horizontalLayout_frame_main_app.addWidget(self.splitter)

        # frame for the system monitor
        if self.dict_for_settings["setting_enable_system_monitor"]:
            self.system_monitor = SystemMonitorWindow(parent = self.central_widget, app_root_path = self.app_root_path, time_period = self.dict_for_settings["refresh_rate_system_monitor"]*1000)
        else:
            self.system_monitor = QWidget(parent = self.central_widget)
        self.verticalLayout_central_widget.addWidget(self.system_monitor)

        # splitter to separate both panels
        if self.dict_for_settings["setting_enable_system_monitor"]:
            self.splitter_2 = QSplitter(Qt.Orientation.Vertical)
            self.splitter_2.addWidget(self.frame_main_app)
            self.splitter_2.addWidget(self.system_monitor)
            self.splitter_2.setHandleWidth(10)
            self.splitter_2.setStretchFactor(0, 95)
            self.splitter_2.setStretchFactor(1, 5)
            self.splitter_2.setSizes([1000,100])
            self.verticalLayout_central_widget.addWidget(self.splitter_2)
        else:
            self.verticalLayout_central_widget.setStretch(0,99)
            self.verticalLayout_central_widget.setStretch(1,1)

        return

    #----------------------------------------------#

    def changeRightTabColors(self, color = "#1D8109"):

        # change colors
        self.tabWidget_right.tabBar().setTabTextColor(1, QColor(color))
        self.tabWidget_right.tabBar().setTabTextColor(2, QColor(color))
        self.tabWidget_right.tabBar().setTabIcon(0, QIcon(os.path.join(self.app_root_path, "resources", "icons", "selection.png")))
        self.tabWidget_right.tabBar().setTabIcon(1, self.change_icon_color(QIcon(os.path.join(self.app_root_path, "resources", "icons", "visualization.png")), QColor(color)))
        self.tabWidget_right.tabBar().setTabIcon(2, self.change_icon_color(QIcon(os.path.join(self.app_root_path, "resources", "icons", "analysis.png")), QColor(color)))
        self.tabWidget_right.tabBar().setIconSize(QSize(24,24))

        return

    #----------------------------------------------#

    def setTabIcons(self):

        # set icons for the tabs (left)
        self.tabWidget_left.tabBar().setTabIcon(1, QIcon(os.path.join(self.app_root_path, "resources", "icons", "nxcals.png")))
        self.tabWidget_left.tabBar().setTabIcon(2, QIcon(os.path.join(self.app_root_path, "resources", "icons", "postmortem.png")))
        self.tabWidget_left.tabBar().setIconSize(QSize(24,24))

        # set icons for the tabs (right)
        self.changeRightTabColors(color = "#000000")

        return

    #----------------------------------------------#

    def initRightTabs(self, remove_tabs = True, update_last_tab_index = True, visualization_tab = None, analysis_tab = None, create_selection_tab = False):

        # bugfix
        if not visualization_tab:
            visualization_tab = QWidget()
        if not analysis_tab:
            analysis_tab = QWidget()

        # remove the tabs
        if remove_tabs:
            self.removeTabs(remove_selection_tab = create_selection_tab)

        # disable signals
        self.tabWidget_right.blockSignals(True)

        # add selection tab
        if create_selection_tab:
            self.selection_tab = MainSelection(self.app, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, qta_str_icon=self.qta_str_icon, parent=self.tabWidget_right, global_parent=self)
            self.tabWidget_right.addTab(self.selection_tab, "Selection")

        # init tab widgets
        self.visualization_tab = visualization_tab
        self.analysis_tab = analysis_tab

        # add tabs
        self.tabWidget_right.addTab(self.visualization_tab, "Visualization")
        self.tabWidget_right.addTab(self.analysis_tab, "Analysis")

        # INSPECTION MODE?
        if self.dict_for_settings["setting_disable_selection_cart"]:
            self.tabWidget_right.setTabEnabled(0, False)
            if update_last_tab_index:
                self.last_selected_tab = 1
                self.last_selected_sub_tab_visualization = 0
                self.last_selected_sub_tab_analysis = 0
        else:
            self.tabWidget_right.setTabEnabled(0, True)
            if update_last_tab_index:
                self.last_selected_tab = 0
                self.last_selected_sub_tab_visualization = 0
                self.last_selected_sub_tab_analysis = 0

        # set current tab
        self.tabWidget_right.setCurrentIndex(self.last_selected_tab)

        # enable signals
        self.tabWidget_right.blockSignals(False)

        # set icons
        self.setTabIcons()

        return

    #----------------------------------------------#

    def refreshLeftTabs(self, refresh_hdf5 = True, refresh_nxcals = True, refresh_postmortem = True):

        # for hdf5
        if refresh_hdf5:

            # empty last index
            self.last_index_tree_view_hdf5 = None

            # refresh the treeview
            if self.file_path:
                self.treeView_hdf5.refreshTreeView(dir_path=self.file_path)

            # go to h5 tab
            self.tabWidget_left.setCurrentIndex(0)

        # for nxcals
        if refresh_nxcals:

            # TODO
            pass

        # for postmortem
        if refresh_postmortem:

            # TODO
            pass

        return

    #----------------------------------------------#

    def createTopMenus(self):

        # create menu bar
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setDefaultUp(False)
        self.menu_bar.setObjectName("menu_bar")
        self.setMenuBar(self.menu_bar)

        # MENU PANEL (FILE AND DIR)
        self.menu_file = QMenu(self.menu_bar)
        self.menu_file.setObjectName("menu_file")
        self.menu_file.setTitle("&File")
        self.menu_bar.addMenu(self.menu_file)
        self.action_open_hdf5_file = QAction("Open HDF5 file", parent=self.menu_file)
        self.action_open_hdf5_file.setIcon(qta.icon("ei.file"))
        self.menu_file.addAction(self.action_open_hdf5_file)
        self.action_open_dir = QAction("Open directory", parent=self.menu_file)
        self.action_open_dir.setIcon(qta.icon("ei.folder"))
        self.menu_file.addAction(self.action_open_dir)

        # shortcuts
        self.action_open_hdf5_file.setShortcut(QKeySequence("Ctrl+H"))
        self.action_open_dir.setShortcut(QKeySequence("Ctrl+D"))

        # MENU PANEL (FILTERS)
        self.menu_filters = QMenu(self.menu_bar)
        self.menu_filters.setObjectName("menu_filters")
        self.menu_filters.setTitle("&Treeview")
        self.menu_bar.addMenu(self.menu_filters)

        # HDF5 actions
        self.action_init_hdf5_tree = QAction("HDF5 - Init treeview", parent=self.menu_file)
        self.action_init_hdf5_tree.setIcon(qta.icon("mdi.restart"))
        self.menu_filters.addAction(self.action_init_hdf5_tree)
        self.action_reload_hdf5_tree = QAction("HDF5 - Reload contents", parent=self.menu_filters)
        self.action_reload_hdf5_tree.setIcon(qta.icon("mdi.refresh"))
        self.menu_filters.addAction(self.action_reload_hdf5_tree)
        self.action_apply_filters_hdf5_tree = QAction("HDF5 - Apply filters", parent=self.menu_file)
        self.action_apply_filters_hdf5_tree.setIcon(qta.icon("ri.play-list-add-fill"))
        self.menu_filters.addAction(self.action_apply_filters_hdf5_tree)
        self.action_reset_hdf5_tree = QAction("HDF5 - Reset filters", parent=self.menu_file)
        self.action_reset_hdf5_tree.setIcon(qta.icon("ri.play-list-add-fill"))
        self.menu_filters.addAction(self.action_reset_hdf5_tree)

        # NXCALS actions
        self.menu_filters.addSeparator()
        self.action_init_nxcals_tree = QAction("NXCALS - Init treeview", parent=self.menu_file)
        self.action_init_nxcals_tree.setIcon(qta.icon("mdi.restart"))
        self.menu_filters.addAction(self.action_init_nxcals_tree)

        # PostMortem actions
        self.menu_filters.addSeparator()
        self.action_init_postmortem_tree = QAction("PostMortem - Init treeview", parent=self.menu_file)
        self.action_init_postmortem_tree.setIcon(qta.icon("mdi.restart"))
        self.menu_filters.addAction(self.action_init_postmortem_tree)

        # shortcuts
        self.action_reload_hdf5_tree.setShortcut(QKeySequence("F5"))
        self.action_apply_filters_hdf5_tree.setShortcut(QKeySequence("Shift+F"))
        self.action_reset_hdf5_tree.setShortcut(QKeySequence("Shift+R"))

        # MENU PANEL (SETTINGS)
        self.action_open_settings = QAction("&Settings", parent=self.menu_bar)
        self.menu_bar.addAction(self.action_open_settings)

        # MENU PANEL (VERSION)
        self.menu_version = QMenu(self.menu_bar)
        self.menu_version.setObjectName("menu_version")
        self.menu_version.setTitle("&v{}".format(self.project_version))
        self.menu_bar.addMenu(self.menu_version)
        self.action_open_url_gitlab = QAction("Open project at Gitlab", parent=self.menu_version)
        self.action_open_url_gitlab.setIcon(qta.icon("fa.gitlab"))
        self.menu_version.addAction(self.action_open_url_gitlab)
        self.menu_version.setToolTip("https://gitlab.cern.ch/bisw-python/{}".format(self.qsettings_app_name))

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # signal that gets activated when the current tab changes
        self.tabWidget_right.currentChanged.connect(self.tabRightChanged)

        # open files
        self.action_open_hdf5_file.triggered.connect(lambda: self.openFile(file_or_dir = "file"))
        self.action_open_dir.triggered.connect(lambda: self.openFile(file_or_dir = "dir"))

        # filter bindings
        self.action_reload_hdf5_tree.triggered.connect(self.reloadHDF5Treeview)
        self.action_apply_filters_hdf5_tree.triggered.connect(lambda: self.openFiltersWindow())
        self.action_reset_hdf5_tree.triggered.connect(lambda: self.resetHDF5Filters())
        self.action_init_hdf5_tree.triggered.connect(lambda: self.initHDF5Tree())
        self.action_init_nxcals_tree.triggered.connect(lambda: self.initNXCALSTree())
        self.action_init_postmortem_tree.triggered.connect(lambda: self.initPostMortemTree())
        self.tabWidget_left_filters_hdf5_button.clicked.connect(lambda: self.filtersButtonClicked())

        # open at gitlab
        self.action_open_url_gitlab.triggered.connect(self.openGitlabUrl)

        # setting connections
        self.action_open_settings.triggered.connect(self.openSettingsPanel)

        return

    #----------------------------------------------#

    def tabRightChanged(self, tab_index):

        # update tab
        self.last_selected_tab = tab_index

        # update colors
        if tab_index != 0:
            self.changeRightTabColors(color = "#000000")

        # get current tab widget
        current_tab_widget = self.tabWidget_right.widget(tab_index)

        # build the tab
        if current_tab_widget is not None:
            if hasattr(current_tab_widget, "tab_is_built"):
                if not current_tab_widget.tab_is_built:
                    current_tab_widget.buildTab()

        return

    #----------------------------------------------#

    def reloadHDF5Treeview(self, *, reapply_filters: bool = True) -> None:

        # check if we have a file path
        if not self.file_path:
            message_title = "Reload Problem"
            message_text = ("No directory is currently loaded... Open a folder first!")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            return

        # check if we have filters (for the moment reloadHDF5Treeview is disabled if we have filters applied)
        if self.current_filters_preset:
            message_title = "Reload Problem"
            message_text = ("Unable to reload with filters applied. Please deselect the filters and try reloading again.")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            return

        # empty last index
        self.last_index_tree_view_hdf5 = None

        # clear the existing view & close any open file handles
        for h5obj in self.treeView_hdf5.hdf_dict.values():
            try:
                h5obj.close()
            except Exception:
                pass
        self.treeView_hdf5.clearTreeView()

        # rebuild the tree
        self.treeView_hdf5.refreshTreeView(dir_path=self.file_path, filters=None)

        # init right panel
        self.hideRightPanel(from_top_node=True)

        # go to h5 tab
        self.tabWidget_left.setCurrentIndex(0)

        # expand only the top-level nodes after the event-loop is free
        QTimer.singleShot(0, self.treeView_hdf5.expand_top_level)

        return

    #----------------------------------------------#

    def openSettingsPanel(self):

        # open the dialog
        self.dialog_settings_preferences = SettingsPreferencesView(self.dict_for_settings, self.qsettings, self.default_settings, app = self.app, app_root_path = self.app_root_path, parent = self)
        self.dialog_settings_preferences.setModal(True)
        self.dialog_settings_preferences.show()

        return

    #----------------------------------------------#

    def filtersButtonClicked(self):

        # button logics
        if self.tabWidget_left_filters_hdf5_button.isChecked():
            self.tabWidget_left_filters_hdf5_button.setChecked(False)
            self.openFiltersWindow()
        else:
            self.tabWidget_left_filters_hdf5_button.setChecked(False)
            self.resetHDF5Filters()

        return

    #----------------------------------------------#

    def openFiltersWindow(self):

        # if tree model exists
        if self.file_path:

            # open dialog
            self.filters_window = FiltersWindow(app=self.app, app_root_path=self.app_root_path, parent=self, current_filters_preset=self.current_filters_preset)
            self.filters_window.exec_()

        # message error
        else:

            # show error
            message_title = "Error"
            message_text = ("Unable to open filters until a valid file or directory has been loaded!")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()

        return

    #----------------------------------------------#

    def resetHDF5Filters(self, hide_right_panel=False):

        # if tree model exists
        if self.file_path:

            # if filters were applied before
            if self.current_filters_preset:

                # empty last index
                self.last_index_tree_view_hdf5 = None

                # refresh the treeview
                self.treeView_hdf5.refreshTreeView(dir_path=self.file_path, filters=None)

                # init right panel
                if hide_right_panel:
                    self.hideRightPanel(from_top_node=True)

                # go to h5 tab
                self.tabWidget_left.setCurrentIndex(0)

                # reset dict
                self.current_filters_preset = {}

        return

    #----------------------------------------------#

    def applyFilters(self, filters, hide_right_panel=False, verbose=True):

        # if tree model exists
        if self.file_path:

            # for debugging
            if verbose:
                print("FILTERS")
                print(json.dumps(filters, indent=4))

            # empty last index
            self.last_index_tree_view_hdf5 = None

            # close last window
            self.filters_window.close()
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

            # open waiting widget
            self.waiting_widget = WaitingWidget(app=self.app, app_root_path=self.app_root_path, parent=self)
            self.waiting_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.waiting_widget.show()
            self.waiting_widget.repaint()
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

            # hide treeview during the search
            self.treeView_hdf5.setVisible(False)

            # refresh the treeview
            self.treeView_hdf5.refreshTreeView(dir_path=self.file_path, filters=filters)

            # make tree visible again
            self.treeView_hdf5.setVisible(True)

            # close the waiting animation widget
            self.waiting_widget.close()
            self.waiting_widget = None
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

            # init right panel
            if hide_right_panel:
                self.hideRightPanel(from_top_node=True)

            # go to h5 tab
            self.tabWidget_left.setCurrentIndex(0)

        return

    #----------------------------------------------#

    def initHDF5Tree(self, hide_right_panel=False):

        # if tree model exists
        if self.file_path:

            # reset filters in case we have some
            self.resetHDF5Filters()

            # clear the treeview
            self.treeView_hdf5.clearTreeView()

            # clear variables
            self.file_path = ""
            self.last_index_tree_view_hdf5 = None

            # force garbage collection to reclaim memory
            gc.collect()

            # init right panel
            if hide_right_panel:
                self.hideRightPanel(from_top_node=True)

        # go to h5 tab
        self.tabWidget_left.setCurrentIndex(0)

        return

    #----------------------------------------------#

    def initNXCALSTree(self, hide_right_panel=False):

        # clear the treeview
        self.treeView_nxcals.clearTreeView()

        # clear variables
        self.last_index_tree_view_nxcals = None

        # force garbage collection to reclaim memory
        gc.collect()

        # init right panel
        if hide_right_panel:
            self.hideRightPanel(from_top_node=True)

        # go to h5 tab
        self.tabWidget_left.setCurrentIndex(1)

        return

    #----------------------------------------------#

    def initPostMortemTree(self, hide_right_panel=False):

        # clear the treeview
        self.treeView_postmortem.clearTreeView()

        # clear variables
        self.last_index_tree_view_postmortem = None

        # force garbage collection to reclaim memory
        gc.collect()

        # init right panel
        if hide_right_panel:
            self.hideRightPanel(from_top_node=True)

        # go to h5 tab
        self.tabWidget_left.setCurrentIndex(2)

        return

    #----------------------------------------------#

    def openGitlabUrl(self):

        # open the browser at the gitlab repository
        try:
            url = QUrl("https://gitlab.cern.ch/bisw-python/{}".format(self.qsettings_app_name))
            QDesktopServices.openUrl(url)
        except Exception as xcp:
            print("Exception at openGitlabUrl(): {}".format(xcp))

        return

    #----------------------------------------------#

    def openFile(self, file_path = None, file_or_dir = "file", verbose = True):

        # obtain previous path
        if self.file_path:
            if os.path.isdir(self.file_path):
                default_dir = self.file_path
            else:
                default_dir = os.path.dirname(self.file_path)
        else:
            default_dir = self.default_hdf5_path

        # get file path
        if not file_path:
            try:
                if file_or_dir == "file":
                    file_path, _ = QFileDialog.getOpenFileName(self, "Load HDF5 file", directory=default_dir, filter='HDF5 Files (*.hdf *.h5 *.hdf5);; All Files (*.*)')
                elif file_or_dir == "dir":
                    file_path = QFileDialog.getExistingDirectory(
                        self,
                        "Open directory",
                        default_dir,
                        QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
                    )
                file_path = str(file_path)
            except Exception as xcp:
                if verbose:
                    print(xcp)
                return

        # debugging
        if verbose:
            print("file_path: ", file_path)

        # proceed if file path is not empty
        if file_path:

            # store the file
            self.file_path = file_path

            # reset all
            self.resetRightAndLeftTabs()

        return

    #----------------------------------------------#

    def resetRightAndLeftTabs(self):

        # temporarily disable repaints while we rebuild the panels to avoid flicker
        self.central_widget.setUpdatesEnabled(False)

        try:
            # remake the tabs with empty widgets
            self.initRightTabs(remove_tabs=True, update_last_tab_index=True, create_selection_tab=True)

            # refresh left tabs
            self.refreshLeftTabs()
        finally:
            # re-enable updates and request a repaint so the widgets become visible again
            self.central_widget.setUpdatesEnabled(True)
            self.central_widget.update()

        return

    #----------------------------------------------#

    def openHDF5AttributesWindow(self, path_list, hdf_path_list, type_list):

        # iterate over paths
        for counter, path in enumerate(path_list):

            # get hdf path
            hdf_path = hdf_path_list[counter]

            # get display path
            if path != ".":
                display_path = os.path.join(hdf_path, path)
            else:
                display_path = hdf_path

            # get node
            node = None
            if hdf_path in self.treeView_hdf5.hdf_dict:
                if self.treeView_hdf5.hdf_dict[hdf_path]:
                    node = self.treeView_hdf5.hdf_dict[hdf_path][path]
            if node == None:
                return
            
            # get attributes
            attributes = node.attrs

            # set the window id
            try:
                win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
            except:
                print("No more windows can be opened because the maximum number of windows has already been reached...")

            # open new window
            self.attributes_table_new_windows[win_id] = AttributesWindow(self.app, attributes, display_path, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self, global_parent=None, popup_window=True)

            # save window id in the window
            self.attributes_table_new_windows[win_id].win_id = win_id

            # change window title
            self.attributes_table_new_windows[win_id].setWindowTitle("Attributes Window (Popup) [id={}]".format(win_id))

            # open as pop up
            self.attributes_table_new_windows[win_id].show()

            # update the global counter
            self.random_id_sequence_counter += 1

        return

    #----------------------------------------------#

    def openNewVisualizationWindow(self, path_list, hdf_path_list, type_list, merge = False, auto_multiple_axes = False):

        # merge strategy (open only 1 window with a new merged dataframe)
        if merge:

            # set display name
            display = "merged"

            # iterate over paths
            df_list = []
            for counter, path in enumerate(path_list):

                # get hdf path
                hdf_path = hdf_path_list[counter]

                # get node
                node = None
                if hdf_path in self.treeView_hdf5.hdf_dict:
                    if self.treeView_hdf5.hdf_dict[hdf_path]:
                        node = self.treeView_hdf5.hdf_dict[hdf_path][path]
                if node == None:
                    return

                # check if it is dataset
                if type_list[counter] == "Dataset":
                    is_it_dataset = True
                else:
                    is_it_dataset = False

                # create the data to be passed to the tabs
                dataframe, attributes, chunk_size, error_message = self.createDfDataObject(node, is_it_dataset=is_it_dataset)
                if error_message:
                    return

                # add to the list
                df_list.append(dataframe)

            # scalar case or multi array case?
            if all(individual_df.shape == (1, 1) for individual_df in df_list):
                axis = 0
                ignore_index = True
            else:
                axis = 1
                ignore_index = False

            # method and arguments
            pandas_method = "pd.concat"
            join_arg = "outer"

            # try to get the result dataframe
            try:
                result_df = eval(pandas_method)(df_list, axis=axis, ignore_index=ignore_index, join=join_arg)
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

            # set the window id
            try:
                win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
            except:
                print("No more windows can be opened because the maximum number of windows has already been reached...")

            # get color dict
            color_dict = {}
            color_dict["color_background"] = self.dict_for_settings["color_background"]
            color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

            # open new visualization
            self.visualization_tab_new_windows[win_id] = MainVisualization(self.app, result_df, {}, display, True, last_selected_sub_tab=0, app_root_path=self.app_root_path,
                                                                           window_icon_path=self.window_icon_path, parent=self,
                                                                           global_parent=None, popup_window=True, color_dict=color_dict,
                                                                           mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"],
                                                                           pyqtgraph_default_downsample=self.dict_for_settings["setting_enable_downsampling_plots"],
                                                                           sticky_options=self.dict_for_settings["setting_sticky_options"],
                                                                           display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"],
                                                                           ncurves_at_init=self.dict_for_settings["ncurves_at_init"],
                                                                           min_big_data_sample_size=self.dict_for_settings["min_big_data_sample_size"],
                                                                           chunk_size=None, max_n_columns=self.dict_for_settings["max_n_columns"],
                                                                           auto_multiple_axes = auto_multiple_axes)

            # save window id in the window
            self.visualization_tab_new_windows[win_id].win_id = win_id

            # change window title
            self.visualization_tab_new_windows[win_id].setWindowTitle("Visualization Window (Popup) [id={}]".format(win_id))

            # open as pop up
            self.visualization_tab_new_windows[win_id].show()

            # update the global counter
            self.random_id_sequence_counter += 1

        # multiple windows strategy
        else:

            # iterate over paths
            for counter, path in enumerate(path_list):

                # get hdf path
                hdf_path = hdf_path_list[counter]

                # get display name
                display = path.split(os.sep)[-1]

                # get node
                node = None
                if hdf_path in self.treeView_hdf5.hdf_dict:
                    if self.treeView_hdf5.hdf_dict[hdf_path]:
                        node = self.treeView_hdf5.hdf_dict[hdf_path][path]
                if node == None:
                    return

                # check if it is dataset
                if type_list[counter] == "Dataset":
                    is_it_dataset = True
                else:
                    is_it_dataset = False

                # create the data to be passed to the tabs
                dataframe, attributes, chunk_size, error_message = self.createDfDataObject(node, is_it_dataset=is_it_dataset)
                if error_message:
                    continue

                # set the window id
                try:
                    win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
                except:
                    print("No more windows can be opened because the maximum number of windows has already been reached...")

                # get color dict
                color_dict = {}
                color_dict["color_background"] = self.dict_for_settings["color_background"]
                color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

                # open new visualization
                self.visualization_tab_new_windows[win_id] = MainVisualization(self.app, dataframe, attributes, display, True, last_selected_sub_tab=0,
                                                                               app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self,
                                                                               global_parent=None, popup_window=True, color_dict=color_dict,
                                                                               mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"],
                                                                               pyqtgraph_default_downsample=self.dict_for_settings["setting_enable_downsampling_plots"],
                                                                               sticky_options=self.dict_for_settings["setting_sticky_options"],
                                                                               display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"],
                                                                               ncurves_at_init=self.dict_for_settings["ncurves_at_init"],
                                                                               min_big_data_sample_size=self.dict_for_settings["min_big_data_sample_size"],
                                                                               chunk_size=chunk_size, max_n_columns=self.dict_for_settings["max_n_columns"],
                                                                               auto_multiple_axes=auto_multiple_axes)

                # save window id in the window
                self.visualization_tab_new_windows[win_id].win_id = win_id

                # change window title
                self.visualization_tab_new_windows[win_id].setWindowTitle("Visualization Window (Popup) [id={}]".format(win_id))

                # open as pop up
                self.visualization_tab_new_windows[win_id].show()

                # update the global counter
                self.random_id_sequence_counter += 1

        return

    #----------------------------------------------#

    def openNewAnalysisWindow(self, path_list, hdf_path_list, type_list, merge = False, auto_multiple_axes = False):

        # do not apply any merging (maybe in the future)
        if True:

            # iterate over paths
            for counter, path in enumerate(path_list):

                # get hdf path
                hdf_path = hdf_path_list[counter]

                # get display name
                display = path.split(os.sep)[-1]

                # get node
                node = None
                if hdf_path in self.treeView_hdf5.hdf_dict:
                    if self.treeView_hdf5.hdf_dict[hdf_path]:
                        node = self.treeView_hdf5.hdf_dict[hdf_path][path]
                if node == None:
                    return

                # check if it is dataset
                if type_list[counter] == "Dataset":
                    is_it_dataset = True
                else:
                    is_it_dataset = False

                # create the data to be passed to the tabs
                dataframe, attributes, chunk_size, error_message = self.createDfDataObject(node, is_it_dataset=is_it_dataset)
                if error_message:
                    continue

                # set the window id
                try:
                    win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
                except:
                    print("No more windows can be opened because the maximum number of windows has already been reached...")

                # get color dict
                color_dict = {}
                color_dict["color_background"] = self.dict_for_settings["color_background"]
                color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

                # open new analysis
                self.analysis_tab_new_windows[win_id] = MainAnalysis(self.app, dataframe, attributes, display, True,
                                                                     last_selected_sub_tab=0, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path,
                                                                     parent=self, global_parent=None, popup_window=True, color_dict=color_dict,
                                                                     mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"],
                                                                     pyqtgraph_default_downsample=self.dict_for_settings["setting_enable_downsampling_plots"],
                                                                     sticky_options=self.dict_for_settings["setting_sticky_options"],
                                                                     display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"],
                                                                     ncurves_at_init=self.dict_for_settings["ncurves_at_init"],
                                                                     min_big_data_sample_size=self.dict_for_settings["min_big_data_sample_size"],
                                                                     chunk_size=chunk_size, max_n_columns=self.dict_for_settings["max_n_columns"],
                                                                     auto_multiple_axes=auto_multiple_axes)

                # save window id in the window
                self.analysis_tab_new_windows[win_id].win_id = win_id

                # change window title
                self.analysis_tab_new_windows[win_id].setWindowTitle("Analysis Window (Popup) [id={}]".format(win_id))

                # open as pop up
                self.analysis_tab_new_windows[win_id].show()

                # update the global counter
                self.random_id_sequence_counter += 1

        return

    #----------------------------------------------#

    def openNewVisualizationWindowFromNXCALS(self, index_list, model, merge = False, auto_multiple_axes = False):

        # merge strategy (open only 1 window with a new merged dataframe)
        if merge:

            # set display name
            display = "merged"

            # iterate over indexes
            df_list = []
            for counter, index in enumerate(index_list):

                # get data
                data = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)

                # if there is no data just skip
                if data.size == 0:
                    continue

                # get dataframe and attributes
                dataframe, attributes, chunk_size = self.createDfFromNXCALS(data)

                # add to the list
                df_list.append(dataframe)

            # scalar case or multi array case?
            if all(individual_df.shape == (1, 1) for individual_df in df_list):
                axis = 0
            else:
                axis = 1

            # method and arguments
            pandas_method = "pd.concat"
            ignore_index = False
            join_arg = "outer"

            # try to get the result dataframe
            try:
                result_df = eval(pandas_method)(df_list, axis=axis, ignore_index=ignore_index, join=join_arg)
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

            # set the window id
            try:
                win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
            except:
                print("No more windows can be opened because the maximum number of windows has already been reached...")

            # get color dict
            color_dict = {}
            color_dict["color_background"] = self.dict_for_settings["color_background"]
            color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

            # open new visualization
            self.visualization_tab_new_windows[win_id] = MainVisualization(self.app, result_df, {}, display, True, last_selected_sub_tab=0, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path,
                                                                           parent=self, global_parent=None, popup_window=True, color_dict=color_dict, mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"],
                                                                           pyqtgraph_default_downsample=self.dict_for_settings["setting_enable_downsampling_plots"],
                                                                           sticky_options=self.dict_for_settings["setting_sticky_options"],
                                                                           display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"],
                                                                           ncurves_at_init=self.dict_for_settings["ncurves_at_init"], min_big_data_sample_size=self.dict_for_settings["min_big_data_sample_size"], chunk_size=chunk_size,
                                                                           max_n_columns=self.dict_for_settings["max_n_columns"], auto_multiple_axes=auto_multiple_axes)

            # save window id in the window
            self.visualization_tab_new_windows[win_id].win_id = win_id

            # change window title
            self.visualization_tab_new_windows[win_id].setWindowTitle("Visualization Window (Popup) [id={}]".format(win_id))

            # open as pop up
            self.visualization_tab_new_windows[win_id].show()

            # update the global counter
            self.random_id_sequence_counter += 1

        # multiple windows strategy
        else:

            # iterate over indexes
            for counter, index in enumerate(index_list):

                # get data
                data = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)

                # get display name
                display = model.itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)

                # if there is no data just skip
                if data.size == 0:
                    continue

                # get dataframe and attributes
                dataframe, attributes, chunk_size = self.createDfFromNXCALS(data)

                # set the window id
                try:
                    win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
                except:
                    print("No more windows can be opened because the maximum number of windows has already been reached...")

                # get color dict
                color_dict = {}
                color_dict["color_background"] = self.dict_for_settings["color_background"]
                color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

                # open new visualization
                self.visualization_tab_new_windows[win_id] = MainVisualization(self.app, dataframe, attributes, display, True, last_selected_sub_tab=0, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self, global_parent=None, popup_window=True, color_dict=color_dict, mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"], pyqtgraph_default_downsample = self.dict_for_settings["setting_enable_downsampling_plots"], sticky_options=self.dict_for_settings["setting_sticky_options"], display_strings_on_x_axis = self.dict_for_settings["setting_display_strings_on_x_axis"], ncurves_at_init = self.dict_for_settings["ncurves_at_init"], min_big_data_sample_size = self.dict_for_settings["min_big_data_sample_size"], chunk_size = chunk_size, max_n_columns=self.dict_for_settings["max_n_columns"], auto_multiple_axes=auto_multiple_axes)

                # save window id in the window
                self.visualization_tab_new_windows[win_id].win_id = win_id

                # change window title
                self.visualization_tab_new_windows[win_id].setWindowTitle("Visualization Window (Popup) [id={}]".format(win_id))

                # open as pop up
                self.visualization_tab_new_windows[win_id].show()

                # update the global counter
                self.random_id_sequence_counter += 1

        return

    #----------------------------------------------#

    def openNewAnalysisWindowFromNXCALS(self, index_list, model, merge = False, auto_multiple_axes = False):

        # do not apply any merging (maybe in the future)
        if True:

            # iterate over indexes
            for counter, index in enumerate(index_list):

                # get data
                data = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)

                # get display name
                display = model.itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)

                # if there is no data just skip
                if data.size == 0:
                    continue

                # get dataframe and attributes
                dataframe, attributes, chunk_size = self.createDfFromNXCALS(data)

                # set the window id
                try:
                    win_id = str(self.random_id_sequence_list[self.random_id_sequence_counter])
                except:
                    print("No more windows can be opened because the maximum number of windows has already been reached...")

                # get color dict
                color_dict = {}
                color_dict["color_background"] = self.dict_for_settings["color_background"]
                color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

                # open new analysis
                self.analysis_tab_new_windows[win_id] = MainAnalysis(self.app, dataframe, attributes, display, True, last_selected_sub_tab=0, app_root_path=self.app_root_path,
                                                                     window_icon_path=self.window_icon_path, parent=self, global_parent=None, popup_window=True, color_dict=color_dict,
                                                                     mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"],
                                                                     pyqtgraph_default_downsample=self.dict_for_settings["setting_enable_downsampling_plots"],
                                                                     sticky_options=self.dict_for_settings["setting_sticky_options"],
                                                                     display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"],
                                                                     ncurves_at_init=self.dict_for_settings["ncurves_at_init"],
                                                                     min_big_data_sample_size=self.dict_for_settings["min_big_data_sample_size"],
                                                                     chunk_size=chunk_size, max_n_columns=self.dict_for_settings["max_n_columns"],
                                                                     auto_multiple_axes=auto_multiple_axes)

                # save window id in the window
                self.analysis_tab_new_windows[win_id].win_id = win_id

                # change window title
                self.analysis_tab_new_windows[win_id].setWindowTitle("Analysis Window (Popup) [id={}]".format(win_id))

                # open as pop up
                self.analysis_tab_new_windows[win_id].show()

                # update the global counter
                self.random_id_sequence_counter += 1

        return

    #----------------------------------------------#

    def isItDataframeNode(self, node):

        # init
        boolean = False

        # data type should be DataFrame and node should be Group
        if isinstance(node, h5py.Group):
            if "data_type" in node.attrs.keys():
                if node.attrs["data_type"] == "DataFrame":
                    boolean = True

        return boolean

    #----------------------------------------------#

    def isItAutoMergingGroup(self, node):

        # init
        boolean = False

        # check if auto is ON and the node is a group
        if isinstance(node, h5py.Group):
            if self.dict_for_settings["setting_auto_merge_group"]:
                boolean = True

        return boolean

    #----------------------------------------------#

    def isItAutoMergingGroupNXCALS(self, model, index):

        # init
        boolean = False

        # check if auto is ON and the index has children
        if model.hasChildren(index):
            if self.dict_for_settings["setting_auto_merge_group"]:
                boolean = True

        return boolean

    #----------------------------------------------#

    def performAutoMergingGroup(self, node=None, model=None, index=None):

        # enable if we only want to merge integers
        ONLY_MERGE_INTS = False

        # init
        display_name = "data"
        child_data = {}
        child_shapes = {}

        # will be set to True if any child array is nonempty
        non_empty_found = False

        # helper: normalize an array shape so that (N,1) becomes (N,)
        def normalize_array(arr):
            if arr.ndim == 2 and arr.shape[1] == 1:
                return arr.ravel()
            return arr

        # helper: determine if the array is "scalar-like"
        # either a 0-dimensional array or a 1D array with exactly one element
        def is_scalar_like(arr):
            return (arr.ndim == 0) or (arr.ndim == 1 and arr.shape[0] == 1)

        # NXCALS route: when model is provided
        if model is not None and index is not None:
            display_name = model.data(index, Qt.ItemDataRole.DisplayRole)
            rows = model.rowCount(index)
            if rows == 0:
                return pd.DataFrame([])
            for row in range(rows):
                child_index = model.index(row, 0, index)
                key = model.data(child_index, Qt.ItemDataRole.DisplayRole)
                data = model.data(child_index, Qt.ItemDataRole.UserRole)
                if data is None:
                    continue
                try:
                    arr = np.array(data)
                    if ONLY_MERGE_INTS and not np.issubdtype(arr.dtype, np.number):
                        arr = None
                except Exception:
                    arr = None
                if arr is None:
                    continue
                arr = normalize_array(arr)
                child_data[key] = arr
                child_shapes[key] = arr.shape
                if arr.size != 0:
                    non_empty_found = True

        # HDF5 route: when no model is provided
        elif node is not None:
            display_name = node.name.replace("/", "")
            for name in natsort.natsorted(node.keys()):
                child = node[name]
                if isinstance(child, h5py.Dataset):
                    try:
                        arr = np.array(child)
                        if ONLY_MERGE_INTS and not np.issubdtype(arr.dtype, np.number):
                            arr = None
                    except Exception:
                        arr = None
                    if arr is None:
                        continue
                    arr = normalize_array(arr)
                    child_data[name] = arr
                    child_shapes[name] = arr.shape
                    if arr.size != 0:
                        non_empty_found = True

        # no valid input was provided
        else:
            return pd.DataFrame([])

        # no valid children found
        if not child_data or not non_empty_found:
            return pd.DataFrame([])

        # determine if all children are scalars (0D) or all are 1D arrays
        all_scalar_like = all(is_scalar_like(arr) for arr in child_data.values())
        all_1D = all((arr.ndim == 1 and arr.shape[0] > 1) for arr in child_data.values())

        # 0D case
        if all_scalar_like:
            data_dict = {str(display_name): [np.array(child_data[key]).item() for key in child_data]}
            return pd.DataFrame(data_dict, index=list(child_data.keys()))

        # 1D case
        elif all_1D:

            # check that the lengths (first dimension) are the same for every child
            lengths = [arr.shape[0] for arr in child_data.values()]
            if len(set(lengths)) != 1:
                message_title = "Error: Mismatched Dimensions"
                message_text = "Not all children have the same number of elements. Unable to merge."
                message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
                message_box.setWindowIcon(QIcon(self.window_icon_path))
                message_box.exec_()
                return pd.DataFrame([])

            # create a DataFrame with each child array as a separate column
            else:
                return pd.DataFrame(child_data)

        # if mixed or unsupported dimensions
        else:
            message_title = "Error: Incompatible Child Shapes"
            message_text = ("Unable to perform auto merging because the children inside the group "
                            "are not all scalars or all 1D arrays.")
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon(QIcon(self.window_icon_path))
            message_box.exec_()
            return pd.DataFrame([])

    #----------------------------------------------#

    def createDfDataObject(self, node, is_it_dataset = False, monitor_memory = False, auto_dtype = "infer_objects", min_chunk = 100_000, auto_merging = False):

        # function to estimate the memory requirements of a dataframe
        def estimate_memory_requirements(node, is_it_dataset):
            data_type_size = {
                'float64': 8,  # 64-bit floating point
                'float32': 4,  # 32-bit floating point
                'int64': 8,  # 64-bit integer
                'int32': 4,  # 32-bit integer
                'int16': 2,  # 16-bit integer
                'int8': 1,  # 8-bit integer
                'uint64': 8,  # 64-bit unsigned integer
                'uint32': 4,  # 32-bit unsigned integer
                'uint16': 2,  # 16-bit unsigned integer
                'uint8': 1,  # 8-bit unsigned integer
                'bool': 1,  # Boolean
                'complex64': 8,  # 64-bit complex number (composed of two 32-bit floats)
                'complex128': 16,  # 128-bit complex number (composed of two 64-bit floats)
                'float16': 2,  # 16-bit half precision float
            }
            if is_it_dataset:
                try:
                    dtype = str(node.dtype)
                except Exception as xcp:
                    dtype = "float64"
                element_size = data_type_size.get(dtype, 8)
                total_elements = np.prod(node.shape)
                total_memory_bytes = total_elements * element_size
                total_memory_mb = total_memory_bytes / (1024 ** 2)
                return total_memory_mb
            else:
                return np.nan

        # estimate needed memory
        mem_required_in_mb = estimate_memory_requirements(node, is_it_dataset)

        # reserve an extra 500 MB for safe operation
        safety_margin_mb = 500

        # get available memory
        available_memory_mb = psutil.virtual_memory().available / (1024 ** 2)

        # check memory limits
        if available_memory_mb < mem_required_in_mb + safety_margin_mb:
            message_title = "Error: Insufficient Memory"
            message_text = (
                "Not enough memory to load the data. Please free up some space before attempting this operation.\n\n"
                f"MEMORY SPECIFICATIONS\n"
                f"Memory Required: {mem_required_in_mb + safety_margin_mb:.2f} MB\n"
                f"Memory Available: {available_memory_mb:.2f} MB"
            )
            message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
            message_box.setWindowIcon((QIcon(self.window_icon_path)))
            message_box.exec_()
            return None, None, None, "memory_error"

        # open waiting widget
        self.waiting_widget_create_df = None
        if (len(node) >= 1_000_000 * int(self.dict_for_settings["min_big_data_sample_size"])) or (auto_merging and len(node) >= 10_000):
            if auto_merging:
                mem_required_in_mb = "Unknown"
            self.waiting_widget_create_df = WaitingWidgetCreateDf(app=self.app, app_root_path=self.app_root_path, parent=self, memory_in_mb=mem_required_in_mb)
            self.waiting_widget_create_df.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.waiting_widget_create_df.show()
            self.waiting_widget_create_df.repaint()
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        # init dtype
        dtype = None

        # init chunk size
        chunk_size = None

        # init attributes
        attributes = {}
        attributes["df"] = node.attrs
        attributes["columns"] = {}
        attributes["data"] = {}
        attributes["index"] = {}

        # dataset case
        if is_it_dataset:

            # force dtype if we have it as an attribute
            if node.attrs:
                if "dtype" in node.attrs.keys():
                    dtype = fromBytesToString(node.attrs["dtype"])

            # handle scalar dataset
            if node.shape == ():
                df = pd.DataFrame([node[()]], dtype=dtype)

            # handle non‐scalar dataset
            else:
                # check for a compound (structured) dtype
                if hasattr(node.dtype, "names") and node.dtype.names is not None:
                    # read entire structured array into memory
                    data_array = node[...]
                    # build a DataFrame column for each field name
                    df = pd.DataFrame({ field: data_array[field] for field in node.dtype.names })
                else:
                    # normal numeric (or simple) array
                    df = pd.DataFrame(node, dtype=dtype)

            # get chunk size
            if hasattr(node, "chunks") and node.chunks:
                chunk_size = node.chunks[0]
                if chunk_size < min_chunk:
                    chunk_size = min_chunk

            # get attributes
            attributes["data"] = node.attrs

        # group (df) case
        else:

            # use auto merging at group level
            if auto_merging:
                df = self.performAutoMergingGroup(node)

            # normal behaviour
            else:

                # get data and store it into a dictionary
                data = {}
                attrs = {}
                for name in node.keys():
                    child = node[name]
                    if isinstance(child, h5py.Dataset):
                        data[name] = np.array(child)
                        attrs[name] = child.attrs

                # just some parsing to avoid byte errors
                if "index" in data:
                    data["index"] = data["index"].astype(str)
                    attributes["index"] = attrs["index"]
                if "columns" in data:
                    data["columns"] = data["columns"].astype(str)
                    attributes["columns"] = attrs["columns"]
                if "data" in data:
                    if np.ndim(data["data"]) == 1:
                        data["data"] = np.expand_dims(data["data"], 1)
                    attributes["data"] = attrs["data"]

                # instantiate dataframe
                if "data" in data and "columns" in data and "index" in data:
                    df = pd.DataFrame(data["data"], columns = data["columns"], index = data["index"])
                elif "data" in data and "columns" in data and "index" not in data:
                    df = pd.DataFrame(data["data"], columns = data["columns"], index = np.arange(0,data["data"].shape[0]).astype(str))
                elif "data" in data and "columns" not in data and "index" in data:
                    df = pd.DataFrame(data["data"], columns = np.arange(0,data["data"].shape[1]).astype(str), index = data["index"])
                else:
                    df = pd.DataFrame([])

        # print for monitoring the memory
        if monitor_memory:
            print("\nINFORMATION FOR createDfDataObject() FUNCTION!\n")
            print("DataFrame object created with shape {}\n".format(df.shape))
            print("df.memory_usage: \n{}\n".format(df.memory_usage(deep=True)))
            df.info(memory_usage="deep")

        # automatically convert types if dtype is not found in attributes
        if auto_dtype:
            if not dtype:
                if auto_dtype == "infer_objects":
                    df = df.infer_objects()
                elif auto_dtype == "convert_dtypes":
                    df = df.convert_dtypes()

        # print for monitoring the memory
        if monitor_memory:
            print("\nINFORMATION FOR createDfDataObject() FUNCTION!\n")
            print("DataFrame object created with shape {}\n".format(df.shape))
            print("df.memory_usage: \n{}\n".format(df.memory_usage(deep=True)))
            df.info(memory_usage="deep")

        # close the waiting animation widget
        if self.waiting_widget_create_df:
            self.waiting_widget_create_df.close()
            self.waiting_widget_create_df = None
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        return df, attributes, chunk_size, ""

    #----------------------------------------------#

    def createDfFromNXCALS(self, data, attributes = [], chunk_size = 100_000, model = None, index = None, auto_merging = False):

        # auto merging case
        if auto_merging and model is not None and index is not None:
            df = self.performAutoMergingGroup(model=model, index=index)
            return df, attributes, chunk_size

        # case 1: data has shape (n,)
        if np.ndim(data) == 1:
            columns = np.array(["0"])
            index = np.arange(0,data.size).astype(str)

        # case 2: data has shape (n,m)
        else:
            columns = np.arange(0,data.shape[1]).astype(str)
            index = np.arange(0,data.shape[0]).astype(str)

        # create dataframe
        df = pd.DataFrame(data, columns=columns, index=index)

        return df, attributes, chunk_size

    #----------------------------------------------#

    def updateRightPanel(self, index, model = None, tree_type = "hdf5", verbose = True):

        # init variables
        dataframe = pd.DataFrame([])
        attributes = []

        # init boolean
        update_panel = True

        # CASE 1: NXCALS or POSTMORTEM
        if tree_type == "nxcals" or tree_type == "postmortem":

            # get data
            data = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)

            # get display name
            display = model.itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)

            # check it is not the same item
            if tree_type == "nxcals":
                if self.last_index_tree_view_nxcals == index:
                    return
                self.last_index_tree_view_nxcals = index
            if tree_type == "postmortem":
                if self.last_index_tree_view_postmortem == index:
                    return
                self.last_index_tree_view_postmortem = index

            # regular case
            if not self.isItAutoMergingGroupNXCALS(model, index):

                # if there is no data just skip
                if data.size == 0:
                    self.hideRightPanel(from_top_node=True, model=model)
                    return

                # for debugging
                if verbose:
                    print("Selected {} from {} TreeView!".format(tree_type, display))

                # get dataframe and attributes
                dataframe, attributes, chunk_size = self.createDfFromNXCALS(data)

            # auto merging case
            else:

                # for debugging
                if verbose:
                    print("Selected {} from {} TreeView with auto merging ON!".format(tree_type, display))

                # get dataframe and attributes
                dataframe, attributes, chunk_size = self.createDfFromNXCALS(data, model=model, index=index, auto_merging=True)
                if dataframe.empty:
                    update_panel = False

        # CASE 2: HDF5
        elif tree_type == "hdf5":

            # get node type (hdf5 or dir)
            node_type = model.get_type_from_index(index)

            # if we have a dir do not update right panel
            if node_type == "dir":

                # hide right panel if we have no dataframe
                self.hideRightPanel(from_top_node=True, model=model)
                return

            # get corresponding hdf5 file path
            hdf_path = model.get_hdf5_path_from_index(index)

            # get path
            path = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
            path = os.path.relpath(path, hdf_path)

            # get node
            node = None
            if hdf_path in self.treeView_hdf5.hdf_dict:
                if self.treeView_hdf5.hdf_dict[hdf_path]:
                    node = self.treeView_hdf5.hdf_dict[hdf_path][path]
            if node == None:
                return

            # get display name
            display = model.itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)

            # check it is a dataframe or not
            is_it_df = self.isItDataframeNode(node)

            # check if it is dataset
            is_it_dataset = isinstance(node, h5py.Dataset)

            # check it is not the same item
            if self.last_index_tree_view_hdf5 == index:
                return

            # store last index
            self.last_index_tree_view_hdf5 = index

            # now check that we are in a group that is a dataframe or we have a dataset
            if is_it_df or is_it_dataset:

                # for debugging
                if verbose:
                    print("Selected {} from HDF5 TreeView!".format(path))

                # create the data to be passed to the tabs
                dataframe, attributes, chunk_size, error_message = self.createDfDataObject(node, is_it_dataset=is_it_dataset)
                if error_message:
                    update_panel = False

            # if it is not df or dataset then check if auto is ON
            elif self.isItAutoMergingGroup(node):

                # for debugging
                if verbose:
                    print("Selected {} from HDF5 TreeView with auto merging ON!".format(path))

                # create the data to be passed to the tabs
                dataframe, attributes, chunk_size, error_message = self.createDfDataObject(node, is_it_dataset=False, auto_merging=True)
                if error_message or dataframe.empty:
                    update_panel = False

            # do not show the panel
            else:

                # update boolean
                update_panel = False

        # update the panel
        if update_panel:

            # get color dict
            color_dict = {}
            color_dict["color_background"] = self.dict_for_settings["color_background"]
            color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

            # init tab widgets
            visualization_tab = MainVisualization(self.app, dataframe, attributes, display, False, last_selected_sub_tab=self.last_selected_sub_tab_visualization, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget_right, global_parent=self, color_dict=color_dict, mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"], pyqtgraph_default_downsample = self.dict_for_settings["setting_enable_downsampling_plots"], sticky_options=self.dict_for_settings["setting_sticky_options"], display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"], ncurves_at_init = self.dict_for_settings["ncurves_at_init"], min_big_data_sample_size = self.dict_for_settings["min_big_data_sample_size"], chunk_size = chunk_size, max_n_columns=self.dict_for_settings["max_n_columns"])
            analysis_tab = MainAnalysis(self.app, dataframe, attributes, display, False, last_selected_sub_tab=self.last_selected_sub_tab_analysis, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget_right, global_parent=self, color_dict=color_dict, mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"], pyqtgraph_default_downsample = self.dict_for_settings["setting_enable_downsampling_plots"], sticky_options=self.dict_for_settings["setting_sticky_options"], display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"], ncurves_at_init = self.dict_for_settings["ncurves_at_init"], min_big_data_sample_size = self.dict_for_settings["min_big_data_sample_size"], chunk_size = chunk_size, max_n_columns=self.dict_for_settings["max_n_columns"])

            # init the tabs
            self.initRightTabs(remove_tabs = True, update_last_tab_index = False, visualization_tab = visualization_tab, analysis_tab = analysis_tab)

            # build the tab
            current_tab_widget = self.tabWidget_right.widget(self.last_selected_tab)
            if current_tab_widget is not None:
                if hasattr(current_tab_widget, "tab_is_built"):
                    if not current_tab_widget.tab_is_built:
                        current_tab_widget.buildTab()

        # ignore top levels
        else:

            # hide right panel if we have no dataframe
            self.hideRightPanel(from_top_node=True, model=model)
            return

        return

    #----------------------------------------------#

    def createVisualizationAndAnalysisTabs(self, df, display_name = "", empty_selection_in_tree = True):

        # deselect tree (hdf5)
        if empty_selection_in_tree:
            if self.treeView_hdf5.treeView:
                if self.treeView_hdf5.treeView.selectionModel():
                    self.treeView_hdf5.treeView.selectionModel().blockSignals(True)
                    self.treeView_hdf5.treeView.clearSelection()
                    self.last_index_tree_view_hdf5 = None
                    self.treeView_hdf5.treeView.selectionModel().blockSignals(False)

        # deselect tree (nxcals)
        if empty_selection_in_tree:
            if self.treeView_nxcals.treeView:
                if self.treeView_nxcals.treeView.selectionModel():
                    self.treeView_nxcals.treeView.selectionModel().blockSignals(True)
                    self.treeView_nxcals.treeView.clearSelection()
                    self.last_index_tree_view_nxcals = None
                    self.treeView_nxcals.treeView.selectionModel().blockSignals(False)

        # deselect tree (postmortem)
        if empty_selection_in_tree:
            if self.treeView_postmortem.treeView:
                if self.treeView_postmortem.treeView.selectionModel():
                    self.treeView_postmortem.treeView.selectionModel().blockSignals(True)
                    self.treeView_postmortem.treeView.clearSelection()
                    self.last_index_tree_view_postmortem = None
                    self.treeView_postmortem.treeView.selectionModel().blockSignals(False)

        # get color dict
        color_dict = {}
        color_dict["color_background"] = self.dict_for_settings["color_background"]
        color_dict["color_foreground_palette_name"] = self.dict_for_settings["color_foreground_palette_name"]

        # init tab widgets
        if df.empty:
            visualization_tab = None
            analysis_tab = None
            update_last_tab_index = True
        else:
            visualization_tab = MainVisualization(self.app, df, {}, display_name, False, last_selected_sub_tab=self.last_selected_sub_tab_visualization, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget_right, global_parent=self, color_dict=color_dict, mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"], pyqtgraph_default_downsample = self.dict_for_settings["setting_enable_downsampling_plots"], sticky_options=self.dict_for_settings["setting_sticky_options"], display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"], ncurves_at_init = self.dict_for_settings["ncurves_at_init"], min_big_data_sample_size = self.dict_for_settings["min_big_data_sample_size"], chunk_size = None, max_n_columns = self.dict_for_settings["max_n_columns"])
            analysis_tab = MainAnalysis(self.app, df, {}, display_name, False, last_selected_sub_tab=self.last_selected_sub_tab_analysis, app_root_path=self.app_root_path, window_icon_path=self.window_icon_path, parent=self.tabWidget_right, global_parent=self, color_dict=color_dict, mouse_mode_1_button=self.dict_for_settings["setting_enable_1_button_mouse_mode"], pyqtgraph_default_downsample = self.dict_for_settings["setting_enable_downsampling_plots"], sticky_options=self.dict_for_settings["setting_sticky_options"], display_strings_on_x_axis=self.dict_for_settings["setting_display_strings_on_x_axis"], ncurves_at_init = self.dict_for_settings["ncurves_at_init"], min_big_data_sample_size = self.dict_for_settings["min_big_data_sample_size"], chunk_size = None, max_n_columns = self.dict_for_settings["max_n_columns"])
            update_last_tab_index = False

        # init the tabs
        self.initRightTabs(remove_tabs=True, update_last_tab_index=update_last_tab_index, visualization_tab=visualization_tab, analysis_tab=analysis_tab)

        # change the colors
        self.changeRightTabColors()

        # build the tab
        current_tab_widget = self.tabWidget_right.widget(self.last_selected_tab)
        if current_tab_widget is not None:
            if hasattr(current_tab_widget, "tab_is_built"):
                if not current_tab_widget.tab_is_built:
                    current_tab_widget.buildTab()

        # update view to empty selection
        if empty_selection_in_tree:
            self.update()
            self.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

        return

    #----------------------------------------------#

    def removeTabs(self, remove_selection_tab = False):

        # set the number of removed tabs based on the value of remove_selection_tab
        n_removed_tabs = 3 if remove_selection_tab else 2

        # check widget exists
        if self.tabWidget_right:

            # block signals
            self.tabWidget_right.blockSignals(True)

            # get the total number of tabs and calculate the index for the last n_removed_tabs
            total_tabs = self.tabWidget_right.count()
            removed_tabs_start_index = max(0, total_tabs - n_removed_tabs)

            # remove the last n_removed_tabs
            for tab in range(removed_tabs_start_index, total_tabs):
                widget = self.tabWidget_right.widget(removed_tabs_start_index)
                widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                widget.close()
                self.tabWidget_right.removeTab(removed_tabs_start_index)

            # set the last tab references to None based on the value of remove_selection_tab
            self.analysis_tab = None
            self.visualization_tab = None
            if remove_selection_tab:
                self.selection_tab = None

            # unblock signals
            self.tabWidget_right.blockSignals(False)

        return

    #----------------------------------------------#

    def hideRightPanel(self, from_top_node = False, model = None):

        # remove the panel
        if from_top_node:

            # remake the tabs with empty widgets
            self.initRightTabs(remove_tabs = True, update_last_tab_index = False)

            # empty last index
            self.last_index_tree_view_hdf5 = None
            self.last_index_tree_view_nxcals = None
            self.last_index_tree_view_postmortem = None

        return

    #----------------------------------------------#

    def setUpOpsAfterInit(self):

        # set up a timer for those operations that will be set after the init
        self.timer_after_init = QTimer(self)
        self.timer_after_init.setInterval(50)
        self.timer_after_init.timeout.connect(self.doOperationsAfterInit)
        self.timer_after_init.start()

        return

    #----------------------------------------------#

    def doOperationsAfterInit(self):

        # stop and delete the timer
        self.timer_after_init.stop()
        del self.timer_after_init

        # open file at startup (if introduced)
        if self.startup_dir_to_open:
            if os.path.exists(self.startup_dir_to_open):
                self.openFile(file_path = self.startup_dir_to_open)

        return

    #----------------------------------------------#

    def getDroppedFiles(self, event):
        return [url.toLocalFile() for url in event.mimeData().urls()]

    #----------------------------------------------#

    def dragEnterEvent(self, event):
        event.accept() if self.getDroppedFiles(event) else event.ignore()
        return

    #----------------------------------------------#

    def dropEvent(self, event):
        for file_path in self.getDroppedFiles(event):
            if os.path.isdir(file_path):
                self.openFile(file_path = file_path, file_or_dir = "dir")
            else:
                try:
                    xt = file_path.split(".")[-1]
                    if xt == "hdf" or xt == "h5" or xt == "hdf5" or xt == "h5part":
                        self.openFile(file_path = file_path, file_or_dir = "file")
                except Exception as xcp:
                    pass
            break
        return

    #----------------------------------------------#

    def retrieveSettings(self):

        # retrieve only if path was created previously
        if os.path.exists(self.qsettings.fileName()):

            # print
            print("Retrieving stored settings from: {}".format(self.qsettings.fileName()))

            # save all settings
            for key in self.default_settings:
                value = self.qsettings.value(key)
                if value is not None:
                    self.dict_for_settings[key] = int(value) if "color" not in key else str(value)
                else:
                    self.dict_for_settings[key] = self.default_settings[key]

        # defaults
        else:

            # save defaults
            self.dict_for_settings.update(self.default_settings)

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # print
        print("Closing the application...")

        # handle settings
        for key, value in self.dict_for_settings.items():
            value = int(value) if "color" not in key else str(value)
            self.qsettings.setValue(key, value)

        # handle nxcals threads
        if self.treeView_nxcals:
            if self.treeView_nxcals.threads_panel:
                for id in self.treeView_nxcals.threads_panel.ids:
                    try:
                        self.treeView_nxcals.threads_panel.removeThread(id, terminate_thread = False)
                    except Exception as xcp:
                        print("Unable to remove thread (id = {}) due to the following exception: {}".format(id, xcp))

        # handle postmortem threads
        if self.treeView_postmortem:
            if self.treeView_postmortem.threads_panel:
                for id in self.treeView_postmortem.threads_panel.ids:
                    try:
                        self.treeView_postmortem.threads_panel.removeThread(id, terminate_thread = False)
                    except Exception as xcp:
                        print("Unable to remove thread (id = {}) due to the following exception: {}".format(id, xcp))

        # close additional windows
        for win_id in list(self.visualization_tab_new_windows.keys()):
            self.visualization_tab_new_windows[win_id].close()
        for win_id in list(self.analysis_tab_new_windows.keys()):
            self.analysis_tab_new_windows[win_id].close()
        for win_id in list(self.attributes_table_new_windows.keys()):
            self.attributes_table_new_windows[win_id].close()

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

    def change_icon_color(self, icon: QIcon, color: QColor) -> QIcon:
        pixmap = icon.pixmap(icon.availableSizes()[0])
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return QIcon(pixmap)

    #----------------------------------------------#

    def show_java_error(self):
        message_title = "Error"
        message_text = (
            "The 'pytimber' library failed to initialize correctly due to missing Java dependencies in your machine.\n\n"
            "The necessary dependencies have now been installed automatically using "
            "'cmmnbuild_dep_manager'. This tool handles the resolution and installation of required "
            "Java dependencies for the application.\n\n"
            "Please restart DAVIT to apply the changes and ensure that all components function properly."
        )
        message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self)
        message_box.setWindowIcon(QIcon(self.window_icon_path))
        message_box.exec_()
        return

    #----------------------------------------------#

#################################################################
#################################################################