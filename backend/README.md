# 5ibra — Backend FastAPI

API REST pour la plateforme 5ibra (freelancing, mentorat, apprentissage).

## Structure du projet

```
backend/
├── alembic/              # Migrations de base de données (Alembic)
│   └── versions/         # Fichiers de migration (001_initial_schema.py)
├── app/
│   ├── core/             # Config, DB, sécurité JWT, dépendances FastAPI
│   ├── models/           # Modèles SQLAlchemy (tables PostgreSQL)
│   ├── schemas/          # Schémas Pydantic (validation entrée/sortie API)
│   ├── services/         # Logique métier (auth, scores, serializers)
│   ├── routers/          # Endpoints HTTP groupés par domaine
│   └── main.py           # Point d'entrée FastAPI + CORS
├── scripts/              # Scripts utilitaires (seed catégories)
├── requirements.txt
├── .env.example
└── alembic.ini
```

| Dossier | Rôle |
|---------|------|
| `app/core/` | Configuration (`Settings`), connexion SQLAlchemy, hash/JWT, guards par rôle |
| `app/models/` | Définition des tables et relations (User, Project, Listing, Pack, Review…) |
| `app/schemas/` | Contrats API alignés sur les types TypeScript du frontend |
| `app/services/` | Règles métier réutilisables (inscription, calcul de score 0–100) |
| `app/routers/` | Routes REST par rôle : auth, client, mentor, apprenant, admin, public |
| `alembic/` | Historique des migrations PostgreSQL sur Supabase |

## Prérequis

- Python 3.11+
- Projet Supabase existant (PostgreSQL uniquement — **pas** Supabase Auth)

---

## Étape 1 — Créer le fichier `.env`

```powershell
cd c:\Users\HP\Desktop\5ibra\backend
Copy-Item .env.example .env
```

Ouvrez `.env` et remplissez les valeurs depuis le dashboard Supabase :

