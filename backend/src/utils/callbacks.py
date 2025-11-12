import re
import logging
from difflib import SequenceMatcher

from google.adk.agents.callback_context import CallbackContext
from google.genai import types as genai_types
from src.utils.setup_log import setup_logger

# Setup logger for callbacks
logger = setup_logger()


def add_citations_to_report(report: str, sources: dict) -> str:
    """Add citation tags to the report based on supported claims from sources.

    Args:
        report: The research report text
        sources: Dictionary of sources with supported claims

    Returns:
        Report with citation tags added
    """
    # Create a list of all supported claims with their source IDs
    claims_with_sources = []
    for source_id, source_info in sources.items():
        for claim in source_info.get("supported_claims", []):
            text_segment = claim.get("text_segment", "").strip()
            if text_segment:
                # Clean up the text segment for matching
                clean_text = re.sub(
                    r"\*+([^*]+)\*+", r"\1", text_segment
                )  # Remove markdown bold
                clean_text = re.sub(r"\s+", " ", clean_text)  # Normalize whitespace
                # Only include claims that are substantial (more than 30 characters)
                if len(clean_text) > 30:
                    claims_with_sources.append((clean_text, source_id))

    # Sort by length (longest first) to avoid partial matches
    claims_with_sources.sort(key=lambda x: len(x[0]), reverse=True)

    result = report
    used_positions = set()

    for claim_text, source_id in claims_with_sources:
        if not claim_text:
            continue

        # Try exact matching first
        start_pos = 0
        while True:
            # Find the next occurrence of the claim text
            pos = result.lower().find(claim_text.lower(), start_pos)
            if pos == -1:
                break

            # Check if this position is already used
            if any(start <= pos < start + len(claim_text) for start in used_positions):
                start_pos = pos + 1
                continue

            # Check if it's at a word boundary
            is_word_boundary = (
                pos == 0
                or result[pos - 1] in " \n\t.,;:!?-"
                or result[pos - 1] in "()[]{}"
            )

            if is_word_boundary:
                # Add citation tag after the matched text
                citation_tag = f' <cite source="{source_id}"/>'
                result = (
                    result[: pos + len(claim_text)]
                    + citation_tag
                    + result[pos + len(claim_text) :]
                )

                # Mark this position as used
                used_positions.add(pos)
                used_positions.add(pos + len(claim_text) + len(citation_tag))
                break
            else:
                start_pos = pos + 1

    return result


def collect_research_sources_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """Collects and organizes web-based research sources and their supported claims from agent events.

    This function processes the agent's `session.events` to extract web source details (URLs,
    titles, domains from `grounding_chunks`) and associated text segments with confidence scores
    (from `grounding_supports`). The aggregated source information and a mapping of URLs to short
    IDs are cumulatively stored in `callback_context.state`.

    Args:
        callback_context (CallbackContext): The context object providing access to the agent's
            session events and persistent state.
    """
    # Log agent callback execution
    agent_name = getattr(callback_context._invocation_context, 'agent_name', 'Unknown Agent')
    logger.info(f"AGENT CALLBACK: Executing research sources callback for '{agent_name}'")
    logger.info(f"RESEARCH SOURCES CALLBACK: Collecting research sources from agent events '{callback_context.state}'")

    session = callback_context._invocation_context.session
    url_to_short_id = callback_context.state.get("url_to_short_id", {})
    sources = callback_context.state.get("sources", {})
    id_counter = len(url_to_short_id) + 1
    for event in session.events:
        if not (event.grounding_metadata and event.grounding_metadata.grounding_chunks):
            continue
        chunks_info = {}
        for idx, chunk in enumerate(event.grounding_metadata.grounding_chunks):
            if not chunk.web:
                continue
            url = chunk.web.uri
            title = (
                chunk.web.title
                if chunk.web.title != chunk.web.domain
                else chunk.web.domain
            )
            if url not in url_to_short_id:
                short_id = f"src-{id_counter}"
                url_to_short_id[url] = short_id
                sources[short_id] = {
                    "short_id": short_id,
                    "title": title,
                    "url": url,
                    "domain": chunk.web.domain,
                    "supported_claims": [],
                }
                id_counter += 1
            chunks_info[idx] = url_to_short_id[url]
        if event.grounding_metadata.grounding_supports:
            for support in event.grounding_metadata.grounding_supports:
                confidence_scores = support.confidence_scores or []
                chunk_indices = support.grounding_chunk_indices or []
                for i, chunk_idx in enumerate(chunk_indices):
                    if chunk_idx in chunks_info:
                        short_id = chunks_info[chunk_idx]
                        confidence = (
                            confidence_scores[i] if i < len(confidence_scores) else 0.5
                        )
                        text_segment = support.segment.text if support.segment else ""
                        sources[short_id]["supported_claims"].append(
                            {
                                "text_segment": text_segment,
                                "confidence": confidence,
                            }
                        )
    callback_context.state["url_to_short_id"] = url_to_short_id
    callback_context.state["sources"] = sources
    research_report = callback_context.state.get("sephora_trend_research_findings", "")

    if not research_report:
        logging.warning("No research report found in callback context")
        return genai_types.Content(parts=[genai_types.Part(text="")])

    # First, add citation tags to the report based on supported claims
    report_with_citations = add_citations_to_report(research_report, sources)

    def tag_replacer(match: re.Match) -> str:
        short_id = match.group(1)
        if not (source_info := sources.get(short_id)):
            logging.warning(f"Invalid citation tag found and removed: {match.group(0)}")
            return ""
        display_text = source_info.get("title", source_info.get("domain", short_id))
        return f" [{display_text}]({source_info['url']})"

    processed_report = re.sub(
        r'<cite\s+source\s*=\s*["\']?\s*(src-\d+)\s*["\']?\s*/>',
        tag_replacer,
        report_with_citations,
    )
    processed_report = re.sub(r"\s+([.,;:])", r"\1", processed_report)
    callback_context.state["sephora_trend_research_findings_with_citations"] = (
        processed_report
    )

    logger.info("RESEARCH SOURCES CALLBACK: Successfully processed research report with citations", processed_report)
    return genai_types.Content(parts=[genai_types.Part(text=processed_report)])


def output_composer_callback(
    callback_context: CallbackContext,
) -> genai_types.Content:
    """Logs the completion of the output composer agent.

    Args:
        callback_context (CallbackContext): The context object providing access to the agent's
            session events and persistent state.
    """
    # Log agent callback execution  
    agent_name = getattr(callback_context._invocation_context, 'agent_name', 'output_composer_agent')
    logger.info(f"AGENT CALLBACK: Executing output composer callback for '{agent_name}'")
    logger.info(f"OUTPUT COMPOSER: Finalizing structured trend data into Pydantic model")
    
    # Get the final trends report from state
    trends_report = callback_context.state.get("sephora_trends_report", {})
    
    if trends_report:
        logger.info(f"OUTPUT COMPOSER: Successfully composed trends report with {len(trends_report)} categories")
        
        # Log category breakdown if available
        if isinstance(trends_report, dict) and 'trends' in trends_report:
            trends_data = trends_report['trends']
            for category, trend_list in trends_data.items():
                if isinstance(trend_list, list):
                    logger.info(f"   └─ {category}: {len(trend_list)} trends")
    else:
        logger.warning("OUTPUT COMPOSER: No trends report found in state")
    
    return genai_types.Content(parts=[genai_types.Part(text="Output composition completed")])


