import folium
import pickle
import json

from default_map import get_default_map


def folium_update(polygon_locations, points:list) -> list:
    list(map(lambda x: x.reverse(), polygon_locations))
    
    postamat_count = len(points)

    m = get_default_map()

    folium.Polygon(locations=polygon_locations, color="green", fill_color="green").add_to(m)
    
    for object_id in range(len(points)):

        print(points[object_id])

        point_loc = points[object_id][object_id][-1]
        pop = "Рейтинг: " + str(points[object_id][object_id][4]) + "<br>"  + "ID:" + str(object_id) + "<br>" + points[object_id][object_id][0] + "<br>" + points[object_id][object_id][2]
        postamat_icon = folium.CustomIcon("assets/postamat.png", icon_size=[36,43])
        
        folium.Marker(location=point_loc, icon=postamat_icon, popup=pop).add_to(m)

    with open("pickles/identifier.pickle", "rb") as s_identifier:
        identifier = pickle.load(s_identifier)    

    identifier += 1
    filename = "map_" + str(identifier) + ".html"
    path = "./static/result_maps/" + filename
    

    with open("identifier.pickle", "wb") as s_identifier:
        pickle.dump(identifier, s_identifier)

    m.save(path)

    return ["." + path, str(postamat_count), str(identifier)]

    
# points = [{0: ['Москва, улица Столетова 11', 'район Раменки', 'Жилой дом', 'Западный административный округ', 100, [55.703143, 37.498909]]}, {1: ['Москва, проспект  Мичуринский 13', 'район Раменки', 'Жилой дом', 'Западный административный округ', 93, [55.698209, 37.511294]]}, 
# {2: ['Москва, проспект  Ломоносовский 41 к1', 'район Раменки', 'Жилой дом', 'Западный административный округ', 100, [55.706016, 37.50665]]}, {3: ['Москва, проспект  Мичуринский 21 к1', 'район Раменки', 'Жилой дом', 'Западный административный округ', 95, [55.699586, 37.504039]]}, 
# {4: ['Москва, проспект  Ломоносовский 29 к3', 'район Раменки', 'Жилой дом', 'Западный административный округ', 86, [55.704046, 37.514349]]}]

# # # хлам для распарса geojson---------------------------------------
# with open("./data (1).geojson", "r") as file_json:
#     study_area = json.load(file_json)


# print(folium_update(study_area['features'][0]['geometry']['coordinates'][0], points))
