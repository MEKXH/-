import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.mask import mask

# 读取全球矢量数据
world = gpd.read_file('path/to/country_shapefile.shp')

ssps = {1, 2, 3, 5}

with open("PM25_avg.csv", "a") as f:
    f.write("year,name,weighted_avg_pm2_5\n")

for year in range(2000, 2020):
    print(f"-----{year}------")
    # PM2.5栅格
    with rasterio.open(f'path/to/PM2.5_data/{year}_ALIGNED.tif') as src3:
        raster_geom = src3.bounds

    # 裁剪矢量数据以匹配栅格数据的范围
    world_countries = world.cx[raster_geom.left:raster_geom.right, raster_geom.bottom:raster_geom.top]

    pm = f'path/to/PM2.5_data/{year}_ALIGNED.tif'  # 可替换为DAPP栅格数据
    pp = f'path/to/population_data/CHN_ppp_{year}_1km_Aggregated.tif'

    with rasterio.open(pm) as src, rasterio.open(pp) as src1:
        for index, country in world_countries.iterrows():
            country_name = country['省']
            print(f"正在处理: {year}_PM25")

            # 使用mask函数提取特定国家的栅格数据
            out_image, out_transform = mask(src, [country['geometry']], crop=True, nodata=0)
            out_image1, out_transform1 = mask(src1, [country['geometry']], crop=True, nodata=0)

            pm_data = out_image.flatten()
            pp_data = out_image1.flatten()
            
            list_pm = pm_data.tolist()
            list_pp = pp_data.tolist()
            
            print(len(list_pm), len(list_pp))

            # 创建DataFrame
            df = pd.DataFrame({'Concentration': pm_data[:min(len(list_pm), len(list_pp))], 
                               'Population': pp_data[:min(len(list_pm), len(list_pp))]},
                              copy=False)
            del out_image, out_image1, list_pp, list_pm
            
            df['Population'] = df['Population'].astype(int)
            
            # 筛选出人数和浓度都不为零的行
            df = df[(df['Concentration'] > 0) & (df['Population'] > 0)]

            total_population = np.sum(df['Population'])
            print(f"--{year}--Population is {total_population}\n")
            
            # 计算人口加权PM2.5浓度
            weighted_sum_pm2_5 = np.sum(df['Concentration'] * df['Population'])
            weighted_avg_pm2_5 = weighted_sum_pm2_5 / total_population

            print(f"Year {year} - Population weighted average PM2.5 concentration: {weighted_avg_pm2_5}")

            with open("PM25_avg.csv", "a") as f:
                f.write(f"{year},{weighted_avg_pm2_5}\n")
    
            df = df.groupby('Concentration').sum().reset_index()

            df.to_csv(f'{year}.csv', index=False)

            print(f"分组求和后的df长度为{len(df)}")
            print(f"{year} PM25_df done")
            
            del df
