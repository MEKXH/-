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

world = gpd.read_file(r'G:\【立方数据学社】广东省\用来提取数据的行政区划数据_来源于数读城事\全国面.shp')
df = pd.read_excel(r"C:\Users\szu\Desktop\危险系数表.xlsx")
death_rate = pd.read_excel(r"C:\Users\szu\Desktop\全球死亡率.xlsx",sheet_name="Sheet1")
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
            fr"E:\逐年数据\全国范围的数据\tif格式的数据\数据\{year}.tif",
            True,
        )
        pop, pop_meta = clip(gdf, fr'E:\柳叶刀-中国PM2.5公平性以及健康负担研究\CHN_ppp_{year}_1km_Aggregated.tif', False, pm25.shape[0], pm25.shape[1])

        save_to = fr"E:\CHN过早死亡率\{year}\{region}"
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

import os
import rasterio
import rasterio.merge
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib.font_manager as fm
import pandas as pd
from matplotlib.ticker import FormatStrFormatter

for year in range(2000, 2020):
    for index, type in enumerate(["COPD", "LNC", "LRI", "IHD", "STR"]):
        dirs = os.listdir(fr"E:\CHN过早死亡率\{year}")
        tifs = [fr"E:\CHN过早死亡率\{year}\{dir}\{type}.tif" for dir in dirs if os.path.exists(fr"E:\CHN过早死亡率\{year}\{dir}\{type}.tif")]
        src_files_to_mosaic = [rasterio.open(tif) for tif in tifs]
        dest, out_transform = rasterio.merge.merge(src_files_to_mosaic)
        out_meta = src_files_to_mosaic[0].meta.copy()
        out_meta.update({"driver": "GTiff", "height": dest.shape[1], "width": dest.shape[2], "transform": out_transform})
        with rasterio.open(fr"E:\CHN过早死亡率\{year}\{type}.tif", "w", **out_meta) as out:
            out.write(dest)
            print(f"{year} {type} 合并完成")

#
from osgeo import gdal
import numpy as np
for year in range(2000, 2020):
    # 输入文件名
    input_files = [fr'E:\CHN过早死亡率\{year}\COPD.tif', fr'E:\CHN过早死亡率\{year}\LNC.tif', fr'E:\CHN过早死亡率\{year}\LRI.tif', fr'E:\CHN过早死亡率\{year}\IHD.tif', fr'E:\CHN过早死亡率\{year}\STR.tif']
    output_file = fr'E:\CHN过早死亡率\{year}\合并new.tif'

    # 打开第一个输入文件，获取基本信息
    ds = gdal.Open(input_files[0])
    rows = ds.RasterYSize
    cols = ds.RasterXSize
    bands = ds.RasterCount

    # 创建一个数组来存储累加的像素值
    sum_array = np.zeros((rows, cols), dtype=np.float32)

    # 逐个打开输入文件并将像素值相加
    for file in input_files:
        ds = gdal.Open(file)
        band = ds.GetRasterBand(1)
        data = band.ReadAsArray()
        sum_array += data

    # 创建输出文件
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_file, cols, rows, 1, gdal.GDT_Float32)
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(sum_array)

    # 设置地理参考信息和投影信息
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())
    # 关闭文件
    out_band = None
    out_ds = None
    print(f"--------{year}合并完成---------")