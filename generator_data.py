import json
import random
import openai
# ========== DeepSeek 配置 ==========
DEEPSEEK_API_KEY = "sk-b3a4f4a80d474b81bd673c27f6af92cb"  # 替换成你的真实 key

# 初始化客户端
client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


# 加载生成的详细角色数据
with open("characters_data.json", "r", encoding="utf-8") as f:
    GENERATED_CHARACTERS = json.load(f)

# 合并到 CHARACTERS（优先使用生成的数据，缺失则用模板）
CHARACTERS = {}
for name in GENERATED_CHARACTERS:
    gen = GENERATED_CHARACTERS[name]
    CHARACTERS[name] = {
        "personality": gen.get("personality", "未知"),
        "active_coefficient": gen.get("active_coefficient", 0.5),
        "interests": gen.get("interests", []),
        "style": gen.get("style", ""),
        "catchphrases": gen.get("catchphrases", [])
    }

# 角色间关系值矩阵 (0-1)
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

# 所有角色列表
ALL_CHARACTERS = list(CHARACTERS.keys())

def relevance_score(character, post_content):
    """计算角色与朋友圈内容的相关性 (0-1)"""
    interests = CHARACTERS[character]["interests"]
    if not interests:
        return 0.5
    content_lower = post_content.lower()
    matches = sum(1 for interest in interests if interest.lower() in content_lower)
    score = min(matches / 3.0, 1.0)
    return score

def will_interact(character, post_content, interaction_type="like"):
    """判断角色是否会互动（点赞或评论）"""
    base_prob = CHARACTERS[character]["active_coefficient"]
    relevance = relevance_score(character, post_content)
    adjusted_prob = base_prob * (0.5 + 0.5 * relevance)
    final_prob = min(adjusted_prob * random.uniform(0.8, 1.2), 1.0)
    return random.random() < final_prob

def get_relationship(character_a, character_b):
    """获取两个角色之间的关系系数"""
    if character_a == character_b:
        return 1.0
    key = (character_a, character_b)
    if key in RELATIONSHIPS:
        return RELATIONSHIPS[key]
    return 0.3

def maybe_reply_to_comment(comment_author, comment_content, post_content, replier):
    """判断 replier 是否会回复 comment_author 的评论"""
    
    if replier == comment_author:
        return False
    
    relation = get_relationship(replier, comment_author)
    
    # 关系太差就不回复
    if relation < 0.1:
        return False
    
    base_prob = CHARACTERS[replier]["active_coefficient"] * 0.9
    
    combined_text = (comment_content or "") + " " + (post_content or "")
    relevance = relevance_score(replier, combined_text)
    
    # 即使完全不相关也有保底概率
    if relevance < 0.1:
        final_prob = base_prob * relation * 0.4
    else:
        final_prob = base_prob * relation * (0.7 + 0.3 * relevance)
    
    final_prob = min(final_prob, 0.85)
    
    return random.random() < final_prob

