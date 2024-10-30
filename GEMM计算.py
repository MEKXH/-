import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.mask import mask
from datetime import datetime, timedelta
from rasterio.warp import Resampling




def print_and_log(s):
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=8)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    s = f"[{now}] {s}"
    print(s)
    with open("./result/logs.txt", "a") as f:
        f.write(s + "\n")

world = gpd.read_file(r'.shp')
df = pd.read_excel(r"系数表.xlsx")
death_rate = pd.read_excel(r"\全球死亡率.xlsx",sheet_name="Sheet1")
dicts = {
    "COPD": dict(zip(df["PM2.5"], df["RR_COPD"])),
    "LNC": dict(zip(df["PM2.5"], df["RR_LNC"])),
    "LRI": dict(zip(df["PM2.5"], df["RR_LRI"])),
    "IHD": dict(zip(df["PM2.5"], df["RR_IHD"])),
    "STR": dict(zip(df["PM2.5"], df["RR_STR"])),
}


def clip(gdf, raster, round=False, height=None, width=None):
    with rasterio.open(raster) as src:
        geometries = [geom for geom in gdf.geometry]
        out_image, out_transform = mask(src, geometries, crop=True, nodata=0.0)
        out_image = np.round(out_image[0], 1) if round else out_image[0]

        out_meta = src.meta
        out_meta.update(
            {
                "driver": "GTiff",
                "height": out_image.shape[0],
                "width": out_image.shape[1],
                "transform": out_transform,
                "nodata": 0.0,
            }
        )

        if height and width:
            timestamp = int(datetime.now().timestamp())
            with rasterio.open(fr"E:\CHN过早死亡率\{timestamp}.tif", "w", **out_meta) as dst:
                dst.write(out_image.astype(rasterio.float32), 1)

            out_image = rasterio.open(fr"E:\CHN过早死亡率\{timestamp}.tif")
            out_image = out_image.read(
                out_shape=(height, width),
                resampling=Resampling.bilinear,
            )[0]
            os.remove(fr"E:\CHN过早死亡率\{timestamp}.tif")

        return out_image, out_meta


def process_type(type):
    dict = dicts[type]

    def f(dict):
        return lambda value: 0.0 if value < 1 else dict.get(round(value, 1), 1)

    return np.vectorize(f(dict))

if not os.path.exists("./result/logs.txt"):
    os.makedirs("./result")
    with open("./result/logs.txt", "w") as f:
        f.write("")

for year in range(2000, 2020):
    print_and_log(f"当前处理：{year} 年")

    for index, row in world.iterrows():
        region = 'China'
        if region in ['Antarctica', 'Jan Mayen', 'Svalbard']:
            continue
        print_and_log(f"地区：{region}")
        gdf = gpd.GeoDataFrame([row])
        pm25, pm25_meta = clip(
            gdf,
            fr".tif",
            True,
        )
        pop, pop_meta = clip(gdf, fr'.tif', False, pm25.shape[0], pm25.shape[1])
        save_to = fr"\{year}\{region}"
        if not os.path.exists(save_to):
            os.makedirs(save_to)

        for index, type in enumerate(["COPD", "LNC", "LRI", "IHD", "STR"]):
            rate = death_rate.loc[
                (death_rate["year"] == year)
                & (death_rate["country"] == region)
                & (death_rate["cause_name"] == type)
            ].values
            rate = rate[0][-1] if len(rate) > 0 else 0.0
            coeffs = process_type(type)(pm25)
            result = coeffs * rate

            with rasterio.open(f"{save_to}/{type}.tif", "w", **pm25_meta) as dst:
                dst.write(result.astype(rasterio.float32), 1)
    print_and_log(f"----- {year} 年处理完成 -----")



