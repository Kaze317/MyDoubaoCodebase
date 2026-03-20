import glob
import re
import warnings
from datetime import datetime
import pandas as pd
import ast
from Plan1 import remind, should_complete_by_importance_range, normalize_columns, find_column, ensure_date_columns
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


def pick_plan_date_column(df, kind="start"):
    cols = [c for c in df.columns if isinstance(c, str)]
    if kind == "start":
        targets = ["计划开始日期", "计划开始时间"]
        fuzzy_key = "计划开始"
    else:
        targets = ["计划结束日期", "计划结束时间"]
        fuzzy_key = "计划结束"

    for t in targets:
        c = find_column(df, t)
        if c is not None:
            return c
    for c in cols:
        if fuzzy_key in c and ("日期" in c or "时间" in c):
            return c
    return None


def gantahao(place_and_text):
    
    towerID = re.findall(r"#(\d{2,3})-#(\d{2,3})", place_and_text)
    
    towerID_merge = ""
    for number in range(len(towerID)):
        one_towerID = f"#{towerID[number][0]}-#{towerID[number][1]}"
        towerID_merge += one_towerID + "\n"
    towerID_merge = towerID_merge.rstrip("\n")  
    return towerID_merge


def Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth, Source_data, new_zone, new_data):
    normalize_columns(Source_data)

    work_content_col = find_column(Source_data, "工作地点和内容") or find_column(Source_data, "备注")
    plan_id_col = find_column(Source_data, "计划编号")
    start_col, end_col = ensure_date_columns(Source_data)
    pending_zone_col = find_column(Source_data, "待完成线路段") or find_column(Source_data, "线路段")
    done_zone_col = find_column(Source_data, "已完成线路段")
    finish_col = find_column(Source_data, "完成情况")
    finish_month_col = find_column(Source_data, "完成月份")

    if any(c is None for c in [start_col, end_col, pending_zone_col]):
        print(f"[warn] Plan2 Data_Backfill 找不到关键列，跳过回填。当前列名: {list(Source_data.columns)}")
        return

    if len(new_data) != 0:
        if work_content_col is not None:
            Source_data.iloc[line, Source_data.columns.get_loc(work_content_col)] = str(
                Source_data.iloc[line, Source_data.columns.get_loc(work_content_col)]
            ) + "\n" + place_and_text

        if plan_id_col is not None:
            Source_data.iloc[line, Source_data.columns.get_loc(plan_id_col)] = str(
                Source_data.iloc[line, Source_data.columns.get_loc(plan_id_col)]
            ) + "\n" + str(ID)

        Source_data.iloc[line, Source_data.columns.get_loc(start_col)] = str(
            Source_data.iloc[line, Source_data.columns.get_loc(start_col)]
        ) + "\n" + str(start_time)

        Source_data.iloc[line, Source_data.columns.get_loc(pending_zone_col)] = str(new_zone)

        if done_zone_col is not None:
            Source_data.iloc[line, Source_data.columns.get_loc(done_zone_col)] = str(
                Source_data.iloc[line, Source_data.columns.get_loc(done_zone_col)]
            ) + "\n" + str(new_data)

        if finish_col is not None:
            Source_data.iloc[line, Source_data.columns.get_loc(finish_col)] = '已完成'
        if finish_month_col is not None:
            Source_data.iloc[line, Source_data.columns.get_loc(finish_month_col)] = f"{setMonth}月份已完成"

        Source_data.iloc[line, Source_data.columns.get_loc(end_col)] = end_time


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
    normalize_columns(Source_data)

    planned_start_col = pick_plan_date_column(Source_data, kind="start")
    planned_end_col = pick_plan_date_column(Source_data, kind="end")
    line_importance_col = find_column(Source_data, "线路重要度")
    voltage_col = find_column(Source_data, "电压等级")
    line_name_col = find_column(Source_data, "线路名称")
    pending_zone_col = find_column(Source_data, "待完成线路段") or find_column(Source_data, "线路段")

    if any(c is None for c in [planned_start_col, planned_end_col, line_importance_col, voltage_col, line_name_col, pending_zone_col]):
        raise KeyError(
            "Plan2 找不到必要列（计划开始/结束、线路重要度、电压等级、线路名称、待完成线路段/线路段）。"
            f" 当前列名: {list(Source_data.columns)}"
        )

    Source_data[planned_start_col] = Source_data[planned_start_col].apply(process_date)
    Source_data[planned_end_col] = Source_data[planned_end_col].apply(process_date)

    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间']]
    read_data = read_data[(read_data['工作地点'].str.contains('接地电阻')) | (
        read_data['工作内容'].str.contains('接地电阻'))]
    print(f"2、架空线路接地电阻测试已搜到关键字数据共有：{len(read_data)}")

    for line in range(len(Source_data)):
        line_importance = Source_data.at[line, line_importance_col]
        voltage = Source_data.at[line, voltage_col]
        planned_start_date = Source_data.at[line, planned_start_col]

        zone = Source_data.at[line, pending_zone_col]
        try:
            list_zone = ast.literal_eval(zone) if isinstance(zone, str) else []
        except Exception:
            list_zone = []

        Planned_end_time = process_date(Source_data.at[line, planned_end_col])
        if pd.isna(Planned_end_time):
            continue
        Planned_month = Planned_end_time.month

        line_name = Source_data.at[line, line_name_col]
        sRet = re.sub(r"乙", r".*?乙", str(line_name))
        sRet = re.sub(r"甲", r"甲.*?", sRet)

        for i in range(len(read_data)):
            place_and_text = str(read_data.iloc[i]["工作地点"]) + str(read_data.iloc[i]["工作内容"])
            new_data = split_text(place_and_text)
            for ij in new_data:
                zone_name = str(Source_data.at[line, pending_zone_col])
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

                    numbers = extract_numbers_with_hash(ij)
                    check_list = complete_numbers(numbers)
                    new_zone, done_data = item_ziduan(all_list=list_zone, data=check_list)
                    Data_Backfill(line, line_name, ij, ID, actual_start_time, actual_end_time, setMonth, Source_data, new_zone, done_data)

        remind(Source_data, line, setMonth, Planned_month, year_name="计划结束日期")

    Source_data[planned_start_col] = pd.to_datetime(Source_data[planned_start_col]).dt.strftime('%Y-%m-%d')
    Source_data[planned_end_col] = pd.to_datetime(Source_data[planned_end_col]).dt.strftime('%Y-%m-%d')

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
