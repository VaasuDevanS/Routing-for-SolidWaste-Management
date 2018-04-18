
# Import Dustbins to PostGIS
shp2pgsql -I -s 32644 -S -t 2D SHP/nPoints/nPoints.shp Dustbins | psql "sslmode=require host=localhost port=5432 dbname=SolidWaste user=postgres"

# Import Roads to PostGIS
shp2pgsql -I -s 32644 -S -t 2D SHP/Roads/Roads.shp Roads | psql "sslmode=require host=localhost port=5432 dbname=SolidWaste user=postgres"

# Export Shapefile results
pgsql2shp -f out.shp -u postgres -P root -p 5432 -g geom SolidWaste "SELECT * from dustbins"

SELECT d.seq, d.node, d.edge, d.cost, e.geom FROM pgr_dijkstraVia('SELECT gid as id, source, target, cost, reverse_cost FROM roads', (SELECT ARRAY(SELECT place_id from dustbins where block IN ('Start', 'G2', 'D4', 'J3', 'N1', 'M1', 'J1', 'L2', 'O1', 'I1', 'D2', 'I2', 'H3', 'L4', 'B1', 'N4'
))), directed:=true, strict:=false, U_turn_on_edge:=true ) as d LEFT JOIN roads as e ON d.edge = e.gid;


pgsql2shp -f out.shp -u postgres -P root -p 5432 -g geom SolidWaste "SELECT d.seq, d.node, d.edge, d.cost, e.geom FROM pgr_dijkstraVia('SELECT gid as id, source, target, cost, reverse_cost FROM roads', (SELECT ARRAY(SELECT place_id from dustbins where block IN ('Start', 'G2', 'D4', 'J3', 'N1', 'M1', 'J1', 'L2', 'O1', 'I1', 'D2', 'I2', 'H3', 'L4', 'B1', 'N4'))), directed:=true, strict:=false, U_turn_on_edge:=true ) as d LEFT JOIN roads as e ON d.edge = e.gid;"

ogr2ogr -f "ESRI Shapefile" test.shp PG:"host=localhost port=5432 dbname=SolidWaste user=postgres password=root" "SELECT e.geom FROM     pgr_dijkstraVia(         'SELECT gid as id, source, target, cost, reverse_cost FROM roads',         ARRAY[123, 107, 75, 21, 95, 47, 37, 111, 4, 97, 33, 12, 68, 91],         directed:=true, strict:=false, U_turn_on_edge:=true     ) as d LEFT JOIN roads as e ON d.edge = e.gid;"
