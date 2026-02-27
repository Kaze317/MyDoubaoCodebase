import pandas as pd

from Plan1 import main_1
from Plan2 import main_2
from Plan3 import main_3
from Plan4 import main_4
from Plan5 import main_5
from Plan6 import main_6
from Plan7 import main_7
from Plan8 import main_8

from new_Plan1_cw_xs import new_main_CW_XS
from datetime import datetime


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


def amount_Plan(data, month, columns_extract, years=2025):
    
    data = data[columns_extract]
    
    data['计划结束日期'] = pd.to_datetime(data['计划结束日期'], errors='coerce')
    
    data_filtered = data[(data['计划结束日期'].dt.year == years) & (data['计划结束日期'].dt.month == month)]
    
    data_small_completed = data_filtered[data_filtered['完成情况'] == '已完成']
    
    
    Planned_total = len(data_filtered)
    
    
    data_filtered_completed = data[data['完成情况'] == '已完成']
    Planned_completion = len(data_filtered_completed)
    return Planned_total, Planned_completion  


if __name__ == '__main__':

    
    while True:
        now_month = input("请输入需要核查的月份：")
        if now_month.isdigit():  
            break  
        else:
            print("输入无效，请输入数字。")  
    now_month = int(now_month)
    data_main1 = main_1(now_month)
    data_main1_CW = new_main_CW_XS(now_month)
    data_main2 = main_2(now_month)
    data_main3 = main_3(now_month)
    data_main4 = main_4(now_month)
    data_main5 = main_5(now_month)
    data_main6 = main_6(now_month) 
    data_main7 = main_7(now_month) 
    data_main8 = main_8(now_month)
    
    data_1, number_1 = Month_Stat_Data(data=data_main1, month=now_month,
                                       columns_extract=['工作类型', '计划类型', '电压等级', '线路重要度', '线路名称',
                                                        '作业来源',
                                                        '设备设施名称', '作业方式', '计划开始日期', '计划结束日期',
                                                        '是否停电',
                                                        '责任单位', '中心负责人', '线路专责人', '责任中心',
                                                        '计划完成数',
                                                        '计划临期提醒'])
    data_2, number_2 = Month_Stat_Data(data=data_main2, month=now_month,
                                       columns_extract=['工作类型', '计划类型', '电压等级', '线路重要度', '线路名称',
                                                        '杆塔数量（基）', '计划开始日期', '计划结束日期', '是否停电',
                                                        '责任单位', '中心负责人', '线路专责人', '责任中心',
                                                        '计划临期提醒'])
    data_3, number_3 = Month_Stat_Data(data=data_main3, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '预试到期时间', '计划开始日期', '计划结束日期', '是否停电',
                                                        '责任单位', '中心负责人', '责任中心', '计划临期提醒'])
    data_4, number_4 = Month_Stat_Data(data=data_main4, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度',
                                                        '设备设施名称',
                                                        '工作内容', '预试到期时间', '计划开始日期', '计划结束日期',
                                                        '是否停电',
                                                        '责任单位', '中心负责人', '责任中心', '计划完成数（相）',
                                                        '计划临期提醒'])
    data_5, number_5 = Month_Stat_Data(data=data_main5, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '计划完成数(相）', '计划临期提醒'])
    data_6, number_6 = Month_Stat_Data(data=data_main6, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '每次计划完成数（相）', '计划临期提醒'])
    data_7, number_7 = Month_Stat_Data(data=data_main7, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '计划完成数(相）', '计划临期提醒'])
    data_8, number_8 = Month_Stat_Data(data=data_main8, month=now_month,
                                       columns_extract=['工作类型', '电压等级', '变电站/线路', '线路重要度', '工作内容',
                                                        '计划开始日期', '计划结束日期', '是否停电', '责任单位',
                                                        '中心负责人', '责任中心', '每次计划完成数（相）', '计划临期提醒'])

    data_1_CW, number_1_CW = Month_Stat_Data(data=data_main1_CW, month=now_month,
                                       columns_extract=['工作类型', '计划类型', '电压等级', '线路重要度', '线路名称',
                                                        '作业来源',
                                                        '设备设施名称', '作业方式', '计划开始日期', '计划结束日期',
                                                        '是否停电',
                                                        '责任单位', '中心负责人', '线路专责人', '责任中心',
                                                        '计划完成数',
                                                        '计划临期提醒'])


    
    content_1 = content_data(data=data_1, text='1.架空线路红外检测')
    content_1_CW = content_data(data=data_1_CW, text='2.架空线路红外检测（重要交跨管控要求）')
    content_2 = content_data(data=data_2, text='3.架空线路接地电阻测试')
    content_3 = content_data(data=data_3, text='4.电缆线路交叉互联预试')
    content_4 = content_data(data=data_4, text='5.终端场避雷器试验')
    content_5 = content_data(data=data_5, text='6.电缆护套环流检测')
    content_6 = content_data(data=data_6, text='7.电缆终端红外检测')
    content_7 = content_data(data=data_7, text='8.避雷器红外检测')
    content_8 = content_data(data=data_8, text='9.非直埋式中间接头红外检测')
    
    plan_sum1, plan_com1 = amount_Plan(data=data_main1, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum1_CW, plan_com1_CW = amount_Plan(data=data_main1_CW, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum2, plan_com2 = amount_Plan(data=data_main2, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum3, plan_com3 = amount_Plan(data=data_main3, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum4, plan_com4 = amount_Plan(data=data_main4, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum5, plan_com5 = amount_Plan(data=data_main5, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum6, plan_com6 = amount_Plan(data=data_main6, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum7, plan_com7 = amount_Plan(data=data_main7, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])
    plan_sum8, plan_com8 = amount_Plan(data=data_main8, month=now_month,
                                       columns_extract=['计划结束日期', '完成情况'])

    
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_year = datetime.now().year
    
    
    
    
    
    
    all_content = (f'{current_date}   {now_month}月到期预试计划RPA智能监控核查预警数据：'
                   f'\n{content_1}\n{content_1_CW}\n{content_2}'
                   f'\n{content_3}\n{content_4}\n{content_5}\n{content_6}'
                   f'\n{content_7}\n{content_8}'
                   f'\n具体数据详见《输电管理二所{current_year}年{now_month}月预试计划核查问题记录表》')
    print('正在写入提示内容到“文本内容.txt”中')
    with open('文本内容.txt', 'w', encoding='utf-8') as file:
        file.write(all_content)
    print("写入成功")
    
    print('正在写入数据到核查问题记录表')
    with pd.ExcelWriter(f'《输电二所{current_year}年{now_month}月预试计划核查问题记录表》.xlsx') as writer:
        data_1.to_excel(writer, sheet_name='架空线路红外检测', index=False)
        data_1_CW.to_excel(writer, sheet_name='架空线路红外检测（重要交跨管控要求）', index=False)
        
        data_2.to_excel(writer, sheet_name='架空线路接地电阻测试', index=False)
        data_3.to_excel(writer, sheet_name='电缆线路交叉互联预试', index=False)
        data_4.to_excel(writer, sheet_name='终端场避雷器试验', index=False)
        data_5.to_excel(writer, sheet_name='电缆护套环流检测', index=False)
        data_6.to_excel(writer, sheet_name='电缆终端红外检测', index=False)
        data_7.to_excel(writer, sheet_name='避雷器红外检测', index=False)
        data_8.to_excel(writer, sheet_name='非直埋式中间接头红外检测 ', index=False)
    print("写入成功")
    
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
    print("")
