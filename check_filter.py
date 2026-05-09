from key_mapping import KEY_MAPPING, filter_blank_colors

# 创建测试颜色数组，每个位置的颜色值等于其索引
colors = [(i, 0, 0) for i in range(len(KEY_MAPPING))]

print(f"原始长度: {len(colors)}")

filtered = filter_blank_colors(colors)
print(f"过滤后长度: {len(filtered)}")

print(f"\n过滤后的前45个索引对应的原始索引:")
idx = 0
for i in range(45):
    key = KEY_MAPPING[i]
    if key != 'BLANK':
        print(f"过滤后索引{idx:3d} <- 原始索引{i:3d} ({key})")
        idx += 1
