# RETEX

## Ce qui a bien fonctionné
- Écrire les tests avant le code m'a obligée à lire précisément les fichiers
  YAML (codes 400/404/500/503, format binaire, content-type).
- L'injection du `pointset_client` dans `create_app` a permis de tester toute
  l'API avec un stub, sans serveur réel.
- Les tests de l'algorithme vérifient des propriétés (nombre de triangles,
  aire totale, indices valides) et non un résultat précis.


## Ce qui a moins bien fonctionné
- Mon plan prévoyait Hypothesis, absent de `dev_requirements.txt` : remplacé
  par `parametrize` et `random.Random(42)`.
- Le plan disait « stub 400 → 404 » : erreur corrigée après relecture du YAML.
- Le Makefile contenait `python -m doc` au lieu de `python -m pdoc`, et une
  faute dans `.PHONY` (`unit_testperf_coverage` collé en un mot).
- J'avais commité des fichiers `__pycache__` avant d'avoir un `.gitignore`.


## Mon plan initial
- Bon : trois couches (binaire, algorithme, API), TDD, stub, `--branch`.
- Insuffisant : cas limites ajoutés après coup (points alignés, doublons,
  octets corrompus, ordre des octets).

## Entre les tests prévus et la réalité
- 58 tests unitaires (12 binaire, 25 algorithme, 16 API, 5 client) et
  9 tests de performance, tous verts.
- Tests ajoutés pendant l'implémentation : deux tests d'algorithme (points
  alignés au début, troisième point à droite) et `test_pointset_client.py`.
- Temps mesurés : triangulation de 1000 points en 0,0089 s, décodage de
  10 000 points en 0,0014 s. Mes seuils (1 s et 10 s) étaient très larges
  par rapport à ces mesures. 
- Je n'ai pas mesuré au-delà de 1000 points pour la triangulation.

## Ce que je ferais autrement
- Créer le `.gitignore` et lire tous les fichiers fournis avant de commencer.
- Faire très tôt un test d'API de bout en bout pour valider l'architecture.
- Choisir et justifier l'algorithme dès le plan.
- Confirmer l'ordre des octets (little-endian supposé) avec l'enseignant.

## Utilisation d'un assistant IA
J'ai conçu seule mon plan de tests (rendu 1). Claude m'a ensuite aidée à le
relire et à mettre en place l'outillage, et m'a fourni une grande partie du
code et des tests. Mon travail a été de les intégrer, de lancer et de
vérifier chaque étape, et de signaler les écarts. J'ai compris le principe
de l'algorithme : on trie les points de gauche à droite, puis chaque nouveau 
point est relié aux côtés du contour qu’il voit, ce qui crée de nouveaux triangles. 
Ce qui m'a permis d'avoir mon `make coverage` qui affiche 100ù sur `triangulator/` : chaque
ligne et chaque branche de mon code est exécutée par les 58 tests unitaires.