import pandas as pd
from pathlib import Path
def load_excel_files(file_pattern):
    
    
    return list(Path().glob(file_pattern))


output_file = load_excel_files('*预试检测计划*.xlsx')
if output_file:
    output_file = output_file[0]  
else:
    print("未找到符合条件的预试检测计划文件。")
sheet_name = '三跨两临近重点区段'
data = pd.read_excel(output_file,sheet_name='重要跨越区段测温',skiprows=[0])
print(data)