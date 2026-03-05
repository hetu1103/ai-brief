#!/usr/bin/env python3
"""
AI简报云端自动更新脚本
支持：GitHub Actions, Railway, 阿里云函数等
"""

import asyncio
import os
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
from edge_tts import Communicate
from bs4 import BeautifulSoup


class CloudAIBriefUpdater:
    """云端AI简报更新器"""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.today = datetime.now().strftime("%Y年%m月%d日")
        self.date_slug = datetime.now().strftime("%Y%m%d")
        self.podcasts_dir = self.base_dir / "podcasts"
        self.podcasts_dir.mkdir(exist_ok=True)

        # GitHub Actions 特殊路径
        if os.environ.get('GITHUB_ACTIONS'):
            self.base_dir = Path(os.environ.get('GITHUB_WORKSPACE', '/github/workspace'))

    def log(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        # 强制刷新输出（GitHub Actions需要）
        import sys
        sys.stdout.flush()

    def fetch_readhub_news(self):
        """从 Readhub API 获取当天新闻"""
        self.log("🔍 开始从 Readhub 获取最新资讯...")

        try:
            # Readhub API
            url = "https://api.readhub.cn/topic/list"

            # 设置请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                self.log(f"⚠️  Readhub API 请求失败: {response.status_code}")
                return None

            data = response.json()

            # 提取新闻列表
            news_items = []
            items = data.get('data', {}).get('items', [])

            for item in items[:30]:  # 取前30条
                try:
                    title = item.get('title', '').strip()
                    summary = item.get('summary', '').strip()
                    created_at = item.get('createdAt', '')
                    site_name = item.get('siteNameDisplay', '')

                    if not title:
                        continue

                    news_items.append({
                        'title': title,
                        'summary': summary or title,  # 如果没有摘要就用标题
                        'time': created_at,
                        'source': site_name
                    })

                except Exception as e:
                    self.log(f"⚠️  解析新闻项失败: {e}")
                    continue

            self.log(f"✅ 成功获取 {len(news_items)} 条资讯")
            return news_items

        except Exception as e:
            self.log(f"❌ 获取 Readhub 数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def filter_news_by_category(self, news_items):
        """按类别过滤新闻（AI 和新能源汽车）"""
        if not news_items:
            return {'ai': [], 'ev': []}

        ai_keywords = [
            'AI', '人工智能', 'GPT', 'ChatGPT', '大模型', '机器学习', '深度学习',
            '芯片', '英伟达', 'NVIDIA', '模型', '训练', '推理', '算力',
            'OpenAI', 'Anthropic', 'Google', 'Gemini', 'Claude', 'Siri',
            '融资', '投资', '估值', '独角兽'
        ]

        ev_keywords = [
            '新能源', '电动车', 'EV', '比亚迪', '特斯拉', 'Tesla',
            '充电桩', '电池', '续航', '补贴', '销量', '交付',
            '理想', '蔚来', '小鹏', '小米汽车', '问界', '华为',
            '年检', '车险', '上市', '发布'
        ]

        ai_news = []
        ev_news = []

        for item in news_items:
            title = item['title'].lower()
            summary = item['summary'].lower()

            # 检查是否包含关键词
            ai_match = any(keyword.lower() in title or keyword.lower() in summary for keyword in ai_keywords)
            ev_match = any(keyword.lower() in title or keyword.lower() in summary for keyword in ev_keywords)

            if ai_match:
                ai_news.append(item)
            if ev_match:
                ev_news.append(item)

        self.log(f"📊 过滤结果: AI {len(ai_news)} 条, 新能源车 {len(ev_news)} 条")
        return {'ai': ai_news, 'ev': ev_news}

    def generate_script_from_news(self, categorized_news):
        """从新闻数据生成播客脚本"""
        self.log("📝 根据新闻数据生成脚本...")

        ai_news = categorized_news.get('ai', [])
        ev_news = categorized_news.get('ev', [])

        # 如果没有获取到新闻，使用默认脚本
        if not ai_news and not ev_news:
            self.log("⚠️  未获取到新闻数据，使用默认脚本")
            return self.get_default_script()

        # 构建脚本
        script_parts = []

        # 开场
        script_parts.append(f"大家好，欢迎收听AI简报，今天是{self.today}。")
        script_parts.append("今天为大家带来新能源汽车和人工智能两大领域的最新动态。")
        script_parts.append("")

        # 新能源汽车板块
        if ev_news:
            script_parts.append("【新能源汽车领域】")
            script_parts.append("")
            script_parts.append("首先是今日速览。")

            for i, news in enumerate(ev_news[:5], 1):
                script_parts.append(f"第{i}，{news['title']}。{news['summary']}")

            script_parts.append("")
        else:
            self.log("⚠️  未获取到新能源汽车相关新闻，使用默认内容")
            script_parts.append("【新能源汽车领域】")
            script_parts.append("")
            script_parts.append("今天暂无重大动态更新。")
            script_parts.append("")

        # AI 板块
        if ai_news:
            script_parts.append("【人工智能领域】")
            script_parts.append("")
            script_parts.append("首先是今日速览。")

            for i, news in enumerate(ai_news[:5], 1):
                script_parts.append(f"第{i}，{news['title']}。{news['summary']}")

            script_parts.append("")
        else:
            self.log("⚠️  未获取到AI相关新闻，使用默认内容")
            script_parts.append("【人工智能领域】")
            script_parts.append("")
            script_parts.append("今天暂无重大动态更新。")
            script_parts.append("")

        # 结尾
        script_parts.append("以上就是今天AI简报的全部内容，感谢收听，我们下期再见。")

        script = "\n".join(script_parts)
        self.log(f"✅ 脚本生成完成，长度: {len(script)} 字符")

        return script

    def get_default_script(self):
        """获取播客脚本"""
        return f"""
大家好，欢迎收听AI简报，今天是{self.today}。

今天为大家带来新能源汽车和人工智能两大领域的最新动态。

【新能源汽车领域】

首先是今日速览。

2026年3月新能源车年检新规正式实施，电池衰减超30%不合格。新能源汽车专属年检规定正式落地，三电系统成为必检项目。

汽车补贴新政落地，新能源最高补2万元。报废旧车购买新能源车最高补贴2万元，置换新能源车型最高补贴1.5万元。

3月新车潮来袭，至少10款新能源车排队上市。奇瑞iCAR V27、零跑A10、昊铂A800、问界M6等重磅车型集中发布。

接下来是市场数据。

2月新能源车销量成绩单，比亚迪19.02万辆领跑。小米汽车超2万辆，理想汽车约2.6万台。

招银国际观点：首两月新能源车销售弱于预期，预计3月开始市场份额反弹。

最后是政策动态。

充电电价市场化改革，3月1日起九省市试点。公共充电桩电价随电力市场供需实时浮动。

辟谣：10省市试点开征新能源汽车里程税消息不实。

【人工智能领域】

首先是今日速览。

英伟达3月15日发布"世界前所未见"的革命性AI芯片。

苹果2026年3月推出新一代Siri，深度整合Google Gemini。

AI融资进入寡头时代，前7周17家公司融资540亿美元。

接下来是大佬观点。

黄仁勋表示，AI芯片技术逼近物理极限，需要架构革命。

2026 AI年度展望总结出十条核心趋势判断。

最后是投融资动态。

Anthropic拟筹资250亿美元，将是AI史上最大融资。

2026年1月，9家新AI独角兽诞生。

以上就是今天AI简报的全部内容，感谢收听，我们下期再见。
""".strip()

    async def generate_podcast_audio(self, script):
        """生成播客音频"""
        self.log("🎙️  生成播客音频...")

        output_file = self.podcasts_dir / f"ai_brief_{self.date_slug}.mp3"
        voice = "zh-CN-XiaoyiNeural"

        try:
            communicate = Communicate(script, voice)
            await communicate.save(str(output_file))

            file_size = output_file.stat().st_size / (1024 * 1024)
            self.log(f"✅ 音频生成成功: {output_file.name} ({file_size:.2f} MB)")

            return str(output_file)

        except Exception as e:
            self.log(f"❌ 音频生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_html_audio_link(self, audio_file, categorized_news=None):
        """更新HTML中的音频链接和新闻内容"""
        self.log("📄 更新HTML内容...")

        html_file = self.base_dir / "ai-daily-brief.html"

        if not html_file.exists():
            self.log(f"⚠️  HTML文件不存在: {html_file}")
            return False

        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换音频链接为最新（使用正则表达式）
            pattern = r'podcasts/ai_brief_\d{8}\.mp3'
            new_link = f'podcasts/ai_brief_{self.date_slug}.mp3'
            content = re.sub(pattern, new_link, content)

            # 更新日期（标题中的日期）
            old_date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
            content = re.sub(old_date_pattern, self.today, content)

            # 如果有新闻数据，更新新闻内容
            if categorized_news:
                self.log("📰 更新新闻内容...")
                soup = BeautifulSoup(content, 'html.parser')

                # 更新新能源汽车板块新闻
                ev_news = categorized_news.get('ev', [])
                if ev_news:
                    ev_container = soup.find('div', id='ev-section')
                    if ev_container:
                        # 找到第一个 news-section（今日速览）
                        ev_section = ev_container.find('div', class_='news-section')
                        if ev_section:
                            # 移除旧的新闻项
                            for old_item in ev_section.find_all('div', class_='news-item'):
                                old_item.decompose()

                            # 更新新闻数量
                            section_header = ev_section.find('div', class_='section-header')
                            if section_header:
                                count_elem = section_header.find('div', class_='section-count')
                                if count_elem:
                                    count_elem.string = f'{len(ev_news)}条'

                            # 插入新新闻
                            for news in ev_news[:5]:  # 最多5条
                                news_item = soup.new_tag('div', **{'class': 'news-item'})

                                # 标题
                                title_div = soup.new_tag('div', **{'class': 'news-title'})
                                title_div.string = news['title']
                                news_item.append(title_div)

                                # 元信息
                                meta_div = soup.new_tag('div', **{'class': 'news-meta'})
                                if news.get('source'):
                                    source_span = soup.new_tag('span')
                                    source_span.string = news['source']
                                    meta_div.append(source_span)

                                if news.get('time'):
                                    time_str = news['time'][:10] if len(news['time']) > 10 else news['time']
                                    time_span = soup.new_tag('span')
                                    time_span.string = time_str
                                    meta_div.append(time_span)

                                news_item.append(meta_div)

                                # 摘要
                                summary_div = soup.new_tag('div', **{'class': 'news-summary'})
                                summary_text = news.get('summary', news['title'])[:200]
                                summary_div.string = summary_text
                                news_item.append(summary_div)

                                # 插入到section中
                                ev_section.append(news_item)
                            self.log(f"✅ 更新新能源车新闻 {len(ev_news)} 条")

                # 更新AI板块新闻
                ai_news = categorized_news.get('ai', [])
                if ai_news:
                    ai_container = soup.find('div', id='ai-section')
                    if ai_container:
                        # 找到第一个 news-section（今日速览）
                        ai_section = ai_container.find('div', class_='news-section')
                        if ai_section:
                            # 移除旧的新闻项
                            for old_item in ai_section.find_all('div', class_='news-item'):
                                old_item.decompose()

                            # 更新新闻数量
                            section_header = ai_section.find('div', class_='section-header')
                            if section_header:
                                count_elem = section_header.find('div', class_='section-count')
                                if count_elem:
                                    count_elem.string = f'{len(ai_news)}条'

                            for news in ai_news[:5]:
                                news_item = soup.new_tag('div', **{'class': 'news-item'})

                                title_div = soup.new_tag('div', **{'class': 'news-title'})
                                title_div.string = news['title']
                                news_item.append(title_div)

                                meta_div = soup.new_tag('div', **{'class': 'news-meta'})
                                if news.get('source'):
                                    source_span = soup.new_tag('span')
                                    source_span.string = news['source']
                                    meta_div.append(source_span)
                                news_item.append(meta_div)

                                summary_div = soup.new_tag('div', **{'class': 'news-summary'})
                                summary_text = news.get('summary', news['title'])[:200]
                                summary_div.string = summary_text
                                news_item.append(summary_div)

                                ai_section.append(news_item)
                            self.log(f"✅ 更新AI新闻 {len(ai_news)} 条")

                # 更新内容
                content = str(soup)

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log("✅ HTML更新成功")
            return True

        except Exception as e:
            self.log(f"❌ HTML更新失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_latest_audio_link(self):
        """创建最新的音频符号链接（在GitHub Actions中跳过）"""
        # 在GitHub Actions环境中跳过符号链接创建
        if os.environ.get('GITHUB_ACTIONS'):
            self.log("⏭️  GitHub Actions环境，跳过符号链接创建")
            return

        latest_link = self.podcasts_dir / "ai_brief_latest.mp3"
        current_audio = self.podcasts_dir / f"ai_brief_{self.date_slug}.mp3"

        if current_audio.exists():
            # 删除旧的符号链接
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()

            # 创建新的符号链接
            try:
                latest_link.symlink_to(current_audio.name)
                self.log(f"✅ 创建最新音频链接: {latest_link}")
            except OSError:
                # Windows可能不支持符号链接，复制文件代替
                import shutil
                shutil.copy2(current_audio, latest_link)
                self.log(f"✅ 复制最新音频: {latest_link}")

    async def run(self):
        """执行云端自动更新流程"""
        self.log("=" * 60)
        self.log("🚀 AI简报云端自动更新开始")
        self.log(f"🌍 运行环境: {os.environ.get('GITHUB_ACTIONS', 'Local')}")
        self.log("=" * 60)

        try:
            # 1. 从 Readhub 获取新闻
            news_items = self.fetch_readhub_news()

            # 2. 过滤分类新闻
            categorized_news = None
            if news_items:
                categorized_news = self.filter_news_by_category(news_items)

            # 3. 生成播客脚本（如果有新闻数据就用真实数据，否则用默认脚本）
            if categorized_news:
                script = self.generate_script_from_news(categorized_news)
            else:
                self.log("⚠️  使用默认脚本")
                script = self.get_default_script()

            self.log(f"📝 脚本长度: {len(script)} 字符")

            # 4. 生成播客音频
            audio_file = await self.generate_podcast_audio(script)

            if audio_file:
                # 5. 更新HTML链接和新闻内容
                success = self.update_html_audio_link(audio_file, categorized_news)

                if success:
                    # 6. 创建最新音频链接
                    self.create_latest_audio_link()

                    self.log("=" * 60)
                    self.log("✅ 云端自动更新完成")
                    self.log("=" * 60)

                    # 输出更改的文件（供GitHub Actions检测）
                    self.log(f"📁 更新的文件: {audio_file}")
                    self.log(f"📁 更新的文件: {self.base_dir / 'ai-daily-brief.html'}")

                    return 0
                else:
                    self.log("❌ HTML更新失败")
                    return 1
            else:
                self.log("❌ 音频生成失败")
                return 1

        except Exception as e:
            self.log(f"❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return 1


async def main():
    """主函数"""
    updater = CloudAIBriefUpdater()
    exit_code = await updater.run()
    exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
