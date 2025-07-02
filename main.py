# === Web server để giữ online (cho UptimeRobot ping) ===
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# === Bot Discord: Tài Xỉu từ MD5 ===
import discord
from discord.ext import commands
import os

def md5_to_dice(md5_hash):
    a = int(md5_hash[0:2], 16) % 6 + 1
    b = int(md5_hash[2:4], 16) % 6 + 1
    c = int(md5_hash[4:6], 16) % 6 + 1
    return a, b, c

def dice_sum(a, b, c):
    return a + b + c

def classify_result(total, is_bao):
    if is_bao:
        return "Bộ ba (Hòa)"
    elif 4 <= total <= 10:
        return "Xỉu"
    elif 11 <= total <= 17:
        return "Tài"
    else:
        return "Không xác định"

def estimate_probability(total, is_bao):
    if is_bao:
        return "Xác suất rất thấp"
    elif total in [4, 17]:
        return "Xác suất thấp"
    elif total in [10, 11]:
        return "Xác suất cao"
    else:
        return "Xác suất trung bình"

def smart_predict(md5_hash):
    a, b, c = md5_to_dice(md5_hash)
    total = dice_sum(a, b, c)
    is_bao = (a == b == c)
    result = classify_result(total, is_bao)
    probability = estimate_probability(total, is_bao)

    if result == "Tài" and probability == "Xác suất cao":
        prediction = "🎯 Dự đoán: Tài ✅"
    elif result == "Xỉu" and probability == "Xác suất cao":
        prediction = "🎯 Dự đoán: Xỉu ✅"
    elif probability == "Xác suất rất thấp":
        prediction = "❌ Dự đoán: Không nên đặt (rủi ro cao)"
    else:
        prediction = f"🤔 Dự đoán nhẹ: {result}"

    return f"""
🔢 **MD5**: `{md5_hash}`
🎲 **Xúc xắc**: {a}, {b}, {c}
➕ **Tổng**: {total}
📌 **Loại**: {result}
📊 **Xác suất**: {probability}
{prediction}
"""

# === Bot Discord ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot đã sẵn sàng: {bot.user}")

@bot.command()
async def taixiu(ctx, md5: str):
    if len(md5) != 32:
        await ctx.send("❌ Vui lòng nhập đúng chuỗi MD5 (32 ký tự).")
        return
    try:
        md5 = md5.lower()
        result = smart_predict(md5)
        await ctx.send(result)
    except Exception as e:
        await ctx.send(f"⚠️ Lỗi xử lý: {str(e)}")

bot.run(os.getenv("TOKEN"))
