import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


pd.set_option('display.width', 1000)  
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def load_excel_files(file_pattern):
    
    
    return list(Path().glob(file_pattern))


def extract_data_from_files(file_names, columns_to_extract):
    
    all_data = pd.DataFrame()
    for file_name in file_names:
        df = pd.read_excel(file_name, header=3, engine='openpyxl')
        extracted_data = df[columns_to_extract]
        all_data = pd.concat([all_data, extracted_data], ignore_index=True)
    return all_data


def collect_new_values(file_names, column_index):
    
    new_values = []
    for file_name in file_names:
        df = pd.read_excel(file_name, header=3, engine='openpyxl')
        extracted_data1 = df.iloc[:, column_index]
        new_values.append(extracted_data1)
    return pd.concat(new_values, ignore_index=True)


def dis_Time(data, text, idx, now_month, case_text, now_state, now_class, now_require):
    
    time_text = pd.to_datetime(text, errors='coerce')  
    
    time_month = time_text.month
    if pd.notna(text) and time_text.year == 2025:
        data.at[idx, f'{time_month}月最近一次完成时间'] = time_text.strftime('%Y-%m-%d')
        data.at[idx, f'{time_month}月超期红绿灯'] = case_text
        data.at[idx, '现存状态'] = now_state
        data.at[idx, '跨越等级'] = now_class
        data.at[idx, '工作要求'] = now_require
    else:
        data.at[idx, '现存状态'] = now_state
        data.at[idx, '跨越等级'] = now_class
        data.at[idx, '工作要求'] = now_require
    
    if (now_require == '1月1次' or now_require == '1月2次') and data.at[idx, '现存状态'] == '现存区段':
        if pd.isna(data.at[idx, f'{now_month}月最近一次完成时间']):  
            data.at[idx, '计划临期提醒'] = f'{now_month}月需要提醒'
        else:  
            data.at[idx, '完成月份'] = f'{time_month}月份已完成'
    elif now_require == '2月1次' and now_month % 2 == 0 and data.at[idx, '现存状态'] == '现存区段':
        if pd.isna(data.at[idx, f'{now_month}月最近一次完成时间']) and pd.isna(
                data.at[idx, f'{now_month - 1}月最近一次完成时间']):
            data.at[idx, '计划临期提醒'] = f'{now_month}月需要提醒'
        else:  
            data.at[idx, '完成月份'] = f'{time_month}月份已完成'
    elif now_require == '3月1次' and data.at[idx, '现存状态'] == '现存区段':
        if now_month % 3 == 0:
            if pd.isna(data.at[idx, f'{now_month}月最近一次完成时间']) and pd.isna(
                    data.at[idx, f'{now_month - 1}月最近一次完成时间']) and pd.isna(
                    data.at[idx, f'{now_month - 2}月最近一次完成时间']):
                data.at[idx, '计划临期提醒'] = f'{now_month}月需要提醒'
            else:  
                data.at[idx, '完成月份'] = f'{time_month}月份已完成'
        else:
            data.at[idx, '完成月份'] = f'{time_month}月份已完成'
    return data


def cewen_data(output_file, all_data, sheet_name, now_month):
    data = pd.read_excel(output_file, sheet_name=sheet_name, skiprows=[0])
    hongwai_data = pd.DataFrame()

    for idx, row in data.iterrows():  
        data_ID = row['区段编号']  
        
        matching_row = all_data[all_data['计划编号'] == data_ID]
        if not matching_row.empty:  
            
            hongwai_in_time = matching_row['红外测温最近一次完成时间'].values[0]
            hongwai_case = matching_row['红外测温超期红绿灯'].values[0]
            now_state = matching_row['状态'].values[0]
            now_class = matching_row['跨越等级'].values[0]
            now_require = matching_row['工作要求'].values[0]
            
            hongwai_data = dis_Time(data, text=hongwai_in_time, idx=idx, now_month=now_month, case_text=hongwai_case,
                                    now_state=now_state, now_class=now_class, now_require=now_require)
    return hongwai_data


def xs_data(output_file, all_data, sheet_name, now_month):
    data = pd.read_excel(output_file, sheet_name=sheet_name, skiprows=[0])
    xunshi_data = pd.DataFrame()

    for idx, row in data.iterrows():  
        data_ID = row['区段编号']  
        
        matching_row = all_data[all_data['计划编号'] == data_ID]
        if not matching_row.empty:  
            
            xunshi_in_time = matching_row['日常巡视最近一次完成时间'].values[0]
            xunshi_case = matching_row['日常巡视超期红绿灯'].values[0]
            now_state = matching_row['状态'].values[0]
            now_class = matching_row['跨越等级'].values[0]
            
            
            xunshi_data = dis_Time(data, text=xunshi_in_time, idx=idx, now_month=now_month, case_text=xunshi_case,
                                   now_state=now_state, now_class=now_class, now_require='1月1次')

    return xunshi_data



def each_center(center):
    if '花都' in center:
        return '花都中心'
    elif '白云' in center:
        return '白云中心'
    elif '天河' in center:
        return '天河中心'
    elif '从化' in center:
        return '从化中心'


def main_CW_XS(now_month):
    
    
    input_file_patterns = [
        '*跨越公路重点区段*.xlsx',
        '*跨越铁路重点区段*.xlsx',
        '*跨越河流重点区段*.xlsx'
    ]

    
    file_names = []
    for pattern in input_file_patterns:
        file_names.extend(load_excel_files(pattern))
    
    
    columns_to_extract = ["区段编号", "杆塔区段", "线路名称", "最近一次完成时间.1", "超期红绿灯.1", "状态",
                          "最近一次完成时间", "超期红绿灯", '工作要求.1', '所属班组', '运维单位', '线路责任人',
                          '设备主人']

    
    all_data = extract_data_from_files(file_names, columns_to_extract)

    
    new_values = collect_new_values(file_names, column_index=25)

    
    insert_index = all_data.columns.get_loc("状态") + 1
    all_data.insert(insert_index, "跨越等级", new_values)

    
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
    
    
    
    output_file = load_excel_files('*预试检测计划*.xlsx')
    if output_file:
        output_file = output_file[0]  
    else:
        print("未找到符合条件的预试检测计划文件。")
        return
    
    with pd.ExcelWriter(output_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        all_data.to_excel(writer, sheet_name=f"{now_month}月重要交跨管控要求完成情况", index=False)
    
    
    all_data['红外测温最近一次完成时间'] = pd.to_datetime(
        all_data['红外测温最近一次完成时间'],
        errors='coerce'
    )
    
    all_data = all_data[
        (all_data['状态'] != '已取消') &
        (all_data['红外测温最近一次完成时间'].dt.month == now_month)
        ]
    return len(all_data)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    


if __name__ == '__main__':
    
    
    pass
