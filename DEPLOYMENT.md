# Deploying DC Gadgets to Vercel

This Django project is pre-configured for Vercel (WSGI runtime + WhiteNoise for
static files). Vercel's serverless filesystem is **read-only and ephemeral**, so
SQLite will not persist between requests in production — you need a hosted
Postgres database.

## 1. Get a free Postgres database
Use any of these (all have a free tier):
- Neon (neon.tech)
- Supabase (supabase.com)
- Vercel Postgres (from your Vercel project's Storage tab)

Copy the connection string — it looks like:
`postgresql://user:password@host/dbname?sslmode=require`

## 2. Push this project to GitHub
```bash
git init
git add .
git commit -m "Initial commit - DC Gadgets scheduler"
git branch -M main
git remote add origin https://github.com/<your-username>/dc-gadgets.git
git push -u origin main
```

## 3. Import the project on Vercel
1. Go to vercel.com -> **Add New... -> Project** -> import your GitHub repo.
2. Vercel will detect `vercel.json` and use the Python runtime automatically.
3. Under **Environment Variables**, add:
   - `DATABASE_URL` = your Postgres connection string from step 1
   - `SECRET_KEY` = a new random Django secret key (generate one, don't reuse the dev one in settings.py)
   - `DEBUG` = `False`
4. Click **Deploy**.

## 4. Run migrations against the production database
Vercel doesn't give you a shell, so run migrations from your local machine
pointed at the same `DATABASE_URL`:
```bash
export DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require"
python manage.py migrate
python manage.py createsuperuser
```

## 5. Collect static files
```bash
python manage.py collectstatic --noinput
```
Commit the generated `staticfiles/` folder (or run this as part of a Vercel
build step) so WhiteNoise/`vercel.json`'s static route can serve CSS.

## 6. Visit your live URL
Vercel gives you a URL like `https://dc-gadgets-scheduler.vercel.app` —
this is the link to put in Section 6 ("Hosted Link") of the project
documentation.

## Local development (no Vercel/Postgres needed)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Visit http://127.0.0.1:8000/
