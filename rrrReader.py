# -*- coding: utf-8 -*-
"""
/***************************************************************************
 rrrReader
                                 A QGIS plugin
 Reads RRR files
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-02-28
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Morten Sickel
        email                : morten@sickel.net
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsPointXY, QgsField, QgsProject, QgsMapLayerProxyModel, QgsCoordinateTransform, QgsCoordinateReferenceSystem

from PyQt5.QtCore import *



# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .rrrReader_dialog import rrrReaderDialog
import os.path
import json
import re


class rrrReader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'rrrReader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Spectral data')
        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('rrrReader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=False,
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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/rrrReader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Load RRR-files'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Spectral data'),
                action)
            self.iface.removeToolBarIcon(action)


    def newlayer(self):
        layername = 'rrr-data'
        CRS= QgsProject.instance().crs()
        vl = QgsVectorLayer("Point", layername, "memory",crs=CRS)
        pr = vl.dataProvider()
        # Enter editing mode
        vl.startEditing()
        # is this needed?
        # add fields
        pr.addAttributes( [
                    QgsField("fid",QVariant.Int),
                    QgsField("rrr", QVariant.String),
                    QgsField("rrr_data",  QVariant.String),
                    QgsField("filename", QVariant.String),
                    QgsField("osi_relevant", QVariant.Int),
                    QgsField("sample_id", QVariant.String),
                    QgsField("sample_type", QVariant.String),
                    QgsField("mission_code", QVariant.String),
                    QgsField("bar_code", QVariant.String)
                    ])
        # filename and mission should be kept as the two last fields 
        # as they will be added on later
        # when the data is collected
        # Commit changes - is this needed?
        vl.commitChanges()
        # To display the new layer in the project
        QgsProject.instance().addMapLayer(vl)
        # Set the new layer as the default layer to import data into
        self.dlg.cbMapLayer.setLayer(vl)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = rrrReaderDialog(parent=self.iface.mainWindow())
            # This makes the dialog modal
            # self.dlg.pbLoadData.clicked.connect(self.selectfile)
            self.dlg.pbNewLayer.clicked.connect(self.newlayer)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            filename=self.dlg.fwRRRFile.filePath()
            print(filename)
            if self.dlg.cbAllFiles.isChecked():
                directory=os.path.split(filename)[0]
                files=os.listdir(directory)
                rrrfiles=list(filter(lambda x: x.startswith('rrr_'), files))
                rrrfiles.sort()
                for filename in rrrfiles:
                    self.readFile(directory+'/'+filename)
            else:
                self.readFile(filename)
            self.iface.mapCanvas().refreshAllLayers()
            
    def readFile(self,filename):
        print(f'reading {filename}')
        lat = None
        lon = None
        osirelevantfound = False
        sampleid = None
        rrr_data = {}
        rrr_data['nuclides']={}
        rrr_data['attributes']={}
        #filename = "C:/Users/morten/rrr_244 (002).txt"
        layer=self.dlg.cbMapLayer.currentLayer()
        #layer = QgsProject.instance().mapLayersByName('rrr')[0]
        pr = layer.dataProvider()
        rrr = open(filename,'r').read()
        attributes = {}
        readquantified = False
        lines = rrr.split('\n')
        print(f'{len(lines)} lines read')
        header = None
        fromCRS=QgsCoordinateReferenceSystem("EPSG:4326")
        # The coordinate system the data to be imported are stored in
        toCRS= layer.crs()
        self.transformation = QgsCoordinateTransform(fromCRS, toCRS, QgsProject.instance())

        
        for idx,line in enumerate(lines):
            line = line.strip()
            if line.startswith('--------------------------'):
                header = lines[idx-1].lower()
                print(header)
                continue
            if line.endswith('=============='):
                parts = line.split(' ')
                del parts[-1]
                header = ' '.join(parts).lower()
                print(header)
            if header == 'sample information':
                if sampleid is None and line.startswith('Sample ID:'):
                    data = re.split(r"\s{2,}",line)
                    sampleid = data[1]
                    print(f'Sample ID: {sampleid}')
                    continue
                if line.startswith('OSI_'):
                    try:
                        print(idx,line)
                        if ' ' in line:
                            (k,v) = line.split(' ',1)
                        else:
                            k = line
                            v = lines[idx+1]
                        (OSI,k) = k.split('_')
                        k = k.strip()
                        v = v.strip()
                        if k == 'Lat':
                            lat = float(v)
                        if k == 'Lon':
                            lon = float(v)
                        print(k,v)
                        attributes[k] = v
                    except IndexError as e:
                        print(line,idx)
                        print(e)
                        
                continue
                #if header == 'Activity Summary':
            if line.startswith('Detected'):
                #    acttype = line
                #   continue
                if readquantified or line == 'Nuclides Quantified:':
                    if line.startswith('Nuclide'):
                        if line == 'Nuclides Quantified:':
                            readquantified = True
                            continue
                        else:
                            headers = re.split(r"\s{2,}",line)
                            continue
                    elif line.endswith(':'):
                        readquantified = False
                        continue
                    data = re.split(r"\s{2,}",line)
                   
                    if len(data) > 2:
                        line = {}
                        for idx,head in enumerate(headers):
                            line[head]=data[idx]
                        rrr_data['nuclides'][line['Nuclide']] = line
        if not (lat is None or lon is None):
            rrr_data['attributes']=attributes
            insdata = [None,rrr,json.dumps(rrr_data),filename,osirelevantfound,sampleid,attributes['SampleType'],attributes['MissionCode'],attributes['BarCode']]
            feature = QgsFeature()
            point=QgsPointXY(float(lon),float(lat))
            prpoint=self.transformation.transform(point)
            geom=QgsGeometry.fromPointXY(prpoint)
            feature.setGeometry(geom)
            # Fixes attibs later:
            feature.setAttributes(insdata)
            pr.addFeatures( [ feature ] )

    