# Mobile AI Django - Multi-language AI Chatbot System

🤖 **A comprehensive Django-based AI chatbot system with Tamil and English support, featuring auto fine-tuning, web search integration, and mobile deployment capabilities.**

## 🌟 Features

### 🗣️ Multi-language Support
- **Tamil and English** conversation support
- Automatic language detection
- Real-time translation capabilities
- Voice input recognition

### 🧠 AI Integration
- Multiple AI model support (OpenAI GPT, Hugging Face, Local models)
- Automatic model selection and fallback
- **Auto fine-tuning** based on user ratings
- Confidence scoring and performance metrics

### 🔍 Web Search Integration
- **DuckDuckGo API** integration for real-time information
- Automatic low-rating query improvement
- Search result caching and optimization

### 📊 Analytics & Monitoring
- Real-time performance dashboards
- **Chart.js** visualizations
- Daily/weekly metrics tracking
- Rating-based improvement suggestions

### 📱 Mobile-First Design
- **Termux/Android** compatible
- **Raspberry Pi Zero 2W** deployment
- Responsive web interface
- Touch-friendly interactions

### ⚡ Background Processing
- **Celery** task queue integration
- Daily metrics updates
- Weekly auto fine-tuning
- Automated data cleanup

## 🛠️ Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: SQLite (mobile-friendly)
- **Cache/Queue**: Redis, Celery
- **AI/ML**: OpenAI API, Hugging Face Transformers
- **Search**: DuckDuckGo Search API
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Charts**: Chart.js
- **Translation**: Google Translate API

## 🚀 Quick Start

### Mobile/Termux Installation
```bash
# Install Termux from F-Droid or GitHub
pkg update && pkg upgrade -y
pkg install python git redis clang

# Clone and setup
git clone <repository-url>
cd mobile_ai_django
python setup.py
```

### Raspberry Pi Setup
```bash
# Install dependencies
sudo apt install python3-pip python3-venv git redis-server

# Setup project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### Run Development Server
```bash
# Start Redis
redis-server &

# Run Django
python manage.py runserver 0.0.0.0:8000

# Start Celery (in separate terminals)
celery -A mobile_ai_django worker --loglevel=info
celery -A mobile_ai_django beat --loglevel=info
```

## 📋 Core Components

### 1. AI Chat System
- **Multi-model Support**: OpenAI GPT, Hugging Face, Local models
- **Context Awareness**: Session-based conversation history
- **Topic Classification**: Automatic categorization (garments, share market, AI tools, programming, etc.)
- **Response Rating**: 5-star rating system for continuous improvement

### 2. Auto Fine-tuning Engine
- **Performance Monitoring**: Daily rating analysis
- **Threshold-based Triggering**: Auto fine-tune when ratings drop below 70%
- **Training Data Generation**: High-rated conversations become training samples
- **Model Improvement Tracking**: Before/after accuracy comparison

### 3. Web Search Integration
- **Real-time Search**: DuckDuckGo API integration
- **Low-rating Improvement**: Daily search for poorly-rated queries
- **Result Caching**: Efficient storage and retrieval
- **Multi-language Support**: Tamil and English search capabilities

### 4. Analytics Dashboard
- **Real-time Metrics**: Message counts, ratings, response times
- **Visual Charts**: Line charts, bar charts, pie charts, doughnuts
- **Performance Tracking**: Success rates, model performance
- **Improvement Insights**: Actionable recommendations

## 🗃️ Database Schema

### Core Models
- **ChatSession**: User conversation sessions
- **ChatMessage**: Individual messages with metadata
- **MessageRating**: User feedback and ratings
- **WebSearchQuery**: Search queries and results
- **AIModelConfig**: AI model configurations
- **FineTuningJob**: Auto fine-tuning job tracking
- **DailyMetrics**: Performance analytics

## 🔧 API Endpoints

### Chat API
```
POST /api/chat/          # Send message, get AI response
GET  /api/history/       # Get chat history
POST /api/rate/          # Rate AI response
```

### Search API
```
GET  /api/search/        # Web search with DuckDuckGo
POST /api/translate/     # Text translation
```

### Analytics API
```
GET  /api/metrics/       # Performance metrics and charts
GET  /export/history/    # Export chat history as CSV
```

## 🎯 Topic Support

The system specializes in multiple domains:
- **Garments & Textiles**
- **Share Market & Trading**
- **AI Tools & Technologies**
- **Python Programming**
- **Java Development**
- **HTML/Web Development**
- **Embedded Systems**
- **Raspberry Pi Projects**
- **Linux Administration**

## 📱 Mobile Deployment

### Termux (Android)
- Full Django server on Android
- Redis for background tasks
- Mobile-optimized interface
- Voice input support

### Raspberry Pi Zero 2W
- Lightweight deployment
- Nginx reverse proxy
- Systemd service management
- SSL certificate support

## 🔄 Auto Fine-tuning Process

1. **Daily Rating Analysis**: Check average ratings
2. **Threshold Detection**: Trigger if rating < 0.7
3. **Training Data Preparation**: Collect high-rated (4-5 stars) conversations
4. **Model Fine-tuning**: Improve model with quality data
5. **Performance Validation**: Compare before/after accuracy
6. **Deployment**: Update active model configuration

## 📊 Monitoring & Analytics

### Daily Metrics
- Message volume and language distribution
- Average response time and success rates
- User satisfaction ratings
- Topic popularity analysis

### Performance Dashboards
- Real-time charts with Chart.js
- Mobile-responsive visualizations
- Exportable reports
- Improvement recommendations

## 🛡️ Security Features

- CSRF protection
- SQL injection prevention
- XSS filtering
- Secure file uploads
- API rate limiting
- Session management

## 🌐 Internationalization

- Tamil (ta) and English (en) support
- Unicode text handling
- Right-to-left text support
- Localized date/time formats
- Translation capabilities

## 🔧 Customization

### Adding New Topics
1. Update `TOPIC_CHOICES` in models.py
2. Add topic keywords in utils.py
3. Create topic-specific responses
4. Update frontend topic selector

### New AI Models
1. Create model configuration in admin
2. Implement model interface in utils.py
3. Add to model selection logic
4. Configure API credentials

### Custom Fine-tuning
1. Adjust thresholds in settings.py
2. Modify training data selection
3. Customize model parameters
4. Update evaluation metrics

## 📚 Documentation

- [Installation Guide](DEPLOYMENT.md)
- [API Documentation](docs/api.md)
- [Configuration Reference](docs/configuration.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the robust framework
- OpenAI for GPT API access
- Hugging Face for transformer models
- DuckDuckGo for search API
- Chart.js for beautiful visualizations
- Tamil computing community for language support

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting guide
- Review the documentation

---

**Built with ❤️ for mobile-first AI experiences**

*Supporting Tamil computing and multilingual AI accessibility*
