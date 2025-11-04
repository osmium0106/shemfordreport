# 📊 Student Report System

A comprehensive Flask-based web application for generating detailed academic performance reports with multi-subject support, interactive charts, and topic-wise analytics.

## ✨ Features

- **Multi-Subject Support**: Separate tabs for Maths, Science, and other subjects
- **Interactive Charts**: Progress tracking with Chart.js visualizations
- **Google Sheets Integration**: Direct data import from Google Sheets
- **Responsive Design**: Bootstrap 5 with modern UI/UX
- **Performance Analytics**: Topic-wise scoring and time analysis
- **Print-Friendly Reports**: Professional PDF-ready layouts
- **Class Management**: Support for multiple classes and students

## 🚀 Quick Start

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/student-report-system.git
   cd student-report-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app_simple.py
   ```

4. **Open in browser**: http://localhost:5000

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guides including:
- 🌐 **AWS EC2** with domain setup
- 💰 **Hostinger** shared hosting
- ⚡ **Heroku** quick deployment
- � **Docker** containerization

## 🛠️ Technology Stack

- **Backend**: Flask 2.3.3, Python 3.11+
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Data**: Google Sheets API, gspread
- **Deployment**: Docker, Gunicorn, Nginx
- **Template Engine**: Jinja2

## 📁 Project Structure

```
student-report-system/
├── app_simple.py              # Main Flask application
├── templates/
│   └── topic_report.html      # Report template
├── static/
│   └── css/
│       └── style.css          # Custom styles
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Multi-container setup
├── deploy-aws.sh             # AWS deployment script
├── deploy-hostinger.sh       # Hostinger deployment script
├── .env.example              # Environment template
└── DEPLOYMENT.md             # Deployment guide
```

## 🔧 Configuration

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit configuration**:
   ```bash
   # Required settings
   FLASK_ENV=production
   SECRET_KEY=your-secret-key-here
   DOMAIN=your-domain.com
   ```

## 📊 Usage

### Adding Google Sheets Data

1. **Prepare your Google Sheet** with the following structure:
   - Column A: Student Name
   - Column B: Roll Number  
   - Column C: Class
   - Subsequent columns: Topic scores, time data, etc.

2. **Configure sheet URLs** in `app_simple.py`:
   ```python
   sheets_connector.add_class_sheet_url('1B', 'your_google_sheet_url')
   ```

### Accessing Reports

- **Individual Reports**: `/report/{class}/{student_number}`
- **Class Overview**: `/class/{class_name}`
- **Home Page**: `/` (search interface)

## 🎨 Features Showcase

### Multi-Subject Tabs
- Clean separation between subjects (Maths, Science)
- Subject-specific performance analytics
- Individual progress charts per subject

### Interactive Charts
- Topic-wise progress visualization
- Performance trend analysis
- Color-coded performance indicators

### Professional Reports
- Print-ready layouts
- Comprehensive performance analytics
- Topic-wise breakdowns and recommendations

## 🚀 Deployment Options

### 1. AWS EC2 (Recommended)
```bash
# Run automated deployment script
chmod +x deploy-aws.sh
./deploy-aws.sh
```

**Cost**: $10-50/month | **Best for**: Scalability & control

### 2. Hostinger Shared Hosting
```bash
# Upload and run deployment script
chmod +x deploy-hostinger.sh
./deploy-hostinger.sh
```

**Cost**: $3-15/month | **Best for**: Budget-conscious deployment
   ```

4. **Open Browser**: Navigate to `http://localhost:5000`

## Google Sheets Setup

### Sheet Structure Required:
- **Row 1**: `Class | 1B | (empty cells...)`
- **Row 2**: `Roll No. | Name | Topic 1 | | Topic 2 | | Topic 3 | ...`
- **Row 3**: `| | Time | Marks | Time | Marks | Time | Marks | ...`
- **Row 4+**: Student data

### Publishing Your Sheets:
1. Open your Google Sheet
2. Go to **File → Share → Publish to web**
3. Choose **Entire Document** and **CSV** format
4. Copy the published URL
5. Add it to the application using `sheets_connector.add_class_sheet_url()`

## File Structure

```
├── app_simple.py          # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Main selection page
│   ├── topic_report.html # Student report template
│   └── error.html        # Error page template
└── static/
    ├── css/style.css     # Custom styles
    └── js/main.js        # Frontend JavaScript
```

## Adding New Classes

```python
# Add this to app_simple.py after the sheets_connector initialization
sheets_connector.add_class_sheet_url('CLASS_NAME', 'PUBLISHED_SHEET_URL')
```

Example:
```python
sheets_connector.add_class_sheet_url('1B', 'https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?output=csv')
sheets_connector.add_class_sheet_url('1C', 'https://docs.google.com/spreadsheets/d/e/2PACX-.../pub?output=csv')
```

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Data Source**: Google Sheets (Published CSV)
- **Templating**: Jinja2

## Ready for Your Sheet URLs! 🚀

The application is now clean and ready for you to add your individual class sheet URLs.
