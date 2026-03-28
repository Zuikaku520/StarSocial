import json
import random
import openai
from datetime import datetime
import sys
import io
import os

# 强制设置编码
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ========== DeepSeek 配置 ==========
DEEPSEEK_API_KEY = "sk-b3a4f4a80d474b81bd673c27f6af92cb"  # 替换

client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)
# 测试 API 是否正常
# try:
#     test_response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=[{"role": "user", "content": "你好"}],
#         max_tokens=10
#     )
#     print("✅ API 测试成功:", test_response.choices[0].message.content)
# except Exception as e:
#     print(f"❌ API 测试失败: {e}")
#     exit()


# 加载角色数据
with open("characters_data.json", "r", encoding="utf-8") as f:
    GENERATED_CHARACTERS = json.load(f)

# 构建 CHARACTERS 字典
CHARACTERS = {}
for name, data in GENERATED_CHARACTERS.items():
    CHARACTERS[name] = {
        "personality": data.get("personality", "未知"),
        "active_coefficient": data.get("active_coefficient", 0.5),
        "interests": data.get("interests", []),
        "style": data.get("style", ""),
        "catchphrases": data.get("catchphrases", [])
    }

ALL_CHARACTERS = list(CHARACTERS.keys())
print(f"已加载 {len(ALL_CHARACTERS)} 个角色")

# ========== 阵营和地点数据 ==========
FACTIONS = {
    # 星穹列车
    "三月七": "星穹列车",
    "丹恒": "星穹列车",
    "姬子": "星穹列车",
    "瓦尔特·杨": "星穹列车",
    "帕姆": "星穹列车",
    # 仙舟罗浮
    "景元": "仙舟罗浮",
    "彦卿": "仙舟罗浮",
    "符玄": "仙舟罗浮",
    "白露": "仙舟罗浮",
    "停云": "仙舟罗浮",
    "驭空": "仙舟罗浮",
    "素裳": "仙舟罗浮",
    "罗刹": "仙舟罗浮",
    "桂乃芬": "仙舟罗浮",
    "寒鸦": "仙舟罗浮",
    "雪衣": "仙舟罗浮",
    "藿藿": "仙舟罗浮",
    "银枝": "仙舟罗浮",
    "镜流": "仙舟罗浮",
    "饮月君": "仙舟罗浮",
    # 星核猎手
    "卡芙卡": "星核猎手",
    "银狼": "星核猎手",
    "刃": "星核猎手",
    # 星际和平公司
    "砂金": "星际和平公司",
    "托帕": "星际和平公司",
    "真理医生": "星际和平公司",
    # 匹诺康尼
    "知更鸟": "匹诺康尼",
    "星期日": "匹诺康尼",
    "花火": "匹诺康尼",
    "黑天鹅": "匹诺康尼",
    "黄泉": "匹诺康尼",
    "流萤": "匹诺康尼",
    "波提欧": "匹诺康尼",
    "米沙": "匹诺康尼",
    "加拉赫": "匹诺康尼",
    # 贝洛伯格
    "希儿": "贝洛伯格",
    "布洛妮娅": "贝洛伯格",
    "杰帕德": "贝洛伯格",
    "克拉拉": "贝洛伯格",
    "希露瓦": "贝洛伯格",
    "桑博": "贝洛伯格",
    "娜塔莎": "贝洛伯格",
    "佩拉": "贝洛伯格",
    "卢卡": "贝洛伯格",
    "玲可": "贝洛伯格",
    "虎克": "贝洛伯格",
    "青雀": "贝洛伯格",
    # 黑塔空间站
    "黑塔": "黑塔空间站",
    "艾丝妲": "黑塔空间站",
    "阿兰": "黑塔空间站",
}

