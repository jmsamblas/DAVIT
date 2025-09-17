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

class CustomMultiPlotItemSample(pg.graphicsItems.LegendItem.ItemSample):

    #----------------------------------------------#

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.additional_linked_items = []
        self.items_dict = {}
        self.name = ""
        self.legend_item = None

        return

    #----------------------------------------------#

    def setVisibleState(self):

        # get state
        visibility_state = self.items_dict[self.name]["visible"]

        # set state for the main item
        self.item.setVisible(visibility_state)

        # set state for other items
        if self.additional_linked_items:
            for it in self.additional_linked_items:
                it.setVisible(visibility_state)

        return

    #----------------------------------------------#

    def mouseClickEvent(self, event):

        # check for modifiers
        booleanControlModifier = False
        if event.modifiers():
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                booleanControlModifier = True

        # make sure the click is with left button
        if event.button() == Qt.MouseButton.LeftButton:

            # normal cases
            if not booleanControlModifier:

                # set invisible for the main item
                visible = self.item.isVisible()
                self.item.setVisible(not visible)
                self.items_dict[self.name]["visible"] = not visible

                # set invisible for all the other items
                if self.additional_linked_items:
                    for it in self.additional_linked_items:
                        visible = it.isVisible()
                        it.setVisible(not visible)

            # cases where Ctrl is pressed
            else:

                # boolean for the case B
                theItemBeingShownIsTheOnlyOneBeingShown = False
                n_items_shown = 0
                if self.item.isVisible() == True:
                    for name in self.items_dict.keys():
                        item_tuple = self.items_dict[name]["items"]
                        it = item_tuple[0]
                        if it.isVisible() == True:
                            n_items_shown += 1
                        if n_items_shown > 1:
                            theItemBeingShownIsTheOnlyOneBeingShown = False
                            break
                    if n_items_shown == 1:
                        theItemBeingShownIsTheOnlyOneBeingShown = True

                # case A: mute all minus one
                if not theItemBeingShownIsTheOnlyOneBeingShown:

                    # set invisible for all items except for the current selected
                    if self.items_dict:
                        for name in self.items_dict.keys():
                            item_tuple = self.items_dict[name]["items"]
                            for it in item_tuple:
                                if it == self.item or it in self.additional_linked_items:
                                    it.setVisible(True)
                                    self.items_dict[name]["visible"] = True
                                else:
                                    it.setVisible(False)
                                    self.items_dict[name]["visible"] = False

                # case B: unmute all
                else:

                    # set visible for all
                    if self.items_dict:
                        for name in self.items_dict.keys():
                            item_tuple = self.items_dict[name]["items"]
                            for it in item_tuple:
                                it.setVisible(True)
                                self.items_dict[name]["visible"] = True

        # update the view (the muted icon) of the selected item
        event.accept()
        self.update()

        # this is essential so that the other items (the muted icon) also get properly updated
        if self.legend_item and booleanControlModifier:
            self.legend_item.updateAllItemViews()

        return

    #----------------------------------------------#

#################################################################
#################################################################

class CustomMultiPlotLegendItem(pg.LegendItem):

    #----------------------------------------------#

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setSampleType(CustomMultiPlotItemSample)

        return

    #----------------------------------------------#

    def addAllItems(self, items_dict):

        self.items_dict = items_dict

        return

    #----------------------------------------------#

    def setVisibilityStateForAllItems(self):

        for it in self.items:
            sample = it[0]
            sample.setVisibleState()
            sample.update()

        return

    #----------------------------------------------#

    def addItem(self, item, name, additional_linked_items=[]):

        if "Ø" in name:
            label = pg.LabelItem(name, color='r', justify='left', size=self.opts['labelTextSize'])
        else:
            label = pg.LabelItem(name, color=self.opts['labelTextColor'], justify='left', size=self.opts['labelTextSize'])

        if isinstance(item, self.sampleType):
            sample = item
        else:
            sample = self.sampleType(item)
            sample.additional_linked_items = additional_linked_items
            sample.items_dict = self.items_dict
            sample.name = name
            sample.legend_item = self

        self.items.append((sample, label))
        self._addItemToLayout(sample, label)
        self.updateSize()

        return

    def updateAllItemViews(self):

        for it in self.items:
            sample = it[0]
            sample.update()

        return

    #----------------------------------------------#

#################################################################
#################################################################

