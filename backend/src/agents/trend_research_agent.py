from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.genai import types as genai_types
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

import sys

# Add the backend directory to the path so we can import from src
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from src.config.research_config import config
from src.utils.callbacks import collect_research_sources_callback
from src.utils.setup_log import setup_logger
from src.utils.prompt_loader import get_trend_research_agent_prompt

# Setup logger for the trend research agent
logger = setup_logger()

# Log agent creation
logger.info("TREND RESEARCH AGENT: Creating trend research agent for beauty trend discovery")

trend_research_agent = LlmAgent(
    model=config.critic_model,
    name="sephora_trend_research_agent",
    description="Identifies up-and-coming beauty and style trends using Google Search with source attribution and timestamps.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=False)
    ),
    instruction=get_trend_research_agent_prompt(),
    # output_model=SephoraTrendsReport,
    tools=[google_search],
    output_key="sephora_trend_research_findings",
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
    after_agent_callback=collect_research_sources_callback,
)