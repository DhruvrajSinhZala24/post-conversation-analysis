A Django REST Framework application that performs automated post-conversation analysis on chat messages between AI agents and human users. Analyzes conversations using 11 quality metrics and stores results in a database.

## ✨ Features

- **11 Analysis Parameters**: Clarity, Relevance, Accuracy, Completeness, Sentiment, Empathy, Response Time, Resolution, Escalation Need, Fallback Frequency, Overall Score
- **RESTful API**: Complete API endpoints for conversations, analysis, and reports
- **Automated Daily Analysis**: Cron job runs daily at 12 AM
- **Database Integration**: SQLite (default) or PostgreSQL support
- **Frontend UI**: Beautiful, responsive web interface
- **File Upload**: Support for JSON file uploads

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/DhruvrajSinhZala24/post-conversation-analysis.git
cd post-conversation-analysis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/conversations/` | POST | Create a conversation |
| `/api/conversations/` | GET | List all conversations |
| `/api/analyse/` | POST | Trigger analysis on a conversation |
| `/api/reports/` | GET | Get all analysis reports |
| `/api/upload/` | POST | Upload JSON file |

## 📖 Usage Examples

### Create Conversation

```bash
curl -X POST http://127.0.0.1:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Customer Support",
    "messages": [
      {"sender": "user", "message": "Hi, I need help with my order."},
      {"sender": "ai", "message": "Sure, can you share your order ID?"},
      {"sender": "user", "message": "It'\''s 12345."},
      {"sender": "ai", "message": "Thanks! Your order has been shipped."}
    ]
  }'
```

### Analyze Conversation

```bash
curl -X POST http://127.0.0.1:8000/api/analyse/ \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": 1}'
```

### Get Reports

```bash
curl http://127.0.0.1:8000/api/reports/
```

## 🔧 Cron Job Setup

```bash
# Add cron job (runs daily at 12 AM)
python manage.py crontab add

# View cron jobs
python manage.py crontab show

# Remove cron jobs
python manage.py crontab remove
```

## 📊 Analysis Parameters

The application analyzes conversations using 11 parameters:

1. **Clarity Score** - Message clarity and understandability
2. **Relevance Score** - Topic consistency
3. **Accuracy Score** - Response accuracy
4. **Completeness Score** - Answer completeness
5. **Sentiment** - User sentiment (positive/neutral/negative)
6. **Empathy Score** - Empathetic response measurement
7. **Response Time** - Average response time
8. **Resolution** - Issue resolution status
9. **Escalation Need** - Escalation requirement
10. **Fallback Frequency** - AI fallback phrase count
11. **Overall Score** - Weighted satisfaction score

## 🗄️ Database Models

- **Conversation**: Stores conversation metadata
- **Message**: Stores individual messages (user/AI)
- **ConversationAnalysis**: Stores all analysis results

## 🌐 Frontend

Access the web interface at:
- **Home**: `http://127.0.0.1:8000/`
- **Create**: `http://127.0.0.1:8000/create/`
- **Conversations**: `http://127.0.0.1:8000/conversations/`
- **Reports**: `http://127.0.0.1:8000/reports/`
- **Admin**: `http://127.0.0.1:8000/admin/`

## 📁 Project Structure

```
Post Conversation Analysis/
├── conversation_analysis/     # Main Django project
├── analysis/                  # Analysis app
│   ├── models.py             # Database models
│   ├── views.py              # API and frontend views
│   ├── analyzer.py           # Analysis logic
│   ├── cron.py               # Cron job function
│   ├── templates/            # HTML templates
│   └── static/               # CSS files
├── manage.py
├── requirements.txt
└── README.md
```

## 🛠️ Technology Stack

- Django 4.2.7
- Django REST Framework 3.14.0
- django-crontab 0.7.1
- SQLite/PostgreSQL
- HTML, CSS, JavaScript

## 📝 Requirements

- Python 3.8+
- Django 4.2.7
- Django REST Framework 3.14.0
- django-crontab 0.7.1
