import calendar
import os

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
import time
from datetime import datetime,timedelta
import time

def iframe_dingwei(driver,xpath):
    iframe = driver.find_element(By.XPATH, xpath)
    driver.switch_to_frame(iframe)
    return driver


def shouye(driver,text):
    # 进度--"首页"
    wait = WebDriverWait(driver, 10)
    # 点击左上角的九个点展开搜索功能
    nine = wait.until(EC.presence_of_element_located((By.XPATH, '//header/div/div/span')))
    driver.execute_script("arguments[0].click();", nine)
    time.sleep(2)
    # 点击搜索并搜索对应的内容
    search_input = driver.find_element(By.XPATH, '//input[@id="searchApp"]')
    search_input.clear()
    search_input.send_keys(text)
    search_button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="gmp-hamburg-search"]/div/span/i')))
    driver.execute_script("arguments[0].click();", search_button)
    search_text = wait.until(EC.presence_of_element_located((By.XPATH, f'//span[@title="{text}"]')))
    driver.execute_script("arguments[0].click();", search_text)
    # print(driver.title)

def start_time(wait,driver,times):
    date = pd.to_datetime(times)
    month = date.month
    day = date.day
    year = date.year
    month_str = f"{year}年 {month}月"  # 2024年 12月
    yearMonth_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[1]/table/thead/tr[1]/th[2]/div')
    if yearMonth_element.text != month_str:
        time.sleep(0.5)
        # 点击年月
        click_button = wait.until(
            EC.presence_of_element_located((By.XPATH, f'/html/body/div[5]/div[1]/div[1]/table/thead/tr[1]/th[2]/div')))
        driver.execute_script("arguments[0].click();", click_button)
        time.sleep(0.5)
        year_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[1]/div[2]/table/thead/tr/th[2]/div')
        if year_element.text != year:
            # 点击年
            year_click_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f'/html/body/div[5]/div[1]/div[2]/table/thead/tr/th[2]/div')))
            driver.execute_script("arguments[0].click();", year_click_button)
            time.sleep(0.5)
            # 选择年份
            year_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f'/html/body/div[5]/div[1]/div[3]/table/tbody/tr/td/span[text()="{year}"]')))
            driver.execute_script("arguments[0].click();", year_button)
            time.sleep(0.5)
            # 选择月份
            year_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'/html/body/div[5]/div[1]/div[2]/table/tbody/tr/td/span[text()="{month}月"]')))
            driver.execute_script("arguments[0].click();", year_button)
            time.sleep(0.5)
            # 选择日
            yearday_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f'/html/body/div[5]/div[1]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="{day}"]')))
            driver.execute_script("arguments[0].click();", yearday_button)
            time.sleep(0.5)
        else:
            # 选择月份
            month_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'/html/body/div[5]/div[1]/div[2]/table/tbody/tr/td/span[text()="{month}月"]')))
            driver.execute_script("arguments[0].click();", month_button)
            time.sleep(0.5)
            # 选择日 /html/body/div[5]/div[1]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="1"]
            day_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f'/html/body/div[5]/div[1]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="{day}"]')))
            driver.execute_script("arguments[0].click();", day_button)
            time.sleep(0.5)
    else:
        # 选择日 /html/body/div[5]/div[1]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="1"]
        day_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 f'/html/body/div[5]/div[1]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="{day}"]')))
        driver.execute_script("arguments[0].click();", day_button)
        time.sleep(0.5)

