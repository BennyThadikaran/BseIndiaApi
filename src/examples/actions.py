from bse import BSE
from sys import argv
from datetime import datetime

today = datetime.today().date()

with BSE() as bse:
    code = bse.getScripCode(argv[1])
    data = bse.actions(scripcode=code)


for item in data:
    exDt = datetime.strptime(item['Ex_date'], '%d %b %Y').date()
    recordDt = datetime.strptime(item['BCRD'].split(" ")[1], '%d/%m/%Y').date()
    payDt = item['PAYMENT_DATE'].split("T")[0]

    print('{}: {}\n{}\nEx Date: {}\nPayment Date: {}\n'.format(
        item['short_name'],
        item['purpose'],
        item['BCRD'],
        exDt,
        payDt
    ))
