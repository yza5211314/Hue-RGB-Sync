from key_mapping import KEY_MAPPING, filter_blank_colors

# 创建测试颜色数组
colors = [(i % 256, 0, 0) for i in range(len(KEY_MAPPING))]

print(f"原始长度: {len(colors)}")
print(f"过滤后长度: {len(filter_blank_colors(colors))}")
print(f"BACKSPACE索引: {KEY_MAPPING.index('BACKSPACE')}")
print(f"总按键数: {len(KEY_MAPPING)}")

# 统计BLANK数量
blank_count = sum(1 for k in KEY_MAPPING if k == 'BLANK')
print(f"BLANK数量: {blank_count}")
print(f"有效按键数: {len(KEY_MAPPING) - blank_count}")
