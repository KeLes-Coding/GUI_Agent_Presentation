from playwright.sync_api import sync_playwright
import os
import re
import time

def build_html_for_pdf(root_dir):
    """ 生成用于打印的 HTML """
    with open(os.path.join(root_dir, 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()

    # 内联 CSS
    with open(os.path.join(root_dir, 'css', 'style.css'), 'r', encoding='utf-8') as f:
        css = f.read()
    html = re.sub(r'<link rel="stylesheet" href="css/style.css">', f'<style>{css}</style>', html)

    # 拼接 Slides
    slides_dir = os.path.join(root_dir, 'slides')
    files = [f for f in os.listdir(slides_dir) if f.startswith('slide') and f.endswith('.html')]
    files.sort(key=lambda x: int(re.search(r'(\d+)', x).group(1)))

    slides_content = ""
    for i, fname in enumerate(files, 1):
        with open(os.path.join(slides_dir, fname), 'r', encoding='utf-8') as f:
            s_code = f.read()
            # 注入 Logo
            extras = f'<img src="assets/scnu_logo.png" class="scnu-logo"><div class="slide-page-number">{i}</div>'
            idx = s_code.rfind('</div>')
            if idx != -1:
                s_code = s_code[:idx] + extras + s_code[idx:]
            slides_content += s_code + "\n"

    html = html.replace('<div id="presentation-deck"></div>', f'<div id="presentation-deck">{slides_content}</div>')
    # 移除 JS 防止干扰
    html = re.sub(r'<script src="js/.*\.js"></script>', '', html)
    
    return html

def export_to_pdf():
    base_path = os.path.abspath('.')
    html_content = build_html_for_pdf(base_path)
    temp_html_path = os.path.join(base_path, 'temp_print_source.html')
    
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"正在生成 PDF，源文件: {temp_html_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 关键：等待网络空闲，确保图片和 MathJax 加载完毕
        page.goto(f"file://{temp_html_path}", wait_until="networkidle")
        
        # 强制注入打印样式
        page.add_style_tag(content="""
            @page { size: 1280px 720px; margin: 0; }
            body { 
                margin: 0; padding: 0; 
                background: #fff !important; 
                -webkit-print-color-adjust: exact; 
            }
            
            #presentation-deck {
                display: block !important;
                width: 100% !important;
            }
            
            .slide-container {
                width: 1280px !important;
                height: 720px !important;
                page-break-after: always !important;
                break-after: page !important;
                margin: 0 !important;
                position: relative !important;
                overflow: hidden !important;
                border: none !important;
                box-shadow: none !important;
                display: block !important;
            }
            
            #control-bar, .back-to-dir-btn { display: none !important; }
        """)

        # 额外等待 MathJax 渲染（如果页面有 math 标签）
        try:
            page.wait_for_selector('mjx-container', timeout=2000)
            time.sleep(1) # 给渲染一点缓冲时间
        except:
            print("提示: 未检测到 MathJax 容器或已超时，继续打印...")

        output_path = os.path.join(base_path, "GUI_Agent_Proposal_ZhengZihan.pdf")
        page.pdf(
            path=output_path,
            width="1280px",
            height="720px",
            print_background=True
        )
        browser.close()

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    print(f"✅ PDF 导出成功: {output_path}")

if __name__ == "__main__":
    export_to_pdf()