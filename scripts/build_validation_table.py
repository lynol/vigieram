import json
import pandas as pd
from pathlib import Path

results_dir = Path('results')
samples = sorted([d.name for d in results_dir.iterdir()
                   if d.is_dir() and (d / 'mykrobe').exists()])
print(f"{len(samples)} échantillons détectés\n")

truth = pd.read_csv('data/reference/typhoid-consortium-meta/TGC_data.csv', low_memory=False)
truth = truth.set_index('Data Accession')

def get_pred(susc, antibiotic):
    # .upper() : traite "r" (confiance plus faible) comme "R" (confiance pleine)
    # pour la classification MDR/XDR -- Mykrobe distingue les deux, mais les
    # deux signifient "résistance prédite"
    return susc.get(antibiotic, {}).get('predict', 'NA').upper()

def has_low_confidence_call(susc, antibiotics):
    # Repère si au moins un antibiotique clé a été appelé avec confiance
    # réduite (minuscule) -- utile à savoir, pas à cacher
    return any(susc.get(a, {}).get('predict', '') in ('r', 's') for a in antibiotics)

rows = []
for s in samples:
    json_path = results_dir / s / 'mykrobe' / f'{s}.json'
    if not json_path.exists():
        continue
    with open(json_path) as f:
        data = json.load(f)
    result = data[list(data.keys())[0]]
    genotype = result['phylogenetics']['lineage']['lineage'][0]
    susc = result['susceptibility']

    mdr_abx = ['ampicillin', 'chloramphenicol', 'trimethoprim', 'sulfonamides']
    xdr_abx = mdr_abx + ['ciprofloxacin', 'ceftriaxone']
    is_mdr = all(get_pred(susc, a) == 'R' for a in mdr_abx)
    is_xdr = is_mdr and get_pred(susc, 'ciprofloxacin') == 'R' and get_pred(susc, 'ceftriaxone') == 'R'
    low_conf = has_low_confidence_call(susc, xdr_abx)

    t = truth.loc[s] if s in truth.index else None
    rows.append({
        'Echantillon': s,
        'Genotype_predit': genotype,
        'Genotype_connu': t['Final_genotype'] if t is not None else 'NA',
        'Genotype_OK': genotype == t['Final_genotype'] if t is not None else None,
        'MDR_predit': is_mdr,
        'MDR_connu': t['MDR'] if t is not None else 'NA',
        'MDR_OK': is_mdr == t['MDR'] if t is not None else None,
        'XDR_predit': is_xdr,
        'XDR_connu': t['XDR'] if t is not None else 'NA',
        'XDR_OK': is_xdr == t['XDR'] if t is not None else None,
        'Confiance_reduite': low_conf,
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv('results/validation_table.csv', index=False)

print("\n--- Résumé ---")
print(f"Génotype : {df['Genotype_OK'].sum()}/{len(df)} corrects ({100*df['Genotype_OK'].mean():.1f}%)")
print(f"MDR      : {df['MDR_OK'].sum()}/{len(df)} corrects ({100*df['MDR_OK'].mean():.1f}%)")
print(f"XDR      : {df['XDR_OK'].sum()}/{len(df)} corrects ({100*df['XDR_OK'].mean():.1f}%)")
print(f"\nÉchantillons avec au moins un appel à confiance réduite : {df['Confiance_reduite'].sum()}")
