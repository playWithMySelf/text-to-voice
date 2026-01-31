"""
GUI入口程序
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui import MainWindow


def main():
    """主函数"""
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
