import pandas as pd

SEED = 42
N_PER_CATEGORY = 15

df = pd.read_csv('data/reference/klebsiella_ncbi/isolates.tsv', sep='\t')
df = df[df['AST phenotypes'].notna() & df['Assembly'].notna()].copy()

def parse_ast(s):
    d = {}
    for pair in s.split(','):
        if '=' in pair:
            k, v = pair.split('=')
            d[k.strip()] = v.strip()
    return d

df['ast_dict'] = df['AST phenotypes'].apply(parse_ast)
carbapenems = ['imipenem', 'meropenem', 'doripenem', 'ertapenem']
df['CRE'] = df['ast_dict'].apply(lambda d: any(d.get(c) == 'R' for c in carbapenems))

cre = df[df['CRE']].sample(n=N_PER_CATEGORY, random_state=SEED)
non_cre = df[~df['CRE']].sample(n=N_PER_CATEGORY, random_state=SEED)
selection = pd.concat([cre, non_cre])

selection[['Assembly', 'Location', 'CRE', 'AST phenotypes']].to_csv(
    'data/reference/klebsiella_selected.csv', index=False)
print(selection[['Assembly', 'Location', 'CRE']].to_string(index=False))

with open('scripts/download_klebsiella.sh', 'w') as f:
    f.write('#!/bin/bash\n')
    f.write('cd data/raw/klebsiella\n')
    for acc in selection['Assembly']:
        f.write(f'datasets download genome accession {acc} --include genome --filename {acc}.zip\n')
        f.write(f'unzip -o {acc}.zip -d {acc}_dir\n')
    f.write('cd ../../..\n')
print("\nScript ecrit: scripts/download_klebsiella.sh")
