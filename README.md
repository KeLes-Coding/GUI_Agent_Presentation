使用 `pyinstaller` 将 `main.py` 和所有资源（`html/css/js`）打包在一起。
---
完全离线化：

在终端（`VS Code terminal`）中运行以下命令（确保你在项目根目录）：
```shell
python localize.py
```
---
打包：

```shell
python -m PyInstaller build.spec
```