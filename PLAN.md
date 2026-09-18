Sheinez Ben Boubaker

# **Plan de test**

Notre objectif est de coder le **Triangulator**, il doit pouvoir recevoir un `pointSetId`, aller chercher les points chez le `PointSetManager`, calculer une triangulation et renvoyer le résultat.

Le résultat est montré sur une seule route HTTP avec un **GET** :

- **200 → OK** : on renvoie les triangles.
- **400 → Erreur**

Il est préférable de commencer par le test le plus petit, ce qui est simple. Le code `Triangulator` peut se diviser en trois morceaux :

- **I - Le Binaire**
- **II - L’algorithme**
- **III - L’API**

---

## **I - Le Binaire**

Il convertit les bytes reçus en points, et les points calculés en bytes à renvoyer. On le teste avec un **test unitaire (Arrange/Act/Assert)** et **par propriété**.

Ce ne sont que des fonctions, donc c’est correct pour mettre en place :

- le **TDD** : on écrit d’abord un test dit **Red**, pour le passer à **Green**, et puis on nettoie le code (**Refactor**) ;
- et **Hypothesis** pour générer les exemples.

### **Pourquoi ?**

Le cours emploie l’**encodage et décodage**, ce qui est utile pour Hypothesis. On a une propriété simple et évidente à vérifier :

> Décoder ce qu’on vient d’encoder doit redonner exactement la chose qu’on avait au départ.

Le test unitaire par l’exemple **Arrange/Act/Assert** permet de réaliser des cas concrets pour vérifier le comportement normal.

On décode un petit exemple en vérifiant que les points obtenus sont les bons.

Ensuite, on teste le décodage d’une **liste vide** (juste les 4 premiers bytes, `N=0`) pour obtenir une liste vide sans erreur.

---

## **II - L’algorithme de triangulation**

Nous ne savons pas encore quel algorithme nous allons coder, donc on teste des choses qui doivent être vraies **peu importe le choix de l’algorithme**.

Des cas concrets, écrits à la main, où on connaît le résultat attendu :

- **3 points pas alignés → 1 triangle**
- **4 points formant un carré → 2 triangles**

Chaque indice de points dans un triangle doit être **inférieur à `N`**, sinon ça pointerait vers un point qui n’existe pas dans le `PointSet` reçu.

De plus, aucun triangle ne doit avoir une **aire de 0**, sinon ce n’est pas un vrai triangle.

On manipule des `float` et les calculs géométriques peuvent avoir des **erreurs d’arrondi**.

---

## **III - L’API**

Ici, on teste le **comportement complet de l’endpoint HTTP**, du point de vue de celui qui l’appelle. C’est un **test fonctionnel**.

C’est ici que nous allons appliquer le **design testable**.

L’idée est que dans le code, le `Triangulator` ne doit pas appeler le `PointSetManager` « en dur ». On lui passe un `pointset_client` en paramètre.

### **Pourquoi ?**

Dans le code, si l’appel HTTP est écrit directement dans la fonction, on ne peut pas tester sans un vrai serveur qui tourne.

En injectant le client, on peut le remplacer par un **faux client** dans les tests.

Le **Double de test** qu’on va utiliser serait le **Stub**.

Il servirait au `PointSetManager` de répondre avec un `PointSet` valide, et donc on vérifie que le `Triangulator` renvoie bien du **200 avec les bons triangles**.

Dans le cas d’un **Stub erreur 400**, on vérifie bien qu’il renvoie du **404**.

# **Le test Flask**

Si ça marche, l’id est valide et le `PointSetManager` répond **200**, la réponse attendue est donc le **nombre de triangles**.

---

# **Test de performance**

Le sujet le demande (`make unit_test` vs `make perf_test`), et nous savons qu’une mesure sans contexte dit peu de choses. Il nous faut donc une **charge**, une **métrique** et un **environnement**.

### **Ce qu’on va mesurer**

- Décoder un `PointSet` pour différentes tailles (**100 / 10 000 points**).
- Encoder des triangles pour différentes tailles.
- La triangulation elle-même en fonction de `N`.

### **Comment ?**

- Nous marquons ces tests avec `@pytest.mark.performance` pour pouvoir les exclure de `make unit_test`.
- Nous mesurons avec `time.perf_counter()`, plusieurs fois pour avoir une vraie fiabilité.
- Nous séparons bien la **préparation des données** de **l’opération qu’on mesure vraiment**.

# **Couverture de code**

Nous utilisons `coverage run --branch -m pytest`

### **Pourquoi ?**

Dans le code il va y avoir des `if/else`, par exemple pour gérer les erreurs 400/404/500/503. Une ligne "couverte" ne veut pas dire que le `if` et le `else` ont été testés, donc `--branch` permet de vérifier les deux côtés.