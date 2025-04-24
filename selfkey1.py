from telethon import TelegramClient, events, functions, types
import asyncio
import pytz
from datetime import datetime
import logging
import random
import os
from PIL import Image, ImageDraw, ImageFont
import time
import jdatetime
from gtts import gTTS
import textwrap
from io import BytesIO
import requests

# تنظیمات اولیه
api_id = 29042268
api_hash = '54a7b377dd4a04a58108639febe2f443'

# غیرفعال کردن لاگ‌ها
logging.basicConfig(level=logging.ERROR)

# متغیرهای گلوبال 
enemies = set()
current_font = 'normal'
actions = {
    'typing': False,
    'online': False,
    'reaction': False
}
spam_words = []
saved_messages = []
reminders = []
time_enabled = True
saved_pics = []

locked_chats = {
    'screenshot': set(),  # چت‌های دارای قفل اسکرین‌شات
    'forward': set(),     # چت‌های دارای قفل فوروارد
    'copy': set()        # چت‌های دارای قفل کپی
}

# تبدیل اعداد به توان
def to_superscript(num):
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return ''.join(superscripts[n] for n in str(num))

insults = [
    "کیرم تو کص ننت", "مادرجنده", "کص ننت", "کونی", "جنده", "کیری", "بی ناموس", "حرومزاده", "مادر قحبه", "جاکش",
    "کص ننه", "ننه جنده", "مادر کصده", "خارکصه", "کون گشاد", "ننه کیردزد", "مادر به خطا", "توله سگ", "پدر سگ", "حروم لقمه",
    "ننه الکسیس", "کص ننت میجوشه", "کیرم تو کص مادرت", "مادر جنده ی حرومی", "زنا زاده", "مادر خراب", "کصکش", "ننه سگ پرست",
    "مادرتو گاییدم", "خواهرتو گاییدم", "کیر سگ تو کص ننت", "کص مادرت", "کیر خر تو کص ننت", "کص خواهرت", "کون گشاد",
    "سیکتیر کص ننه", "ننه کیر خور", "خارکصده", "مادر جنده", "ننه خیابونی", "کیرم تو دهنت", "کص لیس", "ساک زن",
    "کیرم تو قبر ننت", "بی غیرت", "کص ننه پولی", "کیرم تو کص زنده و مردت", "مادر به خطا", "لاشی", "عوضی", "آشغال",
    "ننه کص طلا", "کیرم تو کص ننت بالا پایین", "کیر قاطر تو کص ننت", "کص ننت خونه خالی", "کیرم تو کص ننت یه دور", 
    "مادر خراب گشاد", "کیرم تو نسل اولت", "کیرم تو کص ننت محکم", "کیر خر تو کص مادرت", "کیرم تو روح مادر جندت",
    "کص ننت سفید برفی", "کیرم تو کص خارت", "کیر سگ تو کص مادرت", "کص ننه کیر خور", "کیرم تو کص زیر خواب",
    "مادر جنده ولگرد", "کیرم تو دهن مادرت", "کص مادرت گشاد", "کیرم تو لای پای مادرت", "کص ننت خیس",
    "کیرم تو کص مادرت بگردش", "کص ننه پاره", "مادر جنده حرفه ای", "کیرم تو کص و کون ننت", "کص ننه تنگ",
    "کیرم تو حلق مادرت", "ننه جنده مفت خور", "کیرم از پهنا تو کص ننت", "کص مادرت بد بو", "کیرم تو همه کس و کارت",
    "مادر کصده سیاه", "کیرم تو کص گشاد مادرت", "کص ننه ساک زن", "کیرم تو کص خاندانت", "مادر جنده خیابونی",
    "کیرم تو کص ننت یه عمر", "ننه جنده کص خور", "کیرم تو نسل و نژادت", "کص مادرت پاره", "کیرم تو شرف مادرت",
    "مادر جنده فراری", "کیرم تو روح مادرت", "کص ننه جندت", "کیرم تو غیرتت", "کص مادر بدکاره",
    "کیرم تو ننه جندت", "مادر کصده لاشی", "کیرم تو وجود مادرت", "کص ننه بی آبرو", "کیرم تو شعور ننت"
]

async def text_to_voice(text, lang='fa'):
    try:
        tts = gTTS(text=text, lang=lang)
        filename = "voice.mp3"
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error in text to voice: {e}")
        return None

async def text_to_image(text):
    try:
        width = 800
        height = 400
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        font_size = 40
        font = ImageFont.truetype("arial.ttf", font_size)
        
        lines = textwrap.wrap(text, width=30)
        y = 50
        for line in lines:
            draw.text((50, y), line, font=font, fill='black')
            y += font_size + 10
            
        filename = "text.png"
        img.save(filename)
        return filename
    except Exception as e:
        print(f"Error in text to image: {e}")
        return None

