"""
日志工具模块
支持文件日志和回调通知
"""
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional, Callable, List


class LogLevel(Enum):
    """日志级别"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class GUILogHandler(logging.Handler):
    """GUI日志处理器 - 将日志发送到GUI"""
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.callback = callback
        self.log_records: List[str] = []
    
    def emit(self, record: logging.LogRecord) -> None:
        """发送日志记录"""
        log_entry = self.format(record)
        self.log_records.append(log_entry)
        
        # 如果设置了回调，通知GUI
        if self.callback:
            try:
                self.callback(log_entry)
            except Exception:
                pass
    
    def set_callback(self, callback: Callable[[str], None]) -> None:
        """设置回调函数"""
        self.callback = callback
    
    def clear(self) -> None:
        """清空日志记录"""
        self.log_records.clear()
    
    def get_logs(self) -> List[str]:
        """获取所有日志记录"""
        return self.log_records.copy()


class Logger:
    """日志管理器"""
    
    _instance: Optional['Logger'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, name: str = "TTSApp", log_file: Optional[str] = None,
                 level: LogLevel = LogLevel.INFO):
        """
        初始化日志管理器
        
        Args:
            name: 日志器名称
            log_file: 日志文件路径
            level: 日志级别
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level.value)
        
        # 清除现有处理器
        self.logger.handlers.clear()
        
        # 创建格式化器
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加控制台处理器
        self._add_console_handler()
        
        # 添加文件处理器
        if log_file:
            self._add_file_handler(log_file)
        
        # 添加GUI处理器
        self.gui_handler = GUILogHandler()
        self.gui_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.gui_handler)
    
    def _add_console_handler(self) -> None:
        """添加控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)
    
    def _add_file_handler(self, log_file: str) -> None:
        """添加文件处理器"""
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)
    
    def set_gui_callback(self, callback: Callable[[str], None]) -> None:
        """
        设置GUI回调函数
        
        Args:
            callback: 回调函数，接收日志字符串
        """
        self.gui_handler.set_callback(callback)
    
    def debug(self, message: str) -> None:
        """记录DEBUG级别日志"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """记录INFO级别日志"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录WARNING级别日志"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """记录ERROR级别日志"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """记录CRITICAL级别日志"""
        self.logger.critical(message)
    
    def clear_gui_logs(self) -> None:
        """清空GUI日志"""
        self.gui_handler.clear()
    
    def get_gui_logs(self) -> List[str]:
        """获取GUI日志记录"""
        return self.gui_handler.get_logs()


# 全局日志实例
_logger: Optional[Logger] = None


def get_logger(name: str = "TTSApp", log_file: Optional[str] = None,
               level: LogLevel = LogLevel.INFO) -> Logger:
    """
    获取日志管理器实例（单例模式）
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径
        level: 日志级别
        
    Returns:
        Logger: 日志管理器实例
    """
    global _logger
    if _logger is None:
        _logger = Logger(name, log_file, level)
    return _logger
