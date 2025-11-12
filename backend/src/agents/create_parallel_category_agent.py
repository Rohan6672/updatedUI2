from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.genai import types as genai_types
from google.genai import types
from dotenv import load_dotenv

from src.config.research_config import config
from src.utils.callbacks import collect_research_sources_callback
from src.utils.setup_log import setup_logger
from src.utils.prompt_loader import get_category_agent_prompt
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import os, sys

# Load environment variables
load_dotenv()
logger = setup_logger()

categories = ["Tools & Brushes", "Skincare", "Mini Size", "Men", "Makeup", "Hair", "Gifts", "Fragrance", "Bath & Body"]
def create_parallel_category_agent():
    # Add the backend directory to the path so we can import from src
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, backend_dir)
    # Setup logger for the parallel category agent

    # Log agent creation
    logger.info("PARALLEL CATEGORY AGENT: Creating parallel category agent for trend discovery across categories")
    logger.info(f"PARALLEL CATEGORY AGENT: Total categories to process: {len(categories)}")
    logger.info(f"PARALLEL CATEGORY AGENT: Categories: {', '.join(categories)}")

    category_agents = []
    for i, category in enumerate(categories, 1):
        agent_name = f"{category.lower().replace(' & ', '_').replace(' ', '_')}_category_agent"
        output_key = f"{category.lower().replace(' & ', '_').replace(' ', '_')}_category_findings"
        
        logger.info(f"PARALLEL CATEGORY AGENT: Creating agent {i}/{len(categories)} - {agent_name} for category '{category}'")
        
        agent = LlmAgent(
            model=config.critic_model,
            name=agent_name,
            description=f"Identifies up-and-coming beauty and style trends in the {category} category using Google Search with source attribution and timestamps.",
            planner=BuiltInPlanner(
                thinking_config=genai_types.ThinkingConfig(include_thoughts=False)
            ),
            instruction=get_category_agent_prompt(category),
            tools=[google_search],
            output_key=output_key,
            generate_content_config=types.GenerateContentConfig(temperature=0.01),
            after_agent_callback=collect_research_sources_callback,
        )
        category_agents.append(agent)
        logger.info(f"PARALLEL CATEGORY AGENT: Successfully created {agent_name} with output_key: {output_key}")

    # Create a consolidation agent that will synthesize all category findings
    consolidation_agent = LlmAgent(
        model=config.critic_model,
        name="trend_consolidation_agent",
        description="Consolidates and synthesizes trend findings from all beauty category agents into a comprehensive final report.",
        planner=BuiltInPlanner(
            thinking_config=genai_types.ThinkingConfig(include_thoughts=False)
        ),
        instruction="""You are a senior beauty industry analyst tasked with creating a comprehensive trend report.

You will receive trend findings from 9 different beauty category agents. Your job is to:

1. **Synthesize Key Themes**: Identify overarching themes that span multiple categories
2. **Highlight Cross-Category Trends**: Note trends that appear across different beauty verticals
3. **Create Executive Summary**: Provide a concise overview of the most significant trends
4. **Organize by Impact**: Prioritize trends by their potential market impact and consumer adoption
5. **Provide Actionable Insights**: Include specific recommendations for beauty retailers and brands

**Output Format**: Create a well-structured report with:
- Executive Summary (2-3 paragraphs)
- Top 5 Cross-Category Trends
- Category-Specific Highlights
- Market Implications
- Recommendations

Use the individual category findings to create a cohesive, comprehensive beauty trend report for November 2025.""",
        tools=[],
        generate_content_config=types.GenerateContentConfig(temperature=0.1),
        after_agent_callback=collect_research_sources_callback,
    )

    parallel_category_agent = ParallelAgent(
        name="parallel_category_agent",
        description="A parallel agent that runs multiple category-specific agents to discover trends across different beauty categories, then consolidates the findings.",
        sub_agents=category_agents + [consolidation_agent],
    )
    
    logger.info(f"PARALLEL CATEGORY AGENT: Successfully created parallel agent with {len(category_agents)} research agents + 1 consolidation agent")
    logger.info(f"PARALLEL CATEGORY AGENT: Research agent names: {[agent.name for agent in category_agents]}")
    logger.info(f"PARALLEL CATEGORY AGENT: Consolidation agent: {consolidation_agent.name}")

    return parallel_category_agent


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    # Constants
    APP_NAME = "Sephora_Parallel_Category_Trends"
    USER_ID = "123"
    SESSION_ID = "123"
    
    # Create the parallel agent
    agent = create_parallel_category_agent()
    
    # Session and Runner
    session_service = InMemorySessionService()
    
    async def run_parallel_test():
        # Create session asynchronously
        await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
        
        runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

        # Agent Interaction
        def call_agent(query):
            content = types.Content(role='user', parts=[types.Part(text=query)])
            events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

            print(f"\n🚀 Starting parallel execution across {len(categories)} beauty categories...")
            print(f"📝 Query: {query}")
            print("⏳ Please wait while agents search for trends...\n")
            
            logger.info(f"PARALLEL EXECUTION: Starting query execution: '{query}'")
            logger.info(f"PARALLEL EXECUTION: Total agents executing: {len(categories)}")
            
            # Store results for each agent
            agent_results = {}
            final_response = ""
            
            for event in events:
                logger.info(f"PARALLEL EXECUTION: Received event type: {type(event).__name__}")
                
                # Log agent-specific events
                if hasattr(event, 'author') and event.author:
                    agent_name = event.author
                    logger.info(f"PARALLEL EXECUTION: Event from agent: {agent_name}")
                    logger.info(f"PARALLEL EXECUTION: Event details: {event}")
                    # Capture content from each agent
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts') and event.content.parts:
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    agent_text = part.text.strip()
                                    if agent_name not in agent_results:
                                        agent_results[agent_name] = []
                                    agent_results[agent_name].append(agent_text)
                                    logger.info(f"PARALLEL EXECUTION: Captured {len(agent_text)} characters from {agent_name}")
                
                #print(f"\n🔍 DEBUG EVENT: {event}\n")
                
                if event.is_final_response() and event.content:
                    final_answer = event.content.parts[0].text.strip()
                    final_response = final_answer
                    logger.info(f"PARALLEL EXECUTION: FINAL RESPONSE LENGTH: {len(final_answer)} characters")
            
            # Log detailed results for each agent
            logger.info("=" * 80)
            logger.info("PARALLEL EXECUTION: DETAILED AGENT RESULTS")
            logger.info("=" * 80)
            
            for agent_name, results in agent_results.items():
                logger.info(f"AGENT RESULTS: {agent_name}")
                logger.info(f"  - Number of responses: {len(results)}")
                total_chars = sum(len(result) for result in results)
                logger.info(f"  - Total characters: {total_chars}")
                logger.info(f"  - Results preview: {results[0][:200] if results else 'No results'}...")
                logger.info("-" * 40)
            
            logger.info(f"PARALLEL EXECUTION: SUMMARY")
            logger.info(f"  - Total agents that responded: {len(agent_results)}")
            logger.info(f"  - Expected agents: {len(categories)}")
            logger.info(f"  - Success rate: {len(agent_results)}/{len(categories)} ({len(agent_results)/len(categories)*100:.1f}%)")
            logger.info(f"  - Final response length: {len(final_response)} characters")
            logger.info("=" * 80)

        # Test with a beauty trend query
        call_agent("Find the top trending beauty products and makeup looks for November 2025")

    # Run the async function
    asyncio.run(run_parallel_test())