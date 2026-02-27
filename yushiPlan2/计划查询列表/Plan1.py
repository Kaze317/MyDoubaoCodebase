import glob
import re
import warnings
from datetime import datetime
import pandas as pd
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



def the_rest(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name = Source_data.at[line, "线路名称"]  
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
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
    return "已填写其余时段"

def guanjian_and_zhongyao(read_data, Source_data, line, Planned_month, setMonth):
    
    line_name = Source_data.at[line, "线路名称"]  
    sRet = re.sub(r"乙", r".*?乙", line_name)
    
    
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text):
            
            read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            read_data_Month = read_data_time.month
            if read_data_Month <= 6 and Planned_month <= 6:
                ID = read_data.iloc[i]["计划编号"]  
                start_time = read_data.iloc[i]["实际开始时间"]
                end_time = read_data_time
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
            elif read_data_Month > 6 and Planned_month > 6:
                ID = read_data.iloc[i]["计划编号"]  
                start_time = read_data.iloc[i]["实际开始时间"]
                end_time = read_data_time
                Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
    return "已填写关键和重要"


def guanzhu_and_yiban(read_data, Source_data, line, setMonth):
    
    line_name = Source_data.at[line, "线路名称"]  
    sRet = re.sub(r"乙", r".*?乙", line_name)
    for i in range(len(read_data)):
        place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
        if re.search(sRet, place_and_text): 
            
            read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
            ID = read_data.iloc[i]["计划编号"]  
            start_time = read_data.iloc[i]["实际开始时间"]
            end_time = read_data_time
            Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
    return "已填写关注和一般"


def gantahao(place_and_text):
    
    towerID = re.findall(r"#(\d{2,3})-#(\d{2,3})", place_and_text)
    
    towerID_merge = ""
    for number in range(len(towerID)):
        one_towerID = f"#{towerID[number][0]}-#{towerID[number][1]}"
        towerID_merge += one_towerID + "\n"
    towerID_merge = towerID_merge.rstrip("\n")  
    return towerID_merge


def Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data):
    
    towerID_merge = gantahao(place_and_text)  
    progress = Source_data.iloc[line]["完成情况"]
    if progress != "已完成":
        
        Source_data.iloc[line, Source_data.columns.get_loc("计划编号")] = ID
        Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")] = place_and_text
        Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")] = start_time
        Source_data.iloc[line, Source_data.columns.get_loc("实际结束日期")] = end_time
        Source_data.iloc[line, Source_data.columns.get_loc("完成月份")] = f"{setMonth}月份已完成"
        Source_data.iloc[line, Source_data.columns.get_loc("完成情况")] = "已完成"
    elif progress == "已完成":
        Source_data.iloc[line, Source_data.columns.get_loc("计划编号")] = str(Source_data.iloc[line, Source_data.columns.get_loc("计划编号")]) + "\n" + ID
        Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")] = str(Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")]) + "\n"+place_and_text
        Source_data.iloc[line, Source_data.columns.get_loc("实际结束日期")] = end_time
        Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")] = str(Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")]) + "\n" + start_time


def remind(Source_data,line,setMonth,Planned_month,year_name): 
    performance = Source_data.at[line,"完成情况"]
    
    Planned_year = Source_data.at[line,year_name]
    Planned_year = process_date(Planned_year)
    Planned_year = Planned_year.year
    
    if performance != "已完成" and setMonth == Planned_month and Planned_year == 2025:
        Source_data.iloc[line, Source_data.columns.get_loc("计划临期提醒")] = f"{setMonth}月需要提醒"


def main_1(setMonth):
    setYear = "2025"
    
    
    
    
    
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
    
    
    Source_data = pd.read_excel(Source_path, sheet_name="1、架空线路红外检测", skiprows=[0,1])
    Source_data['计划开始日期'] = Source_data['计划开始日期'].apply(process_date)
    Source_data['计划结束日期'] = Source_data['计划结束日期'].apply(process_date)
    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间', '工作类别']]
    
    read_data = read_data[(read_data['工作地点'].str.contains('线路红外|导线连接|无人机')) | (
        read_data['工作内容'].str.contains('线路红外|导线连接|无人机'))]
    
    read_data = read_data[
        ~read_data['工作地点'].str.contains('交跨|交叉跨越|重要交跨|重要跨越测温') &
        ~read_data['工作内容'].str.contains('交跨|交叉跨越|重要交跨|重要跨越测温')
        ]
    read_data = read_data[read_data['工作类别'].str.contains('测量')]
    print(f"1、架空线路红外检测已搜到关键字数据共有：{len(read_data)}")

    for line in range(len(Source_data)):
        line_importance = Source_data.at[line, "线路重要度"]  
        Planned_end_time = Source_data.at[line, '计划结束日期']
        Planned_start_time = Source_data.at[line, '计划开始日期']
        
        
        
        Planned_month = Planned_end_time.month
        Planned_year = Planned_end_time.year
        Planned_start_month = Planned_start_time.month
        line_name = Source_data.at[line, "线路名称"]  
        sRet = re.sub(r"乙", r".*?乙", line_name)
        sRet = re.sub(r"甲", r"甲.*?", sRet)
        
        
        for i in range(len(read_data)):
            place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
            if re.search(sRet, place_and_text):
                
                read_data_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
                read_data_Month = read_data_time.month
                read_data_Year = read_data_time.year
                if (Planned_start_month <= read_data_Month <= Planned_month) and (read_data_Year == Planned_year):
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = read_data_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
        remind(Source_data, line, setMonth, Planned_month,year_name='计划结束日期')  
    
    Source_data['计划开始日期'] = pd.to_datetime(Source_data['计划开始日期']).dt.strftime('%Y-%m-%d')
    Source_data['计划结束日期'] = pd.to_datetime(Source_data['计划结束日期']).dt.strftime('%Y-%m-%d')
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="1、架空线路红外检测", startrow=2, startcol=0, index=False)
    
    return Source_data

if __name__ == '__main__':
    data = main_1(4)
    