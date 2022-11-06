import folium

points = [{0: ['Москва, улица Столетова 11', 'район Раменки', 'Жилой дом', 'Западный административный округ', 100, [55.703143, 37.498909]]}, {1: ['Москва, проспект  Мичуринский 13', 'район Раменки', 'Жилой дом', 'Западный административный округ', 93, [55.698209, 37.511294]]}]


map = folium.Map()

#icon = folium.CustomIcon("postamat.png")

for point_id in range(len(points)):
    point_loc = points[point_id][point_id][-1]

    folium.Marker(location=point_loc).add_to(map)

map.save("test_map.html")