from requests import Session
from requests.exceptions import ReadTimeout
from re import search
from pathlib import Path
from zipfile import ZipFile
from mthrottle import Throttle
from typing import Literal
from datetime import datetime

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
    '''Unofficial Python Api for BSE India'''

    base_url = 'https://www.bseindia.com/'
    api_url = 'https://api.bseindia.com/BseIndiaAPI/api'

    valid_groups = ('A', 'B', 'E', 'F', 'FC', 'GC', 'I', 'IF', 'IP', 'M', 'MS',
                    'MT', 'P', 'R', 'T', 'TS', 'W', 'X', 'XD', 'XT', 'Y', 'Z',
                    'ZP', 'ZY')

    def __init__(self):
        self.session = Session()
        ua = 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/118.0'

        self.session.headers.update({
            'User-Agent': ua,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': self.base_url,
            'Referer': self.base_url,
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()

        if exc_type:
            exit(f'{exc_type}: {exc_value} | {exc_traceback}')

        return True

    def exit(self):
        '''Close the Request session'''

        self.session.close()

    @staticmethod
    def __unzip(file: Path, folder: Path):
        with ZipFile(file) as zip:
            filepath = zip.extract(member=zip.namelist()[0], path=folder)

        file.unlink()

        return Path(filepath)

    def __download(self, url: str, folder: Path):
        '''Download a large file in chunks from the given url.
        Returns pathlib.Path object of the downloaded file'''

        fname = folder / url.split("/")[-1]

        th.check()

        try:
            with self.session.get(url,
                                  stream=True,
                                  timeout=15) as r:

                with fname.open(mode='wb') as f:
                    for chunk in r.iter_content(chunk_size=1000000):
                        f.write(chunk)
        except Exception as e:
            exit(f'Download error. Try again later: {e!r}')

        return fname

    def __req(self, url, params=None, timeout=10):
        try:
            response = self.session.get(url,
                                        params=params,
                                        timeout=timeout)
        except ReadTimeout:
            raise TimeoutError('Request timed out')

        if not response.ok:
            raise ConnectionError(f'{response.status_code}: {response.reason}')

        return response

    def __lookup(self, scrip):
        '''return scripname if scrip is a bse scrip code and vice versa'''

        url = f'{self.api_url}/PeerSmartSearch/w'

        params = {
            'Type': 'SS',
            'text': scrip
        }

        th.check('lookup')

        response = self.__req(url, params)

        return response.text.replace('&nbsp;', ' ')

    @staticmethod
    def __getPath(path: str | Path, isFolder: bool = False):
        path = path if isinstance(path, Path) else Path(path)

        if isFolder:
            if path.is_file():
                raise ValueError(f'{path}: must be a folder')

            if not path.exists():
                path.mkdir(parents=True)

        return path

    def bhavcopyReport(self, date: datetime, folder: str | Path):
        '''
        Download the daily bhavcopy report for specified ``date``

        :param date: date of report
        :type date: datetime.datetime
        :param folder: dir/folder to download the file to
        :type folder: str or pathlib.Path
        :raise ValueError: if ``folder`` is not a dir/folder.
        :raise FileNotFoundError: if file download failed or file is corrupt.
        :return: file path of downloaded report
        :rtype: pathlib.Path

        Zip file is extracted and saved filepath returned.
        '''

        folder = BSE.__getPath(folder, isFolder=True)

        url = f'{self.base_url}/download/BhavCopy/Equity/EQ_ISINCODE_{date:%d%m%y}.zip'

        file = self.__download(url, folder)

        if not file.is_file() or file.stat().st_size < 5000:
            file.unlink()
            raise FileNotFoundError(f'Failed to download file: {file.name}')

        return BSE.__unzip(file, file.parent)

    def deliveryReport(self, date: datetime, folder: str | Path):
        '''
        Download the daily delivery report for specified ``date``

        :param date: date of report
        :type date: datetime.datetime
        :param folder: dir/folder to download the file to
        :type folder: str or pathlib.Path
        :raise ValueError: if ``folder`` is not a dir/folder.
        :raise FileNotFoundError: if file download failed or file is corrupt.
        :return: file path of downloaded report
        :rtype: pathlib.Path

        Zip file is extracted, converted to CSV, and saved filepath is returned
        '''

        folder = BSE.__getPath(folder, isFolder=True)

        url = f'{self.base_url}/BSEDATA/gross/{date:%Y}/SCBSEALL{date:%d%m}.zip'

        file = self.__download(url, folder)

        if not file.is_file() or file.stat().st_size < 5000:
            file.unlink()
            raise FileNotFoundError(f'Failed to download file: {file.name}')

        file = BSE.__unzip(file, file.parent)

        file.write_bytes(file.read_bytes().replace(b'|', b','))

        return file.rename(file.with_suffix('.csv'))

    def announcements(self,
                      page_no: int = 1,
                      from_date: datetime | None = None,
                      to_date: datetime | None = None,
                      segment: Literal['equity', 'debt', 'mf_etf'] = 'equity',
                      scripcode: str | None = None,
                      category: str = '-1',
                      subcategory: str = '-1') -> dict[str, list[dict]]:
        '''
        All corporate announcements

        :param from_date: (Optional) From date.
        :type from_date: datetime.datetime or None
        :param to_date: (Optional) To date.
        :type to_date: datetime.datetime or None
        :param segment: Default ``equity``. One of ``equity``, ``debt`` or ``mf_etf``.
        :type segment: str
        :param category: (Optional) Filter announcements by category ex. ``Corp. Action``
        :type category: str
        :param subcategory: (Optional). Filter announcements by subcategory ex. ``Dividend``.
        :type subcategory: str
        :raise ValueError: if ``from_date`` is greater than ``to_date`` or ``subcategory`` argument is passed without ``category``
        :return: All announcements. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/announcements.json>`__
        :rtype: dict[str, list[dict]]

        Response is a dictionary containing ``Table`` and ``Table1`` keys.

        - Response is paginated. Increment the ``page_no`` on every call, to get all announcements.

        - ``Table`` is a list of dictionary announcements.

        - ``data['Table1'][0]['ROWCNT']`` is an integer total of all announcements. Use this info, to increment ``page_no``

        With no arguments, returns all announcements for current day and time by ``page_no``.

        .. NOTE::
            In most cases, it is faster and more bandwidth efficient to lookup
            by ``scripcode``.
            Unless you specifically need to download all announcements.
            On a typical day, BSE could have 50+ pages and 2K+ announcements.

        Provide ``from_date`` and ``to_date`` to return announcements in date range.
        If not provided, the current date and time is considered.

        Provide ``scripcode`` to return announcements for the specified stock.

        Provide ``category`` and or ``subcategory`` to filter announcements.

        - ``subcategory`` is specific to ``category``.
        - ``category`` is required if ``subcategory`` is passed.

        **Available Constants:**

        - **segment**: ``bse.constants.SEGMENT``

        - **category**: ``bse.constants.CATEGORY``
        '''

        _type = 'C' if segment == 'equity' else (
            'D' if segment == 'debt' else 'M')

        if not from_date:
            from_date = datetime.now()

        if not to_date:
            to_date = datetime.now()

        if from_date > to_date:
            raise ValueError("'from_date' cannot be greater than 'to_date'")

        if subcategory != '-1' and category == '-1':
            raise ValueError(
                f"Specify a 'category' for subcategory: {subcategory}")

        url = f'{self.api_url}/AnnSubCategoryGetData/w'

        fmt = '%Y%m%d'

        params = {
            'pageno': page_no,
            'strCat': category,
            'subcategory': subcategory,
            'strPrevDate': from_date.strftime(fmt),
            'strToDate': to_date.strftime(fmt),
            'strSearch': 'P',
            'strscrip': scripcode,
            'strType': _type,
        }

        th.check()
        return self.__req(url, params).json()

    def actions(self,
                segment: Literal['equity', 'debt', 'mf_etf'] = 'equity',
                from_date: datetime | None = None,
                to_date: datetime | None = None,
                by_date: Literal['ex', 'record', 'bc_start'] = 'ex',
                scripcode: str | None = None,
                sector: str = '',
                purpose_code: str | None = None) -> list[dict]:
        '''
        All forthcoming corporate actions

        :param segment: Default ``equity``. One of ``equity``, ``debt`` or ``mf_etf``.
        :type segment: str
        :param from_date: (Optional). From date. Defaults to ``datetime.datetime.now()``
        :type from_date: datetime.datetime
        :param to_date: (Optional). To date. Defaults to ``datetime.datetime.now()``
        :type to_date: datetime.datetime
        :param by_date: Default ``ex``. One of ``ex``, ``record``, ``bc_start``
        :type by_date: str
        :param scripcode: (Optional) Limit result to stock symbol
        :type scripcode: str
        :param sector: (Optional) Limit results to stocks from sector.
        :type sector: str
        :param purpose_code: Limit result to actions with given purpose
        :type purpose_code: str
        :raise ValueError: if ``from_date`` is greater than ``to_date``
        :return: List of actions. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/actions.json>`__
        :rtype: list[dict]

        With no arguments, returns all forthcoming corp. actions.

        Provide ``from_date`` and ``to_date`` to return corp. actions in date range

        By default, actions are returned by Ex date. To change this, specify ``by_date`` as ``record`` (record date) or ``bc_start`` (book closure start date)

        Provide ``scripcode`` to return actions for the specified stock.

        Provide ``sector`` to limit results to stocks in given sector.

        Provide ``purpose_code`` to limit actions to given purpose ex. ``P5`` for bonus. Use ``bse.constants.PURPOSE`` to pass argument.

        **Available Constants:**

        - **sector**: ``bse.constants.SECTOR``

        - **purpose_code**: ``bse.constants.PURPOSE``
        '''

        _type = '0' if segment == 'equity' else (
            '1' if segment == 'debt' else '2')

        by = 'E' if by_date == 'ex' else ('R' if by_date == 'record' else 'B')

        params = {
            'ddlcategorys': by,
            'ddlindustrys': sector,
            'segment': _type,
            'strSearch': 'D',
        }

        if from_date and to_date:
            if from_date > to_date:
                raise ValueError(
                    "'from_date' cannot be greater than 'to_date'")

            fmt = '%Y%m%d'

            params.update({
                'Fdate': from_date.strftime(fmt),
                'TDate': to_date.strftime(fmt)
            })

        if purpose_code:
            params['Purposecode'] = purpose_code

        if scripcode:
            params['scripcode'] = scripcode

        return self.__req(f'{self.api_url}/DefaultData/w', params).json()

    def resultCalendar(self,
                       from_date: datetime | None = None,
                       to_date: datetime | None = None,
                       scripcode: str | None = None) -> list[dict]:
        '''
        Corporate result calendar

        :param from_date: (Optional). From date.
        :type from_date: datetime.datetime
        :param to_date: (Optional). To date
        :type to_date: datetime.datetime
        :param scripcode: (Optional). Limit result to stock symbol
        :type scripcode: str
        :raise ValueError: if ``from_date`` is greater than ``to_date``
        :return: List of Corporate results. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/resultCalendar.json>`__
        :rtype: list[dict]

        With no parameters, returns all forthcoming result dates.

        Provide ``from_date`` and ``to_date`` to filter by date range.

        Provide ``scripcode`` to filter by stock.
        '''

        params = {}

        if from_date and to_date:
            if from_date > to_date:
                raise ValueError(
                    "'from_date' cannot be greater than 'to_date'")

            fmt = '%Y%m%d'

            params.update({
                'fromdate': from_date.strftime(fmt),
                'todate': to_date.strftime(fmt)
            })

        if scripcode:
            params['scripcode'] = scripcode

        url = f'{self.api_url}/Corpforthresults/w'

        return self.__req(url, params=params).json()

    def advanceDecline(self) -> list[dict]:
        '''
        Advance decline values for all BSE indices

        :return: Advance decline values. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/advanceDecline.json>`__
        :rtype: list[dict]
        '''

        url = f'{self.api_url}/advanceDecline/w'

        th.check()

        response = self.__req(url, {'val': 'Index'})

        return response.json()

    def gainers(self,
                by: Literal['group', 'index', 'all'] = 'group',
                name: str | None = None,
                pct_change: Literal['all', '10', '5', '2', '0'] = 'all') -> list[dict]:
        '''
        List of top gainers

        :param by: Default ``group``. One of ``group``, ``index`` or ``all``.
        :type by: str
        :param name: (Optional). Stock group name or Market index name.
        :type name: str
        :param pct_change: Default ``all``. Filter stocks by percent change. One of ``10``, ``5``, ``2``, ``0``.
        :type pct_change: str
        :raise ValueError: if ``name`` is not a valid BSE stock group.
        :return: List of top gainers by percent change. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/gainers.json>`__
        :rtype: list[dict]

        When ``by`` is ``group``, ``name`` defaults to BSE stock group ``A``.

        When ``by`` is ``index``, ``name`` defaults to market index ``S&P BSE SENSEX``.

        When ``by`` is ``all``, ``name`` is ignored.

        By default, all stocks are returned. If ``pct_change`` is provided,
        stocks are filtered by range of percent change.

        - ``10``: greater than 10%

        - ``5``: 5% to 10%

        - ``2``: 2% to 5%

        - ``0``: upto 2%

        **Available Constants:**

        - **name**: ``bse.constants.INDEX``. Only if ``by`` is set to ``index``
        '''

        params = {
            'GLtype': 'gainer',
            'IndxGrp': by,
            'orderby': pct_change,
        }

        if by == 'group':
            if name is None:
                params['IndxGrpval'] = 'A'
            else:
                if not name.upper() in self.valid_groups:
                    raise ValueError(f'{name}: Not a valid BSE stock group')

                params['IndxGrpval'] = name
        elif by == 'index':
            if name is None:
                params['IndxGrpval'] = 'S&P BSE SENSEX'
            else:
                params['IndxGrpval'] = name.upper()

        url = f'{self.api_url}/MktRGainerLoserData/w'

        return self.__req(url, params=params).json()['Table']

    def losers(self,
               by: Literal['group', 'index', 'all'] = 'group',
               name: str | None = None,
               pct_change: Literal['all', '10', '5', '2', '0'] = 'all') -> list[dict]:
        '''
        List of top losers

        :param by: Default ``group``. One of ``group``, ``index`` or ``all``.
        :type by: str
        :param name: (Optional). Stock group name or Market index name.
        :type name: str
        :param pct_change: Default ``all``. Filter stocks by percent change. One of ``10``, ``5``, ``2``, ``0``.
        :type pct_change: str
        :raise ValueError: if ``name`` is not a valid BSE stock group.
        :return: List of top losers by percent change. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/losers.json>`__
        :rtype: list[dict]

        When ``by`` is ``group``, ``name`` defaults to BSE stock group ``A``.

        When ``by`` is ``index``, ``name`` defaults to market index ``S&P BSE SENSEX``.

        When ``by`` is ``all``, ``name`` is ignored.

        By default, all stocks are returned. If ``pct_change`` is provided,
        stocks are filtered by range of percent change.

        - ``10``: less than -10%

        - ``5``: -5% to -10%

        - ``2``: -2% to -5%

        - ``0``: upto -2%

        **Available Constants:**

        - **name**: ``bse.constants.INDEX``. Only if ``by`` is set to ``index``
        '''

        params = {
            'GLtype': 'loser',
            'IndxGrp': by,
            'IndxGrpval': name,
            'orderby': pct_change,
        }

        if by == 'group':
            if name is None:
                params['IndxGrpval'] = 'A'
            else:
                if not name.upper() in self.valid_groups:
                    raise ValueError(f'{name}: Not a valid BSE group')

                params['IndxGrpval'] = name

        if by == 'index':
            if name is None:
                params['IndxGrpval'] = 'S&P BSE SENSEX'
            else:
                params['IndxGrpval'] = name.upper()

        url = f'{self.api_url}/MktRGainerLoserData/w'

        return self.__req(url, params=params).json()['Table']

    def near52WeekHighLow(self,
                          by: Literal['group', 'index', 'all'] = 'group',
                          name: str | None = None) -> dict[str, list[dict]]:
        '''
        Get stocks near 52 week highs and lows

        :param by: Default ``group``. One of ``group``, ``index`` or ``all``.
        :type by: str
        :param name: (Optional). Stock group name or Market index name.
        :type name: str
        :raise ValueError: if ``name`` is not a valid BSE stock group.
        :return: Stocks near 52 week high and lows. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/near52WeekHighLow.json>`__
        :rtype: dict

        - When ``by`` is ``group``, ``name`` defaults to BSE stock group ``A``.

        - When ``by`` is ``index``, ``name`` defaults to market index ``S&P BSE SENSEX``.

        - When ``by`` is ``all``, ``name`` is ignored.

        The result is a dictionary with keys ``high`` and ``low``.

        - ``high`` is a list of dictionary containing stocks near 52 week high.

        - ``low`` is a list of dictionary containing stocks near 52 week low.

        **Available Constants:**

        - **name**: ``bse.constants.INDEX``. Only if ``by`` is set to ``index``
        '''

        url = f'{self.api_url}/MktHighLowData/w'

        params = {
            'HLflag': 'H',
            'Grpcode': '',
            'indexcode': '',
            'scripcode': ''
        }

        if by == 'group':
            if name is None:
                params['Grpcode'] = 'A'
            else:
                if not name.upper() in self.valid_groups:
                    raise ValueError(f'{name}: Not a valid BSE stock group')

                params['Grpcode'] = name
        elif by == 'index':
            if name is None:
                params['indexcode'] = 'S&P BSE SENSEX'
            else:
                params['indexcode'] = name

        th.check()

        response = self.__req(url, params)

        data = response.json()

        if 'Table' in data:
            data['highs'] = data.pop('Table')

        if 'Table1' in data:
            data['lows'] = data.pop('Table1')

        return data

    def quote(self, scripcode) -> dict[str, float]:
        '''
        Get OHLC quotes for given scripcode

        :param scripcode: BSE scrip code
        :type scripcode: str
        :return: OHLC data for given scripcode. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/quote.json>`__
        :rtype: dict[str, float]
        '''

        url = f'{self.api_url}/getScripHeaderData/w'

        params = {
            'scripcode': scripcode,
        }

        th.check()

        response = self.__req(url, params).json()['Header']

        fields = ('PrevClose', 'Open', 'High', 'Low', 'LTP')

        data = {}

        for k in fields:
            data[k] = float(response[k])

        return data

    def quoteWeeklyHL(self, scripcode) -> dict:
        '''
        Get 52 week and monthly high & low data for given stock.

        :param scripcode: BSE scrip code
        :type scripcode: str
        :return: Weekly and monthly high and lows with dates. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/quoteWeeklyHL.json>`__
        :rtype: dict
        '''

        params = {
            'Type': 'EQ',
            'flag': 'C',
            'scripcode': scripcode
        }

        th.check()

        data = self.__req(f'{self.api_url}/HighLow/w', params=params).json()

        wHigh, wLow = data['WeekHighLow'].split(' / ')
        mHigh, mLow = data['MonthHighLow'].split(' / ')

        return {
            'fifty2WeekHigh': float(data['Fifty2WkHigh_adj']),
            'dateHigh': data['Fifty2WkHigh_adjDt'].strip(' ()'),
            'fifty2WeekLow': float(data['Fifty2WkLow_adj']),
            'dateLow': data['Fifty2WkLow_adjDt'].strip(' ()'),
            'monthlyHigh': float(mHigh),
            'monthlyLow': float(mLow),
            'weeklyHigh': float(wHigh),
            'weeklyLow': float(wLow)
        }

    def listSecurities(self,
                       industry: str = '',
                       scripcode: str = '',
                       group: str = 'A',
                       segment: str = 'Equity',
                       status: str = 'Active') -> list[dict]:
        '''
        List all securities and their meta info like symbol code, ISIN code, industry, market cap, segment, group etc.

        :param industry: (Optional) Filter by industry name
        :type industry: str
        :param scripcode: (Optional) BSE scrip code
        :type scripcode: str
        :param group: Default 'A'. BSE stock group
        :type group: str
        :param segment: Default 'Equity'. One of ``equity``, ``mf``, ``Preference Shares``, ``Debentures and Bonds``, ``Equity - Institutional Series``, ``Commercial Papers``
        :param status: Default 'Active'. One of ``active``, ``suspended``, or ``delisted``
        :raise ValueError: if ``group`` is not a valid BSE stock group
        :return: list of securities with meta info. `Sample response <https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/samples/listSecurities.json>`__
        :rtype: list[dict]

        With no arguments, returns all active A group equity stocks

        **Available Constants:**

        - **industry**: ``bse.constants.INDUSTRY``

        - **segment**: ``bse.constants.SEGMENT``

        - **status**: ``bse.constants.STATUS``
        '''

        url = f'{self.api_url}/ListofScripData/w'

        params = {
            'scripcode': scripcode,
            'Group': group,
            'industry': industry,
            'segment': segment,
            'status': status,
        }

        if group:
            group = group.upper()

            if not group.upper() in self.valid_groups:
                raise ValueError('{group} not a valid BSE stock group')

            params['Group'] = group

        th.check()

        response = self.__req(url, params)

        return response.json()

    def getScripName(self, scripcode) -> str:
        '''
        Get stock symbol name for BSE scrip code

        :param scripcode: BSE scrip code
        :raise ValueError: if scrip not found
        :return: Symbol code
        :rtype: str

        Example
        500180 -> 'HDFCBANK'
        '''

        # <span>HDFC   INE001A01036<strong>500010
        regex = rf'<\w+>([A-Z0-9]+)\s+\w+\s+<\w+>{scripcode}'

        response = self.__lookup(scripcode)
        match = search(regex, response)

        if match:
            return match.group(1)

        raise ValueError(f'Could not find scrip name for {scripcode}')

    def getScripCode(self, scripname):
        '''
        Get BSE scrip code for stock symbol name

        :param scripname: Stock symbol code
        :raise ValueError: if scrip not found
        :return: BSE scrip code
        :rtype: str

        Example
        HDFCBANK -> '500180'
        '''
        # <strong>HDFC</strong>   INE001A01036   500010
        regex = rf'<\w+>{scripname.upper()}<\/\w+>\s+\w+\s+(\d{{6}})'

        response = self.__lookup(scripname)
        match = search(regex, response)

        if match:
            return match.group(1)

        raise ValueError(f'Could not find scrip code for {scripname}')
