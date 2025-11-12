from google.genai import types

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from src.agents.coordinator_agent import root_agent
from src.utils.setup_log import setup_logger
from src.utils.file_output import save_agent_output, save_session_state, save_final_response
from src.config.load_config import load_config

logger = setup_logger()
config_data = load_config()

APP_NAME = "sephora_trend_agent"
# USER_ID = "user1"
# SESSION_ID = str(uuid.uuid4())

# Create session service and session
session_service = InMemorySessionService()

# Create runner with the session service
runner = Runner(
    agent=root_agent, session_service=session_service, app_name=APP_NAME
)


async def call_agent_async(query: str, runner, user_id, session_id):
        """Sends a query to the agent and prints the final response."""
        logger.info("=== AGENT SERVICE CALL STARTED ===")
        logger.info(f"User Query: {query}")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Session ID: {session_id}")
        
        logger.info("=== CREATING SESSION ===")
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        logger.info(f"Session created: App='{APP_NAME}', User='{user_id}', Session='{session_id}'")

        # Prepare the user's message in ADK format
        logger.info("=== PREPARING USER MESSAGE ===")
        content = types.Content(role="user", parts=[types.Part(text=query)])
        logger.info("User message prepared in ADK format")

        # Key Concept: run_async executes the agent logic and yields Events.
        # We iterate through events to find the final answer.
        logger.info("=== STARTING AGENT EXECUTION ===")
        event_count = 0
        current_agent = None
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Track agent transitions and log agent-specific information
            event_count += 1
            
            # Log agent transition when author changes
            if current_agent != event.author:
                current_agent = event.author
                logger.info(f"AGENT TRANSITION: Now executing '{current_agent}' agent")
                logger.info(f"   └─ Agent Description: {getattr(event, 'description', 'N/A')}")
            
            # Enhanced event logging with agent identification
            logger.info(f"[Event #{event_count}] Agent: {event.author} | Type: {type(event).__name__} | Final: {event.is_final_response()}")
            
            # Log additional details for specific event types
            if hasattr(event, 'content') and event.content:
                logger.info(f"   └─ Content Preview: {str(event.content)[:100]}{'...' if len(str(event.content)) > 100 else ''}")
            
            # Log when an agent starts/completes
            event_type_name = type(event).__name__
            if 'Start' in event_type_name:
                logger.info(f"AGENT START: '{event.author}' agent beginning execution")
            elif 'Complete' in event_type_name or event.is_final_response():
                logger.info(f"AGENT COMPLETE: '{event.author}' agent finished execution")

            # Key Concept: Only check for final response from the root agent
            if event.is_final_response() and event.author == "output_composer_agent":
                logger.info("=== FINAL RESPONSE DETECTED ===")
                logger.info(f"Final response from: {event.author}")
                
                # Get the final session state to extract the structured output
                logger.info("=== RETRIEVING SESSION STATE ===")
                final_session = await session_service.get_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=session_id,
                )
                logger.info(f"Session retrieved, has state: {final_session and final_session.state is not None}")

                # Check for the final output in session state
                final_output = None
                if final_session and final_session.state:
                    logger.info("=== EXTRACTING FINAL OUTPUT ===")
                    logger.info(f"Session state keys: {list(final_session.state.keys())}")
                    
                    # Get output directory from config
                    output_dir = config_data.get("output_folder", {}).get("OUTPUT_DIR", "src/data/outputs")
                    
                    # Save complete session state to file
                    session_file = save_session_state(
                        final_session.state, 
                        session_id, 
                        user_id, 
                        output_dir
                    )
                    
                    # Extract and save individual agent outputs
                    research_findings = final_session.state.get("sephora_trend_research_findings")
                    if research_findings:
                        research_file = save_agent_output(
                            "trend_research_agent", 
                            research_findings, 
                            session_id, 
                            user_id, 
                            output_dir
                        )
                        logger.info(f"Research findings saved to: {research_file}")
                    
                    research_with_citations = final_session.state.get("sephora_trend_research_findings_with_citations")
                    if research_with_citations:
                        citations_file = save_agent_output(
                            "trend_research_agent_with_citations", 
                            research_with_citations, 
                            session_id, 
                            user_id, 
                            output_dir
                        )
                        logger.info(f"Research with citations saved to: {citations_file}")
                    
                    # Check for the final output from the card composer
                    final_output = final_session.state.get("sephora_trends_report")
                    if final_output:
                        output_file = save_agent_output(
                            "output_composer_agent", 
                            final_output, 
                            session_id, 
                            user_id, 
                            output_dir
                        )
                        logger.info(f"Final output saved to: {output_file}")
                    
                    logger.info(f"Final output extracted: {type(final_output)}")
                    logger.info(f"Final output keys: {final_output.keys() if isinstance(final_output, dict) else 'Not a dict'}")

                    logger.info("=== FINAL OUTPUT ===")
                    logger.debug(f"Final output: {final_output}")

                    citations = final_session.state.get(
                        "sephora_trend_research_findings_with_citations"
                    )
                    logger.info("=== RESEARCH FINDINGS WITH CITATIONS ===")
                    logger.debug(f"Citations: {citations}")
                    
                    research_without_citations = final_session.state.get(
                        "sephora_trend_research_findings"
                    )
                    logger.info("=== RESEARCH FINDINGS (NO CITATIONS) ===")
                    logger.debug(f"Research without citations: {research_without_citations}")
                    
                logger.info("=== AGENT SERVICE CALL COMPLETED ===")
                return final_output



async def run_conversation(request):
    logger.info("=== RUN CONVERSATION STARTED ===")
    logger.info(f"Processing request for user: {request.user_id}")
    logger.info(f"Session: {request.session_id}")
    logger.info(f"Query: '{request.trend_query}'")
    
    trends = await call_agent_async(
        query=request.trend_query,
        runner=runner,
        user_id=request.user_id,
        session_id=request.session_id,
    )
    
    logger.info("=== RUN CONVERSATION COMPLETED ===")
    logger.info(f"Returned data type: {type(trends)}")
    logger.info(f"Returned data keys: {trends.keys() if isinstance(trends, dict) else 'Not a dict'}")
    
    return trends