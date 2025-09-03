Write-Host "正在打包购物记录管理系统..."

pyinstaller --name=购物记录管理系统 --onefile --windowed `
--add-data="data;data" `
--add-data="config;config" `
--paths="E:\anaconda3\Library\plugins" `
--hidden-import=PyQt5.QtWidgets `
--hidden-import=PyQt5.QtCore `
--hidden-import=PyQt5.QtGui `
--hidden-import=matplotlib.backends.backend_qtagg `
main.py

Write-Host ""
Write-Host "打包完成！生成的exe文件在 dist\ 目录下"
Read-Host "按回车键继续"