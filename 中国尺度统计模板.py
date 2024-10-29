import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime
from rasterio.mask import mask
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.integrate import simps

with rasterio.open(
        fr'.tif') as src:
    raster_geom = src.bounds

# 读取全球矢量数据
world = gpd.read_file(fr'.shp')
# 裁剪矢量数据以匹配栅格数据的范围
world_countries = world.cx[raster_geom.left:raster_geom.right, raster_geom.bottom:raster_geom.top]
if not os.path.exists('中国人口-省尺度.csv'):
    with open('中国人口-省尺度', 'w') as f:
        f.write('country,year,death\n')

if not os.path.exists('logs.txt'):
    with open('logs.txt', "w") as f:
        f.write("")
def print_and_log(s):
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=8)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    s = f"[{now}] {s}"
    print(s)
    with open("logs.txt", "a") as f:
        f.write(s + "\n")
for year in range(2000, 2020):
    print_and_log(f"-----{year}------")
    # PM2.5栅格
    # pm = fr'C:\Users\szu\Desktop\人口尺度\Pm_{year}.tif'
    pp = fr'.tif'
    with rasterio.open(pp) as src:
        for index, country in world_countries.iterrows():
            country_name = country['省']
            print_and_log(f"正在处理: {country_name}")
            # 使用mask函数提取特定国家的栅格数据
            out_image, out_transform = mask(src, [country['geometry']], crop=True)
            print_and_log("mask1")  # 8s
            # 创建DataFrame
            df = pd.DataFrame({'Population': out_image.flatten()},
                              copy=False)
            # df = df[(df['Concentration'] < 20000) & (df['pp'] < 200000) & (df['pp'] > 0)]
            pop = df['Population'].sum()
            print(pop)
            with open("中国人口-省尺度.csv", "a") as f:
                f.write(f"{country_name},{year},{pop}\n")
            del df