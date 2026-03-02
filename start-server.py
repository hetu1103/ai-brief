#!/usr/bin/env python3
"""
简单的HTTP服务器，用于测试AI简报H5页面和播客功能
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # 添加CORS头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_server():
    """启动HTTP服务器"""
    os.chdir(DIRECTORY)

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🚀 AI简报本地服务器")
        print("=" * 60)
        print()
        print(f"✅ 服务器已启动: http://localhost:{PORT}")
        print()
        print("📱 在浏览器中打开:")
        print(f"   http://localhost:{PORT}/ai-daily-brief.html")
        print()
        print("💡 提示:")
        print("   - 按 Ctrl+C 停止服务器")
        print("   - 修改HTML后需要刷新浏览器")
        print("   - 音频文件在 podcasts/ 目录")
        print()
        print("=" * 60)
        print()

        # 自动打开浏览器
        url = f"http://localhost:{PORT}/ai-daily-brief.html"
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)

        print()
        print("服务器运行中...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 服务器已停止")

if __name__ == "__main__":
    start_server()
