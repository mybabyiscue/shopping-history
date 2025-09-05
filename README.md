# 购物记录管理系统

一个基于PyQt5开发的桌面应用程序，用于管理购物记录，支持用户权限管理、数据查询、统计分析和数据导出。

## 功能特性

- ✅ 用户登录和权限管理（管理员/普通用户）
- ✅ 购物记录录入（用途、平台、物品、数量、价格等）
- ✅ 数据浏览和查询（日期范围、用途、平台、状态筛选）
- ✅ 数据编辑和删除
- ✅ 统计分析（总消费、月度趋势、分类统计）
- ✅ CSV数据导出（可选择保存路径）
- ✅ 现代化界面设计

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

或双击 `run.bat`

## 打包成EXE

```bash
# 方法1：使用build.bat（推荐）
双击 build.bat

# 方法2：手动打包
pyinstaller --name=购物记录管理系统 --onefile --windowed --add-data="data;data" --add-data="config;config" --add-data="ui/icons;ui/icons" --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtGui --hidden-import=csv --hidden-import=hashlib --hidden-import=datetime --clean main.py
```

### 打包常见问题

1. **图标不显示**：
   - 确保打包命令包含`--add-data="ui/icons;ui/icons"`
   - 检查代码中使用`os.path.join`构建图标路径

2. **权限错误**：
   - 关闭正在运行的exe程序
   - 以管理员身份运行build.bat
   - 手动删除dist目录下的旧exe文件

3. **打包失败**：
   - 检查Python环境是否完整
   - 确保所有依赖已安装
   - 尝试添加`--clean`参数

## 默认账号

- **管理员**: admin / admin123
- **普通用户**: user1 / user123

## 文件结构

```
shopping_tool/
├── main.py                 # 程序入口
├── core/                   # 核心模块
│   ├── auth.py            # 用户认证
│   ├── record_manager.py  # 记录管理
│   ├── user_manager.py    # 用户管理
│   └── utils.py           # 工具函数
├── ui/                    # 界面模块
│   ├── login_window.py    # 登录界面
│   ├── main_window.py     # 主界面
│   ├── record_tab.py      # 记录录入
│   ├── browse_tab.py      # 数据浏览
│   ├── stats_tab.py       # 统计分析
│   ├── user_tab.py        # 用户管理
│   ├── edit_dialog.py     # 编辑对话框
│   └── icons/             # 图标资源
│       ├── edit-solid.svg
│       ├── trash-solid.svg
│       └── eye-solid.svg
├── data/                  # 数据文件
│   ├── users.csv          # 用户数据
│   └── records.csv        # 购物记录
├── config/                # 配置文件
└── build.bat             # 打包脚本
```

## 使用说明

1. 运行程序后使用默认账号登录
2. 管理员可以管理用户和所有数据
3. 普通用户只能查看和录入自己的记录
4. 支持按多种条件查询和筛选数据
5. 可以导出CSV文件到指定位置

## 技术栈

- Python 3.x
- PyQt5 (界面框架)
- CSV (数据存储)
- SHA256 (密码加密)
- PyInstaller (打包工具)