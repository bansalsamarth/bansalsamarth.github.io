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
        
        # Load template once
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()

    def get_drafts(self):
        """Get list of draft posts"""
        drafts = []
        for file in self.published_dir.glob('*.md'):
            try:
                post = frontmatter.load(file)
                # Convert date string to datetime object for consistent sorting
                date_str = post.metadata.get('date_published', '')
                try:
                    date = datetime.datetime.strptime(date_str, "%d %B, %Y")
                except (ValueError, TypeError):
                    date = datetime.datetime.fromtimestamp(0)  # Default to epoch if invalid date
                    
                drafts.append({
                    'title': post.metadata.get('title', file.stem),
                    'slug': post.metadata.get('slug', file.stem),
                    'date': date_str,  # Keep original string for display
                    'sort_date': date,  # Add date object for sorting
                    'tags': post.metadata.get('tags', []),
                    'content': post.content
                })
            except Exception as e:
                print(f"Error loading {file}: {e}")
        return sorted(drafts, key=lambda x: x['sort_date'], reverse=True)

    def get_draft(self, slug):
        """Get specific draft content by slug"""
        try:
            # First try by direct slug match
            for file in self.published_dir.glob('*.md'):
                post = frontmatter.load(file)
                if post.metadata.get('slug') == slug:
                    return {
                        'title': post.metadata.get('title', ''),
                        'content': post.content,
                        'tags': post.metadata.get('tags', []),
                        'date': post.metadata.get('date_published', ''),
                        'slug': slug
                    }
            return None
        except Exception as e:
            print(f"Error loading draft {slug}: {e}")
            return None

    def preview_post(self, content, metadata=None):
        """Generate HTML preview using actual blog template"""
        if metadata is None:
            metadata = {}
            
        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.extra'
            ]
        )
        
        # Read template if not already loaded
        if not hasattr(self, 'template'):
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self.template = f.read()
        
        # Start with template
        html = self.template
        
        # Basic replacements
        basic_replacements = {
            '$lang$': 'en',
            '$dir$': 'ltr',
            '$title$': metadata.get('title', ''),
            '$pagetitle$': metadata.get('title', ''),
            '$author$': 'Samarth Bansal',
            '$author-meta$': 'Samarth Bansal',
            '$date_published$': metadata.get('date_published', ''),
            '$body$': html_content,
        }
        
        for key, value in basic_replacements.items():
            html = html.replace(key, value)
        
        # Handle conditional blocks
        patterns_to_remove = [
            r'\$if\(title-prefix\)\$.*?\$endif\$',
            r'\$if\(keywords\)\$.*?\$endif\$',
            r'\$if\(description-meta\)\$.*?\$endif\$',
            r'\$if\(math\)\$.*?\$endif\$',
            r'\$for\(keywords\)\$.*?\$endfor\$',
            r'\$for\(header-includes\)\$.*?\$endfor\$',
            r'\$for\(include-after\)\$.*?\$endfor\$',
            r'\$if\(toc\)\$.*?\$endif\$',
            r'\$if\(excerpt\)\$.*?\$endif\$'
        ]
        
        for pattern in patterns_to_remove:
            html = re.sub(pattern, '', html, flags=re.DOTALL)
        
        # Clean up any remaining template variables
        html = re.sub(r'\$[^$]+\$', '', html)
        
        # Ensure CSS path is correct for preview
        html = html.replace('href="../css/', 'href="/css/')

        
        return html

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
        # Get the draft
        draft = self.get_draft(slug)
        if not draft:
            raise ValueError(f"Draft not found: {slug}")
            
        # Convert to HTML
        html_content = self.preview_post(draft['content'], {
            'title': draft['title'],
            'date_published': draft['date'],
            'tags': draft['tags']
        })
        
        # Save HTML
        output_path = self.root_dir / 'blog' / f"{slug}.html"
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Update index
        self.update_index({
            'title': draft['title'],
            'slug': slug,
            'date_published': draft['date'],
            'tags': draft['tags']
        })
        
        # Git operations
        try:
            subprocess.run(['git', 'add', str(output_path)], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'add', str(self.blog_index_path)], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f"Publish post: {draft['title']}"], cwd=self.root_dir, check=True)
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

    def parse_index(self, content):
        """Parse the index HTML into structured data"""
        soup = BeautifulSoup(content, 'html.parser')
        categories = {}
        
        for h3 in soup.find_all('h3'):
            category = h3.text.strip()
            posts = []
            
            # Get all posts in this category
            current = h3.find_next()
            while current and current.name != 'h3':
                if current.name == 'p':
                    link = current.find('a')
                    if link:
                        posts.append({
                            'title': link.text.strip(),
                            'url': link['href'],
                            'slug': link['href'].split('/')[-1].replace('.html', ''),
                            'date': current.text.split('—')[1].strip() if '—' in current.text else ''
                        })
                current = current.find_next()
                
            categories[category] = posts
        
        return categories

    def update_index_structure(self, new_structure):
        """Update the index with new structure"""
        # Create new index HTML
        html = []
        for category, posts in new_structure.items():
            html.append(f'<h3>{category}</h3>\n\n')
            for post in posts:
                html.append(f'<p><a href="{post["url"]}">{post["title"]}</a> — {post["date"]}</p>\n')
            html.append('<hr>\n\n')
        
        # Save the new index
        with open(self.blog_index_path, 'w', encoding='utf-8') as f:
            f.write(''.join(html))

    def delete_post(self, slug):
        """Delete a post and remove it from index"""
        # Delete HTML file
        post_path = self.root_dir / 'blog' / f'{slug}.html'
        if post_path.exists():
            post_path.unlink()
        
        # Delete markdown file
        md_path = self.published_dir / f'{slug}.md'
        if md_path.exists():
            md_path.unlink()
        
        # Remove from index
        self.remove_from_index(slug)
        
        # Git commit
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f'Delete post: {slug}'], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'push'], cwd=self.root_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")

    def update_categories(self, new_categories):
        """Update category definitions"""
        self.categories = new_categories['categories']
        self.category_map = new_categories['category_map']
        
        # Save to config file
        config = {
            'categories': self.categories,
            'category_map': self.category_map
        }
        with open(self.root_dir / 'blog_config.json', 'w') as f:
            json.dump(config, f, indent=2)

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
        'date_published': datetime.datetime.now().strftime("%d %B, %Y"),
        'tags': request.form.getlist('tags[]')
    }
    html = blog_manager.preview_post(content, metadata)
    return html

