import json
import pandas as pd

discordant = ["SRR10100115", "ERR4025717", "SRR10267562"]

truth = pd.read_csv('data/reference/typhoid-consortium-meta/TGC_data.csv', low_memory=False)
truth = truth.set_index('Data Accession')

# Correspondance entre le nom Mykrobe et le code du CSV consortium
mapping = {
    'ampicillin': 'AMP',
    'ceftriaxone': 'CEP',
    'chloramphenicol': 'CHL',
    'ciprofloxacin': 'CIP',
    'sulfonamides': 'SMX',
    'trimethoprim': 'TMP',
    'tetracycline': 'TCY',
    'azithromycin': 'AZM',
}

for s in discordant:
    print(f"\n=== {s} ===")
    with open(f'results/{s}/mykrobe/{s}.json') as f:
        data = json.load(f)
    susc = data[list(data.keys())[0]]['susceptibility']

    t = truth.loc[s]
    print(f"{'Antibiotique':15} {'Mykrobe':10} {'Consortium':10} {'Accord'}")
    for myk_name, csv_col in mapping.items():
        myk_pred = susc.get(myk_name, {}).get('predict', 'NA')
        myk_r = (myk_pred == 'R')
        csv_r = bool(t[csv_col]) if pd.notna(t[csv_col]) else None
        ok = "OK" if myk_r == csv_r else "<< DIFFERENT"
        print(f"{myk_name:15} {myk_pred:10} {'R' if csv_r else 'S':10} {ok}")