# 计划结束时间
def end_time(wait,driver,times):
    date = pd.to_datetime(times)
    month = date.month
    day = date.day
    year = date.year
    month_str = f"{year}年 {month}月"  # 2024年 12月
    yearMonth_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/table/thead/tr[1]/th[2]/div')
    if yearMonth_element.text != month_str:
        time.sleep(0.5)
        # 点击年月
        click_button = wait.until(
            EC.presence_of_element_located((By.XPATH, f'/html/body/div[5]/div[2]/div[1]/table/thead/tr[1]/th[2]/div')))
        driver.execute_script("arguments[0].click();", click_button)
        time.sleep(0.5)
        year_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[2]/table/thead/tr/th[2]/div')
        if year_element.text != year:
            # 点击年
            year_click_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f'/html/body/div[5]/div[2]/div[2]/table/thead/tr/th[2]/div')))
            driver.execute_script("arguments[0].click();", year_click_button)
            time.sleep(0.5)
            # 选择年份
            year_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f'/html/body/div[5]/div[2]/div[3]/table/tbody/tr/td/span[text()="{year}"]')))
            driver.execute_script("arguments[0].click();", year_button)
            time.sleep(0.5)
            # 选择月份
            month_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'/html/body/div[5]/div[2]/div[2]/table/tbody/tr/td/span[text()="{month}月"]')))
            driver.execute_script("arguments[0].click();", month_button)
            time.sleep(0.5)
            # 选择日
            yearday_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f'/html/body/div[5]/div[2]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="{day}"]')))
            driver.execute_script("arguments[0].click();", yearday_button)
            time.sleep(0.5)
        else:
            # 选择月份
            month_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, f'/html/body/div[5]/div[2]/div[2]/table/tbody/tr/td/span[text()="{month}月"]')))
            driver.execute_script("arguments[0].click();", month_button)
            time.sleep(0.5)
            # 选择日 /html/body/div[5]/div[2]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="1"]
            day_button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     f'/html/body/div[5]/div[2]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="{day}"]')))
            driver.execute_script("arguments[0].click();", day_button)
            time.sleep(0.5)
    else:
        # 选择日 /html/body/div[5]/div[2]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="1"]
        day_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH,
                 f'/html/body/div[5]/div[2]/div[1]/table/tbody//td[not(@class="c5-datepicker-day   c5-datepicker-old") and not(@class="c5-datepicker-day   c5-datepicker-new") and text()="{day}"]')))
        driver.execute_script("arguments[0].click();", day_button)
        time.sleep(0.5)

def sankua_hongdeng(driver):
    wait = WebDriverWait(driver, 10, 1)
    # 跨越河流
    # 定位第一层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="mainFrame"]')
    river_button = wait.until(EC.presence_of_element_located((By.XPATH, '//li[@data-id="crossingRivers"]')))
    driver.execute_script("arguments[0].click();", river_button)
    # 定位第二层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="innerPage"]')
    river_download = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="btn-excel-export"]'))) # 导出
    driver.execute_script("arguments[0].click();", river_download)
    # time.sleep(10)
    download_iframe(driver)

    # 跨越公路
    driver.switch_to.default_content()
    # 定位第一层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="mainFrame"]')
    highway_button = wait.until(EC.presence_of_element_located((By.XPATH, '//li[@data-id="acrossRoadway"]')))
    driver.execute_script("arguments[0].click();", highway_button)
    # 定位第二层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="innerPage"]')
    highway_download = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="btn-excel-export"]'))) # 导出
    driver.execute_script("arguments[0].click();", highway_download)
    # time.sleep(10)
    download_iframe(driver)
    time.sleep(5)
    x, y = 184, 164
    pyautogui.moveTo(x, y, duration=0.5)
    pyautogui.click()

    # 跨越铁路
    driver.switch_to.default_content()
    # 定位第一层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="mainFrame"]')
    railway_button = wait.until(EC.presence_of_element_located((By.XPATH, '//li[@data-id="acrossRailway"]')))
    driver.execute_script("arguments[0].click();", railway_button)
    # 定位第二层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="innerPage"]')
    railway_download = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@id="btn-excel-export"]'))) # 导出
    driver.execute_script("arguments[0].click();", railway_download)
    # time.sleep(10)
    download_iframe(driver)

