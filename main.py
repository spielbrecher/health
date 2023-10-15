import streamlit as st
import OSMHandler
from OSMPythonTools.overpass import overpassQueryBuilder, Overpass
import pandas as pd

def start(name):
    st.title(f"Hi, {name}")
    st.subheader("fckng sub")

    # scan the input file and fills the handler list accordingly
    st.progress(0)
    st.write()
    #df_osm = tag_genome.sort_values(by=['type', 'id', 'ts'])

def do1():
    osmhandler = OSMHandler.OSMHandler()
    osmhandler.apply_file("ural-fed-district-latest.osm.pbf")
    # transform the list into a pandas DataFrame
    data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid',
                     'user', 'chgset', 'ntags', 'tagkey', 'tagvalue']
    df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
    print(df_osm.head())


def mapit():
    # нахожу айди области
    from OSMPythonTools.nominatim import Nominatim
    nominatim = Nominatim()
    # areaId = nominatim.query('Vienna, Austria').areaId()
    areaId = nominatim.query('Ekaterinburg, Russia').areaId()
    # нахожу количество остановок в этой области

    overpass = Overpass()
    query = overpassQueryBuilder(area=areaId, elementType='node', selector='alcohol')
    #query = overpassQueryBuilder(area=areaId, elementType='node', selector='"building" = "retail"')
    #query = overpassQueryBuilder(area=areaId, elementType='node', selector='"highway"="bus_stop"', out='count')
    result = overpass.query(query)
    result.countElements()

def map_object():
    # узнаем что за объект с таким номером
    from OSMPythonTools.api import Api
    api = Api()
    way = api.query('way/5887599')
    # way = api.query(str(3601477115))
    print(way.tag('building'), way.tag('architect'), way.tag('website'), sep='\n')

if __name__ == '__main__':
    #start('Andy')
    #do1()
    import app_sochi
    app_sochi.start()
