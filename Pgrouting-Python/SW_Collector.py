#!/usr/bin/env python3

__Developer__ = 'Vaasudevan S'
__Name__ = 'SW_Collector.py'

__Version__ = {'Python': '3.5.2', 'GRASS': '7.4',
               'Postgres': '10.3', 'PostGIS': '2.4.3', 'PgRrouting': '2.5.2'}

# -------------------- -ENVIRONMENT FOR GRASS AND POSTGRES ---------------------
import os
import sys

gisdb = '_DB/'
os.environ['GISBASE'] = gisbase = "/usr/lib/grass74"
location = 'Chennai'
mapset = 'Block'
sys.path.append(os.path.join(gisbase, "etc", "python"))

import grass.script.setup as gsetup
rcfile = gsetup.init(gisbase, gisdb, location, mapset)

import psycopg2
conn = psycopg2.connect(database="SolidWaste",
                        user="postgres",
                        host="localhost",
                        password="root")
cursor = conn.cursor()

# -----------------------------------------------------------------------------

from grass.pygrass.modules.shortcuts import general as g
from grass.pygrass.modules.shortcuts import raster as r
from grass.pygrass.modules.shortcuts import vector as v
from grass.pygrass.modules import Module
import random
import subprocess
import shutil
import glob

# ------------------------ Generation of Routes --------------------------------

"""
Each Block is represented by the notation as follows

     3
   -----
  '     '
4 '  A  ' 2
  '     '
  '-----'
     1
"""
# No. of Houses
C = { 'A1': 3,  'B1': 3,  'C1': 3,  'D1': 3,  'E1': 3,
      'A2': 1,  'B2': 1,  'C2': 1,  'D2': 1,  'E2': 6,
      'A3': 3,  'B3': 3,  'C3': 3,  'D3': 3,  'E3': 3,
      'A4': 1,  'B4': 1,  'C4': 1,  'D4': 1,  'E4': 6,

      'F1': 3,  'G1': 3,  'H1': 3,  'I1': 3,  'J1': 6,
      'F2': 6,  'G2': 6,  'H2': 1,  'I2': 1,  'J2': 1,
      'F3': 3,  'G3': 3,  'H3': 3,  'I3': 3,  'J3': 6,
      'F4': 6,  'G4': 6,  'H4': 1,  'I4': 1,  'J4': 1,

      'K1': 3,  'L1': 3,  'M1': 3,  'N1': 3,  'O1': 3,
      'K2': 1,  'L2': 1,  'M2': 6,  'N2': 1,  'O2': 1,
      'K3': 3,  'L3': 3,  'M3': 3,  'N3': 3,  'O3': 3,
      'K4': 1,  'L4': 1,  'M4': 6,  'N4': 1,  'O4': 1,
    }

Values = [[] for i in range(5)] # Values = [[], [], [], []]
Blocks = [[] for i in range(5)] # Blocks = [[], [], [], []]
Vars = [chr(i)+str(j) for i in range(65,80) for j in range(1,5)]
Flag = list(range(60))
Sum = 83

random.seed(9698727450)
ix = 0
Value = Values[ix]
Block = Blocks[ix]

while True:

    j = random.choice(Flag)
    Flag.remove(j)
    val = C[Vars[j]]

    if sum(Value) < Sum:
        Value.append(val*2)
        Block.append(Vars[j])
    if sum(Value) > Sum:
        Excess = sum(Value) - Sum
        Value[-1] -= Excess
        ix += 1
        Value, Block = Values[ix], Blocks[ix]
        Value.append(Excess)
        Block.append(Vars[j])
    elif sum(Value) == Sum:
        ix += 1
        Value, Block = Values[ix], Blocks[ix]
    if ix == 4:
        break

Blocks, Values = Blocks[:-1], Values[:-1]

# --------------------- POSTGIS - PgRouting to generate route ------------------

Query = """\
CREATE TABLE %s AS
SELECT d.seq, d.node, d.edge, d.cost, e.geom
FROM
    pgr_dijkstraVia(
        'SELECT gid as id, source, target, cost, reverse_cost FROM roads',
        ARRAY%s,
        directed:=true, strict:=false, U_turn_on_edge:=true
    ) as d
LEFT JOIN roads as e ON d.edge = e.gid;
"""
Command = 'ogr2ogr -f "ESRI Shapefile" %s %s "%s"'
Layers = []

db = '''PG:"host=localhost
            port=5432
            dbname=SolidWaste
            user=postgres
            password=root"
     '''.replace('\n', ' ')

if not os.path.exists('Out'): os.mkdir('Out')
for ix,block in enumerate(Blocks, start=1):
    Order = []
    T = 'Trip_%s' % ix
    Out = 'Out/%s.shp' % T
    Layers.append(Out)
    for k in ['Start']+block:
        cursor.execute("SELECT place_id from dustbins where block='%s'"%k)
        Order.append(cursor.fetchall()[0][0])
    Full_Query = Query.replace('\n'," ") % (T, Order)
    cursor.execute(Full_Query)
    conn.commit()
    Comm = Command % (Out, db, T)
    subprocess.call([Comm], stdin=subprocess.PIPE, shell=True)

# ----------------- Generation of Maps for the genrated Routes -----------------

O = ['overwrite']
for lyr in Layers+['SHP/Roads', 'SHP/nBlocks']:
    v.in_ogr(input=lyr,
             output=os.path.splitext(os.path.basename(lyr))[0],
             flags=O)
v.label(map='nBlocks', column='Block', labels='Blocks',
        size='30', opaque='no', color='black')

g.region(n=1443552.0, s=1442576.0, e=416851.0, w=415482.0, rows=976,cols=1369)
ps = Module('ps.map')

Path_iden = _ = 'text 416173 1443556 '
for i in range(1,5):
    Path = '->'.join(['Start']+Blocks[i-1])
    sed1 = r"sed -i 's/\bTrip%s\b/Trip%s/g' PS.psmap" % (i-1, i)
    sed2 = r"sed -i 's/\bTrip_%s\b/Trip_%s/g' PS.psmap" % (i-1, i)
    sed3 = r"sed -i 's/%s/%s/g' PS.psmap" % (_, _+Path)
    for j in (sed1, sed2, sed3):
        subprocess.call([j], stdin=subprocess.PIPE, shell=True)
    ps(input='PS.psmap',output='Path_%s.ps'%i, flags=O)
    subprocess.call(['ps2pdf Path_%s.ps'%i], stdin=subprocess.PIPE, shell=True)
    # Replace the new path with the default
    sed4 = r"sed -i 's/%s/%s/g' PS.psmap" % (_+Path, _)
    subprocess.call([sed4], stdin=subprocess.PIPE, shell=True)
else:
    sed1 = r"sed -i 's/\bTrip4\b/Trip0/g' PS.psmap"
    sed2 = r"sed -i 's/\bTrip_4\b/Trip_0/g' PS.psmap"
    for i in (sed1, sed2):
        subprocess.call([i], stdin=subprocess.PIPE, shell=True)

# Combining Maps
subprocess.call(['pdftk *.pdf cat output SW_Collection_Routes.pdf'],
                stdin=subprocess.PIPE,
                shell=True)

# Cleaning the Workspace and removing the PS Outputs
[os.remove(i) for i in glob.glob('Path*')]
# g.remove(type='vector', pattern='*', flags=['f'])
shutil.rmtree('Out')
cursor.execute("DROP TABLE trip_1,trip_2,trip_3,trip_4")
conn.commit()
conn.close()

print("\n\n")
[print(*i, sep='-> ') for i in Blocks]

# EOF
