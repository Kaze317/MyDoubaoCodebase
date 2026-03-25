import glob
import os
import sys
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


def normalize_columns(df):
    """
    把 DataFrame 列名做一次统一清洗：
    - 去掉首尾空白
    - 把非断行空格(NBSP)转成普通空格
    - 把连续空白压缩成单个空格
    目的：避免Excel列名带空格/换行导致 KeyError。
    """
    import re as _re
    cleaned = []
    for c in df.columns:
        if isinstance(c, str):
            c2 = c.replace("\xa0", " ")
            c2 = c2.strip()
            c2 = _re.sub(r"\s+", " ", c2)
            cleaned.append(c2)
        else:
            cleaned.append(c)
    df.columns = cleaned
    return df


def find_column(df, target_name):
    """
    查找列名：
    1) 精确匹配（strip 后）
    2) 模糊匹配：列名包含 target_name
    返回列名字符串；找不到返回 None
    """
    if target_name in df.columns:
        return target_name
    candidates = [c for c in df.columns if isinstance(c, str) and target_name in c]
    if len(candidates) == 1:
        return candidates[0]
    return None


def ensure_column(df, col_name, default_value=""):
    if col_name not in df.columns:
        df[col_name] = default_value
    return col_name


def ensure_date_columns(df):
    """确保存在“实际开始日期”“实际结束日期”，不存在则自动新建。"""
    start_col = find_column(df, "实际开始日期") or find_column(df, "实际开始时间")
    end_col = find_column(df, "实际结束日期") or find_column(df, "实际结束时间")

    if start_col is None:
        start_col = ensure_column(df, "实际开始日期", "")
    if end_col is None:
        end_col = ensure_column(df, "实际结束日期", "")

    return start_col, end_col


