#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.views.general.main_window import MainWindow
from davit.views.general.main_window import obtain_real_path

# IMPORTS FOR ARGUMENT PARSING

import os
import sys
import argparse

# IMPORTS (BEFORE SPLASH SCREEN)

from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer

#################################################################
#################################################################

# SPLASH SCREEN STUFF

class CustomSplashScreen(QSplashScreen):

    def mousePressEvent(self, event):
        pass

def show_splash(app, image_path, font_size=10, scale_factor=0.60):

    # get screen resolution
    screen_resolution = app.primaryScreen().size()

    # calculate splash size
    splash_width = int(screen_resolution.width() * scale_factor)
    splash_height = int(screen_resolution.height() * scale_factor)

    # load and scale the pixmap
    splash_pix = QPixmap(image_path)
    scaled_splash_pix = splash_pix.scaled(
        splash_width,
        splash_height,
        Qt.AspectRatioMode.KeepAspectRatio,
    )

    # create the splash screen
    splash = CustomSplashScreen(scaled_splash_pix)

    # set font and show message
    font = QFont()
    font.setPointSize(font_size)
    splash.setFont(font)
    splash.showMessage(
        "Initializing...",
        alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
        color=Qt.GlobalColor.black,
    )

    # show the splash screen
    splash.show()
    app.processEvents()

    return splash

#################################################################
#################################################################

if (__name__ == '__main__'):

    # init app
    print("Starting the application...")
    app = QApplication(sys.argv)

    # get splash path
    splash_path = os.path.join(obtain_real_path(), "resources", "icons", "davit_2_white_bg.png")

    # start splash screen
    splash = show_splash(app, splash_path)

    # big import here
    from davit.__imports__ import *

    # default path?? (OAF is /eos/project/o/oaf/www/results)
    default_path = os.path.expanduser('~')

    # define command-line arguments
    parser = argparse.ArgumentParser(description="DAVIT")
    parser.add_argument("--window_title", default="DAVIT", help="Set the window title")
    parser.add_argument("--window_icon_path", default="davit2.png", help="Set the window icon path")
    parser.add_argument("--screen_resize_factor", type=float, default = 4/5, help="Set the screen resize factor")
    parser.add_argument("--app_root_path", help="Set the application root path")
    parser.add_argument("--qsettings_company_name", default="cern-martinja", help="Set the QSettings company name")
    parser.add_argument("--qsettings_app_name", default="davit", help="Set the QSettings app name")
    parser.add_argument("--default_hdf5_path", default=default_path, help="Set the default HDF5 path")
    parser.add_argument("--startup_dir_to_open", default="", help="Set the startup directory to open")

    # parse command-line arguments
    args = parser.parse_args()

    # init main window
    main_window = MainWindow(app,
                             window_title=args.window_title,
                             window_icon_path=args.window_icon_path,
                             screen_resize_factor=args.screen_resize_factor,
                             app_root_path=args.app_root_path,
                             qsettings_company_name=args.qsettings_company_name,
                             qsettings_app_name=args.qsettings_app_name,
                             default_hdf5_path=args.default_hdf5_path,
                             startup_dir_to_open=args.startup_dir_to_open)

    # function to handle splash and main window interaction
    def show_main_window():
        splash.finish(main_window)
        main_window.setUpOpsAfterInit()
        main_window.show()
        splash.finish(main_window)

    # call the function after 0.5 seconds
    QTimer.singleShot(500, show_main_window)

    # enter into the application running loop
    sys.exit(exec_app_interruptable(app))

#################################################################
#################################################################