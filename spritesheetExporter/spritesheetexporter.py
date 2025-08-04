from krita import Krita, InfoObject
from math import sqrt, ceil, floor
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QMessageBox

class SpritesheetExporter(object):

    def __init__(self):
        self.app = Krita().instance()
        self.layersObjList = []
        self.layersStates = []
        self.layersNamesList = []
        self.layersNamesDict = {}
        self.grayscale_filter = self.app.filter("desaturate") 

        self.width = None
        self.height = None
        self.col = None
        self.depth = None
        self.profile = None
        self.res = None

        ## DEFAULTS
        self.autoSpace = 0
        self.defaultSpace = 4

        ## ASSIGN THESE BEFORE EXPORT
        self.exportDir = Path.home()
        self.exportName = "Spritesheet"

        self.layerNameSplit = " "
        self.referenceLayerName = "Reference"
        self.backgroundLayerName = "Background"

        self.exportVisibleInstead = False
        self.convertToGrayScale = False
        self.exportMergedMode = False

        self.rows = self.defaultSpace
        self.columns = self.autoSpace

        self.scaleImage = True
        self.scaleAmount = 1

                     
    def export(self):
        ## ===== FUNCS USED THROUGHTOUT ==============
        def cleanUp():
            self.layersObjList.clear()
            self.layersStates.clear()
            self.layersNamesList.clear()
            self.layersNamesDict.clear()

        def quickie(layer,name,doc,spritesExportDir):
            if name in self.layersNamesDict.keys():
                self.layersNamesDict[name] += 1
            else:
                self.layersNamesDict[name] = 1

            if self.convertToGrayScale:
                self.grayscale_filter.apply(layer,0,0,self.width,self.height)
            
            doc.refreshProjection()
            idx = str(self.layersNamesDict[name]).zfill(3)
            fileName = f"{self.exportName}_{name}_{idx}.png"
            imagePath = str(spritesExportDir.joinpath(fileName))
            doc.exportImage(imagePath, InfoObject())
            self.layersNamesList.append(fileName)
            doc.waitForDone()

        def quickieMerged(layers, doc,spritesExportDir, name = "body"):
            if name in self.layersNamesDict.keys():
                self.layersNamesDict[name] += 1
            else:
                self.layersNamesDict[name] = 1

            if self.convertToGrayScale:
                for layer in layers:
                    self.grayscale_filter.apply(layer,0,0,self.width,self.height)

            doc.refreshProjection()
            idx = str(self.layersNamesDict[name]).zfill(3)
            fileName = f"{self.exportName}_{name}_{idx}.png"
            imagePath = str(spritesExportDir.joinpath(fileName))
            doc.exportImage(imagePath, InfoObject())
            self.layersNamesList.append(fileName)
            doc.waitForDone()

        def makeSpritesDirectory():
            spritesExportDir = self.exportDir.joinpath(self.exportName+"_sprites")
            if spritesExportDir.exists():
                for file in spritesExportDir.glob("*.png"):
                    file.unlink()
                spritesExportDir.rmdir()
            spritesExportDir.mkdir()

            return spritesExportDir

        def autoSize(count):
            r = self.rows
            c = self.columns

            if self.rows != self.autoSpace and self.columns!=self.autoSpace:
                pass
            elif self.rows == self.autoSpace:
                r = ceil(count/self.columns)
            elif self.columns == self.autoSpace:
                c = ceil(count/self.rows)
            else:
                r = floor(sqrt(count))
                c = ceil(count/self.rows)

            return r,c

        def hideAllLayers(doc,layers):
            for layer in layers:
                self.layersStates.append(layer.visible())
                layer.setVisible(False)
            doc.refreshProjection()

        def extractLayersAndProperties(doc):
            self.width = doc.width()
            self.height = doc.height()
            self.col = doc.colorModel()
            self.depth = doc.colorDepth()
            self.profile = doc.colorProfile()
            self.res = doc.resolution()

            return doc.topLevelNodes()

        def restoreStates(doc,layers):
            for i,layer in enumerate(layers):
                layer.setVisible(self.layersStates[i])
            doc.refreshProjection()

        def groupLayersNames():
            self.layersNamesList = sorted(self.layersNamesList)

            sortedNames = []
            tmpArray = []
            prev_name = ""

            for name in self.layersNamesList:
                n = name.split("_")[1]

                if n != prev_name:
                    prev_name = n
                    if len(tmpArray)!=0:
                        sortedNames.append(tmpArray.copy())
                        tmpArray.clear()

                tmpArray.append(name)
                
            if len(tmpArray)!=0: 
                sortedNames.append(tmpArray)

            self.layersNamesList = sortedNames

        def positionLayer(layer,i,w,h,columns):
            layer.move((i % columns) * w, (int(i/columns)) * h)
            
        def exportNormalMode(layers,doc,spritesExportDir):
            doc.setBatchmode(True)
            root_node = doc.rootNode()

            for layer,state in zip(layers,self.layersStates):
                name = layer.name().lower().split(self.layerNameSplit)[0]
                
                if name == self.backgroundLayerName.lower() \
                    or name == self.referenceLayerName.lower() \
                        or name == "no" \
                            or (self.exportVisibleInstead and state == False):
                    continue
                
                layer_duplicate = layer.duplicate()
                layer_duplicate.setVisible(True)
                root_node.addChildNode(layer_duplicate, None)
                doc.refreshProjection()
                    
                if layer.animated():
                    for i in range(0, doc.fullClipRangeEndTime()+1):
                        if not layer.hasKeyframeAtTime(i): continue
                        doc.setCurrentTime(i)
                        quickie(layer_duplicate, name, doc, spritesExportDir)
                else:
                    quickie(layer_duplicate, name, doc, spritesExportDir)

                doc.waitForDone()
                root_node.removeChildNode(layer_duplicate)
                layer_duplicate.remove()
        
        def exportMergedMode(layers,doc,spritesExportDir):
            doc.setBatchmode(True)
            root_node = doc.rootNode()

            layer_duplicates = []
            for layer,state in zip(layers,self.layersStates):
                name = layer.name().lower().split(self.layerNameSplit)[0]
                if name == self.backgroundLayerName.lower() \
                    or name == self.referenceLayerName.lower() \
                        or name == "no" \
                            or (self.exportVisibleInstead and state == False):
                    continue
                layer_duplicate = layer.duplicate()
                layer_duplicate.setVisible(True)
                root_node.addChildNode(layer_duplicate, None)
                layer_duplicates.append(layer_duplicate)

            doc.refreshProjection()

            for i in range(0, doc.fullClipRangeEndTime()+1):
                doc.setCurrentTime(i)
                quickieMerged(layer_duplicates, doc, spritesExportDir)
                doc.waitForDone()

            for layer_duplicate in layer_duplicates:
                root_node.removeChildNode(layer_duplicate)
                layer_duplicate.remove()

        def scaleDoc(doc, width, height, amount):
            doc.scaleImage(width*amount,height*amount,self.res,self.res,"NearestNeighbor")
            doc.waitForDone()

        def exportSpritesheetFromImageGroup(img_count, img_group):
            rows,columns = autoSize(img_count)
            sheet_width = columns * self.width
            sheet_height = rows * self.height
            
            sheet = self.app.createDocument(
                sheet_width,
                sheet_height,
                self.exportName,
                self.col, self.depth, self.profile, self.res)
            sheet_root_node = sheet.rootNode()

            for i,img in enumerate(img_group):
                
                layer = sheet.createFileLayer(img, 
                    str(spritesExportDir.joinpath(img)).replace("\\","/"), "ImageToSize")

                sheet_root_node.addChildNode(layer, None)
                    
                positionLayer(layer,i,self.width,self.height,columns)
                sheet.waitForDone()
                
            name = img_group[0].split("_")[1].lower()
            
            sheet.refreshProjection()
            sheet.setBatchmode(True)

            for layer in sheet.topLevelNodes()[1:]:
                layer.mergeDown()

            sheet.refreshProjection()

            if self.scaleImage and self.scaleAmount != 1: 
                scaleDoc(sheet, sheet_width, sheet_height, self.scaleAmount)

            sheet.exportImage(str(self.exportDir.joinpath(f"{self.exportName}_{name}.png")),
                InfoObject())

        
        ## ===== CODE STARTS HERE ====================
        cleanUp()

        spritesExportDir = makeSpritesDirectory()
        doc = self.app.activeDocument()
        layers = extractLayersAndProperties(doc)

        hideAllLayers(doc,layers)

        if not self.exportMergedMode:
            exportNormalMode(layers,doc,spritesExportDir)
        else:
            exportMergedMode(layers,doc,spritesExportDir)
        
        restoreStates(doc,layers)
        groupLayersNames()

        for img_group in self.layersNamesList:
            
            img_count = len(img_group)
            if img_count == 0: continue

            exportSpritesheetFromImageGroup(img_count, img_group)