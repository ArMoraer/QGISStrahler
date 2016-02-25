# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Strahler
                                 A QGIS plugin
 This plugin computes the Strahler number of a line network.
                              -------------------
        begin                : 2016-02-21
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Alexandre Delahaye
        email                : menoetios@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QObject, QSettings, QTranslator, QVariant, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMessageBox
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from strahler_dialog import StrahlerDialog
import os.path


class Strahler(QObject):
    """QGIS Plugin Implementation."""

    partDone = pyqtSignal(int)
    allDone = pyqtSignal()

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        super(Strahler, self).__init__() # necessary for pyqtSignal

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Strahler_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = StrahlerDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Strahler')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Strahler')
        self.toolbar.setObjectName(u'Strahler')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Strahler', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Strahler/img/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Strahler'),
            callback=self.run,
            parent=self.iface.mainWindow())
        self.dlg.runButton.clicked.connect( self.onStart )
        self.dlg.attributeEdit.textChanged.connect( self.checkAttr )
        self.partDone.connect( self.updateProgressBar )
        self.allDone.connect( self.onFinished )


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Strahler'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    @pyqtSlot()
    def onStart(self):
        self.dlg.runButton.setEnabled(False)
        self.dlg.closeButton.setEnabled(False)

        # input params
        self.v = False # verbose

        self.main()


    @pyqtSlot()
    def onFinished(self):
        self.dlg.progressBar.setValue( 100 )
        # self.dlg.runButton.setEnabled(True)
        self.dlg.closeButton.setEnabled(True)


    def checkAttr(self, text):
        if len(text) > 0:
            self.dlg.runButton.setEnabled(True)
        else:
            self.dlg.runButton.setEnabled(False)


    def main(self):

        # If attribute already exists
        if not self.layer.dataProvider().fields().indexFromName( self.dlg.attributeEdit.text() ) == -1:
            messageBox = QMessageBox()
            messageBox.setWindowTitle( "Strahler" )
            messageBox.setText( self.tr("Attribute already exists!") )
            messageBox.setInformativeText( self.tr("Continue anyway? Existing values will be lost.") )
            messageBox.setIcon( QMessageBox.Warning )
            messageBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel);
            res = messageBox.exec_()

            if res == QMessageBox.Cancel:
                self.dlg.runButton.setEnabled(True)
                self.dlg.closeButton.setEnabled(True)
                return
            else:
                self.attrIdx = self.layer.dataProvider().fields().indexFromName( self.dlg.attributeEdit.text() )

        else:
            # Add new attribute
            self.layer.dataProvider().addAttributes( [QgsField(self.dlg.attributeEdit.text(), QVariant.String)] )
            self.attrIdx = self.layer.dataProvider().fields().indexFromName( self.dlg.attributeEdit.text() )
            self.layer.updateFields() # tell the vector layer to fetch changes from the provider

        self.layer.startEditing()

        # Anti-loop device
        self.treatedFeatures = []

        # Real job is here
        self.computeStrahler( self.rootFeature, self.rootEndPoint )

        self.layer.commitChanges()
        self.allDone.emit()


    def computeStrahler(self, feature, originPoint):

        # Anti-loop device
        if feature.id() in self.treatedFeatures:
            if self.v: print "Feature ID {0} already done".format(feature.id())
            return 0

        self.treatedFeatures.append( feature.id() )

        # Progress bar
        self.countFeat += 1
        self.partDone.emit( float(self.countFeat)/len(self.allFeatures)*100 )

        # Gets children lines
        connectedLines = self.getConnectedLines( feature, originPoint )

        if self.v: print "ID {0}: connectedLines={1}".format( feature.id(), list({f.id() for f in connectedLines}) )

        # If no children, Strahler number = 1
        if len( connectedLines ) == 0:
            strahler = 1

        # Else, compute children's Strahler number
        else:
            points = feature.geometry().asPolyline()
            endpoint = points[-1] if originPoint == points[0] else points[0]

            # for line in connectedLines:
            strahlerList = [ self.computeStrahler( line, endpoint ) for line in connectedLines ]

            if self.v: print "| ID {0}: strahlerList={1}".format( feature.id(), strahlerList )
            
            m = max( strahlerList ) # maximum Strahler number
            m_nbr = len( [i for i, j in enumerate(strahlerList) if j == m] ) # number of maxima

            # if there is only 1 maximum, parent's Strahler = maximum; else, parent's Strahler = maximum+1
            strahler = m if m_nbr == 1 else m+1

        self.layer.changeAttributeValue(feature.id(), self.attrIdx, strahler)

        return strahler


    def getConnectedLines( self, feature, originPoint ):
        """Get all lines which are connected to <feature> by one endpoint (other than <originPoint>)."""
    
        connectedLines = []

        points = feature.geometry().asPolyline()
        endpoint = points[-1] if originPoint == points[0] else points[0]

        # Get the ids of all the features in the index that are within
        # the bounding box of the current feature because these are the ones
        # that will be connected.
        ids = self.spatialIdx.intersects( feature.geometry().boundingBox() )
        
        # if self.v: 
        #   spatialList = sorted( list(self.spatialIdx.intersects( self.outLyr.extent() )) )
        #   print "| getConnectedLines::spatialIdx={0} {1}".format( len( spatialList ), spatialList )
        
        for id in ids:
            
            ifeature = self.allFeatures[id] # self.allFeatures is computed in checkSelectedFeature

            if ifeature.id() == feature.id():
                continue

            if ifeature.geometry().isMultipart(): # multipart lines are ignored
                continue

            ipoints = ifeature.geometry().asPolyline()
            iendPt0 = ipoints[0]
            iendPt1 = ipoints[-1]

            # check if one endpoint of <feature> is equal to one endpoint of <ifeature>
            if (endpoint == iendPt0) or (endpoint == iendPt1):
                connectedLines.append( ifeature )
                
        return connectedLines


    def checkSelectedFeature(self, selectedFeatures):
        """Checks if there is exactly one selected feature, and if this feature has one free and one connected endpoint"""

        if (selectedFeatures == None) or (len(selectedFeatures) < 1):
            self.displayErrorMessage( self.tr("Please select a root segment") )
            return False, None

        if len(selectedFeatures) > 1:
            self.displayErrorMessage( self.tr("Only one root segment can be selected") )
            return False, None

        selectedFeature = selectedFeatures[0]

        # Build the spatial index for faster lookup.
        featureList = list( self.layer.getFeatures() )
        self.spatialIdx = QgsSpatialIndex()
        map( self.spatialIdx.insertFeature, featureList )

        # Get the ids of all the features in the index that are within
        # the bounding box of the current feature because these are the ones
        # that will be connected.
        ids = self.spatialIdx.intersects( selectedFeature.geometry().boundingBox() )
        self.allFeatures = { feature.id(): feature for feature in featureList }

        points = selectedFeature.geometry().asPolyline()
        endPt0 = points[0]
        endPt1 = points[-1]
        isConnectedEndPt0 = False
        isConnectedEndPt1 = False

        # Checks which endpoint is connected
        for id in ids:
            
            ifeature = self.allFeatures[id]
            
            if ifeature.id() == selectedFeature.id():
                continue

            if ifeature.geometry().isMultipart(): # multipart lines are ignored
                continue

            ipoints = ifeature.geometry().asPolyline()
            iendPt0 = ipoints[0]
            iendPt1 = ipoints[-1]

            if (iendPt0 == endPt0) or (iendPt1 == endPt0):
                isConnectedEndPt0 = True

            if (iendPt0 == endPt1) or (iendPt1 == endPt1):
                isConnectedEndPt1 = True

            if isConnectedEndPt0 and isConnectedEndPt1:
                self.displayErrorMessage( self.tr("The selected segment is not a root segment") )
                return False, None

        if not isConnectedEndPt0 and not isConnectedEndPt1:
            self.displayErrorMessage( self.tr("The selected segment is not connected to a network") )
            return False, None

        return True, endPt0 if isConnectedEndPt1 else endPt1 # returns the free endpoint


    def displayErrorMessage(self, content):
        """Displays a QMessageBox popup"""
        
        messageBox = QMessageBox()
        messageBox.setWindowTitle( "Strahler" )
        messageBox.setText( content )
        messageBox.setIcon( QMessageBox.Critical )
        messageBox.exec_()


    def updateProgressBar( self, progress ):
        self.dlg.progressBar.setValue( progress )


    def run(self):
        """Run method that performs all the real work"""

        # Get selected features
        self.layer = self.iface.mapCanvas().currentLayer()
        featureList = None

        if hasattr(self, 'layer') and not self.layer == None: # if a layer is selected
            featureList = self.layer.selectedFeatures()
        
        # print "layer name={0}".format( self.layer.name() )
        # print "feature id={0}".format( [f.id() for f in featureList] )

        res, self.rootEndPoint = self.checkSelectedFeature( featureList )

        if not res:
            return

        self.rootFeature = featureList[0]
        self.countFeat = 0 # for progress bar

        # If the selected feature is fine:
        if res:
            self.dlg.runButton.setEnabled(True)
            self.dlg.layerLabel.setText( self.layer.name() )

            # show the dialog
            self.dlg.show() 

            # Run the dialog event loop
            self.dlg.exec_()
            self.dlg.progressBar.setValue(0)
