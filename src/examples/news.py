from bse import BSE
from datetime import datetime, timedelta
from sys import argv

if len(argv) == 1:
    exit(
        'Usage:\npy news.py <symbol> [ count ]\n\nsymbol - Stock symbol name\ncount - No of announcements to print')

sym = argv[1]
toDate = datetime.today()
daysBack = 10
count = int(argv[2]) if len(argv) == 3 else None

attach_url = 'https://www.bseindia.com/xml-data/corpfiling/AttachLive'

fromDate = toDate - timedelta(daysBack)


def is_blacklisted(string):
    string = string.lower()
    filterList = ['investor meet', 'trading window', 'book closure']
    for key in filterList:
        if key in string:
            return True
    return False


def getDate(string):
    dt_str = string.split('.')[0]
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')

    return dt.strftime('%d %b %Y %H:%M')


class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


with BSE() as bse:
    code = bse.getScripCode(sym)
    data = bse.announcements(code, fromDate, toDate)

if not data:
    exit(f'No updates in last {daysBack} days')

# Print the results
text = ''

news_list = data[:int(argv[2])] if len(argv) == 3 else data

for news in news_list:
    if not news['CATEGORYNAME'] or is_blacklisted(news['NEWSSUB']):
        continue

    headline = news['HEADLINE'].replace('<BR> ', '\n')
    dt = getDate(news['NEWS_DT'])

    text += f"{C.BOLD}{C.CYAN}{dt}: {news['CATEGORYNAME']}\n"
    text += f"{C.WARNING}{news['NEWSSUB']}{C.ENDC}\n"
    text += f"{headline}\n"
    text += f"{C.CYAN}{attach_url}/{news['ATTACHMENTNAME']}\n\n"

if not text:
    exit('No updates in last 4 days')

symName = f"{C.BOLD}{C.WARNING}**** {data[0]['SLONGNAME']} ****"
print(symName)
print(text)
print(symName)
