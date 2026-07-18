import pandas as pd

SEED = 42
N_PER_CATEGORY = 10

df = pd.read_csv('data/reference/typhoid-consortium-meta/TGC_data.csv', low_memory=False)
df = df[df['exclude_assembly'] != True]
df = df[~df['Data Accession'].str.contains(',', na=False)]  # exclut les runs multiples

already_have = ["ERR2093255", "ERR2093334", "SRR8878443", "ERR319495",
                "ERR4790678", "ERR731380", "ERR586799", "ERR319410", "ERR998638"]
df = df[~df['Data Accession'].isin(already_have)]

xdr = df[df['XDR'] == True].sample(n=N_PER_CATEGORY, random_state=SEED)
mdr = df[(df['MDR'] == True) & (df['XDR'] == False)].sample(n=N_PER_CATEGORY, random_state=SEED)
sensible = df[(df['MDR'] == False) & (df['XDR'] == False)].sample(n=N_PER_CATEGORY, random_state=SEED)

selection = pd.concat([xdr, mdr, sensible])
cols = ['Data Accession', 'Country', 'Final_genotype', 'MDR', 'XDR']
print(selection[cols].to_string(index=False))
selection[cols].to_csv('data/reference/selected_samples_round2.csv', index=False)

def ena_url(acc):
    prefix, digits = acc[:6], acc[3:]
    if len(digits) == 6: mid = ''
    elif len(digits) == 7: mid = '00' + digits[-1] + '/'
    elif len(digits) == 8: mid = '0' + digits[-2:] + '/'
    else: mid = digits[-3:] + '/'
    base = f'ftp://ftp.sra.ebi.ac.uk/vol1/fastq/{prefix}/{mid}{acc}/{acc}'
    return base + '_1.fastq.gz', base + '_2.fastq.gz'

with open('scripts/download_round2.sh', 'w') as f:
    f.write('#!/bin/bash\n')
    for acc in selection['Data Accession']:
        r1, r2 = ena_url(acc)
        f.write(f'mkdir -p data/raw/{acc}\n')
        f.write(f'wget -P data/raw/{acc}/ {r1}\n')
        f.write(f'wget -P data/raw/{acc}/ {r2}\n')
print("\nScript ecrit: scripts/download_round2.sh")
