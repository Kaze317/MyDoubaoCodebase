import calendar
from datetime import datetime
import pandas as pd

def amount_Plan(data, month, columns_extract, years=2025):
    
    data = data[columns_extract]
    
    data['计划结束日期'] = pd.to_datetime(data['计划结束日期'], errors='coerce')
    
    data_filtered = data[(data['计划结束日期'].dt.year == years) & (data['计划结束日期'].dt.month <= month)]
    
    data_small_completed = data_filtered[data_filtered['完成情况'] == '已完成']
    
    Planned_total = len(data_filtered) - len(data_small_completed)
    
    
    data_filtered_completed = data[data['完成情况'] == '已完成']
    Planned_completion = len(data_filtered_completed)
    return Planned_total, Planned_completion  

