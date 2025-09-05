import folium
import pandas as pd

data = pd.read_csv('data/property_data_1402.csv', sep=',')

map = folium.Map(location=[50.850346, 4.351721], zoom_start=10)

last_location_add = []
count = 0
count_red = 0
count_orange = 0
count_green = 0
count_blue = 0
count_apartment = 0
count_black = 0
count_house = 0
for index, row in data.iterrows():
    if row['Province'] == 'Hainaut':
        if row['Price'] <= 200000 or row['Price'] > 800000:
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                color = 'black'
                icon = 'house'
                count += 1
                if row['Price'] <= 800000:
                    color = 'red'
                if row['Price'] <= 600000:
                    color = 'orange'
                if row['Price'] <= 400000:
                    color = 'green'
                if row['Price'] <= 200000:
                    color = 'blue'
                if row['Type of property'] == 'APARTMENT':

                    icon = 'building'

                coords = [row['Latitude'], row['Longitude']]
                folium.Marker(coords, tooltip="Click for More", popup=(f"\nID:{row['Property ID']}"
                                                                       f"\nPrice:{row['Price']}"
                                                                       f"\nEnergy:{row['Energy Level']}"
                                                                       f"\nPostal:{row['Postal code']}"
                                                                       f"\nRoom:{row['Number of Rooms']}"
                                                                       f"\nSurface:{row['Surface of good']}"
                                                                       f"\nTaxes:{row['Taxes Year']}"),
                              icon=folium.Icon(icon=icon, prefix='fa', color=color)).add_to(map)
                if icon == 'building':
                    count_apartment += 1
                if icon == 'house':
                    count_house += 1
                if color == 'blue':
                    count_blue += 1
                if color == 'green':
                    count_green += 1
                if color == 'orange':
                    count_orange += 1
                if color == 'red':
                    count_red += 1
                if color == 'black':
                    count_black += 1

                last_location_add = row['Latitude'], row['Longitude']


print(f"Total of Houses and Apartments: {count}")
print(f"Total of Houses: {count_house}")
print(f"% of Houses: {count_house/count*100:.2f}%")
print(f"Total of Apartments: {count_apartment}")
print(f"% of Apartments: {count_apartment/count*100:.2f}%")

print(f"Total of Houses and Apartments Price less than 200k: {count_blue}")
print(
    f"% of Houses and Apartments Price less than 200k: {count_blue/count*100:.2f}%")

print(f"% of Houses and Apartments Price between 200k to 400k: {count_green}")
print(
    f"Total of Houses and Apartments Price between 200k to 400k: {count_green/count*100:.2f}%")

print(
    f"Total of Houses and Apartments Price between 600k to 800k: {count_orange}")
print(
    f"% of Houses and Apartments Price between 600k to 800k: {count_orange/count*100:.2f}%")

print(
    f"Total of Houses and Apartments Price between 600k to 800k: {count_red}")
print(
    f"% of Houses and Apartments Price between 600k to 800k: {count_red/count*100:.2f}%")

print(f"Total of Houses and Apartments Price More than 800k: {count_black}")
print(
    f"% of Houses and Apartments Price More than 800k: {count_black/count*100:.2f}%")

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
