"""
屏幕颜色提取器
从屏幕提取主色调
"""

from PIL import ImageGrab
import colorsys
from collections import Counter


class ColorExtractor:
    """屏幕颜色提取器"""
    
    def __init__(self, sample_size=(160, 90), dark_threshold=60, 
                 black_percent_threshold=0.6, saturation_boost=1.4, 
                 brightness_boost=1.2):
        """
        初始化颜色提取器
        
        Args:
            sample_size: 采样分辨率
            dark_threshold: 黑暗阈值
            black_percent_threshold: 黑色占比阈值
            saturation_boost: 饱和度增强倍数
            brightness_boost: 亮度增强倍数
        """
        self.sample_size = sample_size
        self.dark_threshold = dark_threshold
        self.black_percent_threshold = black_percent_threshold
        self.saturation_boost = saturation_boost
        self.brightness_boost = brightness_boost
    
    def get_screen_color(self, method="dominant"):
        """
        获取屏幕颜色
        
        Args:
            method: 提取方法 ("dominant" 或 "vibrant")
        
        Returns:
            tuple: (r, g, b)
        """
        img = ImageGrab.grab()
        
        if method == "vibrant":
            return self.get_vibrant_color(img)
        else:
            return self.get_dominant_color(img)
    
    def get_dominant_color(self, img):
        """获取主导颜色（智能处理黑色场景）"""
        top_colors = self._get_top_colors(img, top_n=3)
        
        if not top_colors:
            return (0, 0, 0)
        
        # 分析黑色占比
        black_percentage = 0
        non_black_colors = []
        
        for color, percentage in top_colors:
            if self._is_black(color):
                black_percentage += percentage
            else:
                non_black_colors.append((color, percentage))
        
        # 如果黑色占比超过阈值，使用黑色
        if black_percentage > self.black_percent_threshold:
            return (0, 0, 0)
        
        # 选择最突出的非黑色
        if non_black_colors:
            selected_color = non_black_colors[0][0]
            return self.enhance_color(selected_color)
        
        return (0, 0, 0)
    
    def get_vibrant_color(self, img):
        """直接提取最鲜艳的颜色"""
        img_resized = img.resize(self.sample_size).convert("RGB")
        pixels = list(img_resized.getdata())
        
        best_color = None
        max_vibrance = 0
        
        for r, g, b in pixels:
            # 跳过黑色像素
            if self._is_black((r, g, b)):
                continue
            
            # 计算鲜艳度
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            vibrance = s * v
            
            if vibrance > max_vibrance:
                max_vibrance = vibrance
                best_color = (r, g, b)
        
        if best_color:
            return self.enhance_color(best_color)
        
        return (0, 0, 0)
    
    def _get_top_colors(self, img, top_n=3):
        """获取前N个主要颜色"""
        img_resized = img.resize(self.sample_size).convert("RGB")
        pixels = list(img_resized.getdata())
        
        # 量化颜色
        quantized_pixels = []
        for r, g, b in pixels:
            r_q = (r // 8) * 8
            g_q = (g // 8) * 8
            b_q = (b // 8) * 8
            quantized_pixels.append((r_q, g_q, b_q))
        
        # 统计频率
        color_counter = Counter(quantized_pixels)
        total_pixels = len(quantized_pixels)
        
        # 获取前N个颜色
        top_colors = []
        for color, count in color_counter.most_common(top_n):
            percentage = count / total_pixels
            top_colors.append((color, percentage))
        
        return top_colors
    
    def _is_black(self, rgb_color):
        """判断是否为黑色"""
        r, g, b = rgb_color
        return r < self.dark_threshold and g < self.dark_threshold and b < self.dark_threshold
    
    def enhance_color(self, rgb_color):
        """增强颜色饱和度和亮度"""
        if rgb_color == (0, 0, 0) or self._is_black(rgb_color):
            return (0, 0, 0)
        
        r, g, b = rgb_color
        r_norm, g_norm, b_norm = r/255, g/255, b/255
        
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        s = min(1.0, s * self.saturation_boost)
        v = min(1.0, v * self.brightness_boost)
        
        r_enh, g_enh, b_enh = colorsys.hsv_to_rgb(h, s, v)
        return (int(r_enh * 255), int(g_enh * 255), int(b_enh * 255))
    
    def color_distance(self, c1, c2):
        """计算两个颜色的距离"""
        return sum(abs(a - b) for a, b in zip(c1, c2))
