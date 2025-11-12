# Sephora Trends API

A FastAPI-based backend for beauty trends research and analysis using Google ADK agents.

## Features

- **AI-Powered Trend Research**: Uses Google ADK agents to discover emerging beauty trends
- **Multi-Category Analysis**: Finds trends across Hair, Skincare, and Makeup categories
- **Comprehensive Logging**: End-to-end logging with detailed step tracking
- **Session-Based File Output**: Organized file storage for each session
- **Real-time Data**: Searches across social media platforms and beauty publications
- **Structured Output**: Returns data in a format ready for frontend consumption

## Architecture

### Agent System
- **Trend Research Agent**: Searches for beauty trends across multiple sources
- **Output Composer Agent**: Structures research data into standardized format
- **Coordinator Agent**: Orchestrates the multi-agent workflow

### Data Sources
- Social Media: TikTok, Instagram, YouTube, Reddit, Pinterest
- Beauty Publications: Vogue, Allure, Elle, Byrdie, Cosmopolitan
- Search Platforms: Google Search with targeted queries

## Setup

### Prerequisites

- Python 3.10+
- Poetry (for dependency management)
- Google Cloud Project with Vertex AI enabled
- Google Search API credentials

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file in the backend directory with your environment variables:
```env
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=
GOOGLE_GENAI_USE_VERTEXAI=True
```

3. Configure the application by updating `src/config/config.yaml`:
```yaml
logging:
  logger_path: "src/logs/app_logs.log"

output_folder:
  OUTPUT_DIR: "src/data/outputs"

llm_config:
  critic_model: "gemini-2.5-pro"
  worker_model: "gemini-2.5-flash"
```

4. Start the development server:
```bash
poetry run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

## Usage

### API Endpoints

#### POST `/analysis/`
Discover beauty trends based on a user query.

**Request Body:**
```json
{
  "session_id": "123",
  "user_id": "user1",
  "trend_query": "What are the latest beauty trends?",
  "created_at": "2025-11-06T12:00:00Z"
}
```

**Response:**
```json
{
  "reportSummary": "Comprehensive summary of beauty trends...",
  "trends": {
    "makeupTrends": [...],
    "skincareTrends": [...],
    "hairTrends": [...]
  },
  "discoveryDate": "2025-11-06",
  "totalTrendsFound": 9
}
```

#### GET `/analysis/test`
Test endpoint to verify model structure.

#### GET `/`
Health check endpoint.

## File Output System

The system automatically saves detailed outputs for each session in organized folders:

### Directory Structure
```
src/data/outputs/
├── session_123/
│   ├── trend_research_agent_user1_20251106_184500.json
│   ├── trend_research_agent_with_citations_user1_20251106_184500.json
│   ├── output_composer_agent_user1_20251106_184501.json
│   ├── session_state_user1_20251106_184501.json
│   ├── final_response_user1_20251106_184502.json
│   └── session_summary.json
└── session_456/
    └── (similar files for different session)
```

### File Types
- **trend_research_agent**: Raw research findings without citations
- **trend_research_agent_with_citations**: Research findings with source citations
- **output_composer_agent**: Structured data from the composer agent
- **session_state**: Complete session state with all agent outputs
- **final_response**: Final API response sent to client
- **session_summary**: Overview of all files created for the session

## Logging System

Comprehensive logging tracks the entire request flow:

### Log Levels
- **Application Startup/Shutdown**: Server lifecycle events
- **Request Processing**: Incoming requests and routing
- **Agent Execution**: Individual agent processing steps
- **Data Transformation**: Converting between formats
- **File Operations**: Output file creation and organization
- **Error Handling**: Detailed error information

### Log Location
Logs are written to `src/logs/app_logs.log` with timestamp and structured format.

### Log Categories
```
=== APPLICATION STARTUP ===
=== TREND DISCOVERY REQUEST RECEIVED ===
=== STARTING AGENT CONVERSATION ===
=== AGENT CONVERSATION COMPLETED ===
=== PROCESSING TRENDS DATA ===
=== RESPONSE READY ===
=== RETURNING TRENDS DATA TO CLIENT ===
```

## Setup

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file in the backend directory with your environment variables.

3. Start the development server:
```bash
poetry run start
```

Or alternatively:
```bash
poetry run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

## Development

### Code Formatting

Format code with Black:
```bash
poetry run black src/
```

Sort imports with isort:
```bash
poetry run isort src/
```

### Linting

Run flake8:
```bash
poetry run flake8 src/
```

Run mypy type checking:
```bash
poetry run mypy src/
```

### Testing

Run tests:
```bash
poetry run pytest
```

### Monitoring and Debugging

1. **Log Monitoring**: Watch real-time logs during development:
```bash
tail -f src/logs/app_logs.log
```

2. **Session Analysis**: Review session outputs in `src/data/outputs/session_{id}/`

3. **Agent Debugging**: Check individual agent outputs for troubleshooting

## Project Structure

```
backend/
├── src/
│   ├── app.py                  # FastAPI application
│   ├── agents/                 # Google ADK agents
│   │   ├── coordinator_agent.py
│   │   ├── trend_research_agent.py
│   │   └── output_composer_agent.py
│   ├── config/                 # Configuration files
│   │   ├── config.yaml         # Main configuration
│   │   ├── load_config.py      # Configuration loader
│   │   └── research_config.py  # Agent configuration
│   ├── data/                   # Data storage
│   │   └── outputs/            # Session-based output files
│   ├── logs/                   # Application logs
│   │   └── app_logs.log        # Main log file
│   ├── models/                 # Pydantic models
│   │   └── session_models.py   # Data models
│   ├── routers/                # API routes
│   │   └── discover_trends.py  # Trends API endpoints
│   └── utils/                  # Utility functions
│       ├── setup_log.py        # Logging setup
│       ├── service.py          # Agent service layer
│       ├── file_output.py      # File output utilities
│       └── callbacks.py        # Agent callbacks
├── pyproject.toml              # Poetry configuration
└── README.md                   # This file
```

## Configuration

### Environment Variables
Required environment variables in `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GOOGLE_SEARCH_API_KEY=your_search_api_key
GOOGLE_SEARCH_CX=your_search_engine_id
```

### YAML Configuration
Key configuration options in `src/config/config.yaml`:
```yaml
logging:
  logger_path: "src/logs/app_logs.log"
  log_level: "info"

output_folder:
  OUTPUT_DIR: "src/data/outputs"

llm_config:
  critic_model: "gemini-2.5-pro"
  worker_model: "gemini-2.5-flash"
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account
2. **Search API Limits**: Check Google Search API quotas and usage
3. **Model Access**: Verify Vertex AI model access in your Google Cloud project
4. **File Permissions**: Ensure write permissions for logs and outputs directories

### Debug Mode
Enable detailed logging by setting log level to "debug" in config.yaml:
```yaml
logging:
  log_level: "debug"
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## Performance Considerations

- **Session Management**: Each session creates multiple output files
- **Search Rate Limits**: Google Search API has daily quotas
- **Model Costs**: Vertex AI usage is billable per token
- **File Storage**: Monitor disk usage for output files

## License

This project is proprietary to Sephora.