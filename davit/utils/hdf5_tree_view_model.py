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

# CONSTANTS

MIN_N_ELEMENTS_PROGRESS_BAR = 999
DESIRED_UPDATES_FOR_PROGRESS_BAR = 100 # (e.g. 100 for 1% increments)

class HDF5TreeViewModel(QStandardItemModel):

    #----------------------------------------------#

    def __init__(self, path = "", header_labels = ['Object', 'Type', 'HDF5', 'nAttrs', 'Shape', 'IconStr'], only_h5_and_dirs = True, filters = {}, filter_mode = False, tree_dict = {}, parent = None, global_parent = None):

        # inheritance
        super().__init__()

        # attributes
        self.path = path
        self.header_labels = header_labels
        self.only_h5_and_dirs = only_h5_and_dirs
        self.filters = filters
        self.filter_mode = filter_mode
        self.tree_dict = tree_dict
        self.parent = parent
        self.global_parent = global_parent

        # init properties
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(len(self.header_labels))
        self.setHorizontalHeaderLabels(self.header_labels)

        # CASE 1: NO FILTERS (DYNAMICALLY BUILT / LAZY LOADING)
        if not self.filter_mode:

            # if path is a single HDF5 file
            if self.is_h5_file(self.path):

                # open h5 file
                xcp = self.open_h5_file(path)
                if xcp:
                    self.error_message_wrong_h5_file(xcp)
                hdf = self.parent.hdf_dict[self.path]

                # create a top-level item representing the root of this single HDF5 file
                if hdf:
                    root = self.add_h5_node(parent_item=self, node=hdf, hdf_path=self.path)

            # normal directory procedure
            else:

                # add a top-level directory item and do not drill further
                root = self.add_node(self, self.path, os.sep)

        # CASE 2: FILTERS (NOT DYNAMICALLY BUILT)
        else:

            # add the root node and all the children
            root_dict = self.tree_dict["/"]
            type_item = root_dict["type_item"]
            hdf5_path_item = root_dict["hdf5_path_item"]
            attrs_item = root_dict["attrs_item"]
            dataset_item = root_dict["dataset_item"]
            tooltip_str = root_dict["tooltip_str"]
            icon_str = root_dict["icon_str"]
            foreground_color = root_dict["foreground_color"]
            root = self.add_node_after_filter(self, root_dict["full_path"], "/", type_item, hdf5_path_item, attrs_item, dataset_item, tooltip_str, icon_str, foreground_color)
            self.load_dict_children(parent_item=root, parent_dict=root_dict)

        return

    #----------------------------------------------#

    def load_dict_children(self, parent_item, parent_dict):

        # get children
        children_dict = parent_dict.get("children")

        # iterate over children
        if children_dict is not None:
            for child_name, child_dict in children_dict.items():
                if child_name == "Loading...":
                    continue
                if child_dict["show"][0] and child_dict["show"][1] and child_dict["show"][2]:
                    type_item = child_dict["type_item"]
                    hdf5_path_item = child_dict["hdf5_path_item"]
                    attrs_item = child_dict["attrs_item"]
                    dataset_item = child_dict["dataset_item"]
                    tooltip_str = child_dict["tooltip_str"]
                    icon_str = child_dict["icon_str"]
                    foreground_color = child_dict["foreground_color"]
                    node = self.add_node_after_filter(parent_item, child_dict["full_path"], child_name, type_item, hdf5_path_item, attrs_item, dataset_item, tooltip_str, icon_str, foreground_color)
                    if "children" in child_dict.keys():
                        self.load_dict_children(parent_item=node, parent_dict=child_dict)

        return

    #----------------------------------------------#

    def filter_data(self, filters, verbose = False):

        # store filters
        self.filters = filters

        # iterate with the filters
        result_dict = self.iterate_model()

        # for debugging
        if verbose:
            print("TREE")
            print(json.dumps(result_dict, indent=2))

        # recursively backpropagate the 'show' attribute from leaf nodes to top nodes of the tree
        self.propagate_show(result_dict["/"])

        # for debugging
        if verbose:
            print("TREE AFTER BACKPROPAGATION")
            print(json.dumps(result_dict, indent=2))

        return result_dict

    #----------------------------------------------#

    def propagate_show(self, node, propagate_1 = True):

        # base case: bottom node, nothing to propagate
        if "children" not in node:
            if node["h5_type"] == "dataset":
                propagate_1 = False
            return node["show"], propagate_1

        # recursive case: propagate show value up the tree
        show = [False, False, node["show"][2]]
        for child in node["children"].values():

            # recursive call
            child_show, propagate_1 = self.propagate_show(child, propagate_1)

            # update booleans
            show[0] = show[0] or child_show[0]
            if propagate_1:
                show[1] = show[1] or child_show[1]
            else:
                show[1] = node["show"][1]

            # update propagation booleans
            if node["h5_type"] == "group":
                propagate_1 = True

            # update waiting widget
            if self.global_parent:
                if self.global_parent.waiting_widget:
                    self.global_parent.waiting_widget.updateLabel()

        # update value
        node["show"] = show
        return show, propagate_1

    #----------------------------------------------#

    def iterate_model(self, parent=QModelIndex()):

        # init result
        result = {}

        # iterate over rows
        for row in range(self.rowCount(parent)):

            # get first column
            index = self.index(row, 0, parent)
            item = self.itemFromIndex(index)

            # skip if no item
            if not item:
                continue

            # skip if dummy child
            display_text = item.text()
            if display_text == "Loading...":
                continue

            # get full path
            full_path = item.data(Qt.ItemDataRole.UserRole)

            # get hdf5 path
            hdf_path = self.get_hdf5_path_from_index(index)

            # get display
            display = item.data(Qt.ItemDataRole.DisplayRole)

            # init
            node = None
            sub_hdf_path = ""

            # get node
            if hdf_path and (hdf_path in self.parent.hdf_dict):
                sub_hdf_path = os.path.relpath(full_path, hdf_path)
                node_obj = self.parent.hdf_dict[hdf_path]
                if node_obj is not None and sub_hdf_path in node_obj:
                    node = node_obj[sub_hdf_path]
                else:
                    node = None

            # get data from item
            key = display
            value = {"full_path": full_path}

            # store group or dataset
            value["h5_type"] = ""
            if node:
                if isinstance(node, h5py.Group):
                    value["h5_type"] = "group"
                elif isinstance(node, h5py.Dataset):
                    value["h5_type"] = "dataset"

            # get index and item
            index = self.index(row, 0, parent)
            item = self.itemFromIndex(index)

            # store more metadata
            value["type_item"] = self.itemFromIndex(self.index(row, 1, parent)).text()
            value["hdf5_path_item"] = hdf_path
            value["attrs_item"] = self.itemFromIndex(self.index(row, 3, parent)).text()
            value["dataset_item"] = self.itemFromIndex(self.index(row, 4, parent)).text()
            value["icon_str"] = self.itemFromIndex(self.index(row, 5, parent)).text()
            value["tooltip_str"] = item.data(Qt.ItemDataRole.ToolTipRole)
            value["foreground_color"] = item.foreground().color().name()

            # apply filters
            b1 = self.filter_by_path_h5(hdf_path, sub_hdf_path)
            b2 = self.filter_by_path_dir(full_path, hdf_path)
            b3 = self.filter_by_attributes(node, type = "group")
            b4 = self.filter_by_attributes(node, type = "dataset")

            # init show
            value["show"] = [True, True, True]

            # show or not? (path)
            if b1 and b2:
                value["show"][0] = True
            else:
                value["show"][0] = False

            # show or not? (group)
            if b3:
                value["show"][1] = True
            else:
                value["show"][1] = False

            # show or not? (dataset)
            if b4:
                value["show"][2] = True
            else:
                value["show"][2] = False

            # recursively iterate over child items
            if self.hasChildren(index):
                value["children"] = self.iterate_model(index)

            # store result
            result[key] = value

            # update waiting widget
            if self.global_parent:
                if self.global_parent.waiting_widget:
                    self.global_parent.waiting_widget.updateLabel()

        return result

    #----------------------------------------------#

    def filter_by_attributes(self, node, type = "group"):

        # init boolean
        boolean = True

        # case 1
        if not self.filters["attributes"][type]:
            return True

        # case 2
        if not node:
            return True

        # case 3
        if type == "group":
            if not isinstance(node, h5py.Group):
                return True
        elif type == "dataset":
            if not isinstance(node, h5py.Dataset):
                return True

        # case 4
        if not (len(node.attrs) > 0):
            return False

        # iterate over attributes
        for filtered_attr in self.filters["attributes"][type].keys():

            # check attribute exists
            if filtered_attr in node.attrs.keys():

                # get interval
                interval = self.filters["attributes"][type][filtered_attr]

                # try catch flow
                try:

                    # convert from bytes to string
                    at = fromBytesToString(node.attrs[filtered_attr])

                    # CASE 1 (INTERVAL SEARCH)
                    if (interval[0] != "" and interval[0] != None) and (interval[1] != "" and interval[1] != None):
                        if float(interval[0]) <= float(at) <= float(interval[1]):
                            boolean = True
                        else:
                            return False

                    # case 2 (EXACT KEY VALUE)
                    elif (interval[0] != "" and interval[0] != None):
                        if str(at).lower() == str(interval[0]).lower():
                            boolean = True
                        else:
                            return False

                # just print exception
                except Exception as xcp:
                    print("Exception at filter_by_attributes function: {}".format(xcp))
                    pass

            # if attribute does not exist filter it out
            else:
                return False

        return boolean

    #----------------------------------------------#

    def filter_by_path_h5(self, hdf5_path, subpath):

        # boolean is true if the row should be included
        boolean = True

        # only if user introduced some filtering (hdf5)
        if self.filters["path"]["hdf5"]:

            # check hdf5 path exists
            if hdf5_path:

                # get pattern
                pattern = self.filters["path"]["hdf5"]

                # proceed with pattern matching
                re_object = re.compile("{}".format(pattern))

                # if path is found row is included
                if re_object.search(subpath):
                    boolean = True
                else:
                    boolean = False

        return boolean

    #----------------------------------------------#

    def filter_by_path_dir(self, full_path, hdf5_path):

        # boolean is true if the row should be included
        boolean = True

        # only if user introduced some filtering (dir)
        if self.filters["path"]["dir"]:

            # which subpath to use
            subpath = ""
            if hdf5_path:
                subpath = hdf5_path
            elif full_path:
                subpath = full_path

            # get pattern
            pattern = self.filters["path"]["dir"]

            # proceed with pattern matching
            re_object = re.compile("{}".format(pattern))

            # if path is found row is included
            if re_object.search(subpath):
                boolean = True
            else:
                boolean = False

        return boolean

    #----------------------------------------------#

    def add_node_after_filter(self, parent_item, node_path, node_name, type_item, hdf5_path_item, attrs_item, dataset_item, tooltip_str, icon_str, foreground_color):

        # init item
        tree_item = QStandardItem(str(node_name))
        tree_item.setData(node_path, Qt.ItemDataRole.UserRole)
        tree_item.setToolTip(tooltip_str)

        # create items for the header info
        type_item = QStandardItem(type_item)
        hdf5_path_item = QStandardItem(hdf5_path_item)
        attrs_item = QStandardItem(attrs_item)
        dataset_item = QStandardItem(dataset_item)
        icon_str_item = QStandardItem(icon_str)

        # set icon
        tree_item.setIcon(QIcon(qta.icon(icon_str)))

        # foreground for the tree item
        tree_item.setForeground(QBrush(QColor(foreground_color)))

        # set foregrounds
        attrs_item.setForeground(QBrush((Qt.GlobalColor.darkGray)))
        dataset_item.setForeground(QBrush((Qt.GlobalColor.darkGray)))

        # append the row
        parent_item.appendRow([tree_item, type_item, hdf5_path_item, attrs_item, dataset_item, icon_str_item])

        return tree_item

    #----------------------------------------------#

    def add_node(self, parent_item, node_path, node_name):
        """
        This method is used for creating an item that represents either:
          - A directory
          - An HDF5 file
        We do NOT load children right away. Instead, we add a dummy child to handle lazy loading.
        """

        # create the main item
        tree_item = QStandardItem(str(node_name))
        tree_item.setData(node_path, Qt.ItemDataRole.UserRole)
        tree_item.setToolTip(self.create_tooltip([], node_path))

        # create empty items for the header info
        type_item = QStandardItem('')
        hdf5_path_item = QStandardItem('')
        attrs_item = QStandardItem('')
        dataset_item = QStandardItem('')
        icon_str_item = QStandardItem('')

        # if directory
        if os.path.isdir(node_path):
            tree_item.setIcon(QIcon(qta.icon("ei.folder")))
            icon_str_item = QStandardItem("ei.folder")
            type_item = QStandardItem('dir')
            dummy_child = QStandardItem("Loading...")
            tree_item.appendRow([
                dummy_child, QStandardItem(""), QStandardItem(""),
                QStandardItem(""), QStandardItem(""), QStandardItem("")
            ])

        # if single h5 file
        elif self.is_h5_file(node_path):
            tree_item.setIcon(QIcon(qta.icon("ri.database-line")))
            icon_str_item = QStandardItem("ri.database-line")
            type_item = QStandardItem('hdf5')
            hdf5_path_item = QStandardItem(str(node_path))
            dummy_child = QStandardItem("Loading...")
            tree_item.appendRow([
                dummy_child, QStandardItem(""), QStandardItem(""),
                QStandardItem(""), QStandardItem(""), QStandardItem("")
            ])

        # append the row
        parent_item.appendRow([tree_item, type_item, hdf5_path_item, attrs_item, dataset_item, icon_str_item])

        return tree_item

    #----------------------------------------------#

    def add_h5_node(self, parent_item, node, hdf_path, sub_hdf_path = ""):
        """
        Create an item representing a single HDF5 object (Group or Dataset).
        We do NOT load grandchildren. Instead, if it's a group, we add a dummy child.
        """

        # get node path and name
        node_path = node.name
        node_name = node_path.split(os.sep)[-1]
        if not node_name:
            node_name = node_path

        # create full path
        if node_path.startswith(os.sep):
            node_path_formatted = node_path[1:]
        else:
            node_path_formatted = node_path
        full_path = os.path.join(hdf_path, node_path_formatted)

        # init item
        tree_item = QStandardItem(node_name)
        tree_item.setData(full_path, Qt.ItemDataRole.UserRole)
        tree_item.setToolTip(self.create_tooltip(node.attrs, full_path))

        # init type item
        type_item = QStandardItem('hdf5')
        type_item.setForeground(QBrush((Qt.GlobalColor.darkGray)))

        # init h5 path item
        hdf5_path_item = QStandardItem(str(hdf_path))
        hdf5_path_item.setForeground(QBrush((Qt.GlobalColor.darkGray)))

        # create item for the number of attributes
        num_attrs = len(node.attrs)
        if num_attrs > 0:
            attrs_item = QStandardItem(str(num_attrs))
        else:
            attrs_item = QStandardItem('')

        # set foreground
        attrs_item.setForeground(QBrush((Qt.GlobalColor.darkGray)))

        # init
        icon_str_item = QStandardItem('')
        dataset_item = QStandardItem('')

        # if dataset
        if isinstance(node, h5py.Dataset):
            tree_item.setIcon(QIcon(qta.icon("mdi.data-matrix")))
            icon_str_item = QStandardItem("mdi.data-matrix")
            dataset_item = QStandardItem(str(node.shape))

        # if group
        elif isinstance(node, h5py.Group):
            tree_item.setIcon(QIcon(qta.icon("fa5s.layer-group")))
            icon_str_item = QStandardItem("fa5s.layer-group")

            # check if it's a DataFrame-like group
            df_node_boolean, df_node_shape = self.is_df_node(node)
            if df_node_boolean:
                dataset_item = QStandardItem(str(df_node_shape))

            # add a dummy child so the user can expand
            dummy_child = QStandardItem("Loading...")
            tree_item.appendRow([
                dummy_child, QStandardItem(""), QStandardItem(""),
                QStandardItem(""), QStandardItem(""), QStandardItem("")
            ])

        # set foreground
        dataset_item.setForeground(QBrush((Qt.GlobalColor.darkGray)))

        # append the row
        parent_item.appendRow([tree_item, type_item, hdf5_path_item, attrs_item, dataset_item, icon_str_item])

        return tree_item

    #----------------------------------------------#

    def load_dir(self, item, path):

        # get list of files and dirs
        elements = os.listdir(path)

        # sort list
        elements = natsort.natsorted(elements)

        # create nodes for all elements
        for element in elements:
            element_path = os.path.join(path, element)
            if self.only_h5_and_dirs:
                if not (os.path.isdir(element_path) or self.is_h5_file(element_path)):
                    continue
            self.add_node(item, element_path, element)

        return

    #----------------------------------------------#

    def create_progress_bar_for_handle_expanded(self, message, number_of_elements):

        # create the progress bar
        self.progress_dialog_handle_expanded = QProgressDialog(message, None, 0, number_of_elements)
        self.progress_dialog_handle_expanded.setMaximumHeight(300)
        self.progress_dialog_handle_expanded.setMaximumWidth(1000)
        self.progress_dialog_handle_expanded.setMinimumHeight(75)
        self.progress_dialog_handle_expanded.setMinimumWidth(600)
        self.progress_dialog_handle_expanded.setAutoClose(True)
        self.progress_dialog_handle_expanded.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_dialog_handle_expanded.closeEvent = closeEventIgnore
        self.progress_dialog_handle_expanded.setWindowTitle("Progress")
        self.progress_dialog_handle_expanded.setWindowIcon(qta.icon("mdi6.timer-sand"))
        self.progress_dialog_handle_expanded.show()
        self.progress_dialog_handle_expanded.repaint()
        self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        self.progress_dialog_handle_expanded.setValue(0)
        self.progress_dialog_handle_expanded.repaint()
        sleep(0.025)
        self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        sleep(0.025)

    #----------------------------------------------#

    def update_progress_bar_for_handle_expanded(self, i):
        if self.progress_dialog_handle_expanded:
            self.progress_dialog_handle_expanded.setValue(i + 1)
            self.progress_dialog_handle_expanded.repaint()
            self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

    #----------------------------------------------#

    def delete_progress_bar_for_handle_expanded(self):
        if self.progress_dialog_handle_expanded:
            self.progress_dialog_handle_expanded.close()
            del self.progress_dialog_handle_expanded
            self.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

    #----------------------------------------------#

    def handle_expanded(self, index):
        """
        Key method that checks if an item has a single dummy child.
        If so, remove it and load the real children (lazy loading).
        """

        item = self.itemFromIndex(index)
        if not item:
            return

        # we only load children if exactly 1 child = "Loading..."
        if item.rowCount() != 1:
            return

        child_dummy = item.child(0)
        if not child_dummy or child_dummy.text() != "Loading...":
            return

        # remove the dummy row
        item.removeRow(0)

        # grab item type (col=1) and hdf_path (col=2)
        idx_type = index.siblingAtColumn(1)
        idx_hdf5 = index.siblingAtColumn(2)
        item_type = self.itemFromIndex(idx_type).text() # e.g. "dir" or "hdf5"
        path_hdf5 = self.itemFromIndex(idx_hdf5).text() # e.g. "/my/path/file.h5" or ""

        # the "full_path" is what's stored in the first column's UserRole
        # it may be an actual directory path or an HDF5 path with group info
        full_path = item.data(Qt.ItemDataRole.UserRole)

        # -------------------------------------------------
        # 1) DIRECTORY CASE
        # -------------------------------------------------
        if item_type == 'dir':
            if os.path.isdir(full_path):
                elements = os.listdir(full_path)
                elements = natsort.natsorted(elements)

                num_elements = len(elements)
                update_interval = max(1, num_elements // DESIRED_UPDATES_FOR_PROGRESS_BAR)
                self.progress_dialog_handle_expanded = None
                if num_elements >= MIN_N_ELEMENTS_PROGRESS_BAR:
                    self.create_progress_bar_for_handle_expanded("Loading directory children... (N_ELEMENTS = {})".format(num_elements), num_elements)

                for i, elem in enumerate(elements):
                    elem_path = os.path.join(full_path, elem)
                    if self.only_h5_and_dirs:
                        # only show subdirs and h5 files
                        if not (os.path.isdir(elem_path) or self.is_h5_file(elem_path)):
                            continue

                    self.add_node(item, elem_path, elem)

                    if (i % update_interval) == 0:
                        self.update_progress_bar_for_handle_expanded(i)

                self.delete_progress_bar_for_handle_expanded()

        # -------------------------------------------------
        # 2) HDF5 CASE
        # -------------------------------------------------
        elif item_type == 'hdf5':

            # distinguish top-level HDF5 file vs an internal group
            is_top_level_file = False

            # if path_hdf5 == full_path and not empty -> top-level h5
            if path_hdf5 == full_path and path_hdf5 != "":
                is_top_level_file = True
            elif path_hdf5 == "" and self.is_h5_file(full_path):
                # another scenario: we stored the h5 path in full_path
                is_top_level_file = True

            # -------------------------------
            # 2a) TOP-LEVEL HDF5 FILE
            # -------------------------------
            if is_top_level_file:
                actual_h5_file = path_hdf5 if path_hdf5 else full_path
                xcp = self.open_h5_file(actual_h5_file)
                if xcp:
                    self.item_has_to_be_red(item, xcp)
                    self.show_red_error_message()
                    self.parent.treeView.selectionModel().clearSelection()
                    self.parent.treeView.setCurrentIndex(QModelIndex())
                    return
                root_group = self.parent.hdf_dict[actual_h5_file]
                if root_group:
                    # we'll gather the immediate children of the root group
                    child_keys = root_group.keys()
                    num_keys = len(child_keys)
                    update_interval = max(1, num_keys // DESIRED_UPDATES_FOR_PROGRESS_BAR)

                    self.progress_dialog_handle_expanded = None
                    if num_keys >= MIN_N_ELEMENTS_PROGRESS_BAR:
                        self.create_progress_bar_for_handle_expanded("Loading HDF5 root group in {} (N_ELEMENTS = {})".format(os.path.basename(actual_h5_file), num_keys), num_keys)

                    for i, name in enumerate(natsort.natsorted(child_keys)):
                        child_node = root_group[name]
                        self.add_h5_node(item, child_node, hdf_path=actual_h5_file)

                        if (i % update_interval) == 0:
                            self.update_progress_bar_for_handle_expanded(i)

                    self.delete_progress_bar_for_handle_expanded()

                return

            # -------------------------------
            # 2b) GROUP/ DATASET INSIDE h5
            # -------------------------------
            if path_hdf5 and path_hdf5 != full_path:
                # sub_path is "GroupName/..." relative to the file
                sub_path = os.path.relpath(full_path, path_hdf5)
                hdf_file_obj = self.parent.hdf_dict.get(path_hdf5, None)
                if hdf_file_obj:
                    node = hdf_file_obj.get(sub_path, None)
                    if node and isinstance(node, h5py.Group):
                        # load immediate children
                        child_keys = node.keys()
                        num_keys = len(child_keys)
                        update_interval = max(1, num_keys // DESIRED_UPDATES_FOR_PROGRESS_BAR)

                        self.progress_dialog_handle_expanded = None
                        if num_keys >= MIN_N_ELEMENTS_PROGRESS_BAR:
                            self.create_progress_bar_for_handle_expanded("Loading HDF5 group {} in {} (N_ELEMENTS = {})".format(node.name, os.path.basename(path_hdf5), num_keys), num_keys)

                        for i, name in enumerate(natsort.natsorted(child_keys)):
                            child_node = node[name]
                            self.add_h5_node(item, child_node, hdf_path=path_hdf5)

                            if (i % update_interval) == 0:
                                self.update_progress_bar_for_handle_expanded(i)

                        self.delete_progress_bar_for_handle_expanded()

        # item_type == 'other' or something else
        else:
            pass

        return

    #----------------------------------------------#

    def error_message_wrong_h5_file(self, xcp):

        # show error message
        message_title = "Error"
        message_text = ("{}".format(xcp))
        message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self.parent.global_parent)
        message_box.setWindowIcon(QIcon(self.parent.global_parent.window_icon_path))
        message_box.exec_()

        return

    #----------------------------------------------#

    def item_has_to_be_red(self, item, error_message):

        # item error
        item.setForeground(QBrush((Qt.GlobalColor.red)))
        item.setToolTip(str(error_message))

        return

    #----------------------------------------------#

    def show_red_error_message(self):

        # show message
        message_title = "Error"
        message_text = "The file cannot be opened because it is probably corrupted."
        message_box = QMessageBox(QMessageBox.Icon.Critical, message_title, message_text, parent=self.parent.global_parent)
        message_box.setWindowIcon(QIcon(self.parent.global_parent.window_icon_path))
        message_box.exec_()

        return

    #----------------------------------------------#

    def handle_collapsed(self, index, disabled = True):

        # disable this function
        if disabled:
            return

        # get item from index
        item = self.itemFromIndex(index)

        # is it hdf5 or dir?
        type = self.get_type_from_index(index)

        return

    #----------------------------------------------#

    def get_type_from_index(self, index):

        # first column index
        idx_col = index.siblingAtColumn(1)
        item_col = self.itemFromIndex(idx_col)
        type = str(item_col.data(Qt.ItemDataRole.DisplayRole))

        return type

    #----------------------------------------------#

    def get_hdf5_path_from_index(self, index):

        # second column index
        idx_col = index.siblingAtColumn(2)
        item_col = self.itemFromIndex(idx_col)
        type = str(item_col.data(Qt.ItemDataRole.DisplayRole))

        return type

    #----------------------------------------------#

    def open_h5_file(self, path):

        # open and store hdf
        try:
            self.parent.hdf_dict[path] = h5py.File(path, "r")
        except Exception as xcp:
            print("Exception at {} for path {}: {}".format("open_h5_file", path, xcp))
            self.parent.hdf_dict[path] = None
            return xcp

        return None

    #----------------------------------------------#

    def is_df_node(self, node):

        # init variables
        boolean = False
        shape = None

        # data type should be DataFrame and node should be Group
        if isinstance(node, h5py.Group):
            if "data_type" in node.attrs.keys():
                if fromBytesToString(node.attrs["data_type"]) == "DataFrame":
                    boolean = True
                    if "data" in node.keys():
                        child = node["data"]
                        if isinstance(child, h5py.Dataset):
                            shape = child.shape

        return boolean, shape

    #----------------------------------------------#

    def is_h5_file(self, path):

        # init boolean
        boolean = False

        # try to check the extension
        try:
            xt = path.split(".")[-1]
            if xt == "hdf" or xt == "h5" or xt == "hdf5" or xt == "h5part":
                boolean = True
        except Exception as xcp:
            pass

        return boolean

    #----------------------------------------------#

    def create_tooltip(self, node_attrs, node_path):

        # init html
        tooltip = "<html>"
        tooltip += '<table>'

        # title for the path
        tooltip += '<tr>'
        tooltip += '<td><b>Path</b></td>'
        tooltip += '</tr>'

        # set path
        tooltip += '<tr>'
        tooltip += '<td>{}</td>'.format(node_path)
        tooltip += '</tr>'

        # title for the attributes
        tooltip += '<tr>'
        tooltip += '<td><b>Attributes</b></td>'
        tooltip += '</tr>'

        # define width of the tooltip
        if "TIMESTAMP" in node_attrs:
            width = 600
        else:
            width = 400

        # iterate over attributes
        if len(node_attrs) > 0:
            for at in node_attrs:
                tooltip += '<tr>'
                tooltip += '<td width="{}">{} = {}</td>'.format(width, at, fromBytesToString(node_attrs[at]))
                tooltip += '</tr>'
        else:
            tooltip += '<tr>'
            tooltip += '<td width="{}">No attributes found</td>'.format(width)
            tooltip += '</tr>'

        # end html
        tooltip += '</table>'
        tooltip += '</html>'

        return tooltip

    #----------------------------------------------#

#################################################################
#################################################################