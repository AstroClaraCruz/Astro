import streamlit as st
from skyfield.api import load, wgs84
from datetime import datetime, timezone, date, time
from geopy.geocoders import Nominatim
import pycountry
from email_utils import send_email

def get_city_coordinates(city_name, country_code=None):
    geolocator = Nominatim(user_agent="my_app")
    
    # If country code is provided, include it in the search query
    if country_code:
        search_query = f"{city_name}, {country_code}"
    else:
        search_query = city_name
    
    location = geolocator.geocode(search_query)
    if location:
        return location.latitude, location.longitude, location.address
    else:
        return None, None, None

def calcular_posiciones_planetarias(fecha, latitud, longitud, nombre_archivo, first_name, email):
    # Cargar los datos de los planetas
    planetas = load('de421.bsp')
    tierra = planetas['earth']
    
    # Crear un objeto Time para la fecha y hora especificadas
    ts = load.timescale()
    # t = ts.from_datetime(fecha.replace(tzinfo=timezone.utc))
    t = ts.from_datetime(fecha)
    
    # Crear un objeto para la ubicación en la Tierra
    ubicacion = tierra + wgs84.latlon(latitud, longitud)
    
    # Lista de cuerpos celestes a calcular
    cuerpos_celestes = {
        'sol': 'sun',
        'luna': 'moon',
        'mercurio': 'mercury barycenter',
        'venus': 'venus barycenter',
        'marte': 'mars barycenter',
        'jupiter': 'jupiter barycenter',
        'saturno': 'saturn barycenter',
        'urano': 'uranus barycenter',
        'neptuno': 'neptune barycenter',
        'pluton': 'pluto barycenter'
    }
    
    resultados = {}
    
    for nombre_es, nombre_en in cuerpos_celestes.items():
        astrobj = planetas[nombre_en]
        astro = ubicacion.at(t).observe(astrobj)
        alt, az, _ = astro.apparent().altaz()
        
        # Convertir a grados zodiacales (aproximación simple)
        ra, dec, _ = astro.radec()
        long_ecliptica = (ra.hours / 24) * 360
        signo_zodiacal = int(long_ecliptica / 30)
        grados_en_signo = long_ecliptica % 30
        
        signos = ['Aries', 'Tauro', 'Géminis', 'Cáncer', 'Leo', 'Virgo', 
                  'Libra', 'Escorpio', 'Sagitario', 'Capricornio', 'Acuario', 'Piscis']
        
        resultados[nombre_es] = {
            'altitud': alt.degrees,
            'azimut': az.degrees,
            'signo': signos[signo_zodiacal],
            'grados': grados_en_signo
        }
        
        # Guardar resultados en archivo
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"Birth Chart for {first_name}\n")
            if email:
                f.write(f"Email: {email}\n")
            f.write(f"Posiciones planetarias para {fecha}\n")
            f.write(f"Ubicación: Latitud {latitud}, Longitud {longitud}\n")
            f.write("-" * 50 + "\n\n")
        
            for cuerpo, datos in resultados.items():
                f.write(f"{cuerpo.capitalize()}:\n")
                f.write(f"  Signo: {datos['signo']}\n")
                f.write(f"  Grados: {datos['grados']:.2f}°\n")
                f.write("\n")
    
    return resultados


