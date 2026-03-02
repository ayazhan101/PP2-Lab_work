import re
import json

receipt = """
ДУБЛИКАТ
Филиал ТОО EUROPHARMA Астана
БИН 080841000762

1.
Натрия хлорид 0,9%, 200 мл, фл
2,000 x 154,00
308,00

2.
Борный спирт 3%, 20 мл, фл.
1,000 x 51,00
51,00

3.
Шприц 2 мл, 3-х комп. (Bioject)
2,000 x 16,00
32,00

Банковская карта:
18 009,00
ИТОГО:
18 009,00

Время: 18.04.2019 11:13:58
"""

#1

price_pattern = r"\d[\d\s]*,\d{2}"

prices = re.findall(price_pattern, receipt)

clean_prices = []

for p in prices:
    number = p.replace(" ", "").replace(",", ".")
    clean_prices.append(float(number))


#2

product_pattern = r"\d+\.\s*\n(.+)"

products = re.findall(product_pattern, receipt)


#3

total_pattern = r"ИТОГО:\s*\n?([\d\s]+,\d{2})"

total_match = re.search(total_pattern, receipt)

if total_match:
    total = total_match.group(1)
    total = float(total.replace(" ", "").replace(",", "."))
else:
    total = None


#4

datetime_pattern = r"\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2}"

datetime_match = re.search(datetime_pattern, receipt)

if datetime_match:
    datetime = datetime_match.group()
else:
    datetime = None


#5

payment_pattern = r"(Банковская карта|Наличные)"

payment_match = re.search(payment_pattern, receipt)

if payment_match:
    payment_method = payment_match.group()
else:
    payment_method = None


#6

data = {
    "products": products,
    "prices": clean_prices,
    "total": total,
    "payment_method": payment_method,
    "datetime": datetime
}

print(json.dumps(data, indent=4, ensure_ascii=False))