"""
MK850 键盘按键映射配置

这个文件定义了 MK850 (EVision Keyboard) 的按键映射关系。
从 mk850_key_mapping.ini 配置文件加载按键映射。

使用方式：
    from key_mapping import KEY_MAPPING
    
    # 获取按键总数
    total_keys = len(KEY_MAPPING)
    
    # 根据索引获取按键名称
    key_name = KEY_MAPPING[36]  # 'W'
    
    # 根据按键名称获取索引
    key_index = KEY_NAME_TO_INDEX['W']  # 36
"""

import configparser
import os
import sys

# ============================================================================
# 从INI配置文件加载按键映射
# ============================================================================

def load_key_mapping_from_ini():
    """从INI配置文件加载按键映射"""
    config = configparser.ConfigParser()
    
    # 搜索路径优先级：
    # 1. 内部打包路径 (PyInstaller _MEIPASS) - 对应 --add-data 打包进来的文件
    # 2. EXE 同级目录 - 允许用户在外部放置 INI 进行覆盖
    # 3. 脚本同级目录 - 开发环境
    search_paths = []
    if hasattr(sys, '_MEIPASS'):
        search_paths.append(sys._MEIPASS)
    if getattr(sys, 'frozen', False):
        search_paths.append(os.path.dirname(sys.executable))
    search_paths.append(os.path.dirname(os.path.abspath(__file__)))

    ini_path = None
    for path in search_paths:
        target = os.path.join(path, 'mk850_key_mapping.ini')
        if os.path.exists(target):
            ini_path = target
            break
    
    if not os.path.exists(ini_path):
        print(f"⚠️  警告: 配置文件不存在: {ini_path}")
        print("使用默认映射表")
        return None
    
    try:
        config.read(ini_path, encoding='utf-8')
        
        if 'key_mappings' not in config:
            print("⚠️  警告: 配置文件中缺少 [key_mappings] 节")
            return None
        
        # 读取所有按键映射
        mappings = {}
        for key, value in config['key_mappings'].items():
            try:
                index = int(key.strip())
                key_name = value.strip()
                mappings[index] = key_name
            except ValueError:
                print(f"⚠️  跳过无效的配置项: {key} = {value}")
        
        if not mappings:
            print("⚠️  警告: 配置文件中没有有效的按键映射")
            return None
        
        # 按索引排序，生成列表（保留BLANK位置）
        max_index = max(mappings.keys())
        key_list = [None] * (max_index + 1)
        
        for idx, key_name in mappings.items():
            key_list[idx] = key_name
        
        # 统计有效按键数量（排除BLANK和None）
        valid_keys_count = sum(1 for k in key_list if k and k != 'BLANK')
        
        print(f"✅ 从配置文件加载了 {len(key_list)} 个位置（其中 {valid_keys_count} 个有效按键）")
        return key_list
        
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None

# 尝试从INI文件加载，如果失败则使用默认映射
loaded_mapping = load_key_mapping_from_ini()

if loaded_mapping:
    KEY_MAPPING = loaded_mapping
else:
    # 默认映射表（备用）
    KEY_MAPPING = [
        'ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
        'PRTSC', 'SCRLK', 'PAUSE',
        '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BACKSPACE',
        'TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '|',
        'CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'SEMICOLON', 'QUOTE', 'ENTER',
        'SHIFT_L', 'L/', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', 'COMMA', 'PERIOD', 'SLASH', 'RIGHT_SHIFT',
        'CTRL_L', 'WIN_L', 'ALT_L', 'SPACE', 'ALT_R', 'FN', 'MENU', 'CTRL_R',
        'INS', 'HOME', 'PGUP', 'DEL', 'END', 'PGDN',
        'UP', 'LEFT', 'DOWN', 'RIGHT',
        'NUM', 'NUM/', 'NUM*', 'NUM-',
        'NUM7', 'NUM8', 'NUM9', 'NUM+',
        'NUM4', 'NUM5', 'NUM6',
        'NUM1', 'NUM2', 'NUM3', 'NUM_ENT',
        'NUM0', 'NUM.',
    ]

# ============================================================================
# 反向映射：按键名称 -> 索引
# ============================================================================

KEY_NAME_TO_INDEX = {key: idx for idx, key in enumerate(KEY_MAPPING)}

# ============================================================================
# 显示名称映射（用于虚拟键盘界面显示）
# 将内部使用的按键名称转换为更易读的显示名称
# ============================================================================

