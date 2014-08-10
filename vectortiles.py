# -*- coding: utf-8 -*-
"""
/***************************************************************************
 vectorTiles
                                 A QGIS plugin
 load vector tiles from GSI Maps
                              -------------------
        begin                : 2014-08-08
        copyright            : (C) 2014 by ASAHI Kosuke
        email                : waigania13@gmail.com
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import os.path
import urllib, urllib2
from tempfile import mkdtemp

from xyUtil import scale2zoom, latlng2xy

class vectorTiles:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'vectortiles_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
                
        # gourp layer id
        self.groupLayerID = -1
        
        # define jgd2000 coodinate
        self.jgd = QgsCoordinateReferenceSystem()
        self.jgd.createFromSrid(4612)
        
        # make temp directory
        self.tempdir = mkdtemp()
        
        # tiles on current view
        self.currentTiles = []
        
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(ur"国土地理院ベクトルタイル提供実験", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        #self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&vector tiles", self.action)
        
    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&vector tiles", self.action)
        #self.iface.removeToolBarIcon(self.action)

    # run method that performs all the real work
    def run(self):
        # prevent multiple start
        if self.iface.legendInterface().groupExists(self.groupLayerID):
            return
        
        # make layer group for vector tiles
        self.groupLayerID = self.iface.legendInterface().addGroup('vector tiles')
        
        # connect extents changed signal to loadTiles method
        self.iface.mapCanvas().mapCanvasRefreshed.connect(self.loadTiles)
        
        # zoom to GSI
        centerGeometry = QgsGeometry.fromWkt(QgsPoint(140.0845833, 36.10458).wellKnownText())
        centerGeometry.transform(QgsCoordinateTransform(self.jgd, self.iface.mapCanvas().mapSettings().destinationCrs()))
        centerPoint = centerGeometry.asPoint()
        extent = self.iface.mapCanvas().extent()
        extent.scale(5000.0/self.iface.mapCanvas().scale(), centerPoint)
        self.iface.mapCanvas().setExtent(extent)
        self.iface.mapCanvas().refresh()
        
    # load vector tiles on canvas extent
    def loadTiles(self):
        extent = QgsGeometry.fromWkt(self.iface.mapCanvas().extent().asWktPolygon()) 
        extent.transform(QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(), self.jgd))
        
        # calculate x,y,z
        zoom = scale2zoom(self.iface.mapCanvas().scale())
        swxy = latlng2xy(extent.boundingBox().yMinimum(), extent.boundingBox().xMinimum(), zoom)
        nexy = latlng2xy(extent.boundingBox().yMaximum(), extent.boundingBox().xMaximum(), zoom)
        
        # load tiles
        tiles = []
        for x in range(swxy[0], nexy[0]+1):
            for y in range(nexy[1], swxy[1]+1):
                zxy = '%i-%i-%i.geojson' % (zoom, x, y)
                #QMessageBox.information (self.iface.mainWindow(), 'Debug', 'add'+zxy)
                id = getLayerIDByName(zxy)
                if id is not None:
                    tiles.append(id)
                    continue
               
                ## download vector tiles to temporary folder
                ## if already exist in temporary folder, use downloaded one
                
                #tempfile = os.path.join(self.tempdir, zxy)
                #if not os.path.exists(tempfile):
                #    try:
                #        urllib.urlretrieve(r'http://cyberjapandata.gsi.go.jp/xyz/experimental_rdcl/'+str(zoom)+'/'+str(x)+'/'+str(y)+'.geojson', tempfile)
                #    except IOError:
                #        continue
                #tileLayer = QgsVectorLayer(tempfile, zxy, 'ogr')
                
                tileLayer = QgsVectorLayer('http://cyberjapandata.gsi.go.jp/xyz/experimental_rdcl/'+str(zoom)+'/'+str(x)+'/'+str(y)+'.geojson', zxy, 'ogr')
                if not tileLayer.isValid():
                    continue
                
                tileLayer.setCrs(self.jgd)
                QgsMapLayerRegistry.instance().addMapLayer(tileLayer)
                self.iface.legendInterface().moveLayer(tileLayer, self.groupLayerID)
                tiles.append(tileLayer.id())
                
        
        # remove tiles outside of current extent
        QgsMapLayerRegistry.instance().removeMapLayers(list(set(self.currentTiles).difference(set(tiles))))

        self.currentTiles = tiles[:]

def getLayerIDByName(name):
    for layer in QgsMapLayerRegistry.instance().mapLayers().values():
        if layer.name() == name:
            return layer.id()
    return None