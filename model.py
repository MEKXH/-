import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import t
from sklearn.metrics import r2_score

# 文件路径
file_path = "D:\\通用文件夹\\疾病死亡数据研究\\预测模型\\8.20预测模型\\merged_output.csv"

# 读取数据
df_cleaned = pd.read_csv(file_path)

# 年份列
years = [str(year) for year in range(1990, 2019 + 1)]
train_years_all = list(range(1990, 2016 + 1))
test_years = list(range(2016, 2019 + 1))
all_years = list(range(1990, 2019 + 1))
future_years = list(range(2025, 2101, 5))

# 定义模型函数
def compute_y(a, b, c, SDI, year, base_year):
    loss_factor = 0.99
    return a * SDI + b * (year - base_year) * (loss_factor ** (year - base_year)) + c

# 定义损失函数，用于优化参数，增加了正则化项
def loss_function(params, SDI, years, val, base_year, reg_lambda=0.001):
    a1, a2, b, c, d = params
    a = np.where(SDI >= 0.8, a1, a2)
    y_pred = np.array([compute_y(a[i], b, c, SDI[i], years[i], base_year) for i in range(len(years))])
    residuals = np.log(val) - y_pred
    residuals_pred = np.zeros_like(residuals)
    residuals_pred[1:] = d * residuals[:-1]
    
    # 加入正则化项
    regularization = reg_lambda * np.sum(np.square(b))
    
    return np.sum((residuals - residuals_pred) ** 2) + regularization

# 计算模型参数
def calculate_parameters(group, base_year, train_years, val, reg_lambda=0.001):
    SDI = group[years].iloc[0].values  # 取该地区的SDI值
    
    # 设置初始参数
    initial_params = [0.05, 0.05, 0.01, 0.01, 0.01]
    
    # 优化参数
    result = minimize(loss_function, initial_params, args=(SDI, train_years, val, base_year, reg_lambda))
    
    a1, a2, b, c, d = result.x
    return a1, a2, b, c, d

# 初始化结果数据框
results1 = []
results2 = []
results3 = []
results4 = []

# 基准年份
base_year = 1990

# 对每个location、cause分组计算
for (location, cause), group in df_cleaned.groupby(['location', 'cause']):
    # 分割训练集和测试集
    train_group = group[group['year'].isin(train_years_all)]
    test_group = group[group['year'].isin(test_years)]
    
    train_year = train_group['year'].values
    train_val = train_group['val'].values
    
    # 计算模型参数
    a1, a2, b, c, d = calculate_parameters(group, base_year, train_year, train_val, reg_lambda=0.001)

    SDI = group[years].iloc[0].values
    a = np.where(SDI >= 0.8, a1, a2)

    # 训练集预测对数值
    predicted_log_val_train = np.array([compute_y(a[i], b, c, SDI[i], y, base_year) for i, y in enumerate(train_year)])
    
    # 测试集预测对数值
    test_year = test_group['year'].values
    test_val = test_group['val'].values
    predicted_log_val_test = np.array([compute_y(a[i], b, c, SDI[i], y, base_year) for i, y in enumerate(test_year)])
    
    # 计算训练集决定系数
    r2_train = r2_score(np.log(train_val), predicted_log_val_train)
    
    # 计算测试集偏差比例和偏差数值
    test_log_val = np.log(test_val)
    test_residuals = test_log_val - predicted_log_val_test
    test_bias_percentage = (test_residuals / test_log_val) * 100
    
    # 存储结果1
    for idx, y in enumerate(test_year):
        results1.append({
            'cause': cause,
            'location': location,
            'year': y,
            'bias_value': test_residuals[idx],
            'bias_percentage': test_bias_percentage[idx],
            'r2_train': r2_train
        })
    
    # 预测未来年的预测值
    future_predicted_log_val = np.array([compute_y(a1 if SDI[-1] >= 0.8 else a2, b, c, SDI[-1], y, base_year) for y in future_years])
    
    # 存储结果2
    for idx, y in enumerate(future_years):
        results2.append({
            'cause': cause,
            'location': location,
            'year': y,
            'predicted_log_val': future_predicted_log_val[idx],
            'r2_train': r2_train
        })
    
    # 存储结果3
    for idx, y in enumerate(all_years):
        results3.append({
            'cause': cause,
            'location': location,
            'r2_train': r2_train
        })

# 转换结果为DataFrame
results_df1 = pd.DataFrame(results1)
results_df2 = pd.DataFrame(results2)
results_df3 = pd.DataFrame(results3)

# 保存结果到CSV文件
results_df1.to_csv("D:\\通用文件夹\\疾病死亡数据研究\\预测模型\\8.20预测模型\\test_set_evaluation.csv", index=False)
results_df2.to_csv("D:\\通用文件夹\\疾病死亡数据研究\\预测模型\\8.20预测模型\\future_predictions.csv", index=False)
results_df3.to_csv("D:\\通用文件夹\\疾病死亡数据研究\\预测模型\\8.20预测模型\\all_years_r2.csv", index=False)