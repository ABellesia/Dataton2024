import pandas as pd
from haversine import haversine, Unit

# 1. Cargar los datos de localidades, farmacias existentes, y precios
hospitales_df = pd.read_csv('hospitales.csv')  # nombre_hospital, latitud, longitud, capacidad, num_pacientes_dia
localidades_df = pd.read_csv('localidades.csv')  # Contiene: nombre_localidad, latitud, longitud, poblacion, PIB, num_farmacias
farmacias_existentes_df = pd.read_csv('farmacias_existentes.csv')  # Contiene: nombre_farmacia, latitud, longitud
precios_farmacias_df = pd.read_csv('precios_farmacias.csv')  # Contiene: nombre_farmacia, rango_precio

# 2. Definir función para calcular la distancia mínima a farmacias existentes
def distancia_minima(punto, lista_puntos):
    return min([haversine(punto, (lat, lon), unit=Unit.KILOMETERS) for lat, lon in lista_puntos])

# 3. Crear listas de coordenadas de farmacias existentes
coords_farmacias = list(zip(farmacias_existentes_df['latitud'], farmacias_existentes_df['longitud']))

# 4. Calcular la distancia mínima de cada hospital a una farmacia existente
hospitales_df['distancia_farmacia'] = hospitales_df.apply(
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_farmacias_existentes), axis=1)

# 4. Calcular la distancia mínima de cada localidad a una farmacia existente
localidades_df['distancia_farmacia'] = localidades_df.apply(
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_farmacias), axis=1)
# 4. Calcular la distancia mínima de cada hospital a una farmacia existente

hospitales_df['distancia_farmacia'] = hospitales_df.apply(
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_farmacias_existentes), axis=1)

# 5. Filtrar localidades sin farmacias cercanas (> 10 km)
localidades_sin_farmacias = localidades_df[localidades_df['distancia_farmacia'] > 10]

# 6. Filtrar localidades con alto PIB y población
localidades_rentables = localidades_sin_farmacias[
    (localidades_sin_farmacias['PIB'] > 5000000) &  # Ajusta según tus criterios
    (localidades_sin_farmacias['poblacion'] > 10000)  # Ajusta según tus criterios
]

# 6. Evaluar hospitales con alta capacidad y baja cobertura de farmacias
hospitales_altamente_frecuentados = hospitales_df[
    (hospitales_df['capacidad'] > 500) & (hospitales_df['distancia_farmacia'] > distancia_minima_farmacia)
]

# 7. Incorporar el rango de precios de las farmacias
localidades_rentables = localidades_rentables.merge(precios_farmacias_df, how='left', on='nombre_farmacia')

# 7. Fusionar con localidades rentables (donde se pueden ubicar farmacias) y su PIB
hospitales_con_localidades_cercanas = pd.merge(hospitales_altamente_frecuentados, localidades_df, on=['latitud', 'longitud'])

# 8. Asignar farmacias a hospitales donde no haya farmacias cercanas o donde la densidad sea insuficiente
hospitales_con_localidades_cercanas['farmacia_asignada'] = hospitales_con_localidades_cercanas.apply(asignar_farmacia, axis=1)

# 9. Guardar resultados
hospitales_con_localidades_cercanas.to_csv('hospitales_sin_farmacias.csv', index=False)

# Método para asignar la mejor farmacia a cada localidad según perfil económico
# Método para asignar la mejor farmacia a cada localidad según perfil económico
def asignar_farmacia(localidad):
    """
    Asigna una farmacia a cada localidad según su perfil económico (PIB y población).
    Considera las 7 farmacias: Farmacias San Pablo, Farmacias Guadalajara,
    Farmacias del Ahorro, Farmacias Benavides, Farmacias Klyn's, Grupo Farmatodo y Superfarmacias el Fénix.
    """
    if localidad['PIB'] > 10000000 and localidad['poblacion'] > 50000:
        return 'Farmacias San Pablo'  # Farmacia de rango alto, dirigida a zonas con alto PIB y alta población
    elif localidad['PIB'] > 8000000 and localidad['poblacion'] > 40000:
        return 'Farmacias Guadalajara'  # También para mercados grandes, pero con un enfoque más general
    elif localidad['PIB'] > 6000000 and localidad['poblacion'] > 30000:
        return 'Farmacias Benavides'  # Farmacia de gama media-alta, en mercados medianos con buena economía
    elif localidad['PIB'] > 5000000 and localidad['poblacion'] > 20000:
        return 'Farmacias Klyn\'s'  # Farmacia de rango medio en mercados emergentes
    elif localidad['PIB'] > 4000000 and localidad['poblacion'] > 15000:
        return 'Grupo Farmatodo'  # Zonas de población media y economía en crecimiento
    elif localidad['PIB'] > 3000000 and localidad['poblacion'] > 10000:
        return 'Superfarmacias el Fénix'  # Para zonas con economías más pequeñas pero aún rentables
    else:
        return 'Farmacias del Ahorro'  # Gama baja, enfocada a zonas con PIB más bajo y menos población

# Aplicar el método de asignación a cada localidad
localidades_rentables['farmacia_asignada'] = localidades_rentables.apply(asignar_farmacia, axis=1)


# Aplicar el método de asignación a cada localidad
localidades_rentables['farmacia_asignada'] = localidades_rentables.apply(asignar_farmacia, axis=1)

# Método para maximizar el ingreso, seleccionando las mejores 200 localidades
def maximizar_ingreso(df, n=200):
    # Ordenar por PIB y población, para dar prioridad a zonas con alto potencial de ingresos
    df_ordenado = df.sort_values(by=['PIB', 'poblacion'], ascending=[False, False])

    # Seleccionar las primeras 200 localidades
    return df_ordenado.head(n)

# Aplicar maximización
localidades_seleccionadas = maximizar_ingreso(localidades_rentables)

# 9. Guardar los resultados
localidades_seleccionadas.to_csv('localidades_expansion_max_ingreso.csv', index=False)

print("Se han seleccionado 200 localidades para maximizar el ingreso de ANTAD.")
