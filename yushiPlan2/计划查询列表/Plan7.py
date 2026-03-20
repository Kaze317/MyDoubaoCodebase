

import glob
import re
import warnings
from datetime import datetime
import pandas as pd
from Plan1 import remind, normalize_columns, find_column, ensure_date_columns
warnings.filterwarnings('ignore')
pd.set_option('display.width', 1000)  
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



def process_date(value):
    if isinstance(value, pd.Timestamp) or isinstance(value, datetime):  
        return value  
    elif isinstance(value, str) and value.strip():  
        try:
            return pd.to_datetime(value)  
        except ValueError:
            return pd.NaT  
    elif isinstance(value, (int, float)):  
        return pd.to_datetime(value, unit='D', origin='1899-12-30')  
    else:
        return pd.NaT  


def get_range_start_end_months(line_importance, voltage, planned_start_month):
    """
    根据重要度 + 电压等级 + 计划开始日期月份，得到“允许的时间范围（按月）”。
    规则：
    - 关键/重要：2月1次 => (1-2, 3-4, 5-6, ...)
    - 一般/关注/其余时段：110kV上、下半年各1次；220kV每季度1次
    """
    line_importance = str(line_importance)
    voltage = str(voltage)
    planned_start_month = int(planned_start_month)

    if re.search(r"关键|重要", line_importance):
        start_month = ((planned_start_month - 1) // 2) * 2 + 1
        end_month = min(start_month + 1, 12)
        return start_month, end_month

    if "220" in voltage:
        q_start = ((planned_start_month - 1) // 3) * 3 + 1
        q_end = min(q_start + 2, 12)
        return q_start, q_end

    if planned_start_month <= 6:
        return 1, 6
    return 7, 12


def should_complete_by_importance_range(line_importance, voltage, planned_start_date, actual_start_time, actual_end_time):
    """
    先看“实际开始日期”落在哪个范围内，
    再看“实际结束日期”是否不超过该范围的结束月。
    """
    if pd.isna(planned_start_date) or pd.isna(actual_start_time) or pd.isna(actual_end_time):
        return False

    planned_year = planned_start_date.year
    if actual_start_time.year != planned_year or actual_end_time.year != planned_year:
        return False

    start_m, end_m = get_range_start_end_months(line_importance, voltage, planned_start_date.month)
    actual_start_m = actual_start_time.month
    actual_end_m = actual_end_time.month

    return (start_m <= actual_start_m <= end_m) and (actual_end_m <= end_m)


def the_rest(read_data, Source_data, line, Planned_month, setMonth,line_importance):
    
    line_name_col = find_column(Source_data, "变电站/线路") or find_column(Source_data, "线路名称")
    voltage_col = find_column(Source_data, "电压等级")
    planned_start_col = find_column(Source_data, "计划开始日期") or find_column(Source_data, "计划开始时间")
    if line_name_col is None or planned_start_col is None:
        return "已跳过(缺少关键列)"

    line_name = Source_data.at[line, line_name_col]
    tingdian_IF = Source_data.at[line, "是否停电"] if find_column(Source_data, "是否停电") else ""
    sRet = re.sub(r"乙", r".*?乙", str(line_name))
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    voltage = Source_data.at[line, voltage_col] if voltage_col else ""
    planned_start_date = Source_data.at[line, planned_start_col]

    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):  
            
            actual_start_time = pd.to_datetime(read_data.iloc[i]["实际开始时间"])
            actual_end_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            if should_complete_by_importance_range(
                line_importance=line_importance,
                voltage=voltage,
                planned_start_date=planned_start_date,
                actual_start_time=actual_start_time,
                actual_end_time=actual_end_time,
            ):
                ID = read_data.iloc[i]["计划编号"]
                start_time = actual_start_time
                end_time = actual_end_time
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)

            
            
            
            
            
            
    return "已回填(7、避雷器红外检测)"


def Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data):
    
    normalize_columns(Source_data)
    finish_col = find_column(Source_data, "完成情况")
    work_content_col = find_column(Source_data, "工作地点和内容")
    plan_id_col = find_column(Source_data, "计划编号")
    start_col, end_col = ensure_date_columns(Source_data)
    finish_month_col = find_column(Source_data, "完成月份")

    Source_data.iloc[line, Source_data.columns.get_loc(start_col)] = start_time
    Source_data.iloc[line, Source_data.columns.get_loc(end_col)] = end_time

    if work_content_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(work_content_col)] = place_and_text
    if plan_id_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(plan_id_col)] = ID
    if finish_month_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(finish_month_col)] = f"{setMonth}月份已完成"
    if finish_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(finish_col)] = "已完成"
    
    
    
    
    
    