def main():
    st.title("Step 1: Birth Data Entry")

    # Crear columnas para organizar el formulario
    col1, col2 = st.columns([2, 1])

    with col1:
        # Nombre y apellido
        first_name = st.text_input("First name", max_chars=40)
        last_name = st.text_input("Last name", max_chars=40, placeholder="(optional)")
        email = st.text_input("Email", max_chars=100, placeholder="(optional)")
        
        # Género
        gender = st.radio(
            "Gender",
            options=["Female", "Male", "Event/other"],
            horizontal=True
        )
        if gender == "Event/other":
            st.info("Event chart: No interpretation will be offered.")
        
        # Fecha de nacimiento
        st.subheader("Birthday")
        
        # Crear tres columnas para día, mes y año
        col_day, col_month, col_year = st.columns([1, 2, 1])
        
        with col_day:
            day = st.text_input("Day", max_chars=2)
        
        with col_month:
            months = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
            month = st.selectbox("Month", months, index=0)
            month_num = months.index(month) + 1
        
        with col_year:
            year = st.text_input("Year", max_chars=4)

        # Hora de nacimiento
        st.subheader("Birth Time")
        
        # Crear dos columnas para hora y minutos
        col_hour, col_min = st.columns([2, 1])
        
        with col_hour:
            hours = ["???", "unknown"] + [f"{i} [{i if i <= 12 else i-12} {'am' if i < 12 else 'pm'}]" for i in range(24)]
            hour = st.selectbox("Hour", hours, index=0)
        
        with col_min:
            minutes = st.text_input("Minutes", max_chars=5, help="Enter minutes (00-59) or use format MM:SS or MM:SS.ss for precise time")

        # Ciudad de nacimiento
        st.subheader("Birth Place")
        
        # Lista de países
        countries = [(country.name, country.alpha_2) for country in pycountry.countries]
        countries.sort(key=lambda x: x[0])  # Ordenar alfabéticamente
        
        # Selector de país
        country_name = st.selectbox(
            "Select Country",
            options=[name for name, code in countries],
            index=None,
            placeholder="Choose a country..."
        )
        
        # Obtener el código del país seleccionado
        country_code = next((code for name, code in countries if name == country_name), None)
        
        
        
        
        city = st.text_input("Enter city", placeholder="Enter city name", disabled=not country_name )
        
        if country_name and city:
            latitud, longitud, direccion_completa = get_city_coordinates(city, country_code)
            if latitud is not None:
                st.success(f"Location found:")
                st.write(f"🌍 {direccion_completa}")
                st.write(f"📍 Coordinates: {latitud:.4f}°, {longitud:.4f}°")
            else:
                st.error(f"City not found in {country_name}. Please try another city name.")


    # Botón para generar el reporte
    if st.button("Calculate Positions", type="primary"):
        # Validar que todos los campos necesarios estén completos
        if not all([first_name, day, month, year, hour != "???", minutes, city]):
            st.warning("Please fill in all required fields.")
        else:
            try:
                # Convertir los datos a formato datetime
                hour_val = 0 if hour == "unknown" else int(hour.split()[0])
                min_val = int(minutes.split(':')[0])
                sec_val = int(minutes.split(':')[1]) if ':' in minutes else 0
                
                fecha_hora = datetime(
                    int(year),
                    month_num,
                    int(day),
                    hour_val,
                    min_val,
                    sec_val,
                    tzinfo=timezone.utc
                )
                
                # Calcular posiciones planetarias
                nombre_archivo = f'posiciones_planetarias_{first_name.lower()}.txt'
                posiciones = calcular_posiciones_planetarias(fecha_hora, latitud, longitud, nombre_archivo, first_name, email)
                
                # Mostrar resultados
                st.success(f"Calculation completed for {first_name}")
                st.write(f"Results saved to: {nombre_archivo}")
                
                for cuerpo, datos in posiciones.items():
                    st.write(f"{cuerpo.capitalize()}: en {datos['signo']} a {datos['grados']:.2f}°")
                    
                # Send email if provided
                if email:
                    if send_email(email, nombre_archivo, first_name):
                        st.success(f"Results emailed to {email}")
                    else:
                        st.error("Failed to send email")
                    
            except ValueError as e:
                st.error(f"Error in date/time format: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Agregar información de ayuda en el sidebar
with st.sidebar:
    st.header("Help")
    
    with st.expander("Birth Time Entry"):
        st.write("""
        Please select the hour of birth in the hour field, and enter the minute (between 00 and 59) in the minute field.
        
        The time must be given in wrist watch time, as it would have been shown on a normal person's wrist watch at the place of the birth event.
        
        For precise time entry, you can use:
        - MM:SS format (e.g., 23:45 for 23 minutes 45 seconds)
        - MM:SS.ss format (e.g., 23:45.67 for higher precision)
        """)
    
    with st.expander("Unknown Birth Time"):
        st.write("""
        If you don't know the time of birth, you should try to find it in official records.
        
        You can select 'unknown' in the hour field, but only a limited set of calculations will be available.
        """)


if __name__ == "__main__":
    main()


# st.title("Posiciones Planetarias")

# # Agregar un campo de búsqueda de ciudad
# city_name = st.text_input("Buscar ciudad", placeholder="Escribe el nombre de la ciudad")

# # Obtener las coordenadas de la ciudad
# if city_name:
#     latitud, longitud = get_city_coordinates(city_name)
#     if latitud is not None and longitud is not None:
#         st.write(f"Coordenadas de {city_name}: Latitud {latitud:.4f}, Longitud {longitud:.4f}")
#     else:
#         st.write("No se pudo encontrar la ciudad. Inténtalo de nuevo.")
#         latitud, longitud = None, None

# # Agregar un selector de fecha
# min_date = date(1900, 1, 1)
# max_date = date.today()
# fecha = st.date_input("Selecciona una fecha", value=datetime.now().date(), min_value=min_date, max_value=max_date)
# hora = st.time_input("Selecciona una hora", value=datetime.now().time())
# # fecha_hora = datetime.combine(fecha, datetime.min.time(), tzinfo=timezone.utc)
# fecha_hora = datetime.combine(fecha, hora, tzinfo=timezone.utc)

# # Botón para generar el reporte
# if st.button("Generar Reporte") and latitud is not None and longitud is not None:
#     nombre_archivo = 'posiciones_planetarias.txt'
#     posiciones = calcular_posiciones_planetarias(fecha_hora, latitud, longitud, nombre_archivo)

#     st.write(f"Los resultados se han guardado en '{nombre_archivo}'")

#     for cuerpo, datos in posiciones.items():
#         st.write(f"{cuerpo.capitalize()}: en {datos['signo']} a {datos['grados']:.2f}°")


# Ejemplo de uso
# fecha = datetime(1994, 4, 18, 4, 0, 0)  # 18 de octubre de 2024 a las 12:00 UTC
# latitud = 40.7128  # Nueva York
# longitud = -74.0060
# nombre_archivo = 'posiciones_planetarias.txt'

# posiciones = calcular_posiciones_planetarias(fecha, latitud, longitud, nombre_archivo)

# # Imprimir confirmación
# print(f"Los resultados se han guardado en '{nombre_archivo}'")

# for cuerpo, datos in posiciones.items():
#     print(f"{cuerpo.capitalize()}: en {datos['signo']} a {datos['grados']:.2f}°")
#     # print(f"  Signo: {datos['signo']}")
#     # print(f"  Grados: {datos['grados']:.2f}°")
#     # print(f"  Altitud: {datos['altitud']:.2f}°")
#     # print(f"  Azimut: {datos['azimut']:.2f}°")
#     print()