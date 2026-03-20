import glob
import re
import warnings
from datetime import datetime
import pandas as pd
import ast
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

def gantahao(place_and_text):
    
    towerID = re.findall(r"#(\d{2,3})-#(\d{2,3})", place_and_text)
    
    towerID_merge = ""
    for number in range(len(towerID)):
        one_towerID = f"#{towerID[number][0]}-#{towerID[number][1]}"
        towerID_merge += one_towerID + "\n"
    towerID_merge = towerID_merge.rstrip("\n")  
    return towerID_merge


def Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data,new_zone,new_data):
    
    
    
    
    
    
    
    
    
    
    
    
    
    if len(new_data) != 0:
        Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")] = str(
            Source_data.iloc[line, Source_data.columns.get_loc("工作地点和内容")]) + "\n" + place_and_text
        Source_data.iloc[line, Source_data.columns.get_loc("计划编号")] = str(
            Source_data.iloc[line, Source_data.columns.get_loc("计划编号")]) + "\n" + ID
        Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")] = str(
            Source_data.iloc[line, Source_data.columns.get_loc("实际开始日期")]) + "\n" + start_time
        Source_data.iloc[line, Source_data.columns.get_loc("待完成线路段")] = str(new_zone)
        Source_data.iloc[line, Source_data.columns.get_loc("已完成线路段")] = str(
            Source_data.iloc[line, Source_data.columns.get_loc("已完成线路段")]) + "\n" + str(new_data)
        
        Source_data.iloc[line, Source_data.columns.get_loc("完成情况")] = '已完成'
        Source_data.iloc[line, Source_data.columns.get_loc("完成月份")] = f"{setMonth}月份已完成"
        Source_data.iloc[line, Source_data.columns.get_loc("实际结束日期")] = end_time

def complement(Source_data): 
    def extract_segments(text):  
        if isinstance(text, str):  
            return re.findall(r'#\d+-\d+|#\d+', text)
        return []  

    def fill_missing_numbers(arr):
        
        if len(arr) == 0 or len(arr) % 2 != 0:
            return arr

        filled = []
        for i in range(0, len(arr), 2):  
            start = int(arr[i][1:])
            end = int(arr[i + 1][1:])
            
            for num in range(start, end + 1):
                filled.append(f'#{num:02d}')
        return filled
    
    Source_data['线路段'] = Source_data['线路段'].fillna('').astype(str)
    
    Source_data['提取结果'] = Source_data['线路段'].apply(extract_segments)
    print(Source_data['提取结果'])
    
    Source_data['线路段#号数量'] = Source_data['线路段'].apply(lambda x: x.count('#'))
    Source_data['补全字段'] = Source_data['提取结果'].apply(fill_missing_numbers)
    Source_data['补全字段#号数量'] = Source_data['补全字段'].apply(len)
    new = Source_data[['线路段', '线路段#号数量', '补全字段', '提取结果', '补全字段#号数量']]
    new.to_excel('data.xlsx', index=False)
    

    
    
    
    
    
    
    
    


def item_ziduan(all_list,data):
    data_list = []  
    
    for item in data:
        if item in all_list:
            all_list.remove(item)
            data_list.append(item)
    return all_list,data_list


def extract_numbers_with_hash(text):
    return re.findall(r'(#\d+)', text)


def split_text(text):
    
    return re.split(r'[;；,，、。]', text)



def complete_numbers(numbers):
    if not numbers:  
        return []

    if len(numbers) == 2:
        
        start = int(numbers[0][1:])  
        end = int(numbers[1][1:])  

        
        return [f"#{i:02d}" for i in range(start, end + 1)]  
    else:
        return numbers


def main_2(setMonth):
    
    
    
    
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
    
    
    Source_data = pd.read_excel(Source_path, sheet_name="2、架空线路接地电阻测试", skiprows=[0])
    
    Source_data['计划开始日期'] = Source_data['计划开始日期'].apply(process_date)
    Source_data['计划结束日期'] = Source_data['计划结束日期'].apply(process_date)
    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间']]
    read_data = read_data[(read_data['工作地点'].str.contains('接地电阻')) | (
        read_data['工作内容'].str.contains('接地电阻'))]
    print(f"2、架空线路接地电阻测试已搜到关键字数据共有：{len(read_data)}")

    
    
    for line in range(len(Source_data)):
        line_importance = Source_data.at[line, "线路重要度"]  
        voltage = Source_data.at[line, "电压等级"]
        planned_start_date = Source_data.at[line, "计划开始日期"]
        zone = Source_data.at[line, "待完成线路段"]  
        list_zone = ast.literal_eval(zone)
        job_content = ""  
        Plan_number = ""  
        in_start_time = ""  
        in_end_time = ""  
        Planned_end_time = Source_data.at[line, '计划结束日期']
        Planned_end_time = process_date(Planned_end_time)  
        Planned_month = Planned_end_time.month  
        
        line_name = Source_data.at[line, "线路名称"]  
        sRet = re.sub(r"乙", r".*?乙", line_name)
        sRet = re.sub(r"甲", r"甲.*?", sRet)
        for i in range(len(read_data)):
            
            place_and_text = read_data.iloc[i]["工作地点"] + read_data.iloc[i]["工作内容"]  
            
            
            
            
            new_data =  split_text(place_and_text)
            for ij in new_data:
                zone_name = Source_data.at[line, "待完成线路段"]  
                if re.search(sRet, ij) and "[]" not in zone_name:  
                    ID = read_data.iloc[i]["计划编号"]  
                    actual_start_time = pd.to_datetime(read_data.iloc[i]["实际开始时间"])
                    actual_end_time = pd.to_datetime(read_data.iloc[i]["实际结束时间"])
                    if not should_complete_by_importance_range(
                        line_importance=line_importance,
                        voltage=voltage,
                        planned_start_date=planned_start_date,
                        actual_start_time=actual_start_time,
                        actual_end_time=actual_end_time,
                    ):
                        continue

                    start_time = actual_start_time
                    end_time = actual_end_time
                    end_time_year = end_time
                    
                    
                    numbers = extract_numbers_with_hash(ij)
                    
                    check_list = complete_numbers(numbers)
                    new_zone, new_data = item_ziduan(all_list=list_zone, data=check_list)
                    Data_Backfill(line, line_name, ij, ID, start_time, end_time, setMonth, Source_data, new_zone,
                                  new_data)
        remind(Source_data, line, setMonth, Planned_month,year_name="计划结束日期")  
    
    Source_data['计划开始日期'] = pd.to_datetime(Source_data['计划开始日期']).dt.strftime('%Y-%m-%d')
    Source_data['计划结束日期'] = pd.to_datetime(Source_data['计划结束日期']).dt.strftime('%Y-%m-%d')
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="2、架空线路接地电阻测试", startrow=1, startcol=0, index=False)
    return Source_data

def data_one():
    
    start = int(input("请输入第一个数字："))
    end = int(input("请输入第二个数字："))
    
    result = [f"#{i:02d}" for i in range(start, end + 1)]  
    
    print(result)

if __name__ == '__main__':
    now_time = 4
    main_2(now_time)
    
    
    
    
    
    
    pass


