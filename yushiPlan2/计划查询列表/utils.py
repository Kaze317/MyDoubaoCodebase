import sys
import os

def resource_path(relative_path):
    """获取资源文件的绝对路径，适用于打包后的环境"""
    if getattr(sys, 'frozen', False):
        # PyInstaller会将资源文件放在临时目录中
        base_path = sys._MEIPASS
    else:
        # 开发环境下直接使用相对路径
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)