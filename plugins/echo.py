# ©️ LISA-KOREA | @LISA_FAN_LK | NT_BOT_CHANNEL | TG-SORRY

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math
from PIL import Image
from plugins.config import Config
from plugins.script import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from pyrogram import enums
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Thumbnail

from plugins.functions.verify import verify_user, check_token, check_verification, get_token
from plugins.functions.forcesub import handle_force_subscribe
from plugins.functions.display_progress import humanbytes, progress_for_pyrogram, TimeFormatter
from plugins.functions.help_uploadbot import DownLoadFile
from plugins.functions.ran_text import random_char
from plugins.database.database import db
from plugins.database.add import AddUser

# Temp storage for pending links waiting for caption
pending_links = {}

@Client.on_message(filters.private & filters.regex(r"https?://"))
async def ask_for_caption(bot, message):
    user_id = message.from_user.id
    url = message.text.strip()

    if not await check_verification(bot, user_id) and Config.TRUE_OR_FALSE:
        button = [[
            InlineKeyboardButton("✓⃝ Vᴇʀɪꜰʏ ✓⃝", url=await get_token(bot, user_id, f"https://telegram.me/{Config.BOT_USERNAME}?start="))
        ],[
            InlineKeyboardButton("🔆 Wᴀᴛᴄʜ Hᴏᴡ Tᴏ Vᴇʀɪꜰʏ 🔆", url=f"{Config.VERIFICATION}")
        ]]
        await message.reply_text(
            text="<b>Pʟᴇᴀsᴇ Vᴇʀɪꜰʏ Fɪʀsᴛ Tᴏ Usᴇ Mᴇ</b>",
            reply_markup=InlineKeyboardMarkup(button)
        )
        return

    if Config.LOG_CHANNEL:
        try:
            log_message = await message.forward(Config.LOG_CHANNEL)
            log_info = f"Message Sender Information\n\nFirst Name: {message.from_user.first_name}\nUser ID: {user_id}\nUsername: @{message.from_user.username if message.from_user.username else ''}\nUser Link: {message.from_user.mention}"
            await log_message.reply_text(text=log_info, disable_web_page_preview=True, quote=True)
        except Exception as e:
            print(e)

    await AddUser(bot, message)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, message)
        if fsub == 400:
            return

    pending_links[user_id] = {
        "url": url,
        "msg_id": message.id
    }
    await message.reply_text("📌 Please reply to this message with a caption for the link you sent.")


@Client.on_message(filters.private & filters.reply)
async def handle_caption_reply(bot, message):
    user_id = message.from_user.id

    if user_id not in pending_links:
        return

    original = pending_links[user_id]
    if message.reply_to_message.id != original["msg_id"]:
        return

    url = original["url"]
    caption = message.text.strip()
    del pending_links[user_id]

    command_to_exec = [
        "yt-dlp",
        "--no-warnings",
        "--allow-dynamic-mpd",
        "--no-check-certificate",
        "-j",
        url,
        "--geo-bypass-country", "IN"
    ]

    chk = await bot.send_message(
        chat_id=message.chat.id,
        text=f'ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʟɪɴᴋ ⌛',
        disable_web_page_preview=True,
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )

    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()

    if e_response and "nonnumeric port" not in e_response:
        await chk.delete()
        await bot.send_message(
            chat_id=message.chat.id,
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(e_response)),
            reply_to_message_id=message.id,
            disable_web_page_preview=True
        )
        return

    if t_response:
        if "\n" in t_response:
            t_response, _ = t_response.split("\n")
        response_json = json.loads(t_response)
        randem = random_char(5)
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + "/" + str(user_id) + f'{randem}' + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)

        inline_keyboard = []
        duration = response_json.get("duration")

        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note") or formats.get("format")
                if "DASH" in format_string.upper():
                    continue
                format_ext = formats.get("ext")
                size = formats.get('filesize') or formats.get('filesize_approx') or 0
                cb_string_video = f"video|{format_id}|{format_ext}|{randem}"

                ikeyboard = [
                    InlineKeyboardButton(
                        f"📁 {format_string} {format_ext} {humanbytes(size)}",
                        callback_data=cb_string_video.encode("UTF-8")
                    )
                ]
                inline_keyboard.append(ikeyboard)

            if duration is not None:
                for kbps in ["64", "128", "320"]:
                    cb_string_audio = f"audio|{kbps}k|mp3|{randem}"
                    inline_keyboard.append([
                        InlineKeyboardButton(f"🎵 ᴍᴘ𝟹 ({kbps} ᴋʙᴘs)", callback_data=cb_string_audio.encode("UTF-8"))
                    ])

            inline_keyboard.append([
                InlineKeyboardButton("🔒 ᴄʟᴏsᴇ", callback_data='close')
            ])

        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_video = f"video|{format_id}|{format_ext}|{randem}"
            inline_keyboard.append([
                InlineKeyboardButton("📁 Document", callback_data=cb_string_video.encode("UTF-8"))
            ])

        await chk.delete()
        await bot.send_message(
            chat_id=message.chat.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            disable_web_page_preview=True,
            reply_to_message_id=message.id
        )
    else:
        cb_string_video = "video=LFO=NONE"
        inline_keyboard = [[
            InlineKeyboardButton("📁 ᴍᴇᴅɪᴀ", callback_data=cb_string_video.encode("UTF-8"))
        ]]
        await chk.delete()
        await bot.send_message(
            chat_id=message.chat.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            disable_web_page_preview=True,
            reply_to_message_id=message.id
)
