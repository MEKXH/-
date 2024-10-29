import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd
from gini_decomp_R import calculate_gini_decomp
import os

pd.set_option('display.max_columns', None)

# 激活 pandas2ri
pandas2ri.activate()

# 导入 R 包
dineq = importr('dineq')

####未来gini计算####
# ssps = {1, 2, 3, 5}
# for ssp in ssps:
#     with open(fr"yourpath\ssp{ssp}_gini1.csv", "a") as f:
#         f.write(f"year,gini_total\n")
#     for year in range(2025, 2050, 5):
#         df = pd.read_csv(fr"yourpath\{year}.csv")
#         df['Country'] = 1

#         result = calculate_gini_decomp(df, 'Concentration', 'Country', 'Population')

#         print(fr"{year}_gini is {result.gini_total[0]}")

#         with open(fr"yourpath\ssp{ssp}_gini1.csv", "a") as f:
#             f.write(f"{year},{result.gini_total[0]}\n")

####历史gini计算####

# # 激活 pandas2ri
# pandas2ri.activate()

# # 导入 R 包
# dineq = importr('dineq')

# # 主文件夹路径
# main_folder = fr"yourpath"

# # 初始化结果文件
# with open(os.path.join(main_folder, f"wst_death_gini.csv"), "a", encoding="utf-8-sig") as f:
#     f.write(f"name,year,gini_total\n")

# # 遍历每个省份的子文件夹
# for province_folder in os.listdir(main_folder):
#     province_path = os.path.join(main_folder, province_folder)

#     # 确保是文件夹
#     if os.path.isdir(province_path):
#         # 遍历每个年份的 CSV 文件
#         for year in range(2019, 2020):
#             csv_file = os.path.join(province_path, f"{year}.csv")

#             # 检查 CSV 文件是否存在
#             if os.path.exists(csv_file):
#                 df = pd.read_csv(csv_file)

#                 # 如果 DataFrame 为空，输出 0 并跳过计算
#                 if df.empty:
#                     print(f"{province_folder} - {year}_gini is 0 (empty DataFrame)")
#                     with open(os.path.join(main_folder, f"wst_death_gini.csv"), "a", encoding="utf-8-sig") as f:
#                         f.write(f"{province_folder},{year},0\n")
#                     continue  # 继续下一个循环

#                 df['Country'] = 1  # 为每个省份设置统一的 'Country' 列（或根据需要调整）

#                 # 计算 Gini 系数
#                 result = calculate_gini_decomp(df, 'Concentration', 'Country', 'Population')

#                 # 打印结果
#                 print(f"{province_folder} - {year}_gini_total is {result.gini_total[0]} ")

#                 # 将结果保存到 CSV 文件
#                 with open(os.path.join(main_folder, f"wst_death_gini.csv"), "a", encoding="utf-8-sig") as f:
#                     f.write(f"{province_folder},{year},{result.gini_total[0]}\n")

#### dagum gini 分解 ####
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd
from gini_decomp_R import calculate_gini_decomp
import os

# 激活 pandas2ri
pandas2ri.activate()

# 导入 R 包
dineq = importr('dineq')

for ssp in {1, 2, 3, 5}:
    # 主文件夹路径
    main_folder = fr"yourpath"

    # 初始化结果文件
    with open(os.path.join(main_folder, f"SSP{ssp}_Death_gini_dagum省.csv"), "a", encoding="utf-8-sig") as f:
        f.write(f"year,gini_total,gini_within,gini_between,gini_overlap\n")

    for year in range(2025, 2105, 5):
        csv_file = os.path.join(main_folder, f"{year}.csv")
        df = pd.read_csv(csv_file)
        df['Province_ID'] = df['country'].astype('category').cat.codes
        result = calculate_gini_decomp(df, 'Concentration', 'Province_ID', 'Population')
        # 打印结果
        print(f"{year}_gini_total is {result.gini_total[0]} gini_within is {result.gini_within[0]}, gini_between is {result.gini_between[0]}, gini_overlap is {result.gini_overlap[0]}")

        # 将结果保存到 CSV 文件
        with open(os.path.join(main_folder, f"SSP{ssp}_Death_gini_dagum省.csv"), "a", encoding="utf-8-sig") as f:
            f.write(f"{year},{result.gini_total[0]},{result.gini_within[0]},{result.gini_between[0]},{result.gini_overlap[0]}\n")
