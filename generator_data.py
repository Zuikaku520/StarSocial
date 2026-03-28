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
       "三月七|丹恒": 0.95,
  "三月七|姬子": 0.85,
  "三月七|帕姆": 0.75,
  "丹恒|刃": 0.9,
  "丹恒|景元": 0.85,
  "丹恒|三月七": 0.8,
  "姬子|三月七": 0.8,
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
  "黑塔|螺丝咕姆": 0.9,
  "黑塔|阮·梅": 0.85,
  "知更鸟|砂金": 0.65,
  "帕姆|姬子": 0.85,
  "帕姆|三月七": 0.75,
  "符玄|景元": 0.9,
  "符玄|彦卿": 0.7,
  "黄泉|花火": 0.75,
  "黄泉|砂金": 0.7,
  "黄泉|银狼": 0.65,
  "波提欧|黄泉": 0.9,
  "波提欧|砂金": 0.75,
  "波提欧|知更鸟": 0.6,
  "银枝|波提欧": 0.75,
  "白露|丹恒": 0.9,
  "白露|景元": 0.85,
  "白露|彦卿": 0.75,
  "白露|符玄": 0.65,
  "镜流|丹恒": 0.95,
  "镜流|刃": 0.9,
  "镜流|景元": 0.85,
  "镜流|彦卿": 0.7,
  "阮·梅|黑塔": 0.9,
  "阮·梅|螺丝咕姆": 0.85,
  "螺丝咕姆|黑塔": 0.9,
  "螺丝咕姆|阮·梅": 0.75,
  "翡翠|砂金": 0.9,
  "翡翠|托帕": 0.75,
  "翡翠|知更鸟": 0.65,
  "流萤|托帕": 0.2,
  "流萤|花火": 0.15,
  "流萤|帕姆": 0.3,
  "流萤|卡芙卡": 0.9,
  "流萤|刃": 0.4,
  "流萤|白露": 0.25,
  "流萤|阮·梅": 0.7,
  "流萤|波提欧": 0.1,
  "流萤|景元": 0.15,
  "流萤|砂金": 0.1,
  "流萤|翡翠": 0.1,
  "流萤|姬子": 0.25,
  "流萤|丹恒": 0.2,
  "流萤|银枝": 0.15,
  "流萤|黄泉": 0.3,
  "流萤|螺丝咕姆": 0.35,
  "流萤|符玄": 0.2,
  "流萤|银狼": 0.9,
  "流萤|知更鸟": 0.7,
  "流萤|乱破": 0.1,
  "流萤|彦卿": 0.15,
  "流萤|三月七": 0.4,
  "流萤|黑塔": 0.25,
  "流萤|镜流": 0.3,
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
  "三月七|黄泉": 0.35,
  "黄泉|三月七": 0.35,
  "三月七|波提欧": 0.15,
  "波提欧|三月七": 0.15,
  "三月七|乱破": 0.15,
  "乱破|三月七": 0.15,
  "三月七|银枝": 0.25,
  "银枝|三月七": 0.25,
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
  "姬子|景元": 0.3,
  "景元|姬子": 0.3,
  "姬子|彦卿": 0.15,
  "彦卿|姬子": 0.15,
  "姬子|砂金": 0.15,
  "砂金|姬子": 0.15,
  "姬子|银狼": 0.35,
  "银狼|姬子": 0.35,
  "姬子|卡芙卡": 0.3,
  "卡芙卡|姬子": 0.3,
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
  "姬子|乱破": 0.1,
  "乱破|姬子": 0.1,
  "姬子|银枝": 0.15,
  "银枝|姬子": 0.15,
  "姬子|白露": 0.25,
  "白露|姬子": 0.25,
  "姬子|镜流": 0.15,
  "镜流|姬子": 0.15,
  "姬子|阮·梅": 0.35,
  "阮·梅|姬子": 0.35,
  "姬子|螺丝咕姆": 0.35,
  "螺丝咕姆|姬子": 0.35,
  "姬子|翡翠": 0.15,
  "翡翠|姬子": 0.15,
  "景元|砂金": 0.25,
  "砂金|景元": 0.25,
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
  "彦卿|阮·梅": 0.15,
  "阮·梅|彦卿": 0.15,
  "彦卿|螺丝咕姆": 0.15,
  "螺丝咕姆|彦卿": 0.15,
  "彦卿|翡翠": 0.15,
  "翡翠|彦卿": 0.15,
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
  "砂金|符玄": 0.15,
  "符玄|砂金": 0.15,
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
  "卡芙卡|花火": 0.3,
  "花火|卡芙卡": 0.3,
  "卡芙卡|黑塔": 0.15,
  "黑塔|卡芙卡": 0.15,
  "卡芙卡|知更鸟": 0.15,
  "知更鸟|卡芙卡": 0.15,
  "卡芙卡|帕姆": 0.15,
  "帕姆|卡芙卡": 0.15,
  "卡芙卡|符玄": 0.15,
  "符玄|卡芙卡": 0.15,
  "卡芙卡|黄泉": 0.25,
  "黄泉|卡芙卡": 0.25,
  "卡芙卡|波提欧": 0.15,
  "波提欧|卡芙卡": 0.15,
  "卡芙卡|乱破": 0.85,
  "乱破|卡芙卡": 0.85,
  "卡芙卡|银枝": 0.15,
  "银枝|卡芙卡": 0.15,
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
  "刃|白露": 0.85,
  "白露|刃": 0.85,
  "刃|阮·梅": 0.15,
  "阮·梅|刃": 0.15,
  "刃|螺丝咕姆": 0.05,
  "螺丝咕姆|刃": 0.05,
  "刃|翡翠": 0.15,
  "翡翠|刃": 0.15,
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
  "知更鸟|阮·梅": 0.15,
  "阮·梅|知更鸟": 0.15,
  "知更鸟|螺丝咕姆": 0.35,
  "螺丝咕姆|知更鸟": 0.35,
  "帕姆|符玄": 0.35,
  "符玄|帕姆": 0.35,
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
  "符玄|黄泉": 0.15,
  "黄泉|符玄": 0.15,
  "符玄|波提欧": 0.15,
  "波提欧|符玄": 0.15,
  "符玄|乱破": 0.15,
  "乱破|符玄": 0.15,
  "符玄|银枝": 0.15,
  "银枝|符玄": 0.15,
  "符玄|镜流": 0.65,
  "镜流|符玄": 0.65,
  "符玄|阮·梅": 0.15,
  "阮·梅|符玄": 0.15,
  "符玄|螺丝咕姆": 0.15,
  "螺丝咕姆|符玄": 0.15,
  "符玄|翡翠": 0.15,
  "翡翠|符玄": 0.15,
  "黄泉|乱破": 0.15,
  "乱破|黄泉": 0.15,
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
  "乱破|银枝": 0.3,
  "银枝|乱破": 0.3,
  "乱破|白露": 0.65,
  "白露|乱破": 0.65,
  "乱破|镜流": 0.85,
  "镜流|乱破": 0.85,
  "乱破|阮·梅": 0.15,
  "阮·梅|乱破": 0.15,
  "乱破|螺丝咕姆": 0.15,
  "螺丝咕姆|乱破": 0.15,
  "乱破|翡翠": 0.3,
  "翡翠|乱破": 0.3,
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
  "白露|镜流": 0.15,
  "镜流|白露": 0.15,
  "白露|阮·梅": 0.15,
  "阮·梅|白露": 0.15,
  "白露|螺丝咕姆": 0.15,
  "螺丝咕姆|白露": 0.15,
  "白露|翡翠": 0.15,
  "翡翠|白露": 0.15,
  "镜流|阮·梅": 0.15,
  "阮·梅|镜流": 0.15,
  "镜流|螺丝咕姆": 0.05,
  "螺丝咕姆|镜流": 0.05,
  "镜流|翡翠": 0.15,
  "翡翠|镜流": 0.15,
  "阮·梅|翡翠": 0.15,
  "翡翠|阮·梅": 0.15,
  "螺丝咕姆|翡翠": 0.3,
  "翡翠|螺丝咕姆": 0.3
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
        "托帕": "topaz.png",
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
# POST_TEMPLATES = [
#     ("三月七", "帕姆今天超厉害！做了一整个蛋糕！！", "images/cake.jpg"),
#     ("丹恒", "智库新到了一批古籍。", "images/books.jpg"),
#     ("景元", "难得清闲一日，终于可以摸鱼了。", "images/jingyuan_rest.jpg"),
#     ("砂金", "今天运气不错，小赚一笔。", "images/gamble.jpg"),
#     ("银狼", "通宵打完新游戏了，爽！", "images/gaming.jpg"),
#     ("姬子", "新烘焙的咖啡豆，香味很特别。", "images/coffee.jpg"),
#     ("花火", "嘻嘻，今天二相乐园又有新节目啦！🎪", "images/huahuo_show.jpg"),
#     ("托帕", "星际和平公司季度报告完成。", "images/report.jpg"),
#     ("彦卿", "今日剑术练习完成！将军夸我了！", "images/sword.jpg"),
#     ("帕姆", "列车清洁日！谁都不许乱扔垃圾！", "images/pam_clean.jpg"),
# ]