def get_range_start_end_months(line_importance, voltage, planned_start_month):
    """
    由“线路重要度 + 电压等级 + 计划开始日期(月份)”推导允许完成的时间范围(按月)。
    规则：
    - 关键/重要：2月1次 => (1-2, 3-4, 5-6, ...)
    - 一般/关注/其余时段：110kV上/下半年；220kV每季度
    """
    line_importance = str(line_importance)
    voltage = str(voltage)
    planned_start_month = int(planned_start_month)

    # 关键/重要：两个月一窗
    if re.search(r"关键|重要", line_importance):
        start_month = ((planned_start_month - 1) // 2) * 2 + 1
        end_month = min(start_month + 1, 12)
        return start_month, end_month

    # 一般/关注/其余：按电压等级
    if "220" in voltage:
        q_start = ((planned_start_month - 1) // 3) * 3 + 1
        q_end = min(q_start + 2, 12)
        return q_start, q_end

    # 默认110kV：上半年/下半年
    if planned_start_month <= 6:
        return 1, 6
    return 7, 12


def should_complete_by_importance_range(line_importance, voltage, planned_start_date, actual_start_time, actual_end_time):
    """
    当前按“是否匹配到记录”回填：
    - 只要实际开始/结束时间有效，就允许回填
    - 不再按重要度/季度/半年窗口限制
    """
    if pd.isna(actual_start_time) or pd.isna(actual_end_time):
        return False
    return True



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
    start_col = find_column(Source_data, "实际开始日期") or find_column(Source_data, "实际开始时间")
    end_col = find_column(Source_data, "实际结束日期") or find_column(Source_data, "实际结束时间")
    finish_month_col = find_column(Source_data, "完成月份")

    # 只要求“回填必要列”存在即可执行
    if any(c is None for c in [work_content_col, plan_id_col, start_col, end_col]):
        print("[warn] Data_Backfill 缺少回填必要列(工作地点和内容/计划编号/实际开始/实际结束)，跳过回填。")
        return

    # 回填实际开始/结束日期（匹配到就写）
    Source_data.iloc[line, Source_data.columns.get_loc(plan_id_col)] = ID
    Source_data.iloc[line, Source_data.columns.get_loc(work_content_col)] = place_and_text
    Source_data.iloc[line, Source_data.columns.get_loc(start_col)] = start_time
    Source_data.iloc[line, Source_data.columns.get_loc(end_col)] = end_time

    # 有“完成月份/完成情况”就写，没有就跳过
    if finish_month_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(finish_month_col)] = f"{setMonth}月份已完成"
    if finish_col is not None:
        Source_data.iloc[line, Source_data.columns.get_loc(finish_col)] = "已完成"


def remind(Source_data,line,setMonth,Planned_month,year_name): 
    normalize_columns(Source_data)
    finish_col = find_column(Source_data, "完成情况")
    if finish_col is None:
        # 模板无“完成情况”时，静默跳过提醒，不影响回填
        return

    performance = Source_data.at[line, finish_col]
    
    if performance == "已完成":
        return

    planned_start_col = find_column(Source_data, "计划开始日期")
    if planned_start_col is None:
        print("[warn] 找不到列 '计划开始日期'，已跳过提醒。")
        return

    planned_start_date = process_date(Source_data.at[line, planned_start_col])
    if pd.isna(planned_start_date):
        return

    # 仍沿用你原来项目对年份的口径（默认只提醒2026年）
    if planned_start_date.year != 2026:
        return

    line_importance_col = find_column(Source_data, "线路重要度")
    voltage_col = find_column(Source_data, "电压等级")
    line_importance = Source_data.at[line, line_importance_col] if line_importance_col else ""
    voltage = Source_data.at[line, voltage_col] if voltage_col else ""
    _, due_end_month = get_range_start_end_months(
        line_importance=line_importance,
        voltage=voltage,
        planned_start_month=planned_start_date.month
    )

    remind_col = find_column(Source_data, "计划临期提醒")
    if remind_col is None:
        print("[warn] 找不到列 '计划临期提醒'，已跳过提醒写入。")
        return

    if setMonth == due_end_month:
        Source_data.iloc[line, Source_data.columns.get_loc(remind_col)] = f"{setMonth}月需要提醒"


def main_1(setMonth):
    setYear = "2026"

    # 优先在 exe 所在目录查找；其次当前工作目录；最后脚本目录
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    search_dirs = [
        exe_dir,
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__)),
    ]
    # 去重并保序
    search_dirs = list(dict.fromkeys(search_dirs))

    def _pick_first_file(name_keyword):
        for d in search_dirs:
            pattern = os.path.join(d, f"*{name_keyword}*.xlsx")
            matched_files = glob.glob(pattern)
            if matched_files:
                return matched_files[0]
        return None

    read_path = _pick_first_file("计划查询列表")
    Source_path = _pick_first_file("预试检测计划")

    if read_path is None:
        raise FileNotFoundError(
            "未找到‘计划查询列表’Excel文件。请将文件放到 exe 同目录，文件名包含‘计划查询列表’。"
        )
    if Source_path is None:
        raise FileNotFoundError(
            "未找到‘预试检测计划’Excel文件。请将文件放到 exe 同目录，文件名包含‘预试检测计划’。"
        )

    print(f"[路径] 计划查询列表文件: {read_path}")
    print(f"[路径] 预试检测计划文件: {Source_path}")

    Source_data = pd.read_excel(Source_path, sheet_name="1、架空线路红外检测", skiprows=[0,1])
    normalize_columns(Source_data)
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
        voltage = Source_data.at[line, "电压等级"]
        # Planned_year/Planned_start_month在旧逻辑里使用；新逻辑由 should_complete_by_importance_range 统一判断
        line_name = Source_data.at[line, "线路名称"]  
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
                    actual_end_time=actual_end_time
                ):
                    ID = read_data.iloc[i]["计划编号"]  
                    start_time = read_data.iloc[i]["实际开始时间"]
                    end_time = actual_end_time
                    Data_Backfill(line, line_name, place_and_text, ID, start_time, end_time, setMonth,Source_data)
        remind(Source_data, line, setMonth, Planned_month,year_name='计划结束日期')  
    
    Source_data['计划开始日期'] = pd.to_datetime(Source_data['计划开始日期']).dt.strftime('%Y-%m-%d')
    Source_data['计划结束日期'] = pd.to_datetime(Source_data['计划结束日期']).dt.strftime('%Y-%m-%d')
    
    with pd.ExcelWriter(Source_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        Source_data.to_excel(writer, sheet_name="1、架空线路红外检测", startrow=2, startcol=0, index=False)
    
    return Source_data

if __name__ == '__main__':
    data = main_1(4)
    