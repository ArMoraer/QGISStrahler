# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Strahler
                                 A QGIS plugin
 This plugin computes the Strahler number of a line network.
                             -------------------
        begin                : 2016-02-21
        copyright            : (C) 2016 by Alexandre Delahaye
        email                : menoetios@gmail.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Strahler class from file Strahler.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .strahler import Strahler
    return Strahler(iface)
