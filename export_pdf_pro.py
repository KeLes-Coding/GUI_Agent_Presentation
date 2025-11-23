from playwright.sync_api import sync_playwright
from pypdf import PdfWriter
import os
import re
import time
import shutil

def export_ultimate():
    root_dir = os.path.abspath('.')
    
    # 1. 准备工作目录
    temp_dir = os.path.join(root_dir, "temp_pdf_pages")
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 2. 确定源文件 (优先用本地化版)
    source_html = "index_local.html" if os.path.exists("index_local.html") else "index.html"
    print(f"📖 读取源文件: {source_html}")
    
    # 3. 启动浏览器
    with sync_playwright() as p:
        print("🚀 启动渲染引擎...")
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 4. 加载页面 (使用 file:// 协议)
        # 我们加载完整的页面，这样所有样式和资源都能正确解析
        page.goto(f"file://{os.path.abspath(source_html)}", wait_until="networkidle")

        # 5. 注入“手术刀” CSS
        # 核心逻辑：隐藏所有内容，只有带有 .printing-active 类的幻灯片才显示
        page.add_style_tag(content="""
            /* 全局隐藏 */
            body { 
                background: white !important; 
                overflow: hidden !important; 
                margin: 0 !important;
            }
            #presentation-deck, .slide-container {
                display: none !important; /* 默认全部隐藏 */
            }
            
            /* 只有激活的幻灯片显示 */
            .slide-container.printing-active {
                display: flex !important;
                position: fixed !important; /* 强制固定在左上角 */
                top: 0 !important;
                left: 0 !important;
                width: 1280px !important;
                height: 720px !important;
                z-index: 9999 !important;
                opacity: 1 !important;
                transform: none !important;
                box-shadow: none !important;
                border: none !important;
                background: white !important;
            }
            
            /* 隐藏 UI */
            #control-bar, .back-to-dir-btn { display: none !important; }
        """)

        # 6. 等待资源加载 (MathJax 等)
        print("⏳ 等待资源渲染 (3秒)...")
        try:
            page.wait_for_function("() => window.MathJax && window.MathJax.typesetPromise", timeout=5000)
            page.evaluate("window.MathJax.typesetPromise()")
        except:
            pass
        time.sleep(3)

        # 7. 获取所有幻灯片元素
        # 注意：这里通过 JS 获取 DOM 元素的引用
        slides_count = page.evaluate("document.querySelectorAll('.slide-container').length")
        print(f"🧩 检测到 {slides_count} 张幻灯片，开始逐页导出...")

        pdf_files = []

        # 8. 逐页循环打印
        for i in range(slides_count):
            slide_index = i + 1
            print(f"  -> 正在处理第 {slide_index}/{slides_count} 页...")
            
            # JS 魔法：
            # 1. 移除上一个激活的类
            # 2. 给当前索引的 slide 添加 .printing-active
            # 3. 注入 Logo 和页码 (如果静态文件里没有的话)
            page.evaluate(f"""
                () => {{
                    const slides = document.querySelectorAll('.slide-container');
                    // 清除所有激活状态
                    slides.forEach(s => s.classList.remove('printing-active'));
                    
                    // 激活当前页
                    const current = slides[{i}];
                    if (current) {{
                        current.classList.add('printing-active');
                        
                        // 确保有 Logo (防止重复添加)
                        if (!current.querySelector('.scnu-logo')) {{
                            const img = document.createElement('img');
                            img.src = 'assets/scnu_logo.png';
                            img.className = 'scnu-logo';
                            current.appendChild(img);
                        }}
                        // 确保有页码
                        if (!current.querySelector('.slide-page-number')) {{
                            const num = document.createElement('div');
                            num.className = 'slide-page-number';
                            num.innerText = '{slide_index}';
                            current.appendChild(num);
                        }}
                    }}
                }}
            """)
            
            # 等待渲染稳定
            time.sleep(0.5)
            
            # 打印当前视图为 PDF
            output_filename = os.path.join(temp_dir, f"page_{slide_index:02d}.pdf")
            page.pdf(
                path=output_filename,
                width="1280px",   # 强制匹配 Slide 尺寸
                height="720px",
                print_background=True,
                page_ranges="1"   # 只打印当前视口
            )
            pdf_files.append(output_filename)

        browser.close()

    # 9. 合并 PDF
    print("📑 正在合并所有页面...")
    merger = PdfWriter()
    for pdf in pdf_files:
        merger.append(pdf)
    
    final_output = "GUI_Agent_Proposal_Final.pdf"
    merger.write(final_output)
    merger.close()
    
    # 清理临时文件
    shutil.rmtree(temp_dir)
    
    print(f"\n✅ 完美导出成功！文件已保存为: {final_output}")

if __name__ == "__main__":
    export_ultimate()