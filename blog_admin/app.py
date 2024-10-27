#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import markdown
import frontmatter
from pathlib import Path
import datetime
import subprocess
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tempfile
import shutil
from slugify import slugify
import yaml
import os

app = Flask(__name__)

class BlogManager:
    def __init__(self):
        # Get the root directory (blog_admin's parent directory)
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.obsidian_dir = self.root_dir / "SamarthBlog"
        self.published_dir = self.obsidian_dir / "published"
        self.template_path = self.root_dir / "templates" / "post-template.html"
        self.blog_index_path = self.root_dir / "pages" / "blog.html"
        
        print(f"Root dir: {self.root_dir}")
        print(f"Template path: {self.template_path}")
        
        self.categories = [
            "Writing", "Dating", "Personal", "Work and Career",
            "Journalism", "Politics", "Learning", "Health"
        ]
        
        # Verify paths
        self._verify_paths()
    
    def _verify_paths(self):
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found at {self.template_path}")
        if not self.blog_index_path.exists():
            raise FileNotFoundError(f"Blog index not found at {self.blog_index_path}")
        if not self.published_dir.exists():
            raise FileNotFoundError(f"Published directory not found at {self.published_dir}")

    def preview_post(self, content, metadata=None):
        """Generate HTML preview of the post"""
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                content,
                extensions=[
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.tables',
                    'markdown.extensions.extra'
                ]
            )
            
            # Read template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            if metadata is None:
                metadata = {}
            
            # Current date if not provided
            if 'date_published' not in metadata:
                metadata['date_published'] = datetime.datetime.now().strftime("%d %B, %Y")
                
            # Create HTML
            html = template
            # Replace simple variables first
            html = html.replace('$title$', metadata.get('title', ''))
            html = html.replace('$author$', 'Samarth Bansal')
            html = html.replace('$date_published$', metadata['date_published'])
            html = html.replace('$body$', html_content)
            
            # Remove conditional blocks and their content
            html = re.sub(r'\$if\([^$]+\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$for\([^$]+\)\$.*?\$endfor\$', '', html, flags=re.DOTALL)
            # Remove any remaining template variables
            html = re.sub(r'\$[^$]+\$', '', html)
            
            return html
            
        except Exception as e:
            print(f"Preview error: {e}")
            return f"Error generating preview: {str(e)}"

    def save_draft(self, title, content, metadata):
        """Save post as markdown with frontmatter"""
        slug = slugify(title)
        
        # Prepare frontmatter
        post_metadata = {
            'title': title,
            'slug': slug,
            'date_published': datetime.datetime.now().strftime("%d %B, %Y"),
            'tags': metadata.get('tags', []),
            'author': 'Samarth Bansal'
        }
        
        # Create post with frontmatter
        post = frontmatter.Post(content, **post_metadata)
        
        # Save to published directory
        output_path = self.published_dir / f"{slug}.md"
        with open(output_path, 'wb') as f:
            frontmatter.dump(post, f)
            
        return slug

    def publish_post(self, slug):
        """Convert markdown to HTML and update index"""
        md_path = self.published_dir / f"{slug}.md"
        if not md_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_path}")
            
        # Load the markdown file
        post = frontmatter.load(md_path)
        
        # Convert to HTML
        html_content = self.preview_post(post.content, post.metadata)
        
        # Save HTML
        output_path = self.root_dir / 'blog' / f"{slug}.html"
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Update index
        self.update_index(post.metadata)
        
        # Git operations
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f"Publish post: {slug}"], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'push'], cwd=self.root_dir, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False

    def update_index(self, metadata):
        """Update blog index page"""
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_entry = f'\n      <p><a href="../blog/{metadata["slug"]}.html">{metadata["title"]}</a> — {metadata["date_published"]}</p>\n'
        
        category = self.get_category_from_tags(metadata.get('tags', []))
        category_pattern = f'<h3>{category}</h3>'
        
        if category_pattern in content:
            pos = content.find(category_pattern) + len(category_pattern)
            content = content[:pos] + new_entry + content[pos:]
        else:
            new_section = f'\n      <h3>{category}</h3>{new_entry}\n      <hr>\n'
            last_hr = content.rfind('<hr>')
            content = content[:last_hr] + new_section + content[last_hr:]
            
        with open(self.blog_index_path, 'w', encoding='utf-8') as f:
            f.write(content)

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

    def get_drafts(self):
        """Get list of draft posts"""
        drafts = []
        for file in self.published_dir.glob('*.md'):
            try:
                post = frontmatter.load(file)
                drafts.append({
                    'title': post.metadata.get('title', file.stem),
                    'slug': post.metadata.get('slug', file.stem),
                    'date': post.metadata.get('date_published', ''),
                    'tags': post.metadata.get('tags', [])
                })
            except Exception as e:
                print(f"Error loading {file}: {e}")
        return drafts

blog_manager = BlogManager()

@app.route('/')
def index():
    drafts = blog_manager.get_drafts()
    return render_template('editor.html', 
                         categories=blog_manager.categories,
                         drafts=drafts)

@app.route('/preview', methods=['POST'])
def preview():
    content = request.form.get('content', '')
    metadata = {
        'title': request.form.get('title', ''),
        'tags': request.form.getlist('tags[]')
    }
    html = blog_manager.preview_post(content, metadata)
    return html

@app.route('/save', methods=['POST'])
def save():
    title = request.form.get('title')
    content = request.form.get('content')
    metadata = {
        'tags': request.form.getlist('tags[]')
    }
    
    try:
        slug = blog_manager.save_draft(title, content, metadata)
        return jsonify({'success': True, 'slug': slug})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/publish/<slug>', methods=['POST'])
def publish(slug):
    try:
        success = blog_manager.publish_post(slug)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)