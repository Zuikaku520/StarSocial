import json
import time
import openai
FORCE_FULL_GENERATE = False   # 默认 False，增量更新；设为 True 则重新生成全部
# ========== 配置 ==========
DEEPSEEK_API_KEY = "sk-b3a4f4a80d474b81bd673c27f6af92cb"  # 替换成你的

# 新版 OpenAI 客户端初始化
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# 需要生成数据的角色列表
CHARACTER_NAMES = [
    "三月七", "丹恒", "姬子", "景元", "彦卿", 
    "砂金", "托帕", "银狼", "卡芙卡", "刃",
    "花火", "黑塔", "知更鸟", "帕姆", "符玄",
    "黄泉", "波提欧", "乱破", "银枝", "白露",
    "镜流", "阮·梅", "螺丝咕姆", "翡翠", "流萤"
]

def generate_character_profile(character_name):
    """使用 DeepSeek 生成角色详细设定"""
    
    prompt = f"""请提供《崩坏：星穹铁道》中「{character_name}」的详细信息，并整理成以下JSON格式：

{{
    "personality": "角色的性格特点，30字左右，用中文",
    "active_coefficient": "角色在社交媒体上的活跃度，0-1之间的小数，根据性格判断（话痨0.9，高冷0.3等）",
    "interests": ["兴趣关键词1", "兴趣关键词2", "兴趣关键词3", "兴趣关键词4", "兴趣关键词5"],
    "style": "说话风格特点，15字左右，要口语化，例如'活泼，常用语气词和颜文字'或'简洁，偶尔用省略号'",
    "catchphrases": ["日常口头禅1", "日常口头禅2", "日常口头禅3"],
    "relationships": {{
        "关系好的角色": "关系描述",
        "关系一般的角色": "关系描述"
    }}
}}

要求：
1. catchphrases 必须包含3个日常用语，要口语化、接地气，例如“呀！”、“好棒！”、“拍下来拍下来！”等。
2. style 要描述角色说话的口语化特点，如“常用语气词”、“喜欢用短句”、“爱用省略号”等。
3. 确保信息准确，基于游戏实际设定。"""
    
    try:
        # 新版 API 调用方式
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个《崩坏：星穹铁道》的专家。请以JSON格式输出。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        result = response.choices[0].message.content
        # 提取JSON部分
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print(f"解析失败: {result}")
            return None
            
    except Exception as e:
        print(f"生成 {character_name} 失败: {e}")
        return None

def generate_relationship_matrix(character_names):
    """
    为所有角色生成关系矩阵（仅包含有明确关系的对，默认值 0.3）
    返回格式：{(角色A, 角色B): 关系值, ...}
    """
    relationship_dict = {}
    # 默认关系值
    DEFAULT_REL = 0.3

    # 对每个角色，查询与其关系密切的其他角色
    for name in character_names:
        prompt = f"""请列出《崩坏：星穹铁道》中与「{name}」关系最密切的3-5个角色，并为每个关系给出亲密程度评分（0-1之间，1表示最亲密）。输出格式为JSON数组，每个元素包含"character"和"score"，例如：
[
    {{"character": "丹恒", "score": 0.85}},
    {{"character": "姬子", "score": 0.80}}
]
只输出JSON数组，不要其他内容。"""

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            result = response.choices[0].message.content.strip()
            # 提取JSON
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                relations = json.loads(json_match.group())
                for rel in relations:
                    other = rel.get("character")
                    score = rel.get("score", DEFAULT_REL)
                    if other and other in character_names:
                        # 存储双向关系（通常关系是对称的，但可以保留方向）
                        relationship_dict[(name, other)] = score
                        # 如果希望对称，也可以同时添加反向
                        # relationship_dict[(other, name)] = score
            else:
                print(f"  {name} 的关系解析失败: {result}")
        except Exception as e:
            print(f"  {name} 的关系生成失败: {e}")
        
        # 避免请求过快
        time.sleep(0.5)

    return relationship_dict


