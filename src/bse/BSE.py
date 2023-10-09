from requests import Session
from requests.exceptions import ReadTimeout
from .Throttle import Throttle
from re import search

throttle_config = {
    'lookup': {
        'rps': 15,
    },
    'default': {
        'rps': 8,
    }
}


th = Throttle(throttle_config, 15)


class BSE:
    '''Unofficial api for BSE India'''

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

    def __init__(self):
        self.session = Session()
        self.dateFmt = '%Y%m%d'
        self.base = 'https://api.bseindia.com/BseIndiaAPI/api'
        ua = 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'

        self.session.headers.update({
            'User-Agent': ua,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.bseindia.com',
            'Referer': 'https://www.bseindia.com/',
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()
        if exc_type:
            exit(f'{exc_type}: {exc_value} | {exc_traceback}')
        return True

    def exit(self):
        self.session.close()

    def _req(self, url, params=None, timeout=10):
        try:
            response = self.session.get(url,
                                        params=params,
                                        timeout=timeout)
        except ReadTimeout:
            raise TimeoutError('Request timed out')

        if not response.ok:
            raise ConnectionError(f'{response.status_code}: {response.reason}')

        return response

    def _lookup(self, scrip):
        '''return scripname if scrip is a bse scrip code and vice versa'''

        url = self.base + '/PeerSmartSearch/w'

        params = {
            'Type': 'SS',
            'text': scrip
        }

        th.check('lookup')

        response = self._req(url, params)

        return response.text.replace('&nbsp;', ' ')

    def announcements(self, scripcode, fromDate, toDate):
        '''Return Corporate announcements by scripcode and date'''

        url = 'https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w'

        params = {
            'strCat': '-1',
            'strPrevDate': fromDate.strftime(self.dateFmt),
            'strToDate': toDate.strftime(self.dateFmt),
            'strScrip': scripcode,
            'strSearch': 'P',
            'strType': 'C',
        }

        th.check('default')

        response = self._req(url, params)

        data = response.json()

        return data['Table']

    def corporateActions(self, scripcode):
        '''Returns Corporate Actions by scripcode'''

        url = self.base + '/CorporateAction/w'

        params = {
            'scripcode': scripcode
        }

        th.check('default')

        response = self._req(url, params)

        data = response.json()

        data['dividend'] = data.pop('Table')
        data['bonus'] = data.pop('Table1')
        data['recent_actions'] = data.pop('Table2')

        return data

    def allAnnouncements(self, fromDate, toDate, category='-1'):
        '''Returns all news items by date'''

        url = self.base + '/AnnGetData/w'
        output = []
        pageCount = None

        params = {
            'pageno': 1,
            'strCat': category,
            'strPrevDate': fromDate.strftime(self.dateFmt),
            'strScrip': '',
            'strSearch': 'P',
            'strToDate': toDate.strftime(self.dateFmt),
            'strType': 'C',
        }

        while True:
            th.check('default')

            response = self._req(url, params)

            data = response.json()

            if params['pageno'] == 1:
                newsCount = data['Table1'][0]['ROWCNT']
                length = len(data['Table'])
                pageCount = newsCount // length + (newsCount % length > 0)

            output.extend(data['Table'])

            if params['pageno'] == pageCount:
                break

            params['pageno'] += 1

        return output

    def allCorporateActions(self):
        '''returns list of dictionary of all corporate actions'''

        url = self.base + '/DefaultData/w'

        params = {
            'ddlcategorys': 'E',
            'segment': '0',
            'strSearch': 'S'
        }

        th.check('default')

        response = self._req(url, params)

        return response.json()

    def advanceDecline(self):
        '''returns list of dictionary of advance decline values for each index'''

        url = self.base + '/advanceDecline/w'

        th.check('default')

        response = self._req(url, {'val': 'Index'})

        return response.json()

    def near52WeekHighLow(self, scripcode='', indexcode='', group=''):
        '''Returns stocks near 52 week highs and lows'''

        url = f'{self.base}/MktHighLowData/w'

        params = {
            'Grpcode': group,
            'HLflag': 'H',
            'indexcode': indexcode,
            'scripcode': scripcode
        }

        th.check('default')

        response = self._req(url, params)

        data = response.json()
        data['highs'] = data.pop('Table')
        data['lows'] = data.pop('Table1')
        return data

    def quote(self, scripcode):
        '''Get OHLC quotes for given scripcode'''

        url = self.base + '/getScripHeaderData/w'

        params = {
            'Debtflag': '',
            'scripcode': scripcode,
            'seriesid': '',
        }

        th.check('default')

        response = self._req(url, params).json()['Header']

        fields = ('PrevClose', 'Open', 'High', 'Low', 'LTP')

        data = {}

        for k in fields:
            data[k] = float(response[k])

        return data

    def scripMeta(self,
                  scripcode='',
                  segment='Equity',
                  status='Active',
                  group='',
                  industry=''):
        '''Return scrip meta info for all stocks or filtered by industry etc'''

        url = f'{self.base}/ListofScripData/w'

        params = {
            'Group': group,
            'Scripcode': scripcode,
            'industry': industry,
            'segment': segment,
            'status': status,
        }

        th.check('default')

        res = self._req(url, params)

        return res.json()

    def listSecurities(self,
                       industry='',
                       scripcode='',
                       group='',
                       segment='Equity',
                       status='Active'):
        '''List all securities with their meta info or filter by industry etc.'''

        url = self.base + '/ListofScripData/w'

        params = {
            'scripcode': scripcode,
            'Group': group,
            'industry': industry,
            'segment': segment,
            'status': status,
        }

        th.check('default')

        response = self._req(url, params)

        return response.json()

    def getScripName(self, scripcode):
        '''returns stock symbol name for bse scrip code'''

        # <span>HDFC   INE001A01036<strong>500010
        regex = rf'<\w+>([A-Z0-9]+)\s+\w+\s+<\w+>{scripcode}'

        response = self._lookup(scripcode)
        match = search(regex, response)

        if match:
            return match.group(1)

        raise ValueError(f'Could not find scrip name for {scripcode}')

    def getScripCode(self, scripname):
        '''returns bse symbol code for stock symbol name'''
        # <strong>HDFC</strong>   INE001A01036   500010
        regex = rf'<\w+>{scripname.upper()}<\/\w+>\s+\w+\s+(\d{{6}})'

        response = self._lookup(scripname)
        match = search(regex, response)

        if match:
            return match.group(1)

        raise ValueError(f'Could not find scrip code for {scripname}')
