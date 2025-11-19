import webview
import os
import sys

def resource_path(relative_path):
    """ 获取资源绝对路径，兼容 PyInstaller 打包后的环境 """
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    # 获取 html 文件的绝对路径
    html_file = resource_path('index.html')
    
    # 转换为 file:// URL
    file_url = f'file://{os.path.abspath(html_file)}'

    # 创建窗口
    window = webview.create_window(
        title='开题报告 - GUI智能体 - 郑梓瀚',
        url=html_file,
        width=1400,  # 略大于 Slide 宽度
        height=900,
        resizable=True,
        fullscreen=False # 如果想全屏演示，设为 True
    )

    # 启动
    webview.start()