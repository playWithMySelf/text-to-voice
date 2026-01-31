"""
CSV处理器 - 合并读取和结果记录功能
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from src.config import get_config_manager


@dataclass
class ConversionRecord:
    """转换记录数据类"""
    index: int
    text_preview: str
    file_path: str
    status: str  # '成功' 或 '失败'
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@dataclass
class ConversionResult:
    """转换结果数据类"""
    records: List[ConversionRecord] = field(default_factory=list)
    
    @property
    def success_count(self) -> int:
        """成功数量"""
        return sum(1 for r in self.records if r.status == '成功')
    
    @property
    def failed_count(self) -> int:
        """失败数量"""
        return sum(1 for r in self.records if r.status == '失败')
    
    @property
    def total_count(self) -> int:
        """总数"""
        return len(self.records)


class CSVProcessor:
    """CSV处理器 - 读取CSV和记录结果"""
    
    def __init__(self, file_path: Optional[str] = None):
        """
        初始化CSV处理器
        
        Args:
            file_path: CSV文件路径
        """
        self.file_path = Path(file_path) if file_path else None
        self.config = get_config_manager().config
        self._result = ConversionResult()
    
    def read(self, max_records: Optional[int] = None) -> List[Dict[str, str]]:
        """
        读取CSV文件
        
        Args:
            max_records: 最大读取记录数，None表示读取所有
            
        Returns:
            List[Dict[str, str]]: 包含answer_text和file_path的字典列表
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: CSV格式错误或缺少必要列
        """
        if not self.file_path or not self.file_path.exists():
            raise FileNotFoundError(f"CSV文件不存在: {self.file_path}")
        
        try:
            # 读取CSV文件
            data = pd.read_csv(self.file_path, encoding=self.config.csv_encoding)
            
            # 检查必要的列是否存在
            if self.config.answer_text_column not in data.columns:
                raise ValueError(f"CSV文件中缺少必要的列: {self.config.answer_text_column}")
            if self.config.file_path_column not in data.columns:
                raise ValueError(f"CSV文件中缺少必要的列: {self.config.file_path_column}")
            
            # 提取需要的列
            records = []
            for _, row in data.iterrows():
                record = {
                    self.config.answer_text_column: str(row[self.config.answer_text_column]) if pd.notna(row[self.config.answer_text_column]) else "",
                    self.config.file_path_column: str(row[self.config.file_path_column]) if pd.notna(row[self.config.file_path_column]) else ""
                }
                records.append(record)
                
                # 如果达到最大记录数，停止读取
                if max_records is not None and len(records) >= max_records:
                    break
            
            return records
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV文件为空")
        except pd.errors.ParserError as e:
            raise ValueError(f"CSV解析错误: {e}")
        except Exception as e:
            raise ValueError(f"读取CSV文件失败: {e}")
    
    def add_record(self, index: int, answer_text: str, file_path: str, 
                   status: str, message: str = "") -> None:
        """
        添加一条转换记录
        
        Args:
            index: 记录序号
            answer_text: 文本内容
            file_path: 输出文件路径
            status: 状态（成功/失败）
            message: 附加消息
        """
        text_preview = answer_text[:50] + "..." if len(answer_text) > 50 else answer_text
        
        record = ConversionRecord(
            index=index,
            text_preview=text_preview,
            file_path=file_path,
            status=status,
            message=message
        )
        
        self._result.records.append(record)
    
    def save_result(self, output_file: Optional[str] = None) -> str:
        """
        保存结果到Markdown文件
        
        Args:
            output_file: 输出文件路径，默认使用配置文件中的路径
            
        Returns:
            str: 保存的文件路径
        """
        if output_file is None:
            output_file = self.config.result_file
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# TTS转换结果记录\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**总记录数**: {self._result.total_count}\n\n")
            
            # 写入统计信息
            f.write("## 统计信息\n\n")
            f.write(f"| 项目 | 数量 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 成功 | {self._result.success_count} |\n")
            f.write(f"| 失败 | {self._result.failed_count} |\n")
            f.write(f"| 总计 | {self._result.total_count} |\n\n")
            
            # 写入详细记录表格
            f.write("## 详细记录\n\n")
            f.write("| 序号 | 文本预览 | 输出路径 | 状态 | 时间 | 备注 |\n")
            f.write("|------|----------|----------|------|------|------|\n")
            
            for record in self._result.records:
                status_icon = "✅" if record.status == '成功' else "❌"
                f.write(f"| {record.index} | {record.text_preview} | "
                       f"`{record.file_path}` | {status_icon} {record.status} | "
                       f"{record.timestamp} | {record.message} |\n")
            
            f.write("\n---\n")
            f.write("\n*此文件由TTS转换程序自动生成*\n")
        
        return output_file
    
    def get_result(self) -> ConversionResult:
        """获取转换结果"""
        return self._result
    
    def clear_result(self) -> None:
        """清空结果"""
        self._result = ConversionResult()
    
    @staticmethod
    def create_template(output_path: str = "template.csv") -> str:
        """
        创建CSV模板文件（带BOM，解决Excel中文乱码）
        
        Args:
            output_path: 输出路径
            
        Returns:
            str: 创建的文件路径
        """
        import csv
        
        template_data = [
            ['answer_text', 'file_path'],
            ['这是第一条要转换的文本内容', 'output/audio1.mp3'],
            ['这是第二条要转换的文本内容', 'output/audio2.mp3'],
            ['欢迎使用文本转语音工具', 'output/audio3.mp3']
        ]
        
        # 使用UTF-8 with BOM编码，解决Excel中文乱码问题
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(template_data)
        
        return output_path
