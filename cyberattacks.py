import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import matplotlib as mpl

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import os

import time
from datetime import datetime, timedelta

#import threading

from descartes import PolygonPatch

import pandas as pd
import geopandas as gpd

mpl.rcParams['toolbar'] = 'None'
style.use('fivethirtyeight')

fig = plt.figure("Cyberattacks visualization", figsize=(12, 6))
ax1 = fig.add_subplot(1,1,1)

ax1.get_xaxis().set_visible(False)

ax1.get_yaxis().set_visible(False)

username = os.environ["usr"]

password = os.environ["pass"]

URL = "https://"+ username + ":" + password + "@193.225.251.220:64297/map/"

def getBrowser():
    chrome_options = Options()
    #chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')

    # initialize the Chrome driver
    driver = webdriver.Chrome(chrome_options, keep_alive=True)
    

    driver.get(URL)

    time.sleep(10)

    return driver

driver = getBrowser()
print("Driver is ready!")
def getData(driver_):

    driver = driver_
    while True:
            
        time.sleep(10)

        table = driver.find_element(By.XPATH, '//*[@id="live-attacks-table"]')

        soup = BeautifulSoup(table.get_attribute('outerHTML'), "html.parser")
        #driver.refresh()
        table_headers = []
        for th in soup.find_all('th'):
            table_headers.append(th.text)

        table_data = []
        for row in soup.find_all('tr'):
            columns = row.find_all('td')
            output_row = []
            for column in columns:
                output_row.append(column.text)
            table_data.append(output_row)
        
        
        if len(table_data) < 2:
            return []
        
        df = pd.DataFrame(table_data, columns=table_headers)
        
        df = df[df["Country"] != None]
        
        df["Events"] = df["Events"].astype("datetime64[ms]")
        
        current_time = datetime.now()

        # Define a time threshold (90 seconds)
        time_threshold = current_time - timedelta(seconds=90)

        # Filter the DataFrame
        filtered_df = df[df['Events'] > time_threshold]


        if len(filtered_df) > 0:
            break
    print(len(filtered_df))
    
    return filtered_df["Country"].values


datas = list()
index = -1

def GetCountries():
    global datas
    global index

    if index == len(datas) - 1:
        
        datas = getData(driver)

        if len(datas) == 0:
            return None
        index = 0
        return datas[index]
    elif len(datas) == 0:
        datas = getData(driver)
        if len(datas) == 0:
            return None
        index = 0
        return datas[index]
    else:
        
        index += 1

        return datas[index]

def display(countries):

    for country in countries:
        worldmap.plot(color="lightgrey", ax=ax1)
        plotCountryPatch(ax1, country, 'red')


def plotCountryPatch( axes, country_name, fcolor ):
    # plot a country on the provided axes
    #print(country_name)
    nami = worldmap[worldmap.name == country_name]
    namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
    if len(namigm) == 0:
        print(country_name)
    namig0 = {'type': namigm[0]['geometry']['type'], \
              'coordinates': namigm[0]['geometry']['coordinates']}
    color = PolygonPatch( namig0, fc=fcolor, ec="black", alpha=0.85, zorder=2 )
    axes.add_patch(color)
    
worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

def init_map():
    
    worldmap.plot(color="lightgrey", ax=ax1)   


x = 2

def map_(i):
    global country_text
    global x
    global ax1
    
    if x == 1:
        
        worldmap.plot(color="lightgrey", ax=ax1)
        budapest_coords = (47.4979, 19.0402)

        # Add a map marker for Budapest
        #plt.scatter(budapest_coords[1], budapest_coords[0], color='blue', marker='x')

        if len(ax1.patches) > 0:
        
            ax1.patches[0].remove()
        
        if len(ax1.texts) > 0:
            ax1.texts[0].remove()
        
        x = 2
        
    else:
        
        
        country = GetCountries()
        
        if country != None:
            
            
            countries_dict = {
                "The Netherlands" : "Netherlands",
                "United States": "United States of America", 
                "Republic of Moldova" : "Moldova", 
                "Seychelles" : "Madagascar", 
                "Bosnia and Herzegovina" : "Bosnia and Herz.", 
                "Swaziland" : "South Africa", 
                "Singapore" : "Malaysia",
                "Republic of Korea" : "South Korea",
                "Mauritius" : "Madagascar",
                "Hong Kong" : "China"
            }


            for key in countries_dict.keys():
                country = country.replace(key, countries_dict[key])

            worldmap.plot(color="lightgrey", ax=ax1)
            

            # Add a map marker for Budapest
            #budapest_coords = (47.4979, 19.0402)
            #plt.scatter(budapest_coords[1], budapest_coords[0], color='blue', marker='x', label='Budapest')

            #print(country)
            plotCountryPatch(ax1, country, 'red')
            ax1.text(2.5, -106.5, country, ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
            #plt.scatter(-10, 20, color= "red")

        x = 1


ani = animation.FuncAnimation(fig, map_, interval=2000, init_func=init_map)
plt.show()
