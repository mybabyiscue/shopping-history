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

## 文件结构详细说明

```
shopping_tool/
├── main.py                 # 程序主入口，初始化应用和主窗口
├── build/                  # 打包生成文件
│   ├── 购物记录管理系统/    # PyInstaller打包中间文件
│   │   ├── *.toc           # 打包过程跟踪文件
│   │   ├── *.pkg           # 打包组件
│   │   └── localpycs/      # 编译后的Python字节码
│   ├── custom_build/       # 自定义打包配置
│   ├── shopping_tool/      # 旧版打包输出
│   └── ShoppingRecordManager/ # 英文版打包输出
├── core/                   # 核心业务逻辑
│   ├── auth.py            # 用户认证模块，处理登录和权限验证
│   ├── record_manager.py  # 购物记录CRUD操作和查询逻辑
│   ├── user_manager.py    # 用户管理功能（增删改查）
│   └── utils.py           # 通用工具函数（加密、日期处理等）
├── ui/                    # 用户界面模块
│   ├── login_window.py    # 登录窗口界面逻辑
│   ├── main_window.py     # 主窗口框架和导航
│   ├── record_tab.py      # 记录录入界面和逻辑
│   ├── browse_tab.py      # 数据浏览表格和查询控件
│   ├── stats_tab_fixed.py # 统计图表和分析界面
│   ├── user_tab.py        # 用户管理界面（仅管理员可见）
│   ├── edit_dialog.py     # 记录编辑弹出对话框
│   ├── reimbursement_tab.py # 报销管理界面（状态筛选、批量操作）
│   ├── detail_dialog.py   # 记录详情查看对话框 
│   ├── summary_dialog.py  # 统计摘要展示对话框
│   └── icons/             # SVG格式图标资源
│       ├── edit-solid.svg  # 编辑图标
│       ├── trash-solid.svg # 删除图标
│       └── eye-solid.svg   # 查看图标
├── data/                  # 数据存储文件
│   ├── users.csv          # 用户数据表（用户名,加密密码,角色）
│   ├── records.csv        # 购物记录表（ID,用户,日期,用途,平台,物品,数量,价格,状态）
│   ├── records copy.csv   # 备份数据文件
│   ├── summary.csv        # 生成的统计摘要
│   └── summaries.json     # JSON格式的统计缓存
├── config/                # 应用配置文件目录（目前为空）
├── dist/                  # 最终打包生成的EXE文件输出目录
├── images/                # 应用图片资源
├── __pycache__/           # Python编译缓存
├── .git/                  # Git版本控制数据
├── .venv/                 # Python虚拟环境
├── build.bat             # 一键打包脚本
├── check_matplotlib.py    # 依赖检查工具
├── final_test.py          # 集成测试脚本
├── requirements.txt       # Python依赖列表
└── run.bat               # 一键运行脚本
```

## 核心模块说明

### core模块

- **auth.py**: 
  - 实现用户登录验证
  - 密码使用SHA256加密存储
  - 提供权限检查装饰器

- **record_manager.py**:
  - 提供购物记录的增删改查接口
  - 支持多条件组合查询
  - 实现数据导出为CSV

- **user_manager.py**:
  - 管理用户账户CRUD操作
  - 密码修改和重置功能
  - 管理员专属功能

- **utils.py**:
  - 日期格式化工具
  - 加密工具函数
  - 数据验证工具

### ui模块

- **login_window.py**:
  - 实现登录界面布局
  - 处理登录按钮事件
  - 显示登录状态反馈

- **main_window.py**:
  - 程序主窗口框架
  - 选项卡导航管理
  - 根据用户角色显示不同功能

- **record_tab.py**:
  - 购物记录表单录入
  - 输入验证和格式化
  - 自动计算总价

- **browse_tab.py**:
  - 分页数据显示表格
  - 多条件筛选控件
  - 记录详情查看功能

- **reimbursement_tab.py**:
  - 报销状态管理界面
  - 支持按报销状态筛选记录
  - 提供批量修改报销状态功能
  - 生成报销汇总表格

## 数据文件格式

### users.csv
```
username,password,role
admin,8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918,admin
user1,1a8565a9dfbe12ad1c4b7b898d8dfded0451e349ffadeae7f00b7b3c7e7e294d,user
```

### records.csv
```
id,username,date,purpose,platform,item,quantity,price,status
1,admin,2023-01-15,办公用品,京东,笔记本,5,3.5,已报销
2,user1,2023-01-20,个人用品,淘宝,手机,1,2999,未报销
```

## 使用说明

1. **首次使用**:
   - 安装Python 3.8+
   - 运行`pip install -r requirements.txt`安装依赖
   - 使用默认账号登录测试

2. **数据管理**:
   - 管理员可以管理所有记录
   - 普通用户只能查看和编辑自己的记录
   - 支持批量导出CSV格式数据

3. **统计分析**:
   - 查看月度消费趋势图
   - 按用途分类统计
   - 支持自定义日期范围

## 技术栈

- Python 3.x
- PyQt5 (界面框架)
- CSV (数据存储)
- SHA256 (密码加密)
- PyInstaller (打包工具)
- Matplotlib (统计图表)