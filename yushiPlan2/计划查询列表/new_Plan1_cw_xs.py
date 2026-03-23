import glob
import re
import warnings
from datetime import datetime
import pandas as pd
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
    """
    kind='start' -> 匹配计划开始日期/时间
    kind='end'   -> 匹配计划结束日期/时间
    """
    cols = [c for c in df.columns if isinstance(c, str)]

    if kind == "start":
        targets = ["计划开始日期", "计划开始时间"]
        fuzzy_key = "计划开始"
    else:
        targets = ["计划结束日期", "计划结束时间"]
        fuzzy_key = "计划结束"

    # 1) 优先精确命中
    for t in targets:
        c = find_column(df, t)
        if c is not None:
            return c

    # 2) 模糊：包含 计划开始/计划结束 且包含 日期/时间
    for c in cols:
        if fuzzy_key in c and ("日期" in c or "时间" in c):
            return c

    return None


def load_source_with_auto_header(source_path, sheet_name):
    """
    自动识别表头行，避免“标题行被当成列名”导致找不到业务列。
    兼容：计划开始日期/计划开始时间、计划结束日期/计划结束时间。
    """
    preview = pd.read_excel(source_path, sheet_name=sheet_name, header=None)
    preview = preview.iloc[:60].copy()

    def _has_line_name(row_text):
        return ("线路" in row_text and "名称" in row_text) or ("线路名称" in row_text)

    def _has_plan_start(row_text):
        return ("计划开始" in row_text) and (("日期" in row_text) or ("时间" in row_text))

    def _has_plan_end(row_text):
        return ("计划结束" in row_text) and (("日期" in row_text) or ("时间" in row_text))

    header_row = None
    for r in range(len(preview)):
        row_vals = [str(v).strip() for v in preview.iloc[r].tolist() if pd.notna(v)]
        row_text = "|".join(row_vals)
        if _has_line_name(row_text) and _has_plan_start(row_text) and _has_plan_end(row_text):
            header_row = r
            break

    # 方案1：识别到表头行
    if header_row is not None:
        df = pd.read_excel(source_path, sheet_name=sheet_name, header=header_row)
        normalize_columns(df)
        return df

    # 方案2：常见模板回退（不同 skiprows）
    candidates = [
        {"skiprows": [0]},
        {"skiprows": [0, 1]},
        {"skiprows": [0, 1, 2]},
        {"skiprows": [1]},
        {"skiprows": [2]},
        {"skiprows": [3]},
        {"header": 1},
        {"header": 2},
        {"header": 3},
        {"header": 4},
    ]

    for kw in candidates:
        try:
            df = pd.read_excel(source_path, sheet_name=sheet_name, **kw)
            normalize_columns(df)
            cols_text = "|".join([str(c) for c in df.columns])
            if _has_line_name(cols_text) and _has_plan_start(cols_text) and _has_plan_end(cols_text):
                return df
        except Exception:
            continue

    # 最后兜底：返回一个可读对象（后续会抛出带列名的 KeyError）
    df = pd.read_excel(source_path, sheet_name=sheet_name, skiprows=[0])
    normalize_columns(df)
    return df



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
    normalize_columns(Source_data)

    finish_col = find_column(Source_data, "完成情况")
    work_content_col = find_column(Source_data, "工作地点和内容")
    plan_id_col = find_column(Source_data, "计划编号")
    start_col, end_col = ensure_date_columns(Source_data)
    finish_month_col = find_column(Source_data, "完成月份")

    if work_content_col is None or plan_id_col is None:
        print("[warn] new_Plan1_cw_xs Data_Backfill 缺少工作地点和内容/计划编号列。")

    Source_data.iloc[line, Source_data.columns.get_loc(start_col)] = start_time
    Source_data.iloc[line, Source_data.columns.get_loc(end_col)] = end_time

    if plan_id_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(plan_id_col)] = ID
    if work_content_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(work_content_col)] = place_and_text
    if finish_month_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(finish_month_col)] = f"{setMonth}月份已完成"
    if finish_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(finish_col)] = "已完成"



def new_main_CW_XS(setMonth):
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
    
    
    Source_data = load_source_with_auto_header(
        Source_path,
        "1、架空线路红外检测"
    )

    planned_start_col = pick_plan_date_column(Source_data, kind="start")
    planned_end_col = pick_plan_date_column(Source_data, kind="end")
    if planned_start_col is None or planned_end_col is None:
        raise KeyError(
            "在工作表中找不到 '计划开始日期/时间' 或 '计划结束日期/时间' 列。"
            f"当前列名: {list(Source_data.columns)}"
        )

    Source_data[planned_start_col] = Source_data[planned_start_col].apply(process_date)
    Source_data[planned_end_col] = Source_data[planned_end_col].apply(process_date)

    read_data = pd.read_excel(read_path, sheet_name="计划查询列表")
    read_data = read_data[['计划编号', '工作地点', '工作内容', '实际开始时间', '实际结束时间', '工作类别']]
    
    read_data = read_data[(read_data['工作地点'].str.contains('交跨|交叉跨越|重要交跨|重要跨越测温')) | (
        read_data['工作内容'].str.contains('交跨|交叉跨越|重要交跨|重要跨越测温'))]

    line_name_col = find_column(Source_data, "线路名称")
    line_importance_col = find_column(Source_data, "线路重要度")
    voltage_col = find_column(Source_data, "电压等级")
    if any(c is None for c in [line_name_col, line_importance_col, voltage_col]):
        raise KeyError(
            f"在工作表中找不到 '线路名称/线路重要度/电压等级' 必要列。当前列名: {list(Source_data.columns)}"
        )
    
    print(f"1、架空线路红外检测（重要交跨管控要求）已搜到关键字数据共有：{len(read_data)}")

    for line in range(len(Source_data)):
        line_importance = Source_data.at[line, line_importance_col]
        Planned_end_time = Source_data.at[line, planned_end_col]
        Planned_start_time = Source_data.at[line, planned_start_col]
        voltage = Source_data.at[line, voltage_col]

        Planned_month = Planned_end_time.month
        Planned_year = Planned_end_time.year
        Planned_start_month = Planned_start_time.month
        line_name = Source_data.at[line, line_name_col]
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
                    planned_start_date=Planned_start_time,
                    actual_start_time=actual_start_time,
                    actual_end_time=actual_end_time,
                ):
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = actual_start_time
                    end_time = actual_end_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
        remind(Source_data, line, setMonth, Planned_month,year_name='计划结束日期')  
    
    Source_data[planned_start_col] = pd.to_datetime(Source_data[planned_start_col]).dt.strftime('%Y-%m-%d')
    Source_data[planned_end_col] = pd.to_datetime(Source_data[planned_end_col]).dt.strftime('%Y-%m-%d')
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="1、架空线路红外检测（重要交跨管控要求）", startrow=1, startcol=0, index=False)
    
    return Source_data

if __name__ == '__main__':
    data = new_main_CW_XS(6)
    