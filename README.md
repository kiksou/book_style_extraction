# Book Style Extractor

Outil d'extraction de style d'écriture à partir de sagas littéraires pour créer une "bible d'écriture".

## Fonctionnalités

- **Analyse locale** : Extraction de métriques de style (vocabulaire, syntaxe, rythme) sans API
- **Analyse IA** : Utilisation de Claude pour une analyse approfondie du style narratif
- **Support EPUB** : Lecture directe des fichiers EPUB
- **Suivi des coûts** : Affichage en temps réel des coûts API

## Prérequis

- Python 3.10 ou supérieur
- Clé API Anthropic (optionnelle, pour l'analyse IA)

## Installation

```bash
# Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Mettre à jour pip
pip install --upgrade pip

# Installer avec support LLM
pip install -e ".[llm]"

# Télécharger le modèle spaCy français
python -m spacy download fr_core_news_md
```

## Configuration

Copier le fichier d'exemple et ajouter votre clé API :

```bash
cp .env.example .env
```

Éditer `.env` :
```bash
ANTHROPIC_API_KEY=sk-ant-votre-clé-ici
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

### Modèles disponibles (décembre 2025)

| Modèle | ID | Input | Output | Usage |
|--------|-----|-------|--------|-------|
| Sonnet 4.5 | `claude-sonnet-4-5-20250929` | $3/MTok | $15/MTok | Recommandé |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | $1/MTok | $5/MTok | Économique |
| Opus 4.5 | `claude-opus-4-5-20251101` | $5/MTok | $25/MTok | Premium |

## Utilisation

### Analyse locale (sans API)

```bash
style-extractor analyze livre1.epub livre2.epub -n "Ma Saga" -a "Auteur"
```

### Analyse avec Claude (recommandé)

```bash
# Mode hybride : analyse locale + enrichissement IA
style-extractor analyze livre.epub --llm

# Mode IA uniquement (meilleurs résultats)
style-extractor analyze livre.epub --llm-only
```

### Options

```
Options:
  -o, --output PATH    Fichier de sortie (markdown)
  -n, --name TEXT      Nom de la saga
  -a, --author TEXT    Nom de l'auteur
  -q, --quiet          Mode silencieux
  --llm / --no-llm     Activer l'analyse IA
  --llm-only           Utiliser uniquement l'IA
  --api-key TEXT       Clé API Anthropic
  --model TEXT         Modèle Claude à utiliser
```

### Exemple complet

```bash
style-extractor analyze \
  tome1.epub tome2.epub tome3.epub \
  -n "Les Chroniques de l'Ombre" \
  -a "Jean Dupont" \
  -o bible_style.md \
  --llm-only \
  --model claude-sonnet-4-5-20250929
```

## Sortie

L'outil génère une "bible d'écriture" en Markdown contenant :

- **Résumé du style** : Vue d'ensemble de la voix narrative
- **Vocabulaire** : Niveau, mots signatures, registre
- **Syntaxe** : Structure des phrases, ponctuation
- **Narration** : Point de vue, gestion du temps, dialogues
- **Thèmes** : Motifs récurrents, atmosphère
- **Exemples** : Extraits représentatifs du style
- **Coûts API** : Détail des tokens utilisés et coûts

## Structure du projet

```
book_style_extraction/
├── src/style_extractor/
│   ├── cli.py              # Interface ligne de commande
│   ├── core.py             # Logique principale
│   ├── analyzers/
│   │   ├── llm_analyzer.py # Analyse Claude avec suivi coûts
│   │   └── ...
│   └── generators/
│       └── markdown_renderer.py
├── .env.example            # Configuration exemple
└── pyproject.toml          # Dépendances
```

## Licence

MIT
