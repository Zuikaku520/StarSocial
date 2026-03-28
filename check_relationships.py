import json

# 加载现有关系矩阵
with open("relationships_matrix.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

# 获取所有角色列表
with open("characters_data.json", "r", encoding="utf-8") as f:
    chars = json.load(f)
all_names = list(chars.keys())

# 统计已有关系对（双向都算）
existing_pairs = set()
for key in raw.keys():
    a, b = key.split("|")
    existing_pairs.add((a, b))
    existing_pairs.add((b, a))  # 视为双向已有

# 找出缺失的对
missing = []
for i, a in enumerate(all_names):
    for b in all_names[i+1:]:  # 只检查一次
        if (a, b) not in existing_pairs and (b, a) not in existing_pairs:
            missing.append((a, b))

print(f"总角色数: {len(all_names)}")
print(f"已有关系对: {len(existing_pairs)//2} 对（去重后）")
print(f"缺失关系对: {len(missing)} 对")
print("\n前10个缺失对:")
for pair in missing[:10]:
    print(f"  {pair[0]} ↔ {pair[1]}")