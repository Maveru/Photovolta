import pandas as pd
import pvlib

# Definir ubicación del panel solar
latitude = 40.546778
longitude = -3.634431
tz = 'Europe/Madrid'

# Definir los datos meteorológicos
date = pd.date_range(start='2023-03-01 08:00:00', end='2023-03-01 19:00:00', freq='5min', tz=tz)
data = pd.DataFrame({'dni': [1000]*len(date),
                     'dhi': [100]*len(date),
                     'airmass_relative': [2]*len(date),
                     'temp_air': [25]*len(date),
                     'wind_speed': [5]*len(date)}, index=date)

# Crear objeto Location
site = pvlib.location.Location(latitude, longitude, tz=tz)

# Obtener la irradiación en un panel solar
solpos = site.get_solarposition(date)
dni_extra = pvlib.irradiance.get_extra_radiation(date)
total_irrad = pvlib.irradiance.get_total_irradiance(surface_tilt=0, surface_azimuth=180, 
                                                    solar_zenith=solpos['apparent_zenith'], 
                                                    solar_azimuth=solpos['azimuth'], 
                                                    dni=data['dni'], ghi=data['dni']+data['dhi'], 
                                                    dhi=data['dhi'], dni_extra=dni_extra, 
                                                    airmass=data['airmass_relative'], 
                                                    albedo=0.2, model='isotropic')
# Calcular la irradiación directa en el plano del panel solar
# Calcular la irradiación global sumando la componente directa y difusa
poa_global = total_irrad['poa_direct'] + total_irrad['poa_diffuse']

# Agregar una columna de fecha para poder agrupar los datos por día
data['fecha'] = data.index.date
# Agrupar los datos por día y obtener la media de la poa_global y poa_directa
daily_mean = data.groupby('fecha').mean()[['dni', 'dhi']]
print(total_irrad)

print(poa_global.sum())
print(poa_global.mean())

total_daily_irradiation = poa_global.sum() / 2
print(f"Irradiancia solar total diaria: {total_daily_irradiation:.2f} kWh/m^2")
