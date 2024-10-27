#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import re
from pathlib import Path
import frontmatter
import subprocess
import markdown

class BlogPublisher:
    def __init__(self):
        self.root_dir = Path(__file__).parent.resolve()
        self.obsidian_dir = self.root_dir / "SamarthBlog"
        self.published_dir = self.obsidian_dir / "published"
        self.template_path = self.root_dir / "templates" / "post-template.html"
        self.blog_index_path = self.root_dir / "pages" / "blog.html"
        self.modified_files = []  # Track files we modify

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

    def add_to_blog_index(self, title, slug, date_published, tags):
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Store original content to check if it changed
        original_content = content

        category = self.get_category_from_tags(tags)
        date_obj = datetime.strptime(date_published, "%d %B, %Y")
        formatted_date = date_obj.strftime("%B %Y")
        
        new_entry = f'\n      <p><a href="../blog/{slug}.html">{title}</a> — {formatted_date}</p>\n'
        
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
            "Writing": ["Blog", "Writing"],
            "Dating": ["Dating", "Romance"],
            "Personal": ["Personal", "Life"],
            "Work and Career": ["Work", "Career"],
            "Journalism": ["Journalism", "Media"],
            "Politics": ["Politics", "Public Affairs"],
            "Learning": ["Learning", "Education"],
            "Health": ["Health", "Fitness"]
        }
        
        if not tags:
            return "Personal"
            
        for category, tag_list in category_map.items():
            if any(tag in tags for tag in tag_list):
                return category
                
        return "Personal"

    def convert_md_to_html(self, md_path):
        """Process markdown file and create HTML using your template"""
        print("  Reading markdown file...")
        try:
            # Read the markdown file with frontmatter
            post = frontmatter.load(md_path)
            print("  Successfully loaded frontmatter")
            print(f"  Metadata found: {list(post.metadata.keys())}")
            
            # Convert markdown content to HTML
            class CustomRenderer(markdown.extensions.Extension):
                def extendMarkdown(self, md):
                    md.parser.blockprocessors.deregister('paragraph')

            print("  Converting markdown to HTML...")
            print("  Content preview (first 200 chars):")
            print("  ---")
            print(post.content[:200])
            print("  ---")
            
            
            print("  Attempting markdown conversion with basic settings...")
            html_content = markdown.markdown(post.content)
            print("  Basic conversion successful, trying with full extensions...")
            
            # Now try full conversion
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
            print("  Full markdown conversion successful")
        
            print("  Reading template...")
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            print("  Template loaded successfully")

            print("  Creating HTML document...")
            # Create a clean HTML document
            html = template\
                .replace('$if(title)$', '')\
                .replace('$endif$', '')\
                .replace('$title$', post.metadata.get('title', ''))\
                .replace('$for(author)$', '')\
                .replace('$endfor$', '')\
                .replace('$author$', post.metadata.get('author', ''))\
                .replace('$if(date_published)$', '')\
                .replace('$date_published$', post.metadata.get('date_published', ''))\
                .replace('$body$', html_content)

            # Remove all remaining template variables and their conditional blocks
            html = re.sub(r'\$if\([^$]+\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$for\([^$]+\)\$.*?\$endfor\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$[^$]+\$', '', html)
            
            # Remove the TOC navigation
            html = re.sub(r'<nav id="TOC"[^>]*>.*?</nav>', '', html, flags=re.DOTALL)
            
            # Clean up any multiple newlines
            html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)
            print("  HTML document created successfully")
            
            return html, post.metadata
            
        except Exception as e:
            print(f"\nERROR in convert_md_to_html: {str(e)}")
            print("\nDetails:")
            import traceback
            traceback.print_exc()
            raise

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

    def publish(self, filename):
        print("\nStarting publication process...")
        
        md_path = self.published_dir / filename
        print(f"Looking for markdown file at: {md_path}")
        
        if not md_path.exists():
            print(f"\nERROR: Markdown file not found!")
            print(f"Expected location: {md_path}")
            print(f"Make sure '{filename}' is in your SamarthBlog/published/ directory")
            sys.exit(1)
            
        try:
            # Read metadata first to get slug
            print("Reading initial metadata...")
            post = frontmatter.load(md_path)
            slug = post.metadata.get('slug', md_path.stem)
            print(f"Found slug: {slug}")
            
            # Safety checks
            self.check_existing_post(slug)
            self.check_slug_in_index(slug)
            
            print(f"Converting {filename}...")
            
            # Convert markdown to HTML
            html_content, metadata = self.convert_md_to_html(md_path)
            
            # Create the HTML file
            output_filename = f"{slug}.html"
            output_path = self.root_dir / 'blog' / output_filename
            
            # Ensure blog directory exists
            output_path.parent.mkdir(exist_ok=True)
            
            print(f"Writing HTML file to {output_path}...")
            
            # Save the HTML file and track it
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.modified_files.append(output_path)
            
            print("Updating blog index...")
            
            # Update blog index (this method will track if the index is modified)
            self.add_to_blog_index(
                metadata.get('title'),
                slug,
                metadata.get('date_published'),
                metadata.get('tags', [])
            )
            
            # Git publish
            print("Publishing to git...")
            if self.git_publish():
                print(f"\nSuccessfully published {filename}")
                print(f"View at: blog/{output_filename}")
            else:
                print("\nPublishing completed but git operations failed")
                print("Modified files that need to be pushed:")
                for file in self.modified_files:
                    print(f"  - {file}")
                    
        except Exception as e:
            print(f"\nERROR during publication: {str(e)}")
            sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 create-pages.py <markdown-filename>")
        sys.exit(1)
    
    try:
        publisher = BlogPublisher()
        publisher.publish(sys.argv[1])
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()