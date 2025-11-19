import re
import os

# 确保 slides 文件夹存在
if not os.path.exists('slides'):
    os.makedirs('slides')

# 读取包含所有 PPT 的源文件 (请先把你提供的完整 HTML 保存为 source.html)
try:
    with open('source.html', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("错误：请先将你的完整 HTML 代码保存为 'source.html' 放在同级目录下。")
    exit()

# 使用正则表达式提取每个 slide-container
# 逻辑：匹配 <div class="slide-container"... 到它结束的地方
# 注意：这里假设你的格式比较标准，基于 注释分割会更稳健
pattern = r'(\s*<div class="slide-container".*?>.*?</div>\s*</div>)'
matches = re.findall(pattern, content, re.DOTALL)

if not matches:
    print("未找到匹配的 Slide，尝试仅匹配 div...")
    # 备用正则，不依赖注释
    pattern = r'(<div class="slide-container".*?>.*?</div>\s*</div>)'
    matches = re.findall(pattern, content, re.DOTALL)

print(f"共找到 {len(matches)} 页幻灯片。")

for i, slide_content in enumerate(matches):
    filename = f"slides/slide{i+1}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(slide_content)
    print(f"已生成: {filename}")

print("拆分完成！")