LOCATIONS_BY_FACTION = {
    "星穹列车": [
        "星穹列车 · 观景车厢",
        "星穹列车 · 客房车厢",
        "星穹列车 · 智库",
        "星穹列车 · 机库"
    ],
    "仙舟罗浮": [
        "仙舟罗浮 · 长乐天",
        "仙舟罗浮 · 工造司",
        "仙舟罗浮 · 太卜司",
        "仙舟罗浮 · 丹鼎司",
        "仙舟罗浮 · 鳞渊境",
        "仙舟罗浮 · 绥园",
        "仙舟罗浮 · 金人巷",
        "仙舟罗浮 · 星槎海中枢",
        "仙舟罗浮 · 流云渡"
    ],
    "星核猎手": [
        "星核猎手 · 基地",
        "未知星域 · 星核猎手据点"
    ],
    "星际和平公司": [
        "星际和平公司 · 总部",
        "星际和平公司 · 分部"
    ],
    "匹诺康尼": [
        "匹诺康尼 · 白日梦酒店",
        "匹诺康尼 · 苏乐达",
        "匹诺康尼 · 朝露公馆",
        "匹诺康尼 · 克劳克影视乐园",
        "匹诺康尼 · 晖长石号",
        "匹诺康尼 · 黄金的时刻",
        "匹诺康尼 · 稚子的梦"
    ],
    "贝洛伯格": [
        "贝洛伯格 · 行政区",
        "贝洛伯格 · 磐岩镇",
        "贝洛伯格 · 大矿区",
        "贝洛伯格 · 永冬岭",
        "贝洛伯格 · 搏击俱乐部"
    ],
    "黑塔空间站": [
        "黑塔空间站 · 主控舱段",
        "黑塔空间站 · 基座舱段",
        "黑塔空间站 · 收容舱段",
        "黑塔空间站 · 支援舱段"
    ]
}

# ========== 关系矩阵 ==========
RELATIONSHIPS = {
    ("三月七", "丹恒"): 0.85,
    ("丹恒", "三月七"): 0.70,
    ("三月七", "姬子"): 0.80,
    ("景元", "彦卿"): 0.90,
    ("彦卿", "景元"): 0.95,
    ("砂金", "托帕"): 0.65,
    ("托帕", "砂金"): 0.60,
    ("银狼", "卡芙卡"): 0.80,
    ("花火", "任何人"): 0.30,
}
DEFAULT_RELATION = 0.3

def get_relationship(a, b):
    if a == b:
        return 1.0
    key = (a, b)
    return RELATIONSHIPS.get(key, DEFAULT_RELATION)

def relevance_score(character, text):
    interests = CHARACTERS[character].get("interests", [])
    if not interests:
        return 0.5
    text_lower = text.lower()
    matches = sum(1 for interest in interests if interest.lower() in text_lower)
    score = min(matches / 3.0, 1.0)
    return score

def will_interact(character, post_content, interaction_type="like"):
    base_prob = CHARACTERS[character]["active_coefficient"]
    relevance = relevance_score(character, post_content)
    adjusted_prob = base_prob * (0.5 + 0.5 * relevance)
    final_prob = min(adjusted_prob * random.uniform(0.8, 1.2), 1.0)
    return random.random() < final_prob

def maybe_reply(comment_author, comment_text, post_content, replier):
    if replier == comment_author:
        return False
    relation = get_relationship(replier, comment_author)
    if relation < 0.1:
        return False
    base_prob = CHARACTERS[replier]["active_coefficient"] * 0.9
    combined = (comment_text or "") + " " + (post_content or "")
    relevance = relevance_score(replier, combined)
    if relevance < 0.1:
        final_prob = base_prob * relation * 0.4
    else:
        final_prob = base_prob * relation * (0.7 + 0.3 * relevance)
    final_prob = min(final_prob, 0.85)
    return random.random() < final_prob

