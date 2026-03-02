#!/usr/bin/env python3
"""
AI简报Railway部署脚本
持续运行，定时执行更新
"""

import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cloud-update import CloudAIBriefUpdater


class RailwayAIBriefService:
    """Railway持续运行服务"""

    def __init__(self):
        self.updater = CloudAIBriefUpdater()
        self.scheduler = AsyncIOScheduler()

    def log(self, message):
        """输出日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    async def scheduled_update(self):
        """定时更新任务"""
        self.log("⏰ 定时任务触发")
        await self.updater.run()

    async def health_check(self):
        """健康检查接口"""
        from aiohttp import web
        app = web.Application()

        async def health(request):
            return web.json_response({
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "service": "AI简报自动更新服务"
            })

        async def manual_update(request):
            """手动触发更新"""
            # 在后台运行更新
            asyncio.create_task(self.scheduled_update())
            return web.json_response({
                "status": "triggered",
                "message": "更新任务已触发"
            })

        app.router.add_get('/health', health)
        app.router.add_post('/update', manual_update)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8000)))
        await site.start()

        self.log(f"🌐 健康检查服务已启动: http://0.0.0.0:{os.environ.get('PORT', 8000)}/health")

    async def start(self):
        """启动服务"""
        self.log("=" * 60)
        self.log("🚀 AI简报Railway服务启动")
        self.log("=" * 60)

        # 添加定时任务（每天北京时间7点执行）
        self.scheduler.add_job(
            self.scheduled_update,
            'cron',
            hour=23,  # UTC时间23点
            minute=0,
            id='daily_update'
        )

        self.log("⏰ 定时任务已配置: 每天7:00 (北京时间)")

        # 启动定时器
        self.scheduler.start()

        # 启动健康检查服务
        await self.health_check()

        # 保持运行
        self.log("✅ 服务已启动，等待定时任务...")

        try:
            # 持续运行
            while True:
                await asyncio.sleep(3600)  # 每小时检查一次
        except asyncio.CancelledError:
            self.log("⏹️  服务停止")
            self.scheduler.shutdown()


async def main():
    """主函数"""
    service = RailwayAIBriefService()
    await service.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
