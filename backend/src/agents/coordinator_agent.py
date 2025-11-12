from google.adk.agents import SequentialAgent
from src.agents.trend_research_agent import trend_research_agent
from src.agents.output_composer_agent import output_composer_agent
from src.utils.setup_log import setup_logger

# Setup logger for the coordinator agent
logger = setup_logger()

# Log the creation of the root agent
logger.info("COORDINATOR: Creating Sephora Trend Agent with sequential execution")
logger.info("   Agent 1: sephora_trend_research_agent (trend discovery)")
logger.info("   Agent 2: output_composer_agent (data structuring)")

root_agent = SequentialAgent(
    name="sephora_trend_agent",
    description="A sequential agent that uses the trend research agent to find trends and the output composer agent to compose the output into a pydantic model.",
    sub_agents=[trend_research_agent, output_composer_agent],
)