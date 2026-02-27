import glob
from datetime import datetime

import pandas as pd


def Month_Stat_Data(data, month, columns_extract):  
    now_data = data[data['完成月份'] == f'{month}月份已完成']
    stat = len(now_data)
    new_data = data[data['计划临期提醒'] == f'{month}月需要提醒']
    cont_data = new_data[columns_extract]
    return cont_data, stat


def content_data(data, text):  
    if len(data) == 0:
        content = f'{text}暂无提醒数据;'
    else:
        
        unique_centers = data['责任中心'].unique()
        
        result = "涉及" + "、".join(unique_centers)
        content = f'{text}待完成数据{len(data)}条,{result};'
    return content


def amount_Plan(data, month, columns_extract):
    
    data = data[columns_extract].copy()
    
    data['计划开始日期'] = pd.to_datetime(data['计划开始日期'], errors='coerce')
    
    data_filtered = data[data['计划开始日期'].dt.month <= month]
    
    data_small = data[data['计划开始日期'].dt.month < month]
    data_small_completed = data_small[data_small['完成情况'] == '已完成']
    
    Planned_total = len(data_filtered) - len(data_small_completed)
    
    
    data_filtered_completed = data[data['完成情况'] == '已完成']
    Planned_completion = len(data_filtered_completed)
    return Planned_total, Planned_completion  


def data(Path, Sheet_name, Skiprows):
    Source_data = pd.read_excel(Path, sheet_name=Sheet_name, skiprows=Skiprows)
    return Source_data


def main(now_month):
    path = {
        'path': './*预试检测计划*.xlsx',
    }
    paths = {}
    for key, pattern in path.items():
        matched_files = glob.glob(pattern)
        paths[key] = matched_files[0] if matched_files else None
    Source_path = paths['path']
    plan1 = data(Source_path, "1、架空线路红外检测", [0, 1])
    plan1_CW = data(Source_path, "1、架空线路红外检测（重要交跨管控要求）", [0])
    plan2 = data(Source_path, "2、架空线路接地电阻测试", [0])
    plan3 = data(Source_path, "3、电缆线路交叉互联预试", [0])
    plan4 = data(Source_path, "4、终端场避雷器试验", [0])
    plan5 = data(Source_path, "5、电缆护套环流检测", [0])
    plan6 = data(Source_path, "6、电缆终端红外检测", [0])
    plan7 = data(Source_path, "7、避雷器红外检测", [0])
    plan8 = data(Source_path, "8、非直埋式中间接头红外检测 ", [0])

    
    data_1, number_1 = Month_Stat_Data(data=plan1, month=now_month,
                                       columns_extract=['工作类型', '计划类型', '电压等级', '线路重要度', '线路名称',
                                                        '作业来源',
                                                        '设备设施名称', '作业方式', '计划开始日期', '计划结束日期',
                                                        '是否停电',
                                                        '责任单位', '中心负责人', '线路专责人', '责任中心',
                                                        '计划完成数',
                                                        '计划临期提醒'])
    data_2, number_2 = Month_Stat_Data(data=plan2, month=now_month,
                                       columns_extract=['工作类型', '计划类型', '电压等级', '线路重要度', '线路名称',
                                                        '杆塔数量（基）', '计划开始日期', '计划结束日期', '是否停电',
                                                        '责任单位', '中心负责人', '线路专责人', '责任中心',
                                                        '计划临期提醒'])
    data_3, number_3 = Month_Stat_Data(data=plan3, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '预试到期时间', '计划开始日期', '计划结束日期', '是否停电',
                                                        '责任单位', '中心负责人', '责任中心', '计划临期提醒'])
    data_4, number_4 = Month_Stat_Data(data=plan4, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度',
                                                        '设备设施名称',
                                                        '工作内容', '预试到期时间', '计划开始日期', '计划结束日期',
                                                        '是否停电',
                                                        '责任单位', '中心负责人', '责任中心', '计划完成数（相）',
                                                        '计划临期提醒'])
    data_5, number_5 = Month_Stat_Data(data=plan5, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '计划完成数(相）', '计划临期提醒'])
    data_6, number_6 = Month_Stat_Data(data=plan6, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '每次计划完成数（相）', '计划临期提醒'])
    data_7, number_7 = Month_Stat_Data(data=plan7, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '计划完成数(相）', '计划临期提醒'])
    data_8, number_8 = Month_Stat_Data(data=plan8, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '每次计划完成数（相）', '计划临期提醒'])

    data_1_CW, number_1_CW = Month_Stat_Data(data=plan1_CW, month=now_month,
                                             columns_extract=['工作类型', '计划类型', '电压等级', '线路重要度',
                                                              '线路名称',
                                                              '作业来源',
                                                              '设备设施名称', '作业方式', '计划开始日期',
                                                              '计划结束日期',
                                                              '是否停电',
                                                              '责任单位', '中心负责人', '线路专责人', '责任中心',
                                                              '计划完成数',
                                                              '计划临期提醒'])

    
    plan_sum1, plan_com1 = amount_Plan(data=plan1, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum1_CW, plan_com1_CW = amount_Plan(data=plan1_CW, month=now_month,
                                             columns_extract=['计划开始日期', '完成情况'])
    plan_sum2, plan_com2 = amount_Plan(data=plan2, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum3, plan_com3 = amount_Plan(data=plan3, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum4, plan_com4 = amount_Plan(data=plan4, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum5, plan_com5 = amount_Plan(data=plan5, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum6, plan_com6 = amount_Plan(data=plan6, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum7, plan_com7 = amount_Plan(data=plan7, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])
    plan_sum8, plan_com8 = amount_Plan(data=plan8, month=now_month,
                                       columns_extract=['计划开始日期', '完成情况'])

    print("正在写入预试月报完成情况")
    Performance = {
        "预试项目":
            ['架空线路红外检测（条）', '重要交叉跨越区段红外测温（回）', '接地电阻测试（回）', '交叉互联试验（回）',
             '避雷器试验（回）', '护套环流（回）', '电缆终端红外检测（回）', '避雷器红外检测（回）',
             '非直埋式中间接头红外检测（回）', '局放试验（回）', '高压电缆T接筒SF6气体测试（处）', '电缆桥检测',
             '接地电阻系统阻抗检测', '瓷套终端油面检测'],
        "年度总计划量": [None] * 14,
        "年度总完成量": [plan_com1, plan_com1_CW, plan_com2,
                         plan_com3, plan_com4, plan_com5, plan_com6,
                         plan_com7, plan_com8, None, None, None, None, None],
        "年度计划完成率": [None] * 14,
        f"{now_month}月计划量": [plan_sum1, plan_sum1_CW, plan_sum2,
                                 plan_sum3, plan_sum4, plan_sum5, plan_sum6,
                                 plan_sum7, plan_sum8, None, None, None, None, None],
        f"{now_month}月完成量":
            [number_1, number_1_CW, number_2,
             number_3, number_4, number_5, number_6,
             number_7, number_8, None, None, None, None, None],
        f"{now_month}月计划完成率": [None] * 14,
        "异常情况": [None] * 14
    }
    Performance_data = pd.DataFrame(Performance)
    Performance_data.to_excel(f"{now_month}月份预试月报完成情况.xlsx", index=False)
    print("已完成")


if __name__ == '__main__':
    while True:
        now_month = input("请输入需要核查的月份：")
        if now_month.isdigit():  
            break  
        else:
            print("输入无效，请输入数字。")  
    now_month = int(now_month)
    main(now_month)
