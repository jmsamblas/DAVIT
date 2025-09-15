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

class ComboDelegate(QStyledItemDelegate):

    #----------------------------------------------#

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hash = {}

    #----------------------------------------------#

    def setHash(self, hash):
        self.hash = hash

    #----------------------------------------------#

    def paint(self, painter, option, index):
        if not index.isValid():
            return
        opt = option
        opt.text = self.hash.get(index.row(), "")
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, opt, painter)
        return

    #----------------------------------------------#

#################################################################
#################################################################