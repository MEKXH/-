import os
import arcpy
from arcpy.sa import CellStatistics

arcpy.CheckOutExtension("Spatial")  # 检查 Spatial 分析模块

# 设置工作空间
workspace_nc = r'path/to/your/NC/files'
workspace_tif = r'path/to/save/TIF/files'

arcpy.env.workspace = workspace_nc

nc_files = [f for f in os.listdir(workspace_nc) if f.endswith('.nc')]

# 循环处理每个NC文件
for nc_file in nc_files:
    print(nc_file)
    # 构建NC文件的完整路径
    input_nc_file = os.path.join(workspace_nc, nc_file)

    # 构建输出TIFF文件的完整路径
    output_tif_file = os.path.join(workspace_tif, nc_file[21:-3] + '.tif')  # 这里的数字是根据文件名的长度

    # 使用MakeNetCDFRasterLayer_md函数创建NetCDF图层
    output_layer = "nc_layer_" + os.path.splitext(nc_file)[0]  # 创建唯一的图层名称
    arcpy.md.MakeNetCDFRasterLayer(input_nc_file, "emissions", "lon", "lat", output_layer, "time")  # 选择波段、经纬度等

    # 使用CopyRaster函数将图层转换为TIFF文件，并指定名称
    arcpy.CopyRaster_management(output_layer, output_tif_file, "", "", "", "NONE", "NONE", "")

    # 读取生成的多波段 TIFF 文件
    raster = arcpy.Raster(output_tif_file)
    band_count = raster.bandCount  # 获取波段数量
    
    # 创建一个空列表来存储各个波段
    band_list = []
    
    # 读取每个波段并添加到列表
    for band in range(1, band_count + 1):
        band_raster = arcpy.Raster(output_tif_file + f"\\Band_{band}")
        band_list.append(band_raster)
    
    # 使用 CellStatistics 进行波段累加
    summed_raster = CellStatistics(band_list, "SUM", "DATA")
    
    # 保存累加结果
    output_summed_tif = os.path.join(workspace_tif, nc_file[21:-3] + '_total.tif')
    summed_raster.save(output_summed_tif)

    print(f"Converted NC to TIFF and summed {band_count} bands for {nc_file}.")

arcpy.CheckInExtension("Spatial")  # 归还 Spatial 分析模块
