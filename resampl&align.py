import glob
import os
import arcpy

# 参考文件路径，使用栅格数据集（从其导入方形像元大小）的路径
inf = r"path/to/reference/raster.tif"

# 输入路径
inws = r"path/to/input/tif/files"

# 获取栅格数据集的单元格大小
cellsize = "{0} {1}".format(arcpy.Describe(inf).meanCellWidth, arcpy.Describe(inf).meanCellHeight)

print(cellsize)

# 输出路径
outws = r"path/to/output/resampled/files"

# 确保输出文件夹存在，如果不存在则创建
if not os.path.exists(outws):
    os.makedirs(outws)

# 利用glob包，将输入路径下的所有tif文件读存放到rasters中
rasters = glob.glob(os.path.join(inws, "*.tif"))

# 循环处理所有影像
for raster in rasters:
    print(f"Processing {os.path.basename(raster)}...")
    nameT = os.path.basename(raster).split(".")[0] + ".tif"  # 自定义文件名
    outname = os.path.join(outws, nameT)  # 合并输出文件名+输出路径
    arcpy.Resample_management(raster, outname, cellsize, "NEAREST")
    print(f"{os.path.basename(raster)} has been resampled and saved as {nameT}")

print("Batch resampling complete!")

# 设置工作空间
arcpy.env.workspace = outws
input_folder = outws
output_folder = r"path/to/output/extracted/files"
mask_raster = r"path/to/mask/raster.tif"  # 控制区域栅格

# 获取输入文件夹中的所有栅格数据
arcpy.env.workspace = input_folder
rasters = arcpy.ListRasters("*", "TIF")

# 设置捕捉栅格和像元大小
arcpy.env.snapRaster = mask_raster
desc = arcpy.Describe(mask_raster)
arcpy.env.cellSize = desc.meanCellWidth

# 设置环境变量来保证处理范围与掩膜栅格一致
arcpy.env.extent = mask_raster

# 循环处理每个栅格数据
for raster in rasters:
    # 构建输出路径，确保输出路径与输入路径不同
    output_raster = os.path.join(output_folder, os.path.basename(raster))  # 使用输入文件名作为输出文件名

    # 执行按掩膜提取操作
    arcpy.gp.ExtractByMask_sa(raster, mask_raster, output_raster)

    print(f"Extracted {raster} to {output_raster}")

print("Extraction complete.")
