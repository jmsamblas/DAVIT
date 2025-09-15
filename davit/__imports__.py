#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

# pyqt imports
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QWidget, QWidgetAction, QToolBar, QAction, QMessageBox, QFileDialog, QDialog, QCompleter, QMenuBar, QDateTimeEdit, QCalendarWidget)
from PyQt5.QtWidgets import (QSplitter, QProgressDialog, QPushButton, QLabel, QSpacerItem, QToolButton, QComboBox, QCheckBox, QScrollArea, QAbstractScrollArea, QGroupBox, QLineEdit, QSpinBox)
from PyQt5.QtWidgets import (QBoxLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QStyledItemDelegate, QShortcut, QStyle, QColorDialog)
from PyQt5.QtWidgets import (QTableView, QAbstractItemView, QHeaderView, QTabWidget, QStackedWidget, QTreeView, QListWidget)
from PyQt5.QtGui import (QIcon, QStandardItemModel, QStandardItem, QBrush, QColor, QPixmap, QFont, QKeySequence, QIntValidator, QDoubleValidator, QMovie, QKeyEvent, QPainter, QMouseEvent)
from PyQt5.QtCore import (QModelIndex, QSize, Qt, QTimer, QEvent, QEventLoop, QAbstractTableModel, QObject, pyqtSignal, QPoint, QSettings, QRect, QThread, QStringListModel, QMetaObject, Q_ARG, QVariant, QSortFilterProxyModel, QDate, QTime, QDateTime)
from PyQt5.Qt import (QItemSelectionModel, QMenu, QUrl, QDesktopServices)
from PyQt5 import (uic)

# cern imports
from accwidgets.qt import exec_app_interruptable
import operator
import functools
import pytimber

# other imports
import gc
from time import sleep
from datetime import datetime
from copy import deepcopy
import natsort
import numpy as np
import pandas as pd
import shutil
import pprint
import json
import os
import sys
import re
import collections
import pyqtgraph as pg
import seaborn as sns
import qtawesome as qta
import random
import tempfile
from typing import cast
from itertools import groupby
import ast
import math
import pathlib
import h5py
import psutil
import requests
from scipy.fft import rfft as scipy_compute_rfft
from scipy.fft import fft as scipy_compute_fft
from scipy.fft import rfftfreq as scipy_compute_rfftfreq
from scipy.stats import gaussian_kde

# utils imports
from davit.utils.general_utils import (fromBytesToString, getSystemTempDir, closeEventIgnore, clearLayout, iterItems, getPixelWidthFromQLabel, getVersionNameFromInit, NumpyFindNearest, getTabIndexByName, numpy_find_nearest, get_index_type, columnNameFormatting)
from davit.utils.subclassing_hacks import (CustomMultiPlotLegendItem, CustomMultiPlotItemSample, QVSeparationLine, QHSeparationLine, QComboBoxNoScrollWheel, ScrollLabel, CustomCornerWidget)

# table imports
from custom_martinja_tableview import (DataFrameWidget, DataFrameModel)

#################################################################
#################################################################