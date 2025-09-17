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

class NXCALSThreadsPanelTableModel(QAbstractTableModel):

    #----------------------------------------------#

    def __init__(self, data, header_labels):

        super(NXCALSThreadsPanelTableModel, self).__init__()
        self._data = data
        self._header_labels = header_labels

        return

    #----------------------------------------------#

    def headerData(self, section, orientation, role):

        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._header_labels[section]

    #----------------------------------------------#

    def data(self, index, role):

        row = index.row()
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[row][col]

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        return

    #----------------------------------------------#

    def rowCount(self, index):

        return len(self._data)

    #----------------------------------------------#

    def columnCount(self, index):

        return len(self._data[0])

    #----------------------------------------------#

#################################################################
#################################################################