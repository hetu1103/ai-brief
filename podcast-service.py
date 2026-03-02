#!/usr/bin/env python3
"""
AI简报播客转换服务
使用edge-tts实现真实的文本转语音功能
"""

import os
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

# 安装依赖：pip install edge-tts beautifulsoup4


class PodcastGenerator:
    """播客生成器 - 使用edge-tts实现真实的TTS"""

    def __init__(self, output_dir="podcasts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 中文语音配置
        self.voice_options = {
            'female': 'zh-CN-XiaoxiaoNeural',  # 女声（温柔）
            'male': 'zh-CN-YunyangNeural',     # 男声
            'news': 'zh-CN-XiaoyiNeural',      # 新闻播报风格
        }
        self.default_voice = self.voice_options['news']

    def check_edge_tts(self):
        """检查edge-tts是否已安装"""
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def extract_content_from_html(self, html_file):
        """从HTML文件中提取简报内容"""
        print("📖 正在解析HTML文件...")

        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 提取标题和日期
        title_elem = soup.find('h1')
        date_elem = soup.find(class_='date')

        content = {
            'title': title_elem.text.strip() if title_elem else 'AI简报',
            'date': date_elem.text.strip() if date_elem else datetime.now().strftime('%Y年%m月%d日'),
            'sections': []
        }

        # 提取各个板块
        sections = soup.find_all('section')
        for section in sections:
            section_title = section.find(class_='section-title')
            if not section_title:
                continue

            section_data = {
                'title': section_title.get_text(strip=True),
                'news': []
            }

            news_items = section.find_all('div', class_='news-item')
            for item in news_items:
                title_elem = item.find(class_='news-title')
                news_content = item.find(class_='news-content')
                insight = item.find(class_='insight')

                # 清理文本，移除多余的空白
                def clean_text(elem):
                    if elem:
                        text = elem.get_text(separator=' ', strip=True)
                        # 移除列表符号等
                        text = text.replace('•', '').replace('·', '')
                        # 合并多个空格
                        text = ' '.join(text.split())
                        return text
                    return ''

                news_data = {
                    'title': clean_text(title_elem),
                    'content': clean_text(news_content),
                    'insight': clean_text(insight)
                }

                section_data['news'].append(news_data)

            content['sections'].append(section_data)

        print(f"✅ 提取到 {len(content['sections'])} 个板块")
        return content

    def format_script(self, content):
        """格式化为播客脚本 - 优化口语化表达"""
        print("📝 正在生成播客脚本...")

        script = f"大家好，欢迎收听{content['title']}，{content['date']}。\n\n"
        script += "今天的重要资讯如下。\n\n"

        for idx, section in enumerate(content['sections'], 1):
            # 跳过统计卡片，只关注新闻板块
            if '速览' in section['title']:
                script += f"【{section['title']}】\n\n"
                # 只读前2条最重要的
                for news in section['news'][:2]:
                    if news['title']:
                        script += f"{news['title']}。"
                        if news['insight']:
                            # 简化insight
                            insight = news['insight'].replace('潜在影响：', '').replace('核心判断：', '')
                            script += f" {insight[:100]}。"
                        script += "\n\n"
                script += "\n"
                continue

            script += f"【{section['title']}】\n\n"

            # 每个板块读2-3条
            for news in section['news'][:3]:
                if not news['title']:
                    continue

                script += f"{news['title']}。\n"

                # 内容简化，只保留关键信息
                if news['content']:
                    # 移除HTML标签和特殊字符
                    content_text = news['content']
                    # 截取前面部分
                    if len(content_text) > 150:
                        content_text = content_text[:150] + "。"
                    script += f"{content_text}\n"

                # 洞察/观点
                if news['insight']:
                    insight = news['insight']
                    # 移除标签
                    for label in ['潜在影响：', '核心判断：', '策略转变：', '行业影响：', '关键变化：', '核心观点：', '投资建议：']:
                        insight = insight.replace(label, '')
                    if len(insight) > 100:
                        insight = insight[:100] + "。"
                    script += f"{insight}\n"

                script += "\n"

            script += "\n"

        # 结尾
        script += "以上就是今天AI简报的全部内容，感谢收听，我们下期再见。"

        print(f"✅ 脚本生成完成，共 {len(script)} 字符")
        return script

    async def generate_podcast_edge_tts(self, script, output_filename=None, voice=None):
        """使用edge-tts生成播客音频

        Args:
            script: 播客脚本文本
            output_filename: 输出文件名（可选）
            voice: 语音类型（可选）

        Returns:
            生成的音频文件路径
        """
        if not self.check_edge_tts():
            print("❌ edge-tts未安装")
            print("📦 请运行: pip install edge-tts")
            return None

        import edge_tts

        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ai_brief_{timestamp}.mp3"

        output_path = self.output_dir / output_filename

        if voice is None:
            voice = self.default_voice

        print(f"🎙️  正在生成音频...")
        print(f"   语音: {voice}")
        print(f"   文件: {output_path}")

        try:
            # 创建TTS对象
            communicate = edge_tts.Communicate(script, voice)

            # 保存音频
            await communicate.save(str(output_path))

            print(f"✅ 音频生成成功!")
            print(f"📁 文件位置: {output_path}")

            # 获取文件大小
            file_size = output_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            print(f"📊 文件大小: {size_mb:.2f} MB")

            return str(output_path)

        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return None

    def generate_podcast_pytsx3(self, script, output_filename=None):
        """使用pyttsx3生成播客音频（离线方案）

        Args:
            script: 播客脚本文本
            output_filename: 输出文件名（可选）

        Returns:
            生成的音频文件路径
        """
        try:
            import pyttsx3
        except ImportError:
            print("❌ pyttsx3未安装")
            print("📦 请运行: pip install pyttsx3")
            return None

        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ai_brief_{timestamp}.mp3"

        output_path = self.output_dir / output_filename

        print(f"🎙️  正在生成音频（离线模式）...")
        print(f"   文件: {output_path}")

        try:
            # 创建TTS引擎
            engine = pyttsx3.init()

            # 设置中文语音属性
            engine.setProperty('rate', 150)    # 语速
            engine.setProperty('volume', 1.0)  # 音量

            # 尝试设置中文语音
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'zh' in voice.languages[0].lower():
                    engine.setProperty('voice', voice.id)
                    break

            # 保存音频
            engine.save_to_file(script, str(output_path))
            engine.runAndWait()

            print(f"✅ 音频生成成功!")
            print(f"📁 文件位置: {output_path}")

            return str(output_path)

        except Exception as e:
            print(f"❌ 音频生成失败: {e}")
            return None

    def generate_podcast(self, script, output_filename=None, method='edge', voice=None):
        """生成播客音频文件（自动选择最佳方案）

        Args:
            script: 播客脚本文本
            output_filename: 输出文件名（可选）
            method: TTS方法 ('edge', 'pyttsx3', 或 'auto')
            voice: 语音类型（仅edge-tts支持）

        Returns:
            生成的音频文件路径
        """
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"ai_brief_{timestamp}.mp3"

        # 自动选择最佳方案
        if method == 'auto':
            if self.check_edge_tts():
                method = 'edge'
            else:
                try:
                    import pyttsx3
                    method = 'pyttsx3'
                except ImportError:
                    method = 'edge'  # 最后尝试edge-tts

        if method == 'edge':
            return asyncio.run(self.generate_podcast_edge_tts(script, output_filename, voice))
        elif method == 'pyttsx3':
            return self.generate_podcast_pytsx3(script, output_filename)
        else:
            print(f"❌ 未知的TTS方法: {method}")
            return None

    def save_script(self, script, filename=None):
        """保存播客脚本为文本文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_brief_script_{timestamp}.txt"

        script_path = self.output_dir / filename

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)

        print(f"📝 脚本已保存: {script_path}")
        return str(script_path)


def main():
    """主函数"""
    print("=" * 60)
    print("🎙️  AI简报播客生成服务")
    print("=" * 60)
    print()

    # 初始化播客生成器
    generator = PodcastGenerator()

    # 检查依赖
    print("🔍 检查依赖...")
    has_edge_tts = generator.check_edge_tts()

    try:
        import pyttsx3
        has_pytsx3 = True
    except ImportError:
        has_pytsx3 = False

    print(f"   edge-tts: {'✅ 已安装' if has_edge_tts else '❌ 未安装'}")
    print(f"   pyttsx3:  {'✅ 已安装' if has_pytsx3 else '❌ 未安装'}")
    print()

    if not has_edge_tts and not has_pytsx3:
        print("⚠️  未找到TTS库，请安装其中一个：")
        print("   推荐: pip install edge-tts")
        print("   备选: pip install pyttsx3")
        return

    # 从HTML文件提取内容
    html_file = "ai-daily-brief.html"
    if not Path(html_file).exists():
        print(f"❌ 找不到HTML文件: {html_file}")
        return

    # 提取内容
    content = generator.extract_content_from_html(html_file)

    # 格式化脚本
    script = generator.format_script(content)

    # 保存脚本
    script_path = generator.save_script(script)

    print()
    print("=" * 60)

    # 生成音频
    print("\n🎙️  正在生成播客音频...")
    print("   (这可能需要几分钟时间)\n")

    # 优先使用edge-tts（音质更好）
    if has_edge_tts:
        print("📡 使用 edge-tts (在线，音质更好)")
        audio_path = asyncio.run(
            generator.generate_podcast_edge_tts(script)
        )
    else:
        print("💻 使用 pyttsx3 (离线)")
        audio_path = generator.generate_podcast_pytsx3(script)

    print()
    print("=" * 60)

    if audio_path:
        print("✅ 播客生成完成！")
        print(f"📄 脚本: {script_path}")
        print(f"🎙️  音频: {audio_path}")
        print()
        print("💡 你可以：")
        print("   1. 直接播放音频文件")
        print("   2. 将音频部署到服务器分享")
        print("   3. 使用RSS订阅功能")
    else:
        print("❌ 音频生成失败")

    print("=" * 60)


if __name__ == "__main__":
    main()
