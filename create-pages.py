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
        self.blog_index_path = self.root_dir / "pages" / "blog.html"
        self.archive_index_path = self.root_dir / "pages" / "archive.html"
        self.modified_files = []  # Track files we modify
        self.file_hashes = {}  # Store file hashes to detect changes
        self.processed_posts = []  # Store metadata of processed posts
        self.error_report = []  # Store markdown errors
        
        # Create archive index if it doesn't exist
        if not self.archive_index_path.exists():
            self._create_archive_index()
            
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

    def _create_archive_index(self):
        """Create a new archive index page"""
        archive_html = """<!DOCTYPE html>
<html lang="en">
<head>
<link href="../css/mvp.css" rel="stylesheet"/>
<meta charset="utf-8"/>
<meta content="Website of journalist Samarth Bansal" name="Samarth Bansal"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Samarth's Blog Archive</title>
</head>
<body>
<main>
<h1>Blog Archive</h1>
<span>
<a href="../index.html"> &lt; Home </a>
<a href="../pages/blog.html"> &lt; Blog Categories </a>
</span>
<hr/>
<div class="post-list">
<!-- Posts will be listed here in chronological order -->
</div>
</main>
</body>
</html>"""
        with open(self.archive_index_path, 'w', encoding='utf-8') as f:
            f.write(archive_html)
        self.modified_files.append(self.archive_index_path)

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
    
    def update_archive_index(self):
        """Update the archive index with all processed posts"""
        # Skip if no posts were processed
        if not self.processed_posts:
            return
            
        # Sort posts by date, newest first
        sorted_posts = sorted(
            self.processed_posts, 
            key=lambda x: datetime.strptime(x['date_published'], "%d %B, %Y"),
            reverse=True
        )
        
        # Read current archive content
        with open(self.archive_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find where to insert posts
        insert_point = content.find('<div class="post-list">') + len('<div class="post-list">')
        
        # Generate HTML for all posts
        posts_html = "\n<!-- Posts listed in chronological order -->\n"
        
        # Group by year
        posts_by_year = {}
        for post in sorted_posts:
            year = datetime.strptime(post['date_published'], "%d %B, %Y").year
            if year not in posts_by_year:
                posts_by_year[year] = []
            posts_by_year[year].append(post)
            
        # Generate HTML for each year
        for year in sorted(posts_by_year.keys(), reverse=True):
            posts_html += f"\n<h2>{year}</h2>\n"
            for post in posts_by_year[year]:
                date = datetime.strptime(post['date_published'], "%d %B, %Y")
                formatted_date = date.strftime("%B %d")
                posts_html += f"<p><a href=\"../blog/{post['slug']}.html\">{post['title']}</a> — {formatted_date}</p>\n"
        
        # Replace content
        new_content = content[:insert_point] + posts_html + content[insert_point:]
        
        # Only write if content has changed
        if new_content != content:
            with open(self.archive_index_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            self.modified_files.append(self.archive_index_path)

    def add_to_blog_index(self, title, slug, date_published, tags):
        """Add the post to the blog index under its category"""
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Store original content to check if it changed
        original_content = content

        category = self.get_category_from_tags(tags)
        date_obj = datetime.strptime(date_published, "%d %B, %Y")
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
            
            # Create a clean HTML document
            html = template\
                .replace('$if(title)$', '')\
                .replace('$endif$', '')\
                .replace('$title$', post.metadata.get('title', ''))\
                .replace('$for(author)$', '')\
                .replace('$endfor$', '')\
                .replace('$author$', post.metadata.get('author', ''))\
                .replace('$if(date_published)$', '')\
                .replace('$date_published$', post.metadata.get('date_published', ''))
                
            # Handle excerpt if present
            if 'excerpt' in post.metadata:
                html = html.replace('$if(excerpt)$', '')
                html = html.replace('$endif$', '')
                html = html.replace('$excerpt$', post.metadata.get('excerpt', ''))
            else:
                html = re.sub(r'\$if\(excerpt\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
                
            # Insert the content
            html = html.replace('$body$', html_content)

            # Remove all remaining template variables and their conditional blocks
            html = re.sub(r'\$if\([^$]+\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$for\([^$]+\)\$.*?\$endfor\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$[^$]+\$', '', html)
            
            # Remove the TOC navigation
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
        """Commit and push only the modified files"""
        try:
            # Convert Path objects to strings for git commands
            files_to_commit = [str(f.relative_to(self.root_dir)) for f in self.modified_files]
            
            if not files_to_commit:
                print("No files were modified.")
                return True

            print("\nCommitting the following files:")
            for file in files_to_commit:
                print(f"  - {file}")

            # Add specific files
            for file in files_to_commit:
                subprocess.run(['git', 'add', file], cwd=self.root_dir, check=True)

            # Commit with list of files in message
            commit_message = "Update blog: " + ", ".join(files_to_commit)
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.root_dir, check=True)
            
            # Push
            subprocess.run(['git', 'push'], cwd=self.root_dir, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
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
        """Update blog index and archive index"""
        if not self.processed_posts:
            print("No posts to update in indexes.")
            return
            
        print("\nUpdating blog indexes...")
        
        # Update category-based index
        for post in self.processed_posts:
            self.add_to_blog_index(
                post.get('title'),
                post.get('slug'),
                post.get('date_published'),
                post.get('tags', [])
            )
            
        # Update chronological archive
        self.update_archive_index()
        
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
                
                # Ask for confirmation before git publishing
                print("\nPreview opened in your browser.")
                confirm = input("Do you want to publish these changes? (y/N): ")
                
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
                if confirm.lower() != 'y':
                    print("Aborting publication...")
                    return False
        
            # Git publish
            print("\nPublishing changes to git...")
            if self.git_publish():
                print("\n=== Successfully published changes ===")
                return True
            else:
                print("\nPublishing completed but git operations failed")
                print("Modified files that need to be pushed:")
                for file in self.modified_files:
                    print(f"  - {file}")
                return False
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