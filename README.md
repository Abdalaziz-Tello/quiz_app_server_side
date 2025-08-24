# Quiz App Backend

A FastAPI-based backend for a quiz application with JWT authentication, SQLite database, and leaderboard functionality.

## Features

- **IP-Based Authentication**: No passwords needed! Uses OTP (One-Time Password) for daily access
- **Automatic User Creation**: Users are automatically created based on their IP address
- **Daily OTP System**: New OTP available each day, expires in 10 minutes
- **Question Management**: CRUD operations for quiz questions with points and time limits
- **Quiz Attempts**: Track user quiz attempts with scores and completion times
- **Leaderboards**: Weekly, monthly, and yearly leaderboards based on quiz performance
- **SQLite Database**: Lightweight database for storing all application data

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

#### POST /request-otp
Request OTP for your IP address
```json
{
  "ip_address": "192.168.1.100",
  "device_id": "optional_device_id"
}
```

#### POST /register
Register with a nickname (IP address is automatically detected)
```json
{
  "nickname": "QuizMaster",
  "device_id": "optional_device_id"
}
```

#### POST /login
Login using IP address and OTP
```json
{
  "ip_address": "192.168.1.100",
  "otp_code": "123456"
}
```

### Questions

#### GET /questions
Get all questions (public endpoint)

#### POST /questions
Create a new question (requires authentication)
```json
{
  "question_text": "What is the capital of France?",
  "option_a": "London",
  "option_b": "Paris",
  "option_c": "Berlin",
  "option_d": "Madrid",
  "correct_answer": "B",
  "points": 10,
  "time_limit": 30
}
```

### Quiz Attempts

#### POST /quiz-attempt
Submit a quiz attempt (requires authentication)
```json
{
  "score": 85,
  "total_points": 100,
  "time_taken": 450
}
```

#### GET /user/info
Get current user information (requires authentication)

### Leaderboards

#### GET /leaderboard/week
Get weekly leaderboard (top 10 players)

#### GET /leaderboard/month
Get monthly leaderboard (top 10 players)

#### GET /leaderboard/year
Get yearly leaderboard (top 10 players)

## Database Schema

### Users Table
- `id`: Primary key
- `ip_address`: Unique IP address identifier
- `device_id`: Unique device identifier
- `nickname`: User's display name
- `created_at`: User registration timestamp
- `last_active`: Last activity timestamp
- `is_active`: User account status

### OTP Table
- `id`: Primary key
- `ip_address`: IP address requesting OTP
- `otp_code`: 6-digit OTP code
- `created_at`: OTP creation timestamp
- `expires_at`: OTP expiration timestamp
- `is_used`: Whether OTP has been used
- `daily_attempts`: Number of OTP requests today

### Questions Table
- `id`: Primary key
- `question_text`: The question content
- `option_a`, `option_b`, `option_c`, `option_d`: Multiple choice options
- `correct_answer`: Correct answer (A, B, C, or D)
- `points`: Points awarded for correct answer
- `time_limit`: Time limit in seconds

### Quiz Attempts Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `score`: User's score
- `total_points`: Total possible points
- `time_taken`: Time taken to complete quiz (seconds)
- `completed_at`: Quiz completion timestamp

## Authentication Flow

### How It Works:
1. **Request OTP**: User requests a 6-digit OTP for their IP address
2. **Receive OTP**: System generates and returns OTP (expires in 10 minutes)
3. **Login**: User provides IP address and OTP to get JWT token
4. **Daily Access**: New OTP available each day (max 5 attempts per day)

### Benefits:
- **No Passwords**: Users don't need to remember passwords
- **IP-Based**: Automatic user identification by IP address
- **Secure**: OTP expires quickly and is single-use
- **Convenient**: Perfect for daily quiz access

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **IP-Based Security**: Users identified by IP address
- **OTP System**: One-time passwords that expire quickly
- **Daily Limits**: Maximum 5 OTP requests per day per IP
- **CORS Support**: Cross-origin resource sharing enabled
- **Input Validation**: Pydantic models for request validation

## Usage Examples

### 1. Request OTP
```bash
curl -X POST "http://localhost:8000/request-otp" \
     -H "Content-Type: application/json" \
     -d '{"ip_address": "192.168.1.100", "device_id": "my_device"}'
```

### 2. Register with Nickname
```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"nickname": "QuizMaster", "device_id": "my_device"}'
```

### 3. Login with OTP
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"ip_address": "192.168.1.100", "otp_code": "123456"}'
```

### 3. Create a Question (with token)
```bash
curl -X POST "http://localhost:8000/questions" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"question_text": "Sample question?", "option_a": "A", "option_b": "B", "option_c": "C", "option_d": "D", "correct_answer": "A", "points": 10, "time_limit": 30}'
```

### 4. Submit Quiz Attempt
```bash
curl -X POST "http://localhost:8000/quiz-attempt" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"score": 90, "total_points": 100, "time_taken": 300}'
```

### 5. Get Leaderboards
```bash
# Weekly leaderboard
curl "http://localhost:8000/leaderboard/week"

# Monthly leaderboard
curl "http://localhost:8000/leaderboard/month"

# Yearly leaderboard
curl "http://localhost:8000/leaderboard/year"
```

## Configuration

### Environment Variables
- `SECRET_KEY`: JWT secret key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30 minutes)

### Database
- SQLite database file: `quiz_app.db` (created automatically)
- Database URL: `sqlite:///./quiz_app.db`

## Development

### Adding New Features
1. Create new database models in the main.py file
2. Add corresponding Pydantic models
3. Implement API endpoints
4. Update database schema

### Testing
The API includes automatic interactive documentation at `/docs` for testing endpoints directly in the browser.

## Production Considerations

1. **Change SECRET_KEY**: Use a strong, random secret key
2. **Database**: Consider using PostgreSQL or MySQL for production
3. **HTTPS**: Enable HTTPS in production
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Logging**: Add proper logging and monitoring
6. **Environment Variables**: Use environment variables for sensitive configuration

## License

This project is open source and available under the MIT License.
