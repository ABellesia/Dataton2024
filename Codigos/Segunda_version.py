import pandas as pd
from haversine import haversine, Unit

# 1. Cargar los datos de localidades, farmacias existentes, precios y hospitales
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
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_farmacias), axis=1)

# 5. Calcular la distancia mínima de cada localidad a una farmacia existente
localidades_df['distancia_farmacia'] = localidades_df.apply(
    lambda row: distancia_minima((row['latitud'], row['longitud']), coords_farmacias), axis=1)

# 6. Filtrar localidades sin farmacias cercanas (> 10 km)
localidades_sin_farmacias = localidades_df[localidades_df['distancia_farmacia'] > 10]

# 7. Filtrar localidades con alto PIB y población
localidades_rentables = localidades_sin_farmacias[
    (localidades_sin_farmacias['PIB'] > 5000000) &  # Ajusta según tus criterios
    (localidades_sin_farmacias['poblacion'] > 10000)  # Ajusta según tus criterios
]

# 8. Evaluar hospitales con alta capacidad y baja cobertura de farmacias
hospitales_altamente_frecuentados = hospitales_df[
    (hospitales_df['capacidad'] > 500) & (hospitales_df['distancia_farmacia'] > 10)
]

# 9. Incorporar el rango de precios de las farmacias
localidades_rentables = localidades_rentables.merge(precios_farmacias_df, how='left', on='nombre_farmacia')

# 10. Método para asignar la mejor farmacia a cada localidad considerando también la proximidad a hospitales
def asignar_farmacia(localidad, hospitales_cercanos):
    """
    Asigna una farmacia a cada localidad según su perfil económico (PIB y población) y proximidad a hospitales.
    """
    # Ponderar la asignación de farmacias dependiendo si la localidad está cerca de hospitales con alta capacidad
    hospital_influencia = any(hospitales_cercanos['distancia_hospital'] <= 10)

    if hospital_influencia:
        # Si hay un hospital cercano, aumentar la prioridad de farmacias más grandes
        if localidad['PIB'] > 10000000 and localidad['poblacion'] > 50000:
            return 'Farmacias San Pablo'
        elif localidad['PIB'] > 8000000 and localidad['poblacion'] > 40000:
            return 'Farmacias Guadalajara'
        elif localidad['PIB'] > 6000000 and localidad['poblacion'] > 30000:
            return 'Farmacias Benavides'
        else:
            return 'Farmacias del Ahorro'  # Farmacias más asequibles en áreas hospitalarias
    else:
        # Si no hay un hospital cercano, seguimos con la asignación estándar
        if localidad['PIB'] > 10000000 and localidad['poblacion'] > 50000:
            return 'Farmacias San Pablo'
        elif localidad['PIB'] > 8000000 and localidad['poblacion'] > 40000:
            return 'Farmacias Guadalajara'
        elif localidad['PIB'] > 6000000 and localidad['poblacion'] > 30000:
            return 'Farmacias Benavides'
        elif localidad['PIB'] > 5000000 and localidad['poblacion'] > 20000:
            return 'Farmacias Klyn\'s'
        elif localidad['PIB'] > 4000000 and localidad['poblacion'] > 15000:
            return 'Grupo Farmatodo'
        elif localidad['PIB'] > 3000000 and localidad['poblacion'] > 10000:
            return 'Superfarmacias el Fénix'
        else:
            return 'Farmacias del Ahorro'

"""
# 10. Método para asignar la mejor farmacia a cada localidad considerando también la proximidad a hospitales
def asignar_farmacia(localidad, hospital_influencia):
    
    Asigna una farmacia a cada localidad según su perfil económico (PIB y población) y proximidad a hospitales.
    hospital_influencia: booleano que indica si la localidad está cerca de un hospital de alta capacidad.
    
    if hospital_influencia:
        # Si hay un hospital cercano, dar preferencia a farmacias más grandes con capacidad para grandes flujos de clientes
        if localidad['PIB'] > 10000000 and localidad['poblacion'] > 50000:
            return 'Farmacias San Pablo'  # Farmacias grandes para áreas de alto tráfico
        elif localidad['PIB'] > 8000000 and localidad['poblacion'] > 40000:
            return 'Farmacias Guadalajara'
        elif localidad['PIB'] > 6000000 and localidad['poblacion'] > 30000:
            return 'Farmacias Benavides'
        else:
            return 'Farmacias del Ahorro'  # Farmacias más accesibles en zonas hospitalarias con PIB medio
    else:
        # Si no hay hospitales cercanos, asignar farmacias más pequeñas o de nicho
        if localidad['PIB'] > 10000000 and localidad['poblacion'] > 50000:
            return 'Farmacias Klyn\'s'  # Enfocadas en áreas sin hospital pero con alto PIB
        elif localidad['PIB'] > 8000000 and localidad['poblacion'] > 40000:
            return 'Grupo Farmatodo'  # Mercados con PIB alto pero sin hospital cercano
        elif localidad['PIB'] > 6000000 and localidad['poblacion'] > 30000:
            return 'Superfarmacias el Fénix'  # Zonas medianas, sin hospitales, con PIB razonable
        else:
            return 'Farmacias del Ahorro'  # Gama baja, enfocada a zonas con PIB más bajo y menos población

"""


# 11. Método para maximizar el ingreso, seleccionando las mejores 200 localidades
def maximizar_ingreso(df, n=200):
    # Ordenar por PIB y población, para dar prioridad a zonas con alto potencial de ingresos
    df_ordenado = df.sort_values(by=['PIB', 'poblacion'], ascending=[False, False])

    # Seleccionar las primeras 200 localidades
    return df_ordenado.head(n)

# 12. Incorporar hospitales cercanos en el análisis (maximizar ingresos cerca de hospitales con alta capacidad)
def hospitales_cercanos(hospital, localidades_df, max_distancia=10):
    """
    Encuentra localidades rentables cerca de un hospital dentro de un radio determinado.
    """
    coord_hospital = (hospital['latitud'], hospital['longitud'])
    localidades_df['distancia_hospital'] = localidades_df.apply(
        lambda row: haversine((row['latitud'], row['longitud']), coord_hospital, unit=Unit.KILOMETERS), axis=1
    )
    return localidades_df[localidades_df['distancia_hospital'] <= max_distancia]

# Iterar sobre los hospitales más importantes y encontrar localidades cercanas
for index, hospital in hospitales_altamente_frecuentados.iterrows():
    localidades_cercanas = hospitales_cercanos(hospital, localidades_rentables)
    
    # Aquí se influye la asignación de farmacias según cercanía a hospitales
    localidades_cercanas['farmacia_asignada'] = localidades_cercanas.apply(
        lambda row: asignar_farmacia(row, localidades_cercanas), axis=1
    )

# 13. Maximizar ingreso sobre todas las localidades seleccionadas
localidades_seleccionadas = maximizar_ingreso(localidades_rentables)

# 14. Guardar los resultados
localidades_seleccionadas.to_csv('localidades_expansion_max_ingreso.csv', index=False)

print("Se han seleccionado 200 localidades para maximizar el ingreso de ANTAD.")
