import json
import random
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from generator_data import (
    CHARACTERS, ALL_CHARACTERS, FACTIONS, LOCATIONS_BY_FACTION,
    get_relationship, relevance_score, will_interact, maybe_reply,
    generate_comment, get_avatar_filename, generate_post  # 新增 generate_post
)
import openai

app = Flask(__name__)
CORS(app)  # 允许前端跨域请求

# 配置 DeepSeek（与 generator_data.py 一致）
DEEPSEEK_API_KEY = "你的API Key"
client = openai.OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# 导入 generator_data 中的配置（如 RELATIONSHIPS, CHARACTERS 等已在导入时自动加载）
# 注意：generator_data.py 中已有 client 定义，为了避免冲突，我们重新定义 client
# 但 generator_data.py 中已有 client，直接使用即可

def generate_comment_for_character(character, post_content, post_info):
    """为指定角色生成评论（复用 generate_comment）"""
    # 注意：generate_comment 需要 client 和 CHARACTERS 等全局变量，这些已在 generator_data 中定义
    # 但 generator_data 中的 generate_comment 会调用 openai，我们需要确保它使用正确的 client
    # 由于 generator_data 中已经初始化了 client，我们可以直接使用
    from generator_data import generate_comment as orig_generate_comment
    return orig_generate_comment(character, post_content, context="", post_info=post_info)

@app.route('/post', methods=['POST'])
def create_post():
    """接收玩家发布的朋友圈，生成评论并追加到 data.json"""
    data = request.json
    content = data.get('content', '')
    image = data.get('image', 'images/default.jpg')
    
    # 获取新 ID
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            existing = json.load(f)
            existing_posts = existing.get('posts', [])
            max_id = max([p['id'] for p in existing_posts]) if existing_posts else 0
    except FileNotFoundError:
        existing_posts = []
        max_id = 0
    
    new_id = max_id + 1
    
    # 调用 generate_post 生成完整动态
    new_post = generate_post(new_id, "开拓者", content, image, force_time="刚刚")
    
    # 保存
    existing_posts.append(new_post)
    output = {"posts": existing_posts}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    return jsonify({"success": True, "post": new_post})

if __name__ == '__main__':
    app.run(debug=True, port=5000)