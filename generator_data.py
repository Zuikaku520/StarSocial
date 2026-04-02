import json
import random
import openai
from datetime import datetime
import sys
import io
import os
import requests

# TTS 配置
TTS_ENABLED = True
TTS_PROB = 0.6  # 托帕的评论有 30% 概率生成语音
TTS_API_URL = "http://127.0.0.1:9880/tts"  # GPT-SoVITS API 地址
REF_AUDIO_PATH = "F:/googledownload/GPT-SoVITS-v2pro-20250604-nvidia50/data/topaz/wavs/archive_topaz_7.wav"  # 参考音频（一段托帕的干净语音）
VOICES_DIR = "voices"
os.makedirs(VOICES_DIR, exist_ok=True)

# 强制设置编码
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 广告来源配置
AD_SOURCES = {
    "role": {
        "characters": ["砂金", "托帕", "黑塔", "翡翠"],  # 可扩展
        "weight": 20
    },
    "official": {
        "names": ["星际和平公司", "仙舟商会", "黑塔空间站", "星穹列车广播"],
        "weight": 50
    },
    "random_user": {
        "names": ["星海旅行者", "匿名用户", "路过的小浣熊", "银河美少年", "在逃星核猎手"],
        "weight": 30
    }
}

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


def text_to_speech(text, comment_id):
    """调用 TTS API 生成语音，返回相对路径，失败返回 None"""
    if not TTS_ENABLED:
        return None
    
    output_filename = f"comment_{comment_id}.wav"
    output_path = os.path.join(VOICES_DIR, output_filename)
    
    if os.path.exists(output_path):
        return output_filename
    
    # 关键：在这里指定模型路径
    params = {
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": REF_AUDIO_PATH,
        "prompt_lang": "zh",
        "gpt_model": r"F:\googledownload\GPT-SoVITS-v2pro-20250604-nvidia50\GPT_weights_v2Pro\topaz_voices-e5.ckpt",      # 你的 GPT 模型
        "sovits_model": r"F:\googledownload\GPT-SoVITS-v2pro-20250604-nvidia50\SoVITS_weights_v2Pro\topaz_voices_e10_s3850.pth",  # 你的 SoVITS 模型
        "top_k": 5,
        "top_p": 1,
        "temperature": 1,
        "speed_factor": 1.0,
    }
    
    try:
        response = requests.post(TTS_API_URL, json=params, timeout=60)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_filename
    except Exception as e:
        print(f"TTS 生成失败: {e}")
    return None

def get_trendy_words():
    """调用 DeepSeek API 获取当前流行网络用语"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "请列出最近5个流行的网络用语，用逗号分隔，只输出词语，不要解释。"}],
            max_tokens=50,
            temperature=0.5,
            extra_body={"enable_search": True}   # 开启联网搜索
        )
        words = response.choices[0].message.content.strip()
        return words
    except Exception as e:
        print(f"获取流行语失败: {e}，使用默认")
        return "666, 点了, 绝绝子, YYDS, 神人, 绝了, 破防了, 蚌埠住了"
    
def get_acg_fandom_words():
    """调用 DeepSeek API 获取当前流行的 ACG 和饭圈用语"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "请列出最近流行的10个ACG圈和饭圈用语，用逗号分隔，只输出词语，不要解释。例如：推し、厨力、谷子、打call、本命、塌房、营业、同担、绝美、入股不亏"}],
            max_tokens=100,
            temperature=0.5,
            extra_body={"enable_search": True}   # 开启联网搜索
        )
        words = response.choices[0].message.content.strip()
        return words
    except Exception as e:
        print(f"获取ACG/饭圈用语失败: {e}，使用默认")
        return "推し, 厨力, 谷子, 打call, 本命, 塌房, 营业, 同担, 绝美, 入股不亏"
    

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
        "catchphrases": data.get("catchphrases", []),
        "trendy_style": data.get("trendy_style", ""),  # 新增
        "term_style": data.get("term_style", "")   # 新增
    }

ALL_CHARACTERS = list(CHARACTERS.keys())
print(f"已加载 {len(ALL_CHARACTERS)} 个角色")

# 加载朋友圈内容
with open("posts.json", "r", encoding="utf-8") as f:
    POST_TEMPLATES = json.load(f)
print(f"已加载 {len(POST_TEMPLATES)} 条朋友圈模板")

# ========== 阵营和地点数据 ==========
FACTIONS = {
    # 星穹列车
    "三月七": "星穹列车",
    "丹恒": "星穹列车",
    "姬子": "星穹列车",
    "瓦尔特·杨": "星穹列车",
    "帕姆": "星穹列车",
    "银枝": "星穹列车",
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
    "青雀":"仙舟罗浮",
    #仙舟曜青
    "飞霄":"仙舟曜青",
    "椒丘":"仙舟曜青",
    "貊泽":"仙舟曜青",
    # 星核猎手
    "卡芙卡": "星核猎手",
    "银狼": "星核猎手",
    "刃": "星核猎手",
    # 星际和平公司
    "砂金": "星际和平公司",
    "托帕": "星际和平公司",
    "真理医生": "星际和平公司",
    "银枝": "星际和平公司",
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
    "银枝": "匹诺康尼",
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
    "银枝": "贝洛伯格",
    # 黑塔空间站
    "黑塔": "黑塔空间站",
    "艾丝妲": "黑塔空间站",
    "阿兰": "黑塔空间站",
    "阮·梅":"黑塔空间站",
    "银枝": "黑塔空间站",
}

