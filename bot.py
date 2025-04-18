# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | @NT_BOTS_SUPPORT | LISA-KOREA/UPLOADER-BOT-V4

# [⚠️ Do not change this repo link ⚠️] :- https://github.com/LISA-KOREA/UPLOADER-BOT-V4


import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from plugins.config import Config
from pyrogram import Client

# Start simple HTTP server for Koyeb health check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Bot is alive!')
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server():
    server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

if __name__ == "__main__" :
    
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    plugins = dict(root="plugins")
    Client = Client("@UploaderXNTBot",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=300,
    plugins=plugins)
    print("🎊 I AM ALIVE 🎊  • Support @NT_BOTS_SUPPORT")
    Client.run()
