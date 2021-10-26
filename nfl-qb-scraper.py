from urllib.request import urlopen
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

# Grabbing QB Passing Data
# Change the /2021/ to Data You're Interested In
# Maybe Parse User Input for Which Year ?
url = 'https://www.pro-football-reference.com/years/2021/passing.htm'

html = urlopen(url)
stats_page = BeautifulSoup(html)

# Collecting Table Headers
column_headers = stats_page.findAll('tr')[0]
column_headers = [i.getText() for i in column_headers.findAll('th')]