# VigieRAM - Pipeline de Surveillance Génomique AMR (Afrique de l'Ouest)

*Document vivant - à mettre à jour à chaque session de travail.*
*Dernière mise à jour : 15 juillet 2026*

**Nom du projet : VigieRAM** ("vigie" = surveillance/guet ; "RAM" = Résistance
aux AntiMicrobiens, l'acronyme officiel utilisé dans le PAN-RAM ivoirien et le
GTT-RAM). Le nom couvre l'ensemble du système à 3 couches - pas seulement la
partie génomique.

---

## 1. Objectif (la vision)

Doter l'Afrique de l'Ouest - en commençant par la Côte d'Ivoire - d'un pipeline
open-source de surveillance génomique de la résistance aux antimicrobiens (AMR) :
- **Souverain** : les données ne quittent jamais le pays/labo.
- **Validé scientifiquement** : précision chiffrée, pas juste "ça tourne".
- **Utile à plusieurs niveaux** : décideurs, cliniciens, et public - pas réservé
  à une poignée de gens.

Ce projet est pensé comme la première brique concrète vers un futur institut/
plateforme de recherche bioinformatique, insh'Allah - pas un détour.

---

## 2. Périmètre : espèces vs résistance

⚠️ Point clé à ne pas confondre :

- **La détection de multirésistance (MDR/XDR) est incluse dès le MVP.**
  Les bases de référence (AMRFinderPlus, CARD) couvrent déjà des milliers de
  gènes sur toutes les classes d'antibiotiques. On ne construit pas ça - on
  l'utilise.
- **Ce qui s'étend dans le temps, c'est la couverture d'espèces** :
  1. *Salmonella* Typhi (MVP, année 1)
  2. *Salmonella* non-typhoïdique
  3. *Klebsiella pneumoniae* (sepsis néonatal, carbapénèmes)
  4. Autres pathogènes prioritaires OMS

---

## 3. Architecture générale - 3 couches

| Couche | Nom | Public | Type |
|---|---|---|---|
| 1 | Moteur génomique | Labos de référence (IPCI, réseaux régionaux) | Pipeline / logiciel |
| 2 | Aide à la décision clinique | Hôpitaux, cliniciens (via antibiogramme classique) | Application légère |
| 3 | Tableau de bord public | Société civile, journalistes, patients | Plateforme web |

**Ce qu'on construit MAINTENANT : uniquement la Couche 1.**
Les couches 2 et 3 viendront une fois la Couche 1 validée.

---

## 4. Couche 1 (MVP) - flux de données concret

**Entrée**
- Fichiers de séquençage : FASTQ bruts (Illumina/Nanopore) ou FASTA assemblé.
- Phase actuelle (validation) : génomes publics téléchargés (TyphiNet, ENA/NCBI).
- Phase future (réelle) : sortie brute du séquenceur d'un labo partenaire.

**Traitement (automatique, une fois lancé)**
1. QC / nettoyage des reads (fastp)
2. Assemblage du génome (Shovill pour Illumina / Flye pour Nanopore)
3. Confirmation de l'espèce (Kraken2)
4. Génotypage / lignée (GenoTyphi - ex. H58)
5. Détection des gènes de résistance (AMRFinderPlus + ResFinder)
6. Classification MDR/XDR (langage clair : "résistant fluoroquinolones + C3G")

**Sortie**
- Rapport PDF/HTML bilingue FR/EN, lisible par un non-bioinformaticien.
- Une ligne ajoutée à une base de données locale (accumulation dans le temps).

**Où ça tourne**
- En local, sur un laptop/serveur du labo. Aucune donnée ne sort. Aucun
  internet requis pour l'exécution (téléchargement des bases de référence
  une seule fois, en amont).

**Pourquoi**
- Un clinicien ou microbiologiste doit pouvoir agir sur le résultat sans
  être bioinformaticien.

---

## 5. Méthodologie

- **Validation d'abord** : chaque module comparé à une vérité terrain
  (génomes annotés, PCR) avant d'être considéré "fini" - comme abritAMR.
- **Ouvert dès le premier commit** : GitHub public, documentation continue.
- **Standards, pas de réinvention** : Nextflow/nf-core, AMRFinderPlus,
  GenoTyphi - on assemble et adapte, on ne recode pas l'existant.
- **Sprints courts**, compatibles avec un rythme "de temps en temps".
- **Tests automatisés dès le départ** (CI via GitHub Actions).

---

## 6. Stack technique

| Fonction | Outil |
|---|---|
| Orchestration | Nextflow (+ modules nf-core existants) |
| Conteneurs | Docker (dev) / Singularity-Apptainer (déploiement offline) |
| QC | fastp |
| Assemblage | Shovill (Illumina) / Flye (Nanopore) |
| Espèce | Kraken2 |
| Génotypage Typhi | GenoTyphi |
| Détection résistance | AMRFinderPlus, ResFinder |
| MLST | outil `mlst` (Seemann) |
| Clustering | snippy + snp-dists |
| Rapport | Quarto (→ PDF/HTML) |
| Stockage | SQLite (→ PostgreSQL si besoin plus tard) |
| Couche 2 (futur) | Flask + SQLite |
| Couche 3 (futur) | Plotly Dash |
| Transparence | GitHub public |- **17/07/2026** — 9 génomes publics *Salmonella* Typhi récupérés (ERR2093255 +
  8 sélectionnés pour leur diversité pays/résistance). Premier succès de
  validation ! Pipeline manuel complet exécuté sur ERR2093255 (fastp → shovill
  → Kraken2 → Mykrobe/GenoTyphi). Résultat : génotype 4.3.1.1.P1, profil XDR
  (MDR + ciprofloxacine + ceftriaxone), azithromycine sensible — concordance
  à 100% avec les métadonnées publiées du consortium (échantillon lié à
  l'épidémie XDR Pakistan 2016-2018, PMID 29463654). Prochaine étape :
  répéter sur les 8 autres génomes pour construire un tableau de validation
  complet.
