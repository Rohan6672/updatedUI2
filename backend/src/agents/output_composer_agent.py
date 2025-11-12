from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import sys
import os
from src.models.session_models import SephoraTrendsReport

# Load environment variables
load_dotenv()

# Add the backend directory to the path so we can import from src
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from src.config.research_config import config
from src.utils.callbacks import collect_research_sources_callback, output_composer_callback
from src.utils.setup_log import setup_logger
from src.utils.prompt_loader import get_output_composer_agent_prompt

# Setup logger for the output composer agent
logger = setup_logger()

# Log agent creation
logger.info("OUTPUT COMPOSER AGENT: Creating output composer agent for data structuring")

output_composer_agent = LlmAgent(
    model=config.critic_model,
    name="output_composer_agent", 
    description="Composes the output of the trend research agent into a structured pydantic model with multiple trends.",
    instruction=get_output_composer_agent_prompt(),
    output_key="sephora_trends_report",
    output_schema=SephoraTrendsReport,
    after_agent_callback=output_composer_callback,
)