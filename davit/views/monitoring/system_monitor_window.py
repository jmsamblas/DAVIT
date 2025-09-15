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

# GLOBALS

BACKGROUND_COLOR = "#d9d9d9"
CURVE_COLOR = "#808080"
MAX_N_POINTS = 60

#################################################################
#################################################################

class MemoryPlotWidget(pg.PlotWidget):

    #----------------------------------------------#

    def __init__(self, parent, max_data_points = MAX_N_POINTS):

        # inheritance
        super().__init__(parent=parent, background=BACKGROUND_COLOR)

        # attributes
        self.parent = parent
        self.max_data_points = max_data_points

        # own attributes
        self.memory_data = []
        self.time_data = []
        self.time_counter = 0

        # set up the plot
        self.setTitle("Memory Monitoring")
        self.setLabel("left", "Memory Usage (%)")
        self.setLabel("bottom", "Time (s)")

        # customize plot colors and style
        self.getAxis('left').setTextPen('k')
        self.getAxis('bottom').setTextPen('k')
        self.showGrid(x=False, y=False, alpha=0.5)

        # create the plot curve with a black-grey color
        self.memory_curve = self.plot(pen=pg.mkPen(color=CURVE_COLOR, width=2))

        # init variables
        self.memory_data = [0] * (self.max_data_points+1)
        self.time_data = np.arange(-1*self.max_data_points, 1)

        # plot empty data
        self.memory_curve.setData(self.time_data, self.memory_data)

        # set the Y-axis range from 0% to 100%
        self.setYRange(-10, 110)

        return

    #----------------------------------------------#

    def update_memory_usage(self, limit_x_range = True):

        # get the percentage of memory used from psutil
        percent_used_memory = psutil.virtual_memory().percent

        # normal procedure
        if limit_x_range:

            # update just the memory data
            self.memory_data = self.memory_data[1:] + [percent_used_memory]

        # deprecated case
        else:

            # update the time and memory data lists
            self.time_counter += 1
            self.time_data.append(self.time_counter)
            self.memory_data.append(percent_used_memory)

            # limit the lists to the last max_data_points values
            if len(self.time_data) > self.max_data_points:
                self.time_data.pop(0)
                self.memory_data.pop(0)

        # update the plot data
        self.memory_curve.setData(self.time_data, self.memory_data)

        # set the Y-axis range from 0% to 100%
        self.setYRange(-10, 110)

        # set the X-axis range to display between 0 and max_data_points
        self.setXRange(-1 * self.max_data_points, 1)

        return

    #----------------------------------------------#

#################################################################
#################################################################

class CPUMonitorWidget(pg.PlotWidget):

    #----------------------------------------------#

    def __init__(self, parent, max_data_points = MAX_N_POINTS):

        # inheritance
        super().__init__(parent=parent, background=BACKGROUND_COLOR)

        # attributes
        self.parent = parent
        self.max_data_points = max_data_points

        # own attributes
        self.cpu_data = []
        self.time_data = []
        self.time_counter = 0

        # set up the plot
        self.setTitle("CPU Monitoring")
        self.setLabel("left", "CPU Usage (%)")
        self.setLabel("bottom", "Time (s)")

        # customize plot colors and style
        self.getAxis('left').setTextPen('k')
        self.getAxis('bottom').setTextPen('k')
        self.showGrid(x=False, y=False, alpha=0.5)

        # create the plot curve with a black-grey color
        self.cpu_curve = self.plot(pen=pg.mkPen(color=CURVE_COLOR, width=2))

        # init variables
        self.cpu_data = [0] * (self.max_data_points+1)
        self.time_data = np.arange(-1*self.max_data_points, 1)

        # plot empty data
        self.cpu_curve.setData(self.time_data, self.cpu_data)

        # set the Y-axis range from 0% to 100%
        self.setYRange(-10, 110)

        return

    #----------------------------------------------#

    def update_cpu_usage(self, cpu_usage_percent, limit_x_range=True):

        # normal procedure
        if limit_x_range:

            # update just the cpu data
            self.cpu_data = self.cpu_data[1:] + [cpu_usage_percent]

        # deprecated case
        else:

            # update the time and memory data lists
            self.time_counter += 1
            self.time_data.append(self.time_counter)
            self.cpu_data.append(cpu_usage_percent)

            # limit the lists to the last max_data_points values
            if len(self.time_data) > self.max_data_points:
                self.time_data.pop(0)
                self.cpu_data.pop(0)

        # update the plot data
        self.cpu_curve.setData(self.time_data, self.cpu_data)

        # set the Y-axis range from 0% to 100%
        self.setYRange(-10, 110)

        # set the X-axis range to display between 0 and max_data_points
        self.setXRange(-1*self.max_data_points, 1)

        return

    #----------------------------------------------#

#################################################################
#################################################################

