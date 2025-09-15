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

class SettingsPreferencesView(QDialog):

    #----------------------------------------------#

    def __init__(self, dict_for_settings, qsettings, default_settings, app = None, app_root_path = None, parent = None):

        # inherit from QDialog
        QDialog.__init__(self)

        # main attributes
        self.dict_for_settings = dict_for_settings
        self.qsettings = qsettings
        self.default_settings = default_settings
        self.app = app
        self.app_root_path = app_root_path
        self.parent = parent

        # own attributes
        self.timer_hide_label = None
        self.original_dict_for_settings = self.dict_for_settings.copy()

        # load ui file
        uic.loadUi(os.path.join(self.app_root_path, "resources", "uis", "settings_preferences.ui"), self)

        # title and icon
        self.setWindowTitle("Settings (Preferences)")
        self.setWindowIcon(qta.icon("ri.settings-4-fill"))

        # build and bind widgets
        self.buildCodeWidgets()
        self.bindWidgets()

        return

    #----------------------------------------------#

    def buildCodeWidgets(self):

        # hide green label
        self.label_saved_changes.setVisible(False)

        # load all preferences
        self.loadPreferences()

        return

    #----------------------------------------------#

    def bindWidgets(self):

        # colors
        self.pushButton_color_background.clicked.connect(lambda state, color_type="background": self.onClickColorButton(color_type))

        # defaults
        self.pushButton_back_to_defaults.clicked.connect(self.backToDefaults)

        # apply changes
        self.pushButton_apply.clicked.connect(self.applyChanges)

        return

    #----------------------------------------------#

    def onClickColorButton(self, color_type):

        # open the dialog
        hexa_color = self.openColorDialog(color_type)

        # if color was valid
        if hexa_color:

            # save colors
            # self.dict_for_settings[f"color_{color_type}"] = hexa_color
            self.pushButton_color_background.setStyleSheet(f"QPushButton{{background-color:{hexa_color};}}")

        return

    #----------------------------------------------#

    def openColorDialog(self, color_type):

        # get color
        color = QColorDialog.getColor(QColor(self.dict_for_settings[f"color_{color_type}"]))

        # check that color is valid
        if color.isValid():
            return str(color.name())
        else:
            return None

    #----------------------------------------------#

    def backToDefaults(self):

        # update dict (THIS LINE WILL AUTOMATICALLY SAVE SETTINGS) (DISABLE IN CASE WE DONT WANT TO APPLY CHANGES RIGHT AFTER THE DEFAULTS)
        self.dict_for_settings.update(self.default_settings)

        # set checkboxes
        self.loadPreferences()

        # update preferences in the main window
        self.parent.dict_for_settings = self.dict_for_settings

        # save settings
        for st in self.dict_for_settings:
            if "color" in st:
                self.qsettings.setValue(str(st), str(self.dict_for_settings[st]))
            else:
                self.qsettings.setValue(str(st), int(self.dict_for_settings[st]))

        # update main GUI
        if self.parent:
            if self.original_dict_for_settings != self.dict_for_settings:
                self.parent.resetRightAndLeftTabs()
                self.original_dict_for_settings = self.dict_for_settings.copy()

        # show confirmation label
        self.showLabel("Default settings were applied!")

        return

    #----------------------------------------------#

    def loadPreferences(self):

        # checkboxes
        self.checkBox_setting_disable_selection_cart.setChecked(self.dict_for_settings["setting_disable_selection_cart"] == 1)
        self.checkBox_setting_auto_merge_group.setChecked(self.dict_for_settings["setting_auto_merge_group"] == 1)
        self.checkBox_setting_enable_1_button_mouse_mode.setChecked(self.dict_for_settings["setting_enable_1_button_mouse_mode"] == 1)
        self.checkBox_setting_enable_downsampling_plots.setChecked(self.dict_for_settings["setting_enable_downsampling_plots"] == 1)
        self.checkBox_setting_display_strings_on_x_axis.setChecked(self.dict_for_settings["setting_display_strings_on_x_axis"] == 1)
        self.checkBox_setting_enable_system_monitor.setChecked(self.dict_for_settings["setting_enable_system_monitor"] == 1)

        # spinboxes
        self.spinBox_min_big_data_sample_size.setValue(self.dict_for_settings["min_big_data_sample_size"])
        self.spinBox_max_n_columns.setValue(self.dict_for_settings["max_n_columns"])
        self.spinBox_ncurves_at_init.setValue(self.dict_for_settings["ncurves_at_init"])
        self.spinBox_refresh_rate_system_monitor.setValue(self.dict_for_settings["refresh_rate_system_monitor"])

        # lineedits
        self.lineEdit_color_foreground_palette_name.setText(self.dict_for_settings["color_foreground_palette_name"])

        # color preferences
        hexa_color = self.dict_for_settings["color_background"]
        self.pushButton_color_background.setStyleSheet(f"QPushButton{{background-color:{hexa_color};}}")

        return

    #----------------------------------------------#

    def applyChanges(self):

        # print
        print("Changes were saved!")

        # save preferences
        self.savePreferences()

        # update main GUI
        if self.parent:
            if self.original_dict_for_settings != self.dict_for_settings:
                self.parent.resetRightAndLeftTabs()
                self.original_dict_for_settings = self.dict_for_settings.copy()

        # show confirmation label
        self.showLabel("Changes were saved!")

        return

    #----------------------------------------------#

    def showLabel(self, text):

        # show green label
        self.label_saved_changes.setText(text)
        self.label_saved_changes.setVisible(True)

        # stop timer if it exists
        if self.timer_hide_label:
            if self.timer_hide_label.isActive():
                self.timer_hide_label.stop()

        # hide green timer after a period of time
        self.timer_hide_label = QTimer(self)
        self.timer_hide_label.setSingleShot(True)
        self.timer_hide_label.timeout.connect(self.hideLabel)
        self.timer_hide_label.start(2000)

        return

    #----------------------------------------------#

    def hideLabel(self):

        # hide the label
        self.label_saved_changes.setVisible(False)

        return

    #----------------------------------------------#

    def savePreferences(self):

        # checkboxes
        self.updatePreferences(self.checkBox_setting_disable_selection_cart.isChecked(), "setting_disable_selection_cart", "checkbox")
        self.updatePreferences(self.checkBox_setting_auto_merge_group.isChecked(), "setting_auto_merge_group", "checkbox")
        self.updatePreferences(self.checkBox_setting_enable_1_button_mouse_mode.isChecked(), "setting_enable_1_button_mouse_mode", "checkbox")
        self.updatePreferences(self.checkBox_setting_enable_downsampling_plots.isChecked(), "setting_enable_downsampling_plots", "checkbox")
        self.updatePreferences(self.checkBox_setting_display_strings_on_x_axis.isChecked(), "setting_display_strings_on_x_axis", "checkbox")
        self.updatePreferences(self.checkBox_setting_enable_system_monitor.isChecked(), "setting_enable_system_monitor", "checkbox")
        
        # spinboxes
        self.updatePreferences(self.spinBox_min_big_data_sample_size.value(), "min_big_data_sample_size", "spinbox")
        self.updatePreferences(self.spinBox_max_n_columns.value(), "max_n_columns", "spinbox")
        self.updatePreferences(self.spinBox_ncurves_at_init.value(), "ncurves_at_init", "spinbox")
        self.updatePreferences(self.spinBox_refresh_rate_system_monitor.value(), "refresh_rate_system_monitor", "spinbox")

        # lineedits
        self.updatePreferences(self.lineEdit_color_foreground_palette_name.text(), "color_foreground_palette_name", "lineedit")

        # colors
        match = re.search(r'background-color:(#[0-9A-Fa-f]{6});', self.pushButton_color_background.styleSheet())
        if match:
            hexa_color = match.group(1)
            self.updatePreferences(hexa_color, "color_background", "color")

        # update parent dict
        self.parent.dict_for_settings = self.dict_for_settings

        return

    #----------------------------------------------#

    def updatePreferences(self, value, pref_label, widget_type):

        # Qt.Checked is 2 instead of 1
        if widget_type == "checkbox":
            if int(value) > 0:
                value = 1

        # parse depending on widget
        if widget_type == "lineedit" or widget_type == "color":
            value = str(value)
        else:
            value = int(value)

        # update dict
        self.dict_for_settings[pref_label] = value

        # save settings
        self.qsettings.setValue(str(pref_label), value)

        return

    #----------------------------------------------#

    def closeEvent(self, evt):

        # print
        print("Closing the settings panel...")

        # close the window
        evt.accept()

        return

    #----------------------------------------------#

#################################################################
#################################################################