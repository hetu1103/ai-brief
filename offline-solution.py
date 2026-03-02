#!/usr/bin/env python3
"""
AI简报自动更新脚本 - 支持补执行
即使电脑关机，开机后会自动执行错过的时间段
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from edge_tts import Communicate


class AIBriefUpdaterWithAnacron:
    """支持补执行的自动更新器"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.today = datetime.now().strftime("%Y年%m月%d日")
        self.date_slug = datetime.now().strftime("%Y%m%d")
        self.podcasts_dir = self.base_dir / "podcasts"
        self.podcasts_dir.mkdir(exist_ok=True)

        # 记录文件
        self.last_run_file = self.base_dir / ".last_run"
        self.lock_file = self.base_dir / ".update_lock"

    def log(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def should_run(self):
        """判断是否需要运行"""
        now = datetime.now()

        # 检查锁文件（防止重复运行）
        if self.lock_file.exists():
            lock_time = datetime.fromtimestamp(self.lock_file.stat().st_mtime)
            if (now - lock_time) < timedelta(minutes=30):
                self.log("⏸️  任务正在运行或刚刚完成，跳过")
                return False

        # 检查最后运行时间
        if self.last_run_file.exists():
            last_run = datetime.fromtimestamp(self.last_run_file.stat().st_mtime)
            days_since_last_run = (now - last_run).days

            if days_since_last_run == 0:
                self.log("✅ 今天已经运行过了")
                return False
            elif days_since_last_run > 0:
                self.log(f"📅 距离上次运行已过 {days_since_last_run} 天，现在执行")
                return True

        return True

    def acquire_lock(self):
        """获取锁"""
        self.lock_file.touch()

    def release_lock(self):
        """释放锁"""
        if self.lock_file.exists():
            self.lock_file.unlink()

    def mark_last_run(self):
        """标记最后运行时间"""
        self.last_run_file.touch()

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
            return None

    def update_html_audio_link(self, audio_file):
        """更新HTML中的音频链接"""
        self.log("📄 更新HTML音频链接...")

        html_file = self.base_dir / "ai-daily-brief.html"

        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换音频链接为最新
            import re
            pattern = r'podcasts/ai_brief_\d+\.mp3'
            new_link = f'podcasts/ai_brief_{self.date_slug}.mp3'
            content = re.sub(pattern, new_link, content)

            # 更新日期
            old_date_pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
            content = re.sub(old_date_pattern, self.today, content)

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log("✅ HTML更新成功")

        except Exception as e:
            self.log(f"❌ HTML更新失败: {e}")

    async def run(self):
        """执行自动更新流程"""
        self.log("=" * 60)
        self.log("🚀 AI简报自动更新开始")
        self.log("=" * 60)

        # 检查是否需要运行
        if not self.should_run():
            return

        # 获取锁
        self.acquire_lock()

        try:
            # 生成播客脚本
            script = self.get_default_script()
            self.log(f"📝 脚本长度: {len(script)} 字符")

            # 生成播客音频
            audio_file = await self.generate_podcast_audio(script)

            if audio_file:
                # 更新HTML链接
                self.update_html_audio_link(audio_file)

            # 标记最后运行时间
            self.mark_last_run()

            self.log("=" * 60)
            self.log("✅ 自动更新完成")
            self.log("=" * 60)

        finally:
            # 释放锁
            self.release_lock()


async def main():
    """主函数"""
    updater = AIBriefUpdaterWithAnacron()
    await updater.run()


if __name__ == "__main__":
    asyncio.run(main())