def generate_comment(character, post_content, context="", post_info=None):
    """AI 生成评论，完全基于角色设定、关系、文案内容、地点情况，无模板"""
    try:
        char_data = CHARACTERS.get(character, {})
        is_reply = "正在回复" in context
        
        # 安全获取字段（确保字符串格式正确）
        personality = str(char_data.get('personality', '未知')).encode('utf-8', errors='ignore').decode('utf-8')
        style = str(char_data.get('style', '自然')).encode('utf-8', errors='ignore').decode('utf-8')
        interests_list = char_data.get('interests', [])
        if not isinstance(interests_list, list):
            interests_list = []
        interests = ', '.join([str(i).encode('utf-8', errors='ignore').decode('utf-8') for i in interests_list])
        catchphrases_list = char_data.get('catchphrases', [])
        if not isinstance(catchphrases_list, list):
            catchphrases_list = []
        catchphrases = ', '.join([str(c).encode('utf-8', errors='ignore').decode('utf-8') for c in catchphrases_list])
        
        # 构建场景描述（包含地点信息）
        scene_parts = []
        if post_info:
            author = str(post_info.get("author", "未知")).encode('utf-8', errors='ignore').decode('utf-8')
            location = str(post_info.get("location", "某处")).encode('utf-8', errors='ignore').decode('utf-8')
            time_str = str(post_info.get("time", "某个时间")).encode('utf-8', errors='ignore').decode('utf-8')
            scene_parts.append(f"发布者：{author}")
            scene_parts.append(f"地点：{location}")
            scene_parts.append(f"时间：{time_str}")
            scene_parts.append(f"内容：{post_content}")
        else:
            scene_parts.append(f"内容：{post_content}")
        scene_desc = "\n".join(scene_parts)
        
        # 关系描述
        relation_desc = ""
        if is_reply and "正在回复" in context:
            import re
            match = re.search(r'正在回复 ([^ ]+) 的评论', context)
            if match:
                replied_to = match.group(1)
                relation_val = get_relationship(character, replied_to)
                if relation_val > 0.7:
                    relation_desc = f"\n你与 {replied_to} 的关系：非常亲密，可以开玩笑、调侃。"
                elif relation_val > 0.4:
                    relation_desc = f"\n你与 {replied_to} 的关系：普通朋友，客套但友好。"
                else:
                    relation_desc = f"\n你与 {replied_to} 的关系：不太熟，礼貌回应，保持距离。"
        
        # 角色性格约束（细化）
        personality_constraint = ""
        if character == "丹恒":
            personality_constraint = "你话很少，回复通常只有几个字或简短句子，不会热情洋溢。"
        elif character == "景元":
            personality_constraint = "你说话带文言气息，喜欢用‘本将军’自称，语气慵懒。"
        elif character == "砂金":
            personality_constraint = "你傲娇，爱挑剔，喜欢说‘还行吧’‘下次带你去更好的’之类的话。"
        elif character == "银狼":
            personality_constraint = "你爱用游戏术语，如‘666’‘开黑’‘牛啊’，语气直接。"
        elif character == "花火":
            personality_constraint = "你是个乐子人，说话带‘嘻嘻’，喜欢拉人去二相乐园。"
        elif character == "三月七":
            personality_constraint = "你活泼话多，爱用颜文字✨🍗🎉，说话热情。"
        elif character == "姬子":
            personality_constraint = "你成熟温柔，喜欢咖啡，说话温和有礼。"
        else:
            personality_constraint = f"你的性格：{personality}"
        
        # 强化 prompt：明确要求基于四个维度，禁止模板化，避免逻辑跳跃
        prompt = f"""你是《崩坏：星穹铁道》中的{character}。

【角色核心设定】
{personality_constraint}
- 说话风格：{style}
- 兴趣：{interests}
- 口头禅：{catchphrases}
{relation_desc}

【当前朋友圈场景】（包含发布者、地点、时间、内容）
{scene_desc}
{context}

【严格生成要求】
1. 评论长度 15-40 字。
2. 必须严格基于以下四个维度生成评论：
   - 角色性格（{personality_constraint}）
   - 你与发布者/评论者的关系（根据关系描述调整语气）
   - 朋友圈的文案内容（要承接上文，不能答非所问）
   - 地点情况（可结合地点细节，让评论显得真实）
3. 禁止使用过于简短的通用回复，如“嗯”、“不错”、“有意思”等（除非角色性格极度内敛，如丹恒可简短，但也要有内容）。
4. 如果是回复，必须承接上文，不能出现逻辑断裂（例如别人说“注意休息”，你不能回“那我更要试试”）。
5. 直接输出评论内容，不要加引号或额外说明。

请生成一条符合角色性格、基于上述四个维度的{'回复' if is_reply else '评论'}："""
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,   # 适当降低温度，减少随机性
            max_tokens=100
        )
        
        result = response.choices[0].message.content.strip()
        result = result.encode('utf-8', errors='ignore').decode('utf-8')
        
        # 简单后处理：如果结果过短（<5字），视为生成失败，抛异常触发重试
        if len(result) < 5:
            raise ValueError("生成结果过短")
        
        return result
        
    except Exception as e:
        # 如果 AI 调用失败或结果无效，重试一次（仍不用模板）
        #print(f"AI 调用失败或结果无效 ({character}): {e}，重试一次...")
        try:
            # 简单重试：再次调用同一函数（递归，但只一次）
            # 为了避免无限递归，使用标志
            response2 = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=100
            )
            result2 = response2.choices[0].message.content.strip()
            result2 = result2.encode('utf-8', errors='ignore').decode('utf-8')
            if len(result2) >= 5:
                return result2
        except Exception as e2:
            pass
        
        # 如果重试仍失败，返回一个占位符（避免程序中断，但你也可以改为 raise）
        return f"[{character} 暂时无法评论]"  # 这不是模板，而是错误占位符，你可以决定是否保留

