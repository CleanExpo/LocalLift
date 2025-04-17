# LocalLift Development Environment

This document provides instructions for setting up and managing the development environment for the LocalLift project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+**: Required for running the FastAPI backend
- **Node.js 14+**: Required for package management and frontend tools
- **npm**: Node package manager for installing dependencies
- **PostgreSQL 15**: Required for local database development if not using Supabase locally
- **Git**: For version control

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/local-lift.git
   cd local-lift
   ```

2. **Set up a Python virtual environment**:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env with your actual configuration settings
   ```

## Supabase Setup

### Local Development with Supabase

1. **Install Supabase CLI** (if not already installed):
   ```bash
   npm install -g supabase
   ```

2. **Initialize Supabase project**:
   ```bash
   supabase init
   ```

3. **Start Supabase services**:
   ```bash
   npm run start:supabase
   ```

4. **Run migrations**:
   ```bash
   npm run migrate
   ```

### Using Remote Supabase Instance

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your API URL and keys from the Supabase dashboard
3. Update your `.env` file with these values

## Running the Application

### Backend

```bash
# Run the main API application
python main.py

# Run the simplified API
python mini_main.py

# Run the web application
python modified_web_app.py
```

### Frontend Development

1. **Build CSS**:
   ```bash
   npm run build:css
   ```

2. **Watch CSS for changes** (during development):
   ```bash
   npm run watch:css
   ```

## Project Structure

```
local-lift/
├── apps/                  # Role-specific applications
├── addons/                # Feature modules
├── core/                  # Core functionality
│   ├── auth/              # Authentication
│   ├── config/            # Configuration settings
│   └── database/          # Database connections
├── frontend/              # Frontend source files
│   └── styles/            # TailwindCSS source files
├── public/                # Compiled frontend assets
├── static/                # Static files
├── supabase/              # Supabase configuration
│   ├── migrations/        # Database migrations
│   └── seed.sql           # Seed data
├── templates/             # HTML templates
├── main.py                # Main application entry point
├── mini_main.py           # Simplified main for development
├── modified_web_app.py    # Web interface application
├── package.json           # Node.js package configuration
└── .env                   # Environment variables
```

## Database Migrations

When making changes to the database schema:

1. Create a new migration file in `supabase/migrations/` following the naming convention `00001_description.sql`
2. Add your SQL statements to create/modify tables
3. Run migrations with `npm run migrate`

## Testing

Run tests using pytest:

```bash
npm test
# or
pytest
```

## Common Issues and Troubleshooting

### Missing Environment Variables

If you encounter errors related to missing environment variables:
- Ensure you've copied the `.env.template` to `.env`
- Check that all required variables are set
- Restart your application after modifying environment variables

### Database Connection Issues

If you can't connect to the database:
- Check that Supabase is running with `npm run status:supabase`
- Verify your database connection parameters in `.env`
- Try restarting Supabase with `npm run stop:supabase && npm run start:supabase`

### CSS Not Building

If TailwindCSS isn't generating output:
- Make sure tailwindcss is installed correctly
- Check that source and output paths are correct in your npm scripts
- Try running the build command directly: `npx tailwindcss -i ./frontend/styles/tailwind.css -o ./public/style.css`

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and develop your feature
3. **Run tests** to ensure your changes don't break existing functionality
4. **Commit your changes** with clear, descriptive commit messages
5. **Push your branch** and create a pull request

## Deployment

### Production Environment Setup

For production deployment:

1. Set `DEBUG=False` in your environment variables
2. Set `ENVIRONMENT=production`
3. Use a production-ready database
4. Generate a secure `SECRET_KEY`
5. Configure CORS settings appropriately

### Docker Deployment (Optional)

A Dockerfile is provided for containerizing the application:

```bash
# Build the Docker image
docker build -t locallift .

# Run the container
docker run -p 8000:8000 --env-file .env locallift
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.io/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
