"""
RGB灯光同步控制系统 - GUI控制面板
支持MK850键盘和TSG600鼠标的RGB控制
"""

import tkinter as tk
from tkinter import ttk, colorchooser
import threading
import time
import datetime
import traceback

# 从key_mapping模块导入按键映射配置
from key_mapping import (
    DISPLAY_NAME_MAP,
    KEYBOARD_LAYOUT,
    get_total_keys,
    get_key_index,
    get_display_name,
    create_default_colors,
)

# 导入控制器
from rgb_sync_controller import RGBSyncController

# ====== 虚拟键盘布局定义 ======
# 使用从key_mapping导入的KEYBOARD_LAYOUT

class KeyColorMapper:
    """按键颜色映射器包装类"""
    def __init__(self):
        print(f"✅ 已加载 {get_total_keys()} 个按键映射 (MK850键盘)")

    def create_color_array(self, default_color=(0, 0, 0)):
        return create_default_colors(default_color)

    def set_key_color(self, color_array, key_name, color):
        index = get_key_index(key_name)
        if 0 <= index < len(color_array):
            color_array[index] = color
            return True
        return False
    
    def set_all_colors(self, color_array, color):
        """设置所有按键的颜色"""
        for i in range(len(color_array)):
            color_array[i] = color


class VirtualKeyboard:
    """虚拟键盘显示组件 - 使用独立配置文件中的布局
    支持标准104键布局显示，所有按键都支持RGB控制
    """
    
    def __init__(self, parent, on_key_click=None):
        self.parent = parent
        self.on_key_click = on_key_click
        self.key_buttons = {}  # 存储按键按钮引用 {key_name: button}
        self.key_colors = {}   # 存储按键当前颜色 {key_name: color_hex}
        
        self.main_layout = KEYBOARD_LAYOUT['main']
        self.right_layout = KEYBOARD_LAYOUT['right']
        self.numpad_layout = KEYBOARD_LAYOUT['numpad']
        
        # 显示名称到内部名称的映射 (直接使用导入的映射)
        self.display_name_map = DISPLAY_NAME_MAP.copy()
        
        self._create_keyboard()
    
    def _create_keyboard(self):
        """创建键盘UI - 三个区域分开渲染"""
        # 创建主容器
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 创建三个区域的容器
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # 中间间隔 (主键盘与功能区之间)
        middle_frame = ttk.Frame(main_container, width=10)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # 右侧间隔 (功能区与小键盘之间)
        right_gap_frame = ttk.Frame(main_container, width=10)
        right_gap_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        numpad_frame = ttk.Frame(main_container)
        numpad_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # 渲染三个区域（小键盘区使用Grid布局）
        self._render_area(left_frame, self.main_layout)
        self._render_area(right_frame, self.right_layout)
        self._render_numpad_grid(numpad_frame, self.numpad_layout)
    
    def _render_numpad_grid(self, parent_frame, layout):
        """渲染小键盘区 - 使用Grid布局实现精确的跨行控制"""
        BASE_WIDTH = 45  # 基准宽度（像素）- 统一所有区域
        GRID_UNIT = 4    # 每个标准键宽度对应的网格数
        
        # 配置网格列（4列：NUM7/8/9/+, NUM4/5/6/+, 等）
        for col in range(4):
            parent_frame.grid_columnconfigure(col, weight=1, uniform="numpad_col")
        
        # 不配置行的weight，保持固定高度（防止上下拉长）
        
        current_row = 0
        
        for row_idx, row_keys in enumerate(layout):
            # 处理空行
            if not row_keys:
                ttk.Frame(parent_frame, height=20).grid(
                    row=current_row, column=0, columnspan=4, sticky="nsew"
                )
                current_row += 1
                continue
            
            # 处理自定义高度间隔行 (例如 [('', 1.625)] 用于实现 65px 下移)
            if len(row_keys) == 1 and row_keys[0][0] == '':
                _, height_ratio = row_keys[0]
                h = int(height_ratio * 40) # 1.0 比例对应约 40 像素(一个按键行高)
                ttk.Frame(parent_frame, height=h).grid(
                    row=current_row, column=0, columnspan=4, sticky="nsew"
                )
                current_row += 1
                continue
            
            current_col = 0
            
            for key_data in row_keys:
                key_name, width_ratio = key_data
                
                # 处理间隔（空白）
                if key_name == '':
                    if width_ratio > 0:
                        colspan = max(1, int(width_ratio * GRID_UNIT))
                        current_col += colspan
                    continue
                
                # 计算按键占据的列数
                colspan = max(1, int(width_ratio * GRID_UNIT))
                
                # 对于NUM+和NUM_ENT，强制使用标准宽度（1个标准键）
                if key_name in {'NUM+', 'NUM_ENT'}:
                    colspan = GRID_UNIT  # 固定为4个网格单位（标准宽度）
                
                # 判断是否是竖向按键（跨两行）
                is_vertical = key_name in {'NUM+', 'NUM_ENT'}
                rowspan = 2 if is_vertical else 1
                
                # 获取显示名称
                display_name = self.display_name_map.get(key_name, key_name)
                
                # 计算按键宽度（Tkinter的width参数是字符数）
                btn_width = int(BASE_WIDTH * width_ratio / 7)
                btn_height = 4 if is_vertical else 2
                
                # 创建按键按钮
                btn = tk.Button(
                    parent_frame,
                    text=display_name,
                    width=btn_width,
                    height=btn_height,
                    bg='#2b2b2b',
                    fg='white',
                    activebackground='#3b3b3b',
                    activeforeground='white',
                    relief=tk.RAISED,
                    borderwidth=2,
                    font=("Arial", 9),
                    command=lambda k=key_name: self._on_key_pressed(k)
                )
                
                # 使用Grid布局放置按键
                btn.grid(
                    row=current_row,
                    column=current_col,
                    columnspan=colspan,
                    rowspan=rowspan,
                    sticky="nsew",
                    padx=1,
                    pady=1
                )
                
                # 存储按钮引用
                self.key_buttons[key_name] = btn
                self.key_colors[key_name] = '#2b2b2b'
                
                # 移动到下一列
                current_col += colspan
            
            # 移动到下一行
            current_row += 1
        
        # 不设置行的weight，保持固定高度（防止上下拉长）
        # for row in range(current_row):
        #     parent_frame.grid_rowconfigure(row, weight=1)
    
    def _render_area(self, parent_frame, layout):
        """渲染单个区域"""
        BASE_WIDTH = 45  # 基准宽度（像素）- 统一所有区域
        
        # 需要竖向显示的按键列表（跨两行）
        vertical_keys = {'NUM+', 'NUM_ENT'}
        
        for row_idx, row_keys in enumerate(layout):
            # 为每一行创建框架
            row_frame = ttk.Frame(parent_frame)
            row_frame.pack(fill=tk.X, pady=1)
            
            # 处理空行或间隔行
            if not row_keys:
                # 使用ttk.Frame创建空白行，设置固定高度（减小到20px，更紧凑）
                ttk.Frame(row_frame, height=20).pack(fill=tk.X)
                continue
            
            # 处理自定义高度间隔行
            if len(row_keys) == 1 and row_keys[0][0] == '':
                _, height_ratio = row_keys[0]
                h = int(height_ratio * 40)
                ttk.Frame(row_frame, height=h).pack(fill=tk.X)
                continue
            
            current_col = 0
            
            for key_data in row_keys:
                key_name, width_ratio = key_data
                
                # 处理间隔（空白）
                if key_name == '':
                    # 添加空白占位
                    if width_ratio > 0:
                        empty_width = int(BASE_WIDTH * width_ratio)
                        ttk.Label(row_frame, text="", width=max(1, empty_width // 7)).pack(side=tk.LEFT)
                    continue
                
                # 计算按键宽度（Tkinter的width参数是字符数，约7px/字符）
                btn_width = int(BASE_WIDTH * width_ratio / 7)
                
                # 获取显示名称 (处理特殊符号映射)
                display_name = self.display_name_map.get(key_name, key_name)
                
                # 判断是否是竖向按键（跨两行）
                btn_height = 4 if key_name in vertical_keys else 2
                
                # 创建按键按钮
                btn = tk.Button(
                    row_frame,
                    text=display_name,
                    width=btn_width,
                    height=btn_height,
                    bg='#2b2b2b',
                    fg='white',
                    activebackground='#3b3b3b',
                    activeforeground='white',
                    relief=tk.RAISED,
                    borderwidth=2,
                    font=("Arial", 9),
                    command=lambda k=key_name: self._on_key_pressed(k)
                )
                btn.pack(side=tk.LEFT, padx=1)
                
                # 存储按钮引用
                self.key_buttons[key_name] = btn
                self.key_colors[key_name] = '#2b2b2b'

    def _on_key_pressed(self, key_name):
        """按键被点击时的回调"""
        if self.on_key_click:
            self.on_key_click(key_name)
    
    def set_key_color(self, key_name, color_hex):
        """设置指定按键的颜色"""
        # 直接使用按键名称查找
        if key_name in self.key_buttons:
            btn = self.key_buttons[key_name]
            btn.config(bg=color_hex)
            self.key_colors[key_name] = color_hex
    
    def set_all_keys_color(self, color_hex):
        """设置所有按键的颜色"""
        for key_name, btn in self.key_buttons.items():
            btn.config(bg=color_hex)
            self.key_colors[key_name] = color_hex
    
    def reset_keys_color(self):
        """重置所有按键颜色"""
        self.set_all_keys_color('#2b2b2b')


class RGBControlGUI:
    """RGB灯光控制图形界面"""
    
    def __init__(self):
        self.controller = RGBSyncController()
        # 不在这里创建窗口，由_setup_ui创建
        # self.root = tk.Tk()  # 删除这行
        
        # 状态变量
        self.is_running = False
        self.sync_thread = None
        self.current_color = (255, 255, 255)  # 当前选中的颜色
        self.mode_buttons = {}  # 存储模式按钮引用
        
        # 键盘颜色管理
        self.key_mapper = KeyColorMapper()
        self.keyboard_colors = self.key_mapper.create_color_array((0, 0, 0))  # 所有键默认黑色
        
        self._setup_ui()
        self._update_device_list()
    
    def _setup_ui(self):
        """设置UI界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("🎨 RGB灯光同步控制系统")
        self.root.geometry("1260x530")
        
        # 设置最小窗口大小
        self.root.minsize(1260, 530)
        
        # 创建主容器（不使用滚动条，直接pack）
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # === 第一行：横向排列的四个区域 ===
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.X, pady=2)
        
        # --- 1. 设备管理区域 ---
        device_frame = ttk.LabelFrame(top_frame, text=" 设备管理", padding="5")
        device_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=3)
        
        # 设备列表
        list_frame = ttk.Frame(device_frame, width=100)
        list_frame.pack(fill=tk.X)
        
        ttk.Label(list_frame, text="可用设备:", font=("Arial", 9)).pack(anchor=tk.W)
        self.device_listbox = tk.Listbox(list_frame, height=2, font=("Arial", 9))
        self.device_listbox.pack(fill=tk.X, pady=2)
        
        # 设备操作按钮
        btn_frame = ttk.Frame(device_frame)
        btn_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(btn_frame, text=" 扫描", command=self._scan_devices).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="➕ 添加", command=self._add_selected_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=" 移除", command=self._remove_selected_device).pack(side=tk.LEFT, padx=2)
        
        # 已连接设备
        conn_frame = ttk.Frame(device_frame)
        conn_frame.pack(fill=tk.X, pady=(3, 0))
        
        ttk.Label(conn_frame, text="已连接:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.connected_label = ttk.Label(conn_frame, text="无", foreground="gray", font=("Arial", 9))
        self.connected_label.pack(side=tk.LEFT, padx=5)
        
        # --- 2. 🎮 控制中心 (颜色 + 同步 + 模式) ---
        control_center = ttk.LabelFrame(top_frame, text=" 🎮 控制中心", padding="5")
        control_center.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=3)
        
        # (A) 颜色部分
        color_sub = ttk.Frame(control_center)
        color_sub.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        picker_frame = ttk.Frame(color_sub)
        picker_frame.pack(fill=tk.X)
        
        self.color_preview = tk.Canvas(picker_frame, width=60, height=35, bg="#FFFFFF")
        self.color_preview.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(picker_frame, text="🎯", command=self._choose_color).pack(side=tk.LEFT, padx=2)
        
        slider_frame = ttk.Frame(color_sub)
        slider_frame.pack(fill=tk.X, pady=3)
        
        # R滑块
        r_frame = ttk.Frame(slider_frame)
        r_frame.pack(fill=tk.X, pady=1)
        ttk.Label(r_frame, text="R", width=2, font=("Arial", 9)).pack(side=tk.LEFT)
        self.r_var = tk.IntVar(value=255)
        self.r_slider = ttk.Scale(r_frame, from_=0, to=255, variable=self.r_var, 
                                  orient=tk.HORIZONTAL, command=self._on_color_change)
        self.r_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.r_label = ttk.Label(r_frame, text="255", width=3, font=("Arial", 9))
        self.r_label.pack(side=tk.LEFT)
        
        # G滑块
        g_frame = ttk.Frame(slider_frame)
        g_frame.pack(fill=tk.X, pady=1)
        ttk.Label(g_frame, text="G", width=2, font=("Arial", 9)).pack(side=tk.LEFT)
        self.g_var = tk.IntVar(value=255)
        self.g_slider = ttk.Scale(g_frame, from_=0, to=255, variable=self.g_var,
                                  orient=tk.HORIZONTAL, command=self._on_color_change)
        self.g_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.g_label = ttk.Label(g_frame, text="255", width=3, font=("Arial", 9))
        self.g_label.pack(side=tk.LEFT)
        
        # B滑块
        b_frame = ttk.Frame(slider_frame)
        b_frame.pack(fill=tk.X, pady=1)
        ttk.Label(b_frame, text="B", width=2, font=("Arial", 9)).pack(side=tk.LEFT)
        self.b_var = tk.IntVar(value=255)
        self.b_slider = ttk.Scale(b_frame, from_=0, to=255, variable=self.b_var,
                                  orient=tk.HORIZONTAL, command=self._on_color_change)
        self.b_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.b_label = ttk.Label(b_frame, text="255", width=3, font=("Arial", 9))
        self.b_label.pack(side=tk.LEFT)
        
        # 分割线 1
        ttk.Separator(control_center, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # (B) 同步部分
        sync_sub = ttk.Frame(control_center)
        sync_sub.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        apply_frame = ttk.Frame(sync_sub)
        apply_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(apply_frame, text="✅ 应用当前颜色", command=self._apply_color).pack(fill=tk.X)
        
        # 快捷色块
        quick_color_frame = ttk.Frame(sync_sub)
        quick_color_frame.pack(fill=tk.X, pady=2)
        for c in [(255,255,255), (0,0,0), (255,0,0), (0,255,0), (0,0,255)]:
            tk.Button(quick_color_frame, width=2, bg='#%02x%02x%02x'%c, command=lambda color=c: self._set_preset_color(*color)).pack(side=tk.LEFT, padx=1)

        sync_frame = ttk.Frame(sync_sub)
        sync_frame.pack(fill=tk.X, pady=5)
        
        # 同步控制
        sync_ctrl_frame = ttk.Frame(sync_frame)
        sync_ctrl_frame.pack(fill=tk.X)
        
        self.sync_button = ttk.Button(sync_ctrl_frame, text="▶️ 启动", command=self._toggle_sync)
        self.sync_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sync_ctrl_frame, text="间隔:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(5, 2))
        self.interval_var = tk.DoubleVar(value=0.3)
        interval_spinbox = ttk.Spinbox(
            sync_ctrl_frame,
            from_=0.1,
            to=2.0,
            increment=0.1,
            textvariable=self.interval_var,
            width=5,
            font=("Arial", 9)
        )
        interval_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(sync_ctrl_frame, text="秒", font=("Arial", 9)).pack(side=tk.LEFT)
        
        # 当前颜色显示
        color_info_frame = ttk.Frame(sync_frame)
        color_info_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(color_info_frame, text="屏幕:", font=("Arial", 8)).pack(side=tk.LEFT)
        self.screen_color_label = ttk.Label(color_info_frame, text="255,255,255", font=("Arial", 9))
        self.screen_color_label.pack(side=tk.LEFT, padx=3)
        
        self.screen_color_preview = tk.Canvas(color_info_frame, width=60, height=25, bg="#FFFFFF")
        self.screen_color_preview.pack(side=tk.LEFT)
        
        # 分割线 2
        ttk.Separator(control_center, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # (C) 模式部分
        mode_sub = ttk.Frame(control_center)
        mode_sub.pack(side=tk.LEFT, fill=tk.Y, padx=2)
        
        ttk.Label(mode_sub, text="✨ 硬件模式", font=("Arial", 9)).grid(row=0, column=0, columnspan=2, pady=(0,5))
        
        modes = [
            ("🎨 恒亮", "static"), ("🌈 呼吸", "breathing"),
            ("🌊 波浪", "color_wave"), ("🔄 循环", "spectrum"),
            ("⚡ 触发", "reactive"), ("🌙 熄灭", "off")
        ]
        
        for i, (text, mode_id) in enumerate(modes):
            btn = tk.Button(
                mode_sub, text=text, width=5, height=1,
                bg='#333333', fg='white', font=("Arial", 8),
                command=lambda m=mode_id: self._set_lighting_mode(m)
            )
            btn.grid(row=(i // 2) + 1, column=i % 2, padx=1, pady=1, sticky="nsew")
            self.mode_buttons[mode_id] = btn
        
        # --- 3. 日志区域 ---
        log_frame = ttk.LabelFrame(top_frame, text=" 日志", padding="5")
        log_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        
        self.log_text = tk.Text(log_frame, height=4, width=20, font=("Arial", 9), state=tk.DISABLED, bg="#f0f0f0")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # === 第二行：虚拟键盘区域 ===
        keyboard_frame = ttk.LabelFrame(main_container, text="⌨️ 虚拟键盘", padding="5")
        keyboard_frame.pack(fill=tk.X, expand=False, pady=1)
        
        # 创建虚拟键盘
        self.virtual_keyboard = VirtualKeyboard(keyboard_frame, on_key_click=self._on_virtual_key_click)
    
    def _log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def _on_virtual_key_click(self, key_name):
        """虚拟键盘按键被点击"""
        display_name = get_display_name(key_name)
        self._log_message(f"点击按键: {display_name} (内部: {key_name})")
        
        # 获取当前选中的颜色
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        color = (r, g, b)
        
        # 更新颜色数组中该按键的颜色
        success = self.key_mapper.set_key_color(self.keyboard_colors, key_name, color)
        
        if success:
            # 获取键盘设备
            keyboard = self.controller.device_manager.get_device('mk850')
            
            # 如果键盘未连接，尝试连接
            if not keyboard or not keyboard.is_connected():
                self._log_message("⚠️  键盘未连接，正在尝试连接...")
                self._scan_devices()
                keyboard = self.controller.device_manager.get_device('mk850')
            
            if keyboard and keyboard.is_connected():
                try:
                    self._log_message(f" 发送颜色数据到键盘...")
                    # 直接发送完整的颜色数组（包含BLANK位置，键盘驱动会忽略）
                    # 使用set_custom_colors设置所有按键的颜色
                    success = keyboard.set_custom_colors(self.keyboard_colors)
                    if success:
                        self._log_message(f"✅ 按键 {display_name} 设置为 RGB({r}, {g}, {b})")
                        # 更新虚拟键盘显示
                        color_hex = f"#{r:02x}{g:02x}{b:02x}"
                        self.virtual_keyboard.set_key_color(key_name, color_hex)
                    else:
                        self._log_message(f"❌ 键盘设置失败")
                except Exception as e:
                    self._log_message(f"❌ 错误: {e}")
                    self._log_message(f"   {traceback.format_exc()}")
            else:
                self._log_message("❌ 键盘连接失败，请检查:")
                self._log_message("   1. 键盘是否已插入")
                self._log_message("   2. 是否以管理员权限运行")
                self._log_message("   3. OpenRGB是否已关闭")
        else:
            self._log_message(f"⚠️  未知的按键: {key_name}")
    
    def _update_mode_selection_ui(self, active_mode_id):
        """更新模式按钮高亮"""
        for mode_id, btn in self.mode_buttons.items():
            if mode_id == active_mode_id:
                btn.config(bg='cyan', fg='black')
            else:
                btn.config(bg='#333333', fg='white')

    def _set_lighting_mode(self, mode_name):
        """切换硬件灯光模式"""
        if mode_name == "off":
            self._set_preset_color(0, 0, 0)
            mode_name = "static"
            
        self._log_message(f"🔮 尝试切换灯光模式: {mode_name}")
        self._update_mode_selection_ui(mode_name)
        
        def _execute_mode_change():
            keyboard = self.controller.device_manager.get_device('mk850')
            if keyboard and keyboard.is_connected():
                try:
                    # 调用键盘驱动设置模式
                    if hasattr(keyboard, 'set_mode'):
                        # 发送模式切换指令
                        success = keyboard.set_mode(mode_name)
                        
                        if mode_name == "static":
                            # 恒亮模式本质是软件控制，切换后需补发一次当前颜色数据
                            self._apply_color()
                            self._log_message("💡 恒亮模式：已同步当前选中颜色")
                        elif mode_name == "static" and (self.r_var.get() == 0 and self.g_var.get() == 0 and self.b_var.get() == 0): # 如果是熄灭模式
                            # 熄灭模式：强制发送全黑颜色
                            self._set_preset_color(0, 0, 0)
                            self._log_message("🌙 熄灭模式：已关闭所有灯光")
                        else:
                            self._log_message(f"✅ 成功切换至硬件模式: {mode_name}")
                    else:
                        self._log_message(f"⚠️ 驱动程序不支持 set_mode 方法")
                except Exception as e:
                    self._log_message(f"❌ 模式切换失败: {e}")
            else:
                self._log_message("⚠️ 键盘未连接，无法切换模式")

        # 如果当前正在运行取色同步，必须先停止
        if self.is_running:
            self._stop_sync()
            self._log_message("ℹ️ 正在停止同步并释放接口...")
            # 延迟150ms执行，确保HID通信线程已安全退出
            self.root.after(150, _execute_mode_change)
        else:
            _execute_mode_change()

    def _set_preset_color(self, r, g, b):
        """设置预设颜色"""
        self.r_var.set(r)
        self.g_var.set(g)
        self.b_var.set(b)
        self._on_color_change(None)
        
        # 更新所有按键颜色
        color = (r, g, b)
        self.key_mapper.set_all_colors(self.keyboard_colors, color)
        
        # 应用到实体键盘
        keyboard = self.controller.device_manager.get_device('mk850')
        if keyboard and keyboard.is_connected():
            try:
                # 直接发送完整的颜色数组（包含BLANK位置）
                keyboard.set_custom_colors(self.keyboard_colors)
                color_hex = f"#{r:02x}{g:02x}{b:02x}"
                self.virtual_keyboard.set_all_keys_color(color_hex)
                self._log_message(f"✅ 预设颜色: RGB({r}, {g}, {b})")
            except Exception as e:
                self._log_message(f"❌ 设置失败: {e}")
        else:
            self._log_message("⚠️  键盘未连接")
    
    def _update_device_list(self):
        """更新设备列表显示"""
        self.device_listbox.delete(0, tk.END)
        
        available = self.controller.device_manager.list_available_devices()
        for device_type in available:
            self.device_listbox.insert(tk.END, device_type)
        
        # 更新已连接设备显示
        connected_devices = []
        for device_id, device in self.controller.device_manager.get_all_devices().items():
            if device.is_connected():
                connected_devices.append(f"✓ {device_id}: {device.name}")
        
        if connected_devices:
            self.connected_label.config(text="\n".join(connected_devices), foreground="green")
        else:
            self.connected_label.config(text="无", foreground="gray")
    
    def _scan_devices(self):
        """扫描设备"""
        self._log_message("正在扫描设备...")
        results = self.controller.device_manager.scan_and_auto_connect()
        
        for device_id, status in results.items():
            if status:
                self._log_message(f"✅ {device_id} 连接成功")
            else:
                self._log_message(f"❌ {device_id} 连接失败")
        
        self._update_device_list()
    
    def _add_selected_device(self):
        """添加选中的设备"""
        selection = self.device_listbox.curselection()
        if not selection:
            self._log_message("⚠️  请先选择设备")
            return
        
        device_type = self.device_listbox.get(selection[0])
        success = self.controller.add_device(device_type)
        
        if success:
            self._log_message(f"✅ 已添加设备: {device_type}")
        else:
            self._log_message(f"❌ 添加设备失败: {device_type}")
        
        self._update_device_list()
    
    def _remove_selected_device(self):
        """移除选中的设备"""
        # TODO: 实现移除设备功能
        self._log_message("⚠️  移除功能开发中")
    
    def _choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(title="选择颜色")
        if color[0]:
            r, g, b = map(int, color[0])
            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)
            self._on_color_change(None)
    
    def _on_color_change(self, event):
        """颜色改变回调"""
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        
        # 更新标签
        self.r_label.config(text=str(r))
        self.g_label.config(text=str(g))
        self.b_label.config(text=str(b))
        
        # 更新颜色预览
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        self.color_preview.config(bg=color_hex)
        
        self.current_color = (r, g, b)
    
    def _apply_color(self):
        """应用颜色到所有设备"""
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        color = (r, g, b)
        
        self._log_message(f"应用颜色: RGB({r}, {g}, {b})")
        
        # 设置所有键盘按键为统一颜色
        self.key_mapper.set_all_colors(self.keyboard_colors, color)
        
        # 应用到实体键盘
        keyboard = self.controller.device_manager.get_device('mk850')
        if keyboard and keyboard.is_connected():
            try:
                success = keyboard.set_custom_colors(self.keyboard_colors)
                if success:
                    self._log_message(f"✅ 键盘所有按键设置成功")
                    # 更新虚拟键盘显示
                    color_hex = f"#{r:02x}{g:02x}{b:02x}"
                    self.virtual_keyboard.set_all_keys_color(color_hex)
                else:
                    self._log_message(f"❌ 键盘设置失败")
            except Exception as e:
                self._log_message(f"❌ 错误: {e}")
        else:
            self._log_message("⚠️  键盘未连接")
        
        # 应用到其他设备（鼠标等）
        results = self.controller.sync_color(r, g, b)
        
        for device_id, success in results.items():
            if device_id != 'mk850':  # 键盘已经单独处理了
                if success:
                    self._log_message(f"✅ {device_id} 设置成功")
                else:
                    self._log_message(f"❌ {device_id} 设置失败")
    
    def _toggle_sync(self):
        """切换同步状态"""
        if self.is_running:
            self._stop_sync()
        else:
            self._start_sync()
    
    def _start_sync(self):
        """启动同步"""
        self.is_running = True
        self.sync_button.config(text="⏹️ 停止同步")
        
        # 更新更新间隔
        self.controller.update_interval = self.interval_var.get()
        
        self._log_message("▶️  启动屏幕取色同步")
        
        # 在后台线程中运行
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
    
    def _stop_sync(self):
        """停止同步"""
        self.is_running = False
        self.sync_button.config(text="▶️ 启动同步")
        self._log_message("⏹️  停止屏幕取色同步")
    
    def _sync_loop(self):
        """同步循环"""
        while self.is_running:
            try:
                # 获取屏幕颜色
                current_color = self.controller.get_screen_color()
                
                # 判断是否需要更新
                if self.controller.should_update_color(current_color):
                    r, g, b = current_color
                    color = (r, g, b)
                    
                    # 更新键盘所有按键为屏幕颜色
                    self.key_mapper.set_all_colors(self.keyboard_colors, color)
                    
                    # 应用到实体键盘
                    keyboard = self.controller.device_manager.get_device('mk850')
                    if keyboard and keyboard.is_connected():
                        try:
                            keyboard.set_custom_colors(self.keyboard_colors)
                        except Exception as e:
                            self._log_message(f"❌ 键盘同步错误: {e}")
                    
                    # 应用到其他设备（鼠标等）
                    self.controller.sync_color(r, g, b)
                    self.controller.last_color = current_color
                    
                    # 更新UI（使用after在主线程中更新）
                    self.root.after(0, self._update_screen_color_display, r, g, b)

                time.sleep(self.controller.update_interval)
            
            except Exception as e:
                self._log_message(f"❌ 同步错误: {e}")
                break
    
    def _update_screen_color_display(self, r, g, b):
        """更新屏幕颜色显示"""
        color_hex = f"#{r:02x}{g:02x}{b:02x}"
        self.screen_color_label.config(text=f"RGB({r}, {g}, {b})")
        self.screen_color_preview.config(bg=color_hex)
    
    def run(self):
        """运行GUI"""
        self._log_message("GUI已启动")
        
        # 自动扫描并连接设备
        self._log_message("正在自动扫描设备...")
        self._scan_devices()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """关闭窗口时的处理"""
        if self.is_running:
            self._stop_sync()
        
        self.controller.stop()
        self._log_message("程序已退出")
        self.root.destroy()


if __name__ == "__main__":
    app = RGBControlGUI()
    app.run()
