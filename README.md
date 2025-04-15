# LocalLift Platform

LocalLift is a comprehensive platform for managing local business presence and marketing.

## Project Structure

The project follows a modular structure organized by function:

```
/apps/
  /admin/         # Admin interfaces
  /client/        # Client-facing modules
/core/            # Core system components
/mcp/             # Model Context Protocol tools
/supabase/        # Database schema and migrations
```

## MCP Toolkit

The MCP (Model Context Protocol) toolkit provides code generation capabilities:

- `create_module.py` - Full module generator 
- `quick_generator.py` - Lightweight module generator
- `module_configs.json` - Configuration repository

### Using MCP Tools

Generate complete modules:
```bash
cd mcp
python create_module.py create client_gmb_post_tracker
```

Generate quick prototype modules:
```bash
python quick_generator.py generate admin_crm_manager
```

## Module Architecture

### GMB Post Tracker Module

The GMB Post Tracker module follows a clean separation of concerns:

```
/apps/client/
├── dashboard_post_tracker.py     → Controller logic
├── templates/post_tracker.html   → Frontend layout using Tailwind
├── static/post_tracker.js        → Badge animations, graph loading
├── api/post_tracker_api.py       → FastAPI routes to pull/post data
└── models/post_tracker_model.py  → Supabase schema & helper functions
```

#### Controller Layer (`dashboard_post_tracker.py`)
The controller coordinates between the data layer and presentation layer, handling business logic, data transformation, and session management.

#### Presentation Layer (`post_tracker.html` & `post_tracker.js`)
- HTML template using Tailwind CSS for responsive layout
- JavaScript for interactive features, badge animations and Chart.js integration

#### Data Access Layer (`post_tracker_api.py` & `post_tracker_model.py`)
- FastAPI routes for data operations
- Supabase schema definitions and database helper functions

## Key Features

### Google My Business Post Tracking
- Schedule and monitor social posts
- Track engagement metrics
- Monitor compliance with posting guidelines

### Gamification System
- Achievement badges for clients
- Progress tracking
- Visual feedback

### Dashboard Widgets
- Engagement trends visualization
- Post status tracking
- Compliance timeline

## Development

### Prerequisites
- Python 3.9+
- Node.js 16+
- Supabase account

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

2. Set up environment variables:
```bash
cp .env.template .env
# Edit .env with your configuration
```

3. Start the development server:
```bash
# Start backend API server
python -m uvicorn backend.api:app --reload

# Start Supabase local development
supabase start
```

## Using Module Generation

The MCP toolkit streamlines module development following platform standards:

1. Define module configuration in `module_configs.json`
2. Generate module scaffold using MCP tools
3. Implement specific business logic
4. Register module routes in the appropriate router
