import http.server
import socketserver
import webbrowser
import os
import sys
import socket
import threading
import subprocess
import platform
import time

# --- 1. 资源路径定位 ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. 寻找可用端口 ---
def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

# --- 3. 浏览器启动器 (核心改进) ---
def launch_browser_fullscreen(url):
    """ 
    尝试寻找 Chrome 或 Edge，并以【APP全屏模式】启动。
    这种模式下没有地址栏，体验最接近原生软件。
    """
    system_name = platform.system()
    browser_path = None
    
    # 常见浏览器路径 (Windows)
    if system_name == "Windows":
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for p in possible_paths:
            if os.path.exists(p):
                browser_path = p
                break
    
    # MacOS / Linux 也可以加相应的逻辑，这里主要针对 Windows 演示环境
    
    if browser_path:
        print(f"🚀 已定位浏览器: {browser_path}")
        print("⚡ 正在尝试进入沉浸式演示模式...")
        try:
            # --app=URL : 以应用模式启动(无地址栏)
            # --start-fullscreen : 启动时强制全屏
            # --kiosk : 展台模式(可选，比全屏更霸道，按F11都退不出，还是用start-fullscreen温和点)
            subprocess.Popen([browser_path, f"--app={url}", "--start-fullscreen"])
            return
        except Exception as e:
            print(f"启动特定浏览器失败: {e}，回退到默认方式。")

    # 兜底方案：如果找不到 Chrome/Edge，就调用系统默认浏览器打开新标签页
    # 注意：这种方式无法自动全屏，需要用户手动按 F11
    print("⚠️ 未找到 Chrome/Edge 或启动失败，使用默认浏览器打开。请手动按 F11 全屏。")
    webbrowser.open(url)

# --- 4. 服务器逻辑 ---
def start_server():
    root_dir = resource_path('.')
    os.chdir(root_dir)
    
    PORT = get_free_port()
    
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), QuietHandler) as httpd:
        url = f"http://localhost:{PORT}/index_local.html"
        print(f"\n✅ 服务已启动: {url}")
        print(f"❌ 关闭此黑框即可退出程序。\n")
        
        # 启动浏览器
        threading.Timer(1.0, lambda: launch_browser_fullscreen(url)).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()

if __name__ == "__main__":
    start_server()