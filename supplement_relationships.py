import json
import time
import openai

# ========== DeepSeek 配置 ==========
DEEPSEEK_API_KEY = "sk-b3a4f4a80d474b81bd673c27f6af92cb"

client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

def generate_relationship_score(a, b):
    """生成两个角色之间的关系评分"""
    prompt = f"""请为《崩坏：星穹铁道》中的「{a}」和「{b}」的关系给出亲密程度评分（0-1之间，1表示最亲密）。

输出格式：{{"score": 0.xx}}
只输出JSON，不要其他内容。"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        result = response.choices[0].message.content.strip()
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            score = data.get("score", 0.3)
            # 确保分数在 0-1 之间
            return max(0.0, min(1.0, score))
        return 0.3
    except Exception as e:
        print(f"  错误: {e}")
        return 0.3

def main():
    print("=" * 50)
    print("开始补充角色关系矩阵")
    print("=" * 50)
    
    # 加载角色列表
    with open("characters_data.json", "r", encoding="utf-8") as f:
        chars = json.load(f)
    all_names = list(chars.keys())
    print(f"角色总数: {len(all_names)}")
    
    # 加载现有关系
    with open("relationships_matrix.json", "r", encoding="utf-8") as f:
        existing_raw = json.load(f)
    
    # 现有关系对（双向）
    existing = set()
    for key in existing_raw.keys():
        a, b = key.split("|")
        existing.add((a, b))
        existing.add((b, a))
    
    # 找出缺失的对（只取 A < B 避免重复）
    missing = []
    for i, a in enumerate(all_names):
        for b in all_names[i+1:]:
            if (a, b) not in existing:
                missing.append((a, b))
    
    print(f"已有关系对: {len(existing)//2} 对")
    print(f"缺失关系对: {len(missing)} 对")
    print()
    
    if not missing:
        print("没有缺失的关系，退出。")
        return
    
    # 补充缺失的关系
    new_relations = {}
    total = len(missing)
    
    for idx, (a, b) in enumerate(missing, 1):
        print(f"[{idx}/{total}] 生成 {a} ↔ {b} ...", end=" ")
        score = generate_relationship_score(a, b)
        new_relations[f"{a}|{b}"] = score
        new_relations[f"{b}|{a}"] = score  # 双向相同
        print(f"得分: {score}")
        time.sleep(0.3)  # 避免请求过快
    
    # 合并并保存
    existing_raw.update(new_relations)
    with open("relationships_matrix.json", "w", encoding="utf-8") as f:
        json.dump(existing_raw, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print(f"✅ 补充完成！新增 {len(new_relations)//2} 对关系")
    print(f"总关系对数: {len(existing_raw)}")
    print("=" * 50)

if __name__ == "__main__":
    main()