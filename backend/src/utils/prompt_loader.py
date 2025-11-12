"""
Prompt loader utility for loading agent prompts from YAML configuration.
"""

import yaml
import os
from typing import Dict, Any

def load_prompts() -> Dict[str, Any]:
    """
    Load prompts from the prompts.yml file.
    
    Returns:
        Dict containing all agent prompts and configurations
    """
    # Get the path to the prompts.yml file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_path = os.path.join(current_dir, '..', 'prompts', 'prompts.yml')
    
    try:
        with open(prompts_path, 'r', encoding='utf-8') as file:
            prompts_data = yaml.safe_load(file)
        return prompts_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompts file not found at: {prompts_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")

def get_agent_prompt(agent_name: str) -> Dict[str, str]:
    """
    Get a specific agent's prompt configuration.
    
    Args:
        agent_name: Name of the agent (e.g., 'trend_research_agent', 'output_composer_agent')
    
    Returns:
        Dict containing the agent's name, description, and instruction
    """
    prompts_data = load_prompts()
    
    if 'agents' not in prompts_data:
        raise ValueError("No 'agents' section found in prompts.yml")
    
    if agent_name not in prompts_data['agents']:
        available_agents = list(prompts_data['agents'].keys())
        raise ValueError(f"Agent '{agent_name}' not found in prompts.yml. Available agents: {available_agents}")
    
    return prompts_data['agents'][agent_name]

def get_trend_research_agent_prompt() -> str:
    """
    Get the trend research agent instruction prompt.
    
    Returns:
        The instruction string for the trend research agent
    """
    agent_config = get_agent_prompt('trend_research_agent')
    return agent_config['instruction']

def get_output_composer_agent_prompt() -> str:
    """
    Get the output composer agent instruction prompt.
    
    Returns:
        The instruction string for the output composer agent
    """
    agent_config = get_agent_prompt('output_composer_agent')
    return agent_config['instruction']

def get_category_agent_prompt(category: str) -> str:
    """
    Get a category-specific agent instruction prompt.
    
    Args:
        category: The beauty category (e.g., 'Makeup', 'Skincare', 'Hair')
    
    Returns:
        The instruction string for the category-specific agent
    """
    # Get the base template from prompts.yml
    agent_config = get_agent_prompt('category_agent')
    base_instruction = agent_config['instruction']

    # Category-specific focus areas
    category_specifics = {
        "Tools & Brushes": """
   - Innovative brush designs and technologies
   - Multi-functional beauty tools
   - Sustainable and eco-friendly options
   - Professional vs consumer tool trends
   - Color and aesthetic trends in tool design""",
        
        "Skincare": """
   - Active ingredients and formulations
   - K-beauty and J-beauty innovations
   - Anti-aging and preventative care trends
   - Sustainable and clean beauty products
   - Skin concerns and targeted solutions""",
        
        "Mini Size": """
   - Travel-friendly product innovations
   - Gift set and sampler trends
   - Value-sized versions of popular products
   - Limited edition mini collections
   - Subscription box favorites""",
        
        "Men": """
   - Men's grooming and skincare trends
   - Color cosmetics for men
   - Fragrance preferences and launches
   - Celebrity male beauty influences
   - Breaking gender beauty norms""",
        
        "Makeup": """
   - Color trends and seasonal palettes
   - Application techniques and styles
   - Long-wear and innovative formulas
   - Social media beauty challenges
   - Runway and editorial inspirations""",
        
        "Hair": """
   - Hair color trends and techniques
   - Styling tools and innovations
   - Hair care for different textures
   - Protective and treatment products
   - Celebrity and influencer hair looks""",
        
        "Gifts": """
   - Holiday and seasonal gift sets
   - Limited edition collections
   - Luxury and prestige gifting
   - Personalized and customizable options
   - Value sets and bundles""",
        
        "Fragrance": """
   - New fragrance launches and collections
   - Scent families and note trends
   - Celebrity and designer collaborations
   - Niche and indie fragrance brands
   - Seasonal and occasion-specific scents""",
        
        "Bath & Body": """
   - Body care innovations and trends
   - Aromatherapy and wellness products
   - Seasonal scents and collections
   - Sustainable and natural formulations
   - Self-care and ritual-focused products"""
    }
    
    category_focus = category_specifics.get(category, f"   - Product innovations in {category}\n   - Popular brands and launches\n   - Price point trends\n   - Consumer preferences")
    
    # Replace placeholders in the template
    return base_instruction.format(category=category, category_focus=category_focus)

# Convenience functions for backwards compatibility
def get_trend_research_config() -> Dict[str, str]:
    """
    Get the full trend research agent configuration.
    
    Returns:
        Dict with name, description, and instruction
    """
    return get_agent_prompt('trend_research_agent')

def get_output_composer_config() -> Dict[str, str]:
    """
    Get the full output composer agent configuration.
    
    Returns:
        Dict with name, description, and instruction
    """
    return get_agent_prompt('output_composer_agent')