def guanzhu_and_yiban(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name_col = find_column(Source_data, "变电站/线路") or find_column(Source_data, "线路名称")
    voltage_col = find_column(Source_data, "电压等级")
    line_importance_col = find_column(Source_data, "线路重要度")
    planned_start_col = find_column(Source_data, "计划开始日期") or find_column(Source_data, "计划开始时间")
    if line_name_col is None or planned_start_col is None:
        return "已跳过(缺少关键列)"

    line_name = Source_data.at[line, line_name_col]
    voltage = Source_data.at[line, voltage_col] if voltage_col else ""
    sRet = re.sub(r"乙", r".*?乙", str(line_name))
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):
            
            actual_start_time = pd.to_datetime(read_data.iloc[i]["实际开始时间"])
            actual_end_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            line_importance = Source_data.at[line, line_importance_col] if line_importance_col else ""
            planned_start_date = Source_data.at[line, planned_start_col]
            if should_complete_by_importance_range(
                line_importance=line_importance,
                voltage=voltage,
                planned_start_date=planned_start_date,
                actual_start_time=actual_start_time,
                actual_end_time=actual_end_time,
            ):
                ID = read_data.iloc[i]["计划编号"]
                start_time = actual_start_time
                end_time = actual_end_time
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)
    return "已填写一般和关注"


def guanjian_and_zhongyao(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name_col = find_column(Source_data, "变电站/线路") or find_column(Source_data, "线路名称")
    voltage_col = find_column(Source_data, "电压等级")
    line_importance_col = find_column(Source_data, "线路重要度")
    planned_start_col = find_column(Source_data, "计划开始日期") or find_column(Source_data, "计划开始时间")
    if line_name_col is None or planned_start_col is None:
        return "已跳过(缺少关键列)"

    line_name = Source_data.at[line, line_name_col]
    voltage = Source_data.at[line, voltage_col] if voltage_col else ""
    sRet = re.sub(r"乙", r".*?乙", str(line_name))
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):
            
            actual_start_time = pd.to_datetime(read_data.iloc[i]["实际开始时间"])
            actual_end_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            line_importance = Source_data.at[line, line_importance_col] if line_importance_col else ""
            planned_start_date = Source_data.at[line, planned_start_col]
            if should_complete_by_importance_range(
                line_importance=line_importance,
                voltage=voltage,
                planned_start_date=planned_start_date,
                actual_start_time=actual_start_time,
                actual_end_time=actual_end_time,
            ):
                ID = read_data.iloc[i]["计划编号"]
                start_time = actual_start_time
                end_time = actual_end_time
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)
    return "已填写关键和重要"

def main_7(setMonth):
    
    
    
    
    
    path = {
        'one_path': './*计划查询列表*.xlsx',
        'two_path': './*预试检测计划*.xlsx',
    }
    paths = {}
    for key, pattern in path.items():
        matched_files = glob.glob(pattern)
        paths[key] = matched_files[0] if matched_files else None
    
    read_path = paths['one_path']
    Source_path = paths['two_path']
    
    
    Source_data = pd.read_excel(Source_path, sheet_name="7、避雷器红外检测", skiprows=[0])
    normalize_columns(Source_data)

    planned_start_col = find_column(Source_data, "计划开始日期") or find_column(Source_data, "计划开始时间")
    planned_end_col = find_column(Source_data, "计划结束日期") or find_column(Source_data, "计划结束时间")
    voltage_col = find_column(Source_data, "电压等级")
    line_importance_col = find_column(Source_data, "线路重要度")
    line_name_col = find_column(Source_data, "变电站/线路") or find_column(Source_data, "线路名称")

    if planned_start_col is None or planned_end_col is None or line_name_col is None:
        raise KeyError(f"Plan7 缺少必要列（计划开始/结束、变电站/线路）。当前列名: {list(Source_data.columns)}")

    Source_data[planned_start_col] = Source_data[planned_start_col].apply(process_date)
    Source_data[planned_end_col] = Source_data[planned_end_col].apply(process_date)
    
    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间', '工作方式']]
    
    read_data = read_data[(read_data['工作地点'].str.contains('避雷器红外')) | (
        read_data['工作内容'].str.contains('避雷器红外'))]
    print(f"7、避雷器红外检测已搜到关键字数据共有：{len(read_data)}")

    for line in range(len(Source_data)):
        raw_line_importance = Source_data.at[line, line_importance_col] if line_importance_col else ""
        line_importance = "" if pd.isna(raw_line_importance) else str(raw_line_importance)

        Planned_end_time = Source_data.at[line, planned_end_col]
        Planned_month = process_date(Planned_end_time)
        if pd.isna(Planned_month):
            continue
        Planned_month = Planned_month.month

        if re.search("其余时段", line_importance):
            txt1 = the_rest(read_data, Source_data, line, Planned_month, setMonth, line_importance)
        elif re.search("关注|一般", line_importance):
            txt2 = guanzhu_and_yiban(read_data, Source_data, line, Planned_month, setMonth)
        elif re.search("关键|重要", line_importance):
            txt3 = guanjian_and_zhongyao(read_data, Source_data, line, Planned_month, setMonth)
        else:
            txtd = guanzhu_and_yiban(read_data, Source_data, line, Planned_month, setMonth)
        remind(Source_data, line, setMonth, Planned_month,year_name="计划结束日期")  
    Source_data[planned_start_col] = pd.to_datetime(Source_data[planned_start_col]).dt.strftime('%Y-%m-%d')
    Source_data[planned_end_col] = pd.to_datetime(Source_data[planned_end_col]).dt.strftime('%Y-%m-%d')
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="7、避雷器红外检测", startrow=1, startcol=0, index=False)
    return Source_data
    

if __name__ == '__main__':
    main_7(1)

