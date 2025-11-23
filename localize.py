import os
import re
import requests
import shutil
from urllib.parse import urljoin, urlparse

# ================= 配置区域 =================
# 你的代理地址 (如果不需要代理，请设为 None)
PROXY_URL = "http://127.0.0.1:7890" 

# 资源保存目录
ASSETS_DIR = "assets/vendor"
HTML_FILE = "index.html"
OUTPUT_HTML = "index_local.html"
# ===========================================

# 构造 requests 需要的代理字典
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
} if PROXY_URL else None

if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

def download_file(url, save_dir):
    try:
        # 从 URL 获取文件名
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename: 
            # 如果 URL 是 https://fonts.googleapis.com/css?family=... 这种形式
            filename = "downloaded_style.css"
        
        save_path = os.path.join(save_dir, filename)
        
        # 如果文件已存在且不为空，跳过
        if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
            print(f"  [跳过] 已存在: {filename}")
            return save_path, filename

        print(f"  [下载中] {url} ...")
        
        # 伪装 User-Agent 防止被拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 关键修改：加入 proxies 参数
        r = requests.get(url, headers=headers, proxies=PROXIES, timeout=30)
        r.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(r.content)
        return save_path, filename
        
    except Exception as e:
        print(f"  [错误] 下载失败 {url}: {e}")
        return None, None

def process_css(css_path, base_url):
    """ 解析 CSS 文件，递归下载其中的字体文件 """
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # 有时候下载的可能是二进制乱码，防崩
        print(f"  [警告] 无法读取 CSS 内容: {css_path}")
        return

    # 查找 url(...) 链接
    urls = set(re.findall(r'url\([\'"]?([^)\'"]+)[\'"]?\)', content))
    parent_dir = os.path.dirname(css_path)
    
    modified = False
    for relative_url in urls:
        if relative_url.startswith('data:'): continue
        
        # 构造完整下载链接
        abs_url = urljoin(base_url, relative_url)
        
        # 提取文件名
        font_name = os.path.basename(urlparse(abs_url).path)
        # 防止 query string 干扰文件名 (如 font.woff2?v=4.7.0)
        if '?' in font_name:
            font_name = font_name.split('?')[0]
            
        print(f"    -> 发现子资源: {font_name}")
        
        # 下载子资源
        local_font_path, _ = download_file(abs_url, parent_dir)
        
        if local_font_path:
            # 修改 CSS 中的引用为相对路径 (只保留文件名)
            content = content.replace(relative_url, font_name)
            modified = True
            
    if modified:
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    print(f"=== 开始本地化资源 (代理: {PROXY_URL}) ===")
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 处理 FontAwesome
    print("\n1. 处理 FontAwesome...")
    # 优化正则以匹配更广泛的 CDN 链接
    fa_match = re.search(r'<link[^>]*href=["\'](https://[^"\']*font-awesome[^"\']*)["\'][^>]*>', html)
    if fa_match:
        url = fa_match.group(1)
        fa_dir = os.path.join(ASSETS_DIR, "fontawesome")
        if not os.path.exists(fa_dir): os.makedirs(fa_dir)
        
        local_path, filename = download_file(url, fa_dir)
        if local_path:
            process_css(local_path, url)
            new_link = f'assets/vendor/fontawesome/{filename}'
            html = html.replace(url, new_link)

    # 2. 处理 Google Fonts
    print("\n2. 处理 Google Fonts...")
    gf_match = re.search(r'<link[^>]*href=["\'](https://fonts\.googleapis\.com[^"\']*)["\'][^>]*>', html)
    if gf_match:
        url = gf_match.group(1)
        # 由于 Google Fonts URL 包含特殊字符，我们不需要转义，requests 会处理
        gf_dir = os.path.join(ASSETS_DIR, "fonts")
        if not os.path.exists(gf_dir): os.makedirs(gf_dir)
        
        local_path, filename = download_file(url, gf_dir)
        
        # 如果是 style.css，重命名一下
        if local_path and not filename.endswith('.css'):
            new_path = os.path.join(gf_dir, "google_fonts.css")
            # Windows 下 rename 可能会冲突，先删后移
            if os.path.exists(new_path): os.remove(new_path)
            shutil.move(local_path, new_path)
            local_path = new_path
            filename = "google_fonts.css"

        if local_path:
            process_css(local_path, url)
            new_link = f'assets/vendor/fonts/{filename}'
            html = html.replace(url, new_link)

    # 3. 处理 MathJax
    print("\n3. 处理 MathJax...")
    mj_match = re.search(r'<script[^>]*src=["\'](https://[^"\']*mathjax[^"\']*)["\'][^>]*>', html)
    if mj_match:
        url = mj_match.group(1)
        mj_dir = os.path.join(ASSETS_DIR, "mathjax")
        if not os.path.exists(mj_dir): os.makedirs(mj_dir)
        
        local_path, filename = download_file(url, mj_dir)
        if local_path:
            new_link = f'assets/vendor/mathjax/{filename}'
            html = html.replace(url, new_link)

    # 4. 保存
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 本地化完成！生成文件: {OUTPUT_HTML}")
    print("请再次运行 pyinstaller 打包命令！")

if __name__ == "__main__":
    main()