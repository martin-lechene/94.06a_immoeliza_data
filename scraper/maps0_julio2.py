import folium
import pandas as pd
from folium.plugins import FastMarkerCluster
from folium.plugins import HeatMap


data = pd.read_csv('data/property_data_1402.csv', sep=',')

data.head(5000)

map = folium.Map(location=[50.850346, 4.351721], zoom_start=10)

last_location_add = []

for index, row in data.iterrows():

    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        color = 'black'
        icon = 'house'
        if row['Type of property'] == 'APARTMENT':
            icon = 'building'

        if row['Price'] > 800000:

            coords = [row['Latitude'], row['Longitude']]
            folium.Marker(coords, tooltip="Click for More", popup=(f"Price:{row['Price']}"
                                                                   f"\nEnergy:{row['Energy Level']}"
                                                                   f"\nPostal:{row['Postal code']}"
                                                                   f"\nRoom:{row['Number of Rooms']}"
                                                                   f"\nSurface:{row['Surface of good']}"
                                                                   f"\nTaxes:{row['Taxes Year']}"),
                          icon=folium.Icon(icon=icon, prefix='fa', color=color)).add_to(map)

        last_location_add = row['Latitude'], row['Longitude']

map.location = last_location_add
map.show_in_browser()


'''
map2 = folium.Map(location=[50.850346, 4.351721], zoom_start=10)

latitudes = []
longitudes = []
for index, row in data.iterrows():
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        latitudes.append(row['Latitude'])
        longitudes.append(row['Longitude'])


FastMarkerCluster(data=).add_to(map2)
map2.show_in_browser()




latitudes = []
longitudes = []
for index, row in data.iterrows():
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        latitudes.append(row['Latitude'])
        longitudes.append(row['Longitude'])

# Plot it on the map
HeatMap(list(zip(latitudes, longitudes))).add_to(map2)

# Display the map
map2.show_in_browser()
'''
