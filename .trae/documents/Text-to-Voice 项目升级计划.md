## 项目升级计划

### 一、项目结构优化
重构为标准的Python项目结构，提升代码可读性和维护性：

```
text-to-voice/
├── src/                       # 源代码目录
│   ├── __init__.py
│   ├── config.py              # 配置类（支持JSON持久化）
│   ├── core/                  # 核心逻辑
│   │   ├── tts_generator.py   # TTS生成（优化现有代码）
│   │   ├── csv_processor.py   # CSV读写处理
│   │   └── file_manager.py    # 文件路径管理
│   ├── gui/                   # 图形界面
│   │   ├── main_window.py     # 主窗口
│   │   ├── single_tab.py      # 单个生成标签页
│   │   ├── batch_tab.py       # 批量生成标签页
│   │   ├── settings_tab.py    # 设置标签页
│   │   ├── components.py      # 可复用组件
│   │   └── styles.py          # UI样式（ui-ux-pro-max设计）
│   └── utils/                 # 工具模块
│       ├── logger.py          # 日志系统
│       └── validators.py      # 输入验证
├── assets/                    # 资源文件
│   ├── icon.ico               # 程序图标
│   └── template.csv           # CSV模板文件
├── build/                     # 打包配置
│   ├── build.py               # 打包脚本
│   └── app.spec               # PyInstaller配置
├── config/                    # 用户配置
│   └── settings.json
├── main.py                    # 命令行入口（保留兼容）
├── gui_main.py                # GUI入口
├── setup.py                   # 包配置
├── requirements.txt           # 运行依赖
└── requirements-dev.txt       # 开发依赖
```

### 二、GUI功能设计

**主窗口布局（三标签页）：**

1. **单个生成标签页**
   - 中文文本输入框（多行）
   - 输出文件选择
   - 音色下拉选择（使用config中的AVAILABLE_VOICES）
   - 语速滑块（-50% ~ +50%，默认-22%）
   - 音量滑块（+0% ~ +100%，默认+50%）
   - 生成按钮 + 进度显示

2. **批量生成标签页**
   - CSV文件选择（带下载模板按钮）
   - 配置面板（同上）
   - 进度条 + 实时日志
   - 开始/取消按钮
   - 结果统计展示

3. **设置标签页**
   - 默认配置保存
   - 并发数设置
   - 输出目录设置

**CSV模板格式：**
```csv
answer_text,file_path
"第一条要转换的文本内容","output/audio1.mp3"
"第二条要转换的文本内容","output/audio2.mp3"
```

### 三、打包为EXE

使用PyInstaller打包为Windows可执行文件：
- 单文件模式（可选）或文件夹模式
- 包含所有资源文件
- 自定义程序图标
- 提供一键打包脚本

### 四、额外建议功能

1. **配置持久化** - 保存用户偏好设置到JSON
2. **日志系统** - 文件日志 + GUI日志面板
3. **最近文件** - 记录最近使用的CSV文件
4. **打开输出文件夹** - 生成完成后快速访问
5. **音色试听** - 生成示例音频预览（可选）

### 五、技术选型

- **GUI框架**: tkinter（Python内置，打包体积小）
- **打包工具**: PyInstaller
- **代码规范**: 类型注解 + 文档字符串
- **UI设计**: 参考ui-ux-pro-max技能指南

请确认此计划后，我将开始实施具体的代码重构和开发工作。