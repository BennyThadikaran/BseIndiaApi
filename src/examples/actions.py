from bse import BSE
from sys import argv
from datetime import datetime

today = datetime.today().date()

if len(argv) == 1:
    exit('Pass an stock symbol')


with BSE() as bse:
    code = bse.getScripCode(argv[1])
    data = bse.actions(scripcode=code)


for item in data:
    sym = item['short_name']
    purpose = item['Purpose']
    ex_date = item['Ex_date']
    record_date = item['RD_Date']
    payment_date = item['payment_date'] or '-'

    if 'Dividend' in purpose:
        # 'Interim Dividend - Rs. - 18.0000' -> split on '-' and strip space chars
        # ['Interim Dividend', 'Rs.'], 18.0000
        *str_lst, dividend = tuple(i.strip() for i in purpose.split('-'))
        purpose = f"{' '.join(str_lst)}{float(dividend)}"

    print(f'{sym}: {purpose}\nEx Date: {ex_date}\nRecord Date: {record_date}',
          f'\nPayment Date: {payment_date}\n')
