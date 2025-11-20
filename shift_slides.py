import os
import re
import argparse
import sys

def shift_slides(insert_index, directory="slides"):
    """
    将大于等于 insert_index 的幻灯片编号全部 +1，为新插入腾出空间。
    必须倒序重命名以防止覆盖。
    """
    
    # 1. 检查目录是否存在
    if not os.path.exists(directory):
        print(f"错误: 目录 '{directory}' 不存在。")
        return

    # 2. 扫描所有符合 slideX.html 格式的文件
    files = os.listdir(directory)
    pattern = re.compile(r"^slide(\d+)\.html$")
    
    slide_indices = []
    for f in files:
        match = pattern.match(f)
        if match:
            slide_indices.append(int(match.group(1)))

    # 如果没有找到任何幻灯片
    if not slide_indices:
        print(f"在 '{directory}' 中未找到任何 slideX.html 文件。")
        return

    # 3. 关键步骤：降序排列 (例如: [15, 14, 13, ... 6])
    # 我们必须先移动最后一张，否则 slide6 改名 slide7 时会覆盖原有的 slide7
    slide_indices.sort(reverse=True)

    moved_count = 0
    
    print(f"准备从 slide{insert_index}.html 开始向后移动...")

    for i in slide_indices:
        # 只移动编号 >= 插入位置的文件
        if i >= insert_index:
            old_path = os.path.join(directory, f"slide{i}.html")
            new_path = os.path.join(directory, f"slide{i+1}.html")
            
            try:
                os.rename(old_path, new_path)
                print(f"  [OK] slide{i}.html -> slide{i+1}.html")
                moved_count += 1
            except OSError as e:
                print(f"  [Error] 无法重命名 slide{i}.html: {e}")

    if moved_count > 0:
        print(f"\n成功移动了 {moved_count} 个文件。")
        print(f"现在您可以创建新的 'slide{insert_index}.html' 了！")
    else:
        print(f"\n没有文件被移动（可能原本就没有 >= {insert_index} 的幻灯片）。")
        print(f"您可以直接创建 'slide{insert_index}.html'。")

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="自动将幻灯片编号后移，以便插入新页。")
    parser.add_argument("index", type=int, help="您想要插入的新幻灯片编号 (例如: 6)")
    parser.add_argument("--dir", default="slides", help="幻灯片所在的文件夹 (默认: slides)")

    args = parser.parse_args()
    
    shift_slides(args.index, args.dir)