# def generate_template_comment(character, is_reply):
#     """增强版模板，减少‘嗯’的出现"""
#     templates = {
#         "三月七": [
#             "哇！看起来好棒！✨ 下次一定要带上我！",
#             "啊啊啊这个超喜欢！我也想吃！🍗",
#             "好厉害！开拓者真会找地方！",
#             "拍下来拍下来！我要发朋友圈！"
#         ],
#         "丹恒": [
#             "注意安全。",
#             "嗯，还不错。",
#             "别太累。",
#             "……随你。"
#         ],
#         "姬子": [
#             "看起来不错，下次可以试试配我的咖啡。",
#             "真热闹啊，列车好久没这么开心了。",
#             "注意休息，别太晚。",
#             "嗯，很有品味。"
#         ],
#         "景元": [
#             "好生热闹。本将军也想休沐一日。",
#             "不错不错，罗浮也有类似的地方。",
#             "彦卿，别学我摸鱼。",
#             "悠闲一日，甚好。"
#         ],
#         "砂金": [
#             "还行吧，下次带你去更好的。",
#             "这品味...算了。",
#             "运气不错。",
#             "嗯，一般般。"
#         ],
#         "银狼": [
#             "666，下次开黑吗？",
#             "牛啊！今晚通宵？",
#             "这操作可以啊！",
#             "游戏打完了？"
#         ],
#         "花火": [
#             "嘻嘻，来二相乐园玩啊~比这有意思多了！",
#             "有意思！🎪 让我也瞧瞧！",
#             "乐！搞快点搞快点！",
#             "好玩吗好玩吗？"
#         ],
#         "托帕": [
#             "不错。注意预算。",
#             "砂金你又开始了。",
#             "工作完成了？",
#             "嗯，可以。"
#         ],
#         "彦卿": [
#             "将军说得对！",
#             "我也想去！",
#             "好厉害！我可以去吗！",
#             "将军您不是说减肥吗..."
#         ],
#         "帕姆": [
#             "哼！帕姆也很厉害的！",
#             "注意列车卫生！",
#             "不错不错。",
#             "帕姆要生气了！"
#         ],
#         "黑塔": [
#             "有意思的数据。",
#             "让我研究一下。",
#             "嗯，能量参数异常。",
#             "理论成立。"
#         ],
#         "default": [
#             "不错。",
#             "有意思。",
#             "支持！",
#             "👍"
#         ]
#     }
    
