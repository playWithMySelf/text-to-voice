"""
GUI样式定义
基于ui-ux-pro-max设计系统 - Flat Design风格
"""

# 颜色方案 - 深色音频主题 + 暖色强调
COLORS = {
    # 主色调
    'primary': '#1E1B4B',           # 深靛蓝
    'primary_light': '#312E81',     # 浅靛蓝
    'accent': '#F97316',            # 橙色强调
    'accent_hover': '#EA580C',      # 深橙色
    
    # 背景色
    'bg_primary': '#0F0F23',        # 深色主背景
    'bg_secondary': '#1A1A2E',      # 次背景
    'bg_card': '#16162A',           # 卡片背景
    'bg_input': '#252542',          # 输入框背景
    
    # 文字色
    'text_primary': '#F8FAFC',      # 主文字（白）
    'text_secondary': '#94A3B8',    # 次文字（灰）
    'text_muted': '#64748B',        # 辅助文字
    'text_accent': '#F97316',       # 强调文字
    
    # 边框色
    'border': '#2D2D4A',            # 边框
    'border_focus': '#F97316',      # 聚焦边框
    
    # 状态色
    'success': '#10B981',           # 成功
    'warning': '#F59E0B',           # 警告
    'error': '#EF4444',             # 错误
    'info': '#3B82F6',              # 信息
    
    # 按钮色
    'btn_primary_bg': '#F97316',
    'btn_primary_hover': '#EA580C',
    'btn_secondary_bg': '#312E81',
    'btn_secondary_hover': '#1E1B4B',
}

# 字体配置
FONTS = {
    'family': 'Microsoft YaHei UI',
    'family_fallback': ['Segoe UI', 'Arial', 'Helvetica'],
    'size_small': 9,
    'size_normal': 10,
    'size_medium': 11,
    'size_large': 12,
    'size_xlarge': 14,
    'size_title': 18,
}

# 间距配置
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 20,
    'xxl': 24,
}

# 尺寸配置
DIMENSIONS = {
    'window_width': 850,
    'window_height': 600,
    'input_height': 32,
    'button_height': 36,
    'progress_height': 6,
}


def get_button_style(primary: bool = True) -> dict:
    """获取按钮样式配置"""
    if primary:
        return {
            'bg': COLORS['btn_primary_bg'],
            'fg': COLORS['text_primary'],
            'activebackground': COLORS['btn_primary_hover'],
            'activeforeground': COLORS['text_primary'],
            'disabledforeground': COLORS['text_muted'],
            'relief': 'flat',
            'cursor': 'hand2',
            'font': (FONTS['family'], FONTS['size_normal'], 'bold'),
            'padx': SPACING['lg'],
            'pady': SPACING['sm'],
            'borderwidth': 0,
        }
    else:
        return {
            'bg': COLORS['btn_secondary_bg'],
            'fg': COLORS['text_primary'],
            'activebackground': COLORS['btn_secondary_hover'],
            'activeforeground': COLORS['text_primary'],
            'disabledforeground': COLORS['text_muted'],
            'relief': 'flat',
            'cursor': 'hand2',
            'font': (FONTS['family'], FONTS['size_normal']),
            'padx': SPACING['lg'],
            'pady': SPACING['sm'],
            'borderwidth': 0,
        }


def get_input_style() -> dict:
    """获取输入框样式配置"""
    return {
        'bg': COLORS['bg_input'],
        'fg': COLORS['text_primary'],
        'insertbackground': COLORS['accent'],
        'selectbackground': COLORS['accent'],
        'selectforeground': COLORS['text_primary'],
        'relief': 'flat',
        'highlightthickness': 1,
        'highlightcolor': COLORS['border_focus'],
        'highlightbackground': COLORS['border'],
        'font': (FONTS['family'], FONTS['size_normal']),
    }


def get_label_style(is_title: bool = False, is_secondary: bool = False) -> dict:
    """获取标签样式配置"""
    if is_title:
        return {
            'bg': COLORS['bg_primary'],
            'fg': COLORS['text_primary'],
            'font': (FONTS['family'], FONTS['size_title'], 'bold'),
        }
    elif is_secondary:
        return {
            'bg': COLORS['bg_primary'],
            'fg': COLORS['text_secondary'],
            'font': (FONTS['family'], FONTS['size_small']),
        }
    else:
        return {
            'bg': COLORS['bg_primary'],
            'fg': COLORS['text_primary'],
            'font': (FONTS['family'], FONTS['size_normal']),
        }


def get_card_style() -> dict:
    """获取卡片样式"""
    return {
        'bg': COLORS['bg_card'],
        'relief': 'flat',
        'highlightthickness': 1,
        'highlightbackground': COLORS['border'],
        'padx': SPACING['md'],
        'pady': SPACING['md'],
    }


def apply_modern_style(root) -> None:
    """应用现代样式到根窗口"""
    root.configure(bg=COLORS['bg_primary'])
    
    import tkinter.ttk as ttk
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置Notebook样式
    style.configure(
        'Modern.TNotebook',
        background=COLORS['bg_primary'],
        tabmargins=[0, 0, 0, 0],
    )
    style.configure(
        'Modern.TNotebook.Tab',
        font=(FONTS['family'], FONTS['size_normal']),
        padding=[SPACING['lg'], SPACING['sm']],
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_secondary'],
    )
    style.map(
        'Modern.TNotebook.Tab',
        background=[('selected', COLORS['accent'])],
        foreground=[('selected', COLORS['text_primary'])],
        expand=[('selected', [0, 0, 0, 0])],
    )
    
    # 配置Progressbar样式
    style.configure(
        'Modern.Horizontal.TProgressbar',
        background=COLORS['accent'],
        troughcolor=COLORS['bg_secondary'],
        borderwidth=0,
        thickness=DIMENSIONS['progress_height'],
    )
    
    # 配置Combobox样式
    style.configure(
        'Modern.TCombobox',
        fieldbackground=COLORS['bg_input'],
        background=COLORS['bg_secondary'],
        foreground=COLORS['text_primary'],
        arrowcolor=COLORS['accent'],
    )
