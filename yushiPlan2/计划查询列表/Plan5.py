

import glob
import re
import warnings
from datetime import datetime
import pandas as pd
from Plan1 import remind

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



def the_rest(read_data, Source_data, line, Planned_month, setMonth, line_importance):
    
    line_name = Source_data.at[line, "变电站/线路"]  
    tingdian_IF = Source_data.at[line, "是否停电"]  
    sRet = re.sub(r"乙", r".*?乙", line_name)
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    numbers = re.findall(r'\d+', line_importance)
    first_number = numbers[0] if len(numbers) > 0 else None
    second_number = numbers[1] if len(numbers) > 1 else None
    first_number = int(first_number)
    second_number = int(second_number)
    
    
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):  
            
            read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            read_data_Month = read_data_time.month
            
            if Planned_month <= first_number: 
                if 1 <= read_data_Month <= Planned_month:  
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
            elif Planned_month > second_number: 
                if second_number <= read_data_Month <= Planned_month:  
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
            else:
                if first_number <= read_data_Month <= Planned_month:  
                    
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
            
            
            
            
            
            
    return "已回填(5、电缆护套环流检测)"


def Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data):
    
    progress = Source_data.iloc[line]["完成情况"]
    if progress != "已完成":
        
        
        Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")] = place_and_text
        Source_data.iloc[line, Source_data.columns.get_loc("计划编号")] = ID
        Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")] = start_time
        Source_data.iloc[line, Source_data.columns.get_loc("实际结束日期")] = end_time
        Source_data.iloc[line, Source_data.columns.get_loc("完成月份")] = f"{setMonth}月份已完成"
        Source_data.iloc[line, Source_data.columns.get_loc("完成情况")] = "已完成"
    
    
    
    
    
    



def guanzhu_and_yiban(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name = Source_data.at[line, "变电站/线路"]  
    sRet = re.sub(r"乙", r".*?乙", line_name)
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):
            
            read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            read_data_Month = read_data_time.month
            if Planned_month <= 6:  
                if 1 <= read_data_Month <= Planned_month:
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)
            if Planned_month >= 7:  
                if 6 <= read_data_Month <= Planned_month:
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)
            
            
            
            
            
    return "已填写一般和关注"



def guanjian_and_zhongyao(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name = Source_data.at[line, "变电站/线路"]  
    sRet = re.sub(r"乙", r".*?乙", line_name)
    sRet = re.sub(r"甲", r"甲.*?", sRet)
    
    
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):
            
            read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            read_data_Month = read_data_time.month
            for start_month in range(1, 12, 2):
                if read_data_Month in range(start_month, start_month + 2) and Planned_month in range(start_month,
                                                                                                     start_month + 2):
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)
    return "已填写关键和重要"


def not_zhongyaodu(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name = Source_data.at[line, "变电站/线路"]  
    sRet = re.sub(r"乙", r".*?乙", line_name)
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):
            read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            read_data_Month = read_data_time.month
            if read_data_Month <= Planned_month:
                ID = read_data.iloc[i]["计划编号"]  
                start_time = read_data.iloc[i]["实际开始时间"]
                end_time = read_data_time
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data)
    return "已填写关键和重要"


def main_5(setMonth):
    
    
    
    
    
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
    
    
    Source_data = pd.read_excel(Source_path, sheet_name="5、电缆护套环流检测", skiprows=[0])
    Source_data['计划开始日期'] = Source_data['计划开始日期'].apply(process_date)
    Source_data['计划结束日期'] = Source_data['计划结束日期'].apply(process_date)
    
    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间', '工作方式']]
    
    read_data = read_data[(read_data['工作地点'].str.contains('护套环流')) | (
        read_data['工作内容'].str.contains('护套环流'))]
    print(f"5、电缆护套环流检测已搜到关键字数据共有：{len(read_data)}")

    for line in range(len(Source_data)):
        line_importance = Source_data.at[line, "线路重要度"]  
        
        
        
        
        Planned_end_time = Source_data.at[line, '计划结束日期']
        Planned_month = process_date(Planned_end_time)  
        Planned_month = Planned_month.month  
        if re.search("其余时段", line_importance):
            txt1 = the_rest(read_data, Source_data, line, Planned_month, setMonth, line_importance)
        elif re.search("关注|一般", line_importance):  
            txt2 = guanzhu_and_yiban(read_data, Source_data, line, Planned_month, setMonth)
        elif re.search("关键|重要", line_importance):  
            txt3 = guanjian_and_zhongyao(read_data, Source_data, line, Planned_month, setMonth)
        
        
        remind(Source_data, line, setMonth, Planned_month, year_name="计划结束日期")  
    Source_data['计划开始日期'] = pd.to_datetime(Source_data['计划开始日期']).dt.strftime('%Y-%m-%d')
    Source_data['计划结束日期'] = pd.to_datetime(Source_data['计划结束日期']).dt.strftime('%Y-%m-%d')
    
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="5、电缆护套环流检测", startrow=1, startcol=0, index=False)
    return Source_data





if __name__ == '__main__':
    main_5(5)