#
# def print_and_log(s):
#     now_utc = datetime.utcnow()
#     now = now_utc + timedelta(hours=8)
#     now = now.strftime("%Y-%m-%d %H:%M:%S")
#     s = f"[{now}] {s}"
#     print(s)
#     with open("./result/logs.txt", "a") as f:
#         f.write(s + "\n")
#
#
# world = gpd.read_file(r'C:\Users\szu\Desktop\a\world_adm0_Project.shp')
# df = pd.read_excel(r"C:\Users\szu\Desktop\危险系数表.xlsx")
# death_rate = pd.read_excel(r"C:\Users\szu\Desktop\全球死亡率.xlsx",sheet_name="Sheet1")
# dicts = {
#     "COPD": dict(zip(df["PM2.5"], df["RR_COPD"])),
#     "LNC": dict(zip(df["PM2.5"], df["RR_LNC"])),
#     "LRI": dict(zip(df["PM2.5"], df["RR_LRI"])),
#     "IHD": dict(zip(df["PM2.5"], df["RR_IHD"])),
#     "STR": dict(zip(df["PM2.5"], df["RR_STR"])),
# }
#
#
# def clip(gdf, raster, round=False, height=None, width=None):
#     with rasterio.open(raster) as src:
#         geometries = [geom for geom in gdf.geometry]
#         out_image, out_transform = mask(src, geometries, crop=True, nodata=0.0)
#         out_image = np.round(out_image[0], 1) if round else out_image[0]
#
#         out_meta = src.meta
#         out_meta.update(
#             {
#                 "driver": "GTiff",
#                 "height": out_image.shape[0],
#                 "width": out_image.shape[1],
#                 "transform": out_transform,
#                 "nodata": 0.0,
#             }
#         )
#
#         if height and width:
#             timestamp = int(datetime.now().timestamp())
#             with rasterio.open(fr"E:\全球真实0904\{timestamp}.tif", "w", **out_meta) as dst:
#                 dst.write(out_image.astype(rasterio.float32), 1)
#
#             out_image = rasterio.open(fr"E:\全球真实0904\{timestamp}.tif")
#             out_image = out_image.read(
#                 out_shape=(height, width),
#                 resampling=Resampling.bilinear,
#             )[0]
#             os.remove(fr"E:\全球真实0904\{timestamp}.tif")
#
#         return out_image, out_meta


# def process_type(type):
#     dict = dicts[type]
#
#     def f(dict):
#         return lambda value: 0.0 if value < 1 else dict.get(round(value, 1), 1)
#
#     return np.vectorize(f(dict))
#
#
# if not os.path.exists("./result/logs.txt"):
#     os.makedirs("./result")
#     with open("./result/logs.txt", "w") as f:
#         f.write("")
#
# for year in [2000,2019]:
#     print_and_log(f"当前处理：{year} 年")
#
#     for index, row in world.iterrows():
#         region = row["NAME"]
#         if region in ['Antarctica', 'Jan Mayen', 'Svalbard']:
#             continue
#         print_and_log(f"地区：{region}")
#         gdf = gpd.GeoDataFrame([row])
#         pm25, pm25_meta = clip(
#             gdf,
#             fr"C:\Users\szu\Desktop\PM2.5全球网格\sdei-global-annual-gwr-pm2-5-modis-misr-seawifs-aod-v4-gl-03-{year}.tif",
#             True,
#         )
#         pop, pop_meta = clip(gdf, fr"C:\Users\szu\Desktop\人口数据全球\ppp_{year}_1km_Aggregated.tif", False, pm25.shape[0], pm25.shape[1])
#
#         save_to = fr"E:\全球真实0904\{year}\{region}"
#         if not os.path.exists(save_to):
#             os.makedirs(save_to)
#
#         for index, type in enumerate(["COPD", "LNC", "LRI", "IHD", "STR"]):
#             rate = death_rate.loc[
#                 (death_rate["year"] == year)
#                 & (death_rate["country"] == region)
#                 & (death_rate["cause_name"] == type)
#             ].values
#             rate = rate[0][-1] if len(rate) > 0 else 0.0
#             coeffs = process_type(type)(pm25)
#             result = coeffs * rate * pop * 0.00001
#
#             with rasterio.open(f"{save_to}/{type}.tif", "w", **pm25_meta) as dst:
#                 dst.write(result.astype(rasterio.float32), 1)
#     print_and_log(f"----- {year} 年处理完成 -----")
