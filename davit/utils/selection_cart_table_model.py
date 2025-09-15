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

class SelectionCartTableModel(QAbstractTableModel):

    #----------------------------------------------#

    def __init__(self, data, header_labels, result_table = False, number_of_metadata_columns = 3):

        super(SelectionCartTableModel, self).__init__()
        self._data = data
        self._header_labels = header_labels
        self._result_table = result_table
        self._number_of_metadata_columns = number_of_metadata_columns

        return

    #----------------------------------------------#

    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header_labels[section]
            elif orientation == Qt.Vertical:
                return str(section)

    #----------------------------------------------#

    def data(self, index, role):

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            if not self._result_table:
                if self._header_labels[col] == "Options":
                    return None
                else:
                    return self._data[row][col]
            else:
                return self._data[row][col]

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        elif role == Qt.BackgroundRole:
            if self._result_table:
                if self._data[row][col] == "":
                    return QBrush(QColor("#FFD0D0"))
                else:
                    return QBrush(QColor("#CBFFCE"))

        return

    #----------------------------------------------#

    def update_data(self, row, col, value):
        self._data[row][col] = value
        changed_index = self.index(row, col)
        self.dataChanged.emit(changed_index, changed_index)

    #----------------------------------------------#

    def remove_row(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        self._data.pop(row)
        self.endRemoveRows()

    #----------------------------------------------#

    def add_row(self, new_row):
        row_position = self.rowCount(QModelIndex())
        self.beginInsertRows(QModelIndex(), row_position, row_position)
        self._data.append(new_row)
        self.endInsertRows()

    #----------------------------------------------#

    def flags(self, index):
        col = index.column()
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    #----------------------------------------------#

    def rowCount(self, index):
        return len(self._data)

    #----------------------------------------------#

    def columnCount(self, index):
        return len(self._data[0])

    #----------------------------------------------#

#################################################################
#################################################################