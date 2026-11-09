# Shalin Bhavsar — Portfolio (Django + DRF + PostgreSQL)

A portfolio site backed by a real database. Public visitors get a
read-only gallery; you manage the artwork through Django's built-in
admin at `/admin/`, which is login-protected — no one else can add,
edit, or remove pieces.

## How it's put together

- **`gallery/models.py`** — the `Artwork` model: title, medium
  (graphite/ink), portrait flag, date label, image, description,
  display order, and a publish toggle so you can hide a piece without
  deleting it.
- **`gallery/admin.py`** — the admin interface where you'll actually
  add new work: upload an image, fill in the fields, save. Includes a
  live thumbnail preview.
- **`gallery/views.py` + `gallery/urls.py`** — the public homepage
  (server-rendered from the database) and a read-only REST API at
  `/api/artworks/` (built with Django REST Framework), which supports
  `?medium=ink` filtering if you ever want to build another frontend
  against it.
- **`static/gallery/`** — the site's CSS/JS (same graphite-and-paper
  visual design as before, now driven by the database instead of a
  hardcoded list).
- **`portfolio_site/settings.py`** — reads all environment-specific
  config (secret key, database, media storage) from environment
  variables, so the same code runs locally on SQLite and in
  production on PostgreSQL without edits.

## Run it locally

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # defaults to local SQLite, no DB setup needed

python3 manage.py migrate
python3 manage.py createsuperuser # your admin login
python3 manage.py seed_artwork    # optional: loads the 12 pieces already in seed_images/
python3 manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the site and
`http://127.0.0.1:8000/admin/` to log in and manage artwork.

## Deploying for free

This is set up for **Render** (free web hosting) + **Neon** (free
PostgreSQL) + **Cloudinary** (free image storage). Render's free tier
wipes its local disk on every redeploy, so Neon and Cloudinary are
what make your database and images actually persist.

### 1. Create a free PostgreSQL database on Neon

1. Sign up at [neon.tech](https://neon.tech) (free tier, no card
   required).
2. Create a project. Copy the connection string it gives you — it
   looks like `postgres://USER:PASSWORD@HOST/DBNAME?sslmode=require`.

### 2. Create a free image store on Cloudinary

1. Sign up at [cloudinary.com](https://cloudinary.com) (free tier).
2. From your dashboard, copy the **CLOUDINARY_URL** value — it looks
   like `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`.

### 3. Push this project to a GitHub repo

Render deploys from a Git repo, so this folder needs to be pushed to
GitHub (or GitLab) first.

### 4. Create a free web service on Render

1. Sign up at [render.com](https://render.com).
2. **New → Web Service**, connect your repo.
3. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start command: `gunicorn portfolio_site.wsgi`
5. Choose the **Free** instance type.
6. Under **Environment**, add:
   - `SECRET_KEY` — any long random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — `your-app-name.onrender.com`
   - `DATABASE_URL` — the Neon connection string from step 1
   - `CLOUDINARY_URL` — the Cloudinary URL from step 2
7. Deploy. Render runs migrations automatically via the `release`
   line in `Procfile`.
8. Once it's live, open a shell from the Render dashboard (or run
   locally against `DATABASE_URL` pointed at Neon) and run:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_artwork   # if you haven't added pieces yet
   ```

Your site is now live at `https://your-app-name.onrender.com`, and
`/admin/` is where you'll add every new piece from here on.

**Free-tier note:** Render's free web service spins down after periods
of inactivity and takes ~30-60 seconds to wake back up on the next
visit. That's normal on the free tier — upgrading to a paid instance
removes the spin-down, if it ever bothers you.

## Adding new artwork

Once deployed, this is the whole workflow:

1. Go to `https://your-app-name.onrender.com/admin/`
2. Log in with your superuser account
3. **Artworks → Add artwork**
4. Upload the image, set title/medium/date, save

It appears on the public site immediately — no code changes, no
redeploying.

## Switching to MSSQL later

You mentioned having MSSQL available too. This project uses
PostgreSQL because it has a genuinely free, no-expiry hosted tier
(Neon) that fits a personal portfolio well, whereas free hosted MSSQL
options are far more limited. If you'd rather run this against MSSQL
(e.g. on infrastructure you already have), swap the database backend
to `mssql-django` and point `DATABASE_URL`-equivalent settings at your
SQL Server instance — the models, admin, and API don't need to change.
