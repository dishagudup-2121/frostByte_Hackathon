# 🚀 Deployment Guide for GeoDrive Insight

## Table of Contents
1. [Quick Start](#quick-start)
2. [Deployment Platforms](#deployment-platforms)
3. [Backend Deployment (Render.com)](#backend-deployment-rendercom)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Environment Variables](#environment-variables)
6. [Database Setup](#database-setup)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Quick Start

This project is a full-stack application with:
- **Frontend**: React with Vite
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL
- **AI**: Mistral AI

---

## Deployment Platforms

### Recommended: Render.com + Vercel ⭐

| Platform | Component | Cost | Setup Time |
|----------|-----------|------|------------|
| **Render.com** | Backend + Database | Free tier available | 5 min |
| **Vercel** | Frontend | Free tier | 3 min |

Alternative options:
- Railway.app (full-stack, single platform)
- Heroku (all-in-one but paid)
- AWS + GitHub Codespaces

---

## Backend Deployment (Render.com)

### Step 1: Prepare Backend
```bash
# Make sure requirements.txt is updated
pip freeze > requirements.txt

# Test locally with Docker
docker-compose up
```

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub repository

### Step 3: Deploy Backend Service

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (dishagudup-2121/frostByte_Hackathon)
   - Choose Python as runtime

2. **Configure Service**
   - **Name**: geodrive-backend
   - **Environment**: Python 3.12
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`

3. **Add Environment Variables**
   - Click "Environment"
   - Add the following:
     ```
     MISTRAL_API_KEY=your_mistral_api_key_here
     DATABASE_URL=your_supabase_postgres_url
     ENVIRONMENT=production
     ```

4. **Deploy Database**
   - Click "New +" → "PostgreSQL"
   - Name: `geodrive-db`
   - Copy the internal database URL to `DATABASE_URL` above

### Step 4: Get Backend URL
After deployment, your backend URL will be:
```
https://geodrive-backend.onrender.com
```

---

## Frontend Deployment (Vercel)

### Step 1: Update Environment Variables

Create `.env.production` in frontend folder:
```
VITE_API_BASE_URL=https://geodrive-backend.onrender.com
```

### Step 2: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your GitHub repository

### Step 3: Deploy Frontend

1. **Select Repository**
   - Choose: `dishagudup-2121/frostByte_Hackathon`

2. **Configure Project**
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Add Environment Variables**
   - Add `VITE_API_BASE_URL`:
     ```
     https://geodrive-backend.onrender.com
     ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

Your frontend URL will be:
```
https://geodrive-insight.vercel.app
```

---

## Environment Variables

### Backend (.env)
```
MISTRAL_API_KEY=your_mistral_api_key
DATABASE_URL=postgresql://user:password@host:5432/database
ENVIRONMENT=production
```

### Frontend (.env or .env.production)
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

---

## Database Setup

### Option 1: Using Supabase (Recommended)
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Copy the PostgreSQL connection string
4. Use in `DATABASE_URL`

### Option 2: Render.com PostgreSQL
- Follow Step 4 in Backend Deployment section
- Render automatically creates and manages the database

---

## Local Development with Docker

### Prerequisites
- Docker Desktop installed
- `.env` file with your API keys

### Run Locally
```bash
docker-compose up
```

Access:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173 (after `npm run dev` in frontend folder)

---

## Post-Deployment Checklist

- [ ] Backend is running on Render.com
- [ ] Database migrations completed
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set correctly
- [ ] API endpoints connected (check browser console)
- [ ] Test API calls from frontend
- [ ] Monitor error logs on Render dashboard
- [ ] Set up GitHub actions for auto-deploy (optional)

---

## Monitoring & Troubleshooting

### Check Backend Logs
1. Go to Render Dashboard
2. Select "geodrive-backend"
3. View logs in real-time

### Common Issues

#### 1. Frontend can't connect to backend
```
Error: CORS error or connection refused
```
**Solution:**
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings in `backend/main.py`
- Ensure backend is running

#### 2. Database connection error
```
Error: Could not connect to postgresql
```
**Solution:**
- Verify `DATABASE_URL` format
- Check database credentials
- Ensure database service is running

#### 3. Build fails on Vercel
```
Error: Module not found
```
**Solution:**
- Run `npm install` locally first
- Check `frontend/.env` variables
- Verify build command in Vercel settings

### Useful Commands

```bash
# Test backend locally
uvicorn backend.main:app --reload

# Build frontend
npm run build

# Run tests
pytest

# Check API health
curl https://your-backend-url/
```

---

## Next Steps

1. ✅ Deploy backend to Render.com
2. ✅ Deploy frontend to Vercel
3. ✅ Set up monitoring/logging
4. ✅ Configure CI/CD pipelines
5. ✅ Set up custom domain (optional)
6. ✅ Enable auto-scaling (Render paid tier)

---

## Support Resources

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Deployment](https://react.dev/learn/deployment)

---

**Last Updated**: March 2, 2026
