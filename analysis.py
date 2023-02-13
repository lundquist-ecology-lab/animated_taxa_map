# Analysis of insects from the genus *Hydropsyche*
# over time in relation to urban centers and urbanization.

# Data collected from [INHS Insect Collection Database](http://inhsinsectcollection.speciesfile.org/InsectCollection.aspx) (see inh_scraper.py)
# and then cleaned manually

# Note: can be modified to produce map of other genera (e.g. *Baetis*)

# Import data

#%%
import pandas as pd

# load data file

# Y needs to be continuous and needs to be organized into > two X groups.

hyd = pd.read_csv("cleaned_data/Hydropsyche.csv")
hyd.columns = hyd.columns.str.replace(".","_", regex=False)

#%%

import pandas as pd
import numpy as np

years = np.array(hyd['Year'])
years = np.unique(years)
years = years[years != "\xa0"]
print(years)

country = np.array(hyd['Country'])
country = np.unique(country)
country = country[country != "\xa0"]
print(country)

state = np.array(hyd['State'])
state = np.unique(state)
state = state[state != "\xa0"]
print(state)

county = np.array(hyd['County'])
county = np.unique(county)
county = county[county != "\xa0"]
print(county)

localities = np.array(hyd['Locality'])
localities = np.unique(localities)
localities = localities[localities != "\xa0"]
print(localities)

present = []
local = []
yrs = []
state = []
nation = []
lat = []
lon = []
genus = []

#%%
for year in years:
    for locality in localities:
        x = hyd['Genus'][(hyd['Year'] == year) & (hyd['Locality'] == locality)].unique()
        if len(x) != 0:
                present.append(1)
                local.append(locality)
                yrs.append(year)
                nation.append(hyd['Country'][hyd['Locality'] == locality].iloc[0])
                state.append(hyd['State'][hyd['Locality'] == locality].iloc[0])
                lat.append(hyd['Latitude'][hyd['Locality'] == locality].iloc[0]) 
                lon.append(hyd['Longitude'][hyd['Locality'] == locality].iloc[0])
                genus.append('Hydropsyche') 
        else:
            present.append(0)
            local.append(locality)
            yrs.append(year)
            nation.append(hyd['Country'][hyd['Locality'] == locality].iloc[0])
            state.append(hyd['State'][hyd['Locality'] == locality].iloc[0])
            lat.append(hyd['Latitude'][hyd['Locality'] == locality].iloc[0]) 
            lon.append(hyd['Longitude'][hyd['Locality'] == locality].iloc[0]) 
            genus.append('Hydropsyche') 


data = {'Present' : present,
        'Genus': genus,
        'Locality': local,
        'Years': yrs,
        'Country': nation,
        'State': state,
        'Latitude': lat,
        'Longitude': lon

}

hyd_df = pd.DataFrame(data)

#%%
analysis_df = hyd_df

print(analysis_df.head())

#%%
# analysis_df.to_csv(r'dataframe.csv')

# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.transforms as transforms
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon 

analysis_df["Longitude"] = analysis_df["Longitude"].str.replace('\xa0', '')
analysis_df["Latitude"] = analysis_df["Latitude"].str.replace('\xa0', '')

analysis_df["Longitude"] = analysis_df["Longitude"].replace('', np.nan)
analysis_df["Latitude"] = analysis_df["Latitude"].replace('', np.nan)

analysis_df["Longitude"] = analysis_df["Longitude"].astype(float)
analysis_df["Latitude"] = analysis_df["Latitude"].astype(float)

#%%
county_map = gpd.read_file("map/s_08mr23.shp")

#%%

import fiona

c = fiona.open("map/s_08mr23.shp")

df = analysis_df
crs = c.crs
df.head()

#%%

geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
geometry[:3]

#%%
geo_df = gpd.GeoDataFrame(df, 
                        crs = crs,
                        geometry = geometry)
geo_df.head()

#%%
# Create a list of years
geo_p = geo_df[geo_df['Present'] == 1]
years = geo_p['Years'].unique()

print(years)
#%%

# Initialize the figure and axis
fig, ax = plt.subplots(figsize = (15,15))
county_map.plot(ax = ax, alpha = 0.4, color = "grey")

# Function to update the plot for each frame
def update_plot(i):
    ax.clear()
    county_map.plot(ax = ax, alpha = 0.4, color = "grey")
    geo_p[(geo_p['Years'] == years[i])].plot(ax = ax, markersize = 20, color = "blue", marker = "^", label = "pos")
    ax.set_xlim(-130, -60)
    ax.set_ylim(20, 50)
    ax.set_aspect('equal')
    ax.text(-70, 0.1, "Year: " + years[i], transform = transforms.blended_transform_factory(ax.transData, ax.transAxes), fontsize = 20, ha = "center")
    return ax

# Create the animation using FuncAnimation
ani = animation.FuncAnimation(fig, update_plot, frames = len(years), interval = 2000, repeat = False)

# Writer and file name
Writer = animation.writers['ffmpeg']
writer = Writer(fps=1, metadata=dict(artist='Me'), bitrate=1800)

# Save the animation to an mp4 file
ani.save('animation.mp4', writer = writer)
#%%