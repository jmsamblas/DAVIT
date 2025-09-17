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

class WaitingWidgetNXCALS(QDialog):

    #----------------------------------------------#

    def __init__(self, app, app_root_path = None, window_icon_path = None, parent = None):

        # inherit from QWidget
        QDialog.__init__(self)

        # main attributes
        self.app = app
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.parent = parent

        # own attributes
        self.can_be_closed = False

        # set title and icon
        self.setWindowTitle("Progress Dialog")
        if self.window_icon_path:
            self.setWindowIcon(QIcon(self.window_icon_path))
        else:
            self.setWindowIcon(qta.icon("mdi.timer-sand"))

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "waiting_widget_nxcals.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # size of the widget
        self.setMinimumSize(520, 140)
        self.setMaximumSize(520, 140)

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # layout of the form
        self.verticalLayout_frame_holder = QVBoxLayout(self)
        self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
        self.verticalLayout_frame_holder.setContentsMargins(15, 25, 15, 15)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_holder.setObjectName("frame_holder")
        self.verticalLayout_frame_holder.addWidget(self.frame_holder)

        # main layout
        self.verticalLayout_stack = QVBoxLayout(self.frame_holder)
        self.verticalLayout_stack.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_stack.setSpacing(20)
        self.verticalLayout_stack.setObjectName("verticalLayout_stack")

        # set font
        font = QFont()
        font.setBold(True)
        font.setWeight(75)

        # info label
        self.label_info = QLabel(self.frame_holder)
        self.label_info.setFont(font)
        self.label_info.setObjectName("label_info")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_info.setWordWrap(True)
        self.label_info.setText("Setting up the pytimber session. Please, wait until the session is initialized...")
        self.verticalLayout_stack.addWidget(self.label_info)

        # bottom frame
        self.frame_bottom = QFrame(self.frame_holder)
        self.frame_bottom.setObjectName("frame_bottom")
        self.verticalLayout_stack.addWidget(self.frame_bottom)

        # bottom layout
        self.horizontalLayout_frame_bottom = QHBoxLayout(self.frame_bottom)
        self.verticalLayout_stack.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_stack.setSpacing(10)
        self.horizontalLayout_frame_bottom.setObjectName("horizontalLayout_frame_bottom")

        # spacer 1
        self.spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_bottom.addItem(self.spacer_item)

        # loading gif
        self.movie = QMovie(os.path.join(self.app_root_path, "resources", "icons", "loading_32.gif"))
        self.label_animation = QLabel(self.frame_holder)
        self.label_animation.setMaximumSize(32,32)
        self.label_animation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_animation.setMovie(self.movie)
        self.movie.start()
        self.horizontalLayout_frame_bottom.addWidget(self.label_animation)

        # main label
        self.label = QLabel(self.frame_holder)
        self.label.setObjectName("label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setText("")
        self.horizontalLayout_frame_bottom.addWidget(self.label)

        # spacer 2
        self.spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_bottom.addItem(self.spacer_item)

        return

    #----------------------------------------------#

    def updateLabel(self, txt):

        # update waiting widget
        self.parent.global_parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        self.repaint()
        self.label.setText(str(txt))

        return

    #----------------------------------------------#

    def reject(self):

        # wait for logging to finish
        if self.can_be_closed:
            super().reject()

        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # wait for logging to finish
        if self.can_be_closed:
            super().closeEvent(evt)
        else:
            evt.ignore()

        return

    #----------------------------------------------#

#################################################################
#################################################################