#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星穹铁道 Wiki 爬虫 - 以“托帕”为关键词搜索并抓取所有相关页面文本
使用 MediaWiki API + BeautifulSoup
"""

import requests
import time
import re
from bs4 import BeautifulSoup

# BiliWiki 配置
WIKI_API = "https://wiki.biligame.com/sr/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://wiki.biligame.com/sr/"
}

def search_pages(keyword, limit=50):
    """搜索包含关键词的页面，返回页面标题列表"""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": keyword,
        "srlimit": limit,
        "format": "json",
        "utf8": 1
    }
    resp = requests.get(WIKI_API, params=params, headers=HEADERS)
    data = resp.json()
    pages = []
    for result in data.get("query", {}).get("search", []):
        pages.append(result["title"])
    return pages

def get_page_content(title):
    """获取单个页面的完整HTML内容，并提取纯文本"""
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text",
        "utf8": 1
    }
    resp = requests.get(WIKI_API, params=params, headers=HEADERS)
    data = resp.json()
    html = data.get("parse", {}).get("text", {}).get("*", "")
    if not html:
        return ""
    
    # 用 BeautifulSoup 提取文本
    soup = BeautifulSoup(html, "html.parser")
    
    # 移除不需要的标签（表格、图片、编辑按钮等）
    for tag in soup(["table", ".image", ".editlink", "script", "style", "nav", "aside"]):
        tag.decompose()
    
    # 获取文本，清理空白行
    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)
    return clean_text

def save_all_text(pages, output_file="topaz_all_wiki.txt"):
    """保存所有页面的文本到文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"托帕相关 Wiki 页面抓取\n")
        f.write(f"关键词：托帕 | 页面数量：{len(pages)}\n")
        f.write("=" * 80 + "\n\n")
        
        for idx, title in enumerate(pages, 1):
            print(f"正在抓取 ({idx}/{len(pages)}): {title}")
            content = get_page_content(title)
            f.write(f"【页面标题】{title}\n")
            f.write(f"{content}\n")
            f.write("\n" + "-" * 50 + "\n\n")
            time.sleep(0.5)  # 礼貌延时，避免触发反爬
    
    print(f"所有内容已保存到 {output_file}")

def main():
    keyword = "托帕"
    print(f"正在搜索关键词「{keyword}」...")
    pages = search_pages(keyword)
    print(f"找到 {len(pages)} 个相关页面：")
    for p in pages:
        print(f"  - {p}")
    
    if not pages:
        print("未找到任何页面，请检查网络或关键词。")
        return
    
    save_all_text(pages)

if __name__ == "__main__":
    main()