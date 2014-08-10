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
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load vectorTiles class from file vectorTiles
    from vectortiles import vectorTiles
    return vectorTiles(iface)
