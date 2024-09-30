# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 22:55:45 2024

@author: andyb
"""

import pandas as pd
from haversine import haversine, Unit

import math

# Definir función para calcular la distancia entre dos coordenadas (latitud y longitud)
'''
def haversine_manual(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radio de la Tierra en kilómetros
    
    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distancia en kilómetros
    distancia = R * c
    return distancia
'''



# 1. Cargar los datos de localidades, farmacias existentes, hospitales, gasto en salud y precios promedio por estado
hospitales_df = pd.read_csv('C:\\Users\\andyb\\OneDrive\\Escritorio\\ITAM\\11.Semestre\\Dataton\\BDs\\hospitales.csv')  # nombre_hospital, latitud, longitud
localidades_df = pd.read_csv('C:\\Users\\andyb\\OneDrive\\Escritorio\\ITAM\\11.Semestre\\Dataton\\BDs\\localidades.csv')  # nombre_localidad, latitud, longitud, poblacion, estado
farmacias_existentes_df = pd.read_csv('C:\\Users\\andyb\\OneDrive\\Escritorio\\ITAM\\11.Semestre\\Dataton\\BDs\\farmacias_existentes.csv')  # nombre_farmacia, latitud, longitud
gasto_salud_df = pd.read_csv('C:\\Users\\andyb\\OneDrive\\Escritorio\\ITAM\\11.Semestre\\Dataton\\BDs\\gasto_salud_estados.csv')  # estado, gasto_salud
precios_farmacias_df = pd.read_csv('C:\\Users\\andyb\\OneDrive\\Escritorio\\ITAM\\11.Semestre\\Dataton\\BDs\\precios_farmacias_estados.csv')  # estado, precio_promedio

print(farmacias_existentes_df.columns)
# Asegúrate de que las columnas de latitud y longitud estén en formato float
localidades_df['latitud'] = localidades_df['latitud'].astype(float)
localidades_df['longitud'] = localidades_df['longitud'].astype(float)

farmacias_existentes_df['latitud'] = farmacias_existentes_df['latitud'].astype(float)
farmacias_existentes_df['longitud'] = farmacias_existentes_df['longitud'].astype(float)




# 2. Asignar gasto en salud y precio promedio por estado a cada localidad
localidades_df = localidades_df.merge(gasto_salud_df, on='estado', how='left')
localidades_df = localidades_df.merge(precios_farmacias_df, on='estado', how='left')

# 3. Definir función para calcular la distancia mínima a puntos existentes
'''def distancia_minima(punto, lista_puntos):
    lat1, lon1 = punto
    return min([haversine_manual(lat1, lon1, lat, lon) for lat, lon in lista_puntos])
'''
def distancia_minima(punto, lista_puntos):
    return min([haversine(punto, coord, unit=Unit.KILOMETERS) for coord in lista_puntos])

# 4. Crear listas de coordenadas de farmacias existentes y hospitales
coords_farmacias = list(zip(farmacias_existentes_df['latitud'], farmacias_existentes_df['longitud']))
coords_hospitales = list(zip(hospitales_df['latitud'], hospitales_df['longitud']))

# 5. Calcular la distancia mínima de cada localidad a una farmacia existente
localidades_df['distancia_farmacia'] = localidades_df.apply(
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_farmacias), axis=1
)

print(localidades_df)

print(localidades_df[localidades_df['longitud'].abs() > 180])
localidades_df['latitud'] = localidades_df['latitud'].astype(float)
localidades_df['longitud'] = localidades_df['longitud'].astype(float)

print(localidades_df['latitud'].abs().max())  # Debería ser <= 90
print(localidades_df['longitud'].abs().max())  # Debería ser <= 180

# 6. Calcular la distancia mínima de cada localidad a un hospital
localidades_df['distancia_hospital'] = localidades_df.apply(
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_hospitales), axis=1
)

print(localidades_df.columns)

# 7. Filtrar localidades sin farmacias cercanas (> 10 km)
localidades_sin_farmacias = localidades_df[localidades_df['distancia_farmacia'] > 10]

# 8. Filtrar localidades con alto gasto en salud y población
localidades_sin_farmacias['gasto_salud'] = pd.to_numeric(localidades_sin_farmacias['gasto_salud'], errors='coerce')


localidades_rentables = localidades_sin_farmacias[
    (localidades_sin_farmacias['gasto_salud'] > 50000) &  # Ajustar según criterio
    (localidades_sin_farmacias['poblacion'] > 10000)     # Ajustar según criterio
]

# 9. Asignar farmacias a localidades según perfil económico y precio promedio estatal
def asignar_farmacia(localidad):
    gasto_salud = localidad['gasto_salud']
    poblacion = localidad['poblacion']
    precio_promedio = localidad['precio_promedio']

    # Criterios basados en gasto en salud, población y precio promedio
    if gasto_salud > 8000 and poblacion > 50000 and precio_promedio > 800:
        return 'Farmacias San Pablo'
    elif gasto_salud > 7000 and poblacion > 40000 and precio_promedio > 700:
        return 'Farmacias Guadalajara'
    elif gasto_salud > 6000 and poblacion > 30000 and precio_promedio > 600:
        return 'Farmacias Benavides'
    elif gasto_salud > 5000 and poblacion > 20000 and precio_promedio > 500:
        return 'Farmacias Klyn\'s'
    elif gasto_salud > 4000 and poblacion > 15000 and precio_promedio > 400:
        return 'Grupo Farmatodo'
    elif gasto_salud > 3000 and poblacion > 10000 and precio_promedio > 300:
        return 'Superfarmacias el Fénix'
    else:
        return 'Farmacias del Ahorro'

print(localidades_rentables)

localidades_rentables.loc[:, 'farmacia_asignada'] = localidades_rentables.apply(asignar_farmacia, axis=1)

localidades_rentables['farmacia_asignada'] = localidades_rentables.apply(asignar_farmacia, axis=1)

# 10. Seleccionar las mejores 200 localidades
localidades_seleccionadas = localidades_rentables.sort_values(by=['gasto_salud', 'poblacion'], ascending=False).head(200)

# 11. Guardar los resultados
localidades_seleccionadas[['nombre_localidad', 'latitud', 'longitud', 'farmacia_asignada']].to_csv('localidades_expansion.csv', index=False)

print("Se han seleccionado 200 localidades para la expansión de farmacias.")
print(localidades_seleccionadas)



#PARA IMPRIMIR EL MAPA
 # pip install --user folium

import folium
import pandas as pd

# Cargar los datos de las 200 farmacias seleccionadas
localidades_seleccionadas = pd.read_csv('localidades_expansion_max_ingreso.csv')  # Asegúrate de que tenga las columnas: 'nombre_localidad', 'latitud', 'longitud', 'farmacia_asignada'

# Crear un mapa centrado en México (ajusta las coordenadas según tus necesidades)
mapa = folium.Map(location=[23.6345, -102.5528], zoom_start=5)

# Añadir marcadores para cada farmacia seleccionada
for idx, row in localidades_seleccionadas.iterrows():
    folium.Marker(
        location=[row['latitud'], row['longitud']],
        popup=f"{row['farmacia_asignada']} en {row['nombre_localidad']}",
        icon=folium.Icon(color="blue", icon="plus-sign")
    ).add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("mapa_farmacias.html")

print("Mapa generado y guardado como 'mapa_farmacias.html'")
