import numpy as np
import json
from sklearn.cluster import KMeans
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from geopy.distance import great_circle as GC
import pandas as pd
import math
import pickle

def recommend(geojsonstr, relevant_dict = {'Жилой дом 40-80': 2,
                                    'Жилой дом 80-160': 3,
                                    'Жилой дом 40': 1,
                                    'Жилой дом 160-200': 4,
                                    'Жилой дом 200': 5,
                                    'Постамат': 7,
                                    'Киоск': 10,
                                    'Спортивный объект': 6,
                                    'МФЦ': 8},
                                    clusters=None):
  
  df = pd.read_excel('dataset_v4.xlsx')

  study_area = json.loads(geojsonstr)
  
  coordinates = []
  for i in study_area['features'][0]['geometry']['coordinates'][0]:
      coordinates.append(i)

  coordinates.pop(-1)

  latlong = []
  latitude = df['latitude'].to_numpy()
  longitude = df['longitude'].to_numpy()
  residents = df['apartment'].to_numpy()
  index_list = []
  sum_residents = 0

  for i in range(1,len(df)):
      point = Point(longitude[i], latitude[i])
      polygon = Polygon(coordinates)
      if polygon.contains(point) == True:
        latlong.append([longitude[i],latitude[i]])
        index_list.append(i)
        if df.loc[i,'type'] == 'Жилой дом':
          sum_residents += int(residents[i])



  np_latlong = np.asarray(latlong)
  X = np.vstack(np_latlong)
  
  ################# ЗДЕСЬ БУДЕТ ФУНКЦИЯ МОДЕЛИ ДЛЯ ПРЕЗДСКАЗАНИЯ ############### 

  with open('model_v2.pkl', 'rb') as f:
      ridge = pickle.load(f)
      
  if clusters == None:
    x = np.array([[len(index_list),sum_residents,polygon.area]])
    clusters = ridge.predict(x)
    clusters = math.ceil(clusters)
  if clusters >= len(index_list):
    return len(index_list)
  else:
    pass

  k_means = KMeans(clusters)
  moskva = k_means.fit_predict(X)

  house_dict = {}
  for i in range(0,k_means.n_clusters):
    house_dict[i] = []
    count = 0
    for j in range(0,len(moskva)):
      if moskva[j] == i:
        count +=1
    house_dict[i].append(count)

  weights = np.array([])

  for i in index_list:
    if df.loc[i,'type'] == 'Жилой дом':
      if 40 < int(df.loc[i,'apartment']) <= 80:
        weights = np.append(weights,relevant_dict['Жилой дом 40-80'])
      elif 80 < int(df.loc[i,'apartment']) <= 160:
        weights = np.append(weights,relevant_dict['Жилой дом 80-160'])
      elif int(df.loc[i,'apartment']) <= 40:
        weights = np.append(weights,relevant_dict['Жилой дом 40'])
      elif 160 < int(df.loc[i,'apartment']) <= 200:
        weights = np.append(weights,relevant_dict['Жилой дом 160-200'])
      if 200 < int(df.loc[i,'apartment']):
        weights = np.append(weights,relevant_dict['Жилой дом 200'])
    elif df.loc[i, 'type'] == 'Постамат':
      weights = np.append(weights,relevant_dict['Постамат'])
    elif df.loc[i,'type'] == 'киоск' or df.loc[i,'type'] == 'пресс-стенд':
      weights = np.append(weights,relevant_dict['Киоск'])
    elif df.loc[i, 'type'] == 'Спортивный объект':
      weights = np.append(weights,relevant_dict['Спортивный объект'])
    elif df.loc[i, 'type'] == 'МФЦ' or df.loc[i, 'type'] == 'Флагманский офис':
      weights = np.append(weights,relevant_dict['МФЦ'])

  sum_weights = np.array([])
  for i in range(0,k_means.n_clusters):
    sum = 0
    for j in range(0, len(index_list)):
      if moskva[j] == i:
        sum += weights[j]
    sum_weights = np.append(sum_weights ,sum)

  latitude_postamate = np.array([])
  longitude_postamate = np.array([])

  for i in range(0,k_means.n_clusters):
    latitude_sum = 0
    longitude_sum = 0
    for j in range(0, len(index_list)):
      if moskva[j] == i:
        latitude_sum += (weights[j]*latitude[index_list[j]])/sum_weights[i]
        longitude_sum += (weights[j]*longitude[index_list[j]])/sum_weights[i]
    latitude_postamate = np.append(latitude_postamate, latitude_sum)
    longitude_postamate = np.append(longitude_postamate, longitude_sum)


  new_latlong = np.array([])
  for i in range(0,len(longitude_postamate)):
    near_point = 1 # 1 km
    better_long = latitude_postamate[i]
    better_lat = longitude_postamate[i]
    for j in range(0,len(moskva)):
      if moskva[j] == i:
        a = (latitude_postamate[i], longitude_postamate[i])
        b = (latitude[index_list[j]], longitude[index_list[j]])
        if GC(a,b) < near_point:
          near_point = GC(a,b)
          better_lat = latitude[index_list[j]]
          better_long = longitude[index_list[j]]
    latitude_postamate[i] = better_lat
    longitude_postamate[i] = better_long
    new_latlong = np.append(new_latlong,[longitude_postamate[i],latitude_postamate[i]])


  ##########################  ЭТО ДЕЛАЛ ВЛАД   #################################
  ratings = np.array([])
  _dict = {}
  for i in range(len(moskva)):
    _dict[str(moskva[i])] = []

  for i in range(0,len(longitude_postamate)):
    for j in range(0,len(moskva)):
      if moskva[j] == i:
        _dict[str(moskva[j])].append(j)

  for z in range(0,len(longitude_postamate)):
    rating = 0.0
    count = 0.0
    for i in range(len(_dict[str(z)])):
      x = latitude[index_list[_dict[str(z)][i]]] * 111
      y = longitude[index_list[_dict[str(z)][i]]] * 71

      x0 = latitude_postamate[z] * 111
      y0 = longitude_postamate[z] * 71

      R = 0.400
      
      if ((x - x0)**2 + (y - y0)**2 <= R**2):
        count += 1
    rating = math.ceil((count / len(_dict[str(z)])*100))
    ratings = np.append(ratings, rating)
  print(ratings)
  ##############################################################################
  # sum_rat = math.fsum(ratings)
  # sum_rat  /=len(ratings)


  new_np_latlong = np.asarray(new_latlong)
  new_X = np.vstack(new_np_latlong)

  # fig, axs = plt.subplots(1, 3, figsize=(20,6))
  # axs[0].scatter(X[:, 0], X[:, 1], marker='o')
  # axs[1].scatter(X[:, 0], X[:, 1], c=moskva)
  # axs[2].scatter(X[:,0],X[:,1], marker='o')
  # axs[2].scatter(new_X[:,0],new_X[:,1], marker='o')

  
  address = df['address'].to_numpy()
  district = df['district'].to_numpy()
  type_obj = df['type'].to_numpy()
  AdmArea = df['AdmArea'].to_numpy()

  return_list = []

  # for new_key in range(0,len(ratings)):
  #   for j in range(0,len(index_list)):
  #     return_dict = {}
  #     if latitude_postamate[new_key] == latitude[index_list[j]] and longitude_postamate[new_key] == longitude[index_list[j]]:
  #       return_dict[new_key] = []
  #       return_dict[new_key].append(address[index_list[j]])
  #       return_dict[new_key].append(district[index_list[j]])
  #       return_dict[new_key].append(type_obj[index_list[j]])
  #       return_dict[new_key].append(AdmArea[index_list[j]])
  #       return_dict[new_key].append(ratings[new_key])
  #       return_dict[new_key].append([latitude[index_list[j]], longitude[index_list[j]]])
  #       return_list.append(return_dict)

  
  # return coordinates ,return_list

  coloumns = { 'address': [], 'type': [], 'district': [], 'coordinates': [],
              'ratings': [], 'model': [], 'AdmArea': []}

  df_for_excel = pd.DataFrame(coloumns)
  df_address = []
  df_district = []
  df_AdmArea = []
  df_ratings = []
  df_coord = []
  df_type = []
  df_model = []

  for new_key in range(0,len(ratings)):
    for j in range(0,len(index_list)):
      return_dict = {}
      if latitude_postamate[new_key] == latitude[index_list[j]] and longitude_postamate[new_key] == longitude[index_list[j]]:
        return_dict[new_key] = []

        return_dict[new_key].append(address[index_list[j]])
        df_address.append(address[index_list[j]])

        return_dict[new_key].append(district[index_list[j]])
        df_district.append( district[index_list[j]])

        return_dict[new_key].append(type_obj[index_list[j]])
        df_type.append(type_obj[index_list[j]])

        return_dict[new_key].append(AdmArea[index_list[j]])
        df_AdmArea.append(AdmArea[index_list[j]])

        return_dict[new_key].append(ratings[new_key])
        df_ratings.append(ratings[new_key])

        return_dict[new_key].append([latitude[index_list[j]], longitude[index_list[j]]])
        df_coord.append([latitude[index_list[j]], longitude[index_list[j]]])

        df_model.append('Обученная кластеризация')

        return_list.append(return_dict)



  df_for_excel['address'] = df_address
  df_for_excel['type'] = df_type
  df_for_excel['district'] = df_district
  df_for_excel['coordinates'] = df_coord
  df_for_excel['ratings'] = df_ratings
  df_for_excel['AdmArea'] = df_AdmArea
  df_for_excel['model'] = df_model

  return coordinates, return_list, df_for_excel