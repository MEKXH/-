# -*- coding = utf-8 -*-
# @Author ：YEPEI
# @Time : 2024/7/21 19:06
# @File : gini_decomp_R.py
# @Software : PyCharm

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri
import pandas as pd
pd.set_option('display.max_columns', None)

# 激活 pandas2ri
pandas2ri.activate()

# 导入 R 包
dineq = importr('dineq')

def calculate_gini_decomp(df, x_col, z_col, weights_col):
    """
    计算 Gini 系数分解
    :param df: Pandas DataFrame
    :param x_col: 待分组变量列名
    :param z_col: 分组变量（组别）列名
    :param weights_col: 权重列名
    :return: 包含分解结果的 Pandas DataFrame
    """
    # 获取 DataFrame 中的列数据
    x = robjects.FloatVector(df[x_col])
    z = robjects.FloatVector(df[z_col])
    weights = robjects.FloatVector(df[weights_col])

    # 调用 gini_decomp 函数
    result = dineq.gini_decomp(x=x, z=z, weights=weights)

    # 提取分解结果输出为 DataFrame
    gini_decomp = result.rx2("gini_decomp")

    gini_total = gini_decomp.rx2("gini_total")[0] if 'gini_total' in gini_decomp.names else None
    gini_within = gini_decomp.rx2("gini_within")[0] if 'gini_within' in gini_decomp.names else None
    gini_between = gini_decomp.rx2("gini_between")[0] if 'gini_between' in gini_decomp.names else None
    gini_overlap = gini_decomp.rx2("gini_overlap")[0] if 'gini_overlap' in gini_decomp.names else None

    # 将结果转换为 Pandas DataFrame
    # 其中gini_total是直接用加权基尼系数公式算的，无论是否分组都是这个结果
    result_gini_decomp = {
        'gini_total': [gini_total],
        'gini_within': [gini_within],
        'gini_between': [gini_between],
        'gini_overlap': [gini_overlap]
    }

    df_result_gini_decomp = pd.DataFrame(result_gini_decomp)
    return df_result_gini_decomp