# Sephora Trend Research - Setup Guide

This guide will help you set up and run both the FastAPI backend and Streamlit frontend.

## 🏗️ Architecture Overview

- **Backend**: FastAPI with Google ADK multi-agent system for AI-powered trend discovery
- **Frontend**: Streamlit web application for visualizing and discovering trends
- **API Communication**: REST API endpoints connecting frontend to backend

---

## 📋 Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account with Gemini API access
- Git (for version control)

---

## 🚀 Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Install Dependencies

Using Poetry (recommended):
```bash
poetry install
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Google Cloud Configuration
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

Load the environment variables:
```bash
source .env
```

### 4. Start the Backend Server

```bash
cd src
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`

### 5. Verify Backend is Running

Open your browser and visit:
- API Health: http://localhost:8000/
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

You should see `{"status": "ok"}` at the root endpoint.

---

## 🎨 Frontend Setup

### 1. Return to Project Root

```bash
cd ..  # Return to project root
```

### 2. Install Streamlit Dependencies

```bash
pip install -r requirements-streamlit.txt
```

### 3. Configure Backend URL (Optional)

The default backend URL is `http://localhost:8000`. If your backend is running on a different URL, you can:

**Option A:** Edit the `streamlit_app.py` file:
```python
API_BASE_URL = "http://your-backend-url:port"
```

**Option B:** Change it in the Streamlit UI Settings sidebar after launching.

### 4. Start the Streamlit App

```bash
streamlit run streamlit_app.py
```

The frontend will automatically open in your browser at: `http://localhost:8501`

---

## 🔗 Connecting Frontend to Backend

### Automatic Connection

When you launch the Streamlit app, it will automatically check if the backend is running at the configured URL.

- ✅ **Connected**: Green status indicator "Connected to AI Backend"
- ⚠️ **Disconnected**: Warning message with instructions

### Manual Reconnection

If the backend connection fails:

1. Make sure the backend is running (`http://localhost:8000`)
2. In the Streamlit sidebar, go to **⚙️ Settings**
3. Verify the **Backend URL** is correct
4. Click **🔄 Reconnect to Backend**

---

## 🎯 Using the Application

### View 1: Sephora Trend Discovery

Browse all discovered trends organized by category:
- **Categories**: Skincare, Makeup, Hair, Fragrance, Bath & Body, Tools & Brushes, Men, Gifts, Mini Size
- **Sorting**: Trends sorted by virality score
- **Details**: Expand each card to see full insights, performance metrics, and expert notes

### View 2: Trend Discovery

Discover new trends using AI:

1. **Search Existing Trends**
   - Enter a trend name (e.g., "Glass Skin")
   - Click "🔍 Search Existing Trends"
   - View results from local and backend database

2. **Discover New Trends with AI** (Requires Backend Connection)
   - Enter a trend query (e.g., "clean beauty trends for 2024")
   - Click "✨ Discover New Trends with AI"
   - Wait 2-3 minutes while the AI multi-agent system researches
   - View discovered trends organized by category

### Backend Features

- **📥 Load Recent Trends**: Import previously discovered trends from backend
- **🗑️ Clear Local Trends**: Reset to default demo trends
- **📊 Stats**: View total trends and user ID

---

## 🔧 API Endpoints

### Backend Endpoints Used by Frontend

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Health check |
| `/analysis/` | POST | Discover new trends using AI |
| `/trends/search` | GET | Search existing trends |
| `/trends/recent` | GET | Get recent trends |

### Request Example: Discover Trends

```bash
curl -X POST "http://localhost:8000/analysis/" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "unique-session-id",
    "user_id": "user-123",
    "trend_query": "sustainable beauty trends",
    "created_at": "2025-01-10T12:00:00Z"
  }'
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend fails to start
- **Solution**: Verify Google Cloud credentials are set correctly
- Check `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account key
- Ensure GCP project has Gemini API enabled

**Problem**: `/analysis/` endpoint times out
- **Solution**: Trend discovery takes 2-3 minutes. Increase timeout in `streamlit_app.py`:
  ```python
  API_TIMEOUT = 600  # 10 minutes
  ```

### Frontend Issues

**Problem**: "Backend not connected" warning
- **Solution**:
  1. Verify backend is running: `curl http://localhost:8000/`
  2. Check firewall/network settings
  3. Try manual reconnection in Settings sidebar

**Problem**: Trends not loading
- **Solution**:
  1. Check browser console for errors (F12)
  2. Verify backend URL is correct
  3. Try "🔄 Reconnect to Backend"

**Problem**: Streamlit shows "Connection Error"
- **Solution**: Check if port 8501 is available
  ```bash
  lsof -i :8501
  ```
  If occupied, kill the process or change Streamlit port:
  ```bash
  streamlit run streamlit_app.py --server.port 8502
  ```

---

## 📁 Project Structure

```
Sephora-Trend-Research/
├── backend/
│   ├── src/
│   │   ├── app.py                 # FastAPI application
│   │   ├── routers/               # API route handlers
│   │   ├── agents/                # AI agents
│   │   ├── models/                # Pydantic models
│   │   └── config/                # Configuration
│   ├── pyproject.toml
│   └── README.md
├── streamlit_app.py               # Streamlit frontend
├── requirements-streamlit.txt     # Frontend dependencies
├── SETUP_GUIDE.md                 # This file
└── .env                           # Environment variables (create this)
```

---

## 🔐 Security Notes

- Never commit `.env` files or service account keys to version control
- Add `.env` and `*.json` (service accounts) to `.gitignore`
- Use environment variables for sensitive configuration
- Backend should use HTTPS in production
- Consider adding authentication for production deployments

---

## 🚢 Production Deployment

### Backend Deployment

Recommended platforms:
- **Google Cloud Run** (serverless, auto-scaling)
- **AWS ECS/EKS** (containerized)
- **DigitalOcean App Platform**

Update backend URL in production:
```python
API_BASE_URL = "https://your-backend-domain.com"
```

### Frontend Deployment

Recommended platforms:
- **Streamlit Community Cloud** (free tier available)
- **Heroku**
- **AWS Amplify**

Environment variable setup:
```bash
BACKEND_URL=https://your-backend-domain.com
```

---

## 📊 Performance Tips

1. **Backend**: Use caching for repeated queries
2. **Frontend**: Implement pagination for large trend lists
3. **API**: Add request rate limiting
4. **Database**: Index frequently queried fields
5. **Images**: Use CDN for image assets

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `backend/src/logs/app_logs.log`
3. Check FastAPI docs: http://localhost:8000/docs
4. Review Google ADK documentation for agent issues

---

## 📝 Development Tips

### Running Both Services Concurrently

Use `tmux` or separate terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend/src
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app.py
```

### Hot Reload

Both services support hot reload:
- **Backend**: Uvicorn's `--reload` flag watches for file changes
- **Frontend**: Streamlit automatically detects changes

### Testing API Endpoints

Use the built-in Swagger UI:
1. Navigate to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters and execute

---

## ✅ Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Google Cloud credentials configured
- [ ] Backend dependencies installed
- [ ] Backend server running on port 8000
- [ ] Streamlit dependencies installed
- [ ] Streamlit app running on port 8501
- [ ] Frontend shows "Connected to AI Backend"
- [ ] Test trend search working
- [ ] Test AI discovery working

---

## 🎉 You're Ready!

Your Sephora Trend Research platform is now fully operational. Try discovering some trends!

**Example queries to try:**
- "clean beauty ingredients 2024"
- "Korean skincare innovations"
- "sustainable makeup packaging"
- "men's grooming trends"
- "hair care for damaged hair"
