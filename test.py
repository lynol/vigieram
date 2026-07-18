import pandas as pd

def ena_url(acc):
    prefix = acc[:6]
    digits = acc[3:]
    if len(digits) == 6:
        mid = ''
    elif len(digits) == 7:
        mid = '00' + digits[-1] + '/'
    elif len(digits) == 8:
        mid = '0' + digits[-2:] + '/'
    else:
        mid = digits[-3:] + '/'
    base = f'ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{mid}{acc}/{acc}'
    return base + '_1.fastq.gz', base + '_2.fastq.gz'

df = pd.read_csv('data/reference/selected_samples.csv')
with open('scripts/download_samples.sh', 'w') as f:
    f.write('#!/bin/bash\n')
    for acc in df['Data Accession']:
        r1, r2 = ena_url(acc)
        f.write(f'mkdir -p data/raw/{acc}\n')
        f.write(f'wget -P data/raw/{acc}/ {r1}\n')
        f.write(f'wget -P data/raw/{acc}/ {r2}\n')
print('Script écrit dans scripts/download_samples.sh')
