"""
GUI可复用组件 - 优化版（移除日志，添加打开文件夹功能）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, List, Tuple
from .styles import (
    COLORS, FONTS, SPACING, 
    get_button_style, get_input_style, get_label_style, get_card_style
)


class LabeledEntry(tk.Frame):
    """带标签的输入框组件"""
    
    def __init__(self, parent, label_text: str, **entry_kwargs):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        self.label = tk.Label(
            self, 
            text=label_text,
            **get_label_style()
        )
        self.label.pack(side=tk.LEFT, padx=(0, SPACING['sm']))
        
        self.entry = tk.Entry(self, **get_input_style(), **entry_kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, value: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class FileSelector(tk.Frame):
    """文件选择器组件（带打开文件夹按钮）"""
    
    def __init__(self, parent, label_text: str, file_types: List[Tuple[str, str]],
                 on_select: Optional[Callable[[str], None]] = None,
                 is_save: bool = False, show_open_folder: bool = True):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        self.file_types = file_types
        self.on_select = on_select
        self.is_save = is_save
        self.show_open_folder = show_open_folder
        
        # 标签
        self.label = tk.Label(
            self,
            text=label_text,
            **get_label_style()
        )
        self.label.pack(anchor=tk.W, pady=(0, SPACING['xs']))
        
        # 输入框和按钮容器
        self.input_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.input_frame.pack(fill=tk.X)
        
        # 输入框
        self.entry = tk.Entry(self.input_frame, **get_input_style())
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING['sm']))
        
        # 按钮容器
        self.btn_frame = tk.Frame(self.input_frame, bg=COLORS['bg_primary'])
        self.btn_frame.pack(side=tk.RIGHT)
        
        # 浏览按钮
        btn_style = get_button_style(primary=False)
        self.browse_btn = tk.Button(
            self.btn_frame,
            text="浏览...",
            command=self._browse_file,
            **btn_style
        )
        self.browse_btn.pack(side=tk.LEFT, padx=(0, SPACING['xs']))
        
        # 打开文件夹按钮
        if show_open_folder:
            self.open_folder_btn = tk.Button(
                self.btn_frame,
                text="打开文件夹",
                command=self._open_folder,
                **btn_style
            )
            self.open_folder_btn.pack(side=tk.LEFT)
    
    def _browse_file(self) -> None:
        """打开文件选择对话框"""
        if self.is_save:
            file_path = filedialog.asksaveasfilename(
                filetypes=self.file_types,
                defaultextension=self.file_types[0][1] if self.file_types else ""
            )
        else:
            file_path = filedialog.askopenfilename(filetypes=self.file_types)
        
        if file_path:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, file_path)
            
            if self.on_select:
                self.on_select(file_path)
    
    def _open_folder(self) -> None:
        """打开文件所在文件夹"""
        file_path = self.entry.get()
        if not file_path:
            messagebox.showwarning("提示", "请先选择文件")
            return
        
        import os
        from src.core import FileManager
        
        # 获取文件夹路径
        if os.path.isdir(file_path):
            folder_path = file_path
        else:
            folder_path = os.path.dirname(file_path) or '.'
        
        # 确保文件夹存在
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建文件夹: {e}")
                return
        
        # 打开文件夹
        success = FileManager.open_folder(folder_path)
        if not success:
            messagebox.showerror("错误", "无法打开文件夹")
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, value: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class VoiceSelector(tk.Frame):
    """音色选择器组件 - 美化的自定义下拉框"""
    
    def __init__(self, parent, voices: List[Tuple[str, str]], 
                 default_voice: str = "",
                 on_change: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        self.voices = voices
        self.voice_ids = [v[0] for v in voices]
        self.voice_names = [v[1] for v in voices]
        self.on_change = on_change
        self.is_open = False
        
        # 标签
        self.label = tk.Label(
            self,
            text="选择音色",
            **get_label_style()
        )
        self.label.pack(anchor=tk.W, pady=(0, SPACING['xs']))
        
        # 当前选中的值
        self.var = tk.StringVar()
        if default_voice and default_voice in self.voice_ids:
            default_name = self.voice_names[self.voice_ids.index(default_voice)]
            self.var.set(default_name)
        elif self.voice_names:
            self.var.set(self.voice_names[0])
        
        # 自定义下拉框按钮
        self.dropdown_btn = tk.Frame(
            self,
            bg=COLORS['bg_input'],
            highlightthickness=1,
            highlightcolor=COLORS['border'],
            highlightbackground=COLORS['border'],
            cursor='hand2'
        )
        self.dropdown_btn.pack(fill=tk.X)
        self.dropdown_btn.bind('<Button-1>', self._toggle_dropdown)
        
        # 选中的文本
        self.selected_label = tk.Label(
            self.dropdown_btn,
            textvariable=self.var,
            bg=COLORS['bg_input'],
            fg=COLORS['text_primary'],
            font=(FONTS['family'], FONTS['size_normal']),
            padx=SPACING['sm'],
            pady=SPACING['sm'],
            anchor='w',
            cursor='hand2'
        )
        self.selected_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.selected_label.bind('<Button-1>', self._toggle_dropdown)
        
        # 下拉箭头
        self.arrow_label = tk.Label(
            self.dropdown_btn,
            text="▼",
            bg=COLORS['bg_input'],
            fg=COLORS['accent'],
            font=(FONTS['family'], 8),
            padx=SPACING['sm'],
            cursor='hand2'
        )
        self.arrow_label.pack(side=tk.RIGHT)
        self.arrow_label.bind('<Button-1>', self._toggle_dropdown)
        
        # 悬停效果
        self.dropdown_btn.bind('<Enter>', self._on_hover)
        self.dropdown_btn.bind('<Leave>', self._on_leave)
        self.selected_label.bind('<Enter>', self._on_hover)
        self.selected_label.bind('<Leave>', self._on_leave)
        self.arrow_label.bind('<Enter>', self._on_hover)
        self.arrow_label.bind('<Leave>', self._on_leave)
        
        # 下拉列表窗口（初始隐藏）
        self.list_window = None
        
    def _on_hover(self, event=None):
        """鼠标悬停效果"""
        self.dropdown_btn.configure(highlightcolor=COLORS['accent'])
        self.arrow_label.configure(fg=COLORS['btn_primary_hover'])
        
    def _on_leave(self, event=None):
        """鼠标离开效果"""
        if not self.is_open:
            self.dropdown_btn.configure(highlightcolor=COLORS['border'])
            self.arrow_label.configure(fg=COLORS['accent'])
    
    def _toggle_dropdown(self, event=None):
        """切换下拉列表显示/隐藏"""
        if self.is_open:
            self._close_dropdown()
        else:
            self._open_dropdown()
    
    def _open_dropdown(self):
        """打开下拉列表"""
        self.is_open = True
        self.arrow_label.configure(text="▲")
        self.dropdown_btn.configure(highlightcolor=COLORS['accent'])
        
        # 创建下拉列表窗口
        x = self.dropdown_btn.winfo_rootx()
        y = self.dropdown_btn.winfo_rooty() + self.dropdown_btn.winfo_height()
        
        self.list_window = tk.Toplevel(self)
        self.list_window.overrideredirect(True)
        self.list_window.geometry(f"{self.dropdown_btn.winfo_width()}x200+{x}+{y}")
        self.list_window.configure(bg=COLORS['bg_card'])
        
        # 创建滚动区域
        canvas = tk.Canvas(
            self.list_window,
            bg=COLORS['bg_card'],
            highlightthickness=0,
            bd=0
        )
        scrollbar = tk.Scrollbar(
            self.list_window,
            orient="vertical",
            command=canvas.yview,
            bg=COLORS['bg_secondary'],
            troughcolor=COLORS['bg_card'],
            activebackground=COLORS['accent']
        )
        
        self.list_frame = tk.Frame(canvas, bg=COLORS['bg_card'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=self.dropdown_btn.winfo_width())
        
        # 添加选项
        for i, voice_name in enumerate(self.voice_names):
            option_frame = tk.Frame(
                self.list_frame,
                bg=COLORS['bg_card'],
                cursor='hand2'
            )
            option_frame.pack(fill=tk.X)
            
            # 选项标签
            option_label = tk.Label(
                option_frame,
                text=voice_name,
                bg=COLORS['bg_card'],
                fg=COLORS['text_primary'],
                font=(FONTS['family'], FONTS['size_normal']),
                padx=SPACING['sm'],
                pady=SPACING['xs'],
                anchor='w',
                cursor='hand2'
            )
            option_label.pack(fill=tk.X)
            
            # 悬停效果
            def on_option_enter(e, frame=option_frame, label=option_label):
                frame.configure(bg=COLORS['accent'])
                label.configure(bg=COLORS['accent'])
                
            def on_option_leave(e, frame=option_frame, label=option_label):
                frame.configure(bg=COLORS['bg_card'])
                label.configure(bg=COLORS['bg_card'])
            
            option_frame.bind('<Enter>', on_option_enter)
            option_frame.bind('<Leave>', on_option_leave)
            option_label.bind('<Enter>', on_option_enter)
            option_label.bind('<Leave>', on_option_leave)
            
            # 点击选择
            def on_option_click(e, name=voice_name):
                self._select_voice(name)
                
            option_frame.bind('<Button-1>', on_option_click)
            option_label.bind('<Button-1>', on_option_click)
            
            # 分隔线
            if i < len(self.voice_names) - 1:
                separator = tk.Frame(
                    self.list_frame,
                    bg=COLORS['border'],
                    height=1
                )
                separator.pack(fill=tk.X, padx=SPACING['sm'])
        
        self.list_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # 点击外部关闭
        self.list_window.bind('<FocusOut>', lambda e: self._close_dropdown())
        self.list_window.focus_set()
        
        # 绑定全局点击事件
        self.master.bind_all('<Button-1>', self._on_global_click)
    
    def _on_global_click(self, event):
        """全局点击事件，点击外部关闭下拉列表"""
        if self.list_window and self.list_window.winfo_exists():
            # 检查点击是否在下拉列表或按钮内
            x, y = event.x_root, event.y_root
            list_x1 = self.list_window.winfo_rootx()
            list_y1 = self.list_window.winfo_rooty()
            list_x2 = list_x1 + self.list_window.winfo_width()
            list_y2 = list_y1 + self.list_window.winfo_height()
            
            btn_x1 = self.dropdown_btn.winfo_rootx()
            btn_y1 = self.dropdown_btn.winfo_rooty()
            btn_x2 = btn_x1 + self.dropdown_btn.winfo_width()
            btn_y2 = btn_y1 + self.dropdown_btn.winfo_height()
            
            if not (list_x1 <= x <= list_x2 and list_y1 <= y <= list_y2) and \
               not (btn_x1 <= x <= btn_x2 and btn_y1 <= y <= btn_y2):
                self._close_dropdown()
    
    def _close_dropdown(self):
        """关闭下拉列表"""
        self.is_open = False
        self.arrow_label.configure(text="▼")
        self.dropdown_btn.configure(highlightcolor=COLORS['border'])
        
        if self.list_window and self.list_window.winfo_exists():
            self.list_window.destroy()
            self.list_window = None
        
        # 解绑全局点击事件
        self.master.unbind_all('<Button-1>')
    
    def _select_voice(self, voice_name: str):
        """选择音色"""
        self.var.set(voice_name)
        self._close_dropdown()
        
        if self.on_change:
            voice_id = self.get()
            self.on_change(voice_id)
    
    def get(self) -> str:
        """获取选中的音色ID"""
        selected_name = self.var.get()
        if selected_name in self.voice_names:
            return self.voice_ids[self.voice_names.index(selected_name)]
        return ""
    
    def set(self, voice_id: str) -> None:
        """设置选中的音色"""
        if voice_id in self.voice_ids:
            self.var.set(self.voice_names[self.voice_ids.index(voice_id)])


class SliderWithLabel(tk.Frame):
    """带标签和数值显示的滑块组件"""
    
    def __init__(self, parent, label_text: str, from_: int, to: int,
                 default: int = 0, suffix: str = "%",
                 on_change: Optional[Callable[[int], None]] = None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        self.suffix = suffix
        self.on_change = on_change
        
        self.header_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.header_frame.pack(fill=tk.X)
        
        self.label = tk.Label(
            self.header_frame,
            text=label_text,
            **get_label_style()
        )
        self.label.pack(side=tk.LEFT)
        
        self.value_var = tk.StringVar(value=f"{default:+d}{suffix}")
        self.value_label = tk.Label(
            self.header_frame,
            textvariable=self.value_var,
            fg=COLORS['accent'],
            bg=COLORS['bg_primary'],
            font=(FONTS['family'], FONTS['size_normal'], 'bold')
        )
        self.value_label.pack(side=tk.RIGHT)
        
        self.slider = tk.Scale(
            self,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            showvalue=0,
            bg=COLORS['bg_primary'],
            fg=COLORS['text_primary'],
            highlightthickness=0,
            troughcolor=COLORS['bg_secondary'],
            activebackground=COLORS['accent'],
            command=self._on_slide
        )
        self.slider.set(default)
        self.slider.pack(fill=tk.X, pady=(SPACING['xs'], 0))
    
    def _on_slide(self, value) -> None:
        int_value = int(float(value))
        self.value_var.set(f"{int_value:+d}{self.suffix}")
        
        if self.on_change:
            self.on_change(int_value)
    
    def get(self) -> int:
        return self.slider.get()
    
    def set(self, value: int) -> None:
        self.slider.set(value)
        self.value_var.set(f"{value:+d}{self.suffix}")


class ProgressPanel(tk.Frame):
    """进度面板组件（简洁版）"""
    
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # 进度信息
        self.info_label = tk.Label(
            self,
            text="准备就绪",
            **get_label_style(is_secondary=True)
        )
        self.info_label.pack(anchor=tk.W, pady=(0, SPACING['xs']))
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style='Modern.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X)
        
        # 统计信息
        self.stats_label = tk.Label(
            self,
            text="",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary'],
            font=(FONTS['family'], FONTS['size_small'])
        )
        self.stats_label.pack(anchor=tk.W, pady=(SPACING['xs'], 0))
    
    def set_progress(self, current: int, total: int) -> None:
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.info_label.configure(
                text=f"进度: {current}/{total} ({percentage:.1f}%)",
                fg=COLORS['accent']
            )
        else:
            self.progress_var.set(0)
            self.info_label.configure(text="准备就绪", fg=COLORS['text_secondary'])
    
    def set_stats(self, success: int, failed: int, total: int) -> None:
        self.stats_label.configure(
            text=f"成功: {success} | 失败: {failed} | 总计: {total}"
        )
    
    def reset(self) -> None:
        self.progress_var.set(0)
        self.info_label.configure(text="准备就绪", fg=COLORS['text_secondary'])
        self.stats_label.configure(text="")


class ActionButtons(tk.Frame):
    """操作按钮组组件"""
    
    def __init__(self, parent, 
                 primary_text: str = "开始",
                 secondary_text: str = "取消",
                 on_primary: Optional[Callable] = None,
                 on_secondary: Optional[Callable] = None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        # 主按钮
        primary_style = get_button_style(primary=True)
        self.primary_btn = tk.Button(
            self,
            text=primary_text,
            command=on_primary,
            **primary_style
        )
        self.primary_btn.pack(side=tk.LEFT, padx=(0, SPACING['sm']))
        
        # 次按钮
        secondary_style = get_button_style(primary=False)
        self.secondary_btn = tk.Button(
            self,
            text=secondary_text,
            command=on_secondary,
            **secondary_style
        )
        self.secondary_btn.pack(side=tk.LEFT)
    
    def set_primary_state(self, enabled: bool) -> None:
        self.primary_btn.configure(state=tk.NORMAL if enabled else tk.DISABLED)
    
    def set_secondary_state(self, enabled: bool) -> None:
        self.secondary_btn.configure(state=tk.NORMAL if enabled else tk.DISABLED)


class ConfigPanel(tk.LabelFrame):
    """配置面板组件"""
    
    def __init__(self, parent, config_manager):
        super().__init__(
            parent,
            text="语音配置",
            bg=COLORS['bg_card'],
            fg=COLORS['text_primary'],
            font=(FONTS['family'], FONTS['size_medium'], 'bold'),
            relief='flat',
            highlightthickness=1,
            highlightcolor=COLORS['border'],
            highlightbackground=COLORS['border'],
            padx=SPACING['md'],
            pady=SPACING['md']
        )
        
        self.config_manager = config_manager
        tts_config = config_manager.tts
        
        # 音色选择
        self.voice_selector = VoiceSelector(
            self,
            voices=config_manager.AVAILABLE_VOICES,
            default_voice=tts_config.voice
        )
        self.voice_selector.pack(fill=tk.X, pady=(0, SPACING['md']))
        
        # 语速滑块
        self.rate_slider = SliderWithLabel(
            self,
            label_text="语速调整",
            from_=-50,
            to=50,
            default=self._parse_percent(tts_config.rate),
            suffix="%"
        )
        self.rate_slider.pack(fill=tk.X, pady=(0, SPACING['md']))
        
        # 音量滑块
        self.volume_slider = SliderWithLabel(
            self,
            label_text="音量调整",
            from_=0,
            to=100,
            default=self._parse_percent(tts_config.volume),
            suffix="%"
        )
        self.volume_slider.pack(fill=tk.X)
    
    def _parse_percent(self, value: str) -> int:
        try:
            return int(value.replace('%', ''))
        except ValueError:
            return 0
    
    def get_config(self) -> dict:
        return {
            'voice': self.voice_selector.get(),
            'rate': f"{self.rate_slider.get():+d}%",
            'volume': f"{self.volume_slider.get():+d}%",
            'pitch': 'default'
        }
