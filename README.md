使用 `pyinstaller` 将 `main.py` 和所有资源（`html/css/js`）打包在一起。

在终端（`VS Code terminal`）中运行以下命令（确保你在项目根目录）：
```shell
pyinstaller --noconsole --onefile --name "GUI_Agent_Report" --add-data "index.html;." --add-data "css;css" --add-data "js;js" --add-data "assets;assets" main.py
```