def generate_template_comment(character, post_content, context=""):
    """生成评论，考虑上下文"""
    
    is_reply = "正在回复" in context
    
    templates = {
        "三月七": {
            "normal": [
                "哇！看起来好棒！✨", 
                "我也想去！带上我嘛！", 
                "这个好好吃的样子！🍗",
                "好厉害！我也要试试！🎉"
            ],
            "reply": [
                "真的吗！那我更要试试了！",
                "说得对！支持！✨",
                "啊哈哈，我也这么觉得！",
                "没错没错！就是这个意思！"
            ]
        },
        "丹恒": {
            "normal": ["……", "注意安全。", "嗯。", "不错。"],
            "reply": ["确实。", "嗯。", "你说得对。", "……"]
        },
        "姬子": {
            "normal": ["看起来不错。", "下次可以试试配咖啡。", "真热闹啊。"],
            "reply": ["同意。", "说得对。", "嗯，有道理。"]
        },
        "景元": {
            "normal": ["好生热闹。", "本将军也想休假了。", "不错不错。"],
            "reply": ["言之有理。", "将军也这么想。", "说得是。"]
        },
        "砂金": {
            "normal": ["还行吧。", "下次带你去更好的。", "这品味...算了。"],
            "reply": ["确实一般。", "你也这么觉得？", "嗯。"]
        },
        "银狼": {
            "normal": ["666", "下次开黑吗？", "牛啊"],
            "reply": ["赞同！", "+1", "就是这个意思！"]
        },
        "花火": {
            "normal": ["嘻嘻，来二相乐园玩啊~", "有意思！🎪", "乐！"],
            "reply": ["哈哈说得对！", "没错没错！", "好玩！"]
        },
        "托帕": {
            "normal": ["不错。", "注意预算。", "工作完成了？"],
            "reply": ["同意。", "嗯。", "说得对。"]
        },
        "彦卿": {
            "normal": ["将军说得对！", "我也想去！", "好厉害！"],
            "reply": ["将军说得对！", "我也这么想！", "没错！"]
        },
        "帕姆": {
            "normal": ["哼！帕姆也很厉害的！", "注意列车卫生！", "不错不错。"],
            "reply": ["嗯哼！", "说得对！", "帕姆也这么觉得！"]
        },
        "黑塔": {
            "normal": ["有意思的数据。", "让我研究一下。", "嗯。"],
            "reply": ["理论成立。", "同意。", "嗯。"]
        }
    }
    
    char_templates = templates.get(character, {
        "normal": ["不错。", "嗯。", "有意思。"],
        "reply": ["确实。", "嗯。", "同意。"]
    })
    
    if is_reply:
        return random.choice(char_templates["reply"])
    else:
        return random.choice(char_templates["normal"])


def generate_comment(character, post_content, context=""):
    """生成评论，使用 DeepSeek"""
    try:
        char_data = CHARACTERS.get(character, {})
        is_reply = "正在回复" in context
        
        prompt = f"""你是《崩坏：星穹铁道》中的{character}。

【角色设定】
- 性格：{char_data.get('personality', '未知')}
- 说话风格：{char_data.get('style', '自然')}
- 兴趣：{', '.join(char_data.get('interests', []))}

【当前场景】
朋友圈内容：{post_content}
{context}

请生成一条符合角色性格的{'回复' if is_reply else '评论'}（15-40字），直接输出内容，不要加引号："""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=80
        )
        result = response.choices[0].message.content.strip()
        # 如果结果太长，截取前40字
        if len(result) > 50:
            result = result[:50]
        return result
        
    except Exception as e:
        print(f"AI 调用失败 ({character}): {e}")
        # 返回模板作为 fallback
        return generate_template_comment(character, is_reply)

