# OpenRouter Catalog ZDR

Quel modèle d'IA pour quel usage ? Comparatif des grands modèles (Anthropic, OpenAI, Google, Mistral, Moonshot/Kimi, Z.ai/GLM, DeepSeek) servis via OpenRouter **uniquement** par cinq hébergeurs : Amazon Bedrock, Azure, Google Vertex, Inceptron et Mistral, en Zero Data Retention.

Page publiée : https://mrlinks75.github.io/OpenRouter_Catalog_ZDR/

## Contenu de la page

- Prix entrée / sortie par million de tokens, chez le moins cher des cinq hébergeurs (tarif standard)
- Benchmarks : intelligence générale (Artificial Analysis Intelligence Index), codage avancé (AA Coding Agent Index), codage standard (SWE-bench), multimodal (MMMU-Pro), vitesse
- Deux pastilles par modèle :
  - **Budget** (prix de sortie) : vert ≤ 2,50 $, orange ≤ 8 $, rouge au-delà
  - **Utilisation** : vert = tous les jours, orange = cas d'usage précis, rouge = à éviter / dernier recours

## Mise à jour

| Quoi | Qui | Quand |
|---|---|---|
| Hébergeurs, prix, couleur Budget, liste des nouveaux modèles (`data/candidates.json`) | GitHub Actions, API publique OpenRouter (`scripts/refresh_prices.py`) | Tous les jours, 5 h 17 UTC |
| Scores, ajout/retrait de modèles, couleur Utilisation, recommandations | Tâche planifiée Claude, qui pousse `data/models.json` | Chaque lundi matin |
| Génération et publication de la page | GitHub Actions (`scripts/build.py --page`) | À chaque push sur `main` et après la mise à jour des prix |

Toutes les valeurs sont dans [`data/models.json`](data/models.json) (le champ `_schema` décrit chaque champ). `null` = non disponible, affiché « n.d. ». Pour corriger une valeur à la main : modifier ce fichier et pousser, la page se régénère.

## Mise en place (une fois)

1. **Settings → Pages → Build and deployment → Source : GitHub Actions.**
2. Optionnel : secret `OPENROUTER_API_KEY` (Settings → Secrets and variables → Actions). L'API utilisée est publique, la clé n'est pas obligatoire.
3. Lancer le workflow *Mise à jour et publication* une première fois (onglet Actions → Run workflow).

Un push dont le message de commit contient `[prix]` lance aussi la mise à jour des prix (sinon, un push ne fait que régénérer la page).

## Déploiement sur un GitLab privé

Le fichier [`.gitlab-ci.yml`](.gitlab-ci.yml) publie la page sur GitLab Pages.

- **Mode copie** (variable CI/CD `SYNC_FROM_GITHUB=true`) : récupère `data/models.json` depuis ce dépôt GitHub (prix quotidiens, scores hebdomadaires) et publie la page en interne. Aucun jeton requis.
- **Mode autonome** (sans cette variable) : met à jour les prix via l'API OpenRouter et les enregistre dans le dépôt GitLab avec un jeton d'accès projet `GITLAB_PUSH_TOKEN` (rôle Developer, portée `write_repository`, masqué et protégé). Scores et couleur Utilisation à mettre à jour à la main.

Mise en place : importer le dépôt par URL, régler Pages sur « Only project members » (Settings → General → Visibility), définir la variable du mode choisi, puis créer un pipeline planifié quotidien (Build → Pipeline schedules). Le runner doit pouvoir joindre `raw.githubusercontent.com` (mode copie) ou `openrouter.ai` (mode autonome).

## En local

```bash
python3 scripts/refresh_prices.py data/models.json   # prix et hébergeurs
python3 scripts/build.py data/models.json site --page  # site/index.html
```

Aucune dépendance : Python 3 standard.

## Sources

Prix : [OpenRouter](https://openrouter.ai). Scores : [Artificial Analysis](https://artificialanalysis.ai) (Intelligence Index, MMMU-Pro), [BenchLM](https://benchlm.ai/benchmarks/aacodingagents) (AA Coding Agent Index), éditeurs et [Vals.ai](https://www.vals.ai) (SWE-bench). Données reprises avec attribution, à titre indicatif.
