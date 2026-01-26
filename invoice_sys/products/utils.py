# utils.py
CURRENCY_RATES = {
    "USD": 50,   # 1 دولار = 50 جنيه (مثال)
    "EUR": 55,   # 1 يورو = 55 جنيه
    "EGP": 1,
}

def convert_to_egp(amount, currency):
    rate = CURRENCY_RATES.get(currency, 1)
    return amount * rate
