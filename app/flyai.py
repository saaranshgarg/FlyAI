import json
import os
import random
from datetime import datetime

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


def send_otp(phone):
    otp = random.randint(1000, 9999)
    print(f"\nआपका OTP है: {otp} (मॉक भेजा गया)")
    return str(otp)


def register(data):
    print("\n*** उपयोगकर्ता पंजीकरण ***")
    phone = input("मोबाइल नंबर दर्ज करें: ").strip()
    otp = send_otp(phone)
    user_otp = input("OTP दर्ज करें: ").strip()
    if user_otp != otp:
        print("गलत OTP. पुन: प्रयास करें।")
        return False
    data['user'] = {"phone": phone, "language": "hi"}
    save_data(data)
    print("पंजीकरण सफल!\n")
    return True


def create_booking(data):
    if not data.get('user'):
        print("कृपया पहले पंजीकरण करें।")
        return
    print("\n*** नई बुकिंग ***")
    crop = input("फ़सल का प्रकार: ").strip()
    field_size = input("क्षेत्रफल (हेक्टेयर): ").strip()
    region = input("क्षेत्र: ").strip()
    date_str = input("तारीख/समय (YYYY-MM-DD HH:MM): ").strip()
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    except ValueError:
        print("गलत तारीख प्रारूप।")
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
    print("बुकिंग कन्फर्म्ड! स्थिति: Scheduled\n")


def show_history(data):
    print("\n*** बुकिंग इतिहास ***")
    if not data['bookings']:
        print("कोई बुकिंग नहीं।")
        return
    for b in data['bookings']:
        print(f"#{b['id']} | {b['crop']} | {b['field_size']}ha | {b['region']} | {b['datetime']} | {b['status']}")
    print()


def show_help():
    print("\nसहायता के लिए संपर्क करें:")
    print("फोन: 1800-000-000")
    print("ईमेल: support@flyai.example.com\n")


def main():
    data = load_data()
    if not data.get('user'):
        registered = register(data)
        if not registered:
            return
    while True:
        print("1. नई स्प्रे बुकिंग")
        print("2. बुकिंग इतिहास")
        print("3. सहायता")
        print("4. बाहर निकलें")
        choice = input("चयन करें: ").strip()
        if choice == '1':
            create_booking(data)
        elif choice == '2':
            show_history(data)
        elif choice == '3':
            show_help()
        elif choice == '4':
            break
        else:
            print("अमान्य विकल्प।\n")


if __name__ == '__main__':
    main()