def download_iframe(driver):
    driver.switch_to.default_content()
    driver = iframe_dingwei(driver, '//iframe[@id="dialog-iframe1"]')
    download_daochuchengong = WebDriverWait(driver, 60, 1).until(EC.presence_of_element_located((By.XPATH, '//tr[@data-index="0"]/td[3]/div/font')))
    # print(download_daochuchengong.text)
    while download_daochuchengong.text != "导出成功":
        print("已进入循环")
        driver.execute_script("arguments[0].click();", download_daochuchengong)
        time.sleep(10)
    download_BT = WebDriverWait(driver, 60, 1).until(EC.presence_of_element_located((By.XPATH, '//tr[@data-index="0"]/td[4]/div/i[1]')))
    driver.execute_script("arguments[0].click();", download_BT)
    print("文件已下载")

def weihujianxiu(driver,kaishi_time, jieshu_time):
    # 进度--"维护检修管理"
    wait = WebDriverWait(driver, 10,1)
    search_sumup_button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="查询"]')))
    driver.execute_script("arguments[0].click();", search_sumup_button)
    # 定位第一层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="mainFrame"]')
    weihu_gengduo = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="cui-component"]/a/span'))) # 更多
    driver.execute_script("arguments[0].click();", weihu_gengduo)

    # 计划时间
    time_click = wait.until(
        EC.presence_of_element_located((By.XPATH, f'//*[@id="planDate"]/div/span[2]/button')))
    driver.execute_script("arguments[0].click();", time_click)
    time.sleep(0.5)
    # 计划开始时间
    start_time(wait, driver, kaishi_time)
    # 计划结束时间
    end_time(wait, driver, jieshu_time)

    OKyes_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[text()="确定"]')))
    driver.execute_script("arguments[0].click();", OKyes_button)

    driver.find_element(By.XPATH,'//*[@id="colid-6177602905410561"]/div/input').send_keys("输电管理二所") # 工作组别
    weihu_WG = wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/ul/li/a/strong')))  # 工作组别
    driver.execute_script("arguments[0].click();", weihu_WG)
    driver.find_element(By.XPATH, '//*[@id="planState"]/input').send_keys("待确认;已完成") # 计划状态
    driver.find_element(By.XPATH, '//*[@id="workType"]/input').send_keys("巡视;预试;测量") # 工作类别
    weihu_inquire = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="btn-query"]/span')))  # 查询
    driver.execute_script("arguments[0].click();", weihu_inquire)
    weihu_derive_1 = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown-btn-excel-export"]/button')))  # 导出
    driver.execute_script("arguments[0].click();", weihu_derive_1)
    weihu_derive_2 = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="dropdown-btn-excel-export"]/ul/li[1]/a')))  # 点击导出
    driver.execute_script("arguments[0].click();", weihu_derive_2)
    driver.switch_to.default_content()
    # 定位文件导出层iframe
    driver = iframe_dingwei(driver, '//iframe[@id="dialog-iframe1"]')
    weihu_list = wait.until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[1]/div[2]/div[1]/table/thead/tr/th[1]/div[1]/lable/i')))  # 序列全选
    driver.execute_script("arguments[0].click();", weihu_list)
    weihu_list_daochu = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//button[@id="export"]')))  # 导出
    driver.execute_script("arguments[0].click();", weihu_list_daochu)
    time.sleep(5)
    # 如果出现新的iframe，则点击下载
    try:
        driver.switch_to.default_content()
        driver = iframe_dingwei(driver, '//iframe[@id="dialog-iframe2"]')
        download_g = WebDriverWait(driver, 60, 1).until(EC.presence_of_element_located((By.XPATH, '//tr[@data-index="0"]/td[3]/div/font')))
        while download_g.text != "导出成功":
            print("已进入循环")
            driver.execute_script("arguments[0].click();", download_g)
            time.sleep(10)
        download_BTwei = WebDriverWait(driver, 60, 1).until(EC.presence_of_element_located((By.XPATH, '//tr[@data-index="0"]/td[4]/div/i[1]')))
        driver.execute_script("arguments[0].click();", download_BTwei)
        print("文件已下载")
    except NoSuchElementException:
        print("iframe not found")

