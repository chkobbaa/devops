# Gestion des Incidents IT — Mini-Projet DevOps (DSI3)

Application web simple de gestion et de suivi des incidents informatiques pour un établissement d'enseignement supérieur, accompagnée d'une chaîne DevOps complète (Git/GitHub, Docker, Docker Compose, GitHub Actions CI/CD et GHCR).

---

## 1. Fonctionnalités de l'application

L'application permet aux étudiants et aux enseignants de :

1. **Ajouter un incident** (`/incidents/add`) : titre, description, lieu (salle ou laboratoire) et priorité (`Faible`, `Moyenne`, `Élevée`).
2. **Afficher la liste des incidents** (`/`) : tableau récapitulatif avec indicateurs de priorité et de statut.
3. **Consulter les détails d'un incident** (`/incidents/<id>`) : affichage complet des informations.
4. **Modifier le statut d'un incident** (`/incidents/<id>/status`) : passage entre `Nouveau`, `En cours` et `Résolu`.
5. **Supprimer un incident** (`/incidents/<id>/delete`) : suppression depuis la liste ou la page de détails.
6. **Vérifier l'état du service** (`/health`) : route de santé retournant `{"status": "OK"}`.

---

## 2. Technologies utilisées

- **Langage :** Python 3.11
- **Framework web :** Flask 3.0.0
- **Base de données :** SQLite (`sqlite3` intégré à Python)
- **Interface :** HTML, CSS, templates Jinja2
- **Tests automatisés :** pytest
- **Conteneurisation :** Docker & Docker Compose
- **CI/CD & Registre :** GitHub Actions & GitHub Container Registry (GHCR)

---

## 3. Structure du projet

```text
devops/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add_incident.html
│   └── incident_detail.html
├── static/
│   └── style.css
├── tests/
│   ├── conftest.py
│   ├── test_home.py
│   └── test_incidents.py
├── data/                   # Base SQLite générée automatiquement (ignorée par Git)
├── Dockerfile
├── compose.yaml
├── compose.deploy.yaml
├── requirements.txt
├── .gitignore
├── .dockerignore
├── README.md
└── .github/
    └── workflows/
        ├── ci.yml
        └── cd.yml
```

---

## 4. Installation des dépendances

```bash
python -m venv .venv
# Sur Linux / macOS :
source .venv/bin/activate
# Sur Windows (PowerShell) :
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## 5. Lancer l'application en local

```bash
python app.py
```

L'application est accessible sur `http://localhost:5000` (et `/health` sur `http://localhost:5000/health`).
La base de données SQLite est créée automatiquement dans `data/incidents.db`.

---

## 6. Exécuter les tests automatisés

```bash
pytest -v
```

Les tests utilisent `app.test_client()` et une base SQLite temporaire afin de ne jamais modifier les données de l'application.

---

## 7. Construire et exécuter avec Docker

Construire l'image Docker :

```bash
docker build -t gestion-incidents:1.0 .
```

Lancer un conteneur :

```bash
docker run -d -p 5000:5000 --name gestion-incidents-app gestion-incidents:1.0
```

Vérifier les logs et arrêter le conteneur :

```bash
docker ps
docker logs gestion-incidents-app
docker stop gestion-incidents-app && docker rm gestion-incidents-app
```

---

## 8. Orchestration avec Docker Compose

Démarrer l'application (avec construction de l'image) :

```bash
docker compose up -d --build
```

Vérifier l'état et les journaux :

```bash
docker compose ps
docker compose logs web
```

Arrêter l'application tout en conservant les données :

```bash
docker compose down
```

---

## 9. Persistance des données SQLite (Volume nommé)

Dans `compose.yaml` et `compose.deploy.yaml`, le volume nommé `incidents_data` est monté sur `/app/data` dans le conteneur :

```yaml
volumes:
  - incidents_data:/app/data
```

Ainsi, supprimer et recréer le conteneur avec `docker compose down` puis `docker compose up -d` conserve tous les incidents enregistrés dans `incidents.db`.
*(Attention : `docker compose down -v` supprimerait aussi le volume et donc les données.)*

---

## 10. Pipeline d'intégration continue (CI)

Le fichier `.github/workflows/ci.yml` s'exécute automatiquement lors d'un `push` ou d'une `pull_request` vers `main` :

1. Récupère le code source (`actions/checkout@v4`).
2. Installe Python 3.11 (`actions/setup-python@v5`).
3. Installe les dépendances (`pip install -r requirements.txt`).
4. Exécute les tests (`pytest -v`).
5. Valide la configuration Compose (`docker compose config -q`).
6. Construit l'image Docker (`docker compose build`).

---

## 11. Pipeline de livraison continue (CD) vers GHCR

Le fichier `.github/workflows/cd.yml` s'exécute à chaque `push` sur `main` :

1. **Job `test`** : exécute `pytest -v`.
2. **Job `publish`** (`needs: test`) : ne démarre que si les tests réussissent. Il se connecte à `ghcr.io` avec `GITHUB_TOKEN` (permissions `contents: read` et `packages: write`) puis publie l'image `ghcr.io/chkobbaa/devops` avec deux tags : `latest` et `${{ github.sha }}`.

---

## 12. Déploiement et mise à jour avec `compose.deploy.yaml`

Le fichier `compose.deploy.yaml` utilise directement l'image publiée dans GHCR (`ghcr.io/chkobbaa/devops:latest`) sans reconstruire l'image localement :

```bash
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d
docker ps
docker compose -f compose.deploy.yaml logs
```

Vérifier ensuite dans le navigateur :
- `http://localhost:5000`
- `http://localhost:5000/health`

Pour arrêter le service :

```bash
docker compose -f compose.deploy.yaml down
```

Pour **mettre à jour** l'application après la publication d'une nouvelle image dans GHCR :

```bash
docker compose -f compose.deploy.yaml pull
docker compose -f compose.deploy.yaml up -d
```

---

## 13. Captures d'écran à préparer pour la remise

- [ ] `git log --oneline --graph --all` montrant la branche `feature/gestion-incidents` fusionnée dans `main`.
- [ ] Résultat de `pytest -v` montrant tous les tests réussis.
- [ ] Exécution de `docker compose ps` et `docker compose logs web`.
- [ ] Preuve de persistance du volume (incident visible avant et après `docker compose down` / `docker compose up -d`).
- [ ] Onglet **GitHub Actions** : exécution réussie du workflow CI.
- [ ] Onglet **GitHub Actions** : expérimentation d'une erreur provoquée (échec d'un test) suivie de sa correction et réussite.
- [ ] Onglet **GitHub Actions** : exécution réussie du workflow CD (`test` puis `publish`).
- [ ] Section **Packages (GHCR)** sur GitHub montrant l'image et les tags `latest` et `<sha>`.
- [ ] Application déployée via `compose.deploy.yaml` accessible sur `http://localhost:5000` et `http://localhost:5000/health`.
