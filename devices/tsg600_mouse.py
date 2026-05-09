"""
TSG600 鼠标控制器
VID: 0x2c25, PID: 0xa001
支持9种预设颜色模式
"""

import hid
import time
from .base_device import RGBDevice


class TSG600Mouse(RGBDevice):
    """TSG600 游戏鼠标控制器"""
    
    VID = 0x2c25
    PID = 0xa001
    
    # 颜色报文字典（来自原始代码）
    COLOR_REPORTS = {
        "red":      bytes.fromhex("09aa04ae0aff0100f455" + "00"*(64-10)),
        "green":    bytes.fromhex("09aa04ae0a00ff01f455" + "00"*(64-10)),
        "blue":     bytes.fromhex("09aa04ae0a0100fff455" + "00"*(64-10)),
        "yellow":   bytes.fromhex("09aa04ae0afffe000b55" + "00"*(64-10)),
        "cyan":     bytes.fromhex("09aa04ae0a00fffe0b55" + "00"*(64-10)),
        "purple":   bytes.fromhex("09aa04ae0a9300ff6655" + "00"*(64-11)),
        "magenta":  bytes.fromhex("09aa04ae0aff00fd0855" + "00"*(64-10)),
        "white":    bytes.fromhex("09aa04ae0afffffff555" + "00"*(64-11)),
        "black":    bytes.fromhex("07aa02ac62006655" + "00"*(64-10)),
        "lu100":    bytes.fromhex("07aa02ac62640255" + "00"*(64-10)),  # 亮度100
    }
    
    # RGB到颜色名称的映射
    RGB_TO_COLOR = {
        (255, 1, 0): "red",
        (0, 255, 1): "green",
        (1, 0, 255): "blue",
        (255, 254, 0): "yellow",
        (0, 255, 254): "cyan",
        (147, 0, 255): "purple",
        (255, 0, 253): "magenta",
        (255, 255, 255): "white",
        (0, 0, 0): "black",
    }
    
    def __init__(self):
        super().__init__("TSG600 Mouse", self.VID, self.PID)
        self.old_color = "black"
    
    def connect(self):
        """连接鼠标"""
        try:
            self.device = hid.device()
            self.device.open(self.VID, self.PID)
            
            manufacturer = self.device.get_manufacturer_string()
            product = self.device.get_product_string()
            
            print(f"✅ {self.name} 连接成功")
            print(f"   制造商: {manufacturer}")
            print(f"   产品: {product}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"❌ {self.name} 连接失败: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.device:
            self.device.close()
            self.device = None
            self.connected = False
            print(f"🔌 {self.name} 已断开")
    
    def _find_closest_color(self, target_rgb):
        """找到最接近的预设颜色"""
        if target_rgb == (0, 0, 0):
            return "black"
        
        min_distance = float('inf')
        closest_color = "white"
        
        for rgb, color_name in self.RGB_TO_COLOR.items():
            if color_name == "black":
                continue
            
            distance = sum((t - s) ** 2 for t, s in zip(target_rgb, rgb))
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color_name
        
        return closest_color
    
    def set_color(self, r, g, b, **kwargs):
        """
        设置鼠标颜色（自动匹配最近的预设颜色）
        
        Args:
            r, g, b: RGB颜色值
            **kwargs: 其他参数（忽略）
        
        Returns:
            bool: 是否成功
        """
        if not self.connected:
            if not self.connect():
                return False
        
        target_rgb = (r, g, b)
        color_name = self._find_closest_color(target_rgb)
        
        return self._send_color_report(color_name)
    
    def set_mode(self, mode, **kwargs):
        """
        设置鼠标灯效模式
        
        Args:
            mode: 模式名称 ("static", "breathing", "spectrum", etc.)
            **kwargs: 模式参数
        
        Returns:
            bool: 是否成功
        """
        # TSG600只支持静态颜色，不支持动态模式
        if mode == "static" and 'color' in kwargs:
            r, g, b = kwargs['color']
            return self.set_color(r, g, b)
        
        print(f"⚠️  {self.name} 不支持模式: {mode}")
        return False
    
    def _send_color_report(self, color_name):
        """发送颜色报文"""
        if color_name not in self.COLOR_REPORTS:
            print(f"❌ 未知颜色: {color_name}")
            return False
        
        try:
            # 从黑色切换到其他颜色需要特殊处理
            if self.old_color == "black" and color_name != "black":
                # 先发送目标颜色
                pkt_current = self.COLOR_REPORTS[color_name]
                self.device.write([0x00] + list(pkt_current))
                
                # 再发送亮度100
                pkt_lu100 = self.COLOR_REPORTS.get("lu100")
                if pkt_lu100:
                    self.device.write([0x00] + list(pkt_lu100))
                
                self.old_color = "lu100"
            else:
                # 直接发送颜色
                pkt = self.COLOR_REPORTS[color_name]
                self.device.write([0x00] + list(pkt))
                self.old_color = color_name
            
            return True
            
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            return False
    
    def get_supported_colors(self):
        """获取支持的颜色列表"""
        return list(self.RGB_TO_COLOR.values())
    
    def get_info(self):
        """获取设备信息"""
        info = super().get_info()
        info['supported_colors'] = self.get_supported_colors()
        info['type'] = 'mouse'
        return info
