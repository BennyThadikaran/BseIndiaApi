# BseIndiaApi
An unofficial python api for BSE India stock exchange.

## Installation
Python version: >= 3.6

Download or clone the repo and install the dependencies: `pip install requests`

## Usage

Using with statement
```python
with BSE() as bse:
    code = bse.getScripCode('tcs') # 532540 bse scrip code

    bse.getScripName('532540') # TCS

    data = bse.corporateActions(code)

    bse.quote(scrip_code) # Open, High, Low, LTP
```
or
```python
bse = BSE()

code = bse.getScripCode('tcs') # 532540 bse scrip code

bse.scripMeta(segment=bse.SEGMENT_EQUITY, status=bse.STATUS_ACTIVE, industry=bse.INDUSTRY_IT)

bse.exit() # close the request session
```

## Available methods

```
Help on class BSE in module BSE:

class BSE(builtins.object)
 |  Unofficial api for BSE India
 |  
 |  Methods defined here:
 |  
 |  __init__(self)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  advanceDecline(self)
 |      returns list of dictionary of advance decline values for each index
 |  
 |  allAnnouncements(self, fromDate, toDate, category='-1')
 |      Returns all news items by date
 |  
 |  allCorporateActions(self)
 |      returns list of dictionary of all corporate actions
 |  
 |  announcements(self, scripcode, fromDate, toDate)
 |      Return Corporate announcements by scripcode and date
 |  
 |  corporateActions(self, scripcode)
 |      Returns Corporate Actions by scripcode
 |
 |  exit(self)
 |  
 |  getScripCode(self, scripname)
 |      returns bse symbol code for stock symbol name
 |  
 |  getScripName(self, scripcode)
 |      returns stock symbol name for bse scrip code
 |  
 |  listSecurities(self, industry='', scripcode='', group='', segment='Equity', status='Active')
 |      List all securities with their meta info or filter by industry etc.
 |  
 |  near52WeekHighLow(self, scripcode='', indexcode='', group='')
 |      Returns stocks near 52 week highs and lows
 |  
 |  quote(self, scripcode)
 |      Get OHLC quotes for given scripcode
 |  
 |  scripMeta(self, scripcode='', segment='Equity', status='Active', group='', industry='')
 |      Return scrip meta info for all stocks or filtered by industry etc
```

## CONSTANTS
```python
# Corporate Announcement categories
CATEGORY_AGM = 'AGM/EGM'
CATEGORY_BOARD_MEETING = 'Board Meeting'
CATEGORY_UPDATE = 'Company Update'
CATEGORY_ACTION = 'Corp. Action'
CATEGORY_INSIDER = 'Insider Trading / SAST'
CATEGORY_NEW_LISTING = 'New Listing'
CATEGORY_RESULT = 'Result'
CATEGORY_OTHERS = 'Others'

# segments
SEGMENT_EQUITY = 'Equity'
SEGMENT_MF = 'MF'
SEGMENT_PREFERENCE_SHARES = 'Preference Shares'
SEGMENT_DEBENTURES_BONDS = 'Debentures and Bonds'
SEGMENT_EQUITY_INSTITUTIONAL = 'Equity - Institutional Series'
SEGMENT_COMMERCIAL_PAPERS = 'Commercial Papers'

# status
STATUS_ACTIVE = 'Active'
STATUS_SUSPENDED = 'Suspended'
STATUS_DELISTED = 'Delisted'

# industry / sector
INDUSTRY_AUTO = 'Automobile and Auto Components'
INDUSTRY_CAPITAL_GOODS = 'Capital Goods'
INDUSTRY_CHEMICALS = 'Chemicals'
INDUSTRY_CONSTRUCTION = 'Construction'
INDUSTRY_CONSTRUCTION_MATERIALS = 'Construction Materials'
INDUSTRY_CONSUMER_DURABLES = 'Consumer Durables'
INDUSTRY_CONSUMER_SERVICES = 'Consumer Services'
INDUSTRY_DIVERSIFIED = 'Diversified'
INDUSTRY_FMCG = 'Fast Moving Consumer Goods'
INDUSTRY_FIN_SERVICES = 'Financial Services'
INDUSTRY_FOREST_MATERIALS = 'Forest Materials'
INDUSTRY_IT = 'Information Technology'
INDUSTRY_MEDIA = 'Media, Entertainment & Publication'
INDUSTRY_METAL_MINING = 'Metals & Mining'
INDUSTRY_OIL_GAS = 'Oil, Gas & Consumable Fuels'
INDUSTRY_POWER = 'Power'
INDUSTRY_REALTY = 'Realty'
INDUSTRY_SERVICES = 'Services'
INDUSTRY_TELECOM = 'Telecommunication'
INDUSTRY_TEXTILES = 'Textiles'
INDUSTRY_UTILITIES = 'Utilities'
```