def generate_post(post_id, author, content, image_path):
    """生成一条朋友圈，使用概率引擎"""
    # 1. 决定哪些角色点赞
    likes = []
    for char in ALL_CHARACTERS:
        if will_interact(char, content, "like"):
            likes.append(char)
    if not likes and author in ALL_CHARACTERS:
        likes = [author]

    # 2. 决定哪些角色评论
    commenters = []
    for char in ALL_CHARACTERS:
        if char != author and will_interact(char, content, "comment"):
            commenters.append(char)
    max_comments = min(len(commenters), 6)
    commenters = random.sample(commenters, max_comments) if len(commenters) > max_comments else commenters

    # 3. 生成评论（包括可能的回复）
        # 3. 生成评论（支持链式回复）
    comments = []
    for commenter in commenters:
        comment_text = generate_comment(commenter, content, context="")
        comment = {
            "author": commenter,
            "content": comment_text,
            "time": f"{random.randint(1, 3)}小时前",
            "replies": []
        }
        
        # 第一层回复：直接回复这条评论
        first_level_replies = []
        for replier in ALL_CHARACTERS:
            if replier == commenter or replier == author:
                continue
            if maybe_reply_to_comment(commenter, comment_text, content, replier):
                reply_text = generate_comment(replier, content, context=f"正在回复 {commenter} 的评论：「{comment_text}」")
                first_level_replies.append({
                    "author": replier,
                    "content": reply_text,
                    "time": f"{random.randint(1, 2)}小时前",
                    "replyTo": commenter,
                    "replies": []  # 支持更深层的回复
                })
        
    
         # 第二层回复：有人回复了第一层回复（A回复B，C回复A）
        for reply in first_level_replies:
            second_level_count = 0
            max_second = random.randint(1, 2)  # 每个第一层回复可以有 1-2 条第二层回复
            for deeper_replier in ALL_CHARACTERS:
                if second_level_count >= max_second:
                    break
                if deeper_replier == reply["author"] or deeper_replier == commenter or deeper_replier == author:
                    continue
                if maybe_reply_to_comment(reply["author"], reply["content"], content, deeper_replier):
                    deeper_text = generate_comment(deeper_replier, content, context=f"正在回复 {reply['author']} 的回复：「{reply['content']}」")
                    reply["replies"].append({
                        "author": deeper_replier,
                        "content": deeper_text,
                        "time": f"{random.randint(1, 2)}小时前",
                        "replyTo": reply["author"],
                        "replies": []
                    })
                    second_level_count += 1
        
        comment["replies"] = first_level_replies
        comments.append(comment)

    # 4. 生成表情反应
    reactions = []
    reaction_emojis = ["🍗", "😂", "❤️", "🔥", "✨", "🎉", "😭", "👍", "😎", "🤔"]
    for _ in range(min(len(likes), 5)):
        emoji = random.choice(reaction_emojis)
        existing = next((r for r in reactions if r["emoji"] == emoji), None)
        if existing:
            existing["count"] += random.randint(1, 3)
        else:
            reactions.append({"emoji": emoji, "count": random.randint(1, len(likes))})

    # 5. 其他数据
    time_hours = random.randint(1, 48)
    time_str = f"{time_hours}小时前" if time_hours < 24 else f"{time_hours//24}天前"
    locations = [
        "星穹列车 · 观景车厢", "匹诺康尼 · 梦境", "仙舟 · 罗浮",
        "贝洛伯格 · 下层区", "空间站 · 黑塔", "星核猎手 · 基地"
    ]
    
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

    return {
        "id": post_id,
        "author": author,
        "avatar": f"images/avatars/{get_avatar_filename(author)}",
        "time": time_str,
        "location": random.choice(locations),
        "content": content,
        "images": [image_path],
        "likes": likes,
        "likeCount": len(likes),
        "reactions": reactions,
        "comments": comments
    }

# ========== 生成数据 ==========
if __name__ == "__main__":
    print("开始生成朋友圈数据（概率引擎版）...")
    
    posts_data = [
        ("三月七", "帕姆今天超厉害！做了一整个蛋糕！！", "images/cake.jpg"),
        ("丹恒", "智库新到了一批古籍。", "images/books.jpg"),
        ("景元", "难得清闲一日，终于可以摸鱼了。", "images/jingyuan_rest.jpg"),
        ("砂金", "今天运气不错，小赚一笔。", "images/gamble.jpg"),
        ("银狼", "通宵打完新游戏了，爽！", "images/gaming.jpg"),
        ("姬子", "新烘焙的咖啡豆，香味很特别。", "images/coffee.jpg"),
        ("花火", "嘻嘻，今天二相乐园又有新节目啦！🎪", "images/huahuo_show.jpg"),
        ("托帕", "星际和平公司季度报告完成。", "images/report.jpg"),
        ("彦卿", "今日剑术练习完成！将军夸我了！", "images/sword.jpg"),
        ("帕姆", "列车清洁日！谁都不许乱扔垃圾！", "images/pam_clean.jpg")
    ]
    
    all_posts = []
    for i, (author, content, image) in enumerate(posts_data, 1):
        print(f"生成第{i}条: {author} - {content[:20]}...")
        post = generate_post(i, author, content, image)
        all_posts.append(post)
    
    output = {"posts": all_posts}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 完成！已生成 {len(all_posts)} 条朋友圈，保存到 data.json")
    print("现在可以刷新浏览器查看效果了！")