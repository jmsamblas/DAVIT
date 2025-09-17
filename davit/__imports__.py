#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

# pyqt imports
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QApplication,
    QBoxLayout,
    QCalendarWidget,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDateTimeEdit,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QProgressDialog,
    QScrollArea,
    QSpacerItem,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyledItemDelegate,
    QStyle,
    QTabWidget,
    QTableView,
    QToolBar,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
    QWidgetAction,
)
from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QDesktopServices,
    QDoubleValidator,
    QFont,
    QIcon,
    QIntValidator,
    QKeyEvent,
    QKeySequence,
    QMovie,
    QMouseEvent,
    QPainter,
    QPixmap,
    QShortcut,
    QStandardItem,
    QStandardItemModel,
)
from PyQt6.QtCore import (
    QAbstractTableModel,
    Q_ARG,
    QDate,
    QDateTime,
    QEvent,
    QEventLoop,
    QModelIndex,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSettings,
    QSize,
    QSortFilterProxyModel,
    QThread,
    QTime,
    QTimer,
    Qt,
    QVariant,
    pyqtSignal,
    QStringListModel,
)
from PyQt6.QtCore import QUrl, QItemSelectionModel
from PyQt6 import uic

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