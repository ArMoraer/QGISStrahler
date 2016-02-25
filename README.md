Strahler plugin
=================

Description
-----------

Strahler is designed to compute the [Strahler number](https://en.wikipedia.org/wiki/Strahler_number) of a line network, from a purely topological (i.e. without DEM) point of view. The line network must be divided in segments, so that each "T" junction is made of 3 segments (and not 2). Similarly, each "X" junction must be made of 4 segments, and so on.

This plugin will compute the Strahler number of each segment and add it to a new field (attribute).

Polyline layers are not handled for now.

UI
--

First, select the segment which represents the root of the network; this segment must be connected to the rest of the network by only one endpoint. Only one segment can be selected. Click on the plugin icon: you will be asked the name of the new attribute (default is strahler). If a field with this name already exists, a confirmation window will ask you if you want to overwrite it.

Example
-------

![Strahler order](/img/demo.png "Strahler order")

