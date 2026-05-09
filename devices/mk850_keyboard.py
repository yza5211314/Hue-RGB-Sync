"""
MK850 / EVision Keyboard 控制器
VID: 0x0C45, PID: 0x5004
SONiX主控，支持直接RGB控制
"""

import hid
import time
from .base_device import RGBDevice


class MK850Keyboard(RGBDevice):
    """MK850 / EVision Keyboard 控制器"""
    
    VID = 0x0C45
    PID = 0x5004
    
    # 命令常量（来自 OpenRGB 源码）
    COMMAND_BEGIN = 0x01
    COMMAND_END = 0x02
    COMMAND_SET_PARAMETER = 0x06
    COMMAND_WRITE_COLOR_DATA = 0x11
    
    # 模式常量
    MODES = {
        'static': 0x06,           # 静态颜色
        'breathing': 0x05,        # 呼吸
        'spectrum': 0x04,         # 光谱循环
        'color_wave': 0x01,       # 颜色波浪
        'reactive': 0x07,         # 响应式
        'custom': 0x14,           # 自定义
    }
    
    def __init__(self):
        super().__init__("MK850 Keyboard", self.VID, self.PID)
    
    def connect(self):
        """连接键盘"""
        try:
            self.device = hid.device()
            
            # 查找正确的HID接口（用法页 0xFF1C）
            devices = hid.enumerate(self.VID, self.PID)
            
            target_path = None
            for dev in devices:
                # RGB控制接口的特征：用法页 0xFF1C
                if dev['usage_page'] == 0xFF1C:
                    target_path = dev['path']
                    print(f"✅ 找到RGB控制接口")
                    print(f"   用法页: 0x{dev['usage_page']:04X}")
                    print(f"   用法: 0x{dev['usage']:04X}")
                    break
            
            if target_path is None:
                print(f"❌ 未找到RGB控制接口（用法页 0xFF1C）")
                print("尝试使用默认接口...")
                # 回退到默认方式
                self.device.open(self.VID, self.PID)
            else:
                # 使用路径打开特定接口
                self.device.open_path(target_path)
            
            manufacturer = self.device.get_manufacturer_string()
            product = self.device.get_product_string()
            serial = self.device.get_serial_number_string()
            
            print(f"✅ {self.name} 连接成功")
            print(f"   制造商: {manufacturer}")
            print(f"   产品: {product}")
            if serial:
                print(f"   序列号: {serial}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ {self.name} 连接失败: {e}")
            print("提示: 请关闭 OpenRGB 软件，并以管理员权限运行")
            import traceback
            traceback.print_exc()
            self.connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.device:
            self.device.close()
            self.device = None
            self.connected = False
            print(f"🔌 {self.name} 已断开")
    
    def _compute_checksum(self, usb_buf):
        """计算校验和（来自 OpenRGB 源码）"""
        checksum = 0
        for byte_idx in range(0x03, 64):
            checksum += usb_buf[byte_idx]
        
        usb_buf[0x01] = checksum & 0xFF
        usb_buf[0x02] = (checksum >> 8) & 0xFF
    
    def _send_packet(self, usb_buf):
        """发送数据包"""
        self._compute_checksum(usb_buf)
        # EVision键盘直接发送bytes，不需要Report ID
        self.device.write(bytes(usb_buf))
        time.sleep(0.005)  # 短暂延迟确保稳定
    
    def set_color(self, r, g, b, brightness=3, **kwargs):
        """
        设置键盘静态颜色
        
        Args:
            r, g, b: RGB颜色值 (0-255)
            brightness: 亮度 (0-4, 推荐3)
            **kwargs: 其他参数
        
        Returns:
            bool: 是否成功
        """
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            # 构建 SET_PARAMETER 包
            usb_buf = [0x00] * 64
            usb_buf[0x00] = 0x04
            usb_buf[0x03] = self.COMMAND_SET_PARAMETER
            usb_buf[0x04] = 0x08  # 参数大小
            usb_buf[0x05] = 0x00  # PARAM_MODE
            
            # 参数数据: mode, brightness, speed, direction, random, r, g, b
            usb_buf[0x08] = self.MODES['static']  # 模式
            usb_buf[0x09] = brightness             # 亮度
            usb_buf[0x0A] = 0x03                   # 速度
            usb_buf[0x0B] = 0x00                   # 方向
            usb_buf[0x0C] = 0x00                   # 随机标志
            usb_buf[0x0D] = r                      # 红色
            usb_buf[0x0E] = g                      # 绿色
            usb_buf[0x0F] = b                      # 蓝色
            
            self._send_packet(usb_buf)
            return True
            
        except Exception as e:
            print(f"❌ 设置颜色失败: {e}")
            return False
    
    def set_mode(self, mode, brightness=3, speed=3, color=None, **kwargs):
        """
        设置键盘灯效模式
        
        Args:
            mode: 模式名称 ('static', 'breathing', 'spectrum', etc.)
            brightness: 亮度 (0-4)
            speed: 速度 (0-5, 0最快)
            color: RGB元组 (r, g, b)，某些模式需要
            **kwargs: 其他参数
        
        Returns:
            bool: 是否成功
        """
        if not self.connected:
            if not self.connect():
                return False
        
        if mode not in self.MODES:
            print(f"⚠️  不支持的模式: {mode}")
            print(f"   可用模式: {', '.join(self.MODES.keys())}")
            return False
        
        try:
            mode_code = self.MODES[mode]
            
            # 默认颜色
            if color is None:
                r, g, b = 255, 255, 255
            else:
                r, g, b = color
            
            # 构建 SET_PARAMETER 包
            usb_buf = [0x00] * 64
            usb_buf[0x00] = 0x04
            usb_buf[0x03] = self.COMMAND_SET_PARAMETER
            usb_buf[0x04] = 0x08
            usb_buf[0x05] = 0x00
            
            usb_buf[0x08] = mode_code     # 模式
            usb_buf[0x09] = brightness    # 亮度
            usb_buf[0x0A] = speed         # 速度
            usb_buf[0x0B] = 0x00          # 方向
            usb_buf[0x0C] = 0x00          # 随机标志
            usb_buf[0x0D] = r             # 红色
            usb_buf[0x0E] = g             # 绿色
            usb_buf[0x0F] = b             # 蓝色
            
            self._send_packet(usb_buf)
            print(f"🎨 设置模式: {mode}, 亮度:{brightness}, 速度:{speed}")
            return True
            
        except Exception as e:
            print(f"❌ 设置模式失败: {e}")
            return False
    
    def set_custom_colors(self, colors):
        """
        设置自定义颜色（每个键独立颜色）
        
        Args:
            colors: 颜色列表 [(r,g,b), (r,g,b), ...]，最多98个按键
        
        Returns:
            bool: 是否成功
        """
        if not self.connected:
            if not self.connect():
                return False
        
        # 验证按键数量
        num_keys = len(colors)
        if num_keys > 125:
            print(f"⚠️  警告: 按键数量 {num_keys} 超过MK850最大支持数125，将截断")
            colors = colors[:125]
            num_keys = 125
        
        try:
            print(f" 开始设置 {num_keys} 个按键的颜色...")
            
            # 第一步：先设置键盘为custom模式
            print("  步骤1: 设置键盘为custom模式...")
            self._set_custom_mode()
            time.sleep(0.1)
            
            # 第二步：发送开始命令
            print("  步骤2: 发送开始命令...")
            self._send_begin()
            time.sleep(0.05)
            
            # 第三步：发送颜色数据
            print("  步骤3: 发送颜色数据...")
            
            # 将颜色数据转换为扁平列表
            color_data = []
            for r, g, b in colors:
                color_data.extend([r, g, b])
            
            print(f"   颜色数据大小: {len(color_data)} 字节 ({num_keys} 个按键)")
            
            # 分块发送（每包最多 0x36 = 54 字节 = 18个按键）
            max_packet_size = 0x36
            offset = 0
            packet_count = 0
            
            while offset < len(color_data):
                chunk = color_data[offset:offset + max_packet_size]
                chunk_size = len(chunk)
                
                # 构建颜色数据包
                usb_buf = [0x00] * 64
                usb_buf[0x00] = 0x04  # Report ID
                usb_buf[0x03] = self.COMMAND_WRITE_COLOR_DATA  # 命令码 0x11
                usb_buf[0x04] = chunk_size  # 数据长度
                usb_buf[0x05] = offset & 0xFF  # 偏移量低字节
                usb_buf[0x06] = (offset >> 8) & 0xFF  # 偏移量高字节
                
                # 填充颜色数据（从字节8开始）
                for i, value in enumerate(chunk):
                    usb_buf[0x08 + i] = value
                
                # 计算并填充校验和（从字节3到63）
                self._compute_checksum(usb_buf)
                
                # 发送数据包
                self.device.write(bytes(usb_buf))
                
                offset += chunk_size
                packet_count += 1
                time.sleep(0.015)
            
            print(f"   发送了 {packet_count} 个数据包")
            
            # 第四步：发送结束命令
            print("  步骤4: 发送结束命令...")
            self._send_end()
            time.sleep(0.1)
            
            print(f"✅ 设置自定义颜色: {num_keys} 个键")
            return True
            
        except Exception as e:
            print(f"❌ 设置自定义颜色失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _set_custom_mode(self):
        """设置键盘为custom模式，准备接收自定义颜色数据"""
        usb_buf = [0x00] * 64
        usb_buf[0x00] = 0x04  # Report ID
        usb_buf[0x03] = self.COMMAND_SET_PARAMETER  # 0x06
        usb_buf[0x04] = 0x08  # 参数大小
        usb_buf[0x05] = 0x00  # PARAM_MODE
        
        # 参数数据
        usb_buf[0x08] = self.MODES['custom']  # custom模式 0x14
        usb_buf[0x09] = 0x03  # 亮度
        usb_buf[0x0A] = 0x03  # 速度
        usb_buf[0x0B] = 0x00  # 方向
        usb_buf[0x0C] = 0x00  # 随机标志
        usb_buf[0x0D] = 0xFF  # R
        usb_buf[0x0E] = 0xFF  # G
        usb_buf[0x0F] = 0xFF  # B
        
        # 计算校验和
        self._compute_checksum(usb_buf)
        
        self.device.write(bytes(usb_buf))
        time.sleep(0.05)
    
    def _send_begin(self):
        """发送开始命令 - 准备接收自定义颜色数据"""
        usb_buf = [0x00] * 64
        usb_buf[0x00] = 0x04  # Report ID
        usb_buf[0x03] = self.COMMAND_BEGIN  # 命令码 0x01
        usb_buf[0x04] = 0x00  # 参数
        
        # 计算校验和（从字节3到63）
        self._compute_checksum(usb_buf)
        
        self.device.write(bytes(usb_buf))
        time.sleep(0.02)
    
    def _send_end(self):
        """发送结束命令 - 应用颜色数据"""
        usb_buf = [0x00] * 64
        usb_buf[0x00] = 0x04  # Report ID
        usb_buf[0x03] = self.COMMAND_END  # 命令码 0x02
        usb_buf[0x04] = 0x00  # 参数
        
        # 计算校验和
        self._compute_checksum(usb_buf)
        
        self.device.write(bytes(usb_buf))
        time.sleep(0.02)
        print("✅ 颜色数据已应用到键盘")
    
    def get_supported_modes(self):
        """获取支持的模式列表"""
        return list(self.MODES.keys())
    
    def get_info(self):
        """获取设备信息"""
        info = super().get_info()
        info['supported_modes'] = self.get_supported_modes()
        info['type'] = 'keyboard'
        return info
