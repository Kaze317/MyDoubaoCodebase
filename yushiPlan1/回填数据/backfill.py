import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 显示所有行
# 显示所有列
pd.set_option('display.width', 1000)  # 加了这一行那表格的一行就不会分段出现了
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def load_excel_files(file_pattern):
    """获取当前目录下符合给定模式的 Excel 文件"""
    # return glob.glob(os.path.join(os.getcwd(), file_pattern))
    return list(Path().glob(file_pattern))


def extract_data_from_files(file_names, columns_to_extract):
    """从指定文件中提取数据，返回合并后的 DataFrame"""
    all_data = pd.DataFrame()
    for file_name in file_names:
        df = pd.read_excel(file_name, header=3, engine='openpyxl')
        extracted_data = df[columns_to_extract]
        all_data = pd.concat([all_data, extracted_data], ignore_index=True)
    return all_data


def collect_new_values(file_names, column_index):
    """从指定文件中收集新的列值"""
    new_values = []
    for file_name in file_names:
        df = pd.read_excel(file_name, header=3, engine='openpyxl')
        extracted_data1 = df.iloc[:, column_index]
        new_values.append(extracted_data1)
    return pd.concat(new_values, ignore_index=True)


def main():
    # 表格文件名匹配模式
    input_file_patterns = [
        '*跨越公路重点区段*.xlsx',
        '*跨越铁路重点区段*.xlsx',
        '*跨越河流重点区段*.xlsx'
    ]

    # 动态获取文件列表
    file_names = []
    for pattern in input_file_patterns:
        file_names.extend(load_excel_files(pattern))
    # 要提取的列
    # columns_to_extract = ["区段编号", "杆塔区段", "线路名称", "最近一次完成时间.1", "超期红绿灯.1", "状态", "最近一次完成时间", "超期红绿灯","工作要求.1"]
    columns_to_extract = ["区段编号", "杆塔区段", "线路名称", "最近一次完成时间.1", "超期红绿灯.1", "状态",
                          "最近一次完成时间", "超期红绿灯",'工作要求.1']

    # 提取所有重点区段的数据
    all_data = extract_data_from_files(file_names, columns_to_extract)

    # 收集新值
    new_values = collect_new_values(file_names, column_index=25)

    # 在状态列之后插入新的列
    insert_index = all_data.columns.get_loc("状态") + 1
    all_data.insert(insert_index, "跨越等级", new_values)

    # 重命名列
    all_data.rename(columns={
        "区段编号": "计划编号",
        "杆塔区段": "塔段",
        "线路名称": "线路名",
        "最近一次完成时间.1": "红外测温最近一次完成时间",
        "最近一次完成时间": "日常巡视最近一次完成时间",
        "超期红绿灯.1": "红外测温超期红绿灯",
        "超期红绿灯": "日常巡视超期红绿灯",
        "工作要求.1": "工作要求"
    }, inplace=True)
    # print(all_data.head(5))

    # 获取输出文件
    output_file = load_excel_files('*预试检测计划*.xlsx')
    if output_file:
        output_file = output_file[0]  # 获取第一个符合条件的文件
    else:
        print("未找到符合条件的预试检测计划文件。")
        return

    sheet_name = '三跨两临近重点区段'
    # # 读取原有数据
    # try:
    #     with pd.ExcelFile(output_file, engine='openpyxl') as xls:
    #         updated_data = pd.read_excel(xls, sheet_name=sheet_name)
    #
    #     # 合并数据
    #     # updated_data = pd.concat([existing_data, all_data], ignore_index=True)
    #     # print(updated_data.head(5))
    #
    # except FileNotFoundError:
    #     print(f"文件 '{output_file}' 不存在。")
    #     updated_data = all_data  # 如果文件不存在，则只使用 all_data

    try:
        # 使用 if_sheet_exists='replace' 来覆盖整个工作表
        with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            all_data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0, header=True)
            # 如果已有数据，headers 会被清除掉，但这里我们保持 header=True
        print(f"数据已成功写入到 '{output_file}' 的工作表 '{sheet_name}' 中。")
    except Exception as e:
        print(f"写入数据时发生错误: {e}")

    # # 在写回 Excel 文件时检查是否有数据
    # if not updated_data.empty:
    #     try:
    #         # 因为 if_sheet_exists='replace' 的参数行为。此参数会使 pandas 创建一个新的 sheet，因而引发 ".1" 这种后缀的名称生成
    #         # 所以这里应该使用if_sheet_exists='overlay' 来允许在现有工作表上追加数据。
    #         with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
    #             updated_data.to_excel(writer, sheet_name=sheet_name, index=False)
    #             # updated_data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row, header=False)
    #
    #         print(f"数据已成功追加到 '{output_file}' 的工作表 '{sheet_name}' 中。")
    #     except Exception as e:
    #         print(f"写入数据时发生错误: {e}")
    # else:
    #     print("没有可写入的数据。")


if __name__ == '__main__':
    main()
