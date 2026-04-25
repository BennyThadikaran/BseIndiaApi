from bse import BSE
from os import system
from sys import platform

# Check if system is windows or linux
if 'win' in platform:
    # enable color support in Windows
    system('color')


class C:
    """ANSI color + style helpers for terminal output"""

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    GREEN = "\033[92m"
    DARK_GREEN = "\033[32m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    FAIL = "\033[91m"
    RED = "\033[31m"
    GREY = "\033[90m"

    ENDC = "\033[0m"

    @staticmethod
    def wrap(text, color, bold=False):
        style = ""
        if bold:
            style += C.BOLD
        return f"{style}{color}{text}{C.ENDC}"


def adPercentFormatted(adv, dec, unc=0):
    adv, dec, unc = int(adv), int(dec), int(unc)
    total = adv + dec + unc
    pct = 0 if total == 0 else round((adv / total) * 100, 1)

    sPct = f"{pct:>5.1f}%"

    if pct >= 75:
        s = C.wrap("++ ▲", C.GREEN, bold=True)
    elif pct >= 60:
        s = C.wrap("+  ▲", C.GREEN)
    elif pct >= 52:
        s = C.wrap("-  ▲", C.DARK_GREEN)
    elif pct >= 48:
        s = C.wrap("◀ ▶", C.GREY)
    elif pct >= 35:
        s = C.wrap("-  ▼", C.YELLOW)
    elif pct >= 25:
        s = C.wrap("+  ▼", C.FAIL)
    else:
        s = C.wrap("++ ▼", C.RED, bold=True)

    return f"{s:<12} {sPct}"


broad = {
    "sensex": "Sensex",
    "100": "BSE 100",
    "150 midcap index": "BSE MidCap 150",
    "250 smallcap index": "BSE SmallCap 250",
}
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


sectors = {
    "bankex": "Banking",
    "capital goods": "Capital Goods",
    "capital markets & insurance": "Capital Markets & Insurance",
    "commodities": "Commodities",
    "consumer discretionary": "Consumer Discretionary",
    "consumer durables": "Consumer Durables",
    "cpse": "CPSE",
    "energy": "Energy",
    "fast moving consumer goods": "FMCG",
    "financial services": "Financial Services",
    "focused it": "Focused IT",
    "healthcare": "Healthcare",
    "hospitals": "Hospitals",
    "india defence": "Defence",
    "india infrastructure index": "Infrastructure",
    "india manufacturing index": "Manufacturing",
    "india sector leaders": "Sector Leaders",
    "industrials": "Industrials",
    "information technology": "IT",
    "internet economy": "Internet",
    "metal": "Metals",
}

with BSE("./") as bse:
    data = bse.advanceDecline()

broad_out, sector_out = '', ''

for idx in data:
    name = idx["Sens_ind"].replace("BSE", "").strip().lower()

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
