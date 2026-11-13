# RETEX — Triangulator (Techniques de test)

## 1. Environnement utilisé

| **Élément**                    | **Configuration utilisée**                 |
| ------------------------------ | ------------------------------------------ |
| **Système**                    | Windows                                    |
| **Terminal**                   | PowerShell                                 |
| **Python**                     | Python 3.13, dans un environnement `.venv` |
| **Outils de test**             | pytest 8.4.2, coverage, ruff, pdoc3        |
| **Automatisation**             | `make` (installé à part sous Windows)      |
| **Seule dépendance autorisée** | Flask                                      |

J'utilise un environnement virtuel `.venv` pour installer les dépendances du projet (Flask et les outils de test) à part, sans toucher au Python de mon ordinateur, et pour être sûre de travailler toujours avec les mêmes versions.

## 2. Relancer le projet

Je me place à la racine du projet, puis je crée l'environnement virtuel (une seule fois) :

```
python -m venv .venv
```

À chaque nouvelle session PowerShell, je l'active :

```
.venv\Scripts\Activate.ps1
```

Le terminal affiche alors `(.venv)` au début de la ligne. J'installe ensuite les dépendances :

```
pip install -r requirements.txt -r dev_requirements.txt
```

`requirements.txt` ne contient que Flask (pour faire tourner le service). `dev_requirements.txt` contient les outils de test et de qualité.

## 3. Organisation du projet

```
triangulator/
    binary.py
    algorithm.py
    pointset_client.py
    app.py
test/
    test_binary.py
    test_algorithm.py
    test_pointset_client.py
    test_api.py
    test_performance.py
```

J'ai organisé le projet en deux dossiers. `triangulator/` contient le code : `binary.py` (format binaire), `algorithm.py` (triangulation), `pointset_client.py` (récupération des PointSets) et `app.py` (l'API Flask). `test/` contient un fichier de tests pour chaque partie, et `test_performance.py` à part.

Les dossiers `__pycache__` sont créés automatiquement par Python quand il importe les fichiers, pour aller plus vite la fois suivante. Ce n'est pas du code, donc je les ai mis dans le `.gitignore`.

## 4. Comment j'ai procédé

J'ai travaillé en « test first », en suivant les quatre rendus.

**Rendu 1 : le plan.** J'ai lu l'énoncé et les fichiers YAML pour lister les codes de réponse (200, 400, 404, 500, 503) et le format binaire. J'ai écrit `PLAN.md` en trois couches : binaire, algorithme, API.

**Rendu 2 : le setup de test sans implémentation.** J'ai mis en place le `Makefile`, `ruff`, les squelettes des modules et quatre fichiers de tests (binaire, algorithme, API, performance). Résultat : 51 tests unitaires et 9 tests de performance, tous rouges, sans erreur d'import.

**Rendu 3 : l'implémentation.** J'ai codé les modules un par un : `binary.py`, `algorithm.py`, `pointset_client.py`, puis `app.py`. Après chaque fichier, j'ai lancé les tests et `ruff`, puis j'ai fait un commit.

Le client du PointSetManager est injecté dans `create_app`, donc j'ai pu tester l'API avec un stub, sans serveur réel. Pour le client HTTP, j'ai utilisé `monkeypatch` de pytest pour remplacer `urlopen` par une fausse fonction pendant les tests, sans modifier le code du client. Donc aucun test ne fait de vrai appel réseau.

L'algorithme est écrit sans bibliothèque, comme le demande l'énoncé. On trie les points de gauche à droite, puis chaque nouveau point est relié aux côtés du contour qu'il voit, ce qui crée de nouveaux triangles.

## 5. Lancer les tests et les vérifications

Toutes les commandes se lancent depuis la racine du projet, avec le `.venv` activé.

```
make unit_test
```

58 tests unitaires verts (12 binaire, 25 algorithme, 16 API, 5 client).

```
make perf_test
```

9 tests de performance verts. Pour voir les temps mesurés, j'ai utilisé :

```
python -m pytest -m performance -s
```

Triangulation de 1000 points : 0,0089 s. Décodage de 10 000 points : 0,0014 s.

```
make test
```

Lance tous les tests, performance comprise.

```
make coverage
```

100 % de couverture sur `triangulator/`, branches comprises (`--branch`) : chaque ligne et chaque branche est exécutée par les tests unitaires.

```
make lint
```

`ruff` affiche `All checks passed!`.

```
make doc
```

Génère la documentation dans `html\triangulator\index.html`.

## 6. Erreurs rencontrées

- **Hypothesis dans le plan** : il n'était pas dans `dev_requirements.txt`. Je l'ai remplacé par `pytest.mark.parametrize` et `random.Random(42)` (graine fixe).
- **« Stub 400 → 404 » dans le plan** : c'était faux. Après relecture du YAML, j'ai corrigé : 404 si le PointSet est introuvable, 503 si le PointSetManager est injoignable, 400 si l'identifiant n'est pas un UUID.
- **`make doc`** : erreur `No module named doc`. Mon `Makefile` contenait `python -m doc`, je l'ai remplacé par `python -m pdoc --html --force --output-dir html triangulator`.
- **`.PHONY` du Makefile** : `unit_test`, `perf_test` et `coverage` étaient collés en un seul mot. J'ai remis les espaces.
- **Fichiers `.pyc` dans Git** : je les avais commités avant d'avoir un `.gitignore`. Je les ai retirés du suivi avec `git rm -r --cached test/__pycache__`.
- **Erreurs `ruff`** : D401 (docstring pas à l'impératif) et B905 (`zip()` sans `strict=`). J'ai reformulé la docstring, et ajouté `strict=False` dans l'algorithme et `strict=True` dans `binary.py`.

## 7. Bilan

**Ce qui a bien fonctionné.** Écrire les tests avant le code m'a obligée à lire précisément les YAML. Les tests de l'algorithme vérifient des propriétés (nombre de triangles, aire totale, indices valides) et non un résultat précis, donc ils ne dépendent pas de l'algorithme choisi. Les tests du binaire et de l'algorithme étaient verts dès la première exécution : seul le lint a posé problème.

**Mon plan initial.** Bon sur la structure (trois couches, TDD, stub, `--branch`). Insuffisant sur les cas limites (points alignés, doublons, octets corrompus, ordre des octets), que j'ai ajoutés après coup.

**Entre le plan et la réalité.** J'ai ajouté deux tests d'algorithme (points alignés au début, troisième point à droite du premier segment) et `test_pointset_client.py`. Mes seuils de performance (1 s et 10 s) étaient très larges par rapport aux temps mesurés, et je n'ai pas testé la triangulation au-delà de 1000 points.

**Ce que je ferais autrement.**

- Créer le `.gitignore` et vérifier l'outillage (`make`, PowerShell) avant d'écrire les tests.
- Faire très tôt un test d'API de bout en bout pour valider l'architecture.
- Choisir et justifier l'algorithme dès le plan.
- Confirmer l'ordre des octets avec l'enseignant (j'ai supposé little-endian).

## 8. Utilisation d'un assistant IA

J'ai conçu seule mon plan de tests (rendu 1). Claude m'a ensuite aidée à le relire et à mettre en place l'outillage, et m'a fourni une grande partie du code et des tests. Mon travail a été de les intégrer, de lancer et de vérifier chaque étape, et de signaler les écarts. J'ai compris le principe de l'algorithme et le rôle de chaque test, ce qui m'a permis d'arriver à 100 % de couverture avec des tests qui vérifient vraiment le comportement attendu.