DISPLAY_NAME_MAP = {
    # 符号键
    'SEMICOLON': ';',
    'QUOTE': "'",
    'COMMA': ',',
    'PERIOD': '.',
    'SLASH': '/',
    'BACKSPACE': 'BACKSPACE',
    '|': '\\',
    
    # 功能键简化名称
    'PRTSC': 'PRTSC',
    'SCRLK': 'SCRLK',
    'PAUSE': 'PAUSE',
    'CAPS': 'CAPS',
    
    # 方向键符号
    'UP': '↑',
    'DOWN': '↓',
    'LEFT': '←',
    'RIGHT': '→',
    
    # 小键盘符号（只显示数字和符号）
    'NUM': 'Num',  # 简化显示
    'NUM/': '/',
    'NUM*': '*',
    'NUM-': '-',
    'NUM+': '+',
    'NUM7': '7',
    'NUM8': '8',
    'NUM9': '9',
    'NUM4': '4',
    'NUM5': '5',
    'NUM6': '6',
    'NUM1': '1',
    'NUM2': '2',
    'NUM3': '3',
    'NUM_ENT': 'ENTER',
    'NUM0': '0',
    'NUM.': '.',
    
    # 修饰键（GUI显示名称 -> 标准简洁显示）
    'SHIFT_L': 'Shift',
    'RIGHT_SHIFT': 'Shift',
    'CTRL_L': 'Ctrl',
    'CTRL_R': 'Ctrl',
    'ALT_L': 'Alt',
    'ALT_R': 'Alt',
    'WIN_L': 'Win',
    'FN': 'Fn',
    'MENU': 'Menu',
    'CAPS': 'Caps',
}

# ============================================================================
# 键盘布局信息（用于GUI渲染）- MK850全尺寸键盘布局
# 分为三个独立区域：主键盘区、右侧功能区、小键盘区
# 标准104键 + MK850特有的L/额外按键 = 105个有效按键
# ============================================================================

# ====== 区域1：主键盘区（左侧） ======
MAIN_KEYBOARD_LAYOUT = [
    # 第1行: 功能键区 (16键)
    [
        ('ESC', 1), 
        ('', 0.5),    # ESC和F1之间的间隔（减少）
        ('F1', 1), ('F2', 1), ('F3', 1), ('F4', 1), 
        ('', 0.5),    # F4和F5之间的间隔（减少）
        ('F5', 1), ('F6', 1), ('F7', 1), ('F8', 1), 
        ('', 0.5),    # F8和F9之间的间隔（减少）
        ('F9', 1), ('F10', 1), ('F11', 1), ('F12', 1)
    ],
    
    # 垂直间隙 (对齐标准键盘)
    [],
    
    # 第2行: 数字行 (14键)
    [
        ('`', 1), ('1', 1), ('2', 1), ('3', 1), ('4', 1), ('5', 1), 
        ('6', 1), ('7', 1), ('8', 1), ('9', 1), ('0', 1), ('-', 1), 
        ('=', 1), ('BACKSPACE', 1.75)
    ],
    
    # 第3行: QWERTY行 (14键)
    [
        ('TAB', 1.5), ('Q', 1), ('W', 1), ('E', 1), ('R', 1), ('T', 1), 
        ('Y', 1), ('U', 1), ('I', 1), ('O', 1), ('P', 1), ('[', 1), 
        (']', 1), ('|', 1.25)
    ],
    
    # 第4行: ASDF行 (13键)
    [
        ('CAPS', 1.75), ('A', 1), ('S', 1), ('D', 1), ('F', 1), ('G', 1), 
        ('H', 1), ('J', 1), ('K', 1), ('L', 1), (';', 1), ("'", 1), 
        ('ENTER', 2.25)
    ],
    
    # 第5行: ZXCV行 + 额外按键 (13键)
    [
        ('SHIFT_L', 1.25), ('L/', 1), ('Z', 1), ('X', 1), ('C', 1), ('V', 1), 
        ('B', 1), ('N', 1), ('M', 1), (',', 1), ('.', 1), ('/', 1), 
        ('RIGHT_SHIFT', 2.75)
    ],
    
    # 第6行: 底行 (8键)
    [
        ('CTRL_L', 1.5), ('WIN_L', 1.25), ('ALT_L', 1.25), 
        ('SPACE', 6.75),  # 恢复空格比例，确保底行右边缘与上方 Shift 行齐平
        ('ALT_R', 1.25), ('FN', 1.25), ('MENU', 1.25), ('CTRL_R', 1.5)
    ]
]

