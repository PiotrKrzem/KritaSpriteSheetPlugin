from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QVBoxLayout, QFrame, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QLabel,
                             QPushButton,QSpinBox, QDialog, QLineEdit,
                             QCheckBox, QDialogButtonBox)
from krita import Krita
from pathlib import Path
from . import spritesheetexporter

class describedWidget:
    def __init__(self, widget, descri="", tooltip=""):
        self.widget = widget
        self.descri = descri
        self.tooltip = tooltip


class UISpritesheetExporter(object):

    def __init__(self):
        self.app = Krita().instance()
        self.exp = spritesheetexporter.SpritesheetExporter()
        self.exportPath = Path.home()

        self.mainDialog = QDialog()
        self.mainDialog.setWindowModality(Qt.NonModal)
        self.mainDialog.setMinimumSize(500, 100)
        self.mainLayout = QVBoxLayout(self.mainDialog)

        ## BASIC SETTINGS
        self.exportNameTextBox = QLineEdit()
        self.exportNameTextBox.setText(self.exp.exportName)

        self.exportDirTextBox = QLineEdit()

        self.exportDirButton = QPushButton("Change export directory")
        self.exportDirButton.clicked.connect(self.changeExportDir)

        self.visibleSettingsLayout = QVBoxLayout()

        ## ADVANCED SETTINGSS CHECKBOX
        self.customSettings = QCheckBox()
        self.customSettings.setChecked(False)
        self.customSettings.stateChanged.connect(self.toggleHideable)

        self.hideableWidget = QFrame()
        self.hideableWidget.setFrameShape(QFrame.Panel)
        self.hideableWidget.setFrameShadow(QFrame.Sunken)
        self.hideableLayout = QVBoxLayout(self.hideableWidget)

        ## ADVANCED SETTINGS
        self.grayscaleSettings = QCheckBox()
        self.grayscaleSettings.setChecked(self.exp.convertToGrayScale)

        self.exportMergedSettings = QCheckBox()
        self.exportMergedSettings.setChecked(self.exp.exportMergedMode)

        self.exportVisibleSettings = QCheckBox()
        self.exportVisibleSettings.setChecked(self.exp.exportVisibleInstead)

        self.layerNameSplitTextBox = QLineEdit()
        self.layerNameSplitTextBox.setText(self.exp.layerNameSplit)

        self.backgroundLayerNameTextBox = QLineEdit()
        self.backgroundLayerNameTextBox.setText(self.exp.backgroundLayerName)

        self.referenceLayerNameTextBox = QLineEdit()
        self.referenceLayerNameTextBox.setText(self.exp.referenceLayerName)

        self.scaleSheetSettings = QCheckBox()
        self.scaleSheetSettings.setChecked(self.exp.scaleImage)

        self.scaleAmount = QSpinBox(minimum = 1)
        self.scaleAmount.setValue(self.exp.scaleAmount)

        ## ADVANCED SETTINGS - ROWS AND COLUMNS
        self.columnsRowsSelectionWidget = QFrame()
        self.columnsRowsSelectionWidget.setFrameShape(QFrame.Panel)
        self.columnsRowsSelectionWidget.setFrameShadow(QFrame.Sunken)
        self.columnsRowsSelectionLayout = QHBoxLayout(self.columnsRowsSelectionWidget)

        self.rows = QSpinBox(minimum = self.exp.autoSpace)
        self.rows.setValue(self.exp.autoSpace)

        self.columns = QSpinBox(minimum = self.exp.autoSpace)
        self.columns.setValue(self.exp.defaultSpace)

        ## BOTTOM BUTTONS
        self.OkCancelButtonBox = \
            QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.OkCancelButtonBox.accepted.connect(self.confirmButton)
        self.OkCancelButtonBox.rejected.connect(self.mainDialog.close)

        self.build_layout()

    def addDescribedWidget(self, parent, listWidgets, align=Qt.AlignLeft):
        layout = QGridLayout()
        row = 0
        for widget in listWidgets:
            label = QLabel(widget.descri)
            if widget.descri != "":
                label.setBuddy(widget.widget)
                layout.addWidget(label, row, 0)
            layout.addWidget(widget.widget, row, 1)
            if widget.tooltip != "":
                widget.widget.setToolTip(widget.tooltip)
                label.setToolTip(widget.tooltip)
            row += 1
        layout.setAlignment(align)
        parent.addLayout(layout)
        return layout

    def build_layout(self):

        self.addDescribedWidget(parent=self.visibleSettingsLayout, listWidgets=[
            describedWidget(
                widget=self.exportNameTextBox,
                descri="Export name:",
                tooltip="The name of the exported spritesheet file"
            ),
            describedWidget(
                widget=self.exportDirTextBox,
                descri="Export Directory:",
                tooltip="The directory the spritesheet will be exported to"
            ),
            describedWidget(
                widget=self.exportDirButton,
                descri="",
                tooltip=""
            ),

            describedWidget(
                widget=self.customSettings,
                descri="Advanced Settings:",
                tooltip="Display advanced settings"
            )
        ])

        self.mainLayout.addLayout(self.visibleSettingsLayout, 0)

        ## HIDDEN SETTINGS

        self.addDescribedWidget(parent=self.columnsRowsSelectionLayout, listWidgets=[
            describedWidget(
                widget=self.rows,
                descri="Rows:",
                tooltip="Number of rows of the spritesheet;\n" +
                "default is assigned depending on columns number\n" +
                "or if 0 columns tries to form a square "
            ),
            describedWidget(
                widget=self.columns,
                descri="Columns:",
                tooltip="Number of columns of the spritesheet;\n" +
                "default is assigned depending on rows number\n" +
                "or if 0 rows tries to form a square"
            )
        ])


        self.addDescribedWidget(parent=self.hideableLayout, listWidgets=[
            describedWidget(
                widget = self.columnsRowsSelectionWidget,
                descri="Spritesheet dimensions (0 for auto):",
                tooltip="For example with 16 sprites, " +
                        "leaving both rows and columns at 0\n" +
                        "will set their defaults to 4 each\n" +
                        "while leaving only columns at 0 and rows at 1\n" +
                        "will set columns default at 16"
            ),
            describedWidget(
                widget=self.layerNameSplitTextBox,
                descri="Layer name delimeter:",
                tooltip="Delimeter used to extract layer names"
            ),
            describedWidget(
                widget=self.backgroundLayerNameTextBox,
                descri="Background layers name:",
                tooltip="Layers that begin with this word will be ignored when exporting"
            ),
            describedWidget(
                widget=self.referenceLayerNameTextBox,
                descri="Reference layers name:",
                tooltip="Layers that begin with this word will be ignored when exporting"
            ),
            describedWidget(
                widget=self.grayscaleSettings,
                descri="Convert to grayscale:",
                tooltip="Gets Y-layer from YCbCr version of layers"
            ),
            describedWidget(
                widget=self.exportMergedSettings,
                descri="Merge layers before export:",
                tooltip="Merges animations so that output spritesheet contains\n"+
                        "all frames merged together frame-by-frame"
            ),
            describedWidget(
                widget=self.exportVisibleSettings,
                descri="Export only visible layers:",
                tooltip="Instead of exporting all layers, export only visible layers"
            ),
            describedWidget(
                widget=self.scaleSheetSettings,
                descri="Scale spritesheet:",
                tooltip="When generating final spritesheet, scale it times a given amount using the NearestNeighbour strategy"
            ),
            describedWidget(
                widget=self.scaleAmount,
                descri="Scale times x:",
                tooltip="Output image dimensions will be multiplied by this value"
            ),
        ])

        self.mainLayout.addWidget(self.hideableWidget)
        self.mainLayout.addWidget(self.OkCancelButtonBox)

        self.toggleHideable()


    def toggleHideable(self):
        if self.customSettings.isChecked():
            self.hideableWidget.show()
            self.mainDialog.adjustSize()
        else:
            self.hideableWidget.hide()
            self.mainDialog.adjustSize()

    def showExportDialog(self):
        self.doc = self.app.activeDocument()

        if self.exportDirTextBox.text() == "" \
            and self.doc \
                and self.doc.fileName():
                    self.exportPath = Path(self.doc.fileName()).parents[0]
                    self.exportDirTextBox.setText(str(self.exportPath))

        self.mainDialog.setWindowTitle("Automatic Spritesheet Exporter")
        self.mainDialog.setSizeGripEnabled(True)
        self.mainDialog.show()
        self.mainDialog.activateWindow()
        self.mainDialog.setDisabled(False)

    def changeExportDir(self):
        self.exportDirDialog = QFileDialog()
        self.exportDirDialog.setWindowTitle("Choose Export Directory")
        self.exportDirDialog.setSizeGripEnabled(True)
        self.exportDirDialog.setDirectory(str(self.exportPath))

        self.exportPath = self.exportDirDialog.getExistingDirectory()
        if self.exportPath != "":
            self.exportDirTextBox.setText(str(self.exportPath))

    def confirmButton(self):
        self.mainDialog.setDisabled(True)

        # Basic
        self.exp.exportName = self.exportNameTextBox.text()
        self.exp.exportDir = Path(self.exportDirTextBox.text())
        
        # Advanced
        self.exp.layerNameSplit = self.layerNameSplitTextBox.text()
        self.exp.backgroundLayerName = self.backgroundLayerNameTextBox.text()
        self.exp.referenceLayerName = self.referenceLayerNameTextBox.text()

        self.exp.convertToGrayScale = self.grayscaleSettings.isChecked()
        self.exp.exportMergedMode = self.exportMergedSettings.isChecked()
        self.exp.exportVisibleInstead = self.exportVisibleSettings.isChecked()

        self.exp.scaleImage = self.scaleSheetSettings.isChecked()
        self.exp.scaleAmount = self.scaleAmount.value()

        self.exp.rows = self.rows.value()
        self.exp.columns = self.columns.value()
            
        self.exp.export()
        self.mainDialog.hide()
