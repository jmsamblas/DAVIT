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

class NXCALSTreeViewModel(QStandardItemModel):

    #----------------------------------------------#

    def __init__(self, header_labels = ['Query', 'TS1', 'TS2', 'Elapsed Time', 'Shape'], parent = None, global_parent = None):

        # inheritance
        super().__init__()

        # attributes
        self.header_labels = header_labels
        self.parent = parent
        self.global_parent = global_parent

        # init shape column
        self.shape_column = self.header_labels.index('Shape')

        # init properties
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(len(self.header_labels))
        self.setHorizontalHeaderLabels(self.header_labels)

        return

    #----------------------------------------------#

    def data(self, index, role=Qt.DisplayRole):

        # only intercept display role for Shape column
        if role == Qt.DisplayRole and index.column() == self.shape_column:

            # detect top-level items (invisible root's direct children)
            is_top_level = not index.parent().isValid()

            # retrieve the corresponding tree item (col 0)
            tree_item = self.itemFromIndex(index.siblingAtColumn(0))

            # if has children, show count
            if tree_item.hasChildren():
                count = tree_item.rowCount()
                return f"{count} item{'s' if count != 1 else ''}"

            # leaf node: if top-level and no children, show empty
            if is_top_level:
                return ""

            # otherwise, display numpy array shape (e.g., "(0,)" for empty arrays)
            arr = tree_item.data(Qt.UserRole)
            shape = getattr(arr, 'shape', ())
            return str(shape)

        return super().data(index, role)

    #----------------------------------------------#

    def add_query(self, query, ts1, ts2, elapsed_time):

        # add the root for that query
        root_query = self.add_node(self, node_name = "{}".format(query), node_data = np.array([]), qta_icon_str = "ei.search-alt", ts1 = ts1, ts2 = ts2, elapsed_time = elapsed_time)

        return root_query

    #----------------------------------------------#

    def update_query(self, item, elapsed_time):

        # update elapsed time
        index = self.indexFromItem(item)
        column_index = index.siblingAtColumn(3)
        self.setData(column_index, elapsed_time)

        return

    #----------------------------------------------#

    def add_results_to_query(self, root_query, query, response_dict, error):

        # change elapsed time
        self.update_query(root_query, elapsed_time = "DONE")

        # change color first
        index = self.indexFromItem(root_query)
        for col in range(0, self.columnCount()):
            item = self.itemFromIndex(index.siblingAtColumn(col))
            if error:
                item.setBackground(QBrush(QColor("#E8A2A2")))
                item.setToolTip("Error: {}".format(error))
            else:
                if response_dict:
                    item.setBackground(QBrush(QColor("#95EA71")))
                else:
                    item.setBackground(QBrush(QColor("#ffdf80")))
                    item.setToolTip("Query has finished and is empty!")

        # add the other nodes
        for key in response_dict.keys():
            self.build_key_tree(key, root_query, response_dict)

        return

    #----------------------------------------------#

    def build_key_tree(self, key, root, response_dict):

        # add the node for that key
        node = self.add_node(root, node_name = str(key), node_data = np.array([]), qta_icon_str = "mdi.focus-field")

        # iterate over acq timestamps
        for counter_ts, acq_timestamp in enumerate(response_dict[key][0]):

            # get ts in readable way
            formatted_ts = datetime.fromtimestamp(acq_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

            # get node_data
            node_data = response_dict[key][1][counter_ts]

            # convert to array if it is an scalar
            if node_data.ndim == 0:
                node_data = np.array([node_data])

            # add the node for the corresponding acq stamp
            self.add_node(node, node_name = formatted_ts, node_data = node_data, qta_icon_str = "mdi.data-matrix")

        return

    #----------------------------------------------#

    def add_node(self, parent_item, node_name, node_data, qta_icon_str, ts1 = "", ts2 = "", elapsed_time = ""):

        # init item
        tree_item = QStandardItem(str(node_name))
        tree_item.setData(node_data, Qt.UserRole)

        # create empty items for the query info
        ts1_item = QStandardItem(ts1)
        ts2_item = QStandardItem(ts2)
        elapsed_time_item = QStandardItem(elapsed_time)

        # create shape item
        if node_data.size > 0:
            shape_item = QStandardItem("{}".format(node_data.shape))
        else:
            shape_item = QStandardItem("")

        # set icons
        tree_item.setIcon(QIcon(qta.icon(qta_icon_str)))

        # set foregrounds
        ts1_item.setForeground(QBrush((Qt.darkGray)))
        ts2_item.setForeground(QBrush((Qt.darkGray)))
        elapsed_time_item.setForeground(QBrush((Qt.darkGray)))
        shape_item.setForeground(QBrush((Qt.darkGray)))

        # append the row
        parent_item.appendRow([tree_item, ts1_item, ts2_item, elapsed_time_item, shape_item])

        return tree_item

    #----------------------------------------------#

    def handle_expanded(self, index):

        # background colors back to normal
        for col in range(0, self.columnCount()):
            item = self.itemFromIndex(index.siblingAtColumn(col))
            item.setBackground(QBrush(QColor("#ffffff")))

        return

    #----------------------------------------------#

#################################################################
#################################################################