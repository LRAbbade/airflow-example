from urllib.request import urlretrieve
import zipfile
import os
import re
import pandas as pd


get_year_re = re.compile(r'\d+')

def download_year(year):
    file_path = f'dags/files/{year}.zip'
    urlretrieve(f'http://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP', file_path)
    return file_path

def unzip(file_path):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall('dags/files/')

def delete_zip(file_path):
    os.remove(file_path)

def _to_float(s):
    return float(s[:-2] + '.' + s[-2:])

def _get_info(line):
    return {
        'date': line[2:9],
        'trading_code': line[12:23].strip(),
        'short_name': line[27:38].strip(),
        'open': _to_float(line[56:68].strip()),
        'high': _to_float(line[69:81].strip()),
        'low': _to_float(line[82:94].strip()),
        'close': _to_float(line[108:120].strip()),
        'bid': _to_float(line[121:133].strip()),
        'ask': _to_float(line[134:146].strip()),
        'volume': _to_float(line[170:187].strip())
    }

def process(paths):
    csv_paths = []
    for path in paths:
        print(f'Parsing file {path!r}')
        year = get_year_re.findall(path)[0]
        data = []
        with open(path, 'r') as file:
            for line in file:
                try:
                    data.append(_get_info(line))
                except Exception as e:
                    print(f'Error processing line:\n{line}\n{e}')

        csv_path = f'dags/csv/{year}.csv'
        csv_paths.append(csv_path)
        pd.DataFrame(data).to_csv(csv_path, index=False)

    return csv_paths
