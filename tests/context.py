from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from bse import BSE, SymbolParser
from bse.constants import CATEGORY
