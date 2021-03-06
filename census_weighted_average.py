import psycopg2 

def census_weighted_average(year):
    insert = "INSERT INTO Census_Weighted_Avg_All (poly_id, year, Total_Pop, PCT_WHITE, PCT_BLACK, PCT_OTHER, TOTAL_UNITS, Median, PCT_OCCUPIED, PCT_VACANT, PCT_OWN_OCC, PCT_RENT_OCC, geom) "
    select = "SELECT redline_poly.poly_id, avg(c.year), avg(c.Total_Pop) AS Total_Pop, (SUM(c.pct_white*c.total_pop)/(SUM(c.total_pop)+1)) AS pct_white, (SUM(c.pct_black*c.total_pop)/(SUM(c.total_pop) + 1)) AS PCT_BLACK, (SUM(c.pct_other*c.total_pop)/(SUM(c.total_pop) + 1)) as pct_other, \
            (SUM(c.total_units*c.total_pop)/(SUM(c.total_pop) + 1)) AS total_units, (SUM(c.median*c.total_pop)/(SUM(c.total_pop) + 1)) AS median, (SUM(c.pct_occupied*c.total_pop)/(SUM(c.total_pop)+1)) AS pct_occupied, (SUM(c.pct_vacant*c.total_pop)/(SUM(c.total_pop)+1)) AS pct_vacant, \
            (SUM(c.pct_own_occ*c.total_pop)/(SUM(c.total_pop)+1)) AS pct_own_occ, (SUM(c.pct_rent_occ*c.total_pop)/(SUM(c.total_pop)+1)) AS pct_rent_occ, redline_poly.geom "
    fr = "FROM redline_poly LEFT JOIN (SELECT c{}.year, c{}.total_pop, c{}.pct_white, c{}.pct_black, c{}.pct_other, c{}.total_units, c{}.median, c{}.pct_occupied, c{}.pct_vacant, c{}.pct_own_occ, \
    c{}.pct_rent_occ, c{}s.geom FROM census_{} AS c{} JOIN census_{}_shp AS c{}s ON c{}.gisjoin = c{}s.gisjoin) AS c ".format(year, year, year, year, year, year, year, year, year, year, year, year, year, year, year, year, year, year)
    if year < 1990:
        join = "ON ST_Intersects(redline_poly.geom, c.geom) AND (ST_Area(ST_Intersection(c.geom, redline_poly.geom)) >= 0.15*ST_Area(c.geom) OR ST_Area(ST_Intersection(c.geom, redline_poly.geom)) >= 0.70*ST_Area(redline_poly.geom)) \
            GROUP BY redline_poly.poly_id;"
    else:
        join = "ON ST_Intersects(redline_poly.geom, c.geom) AND (ST_Area(ST_Intersection(c.geom, redline_poly.geom)) >= 0.50*ST_Area(c.geom) OR ST_Area(ST_Intersection(c.geom, redline_poly.geom)) >= 0.70*ST_Area(redline_poly.geom)) \
            GROUP BY redline_poly.poly_id;"

    query = insert + select + fr + join
    update = "UPDATE Census_Weighted_Avg_All SET Year = {} WHERE Year IS NULL;".format(year)

    return (query, update)
'''
    insert = "INSERT INTO Census_Weighted_Avg_All (poly_id, year, Total_Pop, PCT_WHITE, PCT_BLACK, PCT_OTHER, TOTAL_UNITS, Median, PCT_OCCUPIED, PCT_VACANT, PCT_OWN_OCC, PCT_RENT_OCC, geom) "
    select = "SELECT redline_poly.poly_id, avg(c.year), avg(c.Total_Pop) AS Total_Pop, avg(c.pct_white) AS pct_white, avg(c.pct_black) AS PCT_BLACK, avg(c.pct_other) as pct_other, \
            avg(c.total_units) AS total_units, avg(c.median) AS median, avg(c.pct_occupied) AS pct_occupied, avg(c.pct_vacant) AS pct_vacant, \
            avg(c.pct_own_occ) AS pct_own_occ, avg(c.pct_rent_occ) AS pct_rent_occ, redline_poly.geom "
    fr = "FROM redline_poly LEFT JOIN (SELECT c{}.year, c{}.total_pop, c{}.pct_white, c{}.pct_black, c{}.pct_other, c{}.total_units, c{}.median, c{}.pct_occupied, c{}.pct_vacant, c{}.pct_own_occ, \
    c{}.pct_rent_occ, c{}s.geom FROM census_{} AS c{} JOIN census_{}_shp AS c{}s ON c{}.gisjoin = c{}s.gisjoin) AS c ".format(year, year, year, year, year, year, year, year, year, year, year, year, year, year, year, year, year, year) 
    join = "ON ST_Intersects(redline_poly.geom, c.geom) AND ST_Area(ST_Intersection(c.geom, redline_poly.geom)) >= 0.15*ST_Area(c.geom) GROUP BY redline_poly.poly_id;"
'''

    

conn = psycopg2.connect(database="capp30122", user="alenastern", password='', host="localhost", port="5432")
c = conn.cursor()

create = "CREATE TABLE Census_Weighted_Avg_All (poly_id int, year int, Total_Pop float8, PCT_WHITE float8, PCT_BLACK float8, PCT_OTHER float8, TOTAL_UNITS float8, Median float8, PCT_OCCUPIED float8, PCT_VACANT float8, PCT_OWN_OCC float8, PCT_RENT_OCC float8, geom geometry);"
c.execute(create)



census_years = [1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010]
var_list = ["Total_Pop", "PCT_WHITE", "PCT_BLACK", "PCT_OTHER", "TOTAL_UNITS", "Median", "PCT_OCCUPIED", "PCT_VACANT", "PCT_OWN_OCC", "PCT_RENT_OCC"]

for year in census_years:
    query, update = census_weighted_average(year)
    c.execute(query)
    c.execute(update)

for var in var_list:
    update_null = "UPDATE Census_Weighted_Avg_All SET {} = -1 WHERE {} IS NULL;".format(var, var)
    c.execute(update_null)

add_id_unique = "ALTER TABLE Census_Weighted_Avg_All ADD COLUMN id_unique varchar(10);"
update_id_unique = "UPDATE Census_Weighted_Avg_All SET id_unique = concat(poly_id::text, year::text);"
c.execute(add_id_unique)
c.execute(update_id_unique)

conn.commit()
c.close()
conn.close()

#Cutoff of 15% for 1990 this causes a loss of 10% of the sample data 1692 to 1520 buffer areas
#Cutoff of 15% for 1940 caused a loss of 75% of sample data 1692 to 451 buffer areas
#Cutoff of 5% for 1940 dropped to 600 buffer areas
#Cutoff of 15% for 1940 OR 65% of buffer covered gives us about 880 buffer areas

#Cutoff of 15% for 1940 OR 70% of buffer areas gives us 862 buffers - FINAL SELECTION
#Cutoff of 50% for 1990 or 70% of buffer area gives us 1492 buffers - FINAL SELECTION



#SELECT SUM(CASE WHEN pct_black IS NULL THEN 1 END) AS count_null FROM census_weighted_avg_all;

#Option- have cutoffs for coverage of census tract (eg15%) and a higher threshold for coverage of buffer (eg. 80%) - either has to be met
#paper used 15% cutoff for tracts and 50% for blocks
#Count = 13536 buffer-year observations total (1692 per year), 2273 are null across all years

#Census 1940 didn't cover all of the area of the redline boundaries
#SELECT SUM(CASE WHEN LastExecutionResult IS NULL THEN 1 END) from census_weighted_avg_all;




