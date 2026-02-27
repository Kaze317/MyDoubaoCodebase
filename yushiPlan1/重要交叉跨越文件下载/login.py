from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

def iframe_dingwei(driver,xpath):
    iframe = driver.find_element(By.XPATH, xpath)
    driver.switch_to_frame(iframe)
    return driver

def login(driver,account, result): # 登录
    user_login = driver.find_element(By.XPATH, '//div[@class="poptip-content"]')
    print(user_login.text)
    if "账号登录" in user_login.text:
        driver.find_element(By.XPATH, '//div[@class="poptip-content"]').click()
        driver.find_element(By.XPATH, '//li[@title="账号登录"]').click()
        # driver.find_element(By.XPATH, '//span[text() = "总分部/直属单位"]').click()
        # driver.find_element(By.XPATH, '//span[text() = "省（市）公司"]').click()
        driver.find_element(By.XPATH, '(//div[@class="el-input"])[1]/input').send_keys(account) # sejqr@gzps.corp.csg
        driver.find_element(By.XPATH, '//input[@autocomplete="new-password"]').send_keys(result)  # Jqr@0228
        print("请手动输入验证码")
    # return driver.current_url
        # driver.execute_script(f"window.location.href = 'https://iam.ep.gzps/web/#/dashboard")


def error(driver): # 访问异常
    driver.find_element(By.XPATH, '//button[@id="details-button"]').click()
    driver.find_element(By.XPATH, '//a[@id="proceed-link"]').click()
    time.sleep(2)

def yichuangtongban(driver,text):
    # 进度--"一窗通办"
    # 搜索电网管理平台资产域 //input[@placeholder="请输入应用名称"]
    driver.find_element(By.XPATH, '//input[@placeholder="请输入应用名称"]').send_keys(text)
    time.sleep(5)
    sousuo = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button/span[contains(text(),"搜索")]')))
    driver.execute_script("arguments[0].click();", sousuo)
    # 点击"电网管理平台资产域"
    cichangyu = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, f'//span[contains(text(),"{text}")]')))
    driver.execute_script("arguments[0].click();", cichangyu)

def shouye(driver):
    # 进度--"首页"
    wait = WebDriverWait(driver, 10)
    # 点击左上角的九个点展开搜索功能
    nine = wait.until(EC.presence_of_element_located((By.XPATH, '//header/div/div/span')))
    driver.execute_script("arguments[0].click();", nine)
    time.sleep(2)
    # 点击搜索并搜索对应的内容
    text = '输电防灾管理'
    # search_input = wait.until(EC.presence_of_element_located((By.XPATH,'//input[@id="searchApp"]')))
    # driver.execute_script(f"arguments[0].value={text};",search_input)
    search_input = driver.find_element(By.XPATH, '//input[@id="searchApp"]').send_keys(text)
    search_button = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="gmp-hamburg-search"]/div/span/i')))
    driver.execute_script("arguments[0].click();", search_button)
    search_text = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@title="输电防灾管理"]')))
    driver.execute_script("arguments[0].click();", search_text)
    # print(driver.title)

# 判断浏览器标题，如果不正确，则每五秒一直循环获取标题
def check_title(driver,driver_url):
    while True:
        current_title = driver.current_url
        print(current_title)
        # if any(title in current_title for title in driver_title):
        #     break
        if current_title == driver_url:
            break
        time.sleep(5)

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

def login_main(driver,title):
    driver.get("https://iam.ep.gzps/login/")
    driver.maximize_window()
    driver.implicitly_wait(5)
    account, result = get_account_and_password()
    login(driver, account, result)  # 登录功能
    check_title(driver, driver_url="https://iam.ep.gzps/web/#/dashboard")
    time.sleep(1)
    # driver.execute_script(f"window.location.href = 'http://10.150.130.161/isc-portal/iscPortal/getUser';")
    # time.sleep(1)
    print("登录成功")
    # 电网管理平台资产域
    yichuangtongban(driver,text=title)  # 一窗通办
    time.sleep(2)
    driver.switch_to_window(driver.window_handles[-1])  # 获取倒数第一个标签页面，即新打开的页面
    # 判断是出现访问异常
    if driver.title == '隐私错误':
        error(driver)
    if driver.title == '隐私错误':
        error(driver)
    return driver



if __name__ == '__main__':
    # https://iam.ep.gzps/login/#/index
    # 数字身份与访问管理平台
    title = "电网管理平台资产域"
    login_main(title)

