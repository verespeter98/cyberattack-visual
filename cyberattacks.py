import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import matplotlib as mpl

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import time

import threading

from descartes import PolygonPatch

import pandas as pd
import geopandas as gpd

mpl.rcParams['toolbar'] = 'None'
style.use('fivethirtyeight')

fig = plt.figure("Cyberattacks visualization", figsize=(12, 6))
ax1 = fig.add_subplot(1,1,1)

ax1.get_xaxis().set_visible(False)

ax1.get_yaxis().set_visible(False)

URL = "https://threatmap.bitdefender.com/"

def getBrowser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # initialize the Chrome driver
    driver = webdriver.Chrome(chrome_options)

    return driver


def getData():

    driver = getBrowser()

    driver.get(URL)

    time.sleep(10)

    table = driver.find_element(By.XPATH, "/html/body/footer/div[2]/div/div[2]")

    soup = BeautifulSoup(table.get_attribute('outerHTML'), "html.parser")
    
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
    
    df = pd.DataFrame(table_data, columns=table_headers)
    
    df = df[df["Attack country"] != None]
    
    driver.quit()
    
    #print(df["Attack country"].values)
    
    return df["Attack country"].values

data_index = 0
datas = [
    getData(), 
    []
]
index = -1

def load_next_data():
    global data_index
    
    datas[(data_index+1)%2] = getData()

thread = threading.Thread(target=load_next_data)
thread.start()

def GetCountries():
    global data
    global index
    global data_index
    global thread
    #print(len(data) - 1)
    if index == len(datas[data_index]) - 1:
        if thread.is_alive():

            thread.join()
        
        data_index=(data_index+1)%2
        index = 0
        thread = threading.Thread(target=load_next_data)
        thread.start()
        return datas[data_index][index]
    else:
        
        index += 1

        return datas[data_index][index]



def display(countries):

    for country in countries:
        worldmap.plot(color="lightgrey", ax=ax1)
        plotCountryPatch(ax1, country, 'red')


def plotCountryPatch( axes, country_name, fcolor ):
    # plot a country on the provided axes
    #print(country_name)
    nami = worldmap[worldmap.name == country_name]
    namigm = nami.__geo_interface__['features']  # geopandas's geo_interface
    namig0 = {'type': namigm[0]['geometry']['type'], \
              'coordinates': namigm[0]['geometry']['coordinates']}
    color = PolygonPatch( namig0, fc=fcolor, ec="black", alpha=0.85, zorder=2 )
    axes.add_patch(color)
    
worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

def init_map():
    
    worldmap.plot(color="lightgrey", ax=ax1)   


x = 2
def map_(i):
    
    global x
    
    if x == 1:
        
        worldmap.plot(color="lightgrey", ax=ax1)
        if len(ax1.patches) > 0:
        
            ax1.patches[0].remove()
        #color.remove()
        x = 2
        
    else:
        
        
        country = GetCountries()
        
        if country != None:
            
            
            countries_dict = {
                "United States": "United States of America", 
                "Republic of Moldova" : "Moldova", 
                "Seychelles" : "Madagascar", 
                "Bosnia and Herzegovina" : "Bosnia and Herz.", 
                "Swaziland" : "South Africa", 
                "Singapore" : "Malaysia",
                "Republic of Korea" : "South Korea",
                "Mauritius" : "Madagascar",
            }


            for key in countries_dict.keys():
                country = country.replace(key, countries_dict[key])


            

            #print(df)
            
            #country = "Hungary"
            # Creating axes and plotting world map
            #fig, ax = plt.subplots(figsize=(12, 6))
            worldmap.plot(color="lightgrey", ax=ax1)
            plotCountryPatch(ax1, country, 'red')

            #plt.scatter(-10, 20, color= "red")

        x = 1


ani = animation.FuncAnimation(fig, map_, interval=1000, init_func=init_map)
plt.show()
