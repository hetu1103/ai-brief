#!/usr/bin/env python3
"""
AI简报云端自动更新脚本
支持：GitHub Actions, Railway, 阿里云函数等
"""

import asyncio
import os
import re
from datetime import datetime
from pathlib import Path
from edge_tts import Communicate


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

    def update_html_audio_link(self, audio_file):
        """更新HTML中的音频链接"""
        self.log("📄 更新HTML音频链接...")

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

            # 更新日期
            old_date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
            content = re.sub(old_date_pattern, self.today, content)

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
        """创建最新的音频符号链接"""
        latest_link = self.podcasts_dir / "ai_brief_latest.mp3"
        current_audio = self.podcasts_dir / f"ai_brief_{self.date_slug}.mp3"

        if current_audio.exists():
            # 删除旧的符号链接
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()

            # 创建新的符号链接
            latest_link.symlink_to(current_audio.name)
            self.log(f"✅ 创建最新音频链接: {latest_link}")

    async def run(self):
        """执行云端自动更新流程"""
        self.log("=" * 60)
        self.log("🚀 AI简报云端自动更新开始")
        self.log(f"🌍 运行环境: {os.environ.get('GITHUB_ACTIONS', 'Local')}")
        self.log("=" * 60)

        try:
            # 生成播客脚本
            script = self.get_default_script()
            self.log(f"📝 脚本长度: {len(script)} 字符")

            # 生成播客音频
            audio_file = await self.generate_podcast_audio(script)

            if audio_file:
                # 更新HTML链接
                success = self.update_html_audio_link(audio_file)

                if success:
                    # 创建最新音频链接
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
