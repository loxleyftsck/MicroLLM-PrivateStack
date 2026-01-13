# -*- coding: utf-8 -*-
"""
LLM Output Formatter
Cleans and formats LLM responses for better readability
"""

import re
from typing import str

class LLMOutputFormatter:
    """
    Formats LLM output to make it clean and professional
    Removes thinking tags, formats markdown, adds structure
    """
    
    @staticmethod
    def clean_thinking_tags(text: str) -> str:
        """Remove <think> and </think> tags and their content"""
        # Remove <think>...</think> blocks completely
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove orphan tags
        text = re.sub(r'</?think>', '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def remove_repetitions(text: str) -> str:
        """Remove repeated sentences"""
        sentences = text.split('. ')
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence.lower() not in seen:
                seen.add(sentence.lower())
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences)
    
    @staticmethod
    def format_paragraphs(text: str) -> str:
        """Add proper paragraph breaks"""
        # Add line breaks after sentences that end paragraphs
        text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', text)
        
        # Ensure numbered lists have line breaks
        text = re.sub(r'(\d+\.)\s+', r'\n\1 ', text)
        
        # Ensure bullet points have line breaks
        text = re.sub(r'([•\-\*])\s+', r'\n\1 ', text)
        
        return text
    
    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Clean up excessive whitespace"""
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple line breaks (max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def format_markdown(text: str) -> str:
        """Enhance markdown formatting"""
        # Make headers more prominent
        text = re.sub(r'^(#{1,6})\s+(.+)$', r'\1 \2', text, flags=re.MULTILINE)
        
        # Ensure code blocks are properly formatted
        text = re.sub(r'```(\w+)?\n', r'```\1\n', text)
        
        return text
    
    @classmethod
    def format_response(cls, raw_text: str) -> str:
        """
        Main method: Apply all formatting to LLM output
        """
        if not raw_text:
            return ""
        
        # Step 1: Remove thinking tags
        text = cls.clean_thinking_tags(raw_text)
        
        # Step 2: Remove repetitions
        text = cls.remove_repetitions(text)
        
        # Step 3: Format paragraphs
        text = cls.format_paragraphs(text)
        
        # Step 4: Clean whitespace
        text = cls.clean_whitespace(text)
        
        # Step 5: Enhance markdown
        text = cls.format_markdown(text)
        
        return text
    
    @staticmethod
    def truncate_if_needed(text: str, max_length: int = 2000) -> str:
        """Truncate text if too long (for RAM optimization)"""
        if len(text) <= max_length:
            return text
        
        # Truncate at last complete sentence
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.8:  # If found near end
            return truncated[:last_period + 1] + "\n\n[Response truncated for length]"
        else:
            return truncated + "...\n\n[Response truncated for length]"