def get_account_and_password():
    # 获取当前目录
    current_directory = os.getcwd()

    # 设置ID.txt文件路径
    file_path = os.path.join(current_directory, 'ID.txt')

    # 尝试读取文件并提取账号和密码
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # 读取文件内容
            content = file.readlines()

            # 假设文件中的第一行是账号，第二行是密码
            if len(content) >= 2:
                account = content[0].strip().split(':')[-1].strip()  # 处理账号
                password = content[1].strip().split(':')[-1].strip()  # 处理密码

                return account, password
            else:
                return None, "文件格式不正确，请确保有账号和密码"
    except FileNotFoundError:
        return None, "ID.txt 文件未找到，请确保文件在当前目录下"
    except Exception as e:
        return None, f"发生错误: {e}"
# 判断浏览器标题，如果不正确，则每五秒一直循环获取标题
def check_title(driver,driver_title):
    while True:
        current_title = driver.title
        print(current_title)
        if any(title in current_title for title in driver_title):
            break
        time.sleep(5)


def get_first_and_last_day(year,month):
    first_day = datetime(year,month,1)
    last_day = datetime(year,month,calendar.monthrange(year,month)[1])
    return first_day,last_day


if __name__ == '__main__':
    from login import login_main
    year = int(input("请输入年份："))
    month = int(input("请输入月份："))
    first_day, last_day = get_first_and_last_day(year, month)
    now_date = datetime.now()
    now_time = now_date.strftime('%Y-%m-%d')
    current_dir = os.getcwd()  # 当前路径
    capabilities = {
            "browserName": "MicrosoftEdge",
            "version": "",
            "platform": "WINDOWS",
            "ms:edgeOptions":{
                "extensions": [],
                "args": [],
                "prefs": {
                    "download.default_directory": fr"{current_dir}"},
            }
        }
    driver = webdriver.Edge("./MicrosoftWebDriver.exe",capabilities=capabilities)
    # driver.get("https://10.150.130.163/isc_sso/login")
    login_main(driver,"电网管理平台资产域")
    # 更新新的登录平台
    # driver.maximize_window()
    # driver.implicitly_wait(5)
    # account, result = get_account_and_password()
    # login(driver, account, result)  # 登录功能
    # check_title(driver, driver_title=['一窗通办', '登录成功'])
    # current_handle = yichuangtongban(driver) #一窗通办
    # time.sleep(2)
    # driver.switch_to_window(driver.window_handles[-1]) # 获取倒数第一个标签页面，即新打开的页面
    # # print(driver.title)
    # # 判断是出现访问异常
    # if driver.title == '隐私错误':
    #     error(driver)
    '''2025-05-13 暂停使用三跨两临的数据进行统计'''
    # shouye(driver,"输电防灾管理") # 首页
    # driver.switch_to_window(driver.window_handles[-1]) # 获取倒数第一个标签页面，即新打开的页面
    # # 进度--"输电防灾管理"
    # wait = WebDriverWait(driver, 10)
    # search_sumup_button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@title="三跨两临近管理（新）"]')))
    # driver.execute_script("arguments[0].click();", search_sumup_button)
    # time.sleep(2)
    # sankua_hongdeng(driver)
    # # 切换到”首页“标签页中
    # time.sleep(2)
    # driver.close()
    # driver.switch_to_window(driver.window_handles[1]) # 获取第二个标签页面
    time.sleep(2)
    shouye(driver,"维护检修管理") # 首页
    time.sleep(2)
    driver.switch_to_window(driver.window_handles[-1]) # 获取最后标签页面
    weihujianxiu(driver,first_day, last_day)
    print("文件全部导出成功")
