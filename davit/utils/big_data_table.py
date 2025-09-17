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

class BigDataFrameModel(QAbstractTableModel):

    def __init__(self, df: pd.DataFrame = None, parent=None):
        super(BigDataFrameModel, self).__init__(parent)
        if df is None:
            df = pd.DataFrame()
        self._data = df

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._data.columns[section])
        else:
            return str(self._data.index[section])

#################################################################
#################################################################

class BigDataTableView(QTableView):

    def __init__(self, df: pd.DataFrame, chunk_size: int = 100_000, parent = None):
        super(BigDataTableView, self).__init__(parent)
        if not chunk_size:
            chunk_size = 100000
        self.parent = parent
        self.chunk_size = chunk_size
        self.loaded_rows = 0
        self.df = df
        self.load_initial_data(self.chunk_size)
        self.typical_attrs()
        self.init_hack_timer()

    def init_hack_timer(self):
        self.hack_timer = QTimer(self)
        self.hack_timer.timeout.connect(self.resize_columns_custom)
        self.hack_timer.setSingleShot(True)
        self.hack_timer.start(30)

    def typical_attrs(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setDragEnabled(False)
        self.setAlternatingRowColors(False)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setFixedHeight(30)
        self.verticalHeader().setHighlightSections(False)
        self.verticalHeader().setMinimumSectionSize(25)
        self.verticalHeader().setVisible(True)
        self.verticalHeader().setDefaultSectionSize(25)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def load_initial_data(self, chunk_size):
        chunk = self.df.iloc[:chunk_size, :]
        model = BigDataFrameModel(chunk)
        self.setModel(model)
        self.loaded_rows = chunk_size

    def load_more_data(self):
        if self.loaded_rows < len(self.df):
            new_rows = min(self.loaded_rows + self.chunk_size, len(self.df))
            chunk = self.df.iloc[self.loaded_rows:new_rows, :]
            model = self.model()
            model._data = pd.concat([model._data, chunk])
            self.loaded_rows = new_rows
            model.layoutChanged.emit()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_End:
            self.load_initial_data(self.df.shape[0])
            self.scrollToBottom()
        elif event.key() == Qt.Key.Key_Home:
            self.scrollToTop()
        elif event.key() == Qt.Key.Key_PageUp:
            self.scroll_by_chunk(-1)
        elif event.key() == Qt.Key.Key_PageDown:
            self.scroll_by_chunk(1)
        else:
            super().keyPressEvent(event)

    def scrollContentsBy(self, dx, dy):
        if dy != 0 and self.loaded_rows < len(self.df):
            scrollbar = self.verticalScrollBar()
            if scrollbar.value() == scrollbar.maximum():
                self.load_more_data()
        super(BigDataTableView, self).scrollContentsBy(dx, dy)

    def scroll_by_chunk(self, direction: int):
        scrollbar = self.verticalScrollBar()
        current_value = scrollbar.value()
        new_value = current_value + direction * self.chunk_size
        new_value = max(0, min(new_value, scrollbar.maximum()))
        if direction > 0 and new_value == scrollbar.maximum():
            self.load_more_data()
        scrollbar.setValue(new_value)
        row = int(new_value)
        column = self.currentIndex().column()
        index = self.model().index(row, column)
        self.setCurrentIndex(index)
        self.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)

    def init_headers(self, df):
        self.header_labels = df.columns.tolist()
        self.header_labels = [str(i) for i in self.header_labels]
        self.header_labels_widths = [getPixelWidthFromQLabel(i, offset=20) for i in self.header_labels]

    def resize_columns_custom(self):
        if self.hack_timer:
            self.hack_timer.stop()
            del self.hack_timer
        if self.df.empty:
            self.horizontalHeader().setVisible(False)
        else:
            self.horizontalHeader().setVisible(True)
        self.init_headers(self.df)
        self.resize_offsets = [35]
        if self.header_labels:
            length_headers = len(self.header_labels)
            minimum_width = int((self.parent.frameGeometry().width() - self.verticalHeader().width() - self.resize_offsets[0]) / length_headers)
            for c in range(0, len(self.header_labels)):
                if self.header_labels_widths[c] > minimum_width:
                    width_to_set = self.header_labels_widths[c]
                else:
                    width_to_set = minimum_width
                self.setColumnWidth(c, width_to_set)

        return

#################################################################
#################################################################

def getPixelWidthFromQLabel(string, offset=30):
    w = QLabel(string).fontMetrics().boundingRect(QLabel(string).text()).width() + offset
    return w

#################################################################
#################################################################