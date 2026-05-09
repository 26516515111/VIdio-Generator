"""Style and audio tag parser for MiMo TTS Director Mode."""
import re
from typing import Optional, Tuple, List


def parse_style_tags(text: str) -> Tuple[str, str]:
    """Extract style tags from LLM output.
    
    Supports two formats:
    1. Parenthesis prefix: "(冰冷 御姐音)你好" -> ("冰冷 御姐音", "你好")
    2. Style tag prefix: "<style>冰冷 御姐音</style>你好" -> ("冰冷 御姐音", "你好")
    
    Returns:
        Tuple of (style_tags_str, clean_text)
        If no style tags found, returns ("", original_text)
    """
    # Pattern 1: (style1 style2) text
    match = re.match(r'^\(([^)]+)\)\s*(.*)', text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    
    # Pattern 2: <style>style1 style2</style> text
    match = re.match(r'^<style>([^<]+)</style>\s*(.*)', text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    
    return "", text


def extract_audio_tags(text: str) -> List[str]:
    """Extract all audio tags from text.
    
    Audio tags are in brackets: [停顿], [叹气], （紧张，深呼吸）, etc.
    
    Returns:
        List of unique audio tags found
    """
    # Match [tag] format
    bracket_tags = re.findall(r'\[([^\]]+)\]', text)
    # Match （tag） format (Chinese parentheses with comma-separated descriptions)
    paren_tags = re.findall(r'（([^）]+)）', text)
    
    all_tags = bracket_tags + paren_tags
    # Deduplicate while preserving order
    seen = set()
    unique_tags = []
    for tag in all_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags


def build_tts_content(text: str, style_tags: Optional[str] = None) -> str:
    """Build content for TTS API with style tags prepended.
    
    If style_tags provided, wraps in (tag1 tag2) format and prepends.
    Otherwise returns text as-is.
    
    Args:
        text: The text to synthesize (may contain inline audio tags)
        style_tags: Optional style tags string (e.g., "冰冷 御姐音")
    
    Returns:
        Content string ready for TTS assistant message
    """
    if style_tags:
        return f"({style_tags}){text}"
    return text


def parse_director_output(llm_output: str) -> dict:
    """Parse LLM Director Mode output into structured components.
    
    Args:
        llm_output: Raw LLM output with style/audio tags
    
    Returns:
        Dict with keys: processed_text, style_tags, audio_tags, raw_output
    """
    style_tags, clean_text = parse_style_tags(llm_output)
    audio_tags = extract_audio_tags(clean_text)
    
    return {
        "processed_text": clean_text,
        "style_tags": style_tags,
        "audio_tags": audio_tags,
        "raw_output": llm_output,
    }
