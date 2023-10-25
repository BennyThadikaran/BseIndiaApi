from bse import BSE
from os import system
from sys import platform

# Check if system is windows or linux
if 'win' in platform:
    # enable color support in Windows
    system('color')


class C:
    '''Color values for terminal'''

    GREEN = '\033[92m'
    CYAN = '\033[96m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def adRatio(adv, dec):
    return 0 if adv == 0 else (adv if dec == 0 else round(adv / dec, 2))


def adRatioFormatted(adv, dec):
    ratio = adRatio(int(adv), int(dec))
    sRatio = str(ratio).ljust(5)

    if ratio >= 1.5:
        s = f'{C.GREEN}++ ▲'
    elif 1 <= ratio < 1.5:
        s = f'{C.GREEN}+  ▲'
    elif 0.8 <= ratio < 1:
        s = f'{C.GREEN}-  ▲'
    elif 0.5 <= ratio < 0.8:
        s = f'{C.CYAN}◀ ▶'
    elif 0.3 <= ratio < 0.5:
        s = f'{C.FAIL}+  ▼'
    else:
        s = f'{C.FAIL}++ ▼'

    return f'{s.ljust(10)}{C.ENDC} {sRatio}'.ljust(11)


broad = {
    '100': '100',
    'midcap': 'Midcap',
    'smallcap': 'Smallcap'
}

sector = {
    'auto': 'Auto',
    'bankex': 'Banking',
    'basic materials': 'Materials',
    'capital goods': 'Capital Goods',
    'consumer discretionary goods & services': 'Con Discretionary',
    'consumer durables': 'Con Durables',
    'energy': 'Energy',
    'fast moving consumer goods': 'FMCG',
    'finance': 'Finance',
    'healthcare': 'Healthcare',
    'industrials': 'Industrials',
    'information technology': 'Info Tech',
    'metal': 'Metal',
    'oil & gas': 'Oil & Gas',
    'realty': 'Realty',
    'telecom': 'Telecom',
    'utilities': 'Utilities'
}

with BSE() as bse:
    data = bse.advanceDecline()

broad_out, sector_out = '', ''

for idx in data:
    name = idx['Sens_ind'][8:].lower()

    if name in broad:

        idx_name = f'BSE {broad[name].ljust(10)}'

        ratio = adRatioFormatted(idx['UP'], idx['DN'])
        up = idx['UP'].ljust(8)
        down = idx['DN'].ljust(8)
        unchanged = idx['UC'].ljust(2)

        broad_out += f"{idx_name}: {ratio} ▲ {up} ▼ {down} {unchanged}\n"

    if name in sector:
        ratio = adRatioFormatted(idx['UP'], idx['DN'])
        idx_name = sector[name].ljust(24)
        up = idx['UP'].ljust(4)
        down = idx['DN'].ljust(4)
        unchanged = idx['UC'].ljust(2)

        sector_out += f"{idx_name}: {ratio}   ▲ {up}   ▼ {down}  {unchanged}\n"

HR = '-' * 58

print(f'{C.CYAN}++ : Very Strong   + : Strong     -   : Weak')

print(f'▲  : Uptrend       ▼ : Downtrend  ◀ ▶ : Neutral{C.ENDC}\n')

print(f"{C.CYAN}Broad Market\n{HR}{C.ENDC}\n{broad_out}")

print(f"{C.CYAN}Sector Wise\n{HR}{C.ENDC}\n{sector_out}")
