#!/usr/bin/env python3

__Version__ = {'Python':'3.5.2', 'GRASS':'7.4'}
__Name__ = 'Layout_SW_Collection.py'

# --------------------- Environment Variables for GRASS -----------------------
import os
import sys

gisdb = '_DB/'
os.environ['GISBASE'] = gisbase = "/usr/lib/grass74"
location = 'Chennai'
mapset = 'Block'
sys.path.append(os.path.join(gisbase, "etc", "python"))

import grass.script.setup as gsetup
rcfile = gsetup.init(gisbase, gisdb, location, mapset)

from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules import Module
import Calculation

#-------------------------------- Variables -----------------------------------
Join = os.path.join
O = ['overwrite']

Layers = ('nBlocks', 'nPoints', )
# Cleaning the Workspace
#g.remove(type='vector', pattern='*', flags=['f'])

# Importing the ShapeFiles to GRASS
for lr in Layers:
   v.in_ogr(input=Join('SHP',lr), output=lr, flags=O, key='id')

Blocks = Calculation.Blocks # Calculation.py does the calculation
for ix,block in enumerate(Blocks,start=1):

   Points = 'Trip_%s' % ix
   JR = 'JoinedRoad_%s' % ix
   Path = 'Path_%s' % ix
   B = ['Start'] + sorted(block) + ['End']
   L = len(B)
   whr = 'Block IN %s' % str(tuple(B))
   v.extract(input='nPoints', output=Points, where=whr, flags=O)

   v.net(input='nRoads',
        points=Points, # Trip_1
        output=JR,
        operation='connect',
        threshold='100',
        flags = O)

   #v.db_addtable(map=JR, layer=2)
   #v.db_update(map=JR, column='cat', value=1, where="Block like 'Start'")
   #v.db_update(map=JR, column='cat', value=L, where="Block like 'End'")
   #for ix,i in enumerate(sorted(block), start=2):
      #v.db_update(map=Points, column='cat', value=ix, where="Block like '%s'"%i)

   v.net_salesman(input=JR,
                  output=Path,
                  center_cats='1-61',
                  flags=O)

   v.out_ogr(input=Path, output=Path+'.shp', format='ESRI_Shapefile', flags=O)

   # Export Trip
   #if not os.path.exists('Trips'): os.mkdir('Trips')

   #for lyr in (Path, Points):
      #v.out_ogr(input=lyr,
                #output=Join('Trips',lyr),
                #format='ESRI_Shapefile',
                #flags=O)

   #g.remove(type='vector', name=(Points,JR,Path), flags=['f'])
   #break

#g.remove(type='vector', name=('nBlocks', 'nPoints'), flags=['f'])
#EOF
