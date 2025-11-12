import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import google.auth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# AUTHENTICATION CONFIGURATION
# =============================================================================

# Determine authentication method
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate authentication setup
if not USE_VERTEX_AI and not GOOGLE_API_KEY:
    raise ValueError(
        "When GOOGLE_GENAI_USE_VERTEXAI=False, GOOGLE_API_KEY must be provided in environment variables"
    )

if USE_VERTEX_AI:
    try:
        _, project_id = google.auth.default()
        os.environ.setdefault(
            "GOOGLE_CLOUD_PROJECT", str(project_id) if project_id else "unknown"
        )
        print(f"✅ Using Vertex AI authentication with project: {project_id}")
    except Exception as e:
        print(f"⚠️  Warning: Could not get default credentials: {e}")
        print("   Please run: gcloud auth application-default login")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "unknown")
else:
    print("✅ Using Google API Key authentication")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "api-key-mode")

# Set default environment variables for Vertex AI
if USE_VERTEX_AI:
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
else:
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
    
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", str(USE_VERTEX_AI))

# =============================================================================
# RESEARCH CONFIGURATION
# =============================================================================


@dataclass
class ResearchConfiguration:
    """Configuration for research-related models and parameters.

    Attributes:
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
        current_date (str): Current date in ISO format.
        use_vertex_ai (bool): Whether to use Vertex AI authentication.
        google_api_key (Optional[str]): Google API key for non-Vertex AI mode.
        project_id (str): Google Cloud project ID.
    """

    # Use appropriate model names based on authentication method
    critic_model: str = "gemini-1.5-pro" if USE_VERTEX_AI else "gemini-2.5-pro"
    worker_model: str = "gemini-1.5-flash" if USE_VERTEX_AI else "gemini-2.5-flash"
    max_search_iterations: int = 2
    current_date: str = datetime.now().strftime("%Y-%m-%d")
    use_vertex_ai: bool = USE_VERTEX_AI
    google_api_key: Optional[str] = GOOGLE_API_KEY
    project_id: str = str(project_id) if project_id else "unknown"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.use_vertex_ai and not self.google_api_key:
            raise ValueError(
                "Google API key is required when not using Vertex AI authentication"
            )


config = ResearchConfiguration()

# =============================================================================
# CONFIGURATION SUMMARY
# =============================================================================


def print_config_summary():
    """Print a summary of the current configuration."""
    print("\n" + "=" * 60)
    print("🔧 Sephora Trend Research Platform Configuration")
    print("=" * 60)
    print(
        f"📊 Authentication Method: {'Vertex AI' if config.use_vertex_ai else 'API Key'}"
    )
    print(f"🏢 Project ID: {config.project_id}")
    print(f"🤖 Critic Model: {config.critic_model}")
    print(f"⚙️  Worker Model: {config.worker_model}")
    print(f"🔄 Max Search Iterations: {config.max_search_iterations}")
    print(f"📅 Current Date: {config.current_date}")
    print(f"🌐 Location: {os.getenv('GOOGLE_CLOUD_LOCATION')}")
    print("=" * 60 + "\n")


# Print configuration summary on import
if __name__ != "__main__":
    print_config_summary()