
-- DROP TABLE IF EXISTS dustbins, roads, roads_vertices_pgr

-- Add columns
ALTER TABLE roads ADD COLUMN source INTEGER;  
ALTER TABLE roads ADD COLUMN target INTEGER;  
ALTER TABLE roads ADD COLUMN cost FLOAT8;
ALTER TABLE roads ADD COLUMN reverse_cost FLOAT8;

-- Create Topology
-- DROP TABLE roads_vertices_pgr dustbins, roads;
SELECT pgr_createTopology('roads',0.0001,'geom','gid');

-- Set Length for the `length` column
--UPDATE roads SET cost = ST_Length(geom);
--UPDATE roads SET reverse_cost = ST_Length(geom);

-- Add column place_id
ALTER TABLE dustbins ADD COLUMN place_id integer;

-- Update
UPDATE dustbins SET place_id = v.id  
FROM roads_vertices_pgr v  
    WHERE ST_DWithin(v.the_geom, dustbins.geom, 0.005);
    
    
UPDATE roads
SET cost = ST_Length(geom)
WHERE direction in (0,1);

--UPDATE roads
--SET cost = 1000000
--WHERE direction =‐1;

UPDATE roads
SET reverse_cost = ST_Length(geom)
WHERE direction =0; -- direction IN (0, -1)

UPDATE roads
SET reverse_cost= 1000000
WHERE direction =1;    
 
-- Dijkstra Function for routing for Two Points
SELECT d.seq, d.node, d.edge, d.cost, e.geom
FROM
    pgr_dijkstra(
        'SELECT gid as id, source, target, cost, reverse_cost FROM roads',
        (SELECT place_id from dustbins where block='Start'), (SELECT place_id from dustbins where block='A4'),
        directed:=true 
    ) as d
LEFT JOIN roads as e ON d.edge = e.gid;

-- Dijkstra Function for routing for Two Points Via
SELECT d.seq, d.node, d.edge, d.cost, e.geom
FROM
    pgr_dijkstraVia(
        'SELECT gid as id, source, target, cost, reverse_cost FROM roads',
        ARRAY[123, 41, 40, 93, 100, 14, 106, 53, 16, 88, 109, 113, 79, 58, 70, 52],
        directed:=true, strict:=false, U_turn_on_edge:=true
    ) as d
LEFT JOIN roads as e ON d.edge = e.gid;


-- Travelling Salesman Problem
SELECT d.seq, d.cost
FROM
    pgr_tsp('SELECT gid as id, geom FROM dustbins') as d
LEFT JOIN roads as e ON d.edge = e.gid;

-- SELECT id, ST_X(geom)::float, ST_Y(geom)::float FROM dustbins ORDER BY id;

-- Travelling salesman problem from coordinates
SELECT seq, id1, id2, round(cost::numeric, 2), e.geom
    FROM pgr_euclediantsp('SELECT id::INT, ST_X(geom) as x, ST_Y(geom) as y FROM dustbins ORDER BY id', 1)
LEFT JOIN dustbins as e On id2 = e.id;

-- Travelling salesman problem from roads_vertices_pgr
SELECT seq, id1, id2, round(cost::numeric, 2) AS cost
    FROM pgr_tsp('SELECT id::integer, st_x(the_geom) as x,st_x(the_geom) as y FROM roads_vertices_pgr  ORDER BY id', 6, 5);

SELECT ARRAY(SELECT place_id from dustbins where block IN ('Start', 'G2', 'D4', 'J3', 'N1', 'M1', 'J1', 'L2', 'O1', 'I1', 'D2', 'I2', 'H3', 'L4', 'B1', 'N4'
))

