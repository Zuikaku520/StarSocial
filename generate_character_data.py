import json
import openai

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
    "花火", "黑塔", "知更鸟", "帕姆", "符玄"
]

def generate_character_profile(character_name):
    """使用 DeepSeek 生成角色详细设定"""
    
    prompt = f"""请提供《崩坏：星穹铁道》中「{character_name}」的详细信息，并整理成以下JSON格式：

{{
    "personality": "角色的性格特点，30字左右，用中文",
    "active_coefficient": "角色在社交媒体上的活跃度，0-1之间的小数，根据性格判断（话痨0.9，高冷0.3等）",
    "interests": ["兴趣关键词1", "兴趣关键词2", "兴趣关键词3", "兴趣关键词4", "兴趣关键词5"],
    "style": "说话风格特点，15字左右",
    "catchphrases": ["口头禅1", "口头禅2"],
    "relationships": {{
        "关系好的角色": "关系描述",
        "关系一般的角色": "关系描述"
    }}
}}

请确保信息准确，基于游戏实际设定。"""
    
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

def generate_all_characters():
    """生成所有角色的数据"""
    characters_data = {}
    
    for name in CHARACTER_NAMES:
        print(f"正在生成 {name} 的数据...")
        profile = generate_character_profile(name)
        if profile:
            characters_data[name] = profile
            print(f"✅ {name} 生成成功")
        else:
            print(f"❌ {name} 生成失败，使用默认值")
            characters_data[name] = {
                "personality": "待补充",
                "active_coefficient": 0.5,
                "interests": ["旅行", "冒险"],
                "style": "待补充",
                "catchphrases": [],
                "relationships": {}
            }
        
        import time
        time.sleep(1)
    
    with open("characters_data.json", "w", encoding="utf-8") as f:
        json.dump(characters_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！已生成 {len(characters_data)} 个角色的数据，保存到 characters_data.json")
    return characters_data

if __name__ == "__main__":
    print("开始生成角色数据（DeepSeek）...\n")
    generate_all_characters()