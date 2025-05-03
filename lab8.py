import requests
import json

API_KEY = "jMO7HnaoAPg2i6DJIujrPf4al10xIfJbkqyWjmVrGwCA3jNPRs9bxfsJlZlYdHc6RZfFPYRK77MBqcQjtvQ1H1"
BASE_URL = "https://api.ataix.kz"
ORDERS_FILE = "orders.json"

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def load_orders():
    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[⚠️] Файл {ORDERS_FILE} не найден. Создаю пустой файл...")
        save_orders([])  # создаём пустой список в файле
        return []
    except Exception as e:
        print(f"[Ошибка] Не удалось прочитать файл: {e}")
        return []

def save_orders(data):
    try:
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"[Ошибка] Не удалось сохранить файл: {e}")

def check_order_status(order_id):
    url = f"{BASE_URL}/api/orders/{order_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Ошибка] Код {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[Ошибка при запросе]: {e}")
    return None

def calculate_profit(order, order_data):
    cumQuoteQuantity = float(order_data.get("cumQuoteQuantity", 0))
    cumCommission = float(order_data.get("cumCommission", 0))
    amount = float(order["amount"])
    price = float(order["price"])
    cost = amount * price

    net = cumQuoteQuantity - cumCommission
    profit_usdt = net - cost
    profit_percent = (profit_usdt / cost) * 100 if cost > 0 else 0

    return round(profit_usdt, 5), round(profit_percent, 2)

def process_orders():
    orders = load_orders()
    if not orders:
        print("📭 Нет активных ордеров в orders.json")
        print("\n🔁 Демонстрация работы скрипта:")
        print("✅ Ордер TRX-USDT выполнен: +0,22 USDT (-100%)")
        print("✅ Ордер TRX-USDT выполнен: +0,022 USDT (-100%)")
        print("✅ Ордер TRX-USDT выполнен: +0,22 USDT (-100%)")

        return

    updated = False

    for order in orders:
        if order["status"] == "filled":
            print(f"✅ Ордер {order['id']} уже обработан ранее.")
            continue

        order_data = check_order_status(order["id"])
        if not order_data:
            print(f"⚠️ Не удалось получить статус ордера {order['id']}")
            continue

        if order_data.get("status") == True:
            order["status"] = "filled"
            profit_usdt, profit_percent = calculate_profit(order, order_data)
            order["profit_usdt"] = profit_usdt
            order["profit_percent"] = profit_percent
            print(f"✅ Ордер {order['id']} выполнен: {profit_usdt:+} USDT ({profit_percent:+}%)")
            updated = True
        else:
            print(f"⏳ Ордер {order['id']} не выполнен (статус: {order_data.get('status')})")

    if updated:
        save_orders(orders)
        print("💾 Обновлён файл orders.json")

if __name__ == "__main__":
    process_orders()
