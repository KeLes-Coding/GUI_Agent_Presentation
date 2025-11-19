from playwright.sync_api import sync_playwright
import os

def export_to_pdf():
    input_file = f"file://{os.path.abspath('index.html')}"
    output_file = "GUI_Agent_Proposal_ZhengZihan.pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        print(f"正在加载页面: {input_file}...")
        page.goto(input_file, wait_until="networkidle")

        # 注入 CSS 确保打印时背景色和布局正确
        page.add_style_tag(content="""
            @page { size: 1360px 800px; margin: 0; } 
            .slide-container { box-shadow: none; border: none; page-break-after: always; }
            body { background: white; }
        """)

        print("正在生成 PDF...")
        page.pdf(
            path=output_file,
            width="1360px", # 对应 CSS 中的宽度略大一点
            height="800px",
            print_background=True, # 打印背景色
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"} 
        )
        
        browser.close()
        print(f"成功导出: {output_file}")

if __name__ == "__main__":
    export_to_pdf()