#     # 回复专用模板
#     reply_templates = {
#         "三月七": ["真的吗！那我更要试试了！", "说得对！支持！✨", "啊哈哈，我也这么觉得！"],
#         "丹恒": ["确实。", "嗯。", "你说得对。"],
#         "姬子": ["同意。", "说得对。", "嗯，有道理。"],
#         "景元": ["言之有理。", "将军也这么想。", "说得是。"],
#         "砂金": ["确实一般。", "你也这么觉得？", "嗯。"],
#         "银狼": ["赞同！", "+1", "就是这个意思！"],
#         "花火": ["哈哈说得对！", "没错没错！", "好玩！"],
#         "托帕": ["同意。", "嗯。", "说得对。"],
#         "彦卿": ["将军说得对！", "我也这么想！", "没错！"],
#         "帕姆": ["嗯哼！", "说得对！", "帕姆也这么觉得！"],
#         "黑塔": ["理论成立。", "同意。", "嗯。"]
#     }
    
#     if is_reply and character in reply_templates:
#         return random.choice(reply_templates[character])
    
#     char_templates = templates.get(character, templates["default"])
#     return random.choice(char_templates)

def get_avatar_filename(name):
    avatar_map = {
        "三月七": "march_seven.png",
        "丹恒": "dh.png",
        "姬子": "jizi-avatar.png",
        "景元": "jingyuan-avatar.png",
        "彦卿": "yq.png",
        "砂金": "sj.png",
        "托帕": "tuopa-avatar.png",
        "银狼": "silver_wolf.png",
        "卡芙卡": "kafuka-avatar.png",
        "刃": "ren-avatar.png",
        "花火": "huahuo-avatar.png",
        "黑塔": "heita-avatar.png",
        "知更鸟": "zhigengniao-avatar.png",
        "帕姆": "pamu-avatar.png",
        "符玄": "fuxuan-avatar.png"
    }
    return avatar_map.get(name, "default.png")