LOCATIONS_BY_FACTION = {
    "星穹列车": [
        "星穹列车 · 观景车厢",
        "星穹列车 · 客房车厢",
        "星穹列车 · 智库",
        "星穹列车 · 酒吧"
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
    "仙舟曜青": [
        "仙舟曜青 · 将军府",
        "仙舟曜青 · 长乐天",
        "仙舟曜青 · 青丘军俱乐部",
        "仙舟曜青 · 曜青星港"
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
      "三月七|丹恒": 0.95,
  "三月七|姬子": 0.8,
  "三月七|帕姆": 0.7,
  "丹恒|刃": 0.9,
  "丹恒|景元": 0.85,
  "丹恒|三月七": 0.8,
  "姬子|三月七": 0.8,
  "姬子|卡芙卡": 0.65,
  "景元|符玄": 0.9,
  "景元|彦卿": 0.85,
  "景元|刃": 0.7,
  "景元|镜流": 0.65,
  "彦卿|景元": 0.95,
  "彦卿|符玄": 0.75,
  "彦卿|镜流": 0.7,
  "砂金|托帕": 0.9,
  "砂金|翡翠": 0.85,
  "砂金|知更鸟": 0.7,
  "托帕|砂金": 0.85,
  "托帕|翡翠": 0.8,
  "托帕|姬子": 0.65,
  "银狼|卡芙卡": 0.95,
  "银狼|刃": 0.8,
  "银狼|螺丝咕姆": 0.75,
  "卡芙卡|银狼": 0.95,
  "卡芙卡|刃": 0.9,
  "刃|丹恒": 0.95,
  "刃|镜流": 0.9,
  "刃|卡芙卡": 0.85,
  "花火|知更鸟": 0.65,
  "花火|流萤": 0.6,
  "黑塔|螺丝咕姆": 0.9,
  "黑塔|阮·梅": 0.85,
  "知更鸟|流萤": 0.75,
  "知更鸟|砂金": 0.65,
  "帕姆|姬子": 0.85,
  "帕姆|三月七": 0.75,
  "符玄|景元": 0.9,
  "符玄|彦卿": 0.7,
  "黄泉|黑天鹅": 0.9,
  "黄泉|花火": 0.75,
  "黄泉|砂金": 0.7,
  "黄泉|银狼": 0.65,
  "波提欧|黄泉": 0.9,
  "波提欧|砂金": 0.75,
  "波提欧|黑天鹅": 0.7,
  "波提欧|知更鸟": 0.6,
  "银枝|波提欧": 0.75,
  "白露|丹恒": 0.9,
  "白露|景元": 0.85,
  "白露|刃": 0.75,
  "白露|镜流": 0.7,
  "镜流|丹恒": 0.95,
  "镜流|刃": 0.9,
  "镜流|景元": 0.85,
  "镜流|彦卿": 0.7,
  "阮·梅|黑塔": 0.9,
  "阮·梅|螺丝咕姆": 0.85,
  "螺丝咕姆|黑塔": 0.9,
  "螺丝咕姆|阮·梅": 0.75,
  "翡翠|砂金": 0.9,
  "翡翠|托帕": 0.85,
  "翡翠|知更鸟": 0.7,
  "流萤|三月七": 0.7,
  "飞霄|景元": 0.9,
  "飞霄|彦卿": 0.75,
  "飞霄|符玄": 0.7,
  "灵砂|丹恒": 0.9,
  "灵砂|景元": 0.85,
  "灵砂|符玄": 0.75,
  "灵砂|彦卿": 0.7,
  "云璃|彦卿": 0.9,
  "云璃|景元": 0.85,
  "黑天鹅|卡芙卡": 0.95,
  "黑天鹅|流萤": 0.75,
  "黑天鹅|黄泉": 0.7,
  "黑天鹅|砂金": 0.6,
  "三月七|景元": 0.35,
  "景元|三月七": 0.35,
  "三月七|彦卿": 0.35,
  "彦卿|三月七": 0.35,
  "三月七|砂金": 0.15,
  "砂金|三月七": 0.15,
  "三月七|托帕": 0.35,
  "托帕|三月七": 0.35,
  "三月七|银狼": 0.35,
  "银狼|三月七": 0.35,
  "三月七|卡芙卡": 0.15,
  "卡芙卡|三月七": 0.15,
  "三月七|刃": 0.15,
  "刃|三月七": 0.15,
  "三月七|花火": 0.15,
  "花火|三月七": 0.15,
  "三月七|黑塔": 0.35,
  "黑塔|三月七": 0.35,
  "三月七|知更鸟": 0.15,
  "知更鸟|三月七": 0.15,
  "三月七|符玄": 0.65,
  "符玄|三月七": 0.65,
  "三月七|黄泉": 0.25,
  "黄泉|三月七": 0.25,
  "三月七|波提欧": 0.15,
  "波提欧|三月七": 0.15,
  "三月七|乱破": 0.15,
  "乱破|三月七": 0.15,
  "三月七|银枝": 0.15,
  "银枝|三月七": 0.15,
  "三月七|白露": 0.65,
  "白露|三月七": 0.65,
  "三月七|镜流": 0.15,
  "镜流|三月七": 0.15,
  "三月七|阮·梅": 0.15,
  "阮·梅|三月七": 0.15,
  "三月七|螺丝咕姆": 0.15,
  "螺丝咕姆|三月七": 0.15,
  "三月七|翡翠": 0.15,
  "翡翠|三月七": 0.15,
  "三月七|飞霄": 0.15,
  "飞霄|三月七": 0.15,
  "三月七|灵砂": 0.15,
  "灵砂|三月七": 0.15,
  "三月七|云璃": 0.35,
  "云璃|三月七": 0.35,
  "三月七|黑天鹅": 0.15,
  "黑天鹅|三月七": 0.15,
  "丹恒|姬子": 0.35,
  "姬子|丹恒": 0.35,
  "丹恒|彦卿": 0.35,
  "彦卿|丹恒": 0.35,
  "丹恒|砂金": 0.15,
  "砂金|丹恒": 0.15,
  "丹恒|托帕": 0.15,
  "托帕|丹恒": 0.15,
  "丹恒|银狼": 0.15,
  "银狼|丹恒": 0.15,
  "丹恒|卡芙卡": 0.15,
  "卡芙卡|丹恒": 0.15,
  "丹恒|花火": 0.15,
  "花火|丹恒": 0.15,
  "丹恒|黑塔": 0.15,
  "黑塔|丹恒": 0.15,
  "丹恒|知更鸟": 0.15,
  "知更鸟|丹恒": 0.15,
  "丹恒|帕姆": 0.65,
  "帕姆|丹恒": 0.65,
  "丹恒|符玄": 0.25,
  "符玄|丹恒": 0.25,
  "丹恒|黄泉": 0.15,
  "黄泉|丹恒": 0.15,
  "丹恒|波提欧": 0.15,
  "波提欧|丹恒": 0.15,
  "丹恒|乱破": 0.15,
  "乱破|丹恒": 0.15,
  "丹恒|银枝": 0.15,
  "银枝|丹恒": 0.15,
  "丹恒|阮·梅": 0.15,
  "阮·梅|丹恒": 0.15,
  "丹恒|螺丝咕姆": 0.15,
  "螺丝咕姆|丹恒": 0.15,
  "丹恒|翡翠": 0.15,
  "翡翠|丹恒": 0.15,
  "丹恒|流萤": 0.15,
  "流萤|丹恒": 0.15,
  "丹恒|飞霄": 0.15,
  "飞霄|丹恒": 0.15,
  "丹恒|云璃": 0.15,
  "云璃|丹恒": 0.15,
  "丹恒|黑天鹅": 0.15,
  "黑天鹅|丹恒": 0.15,
  "姬子|景元": 0.3,
  "景元|姬子": 0.3,
  "姬子|彦卿": 0.15,
  "彦卿|姬子": 0.15,
  "姬子|砂金": 0.15,
  "砂金|姬子": 0.15,
  "姬子|银狼": 0.35,
  "银狼|姬子": 0.35,
  "姬子|刃": 0.15,
  "刃|姬子": 0.15,
  "姬子|花火": 0.15,
  "花火|姬子": 0.15,
  "姬子|黑塔": 0.65,
  "黑塔|姬子": 0.65,
  "姬子|知更鸟": 0.15,
  "知更鸟|姬子": 0.15,
  "姬子|符玄": 0.65,
  "符玄|姬子": 0.65,
  "姬子|黄泉": 0.15,
  "黄泉|姬子": 0.15,
  "姬子|波提欧": 0.15,
  "波提欧|姬子": 0.15,
  "姬子|乱破": 0.15,
  "乱破|姬子": 0.15,
  "姬子|银枝": 0.15,
  "银枝|姬子": 0.15,
  "姬子|白露": 0.25,
  "白露|姬子": 0.25,
  "姬子|镜流": 0.15,
  "镜流|姬子": 0.15,
  "姬子|阮·梅": 0.25,
  "阮·梅|姬子": 0.25,
  "姬子|螺丝咕姆": 0.35,
  "螺丝咕姆|姬子": 0.35,
  "姬子|翡翠": 0.15,
  "翡翠|姬子": 0.15,
  "姬子|流萤": 0.15,
  "流萤|姬子": 0.15,
  "姬子|飞霄": 0.15,
  "飞霄|姬子": 0.15,
  "姬子|灵砂": 0.15,
  "灵砂|姬子": 0.15,
  "姬子|云璃": 0.15,
  "云璃|姬子": 0.15,
  "姬子|黑天鹅": 0.15,
  "黑天鹅|姬子": 0.15,
  "景元|砂金": 0.35,
  "砂金|景元": 0.35,
  "景元|托帕": 0.15,
  "托帕|景元": 0.15,
  "景元|银狼": 0.15,
  "银狼|景元": 0.15,
  "景元|卡芙卡": 0.15,
  "卡芙卡|景元": 0.15,
  "景元|花火": 0.15,
  "花火|景元": 0.15,
  "景元|黑塔": 0.15,
  "黑塔|景元": 0.15,
  "景元|知更鸟": 0.15,
  "知更鸟|景元": 0.15,
  "景元|帕姆": 0.15,
  "帕姆|景元": 0.15,
  "景元|黄泉": 0.15,
  "黄泉|景元": 0.15,
  "景元|波提欧": 0.15,
  "波提欧|景元": 0.15,
  "景元|乱破": 0.15,
  "乱破|景元": 0.15,
  "景元|银枝": 0.15,
  "银枝|景元": 0.15,
  "景元|阮·梅": 0.15,
  "阮·梅|景元": 0.15,
  "景元|螺丝咕姆": 0.15,
  "螺丝咕姆|景元": 0.15,
  "景元|翡翠": 0.15,
  "翡翠|景元": 0.15,
  "景元|流萤": 0.15,
  "流萤|景元": 0.15,
  "景元|黑天鹅": 0.15,
  "黑天鹅|景元": 0.15,
  "彦卿|砂金": 0.15,
  "砂金|彦卿": 0.15,
  "彦卿|托帕": 0.15,
  "托帕|彦卿": 0.15,
  "彦卿|银狼": 0.15,
  "银狼|彦卿": 0.15,
  "彦卿|卡芙卡": 0.15,
  "卡芙卡|彦卿": 0.15,
  "彦卿|刃": 0.15,
  "刃|彦卿": 0.15,
  "彦卿|花火": 0.15,
  "花火|彦卿": 0.15,
  "彦卿|黑塔": 0.15,
  "黑塔|彦卿": 0.15,
  "彦卿|知更鸟": 0.15,
  "知更鸟|彦卿": 0.15,
  "彦卿|帕姆": 0.15,
  "帕姆|彦卿": 0.15,
  "彦卿|黄泉": 0.15,
  "黄泉|彦卿": 0.15,
  "彦卿|波提欧": 0.15,
  "波提欧|彦卿": 0.15,
  "彦卿|乱破": 0.15,
  "乱破|彦卿": 0.15,
  "彦卿|银枝": 0.15,
  "银枝|彦卿": 0.15,
  "彦卿|白露": 0.65,
  "白露|彦卿": 0.65,
  "彦卿|阮·梅": 0.15,
  "阮·梅|彦卿": 0.15,
  "彦卿|螺丝咕姆": 0.15,
  "螺丝咕姆|彦卿": 0.15,
  "彦卿|翡翠": 0.15,
  "翡翠|彦卿": 0.15,
  "彦卿|流萤": 0.05,
  "流萤|彦卿": 0.05,
  "彦卿|黑天鹅": 0.15,
  "黑天鹅|彦卿": 0.15,
  "砂金|银狼": 0.15,
  "银狼|砂金": 0.15,
  "砂金|卡芙卡": 0.15,
  "卡芙卡|砂金": 0.15,
  "砂金|刃": 0.15,
  "刃|砂金": 0.15,
  "砂金|花火": 0.15,
  "花火|砂金": 0.15,
  "砂金|黑塔": 0.15,
  "黑塔|砂金": 0.15,
  "砂金|帕姆": 0.15,
  "帕姆|砂金": 0.15,
  "砂金|符玄": 0.35,
  "符玄|砂金": 0.35,
  "砂金|乱破": 0.15,
  "乱破|砂金": 0.15,
  "砂金|银枝": 0.15,
  "银枝|砂金": 0.15,
  "砂金|白露": 0.15,
  "白露|砂金": 0.15,
  "砂金|镜流": 0.15,
  "镜流|砂金": 0.15,
  "砂金|阮·梅": 0.15,
  "阮·梅|砂金": 0.15,
  "砂金|螺丝咕姆": 0.15,
  "螺丝咕姆|砂金": 0.15,
  "砂金|流萤": 0.15,
  "流萤|砂金": 0.15,
  "砂金|飞霄": 0.15,
  "飞霄|砂金": 0.15,
  "砂金|灵砂": 0.15,
  "灵砂|砂金": 0.15,
  "砂金|云璃": 0.15,
  "云璃|砂金": 0.15,
  "托帕|银狼": 0.15,
  "银狼|托帕": 0.15,
  "托帕|卡芙卡": 0.15,
  "卡芙卡|托帕": 0.15,
  "托帕|刃": 0.15,
  "刃|托帕": 0.15,
  "托帕|花火": 0.15,
  "花火|托帕": 0.15,
  "托帕|黑塔": 0.15,
  "黑塔|托帕": 0.15,
  "托帕|知更鸟": 0.15,
  "知更鸟|托帕": 0.15,
  "托帕|帕姆": 0.15,
  "帕姆|托帕": 0.15,
  "托帕|符玄": 0.15,
  "符玄|托帕": 0.15,
  "托帕|黄泉": 0.15,
  "黄泉|托帕": 0.15,
  "托帕|波提欧": 0.15,
  "波提欧|托帕": 0.15,
  "托帕|乱破": 0.15,
  "乱破|托帕": 0.15,
  "托帕|银枝": 0.15,
  "银枝|托帕": 0.15,
  "托帕|白露": 0.15,
  "白露|托帕": 0.15,
  "托帕|镜流": 0.15,
  "镜流|托帕": 0.15,
  "托帕|阮·梅": 0.15,
  "阮·梅|托帕": 0.15,
  "托帕|螺丝咕姆": 0.3,
  "螺丝咕姆|托帕": 0.3,
  "托帕|流萤": 0.15,
  "流萤|托帕": 0.15,
  "托帕|飞霄": 0.15,
  "飞霄|托帕": 0.15,
  "托帕|灵砂": 0.15,
  "灵砂|托帕": 0.15,
  "托帕|云璃": 0.15,
  "云璃|托帕": 0.15,
  "托帕|黑天鹅": 0.15,
  "黑天鹅|托帕": 0.15,
  "银狼|花火": 0.15,
  "花火|银狼": 0.15,
  "银狼|黑塔": 0.35,
  "黑塔|银狼": 0.35,
  "银狼|知更鸟": 0.15,
  "知更鸟|银狼": 0.15,
  "银狼|帕姆": 0.15,
  "帕姆|银狼": 0.15,
  "银狼|符玄": 0.65,
  "符玄|银狼": 0.65,
  "银狼|波提欧": 0.15,
  "波提欧|银狼": 0.15,
  "银狼|乱破": 0.15,
  "乱破|银狼": 0.15,
  "银狼|银枝": 0.15,
  "银枝|银狼": 0.15,
  "银狼|白露": 0.15,
  "白露|银狼": 0.15,
  "银狼|镜流": 0.15,
  "镜流|银狼": 0.15,
  "银狼|阮·梅": 0.15,
  "阮·梅|银狼": 0.15,
  "银狼|翡翠": 0.15,
  "翡翠|银狼": 0.15,
  "银狼|流萤": 0.15,
  "流萤|银狼": 0.15,
  "银狼|飞霄": 0.15,
  "飞霄|银狼": 0.15,
  "银狼|灵砂": 0.15,
  "灵砂|银狼": 0.15,
  "银狼|云璃": 0.15,
  "云璃|银狼": 0.15,
  "银狼|黑天鹅": 0.15,
  "黑天鹅|银狼": 0.15,
  "卡芙卡|花火": 0.25,
  "花火|卡芙卡": 0.25,
  "卡芙卡|黑塔": 0.15,
  "黑塔|卡芙卡": 0.15,
  "卡芙卡|知更鸟": 0.15,
  "知更鸟|卡芙卡": 0.15,
  "卡芙卡|帕姆": 0.15,
  "帕姆|卡芙卡": 0.15,
  "卡芙卡|符玄": 0.15,
  "符玄|卡芙卡": 0.15,
  "卡芙卡|黄泉": 0.85,
  "黄泉|卡芙卡": 0.85,
  "卡芙卡|波提欧": 0.15,
  "波提欧|卡芙卡": 0.15,
  "卡芙卡|乱破": 0.85,
  "乱破|卡芙卡": 0.85,
  "卡芙卡|银枝": 0.1,
  "银枝|卡芙卡": 0.1,
  "卡芙卡|白露": 0.15,
  "白露|卡芙卡": 0.15,
  "卡芙卡|镜流": 0.15,
  "镜流|卡芙卡": 0.15,
  "卡芙卡|阮·梅": 0.15,
  "阮·梅|卡芙卡": 0.15,
  "卡芙卡|螺丝咕姆": 0.15,
  "螺丝咕姆|卡芙卡": 0.15,
  "卡芙卡|翡翠": 0.3,
  "翡翠|卡芙卡": 0.3,
  "卡芙卡|流萤": 0.85,
  "流萤|卡芙卡": 0.85,
  "卡芙卡|飞霄": 0.1,
  "飞霄|卡芙卡": 0.1,
  "卡芙卡|灵砂": 0.15,
  "灵砂|卡芙卡": 0.15,
  "卡芙卡|云璃": 0.15,
  "云璃|卡芙卡": 0.15,
  "刃|花火": 0.15,
  "花火|刃": 0.15,
  "刃|黑塔": 0.15,
  "黑塔|刃": 0.15,
  "刃|知更鸟": 0.15,
  "知更鸟|刃": 0.15,
  "刃|帕姆": 0.15,
  "帕姆|刃": 0.15,
  "刃|符玄": 0.15,
  "符玄|刃": 0.15,
  "刃|黄泉": 0.15,
  "黄泉|刃": 0.15,
  "刃|波提欧": 0.15,
  "波提欧|刃": 0.15,
  "刃|乱破": 0.85,
  "乱破|刃": 0.85,
  "刃|银枝": 0.15,
  "银枝|刃": 0.15,
  "刃|阮·梅": 0.15,
  "阮·梅|刃": 0.15,
  "刃|螺丝咕姆": 0.05,
  "螺丝咕姆|刃": 0.05,
  "刃|翡翠": 0.15,
  "翡翠|刃": 0.15,
  "刃|流萤": 0.15,
  "流萤|刃": 0.15,
  "刃|飞霄": 0.15,
  "飞霄|刃": 0.15,
  "刃|灵砂": 0.15,
  "灵砂|刃": 0.15,
  "刃|云璃": 0.15,
  "云璃|刃": 0.15,
  "刃|黑天鹅": 0.15,
  "黑天鹅|刃": 0.15,
  "花火|黑塔": 0.15,
  "黑塔|花火": 0.15,
  "花火|帕姆": 0.15,
  "帕姆|花火": 0.15,
  "花火|符玄": 0.15,
  "符玄|花火": 0.15,
  "花火|波提欧": 0.15,
  "波提欧|花火": 0.15,
  "花火|乱破": 0.85,
  "乱破|花火": 0.85,
  "花火|银枝": 0.15,
  "银枝|花火": 0.15,
  "花火|白露": 0.15,
  "白露|花火": 0.15,
  "花火|镜流": 0.15,
  "镜流|花火": 0.15,
  "花火|阮·梅": 0.15,
  "阮·梅|花火": 0.15,
  "花火|螺丝咕姆": 0.15,
  "螺丝咕姆|花火": 0.15,
  "花火|翡翠": 0.15,
  "翡翠|花火": 0.15,
  "花火|飞霄": 0.15,
  "飞霄|花火": 0.15,
  "花火|灵砂": 0.3,
  "灵砂|花火": 0.3,
  "花火|云璃": 0.3,
  "云璃|花火": 0.3,
  "花火|黑天鹅": 0.15,
  "黑天鹅|花火": 0.15,
  "黑塔|知更鸟": 0.15,
  "知更鸟|黑塔": 0.15,
  "黑塔|帕姆": 0.15,
  "帕姆|黑塔": 0.15,
  "黑塔|符玄": 0.65,
  "符玄|黑塔": 0.65,
  "黑塔|黄泉": 0.15,
  "黄泉|黑塔": 0.15,
  "黑塔|波提欧": 0.15,
  "波提欧|黑塔": 0.15,
  "黑塔|乱破": 0.15,
  "乱破|黑塔": 0.15,
  "黑塔|银枝": 0.15,
  "银枝|黑塔": 0.15,
  "黑塔|白露": 0.15,
  "白露|黑塔": 0.15,
  "黑塔|镜流": 0.15,
  "镜流|黑塔": 0.15,
  "黑塔|翡翠": 0.15,
  "翡翠|黑塔": 0.15,
  "黑塔|流萤": 0.15,
  "流萤|黑塔": 0.15,
  "黑塔|飞霄": 0.15,
  "飞霄|黑塔": 0.15,
  "黑塔|灵砂": 0.15,
  "灵砂|黑塔": 0.15,
  "黑塔|云璃": 0.15,
  "云璃|黑塔": 0.15,
  "黑塔|黑天鹅": 0.15,
  "黑天鹅|黑塔": 0.15,
  "知更鸟|帕姆": 0.15,
  "帕姆|知更鸟": 0.15,
  "知更鸟|符玄": 0.15,
  "符玄|知更鸟": 0.15,
  "知更鸟|黄泉": 0.15,
  "黄泉|知更鸟": 0.15,
  "知更鸟|乱破": 0.85,
  "乱破|知更鸟": 0.85,
  "知更鸟|银枝": 0.15,
  "银枝|知更鸟": 0.15,
  "知更鸟|白露": 0.15,
  "白露|知更鸟": 0.15,
  "知更鸟|镜流": 0.15,
  "镜流|知更鸟": 0.15,
  "知更鸟|阮·梅": 0.3,
  "阮·梅|知更鸟": 0.3,
  "知更鸟|螺丝咕姆": 0.3,
  "螺丝咕姆|知更鸟": 0.3,
  "知更鸟|飞霄": 0.85,
  "飞霄|知更鸟": 0.85,
  "知更鸟|灵砂": 0.85,
  "灵砂|知更鸟": 0.85,
  "知更鸟|云璃": 0.15,
  "云璃|知更鸟": 0.15,
  "知更鸟|黑天鹅": 0.65,
  "黑天鹅|知更鸟": 0.65,
  "帕姆|符玄": 0.15,
  "符玄|帕姆": 0.15,
  "帕姆|黄泉": 0.05,
  "黄泉|帕姆": 0.05,
  "帕姆|波提欧": 0.15,
  "波提欧|帕姆": 0.15,
  "帕姆|乱破": 0.15,
  "乱破|帕姆": 0.15,
  "帕姆|银枝": 0.15,
  "银枝|帕姆": 0.15,
  "帕姆|白露": 0.15,
  "白露|帕姆": 0.15,
  "帕姆|镜流": 0.15,
  "镜流|帕姆": 0.15,
  "帕姆|阮·梅": 0.15,
  "阮·梅|帕姆": 0.15,
  "帕姆|螺丝咕姆": 0.15,
  "螺丝咕姆|帕姆": 0.15,
  "帕姆|翡翠": 0.1,
  "翡翠|帕姆": 0.1,
  "帕姆|流萤": 0.15,
  "流萤|帕姆": 0.15,
  "帕姆|飞霄": 0.15,
  "飞霄|帕姆": 0.15,
  "帕姆|灵砂": 0.15,
  "灵砂|帕姆": 0.15,
  "帕姆|云璃": 0.15,
  "云璃|帕姆": 0.15,
  "帕姆|黑天鹅": 0.15,
  "黑天鹅|帕姆": 0.15,
  "符玄|黄泉": 0.15,
  "黄泉|符玄": 0.15,
  "符玄|波提欧": 0.15,
  "波提欧|符玄": 0.15,
  "符玄|乱破": 0.15,
  "乱破|符玄": 0.15,
  "符玄|银枝": 0.15,
  "银枝|符玄": 0.15,
  "符玄|白露": 0.65,
  "白露|符玄": 0.65,
  "符玄|镜流": 0.15,
  "镜流|符玄": 0.15,
  "符玄|阮·梅": 0.15,
  "阮·梅|符玄": 0.15,
  "符玄|螺丝咕姆": 0.15,
  "螺丝咕姆|符玄": 0.15,
  "符玄|翡翠": 0.15,
  "翡翠|符玄": 0.15,
  "符玄|流萤": 0.15,
  "流萤|符玄": 0.15,
  "符玄|云璃": 0.65,
  "云璃|符玄": 0.65,
  "符玄|黑天鹅": 0.15,
  "黑天鹅|符玄": 0.15,
  "黄泉|乱破": 0.85,
  "乱破|黄泉": 0.85,
  "黄泉|银枝": 0.15,
  "银枝|黄泉": 0.15,
  "黄泉|白露": 0.15,
  "白露|黄泉": 0.15,
  "黄泉|镜流": 0.15,
  "镜流|黄泉": 0.15,
  "黄泉|阮·梅": 0.15,
  "阮·梅|黄泉": 0.15,
  "黄泉|螺丝咕姆": 0.1,
  "螺丝咕姆|黄泉": 0.1,
  "黄泉|翡翠": 0.15,
  "翡翠|黄泉": 0.15,
  "黄泉|流萤": 0.3,
  "流萤|黄泉": 0.3,
  "黄泉|飞霄": 0.15,
  "飞霄|黄泉": 0.15,
  "黄泉|灵砂": 0.15,
  "灵砂|黄泉": 0.15,
  "黄泉|云璃": 0.15,
  "云璃|黄泉": 0.15,
  "波提欧|乱破": 0.85,
  "乱破|波提欧": 0.85,
  "波提欧|白露": 0.15,
  "白露|波提欧": 0.15,
  "波提欧|镜流": 0.1,
  "镜流|波提欧": 0.1,
  "波提欧|阮·梅": 0.15,
  "阮·梅|波提欧": 0.15,
  "波提欧|螺丝咕姆": 0.15,
  "螺丝咕姆|波提欧": 0.15,
  "波提欧|翡翠": 0.3,
  "翡翠|波提欧": 0.3,
  "波提欧|流萤": 0.15,
  "流萤|波提欧": 0.15,
  "波提欧|飞霄": 0.65,
  "飞霄|波提欧": 0.65,
  "波提欧|灵砂": 0.15,
  "灵砂|波提欧": 0.15,
  "波提欧|云璃": 0.15,
  "云璃|波提欧": 0.15,
  "乱破|银枝": 0.3,
  "银枝|乱破": 0.3,
  "乱破|白露": 0.85,
  "白露|乱破": 0.85,
  "乱破|镜流": 0.85,
  "镜流|乱破": 0.85,
  "乱破|阮·梅": 0.15,
  "阮·梅|乱破": 0.15,
  "乱破|螺丝咕姆": 0.15,
  "螺丝咕姆|乱破": 0.15,
  "乱破|翡翠": 0.3,
  "翡翠|乱破": 0.3,
  "乱破|流萤": 0.85,
  "流萤|乱破": 0.85,
  "乱破|飞霄": 0.85,
  "飞霄|乱破": 0.85,
  "乱破|灵砂": 0.85,
  "灵砂|乱破": 0.85,
  "乱破|云璃": 0.85,
  "云璃|乱破": 0.85,
  "乱破|黑天鹅": 0.85,
  "黑天鹅|乱破": 0.85,
  "银枝|白露": 0.15,
  "白露|银枝": 0.15,
  "银枝|镜流": 0.15,
  "镜流|银枝": 0.15,
  "银枝|阮·梅": 0.1,
  "阮·梅|银枝": 0.1,
  "银枝|螺丝咕姆": 0.15,
  "螺丝咕姆|银枝": 0.15,
  "银枝|翡翠": 0.15,
  "翡翠|银枝": 0.15,
  "银枝|流萤": 0.15,
  "流萤|银枝": 0.15,
  "银枝|飞霄": 0.15,
  "飞霄|银枝": 0.15,
  "银枝|灵砂": 0.15,
  "灵砂|银枝": 0.15,
  "银枝|云璃": 0.15,
  "云璃|银枝": 0.15,
  "银枝|黑天鹅": 0.15,
  "黑天鹅|银枝": 0.15,
  "白露|阮·梅": 0.15,
  "阮·梅|白露": 0.15,
  "白露|螺丝咕姆": 0.15,
  "螺丝咕姆|白露": 0.15,
  "白露|翡翠": 0.15,
  "翡翠|白露": 0.15,
  "白露|流萤": 0.15,
  "流萤|白露": 0.15,
  "白露|飞霄": 0.15,
  "飞霄|白露": 0.15,
  "白露|灵砂": 0.75,
  "灵砂|白露": 0.75,
  "白露|云璃": 0.65,
  "云璃|白露": 0.65,
  "白露|黑天鹅": 0.15,
  "黑天鹅|白露": 0.15,
  "镜流|阮·梅": 0.15,
  "阮·梅|镜流": 0.15,
  "镜流|螺丝咕姆": 0.15,
  "螺丝咕姆|镜流": 0.15,
  "镜流|翡翠": 0.15,
  "翡翠|镜流": 0.15,
  "镜流|流萤": 0.15,
  "流萤|镜流": 0.15,
  "镜流|飞霄": 0.15,
  "飞霄|镜流": 0.15,
  "镜流|灵砂": 0.15,
  "灵砂|镜流": 0.15,
  "镜流|云璃": 0.15,
  "云璃|镜流": 0.15,
  "镜流|黑天鹅": 0.15,
  "黑天鹅|镜流": 0.15,
  "阮·梅|翡翠": 0.15,
  "翡翠|阮·梅": 0.15,
  "阮·梅|流萤": 0.65,
  "流萤|阮·梅": 0.65,
  "阮·梅|飞霄": 0.15,
  "飞霄|阮·梅": 0.15,
  "阮·梅|灵砂": 0.65,
  "灵砂|阮·梅": 0.65,
  "阮·梅|云璃": 0.65,
  "云璃|阮·梅": 0.65,
  "阮·梅|黑天鹅": 0.65,
  "黑天鹅|阮·梅": 0.65,
  "螺丝咕姆|翡翠": 0.3,
  "翡翠|螺丝咕姆": 0.3,
  "螺丝咕姆|流萤": 0.15,
  "流萤|螺丝咕姆": 0.15,
  "螺丝咕姆|飞霄": 0.15,
  "飞霄|螺丝咕姆": 0.15,
  "螺丝咕姆|灵砂": 0.3,
  "灵砂|螺丝咕姆": 0.3,
  "螺丝咕姆|云璃": 0.15,
  "云璃|螺丝咕姆": 0.15,
  "螺丝咕姆|黑天鹅": 0.15,
  "黑天鹅|螺丝咕姆": 0.15,
  "翡翠|流萤": 0.15,
  "流萤|翡翠": 0.15,
  "翡翠|飞霄": 0.85,
  "飞霄|翡翠": 0.85,
  "翡翠|灵砂": 0.85,
  "灵砂|翡翠": 0.85,
  "翡翠|云璃": 0.15,
  "云璃|翡翠": 0.15,
  "翡翠|黑天鹅": 0.15,
  "黑天鹅|翡翠": 0.15,
  "流萤|飞霄": 0.15,
  "飞霄|流萤": 0.15,
  "流萤|灵砂": 0.65,
  "灵砂|流萤": 0.65,
  "流萤|云璃": 0.15,
  "云璃|流萤": 0.15,
  "飞霄|灵砂": 0.65,
  "灵砂|飞霄": 0.65,
  "飞霄|云璃": 0.85,
  "云璃|飞霄": 0.85,
  "飞霄|黑天鹅": 0.15,
  "黑天鹅|飞霄": 0.15,
  "灵砂|云璃": 0.85,
  "云璃|灵砂": 0.85,
  "灵砂|黑天鹅": 0.65,
  "黑天鹅|灵砂": 0.65,
  "云璃|黑天鹅": 0.15,
  "黑天鹅|云璃": 0.15,
  "青雀|砂金": 0.2,
  "青雀|黑塔": 0.4,
  "青雀|银枝": 0.1,
  "青雀|螺丝咕姆": 0.3,
  "青雀|飞霄": 0.15,
  "青雀|波提欧": 0.1,
  "青雀|素裳": 0.7,
  "青雀|云璃": 0.6,
  "青雀|丹恒": 0.75,
  "青雀|三月七": 0.7,
  "青雀|翡翠": 0.15,
  "青雀|景元": 0.65,
  "青雀|灵砂": 0.2,
  "青雀|姬子": 0.25,
  "青雀|符玄": 0.8,
  "青雀|黄泉": 0.1,
  "青雀|镜流": 0.1,
  "青雀|帕姆": 0.2,
  "青雀|乱破": 0.15,
  "青雀|桂乃芬": 0.3,
  "青雀|彦卿": 0.25,
  "青雀|白露": 0.4,
  "青雀|流萤": 0.2,
  "青雀|托帕": 0.15,
  "青雀|知更鸟": 0.1,
  "青雀|卡芙卡": 0.15,
  "青雀|花火": 0.25,
  "青雀|银狼": 0.3,
  "青雀|刃": 0.1,
  "青雀|黑天鹅": 0.15,
  "青雀|阮·梅": 0.2,
  "素裳|砂金": 0.1,
  "素裳|黑塔": 0.15,
  "素裳|银枝": 0.7,
  "素裳|螺丝咕姆": 0.1,
  "素裳|飞霄": 0.8,
  "素裳|青雀": 0.6,
  "素裳|波提欧": 0.2,
  "素裳|云璃": 0.75,
  "素裳|丹恒": 0.75,
  "素裳|三月七": 0.7,
  "素裳|翡翠": 0.1,
  "素裳|景元": 0.65,
  "素裳|灵砂": 0.15,
  "素裳|姬子": 0.25,
  "素裳|符玄": 0.6,
  "素裳|黄泉": 0.2,
  "素裳|镜流": 0.15,
  "素裳|帕姆": 0.1,
  "素裳|乱破": 0.25,
  "素裳|桂乃芬": 0.75,
  "素裳|彦卿": 0.65,
  "素裳|白露": 0.5,
  "素裳|流萤": 0.2,
  "素裳|托帕": 0.15,
  "素裳|知更鸟": 0.15,
  "素裳|卡芙卡": 0.1,
  "素裳|花火": 0.1,
  "素裳|银狼": 0.2,
  "素裳|刃": 0.25,
  "素裳|黑天鹅": 0.15,
  "素裳|阮·梅": 0.1,
  "桂乃芬|砂金": 0.2,
  "桂乃芬|黑塔": 0.1,
  "桂乃芬|银枝": 0.3,
  "桂乃芬|螺丝咕姆": 0.1,
  "桂乃芬|飞霄": 0.25,
  "桂乃芬|青雀": 0.7,
  "桂乃芬|波提欧": 0.15,
  "桂乃芬|素裳": 0.9,
  "桂乃芬|云璃": 0.2,
  "桂乃芬|丹恒": 0.3,
  "桂乃芬|三月七": 0.7,
  "桂乃芬|翡翠": 0.1,
  "桂乃芬|景元": 0.4,
  "桂乃芬|灵砂": 0.6,
  "桂乃芬|姬子": 0.5,
  "桂乃芬|符玄": 0.3,
  "桂乃芬|黄泉": 0.2,
  "桂乃芬|镜流": 0.15,
  "桂乃芬|帕姆": 0.3,
  "桂乃芬|乱破": 0.7,
  "桂乃芬|彦卿": 0.25,
  "桂乃芬|白露": 0.35,
  "桂乃芬|流萤": 0.4,
  "桂乃芬|托帕": 0.2,
  "桂乃芬|知更鸟": 0.2,
  "桂乃芬|卡芙卡": 0.15,
  "桂乃芬|花火": 0.25,
  "桂乃芬|银狼": 0.15,
  "桂乃芬|刃": 0.1,
  "桂乃芬|黑天鹅": 0.2,
  "桂乃芬|阮·梅": 0.15,
  "艾丝妲|刃": 0.1,
  "艾丝妲|花火": 0.15,
  "艾丝妲|桂乃芬": 0.2,
  "艾丝妲|桑博": 0.15,
  "艾丝妲|飞霄": 0.25,
  "艾丝妲|螺丝咕姆": 0.7,
  "艾丝妲|藿藿": 0.3,
  "艾丝妲|卡芙卡": 0.1,
  "艾丝妲|景元": 0.25,
  "艾丝妲|托帕": 0.75,
  "艾丝妲|翡翠": 0.65,
  "艾丝妲|镜流": 0.15,
  "艾丝妲|云璃": 0.2,
  "艾丝妲|青雀": 0.4,
  "艾丝妲|素裳": 0.3,
  "艾丝妲|灵砂": 0.35,
  "艾丝妲|黑天鹅": 0.15,
  "艾丝妲|银枝": 0.1,
  "艾丝妲|波提欧": 0.1,
  "艾丝妲|知更鸟": 0.2,
  "艾丝妲|乱破": 0.1,
  "艾丝妲|白露": 0.25,
  "艾丝妲|符玄": 0.3,
  "艾丝妲|黑塔": 0.7,
  "艾丝妲|姬子": 0.9,
  "艾丝妲|三月七": 0.65,
  "艾丝妲|帕姆": 0.75,
  "艾丝妲|丹恒": 0.6,
  "艾丝妲|流萤": 0.25,
  "艾丝妲|砂金": 0.15,
  "艾丝妲|银狼": 0.1,
  "艾丝妲|彦卿": 0.2,
  "艾丝妲|阮·梅": 0.2,
  "艾丝妲|黄泉": 0.1,
  "桑博|刃": 0.2,
  "桑博|花火": 0.7,
  "桑博|桂乃芬": 0.4,
  "桑博|艾丝妲": 0.3,
  "桑博|飞霄": 0.1,
  "桑博|螺丝咕姆": 0.1,
  "桑博|藿藿": 0.3,
  "桑博|卡芙卡": 0.6,
  "桑博|景元": 0.2,
  "桑博|托帕": 0.3,
  "桑博|翡翠": 0.25,
  "桑博|镜流": 0.1,
  "桑博|云璃": 0.15,
  "桑博|青雀": 0.35,
  "桑博|素裳": 0.2,
  "桑博|灵砂": 0.25,
  "桑博|黑天鹅": 0.2,
  "桑博|银枝": 0.1,
  "桑博|波提欧": 0.3,
  "桑博|知更鸟": 0.15,
  "桑博|乱破": 0.25,
  "桑博|白露": 0.1,
  "桑博|符玄": 0.1,
  "桑博|黑塔": 0.15,
  "桑博|姬子": 0.15,
  "桑博|三月七": 0.25,
  "桑博|帕姆": 0.05,
  "桑博|丹恒": 0.2,
  "桑博|流萤": 0.1,
  "桑博|砂金": 0.35,
  "桑博|银狼": 0.3,
  "桑博|彦卿": 0.1,
  "桑博|阮·梅": 0.1,
  "桑博|黄泉": 0.15,
  "藿藿|刃": 0.1,
  "藿藿|花火": 0.15,
  "藿藿|桂乃芬": 0.7,
  "藿藿|艾丝妲": 0.6,
  "藿藿|桑博": 0.2,
  "藿藿|飞霄": 0.3,
  "藿藿|螺丝咕姆": 0.25,
  "藿藿|卡芙卡": 0.1,
  "藿藿|景元": 0.75,
  "藿藿|托帕": 0.25,
  "藿藿|翡翠": 0.15,
  "藿藿|镜流": 0.2,
  "藿藿|云璃": 0.3,
  "藿藿|青雀": 0.4,
  "藿藿|素裳": 0.35,
  "藿藿|灵砂": 0.5,
  "藿藿|黑天鹅": 0.2,
  "藿藿|银枝": 0.15,
  "藿藿|波提欧": 0.1,
  "藿藿|知更鸟": 0.15,
  "藿藿|乱破": 0.1,
  "藿藿|白露": 0.7,
  "藿藿|符玄": 0.8,
  "藿藿|黑塔": 0.25,
  "藿藿|姬子": 0.25,
  "藿藿|三月七": 0.4,
  "藿藿|帕姆": 0.35,
  "藿藿|丹恒": 0.3,
  "藿藿|流萤": 0.15,
  "藿藿|砂金": 0.1,
  "藿藿|银狼": 0.1,
  "藿藿|彦卿": 0.2,
  "藿藿|阮·梅": 0.2,
  "藿藿|黄泉": 0.1,
  "真理医生|知更鸟": 0.2,
  "真理医生|阮·梅": 0.4,
  "真理医生|素裳": 0.1,
  "真理医生|刃": 0.1,
  "真理医生|银枝": 0.3,
  "真理医生|藿藿": 0.1,
  "真理医生|符玄": 0.2,
  "真理医生|帕姆": 0.1,
  "真理医生|砂金": 0.75,
  "真理医生|波提欧": 0.25,
  "真理医生|椒丘": 0.15,
  "真理医生|桂乃芬": 0.1,
  "真理医生|桑博": 0.2,
  "真理医生|花火": 0.3,
  "真理医生|丹恒": 0.4,
  "真理医生|乱破": 0.1,
  "真理医生|黑塔": 0.75,
  "真理医生|白露": 0.15,
  "真理医生|银狼": 0.25,
  "真理医生|螺丝咕姆": 0.7,
  "真理医生|姬子": 0.35,
  "真理医生|灵砂": 0.2,
  "真理医生|黄泉": 0.1,
  "真理医生|黑天鹅": 0.3,
  "真理医生|三月七": 0.1,
  "真理医生|翡翠": 0.3,
  "真理医生|彦卿": 0.2,
  "真理医生|镜流": 0.15,
  "真理医生|云璃": 0.1,
  "真理医生|貊泽": 0.1,
  "真理医生|托帕": 0.25,
  "真理医生|飞霄": 0.15,
  "真理医生|流萤": 0.1,
  "真理医生|卡芙卡": 0.2,
  "真理医生|景元": 0.3,
  "真理医生|艾丝妲": 0.4,
  "真理医生|青雀": 0.25,
  "椒丘|知更鸟": 0.15,
  "椒丘|阮·梅": 0.25,
  "椒丘|素裳": 0.1,
  "椒丘|刃": 0.2,
  "椒丘|银枝": 0.1,
  "椒丘|藿藿": 0.3,
  "椒丘|符玄": 0.35,
  "椒丘|帕姆": 0.15,
  "椒丘|砂金": 0.15,
  "椒丘|波提欧": 0.1,
  "椒丘|桂乃芬": 0.7,
  "椒丘|桑博": 0.25,
  "椒丘|花火": 0.2,
  "椒丘|丹恒": 0.1,
  "椒丘|乱破": 0.3,
  "椒丘|黑塔": 0.05,
  "椒丘|白露": 0.2,
  "椒丘|银狼": 0.4,
  "椒丘|螺丝咕姆": 0.3,
  "椒丘|姬子": 0.25,
  "椒丘|灵砂": 0.7,
  "椒丘|黄泉": 0.6,
  "椒丘|黑天鹅": 0.35,
  "椒丘|三月七": 0.15,
  "椒丘|翡翠": 0.75,
  "椒丘|真理医生": 0.25,
  "椒丘|彦卿": 0.15,
  "椒丘|镜流": 0.1,
  "椒丘|云璃": 0.2,
  "椒丘|貊泽": 0.65,
  "椒丘|托帕": 0.7,
  "椒丘|飞霄": 0.3,
  "椒丘|流萤": 0.2,
  "椒丘|卡芙卡": 0.3,
  "椒丘|景元": 0.7,
  "椒丘|艾丝妲": 0.4,
  "椒丘|青雀": 0.5,
  "貊泽|知更鸟": 0.15,
  "貊泽|阮·梅": 0.1,
  "貊泽|素裳": 0.25,
  "貊泽|刃": 0.05,
  "貊泽|银枝": 0.2,
  "貊泽|藿藿": 0.3,
  "貊泽|符玄": 0.1,
  "貊泽|帕姆": 0.35,
  "貊泽|砂金": 0.15,
  "貊泽|波提欧": 0.1,
  "貊泽|椒丘": 0.7,
  "貊泽|桂乃芬": 0.65,
  "貊泽|桑博": 0.2,
  "貊泽|花火": 0.25,
  "貊泽|丹恒": 0.1,
  "貊泽|乱破": 0.1,
  "貊泽|黑塔": 0.15,
  "貊泽|白露": 0.1,
  "貊泽|银狼": 0.25,
  "貊泽|螺丝咕姆": 0.2,
  "貊泽|姬子": 0.1,
  "貊泽|灵砂": 0.3,
  "貊泽|黄泉": 0.1,
  "貊泽|黑天鹅": 0.1,
  "貊泽|三月七": 0.15,
  "貊泽|翡翠": 0.75,
  "貊泽|真理医生": 0.1,
  "貊泽|彦卿": 0.2,
  "貊泽|镜流": 0.1,
  "貊泽|云璃": 0.25,
  "貊泽|托帕": 0.65,
  "貊泽|飞霄": 0.3,
  "貊泽|流萤": 0.2,
  "貊泽|卡芙卡": 0.1,
  "貊泽|景元": 0.3,
  "貊泽|艾丝妲": 0.25,
  "貊泽|青雀": 0.15
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
    adjusted_prob = base_prob * (0.7 + 0.3 * relevance)
    final_prob = min(adjusted_prob * random.uniform(0.9, 1.1), 1.0)
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
                    relation_desc = f"\n你与 {replied_to} 的关系：不太熟，但可以礼貌回应对方的话题。如果对方提出建议或帮助，应给予适当回应（如'谢谢'或'不必了'），不要完全无视。"
        
        # 获取流行语（仅在需要时调用一次，避免重复请求）
        if not hasattr(generate_comment, "trendy_words"):
            generate_comment.trendy_words = get_trendy_words()
        if not hasattr(generate_comment, "acg_words"):
            generate_comment.acg_words = get_acg_fandom_words()   # 新增
        
         # 从角色数据中获取流行语风格
        trendy_style = char_data.get("trendy_style", "")
        term_style = char_data.get("term_style", "")
        trendy_hint = ""
        if trendy_style and trendy_style != "不使用流行语":
            trendy_hint = f"\n【语言风格提示】你的流行语风格是：{trendy_style}。你可以适当使用一些当下流行的网络用语，比如“{generate_comment.trendy_words}”等，但请根据你的风格选择最合适的用语，不要改变你的核心性格。"
        term_hint = ""
        if term_style and term_style != "不使用":
            term_hint = f"\n【ACG/饭圈用语提示】你的用语风格是：{term_style}。你可以适当使用一些当下的ACG圈或饭圈用语，比如“{generate_comment.acg_words}”等，但不要过度，保持角色性格。"

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
        elif character == "黑塔":
            personality_constraint = "你是科学家，说话带学术感，但可以温和地表达观点，不必完全否定他人的感性描述。"
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
{trendy_hint}
{term_hint}

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



def get_avatar_filename(name):
    avatar_map = {
        "三月七": "march_seven.png",
        "丹恒": "dh.png",
        "姬子": "jizi.png",
        "景元": "jy.png",
        "彦卿": "yq.png",
        "砂金": "sj.png",
        "托帕": "topaz.png",
        "银狼": "silver_wolf.png",
        "卡芙卡": "kafuka-avatar.png",
        "刃": "ren-avatar.png",
        "花火": "huahuo-avatar.png",
        "黑塔": "heita-avatar.png",
        "知更鸟": "zhigengniao-avatar.png",
        "帕姆": "pamu-avatar.png",
        "符玄": "fuxuan-avatar.png",
        "开拓者":"trailblazer-avatar.png",
        "阮·梅":"rm.gif",
        "花火":"hanabi.png",
        "卡芙卡":"kafk.png",
        "黑塔":"herta.png",
        "知更鸟":"robin.png",
        "符玄":"fuxuan.png",
        "流萤":"firefly.png",
        "黄泉":"momo.png",
        "波提欧":"bto.png",
        "银枝":"yzh.png",
        "青雀":"qque.png"
    }
    return avatar_map.get(name, "default.png")

def _is_similar(text1, text2, threshold=0.6):
    """简单判断两段文本是否相似"""
    if text1 == text2:
        return True
    # 如果一段是另一段的子串
    if text1 in text2 or text2 in text1:
        return True
    # 计算公共前缀比例
    min_len = min(len(text1), len(text2))
    if min_len == 0:
        return False
    common = 0
    for i in range(min_len):
        if text1[i] == text2[i]:
            common += 1
        else:
            break
    return (common / min_len) > threshold

def generate_post(post_id, author, content, image_path,force_time=None):

    # 新增：记录每个角色已生成的评论内容（避免重复）
    role_comments_history = {}

    # 时间和地点
    if force_time:
        time_str = force_time
    else:
        time_hours = random.randint(1, 48)
        time_str = f"{time_hours}小时前" if time_hours < 24 else f"{time_hours//24}天前"
    
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
    # commenters = [char for char in ALL_CHARACTERS if char != author and will_interact(char, content, "comment")]
    # random.shuffle(commenters)
    # commenters = commenters[:random.randint(10, 12)]  # 2-5条评论
    
        # ========== 1. 正常筛选评论者 ==========
    normal_commenters = [char for char in ALL_CHARACTERS if char != author and will_interact(char, content, "comment")]
    random.shuffle(normal_commenters)
    normal_count = random.randint(10, 12)
    normal_commenters = normal_commenters[:normal_count]
    
    # ========== 2. 保底机制：低关系角色必定出现 ==========
    LOW_RELATION_THRESHOLD = 0.15  # 关系值 ≤ 0.15 视为低关系
    # 找出所有与作者关系 ≤ 0.15 的角色（且不是作者自己，且尚未在 normal_commenters 中）
    low_relation_chars = []
    for char in ALL_CHARACTERS:
        if char == author:
            continue
        rel = get_relationship(author, char)
        if rel <= LOW_RELATION_THRESHOLD and char not in normal_commenters:
            low_relation_chars.append(char)
    
    # 从低关系角色中随机抽取 1/3（向上取整，至少1个）
    guaranteed_commenters = []
    if low_relation_chars:
        guaranteed_count = max(1, len(low_relation_chars) // 3)
        guaranteed_commenters = random.sample(low_relation_chars, min(guaranteed_count, len(low_relation_chars)))
    
    # ========== 3. 合并评论者 ==========
    commenters = normal_commenters + guaranteed_commenters
    random.shuffle(commenters)  # 打乱顺序
    
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
        # 生成评论内容，最多重试3次避免重复
        comment_text = None
        for attempt in range(3):
            temp_text = generate_comment(commenter, content, context="", post_info=post_info)
            existing = role_comments_history.get(commenter, [])
            if not any(_is_similar(temp_text, old) for old in existing):
                comment_text = temp_text
                role_comments_history.setdefault(commenter, []).append(comment_text)
                break
        if comment_text is None:
            comment_text = generate_comment(commenter, content, context="", post_info=post_info)
            role_comments_history.setdefault(commenter, []).append(comment_text)


            # 只有托帕的评论才可能生成语音
        voice_file = None
        if commenter == "托帕":
            comment_id = f"{post_id}_{len(comments)}"
            voice_file = text_to_speech(comment_text, comment_id)

        comment = {
            "author": commenter,
            "content": comment_text,
            "time": f"{random.randint(1, 3)}小时前",
            "replies": [],
            "voice_url": voice_file,  # 托帕可能有语音，其他角色为 None
        }
        # 第一层回复
        first_level = []
        for replier in ALL_CHARACTERS:
            if replier in (commenter, author):
                continue
            if maybe_reply(commenter, comment_text, content, replier):
                # 生成回复内容，去重
                reply_content = None
                for attempt in range(3):
                    temp_reply = generate_comment(replier, content, f"正在回复 {commenter} 的评论：「{comment_text}」", post_info=post_info)
                    existing = role_comments_history.get(replier, [])
                    if not any(_is_similar(temp_reply, old) for old in existing):
                        reply_content = temp_reply
                        role_comments_history.setdefault(replier, []).append(reply_content)
                        break
                if reply_content is None:
                    reply_content = generate_comment(replier, content, f"正在回复 {commenter} 的评论：「{comment_text}」", post_info=post_info)
                    role_comments_history.setdefault(replier, []).append(reply_content)

                    # 只有托帕的回复才可能生成语音
                voice_file = None
                if replier == "托帕":
                    reply_id = f"{post_id}_{len(comments)}_{len(first_level)}"
                    voice_file = text_to_speech(reply_content, reply_id)
                
                first_level.append({
                    "author": replier,
                    "content": reply_content,
                    "time": f"{random.randint(1, 2)}小时前",
                    "replyTo": commenter,
                    "replies": [],
                    "voice_url": voice_file,
                })
        # 第二层回复
        for reply in first_level:
            second_count = 0
            max_second = random.randint(0, 1)
            for deeper in ALL_CHARACTERS:
                if second_count >= max_second:
                    break
                if deeper in (reply["author"], commenter, author):
                    continue
                if maybe_reply(reply["author"], reply["content"], content, deeper):
                    # 生成更深层回复，去重
                    deeper_content = None
                    for attempt in range(3):
                        temp_deeper = generate_comment(deeper, content, f"正在回复 {reply['author']} 的回复：「{reply['content']}」", post_info=post_info)
                        existing = role_comments_history.get(deeper, [])
                        if not any(_is_similar(temp_deeper, old) for old in existing):
                            deeper_content = temp_deeper
                            role_comments_history.setdefault(deeper, []).append(deeper_content)
                            break
                    if deeper_content is None:
                        deeper_content = generate_comment(deeper, content, f"正在回复 {reply['author']} 的回复：「{reply['content']}」", post_info=post_info)
                        role_comments_history.setdefault(deeper, []).append(deeper_content)
                    
                    reply["replies"].append({
                        "author": deeper,
                        "content": deeper_content,
                        "time": f"{random.randint(1, 2)}小时前",
                        "replyTo": reply["author"],
                        "replies": []
                    })
                    second_count += 1
        comment["replies"] = first_level
        comments.append(comment)

    # 在 comments 列表生成后，决定是否插入广告评论
    AD_PROBABILITY = 0.3  # 30% 概率出现广告
    if random.random() < AD_PROBABILITY:
        ad_comment = generate_ad_comment(content, post_info)
        # 随机位置插入（比如在 0 到 len(comments) 之间，或者固定在最前面）
        insert_pos = random.randint(0, len(comments))
        comments.insert(insert_pos, ad_comment)
    
    # 表情反应
    reactions = []
    # 丰富的表情池
    reaction_emojis = [
    "👍", "❤️", "😂", "😮", "😢", "😡", "👎",          # 基础互动
    "🎉", "🔥", "🍗", "🍕", "🍺", "🎸", "💯",      # 庆祝/食物
    "🤣", "😎", "🤔", "😴", "😭", "🥺", "😱", "🤯",      # 表情包
    "👏", "🙌", "💪", "🫶", "👀", "🤝", "💔", "❓",      # 动作/疑问
    "⭐", "🌟", "⚡", "💎", "🏆", "🚀",        # 特殊符号
    "🐱"]
    if likes:
        # 确定要生成的表情种类数（至少 7 种，最多不超过表情池的 70%，且不超过 15 种）
        max_kinds = min(len(reaction_emojis), 30)
        min_kinds = min(20, max_kinds)
        # 根据点赞数决定种类数，点赞越多种类越多
        num_kinds = min(max_kinds, max(min_kinds, len(likes) // 2))
        # 随机选取不重复的表情
        chosen_emojis = random.sample(reaction_emojis, num_kinds)
        for emoji in chosen_emojis:
            # 每个表情的计数随机在 1 到点赞数之间
            count = random.randint(1, len(likes))
            reactions.append({"emoji": emoji, "count": count})
    else:
        reactions = []
    
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


def get_random_post_template():
    post = random.choice(POST_TEMPLATES)
    return post["author"], post["content"], post["image"]

def generate_ad_comment(post_content, post_info=None):
    """
    生成一条广告评论，内容与朋友圈文案相关
    返回格式与普通评论相同
    """
    # 随机选择来源类型
    source_type = random.choices(
        list(AD_SOURCES.keys()),
        weights=[v["weight"] for v in AD_SOURCES.values()]
    )[0]
    
    if source_type == "role":
        author = random.choice(AD_SOURCES["role"]["characters"])
        avatar = get_avatar_filename(author)
        # 角色广告提示
        context = f"你是{author}，请为你的公司/产品/理念发一条软广，与朋友圈内容相关。"
    elif source_type == "official":
        author = random.choice(AD_SOURCES["official"]["names"])
        avatar = "images/avatars/official.png"  # 统一官方头像，也可单独配置
        context = f"你是崩铁世界观中的官方机构{author}，请发一条推广文案，与朋友圈内容相关。"
    else:
        author = random.choice(AD_SOURCES["random_user"]["names"])
        avatar = "images/avatars/random.png"  # 默认头像
        context = f"你是普通用户{author}，正在刷朋友圈，看到这条动态后随手发了一条广告（可能是自己恰饭或推荐），内容要与朋友圈相关。"
    
    # 构建广告生成 prompt
    scene = ""
    if post_info:
        scene = f"发布者：{post_info.get('author', '未知')}\n地点：{post_info.get('location', '某处')}\n时间：{post_info.get('time', '某个时间')}\n内容：{post_content}"
    else:
        scene = f"内容：{post_content}"
    
    prompt = f"""你需要在《崩坏：星穹铁道》世界观下，生成一条广告评论。

{context}

当前朋友圈场景：
{scene}

要求：
1. 广告评论长度 15-40 字。
2. 广告必须与朋友圈内容相关（如蛋糕动态推荐甜点店，摸鱼动态推荐放松服务）。
3. 语气要符合来源身份（官方机构正式，陌生人随意，角色有个性）。
4. 直接输出评论内容，不要加引号。

请生成广告评论："""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        comment_text = response.choices[0].message.content.strip()
        comment_text = comment_text.encode('utf-8', errors='ignore').decode('utf-8')
        if len(comment_text) < 5:
            raise ValueError("生成过短")
    except Exception:
        # 降级为默认广告文案
        comment_text = "精彩推荐，点击查看详情～"
    
    return {
        "author": author,
        "avatar": avatar,
        "content": comment_text,
        "time": "刚刚",  # 广告一般显示为最新时间
        "replies": []
    }


# ========== 主程序（增量更新版） ==========
if __name__ == "__main__":
    # 1. 加载已有朋友圈数据
    existing_posts = []
    existing_ids = set()
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_posts = existing_data.get("posts", [])
            existing_ids = {post["id"] for post in existing_posts}
        print(f"已加载 {len(existing_posts)} 条现有朋友圈")
    except (FileNotFoundError, json.JSONDecodeError):
        print("未找到现有 data.json 或文件内容无效，将全量生成")
        existing_posts = []
        existing_ids = set()
    
    # 2. 加载待生成的朋友圈列表
    with open("posts.json", "r", encoding="utf-8") as f:
        POST_LIST = json.load(f)
    
    # 3. 筛选出尚未生成的新动态
    new_posts = [post for post in POST_LIST if post["id"] not in existing_ids]
    
    if not new_posts:
        print("没有新的朋友圈需要生成，退出。")
        exit(0)
    
    print(f"发现 {len(new_posts)} 条新朋友圈，开始生成...")
    
    # 4. 生成新动态
    all_posts = existing_posts.copy()
    for i, post in enumerate(new_posts, 1):
        author = post["author"]
        content = post["content"]
        image = post["image"]
        post_id = post["id"]
        print(f"生成第 {i}/{len(new_posts)} 条: {author} - {content[:20]}...")
        post_data = generate_post(post_id, author, content, image)
        all_posts.append(post_data)
        print(f"  完成第 {i} 条")
    
    # 5. 保存
    output = {"posts": all_posts}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完成！共 {len(all_posts)} 条朋友圈，新增 {len(new_posts)} 条")