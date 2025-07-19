#!/usr/bin/env python3
"""
Migration script for importing existing blog posts.

This script analyzes markdown files in the migrate_posts directory,
standardizes their frontmatter, preserves existing slugs for URL compatibility,
suggests categories, and converts them to the new static site generator format.

Usage:
    python migrate.py analyze    # Analyze existing posts and show report
    python migrate.py migrate    # Actually migrate posts to content/posts/
    python migrate.py preview <file>  # Preview migration for specific file
"""

import os
import re
import sys
import yaml
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from config import Config


class PostMigrator:
    """
    Handles migration of existing blog posts to the new format.
    
    Analyzes existing frontmatter, preserves slugs for URL compatibility,
    suggests improvements, categorizes content, and converts posts to the
    standardized format used by the static site generator.
    """
    
    def __init__(self):
        """Initialize the migrator with source and destination paths."""
        self.migrate_dir = os.path.join(Config.BASE_DIR, "migrate_posts")
        self.posts_dir = Config.POSTS_DIR
        
        # Category keywords for auto-categorization
        self.category_keywords = {
            'journalism': [
                'journalism', 'journalist', 'media', 'news', 'reporting', 'story',
                'investigation', 'interview', 'press', 'editor', 'newsroom',
                'wall street journal', 'hindu', 'hindustan times', 'atlantic',
                'mint', 'rest of world', 'plank'
            ],
            'personal': [
                'personal', 'life', 'thoughts', 'reflection', 'diary', 'bombay',
                'mumbai', 'delhi', 'coffee', 'city', 'love', 'family', 'friend',
                'experience', 'story', 'memory', 'travel'
            ],
            'tech': [
                'technology', 'tech', 'programming', 'code', 'software', 'web',
                'development', 'python', 'javascript', 'html', 'css', 'api',
                'database', 'algorithm', 'startup', 'product'
            ],
            'food': [
                'food', 'nutrition', 'health', 'eating', 'diet', 'cooking',
                'restaurant', 'recipe', 'whole truth foods', 'ingredient',
                'organic', 'clean label'
            ]
        }
    
    def analyze_frontmatter(self, content: str) -> Dict[str, Any]:
        """
        Extract and analyze frontmatter from markdown content.
        
        Args:
            content: Raw markdown file content
            
        Returns:
            Dictionary containing frontmatter data or empty dict if none found
        """
        # Pattern to match YAML frontmatter
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if not match:
            return {}
        
        yaml_content = match.group(1)
        try:
            return yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing YAML frontmatter: {e}")
            return {}
    
    def suggest_category(self, title: str, content: str, existing_frontmatter: Dict[str, Any]) -> str:
        """
        Suggest a category based on title, content, and existing frontmatter.
        
        Args:
            title: Post title
            content: Post content (without frontmatter)
            existing_frontmatter: Existing frontmatter data
            
        Returns:
            Suggested category name
        """
        # Check if category already exists in frontmatter
        if 'category' in existing_frontmatter:
            return existing_frontmatter['category'].lower()
        
        # Check for tags or keywords in existing frontmatter
        existing_tags = existing_frontmatter.get('tags', [])
        if isinstance(existing_tags, str):
            existing_tags = [existing_tags]
        
        # Combine title, content, and tags for analysis
        text_to_analyze = f"{title} {content} {' '.join(existing_tags)}".lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return category with highest score
            return max(category_scores, key=category_scores.get)
        
        return 'uncategorized'
    
    def standardize_date(self, date_value: Any) -> Optional[str]:
        """
        Standardize date format to YYYY-MM-DD.
        
        Args:
            date_value: Date in various formats
            
        Returns:
            Standardized date string or None if parsing fails
        """
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        
        if isinstance(date_value, str):
            # Try various date formats
            date_formats = [
                '%Y-%m-%d',           # 2024-01-15
                '%Y/%m/%d',           # 2024/01/15
                '%d/%m/%Y',           # 15/01/2024
                '%B %d, %Y',          # January 15, 2024
                '%b %d, %Y',          # Jan 15, 2024
                '%d %B %Y',           # 15 January 2024
                '%d %B, %Y',          # 31 December, 2023 (your format)
                '%Y-%m-%d %H:%M:%S',  # 2024-01-15 10:30:00
                '%d-%m-%Y',           # 31-12-2023
                '%m/%d/%Y',           # 12/31/2023
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_value, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If we get here, none of the formats worked
            print(f"Warning: Could not parse date '{date_value}' with any known format")
            return None
        
        # Handle date objects
        if hasattr(date_value, 'year'):
            return f"{date_value.year:04d}-{date_value.month:02d}-{date_value.day:02d}"
        
        return None
    
    def preserve_slug(self, existing_frontmatter: Dict[str, Any], title: str) -> Optional[str]:
        """
        Preserve existing slug for URL compatibility.
        
        Args:
            existing_frontmatter: Existing frontmatter data
            title: Post title for fallback slug generation
            
        Returns:
            Slug to use, or None if no existing slug
        """
        # Check for existing slug in frontmatter
        existing_slug = existing_frontmatter.get('slug')
        if existing_slug:
            # Clean the slug (remove .html extension if present)
            slug = existing_slug.replace('.html', '')
            return slug
        
        # No existing slug - let the system generate one from title
        return None
    
    def create_standardized_frontmatter(self, file_path: str, existing_frontmatter: Dict[str, Any], 
                                      title: str, content: str) -> Dict[str, Any]:
        """
        Create standardized frontmatter for the new system.
        
        Args:
            file_path: Path to the original file
            existing_frontmatter: Existing frontmatter data
            title: Post title
            content: Post content
            
        Returns:
            Standardized frontmatter dictionary
        """
        # Extract title (prefer existing, fall back to filename)
        post_title = existing_frontmatter.get('title', title or self._title_from_filename(file_path))
        
        # Standardize date - check multiple possible date fields
        date_str = None
        date_fields = ['date', 'date_published', 'created', 'published_date', 'publish_date']
        
        for field in date_fields:
            if field in existing_frontmatter:
                date_str = self.standardize_date(existing_frontmatter.get(field))
                if date_str:  # If we successfully parsed a date, use it
                    break
        
        # Suggest category
        category = self.suggest_category(post_title, content, existing_frontmatter)
        
        # Preserve existing slug for URL compatibility
        preserved_slug = self.preserve_slug(existing_frontmatter, post_title)
        
        # Build new frontmatter
        new_frontmatter = {
            'title': post_title,
            'published': existing_frontmatter.get('published', True)
        }
        
        if date_str:
            new_frontmatter['date'] = date_str
        
        new_frontmatter['category'] = category
        
        # Add preserved slug if it exists
        if preserved_slug:
            new_frontmatter['slug'] = preserved_slug
        
        # Add description if exists
        description = existing_frontmatter.get('description') or existing_frontmatter.get('summary')
        if description:
            new_frontmatter['description'] = description
        
        return new_frontmatter
    
    def _title_from_filename(self, file_path: str) -> str:
        """Generate title from filename."""
        filename = os.path.basename(file_path)
        name = os.path.splitext(filename)[0]
        # Convert hyphens/underscores to spaces and title case
        return name.replace('-', ' ').replace('_', ' ').title()
    
    def _extract_content_without_frontmatter(self, content: str) -> str:
        """Extract markdown content without frontmatter."""
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            return match.group(2)
        return content
    
    def analyze_migration_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file for migration.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Analysis report dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            existing_frontmatter = self.analyze_frontmatter(content)
            markdown_content = self._extract_content_without_frontmatter(content)
            title = existing_frontmatter.get('title', self._title_from_filename(file_path))
            
            new_frontmatter = self.create_standardized_frontmatter(
                file_path, existing_frontmatter, title, markdown_content
            )
            
            # Determine URL for compatibility check
            original_slug = existing_frontmatter.get('slug', '')
            if original_slug:
                original_url = f"https://www.samarthbansal.com/blog/{original_slug}"
                if not original_slug.endswith('.html'):
                    original_url += '.html'
            else:
                original_url = "No original URL (no slug found)"
            
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'existing_frontmatter': existing_frontmatter,
                'new_frontmatter': new_frontmatter,
                'content_length': len(markdown_content),
                'has_frontmatter': bool(existing_frontmatter),
                'needs_date': 'date' not in new_frontmatter,
                'suggested_category': new_frontmatter['category'],
                'has_slug': 'slug' in new_frontmatter,
                'original_url': original_url,
                'preserved_slug': new_frontmatter.get('slug', 'Generated from title')
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'filename': os.path.basename(file_path),
                'error': str(e)
            }
    
    def analyze_all_files(self) -> List[Dict[str, Any]]:
        """
        Analyze all markdown files in the migration directory.
        
        Returns:
            List of analysis reports
        """
        if not os.path.exists(self.migrate_dir):
            print(f"Migration directory not found: {self.migrate_dir}")
            return []
        
        analysis_reports = []
        
        for filename in os.listdir(self.migrate_dir):
            if filename.endswith(('.md', '.markdown')):
                file_path = os.path.join(self.migrate_dir, filename)
                report = self.analyze_migration_file(file_path)
                analysis_reports.append(report)
        
        return analysis_reports
    
    def print_analysis_report(self, reports: List[Dict[str, Any]]):
        """Print a detailed analysis report."""
        if not reports:
            print("No markdown files found in migration directory.")
            return
        
        print(f"\n📊 MIGRATION ANALYSIS REPORT")
        print(f"{'='*60}")
        print(f"Found {len(reports)} markdown files")
        
        # Count statistics
        with_frontmatter = sum(1 for r in reports if r.get('has_frontmatter', False))
        needs_date = sum(1 for r in reports if r.get('needs_date', False))
        has_errors = sum(1 for r in reports if 'error' in r)
        with_slugs = sum(1 for r in reports if r.get('has_slug', False))
        
        print(f"📝 Files with existing frontmatter: {with_frontmatter}")
        print(f"📅 Files needing date: {needs_date}")
        print(f"🔗 Files with existing slugs (URLs preserved): {with_slugs}")
        print(f"❌ Files with errors: {has_errors}")
        
        # Category distribution
        categories = {}
        for report in reports:
            if 'suggested_category' in report:
                cat = report['suggested_category']
                categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📂 Suggested categories:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat}: {count} posts")
        
        print(f"\n🔗 URL COMPATIBILITY CHECK:")
        print(f"{'-'*60}")
        for report in reports:
            if 'error' in report:
                continue
            if report.get('has_slug'):
                print(f"✅ {report['filename']}: URL preserved")
                print(f"   Original: {report['original_url']}")
                print(f"   New: /posts/{report['preserved_slug']}/")
            else:
                print(f"ℹ️  {report['filename']}: No original slug, new URL will be generated")
        
        print(f"\n📄 INDIVIDUAL FILE ANALYSIS:")
        print(f"{'-'*60}")
        
        for report in reports:
            if 'error' in report:
                print(f"❌ {report['filename']}: ERROR - {report['error']}")
                continue
            
            print(f"\n📄 {report['filename']}")
            print(f"   Title: {report['new_frontmatter']['title']}")
            print(f"   Category: {report['suggested_category']}")
            
            if report.get('has_slug'):
                print(f"   🔗 Slug: {report['preserved_slug']} (preserved for URL compatibility)")
            else:
                print(f"   🔗 Slug: Will be generated from title")
            
            if report.get('needs_date'):
                print(f"   ⚠️  Missing date - needs manual input")
            elif 'date' in report['new_frontmatter']:
                print(f"   Date: {report['new_frontmatter']['date']}")
            
            if 'description' in report['new_frontmatter']:
                print(f"   Description: {report['new_frontmatter']['description']}")
            
            print(f"   Content: {report['content_length']} characters")
    
    def migrate_file(self, report: Dict[str, Any], dry_run: bool = False) -> bool:
        """
        Migrate a single file based on analysis report.
        
        Args:
            report: Analysis report from analyze_migration_file
            dry_run: If True, don't actually create files
            
        Returns:
            True if successful, False otherwise
        """
        if 'error' in report:
            print(f"❌ Skipping {report['filename']}: {report['error']}")
            return False
        
        try:
            # Read original content
            with open(report['file_path'], 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Extract markdown content without frontmatter
            markdown_content = self._extract_content_without_frontmatter(original_content)
            
            # Create new frontmatter YAML
            frontmatter_yaml = yaml.dump(report['new_frontmatter'], default_flow_style=False)
            
            # Build new file content
            new_content = f"---\n{frontmatter_yaml}---\n\n{markdown_content}"
            
            if dry_run:
                print(f"✅ Would migrate: {report['filename']}")
                if report.get('has_slug'):
                    print(f"   → Preserving slug: {report['preserved_slug']}")
                return True
            
            # Create output filename
            if report.get('has_slug'):
                # Use preserved slug for filename
                filename = f"{report['preserved_slug']}.md"
            else:
                # Generate filename from title
                title = report['new_frontmatter']['title']
                filename = re.sub(r'[^a-zA-Z0-9\s\-]', '', title.lower())
                filename = re.sub(r'\s+', '-', filename.strip())
                filename = f"{filename}.md"
            
            # Ensure posts directory exists
            os.makedirs(self.posts_dir, exist_ok=True)
            
            # Write new file
            output_path = os.path.join(self.posts_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            if report.get('has_slug'):
                print(f"✅ Migrated: {report['filename']} → {filename} (slug preserved)")
            else:
                print(f"✅ Migrated: {report['filename']} → {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to migrate {report['filename']}: {e}")
            return False
    
    def migrate_all_files(self, dry_run: bool = False):
        """
        Migrate all files from analysis reports.
        
        Args:
            dry_run: If True, show what would be done without actually doing it
        """
        reports = self.analyze_all_files()
        
        if not reports:
            print("No files to migrate.")
            return
        
        print(f"\n🚀 {'DRY RUN - ' if dry_run else ''}STARTING MIGRATION")
        print(f"{'='*60}")
        
        successful = 0
        failed = 0
        preserved_urls = 0
        
        for report in reports:
            if self.migrate_file(report, dry_run):
                successful += 1
                if report.get('has_slug'):
                    preserved_urls += 1
            else:
                failed += 1
        
        print(f"\n📊 MIGRATION SUMMARY")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"🔗 URLs preserved: {preserved_urls}")
        
        if not dry_run and successful > 0:
            print(f"\n🎉 Migration complete! Run 'python generator.py build' to regenerate your site.")
            if preserved_urls > 0:
                print(f"💡 {preserved_urls} posts will maintain their original URLs for compatibility.")


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description='Migrate existing blog posts')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    subparsers.add_parser('analyze', help='Analyze migration files and show report')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate files to new format')
    migrate_parser.add_argument('--dry-run', action='store_true', 
                               help='Show what would be done without actually doing it')
    
    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview migration for specific file')
    preview_parser.add_argument('filename', help='Filename in migrate_posts directory')
    
    args = parser.parse_args()
    
    migrator = PostMigrator()
    
    if args.command == 'analyze':
        reports = migrator.analyze_all_files()
        migrator.print_analysis_report(reports)
    
    elif args.command == 'migrate':
        migrator.migrate_all_files(dry_run=args.dry_run)
    
    elif args.command == 'preview':
        file_path = os.path.join(migrator.migrate_dir, args.filename)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        report = migrator.analyze_migration_file(file_path)
        if 'error' in report:
            print(f"Error analyzing file: {report['error']}")
            return
        
        print(f"\n📄 PREVIEW: {args.filename}")
        print(f"{'='*60}")
        print(f"Original frontmatter: {report['existing_frontmatter']}")
        print(f"\nNew frontmatter: {report['new_frontmatter']}")
        print(f"\nSuggested category: {report['suggested_category']}")
        if report.get('has_slug'):
            print(f"🔗 Original URL: {report['original_url']}")
            print(f"🔗 New URL: /posts/{report['preserved_slug']}/")
        else:
            print(f"🔗 No original slug found - new URL will be generated from title")
        if report.get('needs_date'):
            print(f"⚠️  This file needs a date to be added manually")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()