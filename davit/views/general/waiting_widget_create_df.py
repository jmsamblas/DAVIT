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

class WaitingWidgetCreateDf(QDialog):

    #----------------------------------------------#

    def __init__(self, app, app_root_path = None, window_icon_path = None, parent = None, memory_in_mb = 0):

        # inherit from QWidget
        QDialog.__init__(self)

        # main attributes
        self.app = app
        self.app_root_path = app_root_path
        self.window_icon_path = window_icon_path
        self.parent = parent
        self.memory_in_mb = memory_in_mb

        # own attributes
        self.counter = 0

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
        with open(os.path.join(self.app_root_path, "resources", "qss", "waiting_widget.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # size of the widget
        self.setMinimumSize(600, 140)
        self.setMaximumSize(600, 140)

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
        self.label_info.setText("Loading the data into pandas. Please, wait until this dialog automatically closes.")
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
        if isinstance(self.memory_in_mb, str):
            self.label.setText("Estimated memory size needed to allocate the dataframe: {} MB".format(self.memory_in_mb))
        else:
            self.label.setText("Estimated memory size needed to allocate the dataframe: {:.2f} MB".format(self.memory_in_mb))
        self.horizontalLayout_frame_bottom.addWidget(self.label)

        # spacer 2
        self.spacer_item = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_frame_bottom.addItem(self.spacer_item)

        return

    #----------------------------------------------#

    def updateLabel(self):

        # update counter
        self.counter = self.counter + 1

        # update waiting widget
        if self.parent:
            if self.counter % 10 == 0:
                self.repaint()
                self.parent.app.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
                self.label.setText(" Number of analyzed items: {}".format(self.counter))

        return

    #----------------------------------------------#

    def bindWidgets(self):

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################