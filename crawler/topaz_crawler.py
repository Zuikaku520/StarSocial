#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
星穹铁道 - 托帕数据爬虫
目标：收集托帕的官方公开文本（角色故事、语音、短信、光锥等）
数据源：灰机Wiki (https://hsr.huijiwiki.com)
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json

# 托帕的Wiki页面URL（灰机Wiki）
TOPAP_URL = "https://hsr.huijiwiki.com/wiki/%E6%89%98%E5%B8%95"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_page(url):
    """获取页面HTML"""
    resp = requests.get(url, headers=HEADERS)
    resp.encoding = 'utf-8'
    return resp.text

def extract_character_stories(soup):
    """提取角色故事（角色详情中的故事章节）"""
    stories = []
    # 查找角色故事所在的section
    story_section = soup.find('div', {'id': '角色故事'})
    if not story_section:
        # 尝试其他可能的选择器
        story_section = soup.find('h2', string=re.compile(r'角色故事'))
        if story_section:
            story_section = story_section.find_parent('div')
    if story_section:
        # 获取所有故事段落
        paragraphs = story_section.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # 过滤太短的行
                stories.append(text)
    return stories

def extract_voice_lines(soup):
    """提取语音列表（通常是表格）"""
    voices = []
    voice_table = soup.find('table', class_='wikitable')
    if not voice_table:
        voice_table = soup.find('table', attrs={'class': re.compile(r'voice')})
    if voice_table:
        rows = voice_table.find_all('tr')
        for row in rows[1:]:  # 跳过表头
            cells = row.find_all('td')
            if len(cells) >= 2:
                title = cells[0].get_text(strip=True)
                text = cells[1].get_text(strip=True)
                if title and text:
                    voices.append(f"{title}：{text}")
    return voices

def extract_messages(soup):
    """提取短信记录（如果页面有）"""
    messages = []
    msg_section = soup.find('div', {'id': '短信'})
    if not msg_section:
        msg_section = soup.find('h2', string=re.compile(r'短信'))
        if msg_section:
            msg_section = msg_section.find_parent('div')
    if msg_section:
        # 短信通常以对话形式呈现
        msg_items = msg_section.find_all('div', class_='message')
        if not msg_items:
            # 尝试普通段落
            msg_items = msg_section.find_all('p')
        for item in msg_items:
            text = item.get_text(strip=True)
            if text and ('托帕' in text or '开拓者' in text):
                messages.append(text)
    return messages

def extract_lightcone_text(soup):
    """提取光锥文本（如果托帕有专属光锥）"""
    lc_text = []
    lc_section = soup.find('div', {'id': '光锥'})
    if not lc_section:
        lc_section = soup.find('h2', string=re.compile(r'光锥'))
        if lc_section:
            lc_section = lc_section.find_parent('div')
    if lc_section:
        paragraphs = lc_section.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                lc_text.append(text)
    return lc_text

def extract_other_info(soup):
    """提取简介、其他描述等"""
    other = []
    # 简介
    intro = soup.find('div', class_='character-intro')
    if intro:
        other.append(intro.get_text(strip=True))
    # 基本信息表
    info_table = soup.find('table', class_='infobox')
    if info_table:
        rows = info_table.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.get_text(strip=True)
                value = td.get_text(strip=True)
                if key and value:
                    other.append(f"{key}：{value}")
    return other

def save_data(data, filename="topaz_data.txt"):
    """保存数据到文本文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("托帕官方数据收集（灰机Wiki）\n")
        f.write("=" * 60 + "\n\n")
        
        if data.get('stories'):
            f.write("【角色故事】\n")
            for story in data['stories']:
                f.write(story + "\n\n")
        
        if data.get('voices'):
            f.write("【语音列表】\n")
            for voice in data['voices']:
                f.write(voice + "\n")
            f.write("\n")
        
        if data.get('messages'):
            f.write("【短信记录】\n")
            for msg in data['messages']:
                f.write(msg + "\n")
            f.write("\n")
        
        if data.get('lightcone'):
            f.write("【光锥文本】\n")
            for lc in data['lightcone']:
                f.write(lc + "\n")
            f.write("\n")
        
        if data.get('other'):
            f.write("【其他信息】\n")
            for info in data['other']:
                f.write(info + "\n")
    print(f"数据已保存到 {filename}")

def main():
    print("正在获取托帕页面...")
    html = fetch_page(TOPAP_URL)
    soup = BeautifulSoup(html, 'html.parser')
    
    data = {}
    print("提取角色故事...")
    data['stories'] = extract_character_stories(soup)
    print("提取语音列表...")
    data['voices'] = extract_voice_lines(soup)
    print("提取短信记录...")
    data['messages'] = extract_messages(soup)
    print("提取光锥文本...")
    data['lightcone'] = extract_lightcone_text(soup)
    print("提取其他信息...")
    data['other'] = extract_other_info(soup)
    
    save_data(data)
    print("完成！")

if __name__ == "__main__":
    main()