1. Allez sur [supabase.com](https://supabase.com) → votre projet
2. **Project Settings** → **Database**
3. Copiez les URLs de connexion :

| Variable | Où la trouver | Usage |
|----------|---------------|-------|
| `DATABASE_URL` | **Connection string** → mode **Transaction** (pooler, port **6543**) | Runtime de l'API |
| `DIRECT_URL` | **Connection string** → mode **Session** (direct, port **5432**) | Migrations Alembic |
| `SECRET_KEY` | Générez une clé aléatoire (voir commande ci-dessous) | Signature JWT |

Générer une `SECRET_KEY` :

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

**Exemple de format** (remplacez par vos vraies valeurs, ne les partagez pas) :

```env
DATABASE_URL=postgresql://postgres.xxxxx:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres?pgbouncer=true
DIRECT_URL=postgresql://postgres.xxxxx:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
SECRET_KEY=abc123...votre_cle_generee...
```

---

## Étape 2 — Installer les dépendances

```powershell
cd c:\Users\HP\Desktop\5ibra\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Étape 3 — Appliquer la migration sur Supabase

```powershell
cd c:\Users\HP\Desktop\5ibra\backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### Vérifier dans Supabase

1. Dashboard → **Table Editor**
2. Vous devez voir les tables : `users`, `categories`, `projects`, `listings`, `applications`, `mentor_packs`, `reviews`, etc.
3. Ou dans **SQL Editor** :

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

---

## Étape 4 — Seed des catégories (optionnel mais recommandé)

```powershell
python scripts/seed_categories.py
```

---

## Étape 5 — Lancer l'API

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Santé : http://localhost:8000/health
- Doc interactive : http://localhost:8000/docs

---

## Tester l'authentification JWT via `/docs`

### 1. Inscription

- Endpoint : `POST /api/v1/auth/register`
- Body JSON exemple (client) :

```json
{
  "email": "client@test.dz",
  "password": "motdepasse123",
  "display_name": "Ahmed Client",
  "role": "client",
  "locale": "fr"
}
```

Rôles possibles : `client`, `mentor`, `apprenant` (pas `admin` via l'API publique).

### 2. Connexion

- Endpoint : `POST /api/v1/auth/login`
- Cliquez **Authorize** en haut de `/docs` **après** avoir obtenu le token
- Dans le formulaire OAuth2 :
  - **username** = votre email
  - **password** = votre mot de passe
- Ou appelez `POST /api/v1/auth/login` avec `username` + `password` (form-data)

La réponse contient `access_token` et `refresh_token`.

### 3. Utiliser le token

1. Copiez `access_token`
2. Cliquez le bouton **Authorize** (cadenas)
3. Collez : `Bearer VOTRE_ACCESS_TOKEN` ou juste le token selon le champ
4. Testez `GET /api/v1/auth/me`

### 4. Rafraîchir le token

`POST /api/v1/auth/refresh` avec `{"refresh_token": "..."}`

---

## Correspondance endpoints ↔ pages frontend

| Page frontend | Endpoint(s) API |
|---------------|-----------------|
| `/auth` | `POST /auth/register`, `POST /auth/login` |
| `/account` | `GET/PATCH /account` |
| `/*/onboarding` | `POST /account/onboarding/complete` |
| `/` (catégories) | `GET /public/categories` |
| `/mentors` | `GET /public/mentors` |
| `/mentors/[id]` | `GET /public/mentors/{id}` |
| `/apprenants/[id]` | `GET /public/apprenants/{id}` |
| `/annonces/[id]` | `GET /public/listings/{id}` |
| `/client/dashboard` | `GET /client/dashboard` |
| `/client/projets` | `GET /client/projects` |
| `/client/projets/nouveau` | `POST /client/projects` |
| `/client/projets/[id]` | `GET/PATCH /client/projects/{id}` |
| `/mentor/dashboard` | `GET /mentor/dashboard` |
| `/mentor/projets` | `GET /mentor/projects` |
| `/mentor/projets/[id]` | `GET /mentor/projects/{id}` |
| `/mentor/recrutement` | `GET/POST /mentor/recrutement/listings` |
| `/mentor/apprenants` | `GET /mentor/apprenants` |
| `/mentor/packs` | `GET/POST /mentor/packs` |
| `/mentor/boost` | `GET /mentor/boost/options`, `POST /mentor/boost/subscribe` |
| `/mentor/progression` | `GET /mentor/progression` |
| `/apprenant/dashboard` | `GET /apprenant/dashboard` |
| `/apprenant/decouvrir` | `GET /apprenant/decouvrir/listings` |
| `/apprenant/activite` | `GET /apprenant/activite/applications`, `GET /apprenant/missions` |
| `/apprenant/missions/[id]` | `GET /apprenant/missions/{id}` |
| `/apprenant/packs` | `GET /apprenant/packs`, `POST /apprenant/packs/purchase` |
| `/apprenant/progression` | `GET /apprenant/progression` |
| `/messages` | `GET/POST /messages` |
| `/notifications` | `GET /notifications` |
| `/admin/dashboard` | `GET /admin/dashboard` |
| `/admin/utilisateurs` | `GET /admin/utilisateurs` |
| `/admin/litiges` | `GET /admin/litiges` |
| `/admin/configuration` | `GET/POST/PATCH /admin/configuration/categories` |
| `/admin/boost-premium` | `GET/POST /admin/boost-premium/*` |

---

## CORS

Le frontend `http://localhost:3000` est autorisé par défaut via `CORS_ORIGINS` dans `.env`.

Pour la production, ajoutez votre domaine Vercel :

```env
CORS_ORIGINS=http://localhost:3000,https://votre-domaine.vercel.app
```

---

## Notes de sécurité

- Ne commitez jamais `.env`
- L'inscription `admin` est bloquée côté API — créez le premier admin manuellement en base ou via un script dédié
- Les mots de passe sont hashés avec bcrypt
- JWT géré entièrement par FastAPI (pas Supabase Auth)
