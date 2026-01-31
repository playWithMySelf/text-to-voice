"""
主窗口 - 优化版（深色主题，简洁布局）
"""
import tkinter as tk
from tkinter import ttk, messagebox

from .styles import (
    COLORS, FONTS, SPACING, DIMENSIONS,
    apply_modern_style, get_label_style
)
from .single_tab import SingleTab
from .batch_tab import BatchTab


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("文本转语音工具")
        self.root.geometry(f"{DIMENSIONS['window_width']}x{DIMENSIONS['window_height']}")
        self.root.minsize(800, 550)
        
        # 应用现代样式
        apply_modern_style(self.root)
        
        # 创建界面
        self._create_menu()
        self._create_header()
        self._create_notebook()
        self._create_status_bar()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_menu(self) -> None:
        """创建菜单栏"""
        menubar = tk.Menu(self.root, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self._on_close)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_secondary'], fg=COLORS['text_primary'])
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_header(self) -> None:
        """创建头部区域"""
        self.header = tk.Frame(self.root, bg=COLORS['bg_primary'], height=50)
        self.header.pack(fill=tk.X, padx=SPACING['lg'], pady=(SPACING['lg'], 0))
        self.header.pack_propagate(False)
        
        # 标题
        self.title_label = tk.Label(
            self.header,
            text="文本转语音工具",
            **get_label_style(is_title=True)
        )
        self.title_label.pack(side=tk.LEFT)
        
        # 副标题
        self.subtitle_label = tk.Label(
            self.header,
            text="基于 Microsoft Edge TTS",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            font=(FONTS['family'], FONTS['size_small'])
        )
        self.subtitle_label.pack(side=tk.LEFT, padx=(SPACING['md'], 0))
    
    def _create_notebook(self) -> None:
        """创建标签页"""
        # 创建Notebook容器
        self.notebook_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        self.notebook_container.pack(
            fill=tk.BOTH, 
            expand=True, 
            padx=SPACING['lg'], 
            pady=SPACING['md']
        )
        
        # 创建Notebook
        self.notebook = ttk.Notebook(
            self.notebook_container,
            style='Modern.TNotebook'
        )
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        self.single_tab = SingleTab(
            self.notebook,
            on_status_change=self._update_status
        )
        self.batch_tab = BatchTab(
            self.notebook,
            on_status_change=self._update_status
        )
        
        # 添加标签页
        self.notebook.add(self.single_tab, text="  单个生成  ")
        self.notebook.add(self.batch_tab, text="  批量生成  ")
    
    def _create_status_bar(self) -> None:
        """创建状态栏"""
        self.status_bar = tk.Frame(
            self.root,
            bg=COLORS['bg_secondary'],
            height=28
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        # 状态文本
        self.status_label = tk.Label(
            self.status_bar,
            text="就绪",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_secondary'],
            font=(FONTS['family'], FONTS['size_small'])
        )
        self.status_label.pack(side=tk.LEFT, padx=SPACING['md'])
        
        # 版本信息
        self.version_label = tk.Label(
            self.status_bar,
            text="v1.0.0",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_muted'],
            font=(FONTS['family'], FONTS['size_small'])
        )
        self.version_label.pack(side=tk.RIGHT, padx=SPACING['md'])
    
    def _update_status(self, status: str) -> None:
        """更新状态栏文本"""
        self.status_label.configure(text=status)
    
    def _show_about(self) -> None:
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            "文本转语音工具 v1.0.0\n\n"
            "基于 Microsoft Edge TTS 技术\n"
            "支持多种中文音色和批量转换\n\n"
            "© 2025 All Rights Reserved"
        )
    
    def _on_close(self) -> None:
        """关闭窗口"""
        # 检查是否正在生成
        if hasattr(self.single_tab, 'is_generating') and self.single_tab.is_generating:
            if not messagebox.askyesno(
                "确认退出",
                "正在生成音频，确定要退出吗？"
            ):
                return
            self.single_tab.on_close()
        
        if hasattr(self.batch_tab, 'is_generating') and self.batch_tab.is_generating:
            if not messagebox.askyesno(
                "确认退出",
                "正在批量生成音频，确定要退出吗？"
            ):
                return
            self.batch_tab.on_close()
        
        self.root.destroy()
    
    def run(self) -> None:
        """运行主循环"""
        self.root.mainloop()