class QVSeparationLine(QFrame):

    #----------------------------------------------#

    def __init__(self):

        super().__init__()
        self.setFixedWidth(20)
        self.setMinimumHeight(1)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        return

    #----------------------------------------------#

class QHSeparationLine(QFrame):

    #----------------------------------------------#

    def __init__(self):

        super().__init__()
        self.setMinimumWidth(1)
        self.setFixedHeight(20)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        return

    #----------------------------------------------#

#################################################################
#################################################################

class QComboBoxNoScrollWheel(QComboBox):

    #----------------------------------------------#

    def __init__(self, scrollWidget=None, *args, **kwargs):

        super(QComboBoxNoScrollWheel, self).__init__(*args, **kwargs)
        self.scrollWidget = scrollWidget
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    #----------------------------------------------#

    def wheelEvent(self, *args, **kwargs):

        if self.hasFocus():
            return QComboBox.wheelEvent(self, *args, **kwargs)
        else:
            return self.scrollWidget.wheelEvent(*args, **kwargs)

    #----------------------------------------------#

#################################################################
#################################################################

class ScrollLabel(QScrollArea):

    #----------------------------------------------#

	def __init__(self, *args, **kwargs):

		QScrollArea.__init__(self, *args, **kwargs)
		self.setWidgetResizable(True)
		content = QWidget(self)
		self.setWidget(content)
		lay = QVBoxLayout(content)
		self.label = QLabel(content)
		self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
		self.label.setWordWrap(True)
		lay.addWidget(self.label)

    #----------------------------------------------#

	def setText(self, text):
		self.label.setText(text)

    #----------------------------------------------#

#################################################################
#################################################################

class CustomCornerWidget(QWidget):

    #----------------------------------------------#

    class CustomTransposePushButton(QPushButton):

        #----------------------------------------------#

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.label = QLabel(self)
            self.label.setText("A<sup>T</sup>")
            self.label.setStyleSheet("background-color:transparent;")
            self.label.setContentsMargins(11, 1, 11, 1)
            self.setDefault(False)
            self.setAutoDefault(False)
            self.setFlat(True)
            self.setStyleSheet("""
                QPushButton {
                    border: none;
                    color: #000;
                    padding: 3px;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #fff;
                    background: #3498db;
                }
            """)
            layout = QHBoxLayout(self)
            layout.addWidget(self.label)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            self.setLayout(layout)

        #----------------------------------------------#

        def mousePressEvent(self, event):
            super().mousePressEvent(event)
            self.clicked.emit()

        #----------------------------------------------#

        def mouseReleaseEvent(self, event):
            super().mouseReleaseEvent(event)

    #----------------------------------------------#

    def __init__(self, name, shape_x, shape_y, auto_transpose=False, *args, **kwargs):
        super(CustomCornerWidget, self).__init__(*args, **kwargs)
        self.transpose_button = self.CustomTransposePushButton(parent=self)
        self.update_transpose_button_style(auto_transpose)
        self.label_name = QLabel(parent=self, text=f"{name}")
        self.label_name.setStyleSheet("""
                    color: gray;
                    font-weight: normal;
                """)
        self.label_shape = QLabel(parent=self, text=f"({shape_x}, {shape_y})")
        self.label_shape.setStyleSheet("""
            color: gray;
            font-weight: normal;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self.label_name)
        layout.addWidget(self.label_shape)
        layout.addWidget(self.transpose_button)
        self.setLayout(layout)

    #----------------------------------------------#

    @property
    def clicked(self):
        return self.transpose_button.clicked

    #----------------------------------------------#

    def update_transpose_button_style(self, auto_transpose_enabled, ENABLE_COLORED_BUTTON = False):
        if ENABLE_COLORED_BUTTON:
            if auto_transpose_enabled:
                self.transpose_button.setStyleSheet("""
                    QPushButton {
                        border: none;
                        color: #000;
                        padding: 3px;
                        background-color: #33cc66;
                    }
                    QPushButton:hover {
                        color: #fff;
                        background-color: #3498db;
                    }
                """)
            else:
                self.transpose_button.setStyleSheet("""
                    QPushButton {
                        border: none;
                        color: #000;
                        padding: 3px;
                        background: transparent;
                    }
                    QPushButton:hover {
                        color: #fff;
                        background: #3498db;
                    }
                """)

    #----------------------------------------------#

#################################################################
#################################################################