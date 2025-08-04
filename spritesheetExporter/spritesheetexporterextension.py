from krita import Extension, Krita

from . import uispritesheetexporter


class spritesheetExporterExtension(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        exportSs = window.createAction("pykrita_spritesheetExporterCustom",
                                       "SpriteSheet Exporter",
                                       "tools")

        self.ui = uispritesheetexporter.UISpritesheetExporter()
        exportSs.triggered.connect(self.ui.showExportDialog)

app = Krita.instance()
app.addExtension(spritesheetExporterExtension(app))
