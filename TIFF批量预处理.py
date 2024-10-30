import rasterio
import numpy as np
import json
from pathlib import Path
import csv
from tqdm import tqdm

def GeoTiff2Json(input_file_path, output_file_path):
    with rasterio.open(input_file_path) as src:
        # 读取波段数据
        band_data = src.read(1)  # 读取第一个波段

        # 处理特殊值
        special_values = [
            -3.4028234663852886e+38,
            -3.4028e+38,
            -9999,
            -9999.0,
            -32768,
            float('inf'),
            float('-inf'),
        ]

        # 将空值(NaN或None)转换为0
        band_data = np.nan_to_num(band_data, nan=0.0, posinf=0.0, neginf=0.0)

        # 将所有特殊值转换为0
        for special_value in special_values:
            band_data = np.where(np.isclose(band_data, special_value, rtol=1e-5), 0, band_data)

        # 将二维数组展平为一维数组并转换为列表
        flattened_data = band_data.flatten().tolist()

        # 创建自定义JSON对象
        json_data = {
            "width": src.width,
            "height": src.height,
            "data": flattened_data
        }

        # 将数据转换为JSON字符串
        json_str = json.dumps(json_data)

        # 解析JSON字符串为Python对象
        parsed_data = json.loads(json_str)

        # 非零值保留两位小数
        processed_data = [round(x, 2) if x != 0 else 0 for x in parsed_data['data']]
        parsed_data['data'] = processed_data

        # 保存为压缩一行的 JSON 文件
        with open(output_file_path, 'w') as json_file:
            json.dump(parsed_data, json_file, separators=(',', ':'))

        return max(processed_data)

def process_folder(input_folder, output_folder):
    # 确保输出文件夹存在
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # 获取所有.tif文件
    tif_files = list(Path(input_folder).glob('*.tif'))
    total_files = len(tif_files)

    print(f"找到 {total_files} 个tif文件待处理...")

    # 创建一个列表存储最大值信息
    max_values = []

    # 使用tqdm创建进度条
    with tqdm(total=total_files, desc="处理进度", ncols=100) as pbar:
        # 处理每个文件
        for tif_path in tif_files:
            # 构建输出文件路径，保持相同的文件名.json
            output_path = Path(output_folder) / f"{tif_path.stem}.json"

            try:
                max_value = GeoTiff2Json(str(tif_path), str(output_path))
                max_values.append([tif_path.stem, max_value])
                # 更新进度条描述，显示当前处理的文件名
                pbar.set_postfix({"当前文件": tif_path.name}, refresh=True)
            except Exception as e:
                print(f"\n处理文件 {tif_path.name} 时出错：{str(e)}")
            finally:
                pbar.update(1)

    # 将最大值信息写入CSV文件
    csv_path = Path(output_folder) / 'MaxValue.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['filename', 'maxValue'])  # 写入表头
        csv_writer.writerows(max_values)  # 写入数据

    print(f"\n所有文件处理完成！共处理 {total_files} 个文件。")
    print(f"最大值数据已保存到：{csv_path}")

# 使用
input_folder = ""  # 输入TIFF数据文件夹
output_folder = ""  # 输出可视化平台自定义json文件夹
process_folder(input_folder, output_folder)