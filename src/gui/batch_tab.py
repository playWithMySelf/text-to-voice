"""
批量生成标签页 - 优化版（自适应布局）
"""
import os
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable

from .styles import COLORS, SPACING, get_label_style, get_button_style, get_card_style
from .components import (
    FileSelector, ConfigPanel, ActionButtons, ProgressPanel
)
from src.config import get_config_manager
from src.core import TTSGenerator, CSVProcessor, FileManager, TTSTask
from src.utils import validate_csv_file


class BatchTab(tk.Frame):
    """批量生成标签页"""
    
    def __init__(self, parent, on_status_change: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=COLORS['bg_primary'])
        
        self.config_manager = get_config_manager()
        self.on_status_change = on_status_change
        self.tts_generator: Optional[TTSGenerator] = None
        self.csv_processor: Optional[CSVProcessor] = None
        self.is_generating = False
        self.tasks = []
        self.results = {'success': 0, 'failed': 0}
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """创建界面组件"""
        # 使用网格布局实现自适应
        self.columnconfigure(0, weight=3)  # 左侧占3份
        self.columnconfigure(1, weight=2)  # 右侧占2份
        self.rowconfigure(0, weight=1)
        
        # ===== 左侧面板 - CSV选择 =====
        self.left_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING['md']))
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=1)
        
        # CSV标签
        self.csv_label = tk.Label(
            self.left_frame,
            text="CSV文件",
            **get_label_style()
        )
        self.csv_label.grid(row=0, column=0, sticky="w", pady=(0, SPACING['xs']))
        
        # CSV文件选择区域（卡片样式）
        self.csv_card = tk.Frame(self.left_frame, **get_card_style())
        self.csv_card.grid(row=1, column=0, sticky="nsew")
        self.csv_card.columnconfigure(0, weight=1)
        
        self.csv_selector = FileSelector(
            self.csv_card,
            label_text="",
            file_types=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            on_select=self._on_csv_selected,
            show_open_folder=True
        )
        self.csv_selector.pack(fill=tk.X, pady=(0, SPACING['sm']))
        
        # 下载模板按钮
        btn_style = get_button_style(primary=False)
        self.template_btn = tk.Button(
            self.csv_card,
            text="下载CSV模板",
            command=self._download_template,
            **btn_style
        )
        self.template_btn.pack(anchor=tk.W, pady=(SPACING['sm'], 0))
        
        # CSV信息标签
        self.csv_info_label = tk.Label(
            self.csv_card,
            text="请选择CSV文件",
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_card'],
            font=(COLORS.get('font_family', 'Microsoft YaHei UI'), 9)
        )
        self.csv_info_label.pack(anchor=tk.W, pady=(SPACING['xs'], 0))
        
        # ===== 右侧面板 - 配置和操作 =====
        self.right_frame = tk.Frame(self, bg=COLORS['bg_primary'])
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(SPACING['md'], 0))
        self.right_frame.columnconfigure(0, weight=1)
        
        # 配置面板
        self.config_panel = ConfigPanel(self.right_frame, self.config_manager)
        self.config_panel.grid(row=0, column=0, sticky="ew", pady=(0, SPACING['lg']))
        
        # 进度面板
        self.progress_panel = ProgressPanel(self.right_frame)
        self.progress_panel.grid(row=1, column=0, sticky="ew", pady=(0, SPACING['lg']))
        
        # 操作按钮
        self.action_buttons = ActionButtons(
            self.right_frame,
            primary_text="开始批量生成",
            secondary_text="取消",
            on_primary=self._on_generate,
            on_secondary=self._on_cancel
        )
        self.action_buttons.grid(row=2, column=0, sticky="w")
        self.action_buttons.set_secondary_state(False)
    
    def _on_csv_selected(self, file_path: str) -> None:
        """CSV文件选择后"""
        try:
            is_valid, error_msg = validate_csv_file(file_path)
            if not is_valid:
                self.csv_info_label.configure(
                    text=f"文件无效: {error_msg}",
                    fg=COLORS['error']
                )
                return
            
            processor = CSVProcessor(file_path)
            records = processor.read()
            
            self.csv_info_label.configure(
                text=f"共 {len(records)} 条记录",
                fg=COLORS['success']
            )
            
        except Exception as e:
            self.csv_info_label.configure(
                text=f"读取失败: {str(e)}",
                fg=COLORS['error']
            )
    
    def _download_template(self) -> None:
        """下载CSV模板"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            initialfile="template.csv"
        )
        
        if file_path:
            try:
                CSVProcessor.create_template(file_path)
                messagebox.showinfo("下载成功", f"模板已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("下载失败", f"保存模板失败:\n{str(e)}")
    
    def _on_generate(self) -> None:
        """开始批量生成"""
        csv_path = self.csv_selector.get()
        
        is_valid, error_msg = validate_csv_file(csv_path)
        if not is_valid:
            messagebox.showerror("输入错误", error_msg)
            return
        
        try:
            self.csv_processor = CSVProcessor(csv_path)
            records = self.csv_processor.read()
        except Exception as e:
            messagebox.showerror("读取错误", f"读取CSV文件失败:\n{str(e)}")
            return
        
        if not records:
            messagebox.showwarning("无数据", "CSV文件中没有有效记录")
            return
        
        # 准备任务
        self.tasks = []
        config = self.config_manager.config
        
        for i, record in enumerate(records, 1):
            answer_text = record.get(config.answer_text_column, '').strip()
            file_path = record.get(config.file_path_column, '').strip()
            
            if not answer_text:
                self.csv_processor.add_record(i, "", file_path, '失败', '文本内容为空')
                continue
            
            output_path = FileManager.process_output_path(
                file_path, i, config.output_dir
            )
            FileManager.ensure_dir(output_path)
            
            self.tasks.append(TTSTask(
                text=answer_text,
                output_path=output_path,
                index=i
            ))
        
        if not self.tasks:
            messagebox.showwarning("无有效任务", "没有有效的转换任务")
            return
        
        tts_config = self.config_panel.get_config()
        
        # 更新UI状态
        self.is_generating = True
        self.results = {'success': 0, 'failed': 0}
        self.action_buttons.set_primary_state(False)
        self.action_buttons.set_secondary_state(True)
        self.progress_panel.reset()
        
        if self.on_status_change:
            self.on_status_change(f"正在批量生成 (0/{len(self.tasks)})...")
        
        # 创建TTS生成器
        self.tts_generator = TTSGenerator(
            voice=tts_config['voice'],
            rate=tts_config['rate'],
            volume=tts_config['volume'],
            pitch=tts_config['pitch']
        )
        
        # 在后台线程中执行生成
        import threading
        self.generate_thread = threading.Thread(
            target=self._generate_task,
            daemon=True
        )
        self.generate_thread.start()
    
    def _generate_task(self) -> None:
        """批量生成任务（在后台线程中执行）"""
        try:
            def progress_callback(completed, total, result):
                self.after(0, lambda: self._update_progress(completed, total, result))
            
            # 批量生成
            results = self.tts_generator.batch_generate_sync(
                self.tasks,
                max_concurrent=self.config_manager.tts.concurrent,
                progress_callback=progress_callback
            )
            
            # 处理结果
            for result in results:
                status = '成功' if result.success else '失败'
                self.csv_processor.add_record(
                    result.index,
                    result.text_preview,
                    result.output_path,
                    status,
                    result.error
                )
            
            # 保存结果
            result_file = self.csv_processor.save_result()
            
            # 显示完成消息
            self.after(0, lambda: self._show_completion(results))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "生成异常",
                f"批量生成过程中出现异常:\n{str(e)}"
            ))
        finally:
            self.is_generating = False
            self.after(0, self._reset_ui_state)
    
    def _update_progress(self, completed: int, total: int, result) -> None:
        """更新进度"""
        self.progress_panel.set_progress(completed, total)
        
        if result.success:
            self.results['success'] += 1
        else:
            self.results['failed'] += 1
        
        self.progress_panel.set_stats(
            self.results['success'],
            self.results['failed'],
            total
        )
        
        if self.on_status_change:
            self.on_status_change(f"正在批量生成 ({completed}/{total})...")
    
    def _show_completion(self, results) -> None:
        """显示完成消息"""
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        message = f"批量生成完成！\n\n成功: {success_count}\n失败: {failed_count}\n总计: {len(results)}"
        
        if failed_count == 0:
            messagebox.showinfo("生成完成", message)
        else:
            messagebox.showwarning("生成完成", message + "\n\n部分任务生成失败，请查看result.md了解详情。")
    
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
