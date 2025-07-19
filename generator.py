#!/usr/bin/env python3
"""
Static Site Generator - Core Generator Script

This script is the main entry point for the static site generator. It handles
content processing, template rendering, and site generation. It can be run
in different modes: build (generate static site), serve (development server),
or new (create new content).

Usage:
    python generator.py build       # Generate the static site
    python generator.py serve       # Start development server with auto-rebuild
    python generator.py new post "My Post Title"  # Create new post
"""

import os
import sys
import shutil
import argparse
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import jinja2
from jinja2 import Environment, FileSystemLoader

from config import Config
from content_processor import ContentProcessor, ContentItem


class SiteGenerator:
    """
    Main static site generator class.
    
    Handles the complete pipeline of content processing, template rendering,
    and static site generation. Manages both full site builds and incremental
    updates during development.
    """
    
    def __init__(self):
        """Initialize the site generator with content processor and template environment."""
        self.content_processor = ContentProcessor()
        
        # Set up Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader(Config.TEMPLATES_DIR),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Add custom template filters
        self._setup_template_filters()
        
        # Content storage
        self.posts: List[ContentItem] = []
        self.essays: List[ContentItem] = []
        self.pages: List[ContentItem] = []
    
    def _setup_template_filters(self):
        """Add custom filters to the Jinja2 environment."""
        def dateformat(value, format='%Y-%m-%d'):
            """Format datetime objects in templates."""
            if value is None:
                return ''
            return value.strftime(format)
        
        def short_date(value):
            """Format date consistently as 'Jan 2025' for all posts."""
            if value is None:
                return ''
            
            # Always show month and full year for clarity
            return value.strftime('%b %Y')
        
        self.template_env.filters['dateformat'] = dateformat
        self.template_env.filters['short_date'] = short_date
    
    def load_content(self):
        """
        Load and process all content from the content directories.
        
        Scans the posts, essays, and pages directories for markdown files,
        processes them into ContentItem objects, and stores them for
        template rendering.
        """
        print("Loading content...")
        
        # Load posts
        self.posts = self.content_processor.process_directory(
            Config.POSTS_DIR, 'posts'
        )
        print(f"Loaded {len(self.posts)} posts")
        
        # Load essays
        self.essays = self.content_processor.process_directory(
            Config.ESSAYS_DIR, 'essays'
        )
        print(f"Loaded {len(self.essays)} essays")
        
        # Load pages
        self.pages = self.content_processor.process_directory(
            Config.PAGES_DIR, 'pages'
        )
        print(f"Loaded {len(self.pages)} pages")
    
    def ensure_output_directory(self):
        """Create or clean the output directory."""
        if os.path.exists(Config.OUTPUT_DIR):
            # Clean existing output directory
            shutil.rmtree(Config.OUTPUT_DIR)
        
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        print(f"Output directory ready: {Config.OUTPUT_DIR}")
    
    def copy_static_files(self):
        """Copy static files (CSS, JS, images) to the output directory."""
        if os.path.exists(Config.STATIC_DIR):
            static_output = os.path.join(Config.OUTPUT_DIR, 'static')
            shutil.copytree(Config.STATIC_DIR, static_output)
            print("Static files copied")
        else:
            print("No static directory found, skipping static files")
    
    def render_template(self, template_name: str, **context) -> str:
        """
        Render a Jinja2 template with the given context.
        
        Args:
            template_name: Name of the template file
            **context: Template context variables
            
        Returns:
            Rendered HTML string
        """
        template = self.template_env.get_template(template_name)
        
        # Add global template variables
        global_context = Config.get_template_vars()
        global_context.update(context)
        
        return template.render(**global_context)
    
    def generate_index_page(self):
        """Generate the index (home) page."""
        html = self.render_template(
            'index.html',
            recent_posts=self.posts[:5]  # Show 5 most recent posts
        )
        
        output_path = os.path.join(Config.OUTPUT_DIR, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated index page")
    
    def _group_posts_by_category(self, posts: List[ContentItem]) -> Dict[str, List[ContentItem]]:
        """
        Group posts by category for the category view.
        
        Args:
            posts: List of ContentItem objects
            
        Returns:
            Dictionary with category names as keys and lists of posts as values
        """
        categories = {}
        for post in posts:
            category = post.category.title()  # Capitalize category name
            if category not in categories:
                categories[category] = []
            categories[category].append(post)
        
        # Sort categories alphabetically, but put common ones first
        category_order = ['Journalism', 'Personal', 'Tech']
        sorted_categories = {}
        
        # Add priority categories first
        for cat in category_order:
            if cat in categories:
                sorted_categories[cat] = categories[cat]
        
        # Add remaining categories alphabetically
        for cat in sorted(categories.keys()):
            if cat not in sorted_categories:
                sorted_categories[cat] = categories[cat]
        
        return sorted_categories

    def generate_blog_page(self):
        """Generate the blog listing page."""
        # Group posts by category
        posts_by_category = self._group_posts_by_category(self.posts)
        
        html = self.render_template(
            'blog.html',
            posts=self.posts,
            posts_by_category=posts_by_category
        )
        
        # Create blog directory and index file
        blog_dir = os.path.join(Config.OUTPUT_DIR, 'blog')
        os.makedirs(blog_dir, exist_ok=True)
        
        output_path = os.path.join(blog_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated blog page")
    
    def generate_essays_page(self):
        """Generate the essays listing page."""
        html = self.render_template(
            'essays.html',
            essays=self.essays
        )
        
        # Create essays directory and index file
        essays_dir = os.path.join(Config.OUTPUT_DIR, 'essays')
        os.makedirs(essays_dir, exist_ok=True)
        
        output_path = os.path.join(essays_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated essays page")
    
    def generate_content_pages(self):
        """Generate individual pages for all content items."""
        all_content = self.posts + self.essays + self.pages
        
        for item in all_content:
            # Skip external links (essays with external_url)
            if item.external_url:
                continue
            
            html = self.render_template(
                'post.html',
                post=item
            )
            
            # Create directory structure for the post URL
            url_path = item.url.strip('/')
            output_dir = os.path.join(Config.OUTPUT_DIR, url_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Write the HTML file
            output_path = os.path.join(output_dir, 'index.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Generated {len(all_content)} content pages")
    
    def build_site(self):
        """
        Build the complete static site.
        
        This is the main build process that:
        1. Loads all content
        2. Sets up output directory
        3. Copies static files
        4. Generates all pages
        """
        print("Starting site build...")
        start_time = datetime.now()
        
        # Load content from markdown files
        self.load_content()
        
        # Prepare output directory
        self.ensure_output_directory()
        
        # Copy static assets
        self.copy_static_files()
        
        # Generate all pages
        self.generate_index_page()
        self.generate_blog_page()
        self.generate_essays_page()
        self.generate_content_pages()
        
        # Build complete
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Site build complete in {duration:.2f}s")
        print(f"Generated site in: {Config.OUTPUT_DIR}")


def create_new_post(title: str, content_type: str = 'posts'):
    """
    Create a new markdown file with frontmatter template.
    
    Args:
        title: Title of the new post
        content_type: Type of content ('posts', 'essays', 'pages')
    """
    # Generate filename from title
    filename = title.lower().replace(' ', '-').replace('_', '-')
    # Remove non-alphanumeric characters except hyphens
    import re
    filename = re.sub(r'[^a-zA-Z0-9\-]', '', filename)
    filename = f"{filename}.md"
    
    # Determine content directory
    content_dirs = {
        'posts': Config.POSTS_DIR,
        'essays': Config.ESSAYS_DIR,
        'pages': Config.PAGES_DIR
    }
    
    if content_type not in content_dirs:
        print(f"Error: Unknown content type '{content_type}'. Use: posts, essays, pages")
        return
    
    content_dir = content_dirs[content_type]
    
    # Create content directory if it doesn't exist
    os.makedirs(content_dir, exist_ok=True)
    
    # File path
    file_path = os.path.join(content_dir, filename)
    
    # Check if file already exists
    if os.path.exists(file_path):
        print(f"Error: File already exists: {file_path}")
        return
    
    # Create frontmatter template
    frontmatter = f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d')}
published: true
"""
    
    if content_type == 'essays':
        frontmatter += "# external_url: \"https://example.com/my-essay\"\n"
    
    frontmatter += "---\n\n"
    
    # Create the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        f.write(f"# {title}\n\n")
        f.write("Write your content here...\n")
    
    print(f"Created new {content_type[:-1]}: {file_path}")


def main():
    """Main entry point with command-line argument handling."""
    parser = argparse.ArgumentParser(description='Static Site Generator')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Build command
    subparsers.add_parser('build', help='Build the static site')
    
    # Serve command (placeholder for now)
    subparsers.add_parser('serve', help='Start development server')
    
    # New content command
    new_parser = subparsers.add_parser('new', help='Create new content')
    new_parser.add_argument('type', choices=['post', 'essay', 'page'], 
                          help='Type of content to create')
    new_parser.add_argument('title', help='Title of the new content')
    
    args = parser.parse_args()
    
    if args.command == 'build':
        generator = SiteGenerator()
        generator.build_site()
    
    elif args.command == 'serve':
        print("Development server not implemented yet. Use 'build' for now.")
        # TODO: Implement development server with auto-rebuild
    
    elif args.command == 'new':
        content_type = args.type + 's'  # Convert 'post' to 'posts'
        create_new_post(args.title, content_type)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()