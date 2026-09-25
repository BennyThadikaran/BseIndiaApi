# BseIndiaApi

An Unofficial Python Api for BSE India stock exchange.

Python version: >= 3.8

## Install with PIP

```
pip install -U bse
```

## Documentation

[https://bennythadikaran.github.io/BseIndiaApi/](https://bennythadikaran.github.io/BseIndiaApi/)

You might like [stock-news](https://github.com/BennyThadikaran/stock-news) built using `BseIndiaApi`. It helps to keep track of corporate announcements and actions on your portfolio.

## Usage

Using with statement

```python
from bse import BSE

with BSE(download_folder='./') as bse:
    scripCode = bse.getScripCode('tcs')  # 532540 bse scrip code

    data = bse.actions(scripcode=scripCode)

    ohlc = bse.quote(scripCode)  # Open, High, Low, LTP
```

or

```python
from bse import BSE
from bse.constants import INDEX

bse = BSE(download_folder='./')

code = bse.getScripCode('tcs')  # 532540 bse scrip code

gainers = bse.gainers(by='index', name=INDEX.BSE500)

bse.exit()  # close the request session
```

## Sample Responses

`src/samples` contain the sample responses from the various methods in JSON format.

The files are named after the corresponding method in `src/BSE.py`. Use it to understand the API response structure.

## Example Folder

`src/examples` contains scripts that use the `BSE.py`.

To use the scripts download or clone the repo.

- [get_all_announcements.py](https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/examples/get_all_announcements.py): This file demonstrates how to paginate and get all announcements using `BSE.announcements`. It has step by step explanation of code.
- [actions.py](https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/examples/actions.py): `py actions.py infy` to print the recent corporate actions. Nothing more.
- [advances.py](https://github.com/BennyThadikaran/BseIndiaApi/blob/main/src/examples/advances.py): `py advances.py` to print the advance decline ratios for various bse Indexes.

You may also like my other repo: [Stock-News](https://github.com/BennyThadikaran/stock-news) - It uses BseIndiaApi and displays stock announcements, dividend, bonus/splits and upcoming results etc for your portfolio or watchlist stocks.
