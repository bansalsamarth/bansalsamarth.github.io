#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import http.server
import socketserver
import webbrowser
import markdown
import frontmatter
import tempfile
import shutil
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PreviewServer:
    def __init__(self, port=8000):
        self.root_dir = Path(__file__).parent.resolve()
        self.template_path = self.root_dir / "templates" / "post-template.html"
        self.port = port
        self.temp_dir = None
        self._setup_temp_dir()

    def _setup_temp_dir(self):
        """Create a temporary directory with necessary files"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Copy CSS directory
        if (self.root_dir / "css").exists():
            shutil.copytree(self.root_dir / "css", self.temp_dir / "css")
        
        # Create blog directory
        (self.temp_dir / "blog").mkdir(exist_ok=True)

    def convert_preview(self, md_path):
        """Convert markdown to HTML for preview"""
        try:
            # Read markdown with frontmatter
            post = frontmatter.load(md_path)
            
            # Convert markdown to HTML
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
            
            # Read template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # Fill template
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
            
            # Remove remaining template variables
            html = re.sub(r'\$if\([^$]+\)\$.*?\$endif\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$for\([^$]+\)\$.*?\$endfor\$', '', html, flags=re.DOTALL)
            html = re.sub(r'\$[^$]+\$', '', html)
            
            # Save the preview
            output_path = self.temp_dir / "blog" / "preview.html"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return output_path

        except Exception as e:
            print(f"\nError converting markdown: {e}")
            return None

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, preview_server, md_path):
        self.preview_server = preview_server
        self.md_path = md_path

    def on_modified(self, event):
        if event.src_path == str(self.md_path):
            print("\nFile changed, updating preview...")
            self.preview_server.convert_preview(self.md_path)
            print("Preview updated!")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 preview.py <markdown-file>")
        sys.exit(1)

    md_path = Path(sys.argv[1]).resolve()
    if not md_path.exists():
        print(f"File not found: {md_path}")
        sys.exit(1)

    # Initialize server
    preview = PreviewServer()
    
    # Initial conversion
    output_path = preview.convert_preview(md_path)
    if not output_path:
        print("Failed to convert markdown")
        sys.exit(1)

    # Set up file watcher
    observer = Observer()
    handler = MarkdownHandler(preview, md_path)
    observer.schedule(handler, str(md_path.parent), recursive=False)
    observer.start()

    # Start server
    os.chdir(preview.temp_dir)
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", preview.port), handler) as httpd:
            preview_url = f"http://localhost:{preview.port}/blog/preview.html"
            print(f"\nPreview server started at {preview_url}")
            print("This preview will update automatically when you save changes")
            print("Press Ctrl+C to stop the preview server")
            
            # Open in browser
            webbrowser.open(preview_url)
            
            # Start serving
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server...")
        observer.stop()
        observer.join()
        shutil.rmtree(preview.temp_dir)
        print("Preview server stopped")
    except Exception as e:
        print(f"Server error: {e}")
        observer.stop()
        observer.join()
        shutil.rmtree(preview.temp_dir)

if __name__ == '__main__':
    main()