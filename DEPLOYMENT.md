# Quiz App Backend - Deployment Guide

## Render.com Deployment

### 1. Repository Setup
- Push your code to GitHub
- Connect your repository to Render.com

### 2. Environment Variables
Set these environment variables in Render:

```
HOST=0.0.0.0
PORT=10000
RELOAD=false
SECRET_KEY=your-production-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./quiz_app.db
```

### 3. Build Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python start.py`

### 4. Health Check
The app includes a health check endpoint at `/health` for monitoring.

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Development Server
```bash
python run.py
```

### 3. Run Production Server
```bash
python start.py
```

## Database

### SQLite (Development)
- File: `quiz_app.db`
- Automatically created on first run

### PostgreSQL (Production)
- Update `DATABASE_URL` environment variable
- Example: `postgresql://user:password@host:port/dbname`

## Testing

### Run Tests
```bash
python test_api.py
```

### Initialize Sample Data
```bash
python init_db.py
```

## API Endpoints

- **Health Check**: `GET /health`
- **Root**: `GET /`
- **Request OTP**: `POST /request-otp`
- **Register**: `POST /register`
- **Login**: `POST /login`
- **Questions**: `GET /questions`
- **Create Question**: `POST /questions`
- **Quiz Attempt**: `POST /quiz-attempt`
- **Leaderboards**: `GET /leaderboard/{week|month|year}`
- **User Info**: `GET /user/info`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure all dependencies are in `requirements.txt`
2. **Database Errors**: Check database URL and permissions
3. **Port Conflicts**: Verify port configuration in environment variables

### Logs
Check Render logs for detailed error information.

## Security Notes

- Change `SECRET_KEY` in production
- Use HTTPS in production
- Consider rate limiting for production use
- Monitor OTP usage patterns
