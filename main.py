import os
import json
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import logging

# --- Configuración ---
API_KEY = "07bd5df1f8bc9fa2515402b995f8a8cb" 
CITY = "Detroit" 
UNITS = "metric"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
CSV_FILE = "clima-detroit-hoy.csv" 
LOG_FILE = "output.log"
PLOT_DIR = "weather-site/content/images"

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[
    logging.FileHandler(LOG_FILE, mode='a'),
    logging.StreamHandler()
])

def get_weather_data(city, api_key, units):
    """Obtiene los datos del clima de la API de OpenWeatherMap."""
    try:
        logging.info(f"Obteniendo datos del clima para {city}...")
        params = {
            'q': city,
            'appid': api_key,
            'units': units
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # Lanza un error para códigos de estado HTTP 4xx/5xx
        data = response.json()

        # Extrae los datos relevantes
        dt_utc = datetime.utcfromtimestamp(data['dt'])
        
        filtered_data = {
            'dt': dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
            'coord_lon': data['coord']['lon'],
            'coord_lat': data['coord']['lat'],
            'weather_0description': data['weather'][0]['description'],
            'main_temp': data['main']['temp'],
            'main_feels_like': data['main']['feels_like'],
            'main_temp_min': data['main']['temp_min'],
            'main_temp_max': data['main']['temp_max'],
            'main_pressure': data['main']['pressure'],
            'main_humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'wind_deg': data['wind']['deg'],
            'clouds_all': data['clouds']['all'],
            'city': data['name'],
            'cod': data['cod']
        }
        return filtered_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al conectar con la API: {e}")
        return None
    except KeyError as e:
        logging.error(f"Error al procesar los datos de la API. Falta la clave: {e}")
        logging.error(f"Respuesta completa: {response.text}")
        return None

def save_to_csv(data, filename):
    """Guarda los datos en un archivo CSV."""
    if data is None:
        return

    df_new_row = pd.DataFrame([data])
    
    if not os.path.exists(filename):
        df_new_row.to_csv(filename, index=False)
        logging.info(f"Datos añadidos a '{filename}'. Filas totales: {len(df_new_row)}")
    else:
        df_existing = pd.read_csv(filename)
        df_combined = pd.concat([df_existing, df_new_row], ignore_index=True)
        df_combined.to_csv(filename, index=False)
        logging.info(f"Datos añadidos a '{filename}'. Filas totales: {len(df_combined)}")

def generate_plots(df, plot_dir):
    """Genera y guarda las gráficas de los datos."""
    if df.empty:
        logging.warning("No hay datos en el DataFrame para generar las gráficas.")
        return

    os.makedirs(plot_dir, exist_ok=True)

    # Gráfica 1: Temperatura vs. Tiempo
    try:
        df['dt'] = pd.to_datetime(df['dt'])
        plt.figure(figsize=(10, 6))
        plt.plot(df['dt'], df['main_temp'], marker='o', linestyle='-', color='b')
        plt.title('Temperatura vs. Tiempo')
        plt.xlabel('Tiempo')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plot_path = os.path.join(plot_dir, 'temperature.png')
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Gráfica de temperatura guardada en {plot_path}")
    except Exception as e:
        logging.error(f"Error al generar la gráfica de temperatura: {e}")

    # Gráfica 2: Humedad vs. Tiempo
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(df['dt'], df['main_humidity'], marker='o', linestyle='-', color='g')
        plt.title('Humedad vs. Tiempo')
        plt.xlabel('Tiempo')
        plt.ylabel('Humedad (%)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plot_path = os.path.join(plot_dir, 'humidity.png')
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Gráfica de humedad guardada en {plot_path}")
    except Exception as e:
        logging.error(f"Error al generar la gráfica de humedad: {e}")
        
    # Gráfica 3: Frecuencia de Descripciones del Clima (Opcional)
    try:
        plt.figure(figsize=(10, 6))
        df['weather_0description'].value_counts().plot(kind='bar')
        plt.title('Frecuencia de Descripciones del Clima')
        plt.xlabel('Descripción del Clima')
        plt.ylabel('Frecuencia')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plot_path = os.path.join(plot_dir, 'optional_plot.png')
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Gráfica de frecuencia de descripciones guardada en {plot_path}")
    except Exception as e:
        logging.error(f"Error al generar la gráfica de frecuencia: {e}")

if __name__ == "__main__":
    weather_data = get_weather_data(CITY, API_KEY, UNITS)
    save_to_csv(weather_data, CSV_FILE)
    
    # Después de guardar, lee el CSV completo para generar las gráficas
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        generate_plots(df, PLOT_DIR)