def generate_relationships_for_one(character_name, all_names):
    """
    为单个角色生成与所有其他角色的关系（分批请求）
    返回格式：{(character_name, other): score}
    """
    relationship_dict = {}
    DEFAULT_REL = 0.3
    
    # 排除自己
    others = [name for name in all_names if name != character_name]
    # 分批，每批最多 8 个角色（避免 token 超限）
    batch_size = 8
    for i in range(0, len(others), batch_size):
        batch = others[i:i+batch_size]
        others_str = "、".join(batch)
        
        prompt = f"""请为《崩坏：星穹铁道》中的「{character_name}」与以下角色的关系给出亲密程度评分（0-1之间，1表示最亲密）：
{others_str}

输出格式为JSON数组，每个元素包含"character"和"score"，例如：
[
    {{"character": "丹恒", "score": 0.85}},
    {{"character": "姬子", "score": 0.80}}
]

如果角色之间没有直接互动或关系不明确，请根据角色设定和阵营给出合理推测，评分可以较低（0.1-0.3）。
只输出JSON数组，不要其他内容。"""

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            result = response.choices[0].message.content.strip()
            import re
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                relations = json.loads(json_match.group())
                for rel in relations:
                    other = rel.get("character")
                    score = rel.get("score", DEFAULT_REL)
                    if other and other in all_names and other != character_name:
                        relationship_dict[(character_name, other)] = score
            else:
                print(f"  {character_name} 与 {batch} 的关系解析失败")
        except Exception as e:
            print(f"  {character_name} 的关系生成失败（批次 {batch}）: {e}")
        
        time.sleep(0.5)  # 避免请求过快
    
    return relationship_dict


def generate_all_characters():
    """生成所有角色的数据（支持增量更新）"""
    
    # ========== 1. 加载已有数据 ==========
    existing_characters = {}
    existing_relationships = {}
    
    try:
        with open("characters_data.json", "r", encoding="utf-8") as f:
            existing_characters = json.load(f)
        print(f"已加载现有角色数据，共 {len(existing_characters)} 个角色")
    except FileNotFoundError:
        print("未找到现有角色数据，将全量生成")
    
    try:
        with open("relationships_matrix.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
            # 转换回元组格式
            existing_relationships = {tuple(k.split("|")): v for k, v in raw.items()}
        print(f"已加载现有关系矩阵，共 {len(existing_relationships)} 对关系")
    except FileNotFoundError:
        print("未找到现有关系矩阵，将全量生成")
    
    # ========== 2. 确定需要生成的角色 ==========
    if FORCE_FULL_GENERATE:
        new_characters = CHARACTER_NAMES
        print("强制全量生成模式")
    else:
        new_characters = [name for name in CHARACTER_NAMES if name not in existing_characters]
        print(f"增量更新模式，新增角色: {new_characters}")
    
    if not new_characters and not FORCE_FULL_GENERATE:
        print("所有角色数据已存在，无需生成。")
        return existing_characters
    
    # ========== 3. 为新增角色生成性格数据 ==========
    for name in new_characters:
        print(f"正在生成 {name} 的数据...")
        profile = generate_character_profile(name)
        if profile:
            existing_characters[name] = profile
            print(f"✅ {name} 生成成功")
        else:
            print(f"❌ {name} 生成失败，使用默认值")
            existing_characters[name] = {
                "personality": "待补充",
                "active_coefficient": 0.5,
                "interests": ["旅行", "冒险"],
                "style": "待补充",
                "catchphrases": [],
                "relationships": {}
            }
        time.sleep(1)
    
    # ========== 4. 保存角色数据 ==========
    with open("characters_data.json", "w", encoding="utf-8") as f:
        json.dump(existing_characters, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 角色数据已保存，共 {len(existing_characters)} 个角色")
    
    # ========== 5. 更新关系矩阵（只针对新增角色） ==========
    if new_characters or FORCE_FULL_GENERATE:
        print("\n正在更新角色关系矩阵...")
        
        if FORCE_FULL_GENERATE:
            # 全量生成：所有角色重新生成关系
            relationships = generate_relationship_matrix(CHARACTER_NAMES)
        else:
            # 增量更新：只生成新增角色与其他所有角色的关系
            relationships = {}
            all_names = list(set(CHARACTER_NAMES))  # 所有角色
            for name in new_characters:
                print(f"  生成 {name} 与所有角色的关系...")
                relations_for_name = generate_relationships_for_one(name, all_names)
                relationships.update(relations_for_name)
                time.sleep(0.5)
        
        # 合并到已有关系矩阵（增量模式时，已有关系保留，新关系覆盖）
        if FORCE_FULL_GENERATE:
            final_relationships = relationships
        else:
            final_relationships = existing_relationships.copy()
            final_relationships.update(relationships)
        
        # 保存关系矩阵
        relationships_jsonable = {f"{a}|{b}": v for (a, b), v in final_relationships.items()}
        with open("relationships_matrix.json", "w", encoding="utf-8") as f:
            json.dump(relationships_jsonable, f, ensure_ascii=False, indent=2)
        print(f"✅ 关系矩阵已保存，共 {len(final_relationships)} 对关系")
    
    return existing_characters



if __name__ == "__main__":
    print("开始生成角色数据（DeepSeek）...\n")
    generate_all_characters()