import json
import os
import random
from datetime import datetime

MESSAGES = {
    'en': {
        'register_title': '*** User Registration ***',
        'enter_phone': 'Enter mobile number: ',
        'enter_otp': 'Enter OTP: ',
        'wrong_otp': 'Wrong OTP. Try again.',
        'register_success': 'Registration successful!\n',
        'language_prompt': 'Select language (en/hi): ',
        'new_booking': '*** New Booking ***',
        'crop': 'Crop type: ',
        'field_size': 'Field size (hectares): ',
        'region': 'Region: ',
        'datetime': 'Date/Time (YYYY-MM-DD HH:MM): ',
        'bad_date': 'Invalid date format.',
        'booking_ok': 'Booking confirmed! Status: Scheduled\n',
        'history': '*** Booking History ***',
        'none': 'No bookings.',
        'help_title': 'Contact for help:',
        'phone': 'Phone: 1800-000-000',
        'email': 'Email: support@flyai.example.com\n',
        'menu_booking': 'New Spray Booking',
        'menu_history': 'Booking History',
        'menu_help': 'Help',
        'menu_exit': 'Exit',
        'choose': 'Choose: ',
        'invalid': 'Invalid option.\n',
        'register_first': 'Please register first.'
    },
    'hi': {
        'register_title': '*** उपयोगकर्ता पंजीकरण ***',
        'enter_phone': 'मोबाइल नंबर दर्ज करें: ',
        'enter_otp': 'OTP दर्ज करें: ',
        'wrong_otp': 'गलत OTP. पुन: प्रयास करें।',
        'register_success': 'पंजीकरण सफल!\n',
        'language_prompt': 'भाषा चुनें (en/hi): ',
        'new_booking': '*** नई बुकिंग ***',
        'crop': 'फ़सल का प्रकार: ',
        'field_size': 'क्षेत्रफल (हेक्टेयर): ',
        'region': 'क्षेत्र: ',
        'datetime': 'तारीख/समय (YYYY-MM-DD HH:MM): ',
        'bad_date': 'गलत तारीख प्रारूप।',
        'booking_ok': 'बुकिंग कन्फर्म्ड! स्थिति: Scheduled\n',
        'history': '*** बुकिंग इतिहास ***',
        'none': 'कोई बुकिंग नहीं।',
        'help_title': 'सहायता के लिए संपर्क करें:',
        'phone': 'फोन: 1800-000-000',
        'email': 'ईमेल: support@flyai.example.com\n',
        'menu_booking': 'नई स्प्रे बुकिंग',
        'menu_history': 'बुकिंग इतिहास',
        'menu_help': 'सहायता',
        'menu_exit': 'बाहर निकलें',
        'choose': 'चयन करें: ',
        'invalid': 'अमान्य विकल्प।\n',
        'register_first': 'कृपया पहले पंजीकरण करें।'
    },
}

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

DEFAULT_DATA = {
    "user": None,
    "bookings": []
}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_DATA.copy()


def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_otp(phone, lang):
    otp = random.randint(1000, 9999)
    msg = 'Your OTP is' if lang == 'en' else 'आपका OTP है'
    print(f"\n{msg}: {otp} (मॉक भेजा गया)")
    return str(otp)


def register(data):
    lang = input(MESSAGES['en']['language_prompt']).strip().lower()
    if lang not in ('en', 'hi'):
        lang = 'en'
    msg = MESSAGES[lang]
    print(f"\n{msg['register_title']}")
    phone = input(msg['enter_phone']).strip()
    otp = send_otp(phone, lang)
    user_otp = input(msg['enter_otp']).strip()
    if user_otp != otp:
        print(msg['wrong_otp'])
        return False
    data['user'] = {"phone": phone, "language": lang}
    save_data(data)
    print(msg['register_success'])
    return True


def create_booking(data):
    if not data.get('user'):
        print(MESSAGES['en']['register_first'])
        return
    lang = data['user'].get('language', 'en')
    msg = MESSAGES[lang]
    print(f"\n{msg['new_booking']}")
    crop = input(msg['crop']).strip()
    field_size = input(msg['field_size']).strip()
    region = input(msg['region']).strip()
    date_str = input(msg['datetime']).strip()
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    except ValueError:
        print(msg['bad_date'])
        return
    booking = {
        "id": len(data['bookings']) + 1,
        "crop": crop,
        "field_size": field_size,
        "region": region,
        "datetime": dt.strftime('%Y-%m-%d %H:%M'),
        "status": "Scheduled"
    }
    data['bookings'].append(booking)
    save_data(data)
    print(msg['booking_ok'])


def show_history(data):
    print("\n*** बुकिंग इतिहास ***")
    if not data['bookings']:
        print("कोई बुकिंग नहीं।")
        return
    for b in data['bookings']:
        print(f"#{b['id']} | {b['crop']} | {b['field_size']}ha | {b['region']} | {b['datetime']} | {b['status']}")
    print()


def show_help(lang='en'):
    msg = MESSAGES[lang]
    print(f"\n{msg['help_title']}")
    print(msg['phone'])
    print(msg['email'])


def main():
    data = load_data()
    if not data.get('user'):
        registered = register(data)
        if not registered:
            return
    while True:
        lang = data.get('user', {}).get('language', 'en')
        msg = MESSAGES[lang]
        print(f"1. {msg['menu_booking']}")
        print(f"2. {msg['menu_history']}")
        print(f"3. {msg['menu_help']}")
        print(f"4. {msg['menu_exit']}")
        choice = input(msg['choose']).strip()
        if choice == '1':
            create_booking(data)
        elif choice == '2':
            show_history(data)
        elif choice == '3':
            show_help(lang)
        elif choice == '4':
            break
        else:
            print(msg['invalid'])


if __name__ == '__main__':
    main()
