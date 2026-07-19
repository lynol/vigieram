import pandas as pd
from pathlib import Path

truth = pd.read_csv('data/reference/klebsiella_selected.csv')
truth = truth.set_index('Assembly')

results_dir = Path('results')
rows = []
for acc in truth.index:
    acc_short = acc.split('.')[0]  # GCA_049383885.1 -> GCA_049383885 (nom reel du dossier Nextflow)
    f = results_dir / acc_short / 'kleborate' / 'klebsiella_pneumo_complex_output.txt'
    if not f.exists():
        rows.append({
            'Assembly': acc, 'Species': 'ECHEC PIPELINE',
            'CRE_connu': truth.loc[acc, 'CRE'], 'CRE_predit': None,
            'Genes_carbapenemase': None, 'Accord': None
        })
        continue
    pred = pd.read_csv(f, sep='\t').iloc[0]
    species = pred['enterobacterales__species__species']
    carb_genes = pred['klebsiella_pneumo_complex__amr__Bla_Carb_acquired']
    predicted_cre = carb_genes != '-'
    rows.append({
        'Assembly': acc,
        'Species': species,
        'CRE_connu': truth.loc[acc, 'CRE'],
        'CRE_predit': predicted_cre,
        'Genes_carbapenemase': carb_genes,
        'Accord': truth.loc[acc, 'CRE'] == predicted_cre,
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))
df.to_csv('results/klebsiella_validation_table.csv', index=False)

valid = df[df['Accord'].notna()]
print(f"\n--- Résumé ---")
print(f"CRE : {valid['Accord'].sum()}/{len(valid)} corrects ({100*valid['Accord'].mean():.1f}%)")
print(f"Échecs pipeline (exclus du calcul, comptés séparément) : {df['Accord'].isna().sum()}")
