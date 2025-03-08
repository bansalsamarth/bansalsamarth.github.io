#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import re
import hashlib
from pathlib import Path
import frontmatter
import subprocess
import markdown
import json
import tempfile
import webbrowser

class BlogPublisher:
    def __init__(self):
        self.root_dir = Path(__file__).parent.resolve()
        self.obsidian_dir = self.root_dir / "SamarthBlog"
        self.published_dir = self.obsidian_dir / "published"
        self.template_path = self.root_dir / "templates" / "post-template.html"
        print(f"Using template: {self.template_path}")
        self.blog_index_path = self.root_dir / "pages" / "blog.html"
        self.modified_files = []  # Track files we modify
        self.file_hashes = {}  # Store file hashes to detect changes
        self.processed_posts = []  # Store metadata of processed posts
        self.error_report = []  # Store markdown errors
        
        # Load existing file hashes if available
        self._load_hashes()

    def _load_hashes(self):
        """Load existing file hashes from cache file"""
        hash_file = self.root_dir / ".file_hashes.json"
        if hash_file.exists():
            try:
                with open(hash_file, 'r', encoding='utf-8') as f:
                    self.file_hashes = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.file_hashes = {}

    def _save_hashes(self):
        """Save current file hashes to cache file"""
        hash_file = self.root_dir / ".file_hashes.json"
        with open(hash_file, 'w', encoding='utf-8') as f:
            json.dump(self.file_hashes, f, indent=2)

    def _update_chronological_view(self):
        """Update the chronological view in blog.html with ALL posts"""
        # Get all published markdown files
        all_md_files = list(self.published_dir.glob('*.md'))
        all_posts = []
        
        # Load metadata from all markdown files
        for md_file in all_md_files:
            try:
                post = frontmatter.load(md_file)
                metadata = post.metadata
                # Ensure slug exists
                metadata['slug'] = metadata.get('slug', md_file.stem)
                # Handle date-prefixed filenames
                parts = md_file.stem.split("-", 3)
                if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                    if 'slug' not in metadata:
                        metadata['slug'] = parts[3]
                all_posts.append(metadata)
            except Exception as e:
                print(f"  WARNING: Could not load metadata from {md_file}: {e}")
        
        # Also include any posts processed in this run that might not be on disk yet
        for post in self.processed_posts:
            if post not in all_posts:
                all_posts.append(post)
                
        # Skip if no posts were found
        if not all_posts:
            print("  WARNING: No posts found for updating the blog index")
            return
            
        # Helper function to safely convert dates to naive datetime objects
        def safe_datetime(dt_value):
            if isinstance(dt_value, datetime):
                # Ensure we're using a naive datetime (no timezone)
                if dt_value.tzinfo is not None:
                    return dt_value.replace(tzinfo=None)
                return dt_value
            try:
                return datetime.strptime(dt_value, "%d %B, %Y")
            except (ValueError, TypeError):
                # Fallback to current date (naive datetime)
                return datetime.now().replace(tzinfo=None)
                
        # Sort posts by date, newest first
        def get_date(post):
            date_published = post.get('date_published')
            return safe_datetime(date_published)
                
        sorted_posts = sorted(
            all_posts,
            key=get_date,
            reverse=True
        )
        
        # Read current blog.html content
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the chronological view section
        chrono_start = content.find('<ul class="posts-list" id="chronological-view">')
        if chrono_start == -1:
            print("  WARNING: Could not locate chronological view section in blog.html")
            return
            
        chrono_end = content.find('<!-- Category View -->', chrono_start)
        if chrono_end == -1:
            print("  WARNING: Could not locate end of chronological view section in blog.html")
            return
        
        # Build new chronological list
        chrono_html = '<ul class="posts-list" id="chronological-view">\n'
        
        for post in sorted_posts:
            date_published = post.get('date_published')
            if isinstance(date_published, datetime):
                date = date_published
                month_year = date.strftime("%b %Y")
            else:
                try:
                    date = datetime.strptime(date_published, "%d %B, %Y")
                    month_year = date.strftime("%b %Y")
                except (ValueError, TypeError):
                    date = datetime.now()
                    month_year = "Unknown"
            
            slug = post.get('slug', '')
            title = post.get('title', 'Untitled')
            
            chrono_html += f'''<li class="post-item">
<span class="post-date">{month_year}</span>
<h2 class="post-title">
<a href="../blog/{slug}.html">
{title}
</a>
</h2>
</li>\n'''
        
        chrono_html += '</ul>\n'
        
        # Replace the chronological view section
        new_content = content[:chrono_start] + chrono_html + content[chrono_end:]
        
        # Only write if content has changed
        if new_content != content:
            with open(self.blog_index_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            self.modified_files.append(self.blog_index_path)

    def _get_file_hash(self, file_path):
        """Calculate MD5 hash for a file"""
        with open(file_path, 'rb') as f:
            file_data = f.read()
            return hashlib.md5(file_data).hexdigest()

    def _has_file_changed(self, file_path):
        """Check if file has changed since last run"""
        str_path = str(file_path)
        current_hash = self._get_file_hash(file_path)
        if str_path in self.file_hashes and self.file_hashes[str_path] == current_hash:
            return False
        self.file_hashes[str_path] = current_hash
        return True
    
    def check_existing_post(self, slug):
        """Check if a post with this slug already exists"""
        html_file = self.root_dir / 'blog' / f"{slug}.html"
        if html_file.exists():
            print(f"\nWARNING: A post with slug '{slug}' already exists!")
            print(f"File: {html_file}")
            confirm = input("Do you want to overwrite it? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborting...")
                sys.exit(1)
            print("Proceeding with overwrite...")

    def check_slug_in_index(self, slug):
        """Check if this slug is already in the blog index"""
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if f"href=\"../blog/{slug}.html\"" in content:
            print(f"\nWARNING: Found existing entry for slug '{slug}' in blog index!")
            print("This might mean:")
            print("1. You're updating an existing post")
            print("2. You've used a slug that was used before")
            confirm = input("Continue anyway? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborting...")
                sys.exit(1)
            print("Proceeding...")
    
    def update_category_view(self):
        """Update the category view in blog.html with ALL posts"""
        # Get all published markdown files
        all_md_files = list(self.published_dir.glob('*.md'))
        all_posts = []
        
        # Load metadata from all markdown files
        for md_file in all_md_files:
            try:
                post = frontmatter.load(md_file)
                metadata = post.metadata
                # Ensure slug exists
                metadata['slug'] = metadata.get('slug', md_file.stem)
                # Handle date-prefixed filenames
                parts = md_file.stem.split("-", 3)
                if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
                    if 'slug' not in metadata:
                        metadata['slug'] = parts[3]
                all_posts.append(metadata)
            except Exception as e:
                print(f"  WARNING: Could not load metadata from {md_file}: {e}")
        
        # Also include any posts processed in this run that might not be on disk yet
        for post in self.processed_posts:
            if post not in all_posts:
                all_posts.append(post)
                
        # Skip if no posts were found
        if not all_posts:
            print("  WARNING: No posts found for updating the blog index")
            return
            
        # Helper function to safely convert dates to naive datetime objects
        def safe_datetime(dt_value):
            if isinstance(dt_value, datetime):
                # Ensure we're using a naive datetime (no timezone)
                if dt_value.tzinfo is not None:
                    return dt_value.replace(tzinfo=None)
                return dt_value
            try:
                return datetime.strptime(dt_value, "%d %B, %Y")
            except (ValueError, TypeError):
                # Fallback to current date (naive datetime)
                return datetime.now().replace(tzinfo=None)
                
        # Sort posts by date, newest first
        def get_date(post):
            date_published = post.get('date_published')
            return safe_datetime(date_published)
                
        sorted_posts = sorted(
            all_posts,
            key=get_date,
            reverse=True
        )
        
        # Read current blog.html content
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find the category view section
        category_start = content.find('<div class="posts-list" id="category-view"')
        if category_start == -1:
            print("  WARNING: Could not locate category view section in blog.html")
            return
            
        category_end = content.find('</div>', category_start)
        if category_end == -1:
            print("  WARNING: Could not locate end of category view section in blog.html")
            return
            
        # Find the closing div for the entire category view
        category_end = content.rfind('</div>', category_start, content.rfind('</body>'))
        if category_end == -1:
            print("  WARNING: Could not locate proper end of category view section in blog.html")
            return
            
        # Group posts by category
        posts_by_category = {}
        for post in sorted_posts:
            category = self.get_category_from_tags(post.get('tags', []))
            if category not in posts_by_category:
                posts_by_category[category] = []
            posts_by_category[category].append(post)
            
        # Build new category view HTML
        category_html = '<div class="posts-list" id="category-view" style="display: none;">\n'
        
        # For each category
        for category in sorted(posts_by_category.keys()):
            category_html += f'<!-- {category} -->\n'
            category_html += f'<div class="category-section">\n'
            category_html += f'<h3 class="category-title">{category}</h3>\n'
            category_html += f'<ul class="posts-list">\n'
            
            for post in sorted(posts_by_category[category], key=get_date, reverse=True):
                date_published = post.get('date_published')
                if isinstance(date_published, datetime):
                    date = date_published
                    month_year = date.strftime("%b %Y")
                else:
                    try:
                        date = datetime.strptime(date_published, "%d %B, %Y")
                        month_year = date.strftime("%b %Y")
                    except (ValueError, TypeError):
                        date = datetime.now()
                        month_year = "Unknown"
                
                slug = post.get('slug', '')
                title = post.get('title', 'Untitled')
                
                category_html += f'''<li class="post-item">
<span class="post-date">{month_year}</span>
<h2 class="post-title">
<a href="../blog/{slug}.html">{title}</a>
</h2>
</li>\n'''
            
            category_html += '</ul>\n'
            category_html += '</div>\n'
        
        category_html += '</div>\n'
        
        # Replace the category view section
        new_content = content[:category_start] + category_html + content[category_end+6:]
        
        # Only write if content has changed
        if new_content != content:
            with open(self.blog_index_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            self.modified_files.append(self.blog_index_path)

    def add_to_blog_index(self, title, slug, date_published, tags):
        """Add the post to the blog index under its category"""
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Store original content to check if it changed
        original_content = content

        category = self.get_category_from_tags(tags)
        
        # Handle date_published which might already be a datetime object
        if isinstance(date_published, datetime):
            date_obj = date_published
        else:
            try:
                date_obj = datetime.strptime(date_published, "%d %B, %Y")
            except (ValueError, TypeError):
                # Fallback to current date if we can't parse the date
                print(f"  WARNING: Could not parse date '{date_published}'. Using current date.")
                date_obj = datetime.now()
                
        formatted_date = date_obj.strftime("%B %Y")
        
        new_entry = f'\n      <p><a href="../blog/{slug}.html">{title}</a> — {formatted_date}</p>\n'
        
        # Check if entry already exists
        if f'href="../blog/{slug}.html"' in content:
            # Find the line with this slug and replace it
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if f'href="../blog/{slug}.html"' in line:
                    lines[i] = f'      <p><a href="../blog/{slug}.html">{title}</a> — {formatted_date}</p>'
                    break
            content = '\n'.join(lines)
        else:
            # Add new entry
            category_pattern = f'<h3>{category}</h3>'
            if category_pattern in content:
                pos = content.find(category_pattern) + len(category_pattern)
                content = content[:pos] + new_entry + content[pos:]
            else:
                new_section = f'\n      <h3>{category}</h3>{new_entry}\n      <hr>\n'
                last_hr = content.rfind('<hr>')
                if last_hr != -1:
                    content = content[:last_hr] + new_section + content[last_hr:]

        # Only write and track if content changed
        if content != original_content:
            with open(self.blog_index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.modified_files.append(self.blog_index_path)

    def get_category_from_tags(self, tags):
        category_map = {
            "Writing": ["Writing"],
            "Dating": ["Dating", "Romance"],
            "Personal": ["Personal", "Life"],
            "Work and Career": ["Work", "Career"],
            "Journalism": ["Journalism", "Media"],
            "Politics and Public Affairs": ["Politics", "Public Affairs"],
            "Learning": ["Learning", "Education"],
            "Health and Fitness": ["Health", "Fitness"]
        }
        
        if not tags:
            return "Personal"
            
        for category, tag_list in category_map.items():
            if any(tag in tags for tag in tag_list):
                return category
                
        return "Personal"

    def convert_md_to_html(self, md_path, tolerant=True):
        """Process markdown file and create HTML using template"""
        print(f"  Reading markdown file: {md_path.name}...")
        
        # Clear previous errors for this file
        self.error_report = []
        
        try:
            # Read the markdown file with frontmatter
            post = frontmatter.load(md_path)
            
            # Validate required metadata
            required_fields = ['title', 'date_published']
            missing_fields = [field for field in required_fields if field not in post.metadata]
            
            if missing_fields:
                error_msg = f"Missing required metadata: {', '.join(missing_fields)}"
                self.error_report.append(error_msg)
                if not tolerant:
                    raise ValueError(error_msg)
                else:
                    print(f"  WARNING: {error_msg}")
                    if 'title' not in post.metadata:
                        post.metadata['title'] = md_path.stem
                    if 'date_published' not in post.metadata:
                        post.metadata['date_published'] = datetime.now().strftime("%d %B, %Y")
            
            print(f"  Metadata found: {list(post.metadata.keys())}")
            
            # Convert markdown content to HTML
            try:
                print("  Converting markdown to HTML...")
                # Basic conversion first
                html_content = markdown.markdown(post.content)
                
                # Now try full conversion with extensions
                html_content = markdown.markdown(
                    post.content,
                    extensions=[
                        'markdown.extensions.fenced_code',
                        'markdown.extensions.tables',
                        'markdown.extensions.smarty',
                        'markdown.extensions.attr_list',
                        'markdown.extensions.extra'
                    ]
                )
                print("  Markdown conversion successful")
            except Exception as md_error:
                error_msg = f"Markdown conversion error: {str(md_error)}"
                self.error_report.append(error_msg)
                
                if not tolerant:
                    raise
                else:
                    print(f"  WARNING: {error_msg}")
                    print("  Falling back to basic conversion...")
                    # Try with just basic markdown conversion
                    html_content = markdown.markdown(post.content)
            
            # Read template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Extract category from tags if available
            category = None
            if 'tags' in post.metadata and post.metadata['tags']:
                category = self.get_category_from_tags(post.metadata['tags'])
                
            print("  Using new template with style.css")
            
            # Create a clean HTML document using the new template structure
            html = template\
                .replace('$title$', post.metadata.get('title', ''))\
                .replace('$author$', post.metadata.get('author', ''))
            
            # Handle date_published
            if 'date_published' in post.metadata:
                html = html.replace('$date_published$', post.metadata.get('date_published', ''))
            else:
                html = html.replace('$date_published$', '')
                
            # Handle category if present
            if category:
                html = html.replace('$if(category)$', '')
                html = html.replace('$category$', category)
                html = html.replace('$endif$', '')
            else:
                html = re.sub(r'\$if\(category\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
                
            # Handle excerpt if present
            if 'excerpt' in post.metadata:
                html = html.replace('$if(excerpt)$', '')
                html = html.replace('$excerpt$', post.metadata.get('excerpt', ''))
                html = html.replace('$endif$', '')
            else:
                html = re.sub(r'\$if\(excerpt\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
                
            # Insert the content
            html = html.replace('$body$', html_content)

            # Handle description metadata
            if 'description-meta' in post.metadata:
                html = html.replace('$if(description-meta)$', '')
                html = html.replace('$description-meta$', post.metadata.get('description-meta', ''))
                html = html.replace('$endif$', '')
            else:
                # Use excerpt as description if available, otherwise use a snippet of the content
                description = ""
                if 'excerpt' in post.metadata:
                    description = post.metadata.get('excerpt', '')
                else:
                    # Create a description from the first 150 characters of content
                    plain_content = re.sub(r'<[^>]+>', '', html_content)
                    description = plain_content[:150] + '...' if len(plain_content) > 150 else plain_content
                
                html = re.sub(r'\$if\(description-meta\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
                html = html.replace('$description-meta$', description)

            # Remove all remaining template variables and their conditional blocks
            html = re.sub(r'\$if\([^$]+\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$for\([^$]+\)\$.*?\$endfor\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$[^$]+\$', '', html)
            
            # Remove the TOC navigation if present
            html = re.sub(r'<nav id="TOC"[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
            
            # Clean up any multiple newlines
            html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)
            
            return html, post.metadata
            
        except Exception as e:
            if not tolerant:
                print(f"\nERROR in convert_md_to_html: {str(e)}")
                print("\nDetails:")
                import traceback
                traceback.print_exc()
                raise
            else:
                error_msg = f"File processing error: {str(e)}"
                self.error_report.append(error_msg)
                print(f"  WARNING: {error_msg}")
                return None, None

    def preview_post(self, html_content, title):
        """Show a preview of the post in the browser"""
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html_content)
            temp_path = f.name
        
        print(f"\nOpening preview for: {title}")
        webbrowser.open('file://' + temp_path)
        
        return temp_path

    def git_publish(self):
        """THIS METHOD IS DISABLED - Git operations are now manual"""
        print("Automatic git publishing is disabled - please commit and push changes manually.")
        return False

    def process_single_file(self, filename, update_indexes=True):
        """Process a single markdown file"""
        md_path = self.published_dir / filename
        
        if not md_path.exists():
            print(f"\nERROR: Markdown file not found: {md_path}")
            return False
            
        # Check if file has changed
        if not self._has_file_changed(md_path):
            print(f"  No changes detected in {filename}, skipping...")
            
            # We still need the metadata for the index updates
            post = frontmatter.load(md_path)
            metadata = post.metadata
            metadata['slug'] = metadata.get('slug', md_path.stem)
            
            # Add to processed posts for index updates
            self.processed_posts.append(metadata)
            return True
            
        print(f"\nProcessing {filename}...")
        
        try:
            # Read metadata first to get slug
            post = frontmatter.load(md_path)
            slug = post.metadata.get('slug', md_path.stem)
            print(f"  Found slug: {slug}")
            
            # Convert markdown to HTML with error tolerance
            html_content, metadata = self.convert_md_to_html(md_path, tolerant=True)
            
            if not html_content or not metadata:
                print(f"  ERROR: Failed to process {filename}")
                for error in self.error_report:
                    print(f"    - {error}")
                return False
                
            # Add slug to metadata if not present
            metadata['slug'] = slug
            
            # Create the HTML file
            output_filename = f"{slug}.html"
            output_path = self.root_dir / 'blog' / output_filename
            
            # Ensure blog directory exists
            output_path.parent.mkdir(exist_ok=True)
            
            # Save the HTML file and track it
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.modified_files.append(output_path)
            
            # Add to processed posts for index updates
            self.processed_posts.append(metadata)
            
            print(f"  Successfully processed {filename} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"\nERROR processing {filename}: {str(e)}")
            return False

    def process_all_files(self):
        """Process all markdown files in the published directory"""
        print("\nScanning for markdown files in published directory...")
        md_files = list(self.published_dir.glob('*.md'))
        
        if not md_files:
            print("No markdown files found!")
            return False
            
        print(f"Found {len(md_files)} markdown files.")
        
        success_count = 0
        for md_file in md_files:
            if self.process_single_file(md_file.name, update_indexes=False):
                success_count += 1
                
        print(f"\nSuccessfully processed {success_count} out of {len(md_files)} files")
        return success_count > 0

    def update_indexes(self):
        """Update blog index views"""
        if not self.processed_posts:
            print("No posts to update in indexes.")
            return
            
        print("\nUpdating blog indexes...")
        
        # Update chronological view
        self._update_chronological_view()
        
        # Update category view
        self.update_category_view()
        
        print("Indexes updated successfully.")

    def publish(self, file_or_all=None):
        """Main publish method - process one file or all files"""
        print("\n=== Starting Blog Publishing Process ===")
        
        # Process files
        if file_or_all == 'all':
            success = self.process_all_files()
        elif file_or_all:
            # Process single file
            success = self.process_single_file(file_or_all)
        else:
            print("No file specified. Use 'all' to process all files.")
            return False
            
        if not success:
            print("\nProcessing failed. No changes will be published.")
            return False
            
        # Update indexes
        self.update_indexes()
        
        # Save file hashes
        self._save_hashes()
        
        # Preview the changes
        if self.modified_files:
            print("\n=== Files Modified ===")
            for file in self.modified_files:
                print(f"  - {file}")
                
            # Show preview for HTML files
            html_files = [f for f in self.modified_files if str(f).endswith('.html') and 'blog/' in str(f)]
            if html_files:
                preview_file = html_files[0]  # Preview first HTML file
                with open(preview_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                temp_file = self.preview_post(html_content, str(preview_file))
                
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
                print("\nPreview opened in your browser.")
                print("\nGeneration completed - no automatic git commit will be performed.")
                print("\nModified files that need to be committed manually:")
                for file in self.modified_files:
                    print(f"  - {file}")
            else:
                print("\nNo HTML blog files were modified, but other files were.")
                print("Changes completed - no automatic git commit will be performed.")
                print("\nModified files that need to be committed manually:")
                for file in self.modified_files:
                    print(f"  - {file}")
            
            return True
        else:
            print("\nNo files were modified.")
            return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 create-pages.py <markdown-filename> OR all")
        sys.exit(1)
    
    try:
        publisher = BlogPublisher()
        
        if sys.argv[1] == 'all':
            publisher.publish('all')
        else:
            publisher.publish(sys.argv[1])
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()