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
import json
from datetime import datetime
from typing import List, Dict, Any, Set
from pathlib import Path

import jinja2
from jinja2 import Environment, FileSystemLoader

from config import Config
from content_processor import ContentProcessor, ContentItem


class BuildTracker:
    """
    Simple build change tracker to show what content was added, updated, or deleted.
    
    Tracks content by comparing titles and dates from current build with previous build.
    Stores minimal metadata in a JSON file to detect changes between builds.
    """
    
    def __init__(self):
        self.tracker_file = os.path.join(Config.BASE_DIR, '.build_tracker.json')
        self.previous_content = self._load_previous_build()
        self.current_content = {}
        
        # Track changes
        self.added = []
        self.updated = []
        self.deleted = []
    
    def _load_previous_build(self) -> Dict[str, Dict]:
        """Load previous build metadata from tracker file."""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def track_content(self, content_items: List[ContentItem]):
        """Track current content and detect changes."""
        # Build current content map
        for item in content_items:
            if item.external_url:  # Skip external links
                continue
                
            key = f"{item.content_type}:{item.slug}"
            
            # Get file modification time for content change detection
            file_mtime = None
            if item.source_file and os.path.exists(item.source_file):
                file_mtime = os.path.getmtime(item.source_file)
            
            self.current_content[key] = {
                'title': item.title,
                'date': item.date.isoformat() if item.date else None,
                'url': item.url,
                'type': item.content_type,
                'file_mtime': file_mtime
            }
        
        # Detect changes
        current_keys = set(self.current_content.keys())
        previous_keys = set(self.previous_content.keys())
        
        # New content
        added_keys = current_keys - previous_keys
        self.added = [self.current_content[key] for key in added_keys]
        
        # Deleted content  
        deleted_keys = previous_keys - current_keys
        self.deleted = [self.previous_content[key] for key in deleted_keys]
        
        # Updated content (same key but different title/date/content)
        for key in current_keys & previous_keys:
            current = self.current_content[key]
            previous = self.previous_content[key]
            
            # Check for title, date, or file modification time changes
            title_changed = current['title'] != previous.get('title')
            date_changed = current['date'] != previous.get('date')
            file_changed = (current.get('file_mtime') and 
                          previous.get('file_mtime') and
                          current['file_mtime'] != previous['file_mtime'])
            
            if title_changed or date_changed or file_changed:
                self.updated.append(current)
    
    def save_current_build(self):
        """Save current build metadata for next comparison."""
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_content, f, indent=2)
    
    def print_changes(self):
        """Print a summary of changes since last build."""
        if not (self.added or self.updated or self.deleted):
            print("✓ No content changes since last build")
            return
        
        print("\n📋 Content Changes:")
        
        if self.added:
            print(f"\n  ✨ Added ({len(self.added)}):")
            for item in self.added:
                print(f"     • {item['title']} ({item['type']})")
        
        if self.updated:
            print(f"\n  📝 Updated ({len(self.updated)}):")
            for item in self.updated:
                print(f"     • {item['title']} ({item['type']})")
        
        if self.deleted:
            print(f"\n  🗑️  Deleted ({len(self.deleted)}):")
            for item in self.deleted:
                print(f"     • {item['title']} ({item['type']})")
        
        print()  # Empty line for spacing


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
        self.build_tracker = BuildTracker()
        
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
        self.journalism: List[ContentItem] = []
        self.evergreen: List[ContentItem] = []
        self.micro: List[ContentItem] = []
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
        
        # Load journalism
        self.journalism = self.content_processor.process_directory(
            Config.JOURNALISM_DIR, 'journalism'
        )
        print(f"Loaded {len(self.journalism)} journalism pieces")
        
        # Load evergreen content
        self.evergreen = self.content_processor.process_directory(
            Config.EVERGREEN_DIR, 'evergreen'
        )
        print(f"Loaded {len(self.evergreen)} evergreen documents")
        
        # Load micro content
        self.micro = self.content_processor.process_directory(
            Config.MICRO_DIR, 'micro'
        )
        print(f"Loaded {len(self.micro)} micro posts")
        
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
            recent_posts=self.posts[:5],  # Show 5 most recent posts
            essays=self.essays,
            journalism=self.journalism,
            evergreen=self.evergreen
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
    
    def generate_journalism_page(self):
        """Generate the journalism listing page."""
        html = self.render_template(
            'journalism.html',
            journalism=self.journalism
        )
        
        # Create journalism directory and index file
        journalism_dir = os.path.join(Config.OUTPUT_DIR, 'journalism')
        os.makedirs(journalism_dir, exist_ok=True)
        
        output_path = os.path.join(journalism_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated journalism page")
    
    def generate_evergreen_page(self):
        """Generate the evergreen listing page."""
        html = self.render_template(
            'evergreen.html',
            evergreen=self.evergreen
        )
        
        # Create evergreen directory and index file
        evergreen_dir = os.path.join(Config.OUTPUT_DIR, 'evergreen')
        os.makedirs(evergreen_dir, exist_ok=True)
        
        output_path = os.path.join(evergreen_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated evergreen page")
    
    def generate_microblog_page(self):
        """Generate the microblog listing page."""
        html = self.render_template(
            'microblog.html',
            micro_posts=self.micro
        )
        
        # Create microblog directory and index file
        micro_dir = os.path.join(Config.OUTPUT_DIR, 'micro')
        os.makedirs(micro_dir, exist_ok=True)
        
        output_path = os.path.join(micro_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated microblog page")
    
    def generate_content_pages(self):
        """Generate individual pages for all content items."""
        all_content = self.posts + self.essays + self.journalism + self.evergreen + self.micro + self.pages
        
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
        2. Tracks changes from previous build
        3. Sets up output directory
        4. Copies static files
        5. Generates all pages
        """
        print("Starting site build...")
        start_time = datetime.now()
        
        # Load content from markdown files
        self.load_content()
        
        # Track content changes
        all_content = self.posts + self.essays + self.journalism + self.evergreen + self.micro + self.pages
        self.build_tracker.track_content(all_content)
        
        # Prepare output directory
        self.ensure_output_directory()
        
        # Copy static assets
        self.copy_static_files()
        
        # Generate all pages
        self.generate_index_page()
        self.generate_blog_page()
        self.generate_essays_page()
        self.generate_journalism_page()
        self.generate_evergreen_page()
        self.generate_microblog_page()
        self.generate_content_pages()
        
        # Save current build state and show changes
        self.build_tracker.save_current_build()
        self.build_tracker.print_changes()
        
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
    # Generate filename - timestamp-based for micro posts
    if content_type == 'micro':
        # Use timestamp for micro posts
        timestamp = datetime.now().strftime('%Y-%m-%d-%H%M')
        filename = f"{timestamp}.md"
    else:
        # Generate from title for other content types
        filename = title.lower().replace(' ', '-').replace('_', '-')
        # Remove non-alphanumeric characters except hyphens
        import re
        filename = re.sub(r'[^a-zA-Z0-9\-]', '', filename)
        filename = f"{filename}.md"
    
    # Determine content directory
    content_dirs = {
        'posts': Config.POSTS_DIR,
        'essays': Config.ESSAYS_DIR,
        'journalism': Config.JOURNALISM_DIR,
        'evergreen': Config.EVERGREEN_DIR,
        'micro': Config.MICRO_DIR,
        'pages': Config.PAGES_DIR
    }
    
    if content_type not in content_dirs:
        print(f"Error: Unknown content type '{content_type}'. Use: posts, essays, journalism, evergreen, micro, pages")
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
    if content_type == 'micro':
        # Micro posts don't need titles and use full datetime
        frontmatter = f"""---
date: {datetime.now().isoformat()}
published: true
"""
    else:
        # Regular content with title
        frontmatter = f"""---
title: "{title}"
date: {datetime.now().strftime('%Y-%m-%d')}
published: true
"""
    
    if content_type == 'essays':
        frontmatter += "# external_url: \"https://example.com/my-essay\"\n"
    elif content_type == 'journalism':
        frontmatter += "external_url: \"https://example.com/my-article\"\n"
    elif content_type == 'evergreen':
        frontmatter += "# last_updated: 2025-07-19  # Update this when you modify the content\n"
    elif content_type == 'micro':
        frontmatter += "# tags: [thought, link]  # Optional tags\n"
    
    frontmatter += "---\n\n"
    
    # Create the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
        if content_type == 'micro':
            # Micro posts don't need title headers
            f.write(f"{title}\n")  # Use title as content
        else:
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
    new_parser.add_argument('type', choices=['post', 'essay', 'journalism', 'evergreen', 'micro', 'page'], 
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
        # Map CLI args to internal content type names
        type_mapping = {
            'post': 'posts',
            'essay': 'essays', 
            'journalism': 'journalism',
            'evergreen': 'evergreen',
            'micro': 'micro',
            'page': 'pages'
        }
        content_type = type_mapping[args.type]
        create_new_post(args.title, content_type)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()