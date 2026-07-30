import discord
from discord.ext import commands
from truemoneywallet import Voucher

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

user_money = {}

# ⚙️ ข้อมูลของคุณ
MY_PHONE_NUMBER = "0988785068"
OWNER_ID = 1504934379775070338
BOT_TOKEN = "MTUzMjI5NDMwNjEzNDQ5MTIyNg.GdDstG.W7C_ckKw2ehu-wWR3qcWYOtl5OH6K_X3VJ78NM"

# 🛒 รายการสินค้า ABREALPOOH
PRODUCTS = {
    1: {"name": "ABREALPOOH 1day", "price": 5},
    2: {"name": "ABREALPOOH 3day", "price": 10},
    3: {"name": "ABREALPOOH 7day", "price": 25},
    4: {"name": "ABREALPOOH 30day", "price": 40},
    5: {"name": "ABREALPOOH 5months", "price": 75},
    6: {"name": "ABREALPOOH ถาวร", "price": 200},
}


@bot.event
async def on_ready():
    print(f"บอท {bot.user} ออนไลน์แล้ว!")


@bot.command()
async def shop(ctx):
    text = "🎯 **รายการสินค้า ABREALPOOH**\n"
    for item_id, item_info in PRODUCTS.items():
        text += f"{item_id}. **{item_info['name']}** - ราคา **{item_info['price']}** บาท (พิมพ์ `!buy {item_id}`)\n"

    text += "\n-------------------------------\n"
    text += "💰 **วิธีเติมเงิน:** พิมพ์ `!topup [วางลิงก์ซองอั่งเปา]`\n"
    text += "💳 **เช็กยอดเงิน:** พิมพ์ `!money`"

    await ctx.send(text)


@bot.command()
async def topup(ctx, voucher_url: str):
    user_id = ctx.author.id
    await ctx.send("⏳ กำลังตรวจสอบซองอั่งเปา...")

    try:
        v = Voucher(MY_PHONE_NUMBER)
        result = v.redeem(voucher_url)

        if result.get("status", {}).get("code") == "SUCCESS":
            amount = float(result["data"]["my_ticket"]["amount_baht"])
            amount_int = int(amount)

            user_money[user_id] = user_money.get(user_id, 0) + amount_int

            await ctx.send(
                f"✅ **เติมเงินสำเร็จ!** ได้รับ: **{amount_int}** บาท | ยอดคงเหลือ: **{user_money[user_id]}** บาท"
            )

            owner = await bot.fetch_user(OWNER_ID)
            if owner:
                await owner.send(
                    f"💸 **[แจ้งเตือนเติมเงิน]**\n👤 ลูกค้า: {ctx.author}\n💵 จำนวน: **{amount_int}** บาท"
                )

        else:
            await ctx.send("❌ เติมเงินไม่สำเร็จ ซองไม่ถูกต้องหรือถูกใช้ไปแล้ว")

    except Exception:
        await ctx.send("❌ เกิดข้อผิดพลาด กรุณาตรวจสอบลิงก์ซองอีกครั้ง")


@bot.command()
async def buy(ctx, item_no: int):
    user_id = ctx.author.id
    balance = user_money.get(user_id, 0)

    if item_no not in PRODUCTS:
        await ctx.send("❌ ไม่มีรายการสินค้านี้")
        return

    item = PRODUCTS[item_no]
    price = item["price"]
    item_name = item["name"]

    if balance >= price:
        user_money[user_id] -= price

        await ctx.send(
            f"🎉 ซื้อ **{item_name}** สำเร็จ!\n💰 เงินคงเหลือ: **{user_money[user_id]}** บาท\n📩 กรุณารอ Admin ติดต่อกลับเพื่อรับสินค้า"
        )

        owner = await bot.fetch_user(OWNER_ID)
        if owner:
            await owner.send(
                f"🛒 **[แจ้งเตือนสั่งซื้อสินค้า!]**\n👤 ลูกค้า: {ctx.author} (ID: `{ctx.author.id}`)\n📦 สินค้า: **{item_name}**\n💵 ราคา: **{price}** บาท"
            )
    else:
        await ctx.send(
            f"❌ เงินไม่พอครับ! คุณมี **{balance}** บาท แต่สินค้าราคา **{price}** บาท"
        )


@bot.command()
async def money(ctx):
    user_id = ctx.author.id
    balance = user_money.get(user_id, 0)
    await ctx.send(f"👛 ยอดเงินคงเหลือ: **{balance}** บาท")


bot.run(BOT_TOKEN)
