import threading
import time
import webbrowser

import uvicorn
from app.main import app


def open_browser():
    """延迟打开浏览器，等待服务启动"""
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    # 在新线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
