
# -*- coding = utf-8 -*-
# @Author ：XIA
# @Time : 2024/9/10 18:57
# @File : 调用R包计算Gini.py
# @Software : PyCharm
import os
import rasterio
import numpy as np
import geopandas as gpd
from datetime import datetime
from rasterio.mask import mask
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from scipy.integrate import simps
# from gini_decomp_R import calculate_gini_decomp
import pandas as pd
from datetime import datetime
from rasterio.mask import mask
from datetime import timedelta
pd.set_option('display.max_columns', None)

if not os.path.exists('.csv'):
    with open('', 'w') as f:
        f.write('country,a,year\n')

if not os.path.exists('logs.txt'):
    with open('logs.txt', "w") as f:
        f.write("")

with rasterio.open(
        fr'') as src:
    raster_geom = src.bounds

# # 读取全球矢量数据
world = gpd.read_file(fr'.shp')
# 裁剪矢量数据以匹配栅格数据的范围
world_countries = world.cx[raster_geom.left:raster_geom.right, raster_geom.bottom:raster_geom.top]
# world = gpd.read_file(r'C:\Users\szu\Desktop\数据\world_adm0_Project.shp')
#
# world_countries = world.cx[raster_geom.left:raster_geom.right, raster_geom.bottom:raster_geom.top]
# if world.crs != target_crs:
#     world = world.to_crs(target_crs)



def print_and_log(s):
    now_utc = datetime.utcnow()
    now = now_utc + timedelta(hours=8)
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    s = f"[{now}] {s}"
    print(s)
    with open("logs.txt", "a") as f:
        f.write(s + "\n")

if not os.path.exists('logs.txt'):
    with open('logs.txt', "w") as f:
        f.write("")

def calculate_concentration_index1(data, exposure_col, income_col):
    data_sorted = data.sort_values(by=income_col)
    N = len(data_sorted)
    mu = data_sorted[exposure_col].mean()
    data_sorted['cumulative_rank'] = data_sorted['rank'] / N
    if mu == 0 or N == 0:
        C = 0
    else:
        C = (2 / (mu * N)) * (data_sorted[exposure_col] * data_sorted['cumulative_rank']).sum() - (1 + 1/N)
    data_sorted['cumulative_exposure'] = data_sorted[exposure_col].cumsum()
    data_sorted['cumulative_exposure_share'] = data_sorted['cumulative_exposure'] / data_sorted[exposure_col].sum()
    # display(data_sorted)
    # return C

    return C, data_sorted['cumulative_rank'], data_sorted['cumulative_exposure_share']


def plot_multiple_curves(data_list, labels, colors):
    plt.figure(figsize=(8, 6))
    for data, label, color in zip(data_list, labels, colors):
        C, cumulative_rank, cumulative_exposure_share = data
        plt.plot(cumulative_rank, cumulative_exposure_share, label=f'{label} (C: {C:.4f})', color=color)
    plt.plot([0, 1], [0, 1], linestyle='--', color='black')
    plt.title('pm2.5 vs gdp')
    plt.xlabel('Cumulative Share of Population by gdp-state')
    plt.ylabel('Cumulative Share of Death')
    plt.legend()
    plt.grid(False)
    plt.savefig("C:/Users/szu/Desktop/CHN_图/低收入发展中国家2-过早死亡CI(前后百分之30)1.jpg", dpi=800)
    # plt.show()

def calculate_concentration_index(data, exposure_col, income_col):
    data_sorted = data.sort_values(by=income_col)
    N = len(data_sorted)
    data_sorted['rank'] = np.arange(1, N + 1)
    mu = data_sorted[exposure_col].mean()
    data_sorted['cumulative_rank'] = data_sorted['rank'] / N
    if mu == 0 or N == 0:
        C = 0
    else:
        C = (2 / (mu * N)) * (data_sorted[exposure_col] * data_sorted['cumulative_rank']).sum() - (1 + 1/N)

    data_sorted['cumulative_exposure'] = data_sorted[exposure_col].cumsum()
    data_sorted['cumulative_exposure_share'] = data_sorted['cumulative_exposure'] / data_sorted[exposure_col].sum()
    #display(data_sorted)
    return C

    # return C, data_sorted['cumulative_rank'], data_sorted['cumulative_exposure_share']

