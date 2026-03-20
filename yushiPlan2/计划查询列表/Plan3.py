

import glob
import re
import warnings
from datetime import datetime
import pandas as pd
from Plan1 import remind, should_complete_by_importance_range
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

def the_rest(read_data, Source_data, line, Planned_month, setMonth,Planned_year):
    
    line_name = Source_data.at[line, "变电站/线路"]  
    line_importance = Source_data.at[line, "线路重要度"]
    voltage = Source_data.at[line, "电压等级"]
    planned_start_date = Source_data.at[line, "计划开始日期"]
    sRet = re.sub(r"乙", r".*?乙", line_name)
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    
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
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
    return "已回填(3、电缆线路交叉互联预试)"

def Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data):
    
    progress = Source_data.iloc[line]["完成情况"]
    if progress != "已完成":
        
        
        Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")] = place_and_text
        Source_data.iloc[line, Source_data.columns.get_loc("计划编号")] = ID
        Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")] = start_time
        Source_data.iloc[line, Source_data.columns.get_loc("实际结束日期")] = end_time
        Source_data.iloc[
            line, Source_data.columns.get_loc("完成月份")] = f"{setMonth}月份已完成"
        Source_data.iloc[line, Source_data.columns.get_loc("完成情况")] = "已完成"
    elif progress == "已完成":
        Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")] = str(Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")]) + "\n"+place_and_text
        Source_data.iloc[line, Source_data.columns.get_loc("计划编号")] = str(Source_data.iloc[line, Source_data.columns.get_loc("计划编号")]) + "\n" + ID
        Source_data.iloc[line, Source_data.columns.get_loc("实际结束日期")] = end_time
        Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")] = str(Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")]) + "\n" + start_time

def main_3(setMonth):
    
    
    
    
    
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
    
    
    Source_data = pd.read_excel(Source_path, sheet_name="3、电缆线路交叉互联预试", skiprows=[0])
    Source_data['预试到期时间'] = Source_data['预试到期时间'].apply(process_date)
    Source_data['计划开始日期'] = Source_data['计划开始日期'].apply(process_date)
    Source_data['计划结束日期'] = Source_data['计划结束日期'].apply(process_date)
    
    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间']]
    
    read_data = read_data[(read_data['工作地点'].str.contains('交叉互联')) | (
        read_data['工作内容'].str.contains('交叉互联'))]
    print(f"3、电缆线路交叉互联预试已搜到关键字数据共有：{len(read_data)}")

    for line in range(len(Source_data)):
        job_content = ""  
        Plan_number = ""  
        in_start_time = ""  
        in_end_time = ""  
        Planned_end_time = Source_data.at[line, '预试到期时间']
        Planned_time = process_date(Planned_end_time)
        Planned_month = Planned_time.month
        Planned_year = Planned_time.year
        txt1 = the_rest(read_data, Source_data, line, Planned_month, setMonth,Planned_year)
        remind(Source_data, line, setMonth, Planned_month,year_name="预试到期时间")  
    Source_data['预试到期时间'] = pd.to_datetime(Source_data['预试到期时间']).dt.strftime('%Y-%m-%d')
    Source_data['计划开始日期'] = pd.to_datetime(Source_data['计划开始日期']).dt.strftime('%Y-%m-%d')
    Source_data['计划结束日期'] = pd.to_datetime(Source_data['计划结束日期']).dt.strftime('%Y-%m-%d')
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="3、电缆线路交叉互联预试", startrow=1, startcol=0, index=False)
    return Source_data

if __name__ == '__main__':
    main_3(4)