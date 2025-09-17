#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *
from davit.utils.hdf5_tree_view_model import HDF5TreeViewModel

#################################################################
#################################################################

class HDF5TreeView(QFrame):

    #----------------------------------------------#

    def __init__(self, parent = None, global_parent = None):

        # inheritance
        super().__init__(parent)

        # attributes
        self.parent = parent
        self.global_parent = global_parent

        # own attributes
        self.hdf_dict = {}
        self.treeView_model = None
        self.treeView_model_filtered = None
        self.filters_applied = False
        self._selection_model = None
        self._selection_changed_handler = None

        # build the tree
        self.buildTree()

        return

    #----------------------------------------------#

    def buildTree(self):

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

        return

    #----------------------------------------------#

    def bindWidgetsTreeView(self, model):

        # reset the connections we manage explicitly
        try:
            self.treeView.expanded.disconnect()
        except (TypeError, RuntimeError):
            pass

        try:
            self.treeView.collapsed.disconnect()
        except (TypeError, RuntimeError):
            pass

        try:
            self.treeView.customContextMenuRequested.disconnect()
        except (TypeError, RuntimeError):
            pass

        if self._selection_model and self._selection_changed_handler:
            try:
                self._selection_model.selectionChanged.disconnect(self._selection_changed_handler)
            except (TypeError, RuntimeError):
                pass
            finally:
                self._selection_model = None
                self._selection_changed_handler = None

        # bindings for the tree model
        self.treeView.expanded.connect(model.handle_expanded)
        self.treeView.collapsed.connect(model.handle_collapsed)

        # binding for the click or selection
        selection_model = self.treeView.selectionModel()
        if selection_model is not None:
            def _handle_selection_changed(selected, deselected, *, _model=model):
                self.itemFromTreeviewSelectionChanged(model=_model)

            selection_model.selectionChanged.connect(_handle_selection_changed)
            self._selection_model = selection_model
            self._selection_changed_handler = _handle_selection_changed

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
        path_list = []
        hdf_path_list = []
        type_list = []

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

                # get corresponding hdf5 file path
                hdf_path = model.get_hdf5_path_from_index(index)
                hdf_path_list.append(hdf_path)

                # get node
                path = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
                path = os.path.relpath(path, hdf_path)
                path_list.append(path)
                node = None
                if hdf_path:
                    if hdf_path in self.hdf_dict.keys():
                        if self.hdf_dict[hdf_path]:
                            node = self.hdf_dict[hdf_path][path]

                # check types
                if isinstance(node, h5py.Dataset):
                    type_list.append("Dataset")
                elif isinstance(node, h5py.Group):
                    if self.is_df_node(index.model(), index):
                        type_list.append("Dataframe")
                    else:
                        type_list.append("Group")
                else:
                    type_list.append("Other")

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
            print(f"Path List: {path_list}")
            print(f"HDF Path List: {hdf_path_list}")
            print(f"Type List: {type_list}")

        # detect if "Other" is in the type list
        if "Other" in type_list or "Group" in type_list:
            only_df_and_ds = False
        else:
            only_df_and_ds = True

        # create the menu
        menu = QMenu()

        # init dict
        self.menu_right_click_dict = {}

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

        # action for opening the attributes window
        self.menu_right_click_dict["open_hdf5_attributes"] = menu.addAction(qta.icon("fa5s.table"), self.tr("Open HDF5 attributes table"))
        self.menu_right_click_dict["open_hdf5_attributes"].triggered.connect(lambda: self.global_parent.openHDF5AttributesWindow(path_list=path_list, hdf_path_list=hdf_path_list, type_list=type_list))
        self.menu_right_click_dict["open_hdf5_attributes"].setEnabled(True)

        # action for opening new windows
        if only_df_and_ds:
            if len(path_list) > 1:
                self.menu_right_click_dict["open_visualization_in_single_window_merge"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in single window (merge)"))
                self.menu_right_click_dict["open_visualization_in_single_window_merge"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindow(path_list = path_list, hdf_path_list = hdf_path_list, type_list = type_list, merge = True, auto_multiple_axes = False))
                self.menu_right_click_dict["open_visualization_in_single_window_merge"].setEnabled(True)
                self.menu_right_click_dict["open_visualization_in_single_window_merge_multiple_axes"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in single window (merge along multiple axes)"))
                self.menu_right_click_dict["open_visualization_in_single_window_merge_multiple_axes"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindow(path_list = path_list, hdf_path_list = hdf_path_list, type_list = type_list, merge = True, auto_multiple_axes = True))
                self.menu_right_click_dict["open_visualization_in_single_window_merge_multiple_axes"].setEnabled(True)
                self.menu_right_click_dict["open_visualization_in_multiple_windows"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in multiple windows"))
                self.menu_right_click_dict["open_visualization_in_multiple_windows"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindow(path_list = path_list, hdf_path_list = hdf_path_list, type_list = type_list))
                self.menu_right_click_dict["open_visualization_in_multiple_windows"].setEnabled(True)
                self.menu_right_click_dict["open_analysis_in_multiple_windows"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open analysis in multiple windows"))
                self.menu_right_click_dict["open_analysis_in_multiple_windows"].triggered.connect(lambda: self.global_parent.openNewAnalysisWindow(path_list = path_list, hdf_path_list = hdf_path_list, type_list = type_list))
                self.menu_right_click_dict["open_analysis_in_multiple_windows"].setEnabled(True)
            else:
                self.menu_right_click_dict["open_visualization_in_new_window"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open visualization in new window"))
                self.menu_right_click_dict["open_visualization_in_new_window"].triggered.connect(lambda: self.global_parent.openNewVisualizationWindow(path_list = path_list, hdf_path_list = hdf_path_list, type_list = type_list))
                self.menu_right_click_dict["open_visualization_in_new_window"].setEnabled(True)
                self.menu_right_click_dict["open_analysis_in_new_window"] = menu.addAction(qta.icon("msc.empty-window"), self.tr("Open analysis in new window"))
                self.menu_right_click_dict["open_analysis_in_new_window"].triggered.connect(lambda: self.global_parent.openNewAnalysisWindow(path_list = path_list, hdf_path_list = hdf_path_list, type_list = type_list))
                self.menu_right_click_dict["open_analysis_in_new_window"].setEnabled(True)

        # update view
        menu.exec_(self.treeView.viewport().mapToGlobal(position))

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

    def headerProcessing(self, hide_meta_columns = True, type_set_header_widths = "type_1"):

        # header changes
        self.treeView.setHeaderHidden(False)
        self.treeView.header().setVisible(True)

        # set meta columns hidden
        if hide_meta_columns:
            self.treeView.setColumnHidden(self.treeView_model.header_labels.index("Type"), True)
            self.treeView.setColumnHidden(self.treeView_model.header_labels.index("HDF5"), True)
            self.treeView.setColumnHidden(self.treeView_model.header_labels.index("IconStr"), True)
            headers_visible_length = len(self.treeView_model.header_labels) - 3
        else:
            headers_visible_length = len(self.treeView_model.header_labels)

        # set header equal widths
        width_frame = self.treeView.frameGeometry().width()
        if type_set_header_widths == "type_1":
            for column in range(0, headers_visible_length):
                if column == 0:
                    self.treeView.setColumnWidth(column, round(width_frame / 2))
                else:
                    self.treeView.setColumnWidth(
                        column,
                        round((width_frame / 2) / (headers_visible_length - 1)),
                    )
        else:
            for column in range(0, headers_visible_length):
                if column == 0:
                    self.treeView.setColumnWidth(
                        column,
                        round(1.1 * width_frame / headers_visible_length),
                    )
                else:
                    self.treeView.setColumnWidth(
                        column,
                        round(width_frame / headers_visible_length),
                    )

        return

    #----------------------------------------------#

    def clearTreeView(self):

        # clear model
        self.treeView.model().clear()

        # init variables
        self.hdf_dict = {}
        self.treeView_model = None
        self.treeView_model_filtered = None

        # reset all connections
        try:
            self.treeView.disconnect()
        except Exception as xcp:
            print("Exception: {}".format(xcp))

        # show and update
        self.treeView.update()
        self.treeView.show()

        return

    #----------------------------------------------#

    def refreshTreeView(self, dir_path, filters = None):

        # case 1: NORMAL PROCEDURE (POPULATE THE TREE DYNAMICALLY)
        if not filters:

            # init hdf5 files dict
            self.hdf_dict = {}

            # declare treeview model
            self.treeView_model = HDF5TreeViewModel(dir_path, filter_mode = False, parent = self, global_parent = self.global_parent)
            self.treeView_model_filtered = None

            # set the model
            self.treeView.setModel(self.treeView_model)

            # bindings for the tree
            self.bindWidgetsTreeView(self.treeView_model)

            # set boolean and style
            self.filters_applied = False
            self.setStyleSheet("QTreeView{background-color:#ffffff;}")
            self.global_parent.tabWidget_left_filters_hdf5_button.setChecked(False)
            self.global_parent.tabWidget_left_filters_hdf5_button.setToolTip("")

        # case 2: APPLY FILTERS (POPULATE THE TREE AT ONCE)
        else:

            # expand and collapse to load the whole tree
            self.fully_expand_treeview(self.treeView)
            self.treeView.collapseAll()

            # filter the data
            self.tree_dict = self.treeView_model.filter_data(filters)

            # declare new filtered model
            self.treeView_model_filtered = HDF5TreeViewModel(filter_mode = True, tree_dict = self.tree_dict, parent = self, global_parent = self.global_parent)

            # set the model
            self.treeView.setModel(self.treeView_model_filtered)

            # bindings for the tree
            self.bindWidgetsTreeView(self.treeView_model_filtered)

            # set boolean and style
            self.filters_applied = True
            self.setStyleSheet("QTreeView{background-color:#fff9e6;}")
            self.global_parent.tabWidget_left_filters_hdf5_button.setChecked(True)
            self.global_parent.tabWidget_left_filters_hdf5_button.setToolTip(json.dumps(filters, indent=2))

        # adjust headers
        self.headerProcessing()

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
        if len(self.treeView.selectedIndexes()) / (len(self.treeView_model.header_labels) - 3) > 1:
            self.global_parent.hideRightPanel(from_top_node=True, model=model)
            return

        # get true index (first column)
        index = indexes[0]

        # update in case everything is OK
        self.global_parent.updateRightPanel(index, model=model, tree_type="hdf5")

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

        # get corresponding hdf5 file path
        hdf_path = model.get_hdf5_path_from_index(index)

        # get node and display
        display_name = model.itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)
        full_path = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
        path = os.path.relpath(full_path, hdf_path)
        node = None
        if hdf_path:
            if hdf_path in self.hdf_dict.keys():
                if self.hdf_dict[hdf_path]:
                    node = self.hdf_dict[hdf_path][path]

        # check it is a dataframe or not
        is_it_df = self.global_parent.isItDataframeNode(node)

        # check if it is dataset
        is_it_dataset = isinstance(node, h5py.Dataset)

        # does it have children?
        does_it_have_children = model.hasChildren(index)

        # now check that we are in a group that is a dataframe or we have a dataset
        if is_it_df or is_it_dataset:

            # create the dataframe
            dataframe, attributes, chunk_size, error_message = self.global_parent.createDfDataObject(node, is_it_dataset=is_it_dataset)
            if error_message:
                return

            # append the important stuff
            self.df_list_to_selection.append(dataframe)
            self.metadata_list_to_selection.append([display_name, str(dataframe.shape), None, str(dataframe.shape), full_path, "HDF5", get_index_type(attributes = attributes, df = dataframe, return_dtype_otherwise = True)])
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

        # determine which model to use
        if self.filters_applied:
            model = self.treeView_model_filtered
        else:
            model = self.treeView_model

        # get selected indexes
        indexes = self.treeView.selectedIndexes()

        # check if we have selected at least one item
        if indexes:

            # get number of items
            n_items = round(len(self.treeView.selectedIndexes()) / (len(self.treeView_model.header_labels) - 3))

            # iterate over items
            for n in range(0, n_items):

                # get true index
                i = n * (len(self.treeView_model.header_labels) - 3)

                # get index
                index = indexes[i]

                # guarantee that model is loaded
                expanded_indexes = self.expand_all_tracking(self.treeView, [index])
                self.collapse_all_tracking(self.treeView, [index], expanded_indexes)

                # determine if it should be added
                self.appendToSelectionList(model, index)

        return self.df_list_to_selection, self.metadata_list_to_selection, self.chunk_size_list

    #----------------------------------------------#

    def expand_top_level(self) -> None:
        tree = self.treeView
        model = tree.model()
        root = QModelIndex()
        for row in range(model.rowCount(root)):
            top_index = model.index(row, 0, root)
            tree.expand(top_index)

    #----------------------------------------------#

    def fully_expand_treeview(self, tree_view, index=QModelIndex()):
        model = tree_view.model()
        row_count = model.rowCount(index)
        for row in range(row_count):
            child_index = model.index(row, 0, index)
            if child_index.isValid():
                tree_view.expand(child_index)
                QApplication.processEvents()
                self.fully_expand_treeview(tree_view, child_index)

    #----------------------------------------------#

    def expand_all(self, tree_view, indexes):
        for index in indexes:
            tree_view.expand(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.is_df_node(child_index.model(), child_index):
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
                if child_index.isValid() and not self.is_df_node(child_index.model(), child_index):
                    self.expand_all_tracking(tree_view, [child_index], expanded_indexes)
        return expanded_indexes

    #----------------------------------------------#

    def collapse_all(self, tree_view, indexes):
        for index in indexes:
            tree_view.collapse(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.is_df_node(child_index.model(), child_index):
                    self.collapse_all(tree_view, [child_index])

    def collapse_all_tracking(self, tree_view, indexes, expanded_indexes):
        for index in indexes:
            if index in expanded_indexes:
                tree_view.collapse(index)
                expanded_indexes.remove(index)
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                if child_index.isValid() and not self.is_df_node(child_index.model(), child_index):
                    self.collapse_all_tracking(tree_view, [child_index], expanded_indexes)

    #----------------------------------------------#

    def is_df_node(self, model, index):
        hdf_path = model.get_hdf5_path_from_index(index)
        full_path = model.itemFromIndex(index).data(Qt.ItemDataRole.UserRole)
        if not hdf_path:
            return False
        path = os.path.relpath(full_path, hdf_path)
        node = None
        if hdf_path:
            if hdf_path in self.hdf_dict.keys():
                if self.hdf_dict[hdf_path]:
                    node = self.hdf_dict[hdf_path][path]
        is_it_df = self.global_parent.isItDataframeNode(node)
        return is_it_df

    #----------------------------------------------#

#################################################################
#################################################################