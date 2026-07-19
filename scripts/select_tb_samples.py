import pandas as pd

SEED = 42
N_PER_CATEGORY = 15

df = pd.read_csv('data/reference/cryptic/CRyPTIC_reuse_table.csv', low_memory=False)
df = df[(df['INH_PHENOTYPE_QUALITY'] == 'HIGH') & (df['RIF_PHENOTYPE_QUALITY'] == 'HIGH')].copy()

mdr = df[(df['INH_BINARY_PHENOTYPE'] == 'R') & (df['RIF_BINARY_PHENOTYPE'] == 'R')]
non_mdr = df[(df['INH_BINARY_PHENOTYPE'] == 'S') & (df['RIF_BINARY_PHENOTYPE'] == 'S')]

print(f"MDR disponibles (qualite HIGH): {len(mdr)}")
print(f"Non-MDR disponibles (qualite HIGH): {len(non_mdr)}")

sel_mdr = mdr.sample(n=N_PER_CATEGORY, random_state=SEED)
sel_non_mdr = non_mdr.sample(n=N_PER_CATEGORY, random_state=SEED)
selection = pd.concat([sel_mdr, sel_non_mdr])
selection['MDR'] = selection['INH_BINARY_PHENOTYPE'].eq('R') & selection['RIF_BINARY_PHENOTYPE'].eq('R')

cols = ['ENA_RUN', 'UNIQUEID', 'INH_BINARY_PHENOTYPE', 'RIF_BINARY_PHENOTYPE', 'MDR']
selection[cols].to_csv('data/reference/tb_selected.csv', index=False)
print(selection[cols].to_string(index=False))

def ena_url(acc):
    prefix, digits = acc[:6], acc[3:]
    if len(digits) == 6: mid = ''
    elif len(digits) == 7: mid = '00' + digits[-1] + '/'
    elif len(digits) == 8: mid = '0' + digits[-2:] + '/'
    else: mid = digits[-3:] + '/'
    base = f'ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{mid}{acc}/{acc}'
    return base + '_1.fastq.gz', base + '_2.fastq.gz'

with open('scripts/download_tb.sh', 'w') as f:
    f.write('#!/bin/bash\n')
    for acc in selection['ENA_RUN']:
        r1, r2 = ena_url(acc)
        f.write(f'mkdir -p data/raw/tb/{acc}\n')
        f.write(f'wget -P data/raw/tb/{acc}/ {r1}\n')
        f.write(f'wget -P data/raw/tb/{acc}/ {r2}\n')
print("\nScript ecrit: scripts/download_tb.sh")