# def get_random_post_template():
#     return random.choice(POST_TEMPLATES)

def get_random_post_template():
    post = random.choice(POST_TEMPLATES)
    return post["author"], post["content"], post["image"]

# ========== 主程序 ==========
# if __name__ == "__main__":
#     NUM_POSTS = random.randint(10, 15)
#     print(f"开始生成 {NUM_POSTS} 条朋友圈...")
#     all_posts = []
#     for i in range(1, NUM_POSTS + 1):
#         author, content, image = get_random_post_template()
#         print(f"生成第 {i}/{NUM_POSTS} 条: {author} - {content[:20]}...")
#         post = generate_post(i, author, content, image)
#         all_posts.append(post)
#         print(f"  完成第 {i} 条")
#     output = {"posts": all_posts}
#     with open("data.json", "w", encoding="utf-8") as f:
#         json.dump(output, f, ensure_ascii=False, indent=2)
#     print(f"\n✅ 完成！共 {len(all_posts)} 条朋友圈，保存到 data.json")

# ========== 主程序 ==========
if __name__ == "__main__":
    # 从 posts.json 读取，有多少条就生成多少条
    with open("posts.json", "r", encoding="utf-8") as f:
        POST_LIST = json.load(f)
    
    print(f"开始生成 {len(POST_LIST)} 条朋友圈...")
    all_posts = []
    for i, post in enumerate(POST_LIST, 1):
        author = post["author"]
        content = post["content"]
        image = post["image"]
        print(f"生成第 {i}/{len(POST_LIST)} 条: {author} - {content[:20]}...")
        post_data = generate_post(i, author, content, image)
        all_posts.append(post_data)
        print(f"  完成第 {i} 条")
    
    output = {"posts": all_posts}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完成！共 {len(all_posts)} 条朋友圈，保存到 data.json")