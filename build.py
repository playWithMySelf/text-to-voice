#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键打包脚本 - 文本转语音工具
使用: python build.py
"""

import os
import sys
import shutil
import subprocess
import time


def print_step(msg):
    """打印步骤信息"""
    print(f"\n{'='*50}")
    print(f"  {msg}")
    print('='*50)


def print_success(msg):
    """打印成功信息"""
    print(f"  ✓ {msg}")


def print_warning(msg):
    """打印警告信息"""
    print(f"  ⚠ {msg}")


def print_error(msg):
    """打印错误信息"""
    print(f"  ✗ {msg}")


def kill_running_exe():
    """终止正在运行的程序实例"""
    print("  检查并终止正在运行的程序...")
    try:
        # 尝试终止可能运行的exe
        subprocess.run(
            'taskkill /F /IM "文本转语音工具.exe" 2>nul',
            shell=True,
            capture_output=True
        )
        time.sleep(1)
    except Exception:
        pass


def clean_build_dirs():
    """清理构建目录"""
    print_step("步骤 1/4: 清理构建目录")
    
    dirs_to_remove = ['build', 'dist']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name, ignore_errors=True)
                print_success(f"已删除 {dir_name}/")
            except Exception as e:
                print_error(f"删除 {dir_name}/ 失败: {e}")
    
    # 清理 __pycache__
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                try:
                    shutil.rmtree(os.path.join(root, dir_name), ignore_errors=True)
                except Exception:
                    pass
    
    print_success("清理完成")
    time.sleep(0.5)


def install_dependencies():
    """安装/检查依赖"""
    print_step("步骤 2/5: 检查依赖")
    
    required_packages = ['pyinstaller', 'edge-tts', 'pandas', 'aiofiles']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} 已安装")
        except ImportError:
            print(f"  → 正在安装 {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         capture_output=True)
            print_success(f"{package} 安装完成")
    
    time.sleep(0.5)


def convert_icon():
    """转换SVG图标为ICO格式"""
    print_step("步骤 3/5: 生成应用图标")
    
    svg_path = os.path.join('assets', 'icon.svg')
    ico_path = os.path.join('assets', 'icon.ico')
    
    if not os.path.exists(svg_path):
        print_error(f"未找到图标文件: {svg_path}")
        print("  请确保 assets/icon.svg 存在")
        return False
    
    # 检查是否需要重新生成图标
    need_convert = True
    if os.path.exists(ico_path):
        svg_mtime = os.path.getmtime(svg_path)
        ico_mtime = os.path.getmtime(ico_path)
        if ico_mtime >= svg_mtime:
            print_success("图标已是最新，跳过转换")
            need_convert = False
    
    if not need_convert:
        # 验证 ICO 文件有效性
        try:
            from PIL import Image
            with Image.open(ico_path) as img:
                print_success(f"图标文件有效: {ico_path}")
                print(f"  尺寸: {img.size if hasattr(img, 'size') else 'N/A'}")
            return True
        except Exception as e:
            print_error(f"图标文件无效，将重新生成: {e}")
            need_convert = True
    
    # 转换图标
    try:
        import cairosvg
        from PIL import Image
        import io
        
        sizes = [16, 32, 48, 64, 128, 256]
        
        images = []
        for size in sizes:
            png_data = cairosvg.svg2png(
                url=svg_path,
                output_width=size,
                output_height=size
            )
            img = Image.open(io.BytesIO(png_data))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            images.append(img)
        
        images[0].save(
            ico_path,
            format='ICO',
            sizes=[(s, s) for s in sizes],
            append_images=images[1:]
        )
        
        print_success(f"图标已生成: {ico_path}")
        return True
        
    except ImportError:
        print("  → 未安装 cairosvg 或 PIL，尝试安装...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 
                          'cairosvg', 'Pillow'], capture_output=True)
            print_success("依赖安装完成，请重新运行打包脚本")
            return False
        except Exception as e:
            print_error(f"安装依赖失败: {e}")
            return False
            
    except Exception as e:
        print_error(f"图标转换失败: {e}")
        return False


def build_exe():
    """执行打包"""
    print_step("步骤 4/5: 开始打包")
    
    try:
        # 执行 pyinstaller
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '文本转语音工具.spec'],
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print_error("打包失败")
            return False
        
        print_success("打包成功")
        return True
        
    except Exception as e:
        print_error(f"打包出错: {e}")
        return False


def copy_additional_files():
    """复制额外文件到dist目录"""
    print_step("步骤 5/5: 复制资源文件")
    
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    if os.path.exists('README.md'):
        shutil.copy('README.md', 'dist/')
        print_success("已复制 README.md")
    
    print_success("资源文件复制完成")


def verify_icon(exe_path):
    """验证exe文件图标"""
    print("  验证应用图标...")
    try:
        import struct
        with open(exe_path, 'rb') as f:
            data = f.read()
        
        if b'\x00\x00\x03\x00' in data or b'\x03\x00\x00\x00' in data:
            print_success("exe 文件包含图标资源")
            return True
        else:
            print_warning("exe 文件可能未包含图标，请检查 icon.ico 文件")
            return False
    except Exception as e:
        print_warning(f"无法验证图标: {e}")
        return False


def show_result():
    """显示打包结果"""
    print_step("打包完成")
    
    exe_path = 'dist/文本转语音工具.exe'
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"""
  输出文件: {exe_path}
  文件大小: {size_mb:.2f} MB
        """)
        verify_icon(exe_path)
        print("""
  使用方式:
    1. 直接双击运行: dist/文本转语音工具.exe
    2. 或复制到任意位置使用
        """)
        print_success("打包成功！")
    else:
        print_error("未找到输出文件，请检查错误信息")


def main():
    """主函数"""
    print("""
  ╔══════════════════════════════════════════╗
  ║     文本转语音工具 - 一键打包脚本         ║
  ╚══════════════════════════════════════════╝
    """)
    
    # 检查是否在正确目录
    if not os.path.exists('gui_main.py'):
        print_error("错误: 请在项目根目录运行此脚本")
        print("  当前目录: " + os.getcwd())
        sys.exit(1)
    
    if not os.path.exists('文本转语音工具.spec'):
        print_error("错误: 未找到 文本转语音工具.spec 文件")
        sys.exit(1)
    
    # 终止可能运行的实例
    kill_running_exe()
    
    # 执行打包流程
    clean_build_dirs()
    install_dependencies()
    convert_icon()  # 转换图标
    
    if build_exe():
        copy_additional_files()
        show_result()
    else:
        print_error("打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