# ====== 区域2：右侧功能区（编辑键 + 方向键） ======
RIGHT_FUNCTION_LAYOUT = [
    # 第0行: 与F键对齐
    [
        ('PRTSC', 1), ('SCRLK', 1), ('PAUSE', 1)
    ],
    [], # 垂直间隙 (20px)
    
    # 第3行: INS/HOME/PGUP (3键)
    [
        ('INS', 1), ('HOME', 1), ('PGUP', 1)
    ],
    
    # 第4行: DEL/END/PGDN (3键)
    [
        ('DEL', 1), ('END', 1), ('PGDN', 1)
    ],
    
    # 垂直占位以对齐ASDF行 (按键高度约为40px，因此使用两个[]确保下移足够距离)
    [],
    [],
    
    # 第6行: UP (1键，在中间)
    [
        ('', 1),    # 左边留白
        ('UP', 1),  # UP在中间上方
        ('', 1)     # 右边留白
    ],
    
    # 第7行: LEFT/DOWN/RIGHT (3键，在同一行)
    [
        ('LEFT', 1), ('DOWN', 1), ('RIGHT', 1)
    ]
]

# ====== 区域3：小键盘区（右侧） ======
NUMPAD_LAYOUT = [
    # 垂直下移占位: 1.625 * 40px = 65px，精确对齐主键区数字行
    [('', 1.625)], 
    
    # Row 2: 与主键盘数字行/INS对齐 (NumLock行)
    [
        ('NUM', 1), ('NUM/', 1), ('NUM*', 1), ('NUM-', 1)
    ],
    
    # Row 3: 与QWERTY行/DEL对齐 (789行)
    [
        ('NUM7', 1), ('NUM8', 1), ('NUM9', 1), ('NUM+', 1)
    ],
    
    # Row 4: 与ASDF行对齐 (456行)
    [
        ('NUM4', 1), ('NUM5', 1), ('NUM6', 1)
    ],
    
    # Row 5: 与ZXCV行对齐 (123行)
    [ 
        ('NUM1', 1), ('NUM2', 1), ('NUM3', 1), ('NUM_ENT', 1)
    ],
    
    # Row 6: 与底座空格行/方向键底行对齐 (0.行)
    [ 
        ('NUM0', 2), ('NUM.', 1)
    ]
]

# ====== 组合布局（保持向后兼容） ======
KEYBOARD_LAYOUT = {
    'main': MAIN_KEYBOARD_LAYOUT,
    'right': RIGHT_FUNCTION_LAYOUT,
    'numpad': NUMPAD_LAYOUT
}

# ============================================================================
# 辅助函数
# ============================================================================

def get_total_keys():
    """获取总按键数"""
    return len(KEY_MAPPING)

def get_key_name(index):
    """根据索引获取按键名称"""
    if 0 <= index < len(KEY_MAPPING):
        return KEY_MAPPING[index]
    return None

def get_key_index(key_name):
    """根据按键名称获取索引"""
    return KEY_NAME_TO_INDEX.get(key_name, -1)

def get_display_name(internal_name):
    """获取显示名称"""
    return DISPLAY_NAME_MAP.get(internal_name, internal_name)

def create_default_colors(default_color=(0, 0, 0)):
    """创建默认颜色数组"""
    return [default_color] * get_total_keys()

def get_valid_key_indices():
    """获取所有有效按键的索引列表（排除BLANK）"""
    valid_indices = []
    for idx, key_name in enumerate(KEY_MAPPING):
        if key_name and key_name != 'BLANK':
            valid_indices.append(idx)
    return valid_indices

def filter_blank_colors(colors):
    """过滤掉BLANK位置的颜色，返回只包含有效按键的颜色数组"""
    if len(colors) != len(KEY_MAPPING):
        print(f"⚠️  警告: 颜色数组长度({len(colors)})与映射表长度({len(KEY_MAPPING)})不匹配")
        return colors
    
    valid_colors = []
    for idx, key_name in enumerate(KEY_MAPPING):
        if key_name and key_name != 'BLANK':
            valid_colors.append(colors[idx])
    
    return valid_colors

def print_mapping_table():
    """打印完整的按键映射表"""
    print("=" * 70)
    print(" MK850 键盘按键映射表")
    print("=" * 70)
    print(f"总按键数: {get_total_keys()}")
    print("=" * 70)
    
    for idx, key_name in enumerate(KEY_MAPPING):
        display_name = get_display_name(key_name)
        print(f"  索引 {idx:3d}: {key_name:15s} (显示: {display_name})")
    
    print("=" * 70)

# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print_mapping_table()
    
    # 测试辅助函数
    print("\n📝 辅助函数测试:")
    print(f"  总按键数: {get_total_keys()}")
    print(f"  W键索引: {get_key_index('W')}")
    print(f"  索引36的按键: {get_key_name(36)}")
    print(f"  SEMICOLON的显示名: {get_display_name('SEMICOLON')}")
    
    # 创建默认颜色数组
    colors = create_default_colors()
    print(f"  默认颜色数组大小: {len(colors)}")