async def text_to_gif(text):
    try:
        width = 800
        height = 400
        frames = []
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        for color in colors:
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 40)
            draw.text((50, 150), text, font=font, fill=color)
            frames.append(img)
        
        filename = "text.gif"
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=500,
            loop=0
        )
        return filename
    except Exception as e:
        print(f"Error in text to gif: {e}")
        return None

async def update_time(client):
    while True:
        try:
            if time_enabled:
                now = datetime.now(pytz.timezone('Asia/Tehran'))
                hours = to_superscript(now.strftime('%H'))
                minutes = to_superscript(now.strftime('%M'))
                time_string = f"{hours}:{minutes}"
                await client(functions.account.UpdateProfileRequest(last_name=time_string))
        except Exception as e:
            print('Error updating time:', e)
        await asyncio.sleep(60)

async def auto_online(client):
    while actions['online']:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
        except Exception as e:
            print('Error updating online status:', e)
        await asyncio.sleep(30)

async def auto_typing(client, chat):
    while actions['typing']:
        try:
            async with client.action(chat, 'typing'):
                await asyncio.sleep(3)
        except:
            pass

async def auto_reaction(event):
    if actions['reaction']:
        try:
            await event.message.react('👍')
        except:
            pass

async def schedule_message(client, chat_id, delay, message):
    await asyncio.sleep(delay * 60)
    await client.send_message(chat_id, message)

async def spam_messages(client, chat_id, count, message):
    for _ in range(count):
        await client.send_message(chat_id, message)
        await asyncio.sleep(0.5)

