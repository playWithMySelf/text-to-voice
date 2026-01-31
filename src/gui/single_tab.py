"""
单个生成标签页 - 优化版（自适应布局）
"""
import os
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable

from .styles import COLORS, SPACING, get_label_style, get_card_style
from .components import (
    FileSelector, ConfigPanel, ActionButtons, ProgressPanel
)
from src.config import get_config_manager
from src.core import TTSGenerator, FileManager
from src.utils import validate_text


class SingleTab(tk.Frame):
    """单个生成标签页"""
    
    def __init__(self, parent, on_status_change: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        self.config_manager = get_config_manager()
        self.on_status_change = on_status_change
        self.tts_generator: Optional[TTSGenerator] = None
        self.is_generating = False
        
        self._create_widgets()
        self._setup_layout()
    
    def _create_widgets(self) -> None:
        """创建界面组件"""
        # 使用网格布局实现自适应
        self.columnconfigure(0, weight=3)  # 左侧占3份
        self.columnconfigure(1, weight=2)  # 右侧占2份
        self.rowconfigure(0, weight=1)
        
        # ===== 左侧面板 - 输入区域 =====
        self.left_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['md']))
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=1)
        
        # 文本输入标签
        self.text_label = tk.Label(
            self.left_frame,
            text="输入文本",
            **get_label_style()
        )
        self.text_label.grid(row=0, column=0, sticky="w", pady=(0, SPACING['xs']))
        
        # 文本输入区域（卡片样式）
        self.text_input = tk.Text(
            self.left_frame,
            wrap=tk.WORD,
            bg=COLORS['bg_input'],
            fg=COLORS['text_primary'],
            font=(COLORS.get('font_family', 'Microsoft YaHei UI'), 11),
            relief='flat',
            highlightthickness=1,
            highlightcolor=COLORS['border_focus'],
            highlightbackground=COLORS['border'],
            padx=SPACING['sm'],
            pady=SPACING['sm'],
            insertbackground=COLORS['accent'],
            height=8
        )
        self.text_input.grid(row=1, column=0, sticky="nsew")
        
        # ===== 右侧面板 - 配置和输出 =====
        self.right_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(SPACING['md'], 0))
        self.right_frame.columnconfigure(0, weight=1)
        
        # 输出文件选择（带打开文件夹按钮）
        self.output_selector = FileSelector(
            self.right_frame,
            label_text="输出文件",
            file_types=[("音频文件", "*.mp3 *.m4a *.wav"), ("所有文件", "*.*")],
            is_save=True,
            show_open_folder=True
        )
        self.output_selector.grid(row=0, column=0, sticky="ew", pady=(0, SPACING['lg']))
        
        # 配置面板
        self.config_panel = ConfigPanel(self.right_frame, self.config_manager)
        self.config_panel.grid(row=1, column=0, sticky="ew", pady=(0, SPACING['lg']))
        
        # 进度面板
        self.progress_panel = ProgressPanel(self.right_frame)
        self.progress_panel.grid(row=2, column=0, sticky="ew", pady=(0, SPACING['lg']))
        
        # 操作按钮
        self.action_buttons = ActionButtons(
            self.right_frame,
            primary_text="开始生成",
            secondary_text="取消",
            on_primary=self._on_generate,
            on_secondary=self._on_cancel
        )
        self.action_buttons.grid(row=3, column=0, sticky="w")
        
        # 设置默认输出路径
        default_output = os.path.join(
            self.config_manager.config.output_dir,
            "output.mp3"
        )
        self.output_selector.set(default_output)
        self.action_buttons.set_secondary_state(False)
    
    def _setup_layout(self) -> None:
        """设置布局权重"""
        # 已经在_create_widgets中设置了网格权重
        pass
    
    def _on_generate(self) -> None:
        """开始生成"""
        # 获取输入文本
        text = self.text_input.get(1.0, tk.END).strip()
        
        # 验证文本
        is_valid, error_msg = validate_text(text)
        if not is_valid:
            messagebox.showerror("输入错误", error_msg)
            return
        
        # 获取输出路径
        output_path = self.output_selector.get()
        if not output_path:
            messagebox.showerror("输入错误", "请选择输出文件路径")
            return
        
        # 确保输出目录存在
        FileManager.ensure_dir(output_path)
        
        # 获取配置
        config = self.config_panel.get_config()
        
        # 更新UI状态
        self.is_generating = True
        self.action_buttons.set_primary_state(False)
        self.action_buttons.set_secondary_state(True)
        self.progress_panel.reset()
        
        if self.on_status_change:
            self.on_status_change("正在生成...")
        
        # 创建TTS生成器
        self.tts_generator = TTSGenerator(
            voice=config['voice'],
            rate=config['rate'],
            volume=config['volume'],
            pitch=config['pitch']
        )
        
        # 在后台线程中执行生成
        import threading
        self.generate_thread = threading.Thread(
            target=self._generate_task,
            args=(text, output_path),
            daemon=True
        )
        self.generate_thread.start()
    
    def _generate_task(self, text: str, output_path: str) -> None:
        """生成任务（在后台线程中执行）"""
        try:
            # 更新进度
            self.after(0, lambda: self.progress_panel.set_progress(0, 1))
            
            # 生成音频
            result = self.tts_generator.generate_audio(text, output_path)
            
            # 更新进度
            self.after(0, lambda: self.progress_panel.set_progress(1, 1))
            
            if result.success:
                self.after(0, lambda: self.progress_panel.set_stats(1, 0, 1))
                self.after(0, lambda: messagebox.showinfo(
                    "生成成功", 
                    f"音频文件已生成:\n{output_path}"
                ))
            else:
                self.after(0, lambda: self.progress_panel.set_stats(0, 1, 1))
                self.after(0, lambda: messagebox.showerror(
                    "生成失败",
                    f"生成过程中出现错误:\n{result.error}"
                ))
                
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "生成异常",
                f"生成过程中出现异常:\n{str(e)}"
            ))
        finally:
            self.is_generating = False
            self.after(0, self._reset_ui_state)
    
    def _on_cancel(self) -> None:
        """取消生成"""
        if self.tts_generator:
            self.tts_generator.cancel()
        
        self.is_generating = False
        self._reset_ui_state()
    
    def _reset_ui_state(self) -> None:
        """重置UI状态"""
        self.action_buttons.set_primary_state(True)
        self.action_buttons.set_secondary_state(False)
        
        if self.on_status_change:
            self.on_status_change("就绪")
    
    def on_close(self) -> None:
        """关闭时的清理"""
        if self.tts_generator:
            self.tts_generator.cancel()