@app.route('/draft/<slug>')
def get_draft(slug):
    draft = blog_manager.get_draft(slug)
    if draft:
        return jsonify(draft)
    return jsonify({'error': 'Draft not found'}), 404

@app.route('/save', methods=['POST'])
def save():
    title = request.form.get('title')
    content = request.form.get('content')
    metadata = {
        'tags': request.form.getlist('tags[]')
    }
    
    try:
        slug = blog_manager.save_draft(title, content, metadata)
        return jsonify({
            'success': True, 
            'slug': slug,
            'message': 'Draft saved successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })

@app.route('/publish/<slug>', methods=['POST'])
def publish(slug):
    try:
        success = blog_manager.publish_post(slug)
        if success:
            return jsonify({
                'success': True,
                'message': 'Post published successfully!'
            })
        return jsonify({
            'success': False,
            'error': 'Failed to publish post'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Add this route to serve static files
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('../css', filename)

@app.route('/api/index')
def get_index():
    """Get the current index structure"""
    try:
        with open(blog_manager.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the index into a structured format
        categories = blog_manager.parse_index(content)
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/index', methods=['POST'])
def update_index():
    """Update the index structure"""
    try:
        new_structure = request.json
        blog_manager.update_index_structure(new_structure)
        return jsonify({
            'success': True,
            'message': 'Index updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all categories and their metadata"""
    return jsonify({
        'categories': blog_manager.categories,
        'category_map': blog_manager.category_map
    })

@app.route('/api/categories', methods=['POST'])
def update_categories():
    """Update categories and their mappings"""
    try:
        new_categories = request.json
        blog_manager.update_categories(new_categories)
        return jsonify({
            'success': True,
            'message': 'Categories updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/post/<slug>', methods=['DELETE'])
def delete_post(slug):
    """Delete a post and remove it from index"""
    try:
        blog_manager.delete_post(slug)
        return jsonify({
            'success': True,
            'message': 'Post deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)