async def main():
    print("\n=== Self Bot ===\n")

    client = TelegramClient('anon', api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("لطفا شماره تلفن خود را وارد کنید (مثال: +989123456789):")
            phone = input("> ")
            
            try:
                await client.send_code_request(phone)
                print("\nکد تایید ارسال شد. لطفا کد را وارد کنید:")
                code = input("> ")
                await client.sign_in(phone, code)
                
            except Exception as e:
                if "two-steps verification" in str(e).lower():
                    print("\nرمز دو مرحله‌ای فعال است. لطفا رمز را وارد کنید:")
                    password = input("> ")
                    await client.sign_in(password=password)
                else:
                    print(f"\nخطا در ورود: {str(e)}")
                    return

        print("\n✅ با موفقیت وارد شدید!")
        print("💡 برای نمایش راهنما، کلمه 'پنل' را ارسال کنید\n")
        
        # شروع آپدیت زمان
        asyncio.create_task(update_time(client))

        @client.on(events.NewMessage(pattern=r'^time (on|off)$'))
        async def time_handler(event):
            global time_enabled
            try:
                if event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                time_enabled = (status == 'on')
                if not time_enabled:
                    await client(functions.account.UpdateProfileRequest(last_name=''))
                await event.edit(f"✅ نمایش ساعت {'فعال' if time_enabled else 'غیرفعال'} شد")
            except Exception as e:
                print(f"Error in time handler: {e}")

        @client.on(events.NewMessage(pattern='^متن به ویس بگو (.+)$'))
        async def voice_handler(event):
            try:
                if event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                voice_file = await text_to_voice(text)
                if voice_file:
                    await event.reply(file=voice_file)
                    os.remove(voice_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به ویس")
            except Exception as e:
                print(f"Error in voice handler: {e}")

        @client.on(events.NewMessage(pattern='^save pic$'))
        async def save_pic_handler(event):
            try:
                if not event.is_reply:
                    return
                replied = await event.get_reply_message()
                if replied.photo:
                    path = await client.download_media(replied.photo)
                    saved_pics.append(path)
                    await event.edit("✅ عکس ذخیره شد")
            except Exception as e:
                print(f"Error in save pic handler: {e}")

        @client.on(events.NewMessage(pattern='^متن به عکس (.+)$'))
        async def img_handler(event):
            try:
                if event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                img_file = await text_to_image(text)
                if img_file:
                    await event.reply(file=img_file)
                    os.remove(img_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به عکس")
            except Exception as e:
                print(f"Error in image handler: {e}")

        @client.on(events.NewMessage(pattern='^متن به گیف (.+)$'))
        async def gif_handler(event):
            try:
                if event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                gif_file = await text_to_gif(text)
                if gif_file:
                    await event.reply(file=gif_file)
                    os.remove(gif_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به گیف")
            except Exception as e:
                print(f"Error in gif handler: {e}")

        @client.on(events.NewMessage(pattern=r'^(screenshot|forward|copy) (on|off)$'))
        async def lock_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                command, status = event.raw_text.lower().split()
                chat_id = str(event.chat_id)
                
                if status == 'on':
                    locked_chats[command].add(chat_id)
                    await event.edit(f"✅ قفل {command} فعال شد")
                else:
                    locked_chats[command].discard(chat_id)
                    await event.edit(f"✅ قفل {command} غیرفعال شد")
                    
            except Exception as e:
                print(f"Error in lock handler: {e}")

        @client.on(events.NewMessage(pattern='پنل'))
        async def panel_handler(event):
            try:
                if not event.from_id:
                    return
                    
                if event.from_id.user_id == (await client.get_me()).id:
                    await event.reply('''📱 راهنمای ربات:

⚙️ تنظیمات دشمن:
• تنظیم دشمن (ریپلای) - اضافه کردن به لیست دشمن
• حذف دشمن (ریپلای) - حذف از لیست دشمن  
• لیست دشمن - نمایش لیست دشمنان

🔤 فونت ها:
• bold on/off - فونت ضخیم
• italic on/off - فونت کج
• script on/off - فونت دست‌نویس 
• double on/off - فونت دوتایی
• bubble on/off - فونت حبابی
• square on/off - فونت مربعی

⚡️ اکشن های خودکار:
• typing on/off - تایپینگ دائم
• online on/off - آنلاین دائم 
• reaction on/off - ری‌اکشن خودکار
• time on/off - نمایش ساعت در نام

🔒 قفل‌ها:
• screenshot on/off - قفل اسکرین‌شات
• forward on/off - قفل فوروارد
• copy on/off - قفل کپی

🎨 تبدیل‌ها:
• متن به ویس بگو [متن] - تبدیل متن به ویس
• متن به عکس [متن] - تبدیل متن به عکس
• متن به گیف [متن] - تبدیل متن به گیف
• save pic - ذخیره عکس (ریپلای)

📝 قابلیت های دیگر:
• schedule [زمان] [پیام] - ارسال پیام زماندار
• spam [تعداد] [پیام] - اسپم پیام
• save - ذخیره پیام (ریپلای)
• saved - نمایش پیام های ذخیره شده
• remind [زمان] [پیام] - تنظیم یادآور
• search [متن] - جستجو در پیام ها
• وضعیت - نمایش وضعیت ربات''')
            except:
                pass

        @client.on(events.NewMessage)
        async def enemy_handler(event):
            global enemies
            
            try:
                if not event.from_id:
                    return
                        
                if event.from_id.user_id != (await client.get_me()).id:
                    return
                
                if event.raw_text == 'تنظیم دشمن' and event.is_reply:
                    replied = await event.get_reply_message()
                    if replied and replied.from_id:
                        enemies.add(str(replied.from_id.user_id))
                        await event.reply('✅ کاربر به لیست دشمن اضافه شد')

                elif event.raw_text == 'حذف دشمن' and event.is_reply:
                    replied = await event.get_reply_message()
                    if replied and replied.from_id:
                        enemies.discard(str(replied.from_id.user_id))
                        await event.reply('✅ کاربر از لیست دشمن حذف شد')

                elif event.raw_text == 'لیست دشمن':
                    enemy_list = ''
                    for enemy in enemies:
                        try:
                            user = await client.get_entity(int(enemy))
                            enemy_list += f'• {user.first_name} {user.last_name or ""}\n'
                        except:
                            enemy_list += f'• ID: {enemy}\n'
                    await event.reply(enemy_list or '❌ لیست دشمن خالی است')

                elif str(event.from_id.user_id) in enemies:
                    insult1 = random.choice(insults)
                    insult2 = random.choice(insults)
                    while insult2 == insult1:
                        insult2 = random.choice(insults)
                    await event.reply(insult1)
                    await asyncio.sleep(0.5)
                    await event.reply(insult2)
            except:
                pass

        @client.on(events.NewMessage)
        async def font_handler(event):
            global current_font
            
            try:
                if not event.from_id or not event.raw_text:
                    return
                            
                if event.from_id.user_id != (await client.get_me()).id:
                    return

                text = event.raw_text.lower().split()
                
                if len(text) == 2 and text[1] in ['on', 'off']:
                    font, status = text
                    if font in ['bold', 'italic', 'script', 'double', 'bubble', 'square']:
                        if status == 'on':
                            current_font = font
                            await event.edit(f'✅ حالت {font} فعال شد')
                        else:
                            current_font = 'normal'
                            await event.edit(f'✅ حالت {font} غیرفعال شد')
                
                elif current_font == 'bold':
                    await event.edit(f"**{event.raw_text}**")
                elif current_font == 'italic':
                    await event.edit(f"__{event.raw_text}__")
                elif current_font == 'script':
                    await event.edit(f"`{event.raw_text}`")
                elif current_font == 'double':
                    await event.edit(f"```{event.raw_text}```")
                elif current_font == 'bubble':
                    await event.edit(f"||{event.raw_text}||")
                elif current_font == 'square':
                    await event.edit(f"```{event.raw_text}```")
            except:
                pass

        @client.on(events.NewMessage)
        async def check_locks(event):
            try:
                chat_id = str(event.chat_id)
                
                if chat_id in locked_chats['forward'] and event.forward:
                    await event.delete()
                    
                if chat_id in locked_chats['copy'] and event.forward_from:
                    await event.delete()
                    
            except Exception as e:
                print(f"Error in check locks: {e}")

        @client.on(events.NewMessage)
        async def message_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return

                if any(word in event.raw_text.lower() for word in spam_words):
                    await event.delete()
                    return

                if actions['typing']:
                    asyncio.create_task(auto_typing(client, event.chat_id))
                
                if actions['reaction']:
                    await auto_reaction(event)

                if event.raw_text.startswith('schedule '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        delay = int(parts[1])
                        message = parts[2]
                        asyncio.create_task(schedule_message(client, event.chat_id, delay, message))
                        await event.reply(f'✅ پیام بعد از {delay} دقیقه ارسال خواهد شد')

                elif event.raw_text.startswith('spam '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        count = int(parts[1])
                        message = parts[2]
                        asyncio.create_task(spam_messages(client, event.chat_id, count, message))

                elif event.raw_text == 'save' and event.is_reply:
                    replied = await event.get_reply_message()
                    saved_messages.append(replied.text)
                    await event.reply('✅ پیام ذخیره شد')

                elif event.raw_text == 'saved':
                    saved_text = '\n'.join(f'{i+1}. {msg}' for i, msg in enumerate(saved_messages))
                    await event.reply(saved_text or '❌ پیامی ذخیره نشده است')

                elif event.raw_text.startswith('remind '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        time = parts[1]
                        message = parts[2]
                        reminders.append((time, message))
                        await event.reply('✅ یادآور تنظیم شد')

                elif event.raw_text.startswith('search '):
                    query = event.raw_text.split(maxsplit=1)[1]
                    messages = await client.get_messages(event.chat_id, search=query)
                    result = '\n'.join(f'• {msg.text}' for msg in messages)
                    await event.reply(result or '❌ پیامی یافت نشد')

                elif event.raw_text in ['typing on', 'typing off']:
                    actions['typing'] = event.raw_text.endswith('on')
                    await event.reply(f"✅ تایپینگ {'فعال' if actions['typing'] else 'غیرفعال'} شد")

                elif event.raw_text in ['online on', 'online off']:
                    actions['online'] = event.raw_text.endswith('on')
                    if actions['online']:
                        asyncio.create_task(auto_online(client))
                    await event.reply(f"✅ آنلاین {'فعال' if actions['online'] else 'غیرفعال'} شد")

                elif event.raw_text in ['reaction on', 'reaction off']:
                    actions['reaction'] = event.raw_text.endswith('on')
                    await event.reply(f"✅ ری‌اکشن {'فعال' if actions['reaction'] else 'غیرفعال'} شد")
            except:
                pass

        @client.on(events.NewMessage(pattern='وضعیت'))
        async def status_handler(event):
            try:
                if not event.from_id:
                    return
                    
                if event.from_id.user_id == (await client.get_me()).id:
                    start_time = time.time()
                    await client(functions.PingRequest(ping_id=0))
                    end_time = time.time()
                    ping = round((end_time - start_time) * 1000, 2)

                    tehran_tz = pytz.timezone('Asia/Tehran')
                    now = datetime.now(tehran_tz)
                    
                    j_date = jdatetime.datetime.fromgregorian(datetime=now)
                    jalali_date = j_date.strftime('%Y/%m/%d')
                    tehran_time = now.strftime('%H:%M:%S')

                    status_text = f"""
⚡️ پینگ ربات: {ping} ms

📅 تاریخ: {jalali_date}
⏰ ساعت: {tehran_time}

💡 وضعیت قابلیت‌ها:
• تایپینگ: {'✅' if actions['typing'] else '❌'}
• آنلاین: {'✅' if actions['online'] else '❌'} 
• ری‌اکشن: {'✅' if actions['reaction'] else '❌'}
• ساعت: {'✅' if time_enabled else '❌'}
"""
                    await event.reply(status_text)
            except Exception as e:
                print(f"Error in status handler: {e}")

        await client.run_until_disconnected()

    except Exception as e:
        print(f"\nخطا: {e}")
        print("لطفا دوباره تلاش کنید\n")

def init():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nخروج از برنامه...")
    except Exception as e:
        print(f"\nخطای غیرمنتظره: {e}")

if __name__ == '__main__':
    init()