class SystemInfoWidget(QFrame):

    #----------------------------------------------#

    def __init__(self, parent):

        # inheritance
        super().__init__(parent=parent)

        # init layout
        self.layout = QGridLayout(self)

        # init labels
        self.used_memory_label = QLabel(self)
        self.used_memory_label.setText("00000.00 MB")
        self.total_memory_label = QLabel(self)
        self.total_memory_label.setText("00000.00 MB")
        self.memory_usage_label = QLabel(self)
        self.memory_usage_label.setText("0.00 %")
        self.cpu_usage_label = QLabel(self)
        self.cpu_usage_label.setText("0.00 %")
        self.cpu_count_label = QLabel(self)
        self.cpu_count_label.setText("0 Cores")

        # spacer item 1
        self.spacer_1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(self.spacer_1)

        # add labels
        self.layout.addWidget(QLabel("Used Memory (MB):"), 1, 0)
        self.layout.addWidget(self.used_memory_label, 1, 1)
        self.layout.addWidget(QLabel("Total Memory (MB):"), 2, 0)
        self.layout.addWidget(self.total_memory_label, 2, 1)
        self.layout.addWidget(QLabel("Memory Usage (%):"), 3, 0)
        self.layout.addWidget(self.memory_usage_label, 3, 1)
        self.layout.addWidget(QLabel("CPU Usage (%):"), 4, 0)
        self.layout.addWidget(self.cpu_usage_label, 4, 1)
        self.layout.addWidget(QLabel("CPU Count:"), 5, 0)
        self.layout.addWidget(self.cpu_count_label, 5, 1)

        # spacer item 2
        self.spacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(self.spacer_2)

        # set layout
        self.setLayout(self.layout)

        return

    #----------------------------------------------#

    def update_memory_info(self, cpu_usage_percent):

        # get info
        mem_info = psutil.virtual_memory()
        used_memory = (mem_info.total - mem_info.available) / (1024 ** 2)
        total_memory = mem_info.total / (1024 ** 2)
        memory_usage_percent = mem_info.percent
        cpu_count = psutil.cpu_count()

        # update labels
        self.used_memory_label.setText(f"{used_memory:.2f} MB")
        self.total_memory_label.setText(f"{total_memory:.2f} MB")
        self.memory_usage_label.setText(f"{memory_usage_percent:.2f} %")
        self.cpu_usage_label.setText(f"{cpu_usage_percent:.2f} %")
        self.cpu_count_label.setText(str(cpu_count) + " Cores")

        return

    #----------------------------------------------#

#################################################################
#################################################################

class SystemMonitorWindow(QFrame):

    #----------------------------------------------#

    def __init__(self, parent, app_root_path, time_period = 1000):

        # inheritance
        super().__init__(parent=parent)

        # attributes
        self.parent = parent
        self.app_root_path = app_root_path
        self.time_period = time_period

        # build widgets
        self.buildWidgets()

        # bind widgets
        self.bindWidgets()

        # apply style
        with open(os.path.join(self.app_root_path, "resources", "qss", "system_monitor_window.qss"), "r") as file_qss:
            self.setStyleSheet(file_qss.read())

        # more styling for the frame
        self.setStyleSheet(f"QFrame {{ background-color: {BACKGROUND_COLOR} }}")
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(140)

        return

    #----------------------------------------------#

    def buildWidgets(self):

        # set scroll area (to make widget resizable)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # layout of the form
        self.verticalLayout_frame_holder = QVBoxLayout(self)
        self.verticalLayout_frame_holder.setObjectName("verticalLayout_frame_holder")
        self.verticalLayout_frame_holder.setContentsMargins(0, 0, 0, 0)

        # holder of the form
        self.frame_holder = QFrame(self)
        self.frame_holder.setFrameShape(QFrame.NoFrame)
        self.frame_holder.setFrameShadow(QFrame.Raised)
        self.frame_holder.setObjectName("frame_holder")

        # set the main frame as the widget of the QScrollArea
        self.scroll_area.setWidget(self.frame_holder)

        # add the QScrollArea to the layout
        self.verticalLayout_frame_holder.addWidget(self.scroll_area)

        # create a horizontal layout
        self.layout = QHBoxLayout(self.frame_holder)

        # create main widgets
        self.memory_monitor = MemoryPlotWidget(parent = self.frame_holder)
        self.cpu_monitor = CPUMonitorWidget(parent = self.frame_holder)
        self.system_info = SystemInfoWidget(parent = self.frame_holder)

        # add the widgets to the layout
        self.layout.addWidget(self.memory_monitor)
        self.layout.addWidget(self.cpu_monitor)
        self.layout.addWidget(self.system_info)

        # set stretch factors
        self.layout.setStretch(0, 40)
        self.layout.setStretch(1, 40)
        self.layout.setStretch(2, 10)

        # sizes for widgets
        self.memory_monitor.setMinimumWidth(300)
        self.cpu_monitor.setMinimumWidth(300)

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # set up the timer and connect the update functions
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerCall)
        self.timer.start(self.time_period)

        return

    #----------------------------------------------#

    def timerCall(self):

        # get cpu percentage
        cpu_usage_percent = psutil.cpu_percent()

        # call the updates for the widgets
        self.memory_monitor.update_memory_usage()
        self.cpu_monitor.update_cpu_usage(cpu_usage_percent=cpu_usage_percent)
        self.system_info.update_memory_info(cpu_usage_percent=cpu_usage_percent)

        return

    #----------------------------------------------#

#################################################################
#################################################################