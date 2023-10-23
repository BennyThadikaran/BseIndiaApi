# BseIndiaApi

An Unofficial Python Api for BSE India stock exchange.

Python version: >= 3.10

## Install with PIP

```
pip install bse
```

## Documentation

[https://bennythadikaran.github.io/BseIndiaApi/](https://bennythadikaran.github.io/BseIndiaApi/)

## Usage

Using with statement

```python
from bse import BSE

with BSE() as bse:
    scripCode = bse.getScripCode('tcs') # 532540 bse scrip code

    bse.getScripName('532540') # TCS

    data = bse.corporateActions(scripCode)

    oclc = bse.quote(scripCode) # Open, High, Low, LTP
```

or

```python
from bse import BSE
from bse.constants import INDEX

bse = BSE()

code = bse.getScripCode('tcs') # 532540 bse scrip code

gainers = bse.gainers(by='index', name=INDEX.BSE500)

bse.exit() # close the request session
```

## Sample Responses

`src/samples` contain the sample responses from the various methods in JSON format.

The files are named after the corresponding method in `src/BSE.py`. Use it to understand the API response structure.

## Example Folder

`src/examples` contains scripts that use the `BSE.py`. These are script i wrote some years back. All scripts incorporate color and fancy formatting to look good. 😄

To use the scripts download or clone the repo.

- **ann.py**: This is the only script i still use to date. It display all corporate announcements and corporate actions relating to your watchlist or portfolio.
  - To get started, store your watchlist symbols in a text file each symbol on a new line.
  - At first, execute `ann.py` passing the text file as an argument. `py ann.py watchlist.txt`. This will generate a `watchlist.json` file and print out all announcements and actions related to your watchlist.
  - Next time, simply execute `py ann.py` to see announcements for the day.
- **news.py**: `news.py` simply prints the last 10 announcements for a scrip.
  - Execute it as `py news.py infy`.
  - You can optionally limit the results by passing a number after the symbol.
  - `py news.py infy 3`. This returns the last 3 announcements.
- **actions.py**: `py actions.py infy` to print the recent corporate actions. Nothing more.
- **advances.py**: `py advances.py` to print the advance decline ratios for various bse Indexes.
