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
- **`gallery/management/commands/export_static.py`** — renders the
  public page to `dist/` as plain files (HTML, CSS, JS, images) so it
  can be hosted anywhere static, with no server at request time.
- **`portfolio_site/settings.py`** — reads all environment-specific
  config (secret key, database, media storage) from environment
  variables, so the same code runs locally on SQLite and in
  production on PostgreSQL without edits.

## Run it locally

Nothing external is needed: no database to install, no accounts, no
keys. `DEBUG` defaults to on, the database falls back to a SQLite file
in this folder, and images are served straight off disk.

**Windows (PowerShell)**, from this folder:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py load_portfolio
python manage.py runserver 8042
```

**macOS / Linux**:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py load_portfolio
python3 manage.py runserver 8042
```

Then open `http://127.0.0.1:8042/`.

Notes:

- **`.env` is optional locally.** Every setting has a working default,
  so the site runs without one. Copying `.env.example` just gives you
  somewhere to put a real `SECRET_KEY`. It is gitignored, so a fresh
  clone won't have it.
- **`load_portfolio`** loads the 31 curated pieces from
  `seed_images/portfolio/`. It matches on slug and updates in place, so
  running it again is safe and won't duplicate anything. Add `--retire`
  to unpublish anything outside that selection.
- **`seed_artwork`** is the older, smaller seed command, kept only for
  reference. Use `load_portfolio`.
- **The port is deliberate.** 8000 is taken by another project on this
  machine, so pass a port explicitly. Any free one works.
- **Admin:** run `python manage.py createsuperuser` once, then log in at
  `http://127.0.0.1:8042/admin/` to add or edit pieces through the
  browser instead of editing `load_portfolio.py`.

## Deploying for free

Two pieces, both on permanently free tiers:

| | What it is | Who uses it | Sleeps? |
|---|---|---|---|
| **Public site** | Static export on Cloudflare Pages | Anyone you send the link to | Never |
| **Admin** | Django on Render, database on Neon | Only you | Yes, and that's fine |

The public site is the link you hand to a studio, so it has to be
instant. It is a folder of plain files with no database and no server
behind it, which means nothing to spin up, nothing to expire and no
cold start.

The admin is a tool for one person. It can take a minute to wake up
because the only one waiting is you.

### Part 1: the public site

Everything the build needs is already in this repo, so this part takes
one account.

1. Sign up at [cloudflare.com](https://cloudflare.com) (no card).
2. **Workers & Pages → Create → Pages → Connect to Git**, pick this
   repo. Project name `shalin-portfolio` (it must match the name in
   `.github/workflows/deploy-static.yml`).
3. When it asks for a build command, leave it empty and set the output
   directory to `dist`. GitHub Actions does the building, not
   Cloudflare.
4. In Cloudflare, **My Profile → API Tokens → Create Token**, using
   the *Edit Cloudflare Workers* template. Copy the token. Copy your
   Account ID from the Workers & Pages sidebar too.
5. In GitHub, **Settings → Secrets and variables → Actions**, add:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
6. Push to `main`, or run the workflow by hand from the Actions tab.

The site is then live at `https://shalin-portfolio.pages.dev`, and
every push to `main` redeploys it. A custom domain is free under the
project's **Custom domains** tab, HTTPS included.

To see exactly what will be published, build it locally:

```bash
python manage.py export_static
python -m http.server 8055 --directory dist
```

### Part 2: the admin

Only worth doing if you want to add pieces from a browser instead of
editing `load_portfolio.py`. Skip it otherwise; Part 1 stands alone.

1. **Database.** Sign up at [neon.tech](https://neon.tech), create a
   project, copy the connection string
   (`postgres://USER:PASSWORD@HOST/DBNAME?sslmode=require`). The free
   plan does not expire. Render's own free Postgres *does*, after 30
   days, which is why the database lives here instead.
2. **Image storage.** Sign up at
   [cloudinary.com](https://cloudinary.com) and copy the
   **CLOUDINARY_URL** (`cloudinary://API_KEY:API_SECRET@CLOUD_NAME`).
   Render's free disk is wiped on every restart, so without this any
   image you upload through the admin disappears.
3. **Web service.** At [render.com](https://render.com): **New → Web
   Service**, connect the repo.
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn portfolio_site.wsgi`
   - Instance type: **Free**
   - Environment variables: `SECRET_KEY` (any long random string),
     `DEBUG=False`, `ALLOWED_HOSTS=your-app.onrender.com`,
     `DATABASE_URL`, `CLOUDINARY_URL`
   - Migrations run automatically from the `release` line in `Procfile`.
4. Create your login and load the existing pieces, from Render's shell
   or locally with `DATABASE_URL` pointed at Neon:

   ```bash
   python manage.py createsuperuser
   python manage.py load_portfolio
   ```

### Keeping the two in sync

This is the part that matters. By default the static build reads the
**repo**, so work added through the admin would never appear publicly.

To connect them, add the same two values as GitHub Actions secrets:

- `DATABASE_URL`
- `CLOUDINARY_URL`

The workflow then skips the seed and builds from the live database
instead. After adding a piece in the admin, trigger **Deploy static
site** from the Actions tab and the public site catches up.

Without those secrets the admin is a scratchpad: real, usable, but
invisible to visitors.

### What each free tier actually gives you

Checked November 2026; these change, so confirm before relying on them.

- **Cloudflare Pages:** unlimited bandwidth on static assets, 500
  builds a month, 20,000 files and 25 MiB per file. This site is about
  13 MB across ~45 files.
- **Neon:** no expiry, 1 GB storage per project, 100 compute-hours a
  month, suspends rather than bills when exceeded. Compute sleeps after
  5 minutes idle.
- **Cloudinary:** 25 credits a month, where a credit is roughly 1 GB of
  storage or 1 GB of bandwidth. The whole image set is 12 MB.
- **Render free:** 512 MB RAM, 750 instance-hours a month per
  workspace, spins down after 15 minutes idle and takes 30 to 60
  seconds to wake. No persistent disk. Render's docs say not to use
  free instances for production, which is the other reason the public
  site is not on it.

## Adding new artwork

Nothing reaches the public site until the static build runs. That is
the trade for a site that never sleeps.

**Through the repo** (no accounts beyond GitHub, and the build stays
reproducible):

1. Put the image in `seed_images/portfolio/`, resized to about 1800px
   on the long edge.
2. Add an entry to `WORKS` in
   `gallery/management/commands/load_portfolio.py`.
3. Commit and push. The workflow rebuilds and redeploys.

**Through the admin** (needs Part 2, and the two sync secrets):

1. Go to `https://your-app-name.onrender.com/admin/`, log in.
2. **Artworks → Add artwork**, upload the image, fill in the fields,
   save.
3. Run **Deploy static site** from the repo's Actions tab.

The second route is quicker in the moment, but the piece then exists
only in Neon and Cloudinary, not in this repo. The first keeps
everything in version control.

## Switching to MSSQL later

You mentioned having MSSQL available too. This project uses
PostgreSQL because it has a genuinely free, no-expiry hosted tier
(Neon) that fits a personal portfolio well, whereas free hosted MSSQL
options are far more limited. If you'd rather run this against MSSQL
(e.g. on infrastructure you already have), swap the database backend
to `mssql-django` and point `DATABASE_URL`-equivalent settings at your
SQL Server instance — the models, admin, and API don't need to change.
