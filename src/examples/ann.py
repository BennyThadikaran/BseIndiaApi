from bse import BSE
from datetime import datetime
from re import findall
from os import system
from sys import platform, argv
from json import loads, dumps
from pathlib import Path

# Check if system is windows or linux
if 'win' in platform:
    # enable color support in Windows
    system('color')


def isBlackListed(string):
    string = string.lower()
    filtered_words = [
        'trading window',
        'investor meet',
        'newspaper publication',
        '74(5)',
        '74 (5)'
    ]

    for key in filtered_words:
        if key in string:
            return True

    return False


def formatString(dct):
    string = ''
    purpose = cleanAction(dct['Purpose'])

    dt = datetime.strptime(dct['exdate'], '%Y%m%d').strftime('%d %b %Y')
    string += f"{Fmt.HEADER}{Fmt.BOLD}{dct['short_name']}:".ljust(25)
    string += f"{Fmt.GREEN}{purpose}{Fmt.ENDC}".ljust(48)
    string += dt
    string += '\n'
    return string


def cleanAction(string):
    if not 'Dividend' in string:
        return string

    string = [i.strip() for i in string.split('-')]
    try:
        dividend = float(string[-1])
    except ValueError:
        return ' '.join(string)

    return f"{' '.join(string[:-1])}{dividend}"


def parseComplaints(string):
    m = findall(r'>(\d+)<', string)

    if len(m) < 4:
        return string

    return f'Pending: {m[0]}\nReceived: {m[1]}\nDisposed: {m[2]}\nUnresolved: {m[3]}'


class Fmt:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def mainHeading(string):
        return f"{Fmt.HEADER}{Fmt.BOLD}{Fmt.UNDERLINE}{string}{Fmt.ENDC}"

    @staticmethod
    def annHeading(sym, category):
        return f"{Fmt.CYAN}{Fmt.BOLD}{sym.upper()} - {category}\n"

    @staticmethod
    def annSubject(subject, headline):
        return f"{Fmt.GREEN}{subject}{Fmt.ENDC}\n{headline}"

    @staticmethod
    def url(filename):
        baseurl = 'https://www.bseindia.com/xml-data/corpfiling/AttachLive'
        return f"\n{Fmt.CYAN}{baseurl}/{filename}{Fmt.ENDC}"

    @staticmethod
    def hr():
        return f"\n{'-' * 70}\n\n"


today = datetime.today()

DIR = Path(__file__).parent
WATCH_FILE = DIR / 'watchlist.json'

symList = None

if len(argv) > 1:
    sym_file = Path(argv[1])

    if not sym_file.exists():
        raise FileNotFoundError(f'{argv[1]} not found')

    symList = sym_file.read_text().strip().split('\n')
    watchlist = {}
else:
    watchlist = loads(WATCH_FILE.read_bytes())


with BSE() as bse:
    if symList:
        for sym in symList:
            code = bse.getScripCode(sym)
            watchlist[code] = sym

        WATCH_FILE.write_text(dumps(watchlist, indent=3))

    annList = bse.allAnnouncements(today, today)
    cActs = bse.allCorporateActions()

# Print Announcements
text = ''

for ann in annList:
    code = str(ann['SCRIP_CD'])

    if not (code in watchlist and ann['CATEGORYNAME']):
        continue

    if isBlackListed(ann['NEWSSUB']) or isBlackListed(ann['HEADLINE']):
        continue

    subject = ann['NEWSSUB'].split('-')[2][:70].strip()
    sym = watchlist[code]

    text += Fmt.annHeading(sym, ann['CATEGORYNAME'])

    if 'investor complaints' in subject.lower():
        headline = parseComplaints(ann['HEADLINE'])
    else:
        headline = ann['HEADLINE'].replace('<BR>', '')

    text += Fmt.annSubject(subject, headline)

    if ann['ATTACHMENTNAME']:
        text += Fmt.url(ann['ATTACHMENTNAME'])

    text += Fmt.hr()

print(Fmt.mainHeading('Corporate Announcements'))
print(text)


# Print Actions
portfolio_acts = ''
other_acts = ''

for act in cActs:
    purpose = act['Purpose'].lower()

    if act['scrip_code'] in watchlist:
        portfolio_acts += formatString(act)
    elif 'bonus' in purpose or 'split' in purpose:
        other_acts += formatString(act)

print(Fmt.mainHeading('Corporate Actions'))

if portfolio_acts:
    print(Fmt.BOLD + 'Portfolio:' + Fmt.ENDC)
    print(portfolio_acts)
else:
    print(f'No actions on Portfolio\n')

if other_acts:
    print(Fmt.BOLD + 'Other:' + Fmt.ENDC)
    print(other_acts)
