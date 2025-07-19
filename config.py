"""
Configuration settings for the static site generator.

This module contains all configuration constants and settings used throughout
the static site generator. It centralizes site metadata, directory paths,
build settings, and provides template variables for Jinja2 templates.
"""

import os
from datetime import datetime
import pytz


class Config:
    """
    Central configuration class for the static site generator.
    
    This class holds all configuration constants including site metadata,
    directory paths, build settings, and development server configuration.
    All paths are computed relative to the project root directory.
    """
    
    # Site metadata - used in templates and meta tags
    SITE_NAME = "Samarth's Blog"
    SITE_URL = "https://www.samarthbansal.com/"
    AUTHOR = "Samarth Bansal"
    DESCRIPTION = "Personal blog and essays"
    TIMEZONE = pytz.timezone('Asia/Kolkata')  # Indian Standard Time
    
    # Base directory paths - all other paths are relative to BASE_DIR
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Project root
    CONTENT_DIR = os.path.join(BASE_DIR, "content")        # Source markdown files
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")    # Jinja2 template files
    STATIC_DIR = os.path.join(BASE_DIR, "static")          # CSS, JS, images
    OUTPUT_DIR = os.path.join(BASE_DIR, "output")          # Generated HTML files
    
    # Content type subdirectories - different types of content
    POSTS_DIR = os.path.join(CONTENT_DIR, "posts")         # Blog posts
    ESSAYS_DIR = os.path.join(CONTENT_DIR, "essays")       # Long-form crafted essays
    JOURNALISM_DIR = os.path.join(CONTENT_DIR, "journalism")  # Published journalism (external links)
    EVERGREEN_DIR = os.path.join(CONTENT_DIR, "evergreen")    # Living documents (principles, beliefs)
    PAGES_DIR = os.path.join(CONTENT_DIR, "pages")         # Static pages
    
    # Build and formatting settings
    DATE_FORMAT = "%B %d, %Y"  # Format for displaying dates (e.g., "January 15, 2024")
    
    # Development server configuration
    DEV_HOST = "localhost"  # Local development server host
    DEV_PORT = 8000         # Local development server port
    
    # File processing settings
    MARKDOWN_EXTENSIONS = ['.md', '.markdown']  # Supported markdown file extensions
    
    @classmethod
    def get_template_vars(cls):
        """
        Get global variables to pass to all Jinja2 templates.
        
        These variables are available in every template and include site metadata
        and commonly needed values like the current year for copyright notices.
        
        Returns:
            dict: Dictionary of template variables with site metadata
        """
        return {
            'site_name': cls.SITE_NAME,
            'site_url': cls.SITE_URL,
            'author': cls.AUTHOR,
            'description': cls.DESCRIPTION,
            'current_year': datetime.now().year,
        }