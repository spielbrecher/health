import geopandas as gpd
import pandas as pd
import numpy as np
import json
import h3
import folium
import osmnx as ox
from shapely import wkt
from folium.plugins import HeatMap
from shapely.geometry import Polygon

# выводим центроиды полигонов
def get_lat_lon(geometry):

    lon = geometry.apply(lambda x: x.x if x.type == 'Point' else x.centroid.x)
    lat = geometry.apply(lambda x: x.y if x.type == 'Point' else x.centroid.y)
    return lat, lon
# выгрузим границы ЕКБ из OSM
cities = ['Екатеринбург']
polygon_krd = ox.features_from_place(cities, {'boundary':'administrative'}).reset_index()
polygon_krd = polygon_krd[(polygon_krd['name'] == 'городской округ Екатеринбург')]

def create_hexagons(geoJson):

    polyline = geoJson['coordinates'][0]

    polyline.append(polyline[0])
    lat = [p[0] for p in polyline]
    lng = [p[1] for p in polyline]
    m = folium.Map(location=[sum(lat)/len(lat), sum(lng)/len(lng)], zoom_start=13, tiles='cartodbpositron')
    my_PolyLine=folium.PolyLine(locations=polyline,weight=8,color="green")
    m.add_child(my_PolyLine)

    hexagons = list(h3.polyfill(geoJson, 8))
    polylines = []
    lat = []
    lng = []
    for hex in hexagons:
        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v:v[0],polyline))
        lng.extend(map(lambda v:v[1],polyline))
        polylines.append(polyline)
    for polyline in polylines:
        my_PolyLine=folium.PolyLine(locations=polyline,weight=3,color='red')
        m.add_child(my_PolyLine)

    polylines_x = []
    for j in range(len(polylines)):
        a = np.column_stack((np.array(polylines[j])[:,1],np.array(polylines[j])[:,0])).tolist()
        polylines_x.append([(a[i][0], a[i][1]) for i in range(len(a))])

    polygons_hex = pd.Series(polylines_x).apply(lambda x: Polygon(x))

    return m, polygons_hex, polylines
# polygon_hex , polylines - геометрии гексагонов в разных форматах

# сгенерим гексагоны внутри полигона г. Екатеринбург
geoJson = json.loads(gpd.GeoSeries(polygon_krd['geometry']).to_json())
geoJson = geoJson['features'][0]['geometry']
geoJson = {'type':'Polygon','coordinates': [np.column_stack((np.array(geoJson['coordinates'][0])[:, 1],
                                                      np.array(geoJson['coordinates'][0])[:, 0])).tolist()]}

m, polygons, polylines = create_hexagons(geoJson)

def osm_query(tag, city):
    gdf = ox.features_from_place(city, tag).reset_index()
    gdf['city'] = np.full(len(gdf), city.split(',')[0])
    gdf['object'] = np.full(len(gdf), list(tag.keys())[0])
    gdf['type'] = np.full(len(gdf), tag[list(tag.keys())[0]])
    gdf = gdf[['city', 'object', 'type', 'geometry']]
    print(gdf.shape)
    return gdf

 # Выгрузим интересующие нас категории объектов
tags = [
        {'building' : 'school'}, {'building' : 'university'},
        {'building':'college'},
        {'amenity':'school'}, {'amenity':'university'},
        {'amenity':'college'},  {'amenity':'bar'},
        {'shop':'alcohol'}

       ]
cities = ['Екатеринбург, Россия']

gdfs = []
for city in cities:
    for tag in tags:
        gdfs.append(osm_query(tag, city))

# посмотрим что получилось
data_poi = pd.concat(gdfs)
data_poi.groupby(['city','object','type'], as_index = False).agg({'geometry':'count'})

# добавим координаты/центроиды
lat, lon = get_lat_lon(data_poi['geometry'])
data_poi['lat'] = lat
data_poi['lon'] = lon

options = ['school', 'university', 'college']

data_poi_uch_zav = data_poi[data_poi['type'].isin(options)]

latitude_uch_zav = data_poi_uch_zav['lat']

longitude_uch_zav = data_poi_uch_zav['lon']

options = ['bar', 'alcohol']

data_poi_alco = data_poi[data_poi['type'].isin(options)]

latitude_alco = data_poi_alco['lat']

longitude_alco = data_poi_alco['lon']



"""Реализация

https://gist.github.com/MachineLearningIsEasy/4feae2e49cb429eba91cf93a51b65979

:
"""

# Commented out IPython magic to ensure Python compatibility.
import osmnx as ox
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
# %matplotlib inline

G = ox.graph_from_place('Ekaterinburg, Russia', network_type='walk')

fig, ax = ox.plot_graph(
                        G,
                        figsize=(16, 16),
                        show=False, close=False
                        )

ax.scatter(longitude_uch_zav, latitude_uch_zav, c='blue', s=10)#, alpha=0.3)
ax.scatter(longitude_alco, latitude_alco, c='red', s=15)#, alpha=0.3)

plt.show()

"""И в вышеупомянутой статье есть подсчет расстояний между точками."""

center_point = latitude_uch_zav.mean(), longitude_uch_zav.mean()

G = ox.graph_from_point(
                        center_point,
                        dist=1000,
                        network_type='walk',
                        simplify=False
                        )

fig, ax = ox.plot_graph(
                        G,
                        figsize=(16, 16),
                        show=False, close=False
                        )

longitude_school = longitude_uch_zav[2]
latitude_school = latitude_uch_zav[2]

ax.scatter(longitude_alco, latitude_alco, c='red', s=20)#, alpha=0.3)
ax.scatter(longitude_school, latitude_school, c='blue', s=10)#, alpha=0.3)

plt.show()

# Найду вершины графа G, ближайшие к алко
nearest_edge_alco = ox.nearest_edges(G, longitude_alco, latitude_alco)

# Найду вершины графа G, ближайшие к школе

school_point = latitude_school, longitude_school
nearest_edge_school = ox.nearest_edges(G, longitude_school, latitude_school)

nearest_edge_school

# Всего вершин

len(list(G))

# Нарисую один путь:

route = nx.shortest_path(G, nearest_edge_school[0][0], nearest_edge_alco[2][0])

fig, ax = ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')

# Измеряю один путь:

G = ox.add_edge_speeds(G)

route_length = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length')))

print('Route  is', route_length, 'meters')

# Теперь измеряю расстояния по всем объектам:
# Здесь надо для всех школ сделать цикл сначала и для каждой школы посчитать количество вредных точек
route_lengths = []
for i in range(len(latitude_alco)):
    route = nx.shortest_path(G, nearest_edge_school[0][0], nearest_edge_alco[i][0])
    route_length = int(sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length')))
    route_lengths.append(route_length)

    print('Route  is', route_length, 'meters')

schools = ox.nearest_edges(G, longitude_uch_zav, latitude_uch_zav)
schools

# считаем плохие объекты для каждой школы по списку
bad_objects_near_school = []
for s in schools:
  count = 0
  for a in nearest_edge_alco:
    r = nx.shortest_path(G, s[0], a[0])  # Кратчайший путь между каждой школой и каждым плохим объектом
    r_len = int(sum(ox.utils_graph.get_route_edge_attributes(G, r, 'length')))
    if r_len < 100:
      count += 1  # +1 если путь короче 100 метров

  bad_objects_near_school.append( (s, count)  )  # Добавляем кортеж самой школы и количества плохих около нее
  if count>=0:
    print(count)

bad_objects_near_school

