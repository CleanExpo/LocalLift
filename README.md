# LocalLift

Powering Visibility. Growing Communities.

A regional group CRM with gamification features, built with FastAPI and Supabase.

![LocalLift Logo](https://via.placeholder.com/1200x400?text=LocalLift+CRM)

## Overview

LocalLift is a modern CRM platform designed specifically for regional businesses and franchise groups, featuring gamification elements to boost engagement and performance. It integrates powerful CRM functionality with points, achievements, leaderboards, and a certification system to create a motivating work environment.

## Key Features

### 🏆 Gamification
- **Points System**: Award points for completing tasks, making referrals, and creating content
- **Achievements**: Unlock badges and rewards for reaching milestones
- **Levels**: Progress through levels as points accumulate

### 📊 Leaderboards
- **Global Rankings**: Compare performance across the entire organization
- **Regional Boards**: View rankings within specific geographical regions
- **Time-Based**: Daily, weekly, monthly, and all-time leaderboards

### 🎓 Certifications
- **Training Courses**: Structured learning paths with modules and materials
- **Progress Tracking**: Monitor completion rates and performance
- **Skill Validation**: Earn certifications to demonstrate expertise

### 💼 CRM Functionality
- **Client Management**: Track client information and engagement
- **Regional Organization**: Structure by geographic regions
- **Franchise Support**: Tools for franchise businesses

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL via Supabase
- **Authentication**: Supabase Auth
- **Frontend**: HTML with TailwindCSS
- **Tooling**: Node.js / npm for frontend build

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 14+
- npm

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/CleanExpo/LocalLift.git
   cd LocalLift
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

4. **Build CSS**
   ```bash
   npm run build:css
   ```

5. **Run the application**
   ```bash
   ./run.sh  # On Unix/Linux
   # or
   run.bat   # On Windows
   ```

6. **Access the web interface at http://localhost:8002**

For more detailed setup instructions, see [environment.md](environment.md).

## Project Structure

```
LocalLift/
├── core/                  # Core functionality
│   ├── config/            # Configuration
│   └── database/          # Database connections
├── frontend/              # Frontend source files
│   └── styles/            # TailwindCSS sources
├── public/                # Compiled assets
├── static/                # Static files
├── supabase/              # Supabase configuration
│   ├── migrations/        # Database migrations
│   └── seed.sql           # Seed data
├── templates/             # HTML templates
└── docs/                  # Documentation
```

## Documentation

- [Environment Setup](environment.md) - Detailed setup instructions
- [Cookbook](cookbook.md) - Code examples and common patterns
- [API Documentation](http://localhost:8002/docs) - Available when running the application

## Development

### Running in Development Mode

To run the application with auto-reload:

```bash
python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8002
```

### CSS Development

Watch for changes and rebuild CSS automatically:

```bash
npm run watch:css
```

### Database Migrations

Apply migrations to your database:

```bash
npm run migrate
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [Supabase](https://supabase.io/) for database and authentication
- [TailwindCSS](https://tailwindcss.com/) for styling