def gini_coef(array):
    """计算基尼系数"""
    array = np.sort(array)  # 值从小到大排序
    index = np.arange(1, array.shape[0] + 1)  # 创建索引数组
    n = array.shape[0]  # 数组长度
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


# df5 = pd.DataFrame(columns=['GDP', 'PP', 'DEATH'])
# df6 = pd.DataFrame(columns=['GDP', 'PP', 'DEATH'])
# df7 = pd.DataFrame(columns=['GDP', 'PP', 'DEATH'])
# df8 = pd.DataFrame(columns=['GDP', 'PP', 'DEATH'])
# df9 = pd.DataFrame(columns=['GDP', 'PP', 'DEATH'])
fig, ax = plt.subplots(figsize=(8, 6))
dict = {"2001": 'blue',"2005": 'red',"2010": 'green',"2013": 'orange',"2015": 'yellow',"2019":'purple'}
for year in [2001,2005,2010,2013,2015,2019]:
    df2 = pd.DataFrame(columns=['GDP', 'PP', 'DEATH'])
    print_and_log(f"-----{year}------")
    # PM2.5栅格
    pm = fr'.tif'
    pp = fr'.tif'
    GDP = fr'.tif'
    with rasterio.open(pm) as src, rasterio.open(pp) as src1, rasterio.open(GDP) as src2:
        for index, country in world_countries.iterrows():
            country_name = country['省']
            print_and_log(f"正在处理: {country_name}")
            # 使用mask函数提取特定国家的栅格数据
            out_image, out_transform = mask(src, [country['geometry']], crop=True)
            print_and_log("mask1")  # 8s
            out_image1, out_transform1 = mask(src1, [country['geometry']], crop=True)
            print_and_log("mask2")
            out_image2, out_transform2 = mask(src2, [country['geometry']], crop=True)
            print_and_log("mask3")
            shape1 = out_image1.shape
            shape2 = out_image.shape
            shape3 = out_image2.shape
            # 计算最小尺寸
            min_shape = tuple(min(dim1, dim2,dim3) for dim1, dim2,dim3 in zip(shape1, shape2, shape3))
            # 调整数组尺寸
            out_image = out_image[:min_shape[0], :min_shape[1], :min_shape[2]]
            out_image1 = out_image1[:min_shape[0], :min_shape[1], :min_shape[2]]
            out_image2 = out_image2[:min_shape[0], :min_shape[1], :min_shape[2]]
            # print(out_image1.shape, out_image.shape)
            list = out_image.flatten().tolist()
            list1 = out_image1.flatten().tolist()
            list2 = out_image2.flatten().tolist()
            # print(len(list1), len(list))
            # 创建DataFrame
            df1 = pd.DataFrame({'GDP':list2,'PP': list1, 'DEATH': list},
                              copy=False)
            del out_image, out_image1, out_transform, out_transform1, list, list1, out_image2, out_transform2,list2
            df1 = df1[(df1['GDP'] > 0) & (df1['PP'] > 0)]

            # df1['PP'] = df1['PP']/10
            # df1['DEATH'] = df1['DEATH']/df1['PP']
            # df1['PP'] = df1['PP'].apply(np.ceil)  # 向上取整 确保不是0

            # print(df2)
            # 调整到一个人一条数据的形式
            # df1 = df1.loc[df1.index.repeat(df1['PP'])].reset_index(drop=True)

            # df1['pp'] = (df1['pp']).astype(int)
            # print(df1)
            # print(fr'{index}')
            df2 = pd.concat([df2,df1],ignore_index=True)
            print(len(df2))
            del df1
        # df3 = df2.groupby('GDP')
        # print(df3)
        df2['DEATH'] = df2['DEATH'] / df2['PP']
        df2['PP'] = df2['PP']/3
        df2['PP'] = df2['PP'].apply(np.ceil)  # 向上取整 确保不是0
        # # print(df2)
        # # 调整到一个人一条数据的形式
        df_expanded = df2.loc[df2.index.repeat(df2['PP'])].reset_index(drop=True)
        df_expanded = df_expanded.sort_values(by='GDP')
        print('调整到一个人一条数据的形式，取代PP列', df_expanded)
        # df_expanded.to_csv('df_expanded.csv')
        df_expanded.drop(columns=['PP'], inplace=True)
        df_expanded['Weight'] = 1
        print('去掉pp列，剩下的分别是按GDP排序好的个体(x)，以及DEATH(y)', df_expanded)
        sum = df_expanded['DEATH'].sum()
        top_30_percent_count = int(len(df_expanded) * 0.3)
        top_10_percent_count = int(len(df_expanded) * 0.1)
        # 获取前百分之30的数据
        df6 = df_expanded.iloc[:top_30_percent_count]
        df7 = df_expanded.iloc[-top_30_percent_count:]
        q = df6['DEATH'].sum() / sum
        f = df7['DEATH'].sum() / sum
        print(q,f)
        df8 = df_expanded.iloc[:top_10_percent_count]
        df9 = df_expanded.iloc[-top_10_percent_count:]
        q1 = df8['DEATH'].sum() / sum
        f1 = df9['DEATH'].sum() / sum
        print(q1,f1)
        # 画图
        # df_expanded = df_expanded.sort_values(by='GDP')
        # 计算人口累计百分比
        cumulative_rank = np.cumsum(df_expanded['Weight']) / np.sum(df_expanded['Weight'])
        # 计算DEATH累计百分比
        cumulative_percentage_extra = np.cumsum(df_expanded['DEATH']) / np.sum(df_expanded['DEATH'])
        # 计算CI指数
        num = len(df_expanded)
        mu = df_expanded['DEATH'].mean()
        if mu == 0 or num == 0:
            C = 0
        else:
            C = (2 / (mu * num)) * (df_expanded['DEATH'] * cumulative_rank).sum() - (1 + 1 / num)
        print(C)
        # with open("动植物.csv", "a") as f:
        #     f.write(f"{country_name},{year},{C}\n")
        #绘制折线散点图
        ax.plot(cumulative_rank, cumulative_percentage_extra, linestyle='-', color=dict[fr'{year}'], label=f'{year} (C: {C:.4f})')
        ax.plot([0, 1], [0, 1], linestyle='--', color='black')
        del df2
        # df['GDP'] = (df['GDP']).astype(int)
        # df2 = df.groupby('GDP').sum()
        # print(df2)
        # df2.to_csv('发达out2000.csv', index=False)
        # value = calculate_concentration_index1(df, 'DEATH', 'GDP')
        # plot_multiple_curves([value],
        #                      ['2019'],
        #                      ['purple'])
        # df2['GDP'] = (df2['GDP']).round(3)
        # df2 = df2.groupby('GDP').sum()
        # print(df2)
        # df2.to_csv(fr'低收入发展中{year}.csv', index=False)
plt.legend()
plt.savefig(".jpg", dpi=800)
# value = calculate_concentration_index1(df5, 'DEATH', 'GDP')
# value1 = calculate_concentration_index1(df6, 'DEATH', 'GDP')
# value2 = calculate_concentration_index1(df7, 'DEATH', 'GDP')
# value3 = calculate_concentration_index1(df8, 'DEATH', 'GDP')
# value4 = calculate_concentration_index1(df9, 'DEATH', 'GDP')
# plot_multiple_curves([value, value1, value2, value3, value4],
#                      ['2001','2005','2010','2015','2019'],
#                      ['blue','red','green','yellow','purple'])
print('ok')