def generate_post(post_id, author, content, image_path):
    """生成单条朋友圈，基于阵营匹配地点"""
    # 获取作者阵营和地点
    faction = FACTIONS.get(author, "未知")
    locations = LOCATIONS_BY_FACTION.get(faction, ["未知地点"])
    location = random.choice(locations)
    
    # 点赞
    likes = [char for char in ALL_CHARACTERS if will_interact(char, content)]
    if not likes and author in ALL_CHARACTERS:
        likes = [author]
    
    # 评论者
    commenters = [char for char in ALL_CHARACTERS if char != author and will_interact(char, content, "comment")]
    random.shuffle(commenters)
    commenters = commenters[:random.randint(2, 5)]  # 2-5条评论
    
    # 朋友圈元信息（用于评论生成）
    post_info = {
        "author": author,
        "location": location,
        "time": f"{random.randint(1, 3)}小时前",  # 暂时用相对时间，也可用绝对时间
        "content": content
    }
    
    # 生成评论
    comments = []
    for commenter in commenters:
        comment_text = generate_comment(commenter, content, context="", post_info=post_info)
        comment = {
            "author": commenter,
            "content": comment_text,
            "time": f"{random.randint(1, 3)}小时前",
            "replies": []
        }
        # 第一层回复
        first_level = []
        for replier in ALL_CHARACTERS:
            if replier in (commenter, author):
                continue
            if maybe_reply(commenter, comment_text, content, replier):
                reply_text = generate_comment(replier, content, f"正在回复 {commenter} 的评论：「{comment_text}」", post_info=post_info)
                first_level.append({
                    "author": replier,
                    "content": reply_text,
                    "time": f"{random.randint(1, 2)}小时前",
                    "replyTo": commenter,
                    "replies": []
                })
        # 第二层回复
        for reply in first_level:
            second_count = 0
            max_second = random.randint(0, 1)  # 0-1条
            for deeper in ALL_CHARACTERS:
                if second_count >= max_second:
                    break
                if deeper in (reply["author"], commenter, author):
                    continue
                if maybe_reply(reply["author"], reply["content"], content, deeper):
                    deeper_text = generate_comment(deeper, content, f"正在回复 {reply['author']} 的回复：「{reply['content']}」", post_info=post_info)
                    reply["replies"].append({
                        "author": deeper,
                        "content": deeper_text,
                        "time": f"{random.randint(1, 2)}小时前",
                        "replyTo": reply["author"],
                        "replies": []
                    })
                    second_count += 1
        comment["replies"] = first_level
        comments.append(comment)
    
    # 表情反应
    reactions = []
    reaction_emojis = ["🍗", "😂", "❤️", "🔥", "✨", "🎉", "😭", "👍", "😎", "🤔"]
    for _ in range(min(len(likes), 5)):
        emoji = random.choice(reaction_emojis)
        existing = next((r for r in reactions if r["emoji"] == emoji), None)
        if existing:
            existing["count"] += random.randint(1, 3)
        else:
            reactions.append({"emoji": emoji, "count": random.randint(1, len(likes))})
    
    # 时间和地点（已包含在 post_info 中，但返回中还需要）
    time_hours = random.randint(1, 48)
    time_str = f"{time_hours}小时前" if time_hours < 24 else f"{time_hours//24}天前"
    
    return {
        "id": post_id,
        "author": author,
        "avatar": f"images/avatars/{get_avatar_filename(author)}",
        "time": time_str,
        "location": location,
        "content": content,
        "images": [image_path],
        "likes": likes,
        "likeCount": len(likes),
        "reactions": reactions,
        "comments": comments
    }

# ========== 朋友圈内容模板 ==========
POST_TEMPLATES = [
    ("三月七", "帕姆今天超厉害！做了一整个蛋糕！！", "images/cake.jpg"),
    ("丹恒", "智库新到了一批古籍。", "images/books.jpg"),
    ("景元", "难得清闲一日，终于可以摸鱼了。", "images/jingyuan_rest.jpg"),
    ("砂金", "今天运气不错，小赚一笔。", "images/gamble.jpg"),
    ("银狼", "通宵打完新游戏了，爽！", "images/gaming.jpg"),
    ("姬子", "新烘焙的咖啡豆，香味很特别。", "images/coffee.jpg"),
    ("花火", "嘻嘻，今天二相乐园又有新节目啦！🎪", "images/huahuo_show.jpg"),
    ("托帕", "星际和平公司季度报告完成。", "images/report.jpg"),
    ("彦卿", "今日剑术练习完成！将军夸我了！", "images/sword.jpg"),
    ("帕姆", "列车清洁日！谁都不许乱扔垃圾！", "images/pam_clean.jpg"),
]

def get_random_post_template():
    return random.choice(POST_TEMPLATES)

# ========== 主程序 ==========
if __name__ == "__main__":
    NUM_POSTS = random.randint(10, 15)
    print(f"开始生成 {NUM_POSTS} 条朋友圈...")
    all_posts = []
    for i in range(1, NUM_POSTS + 1):
        author, content, image = get_random_post_template()
        print(f"生成第 {i}/{NUM_POSTS} 条: {author} - {content[:20]}...")
        post = generate_post(i, author, content, image)
        all_posts.append(post)
        print(f"  完成第 {i} 条")
    output = {"posts": all_posts}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完成！共 {len(all_posts)} 条朋友圈，保存到 data.json")