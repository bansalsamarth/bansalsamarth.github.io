#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import re
import subprocess
from bs4 import BeautifulSoup  # pip install beautifulsoup4

class BlogIndexManager:
    def __init__(self):
        # Get the directory where the script is located
        self.root_dir = Path(os.getcwd()).resolve()  # This will be bansalsamarth.github.io
        print(f"Working directory: {self.root_dir}")
        
        # Set paths for index and blog directories
        self.blog_index_path = self.root_dir / "pages" / "blog.html"
        self.blog_dir = self.root_dir / "blog"
        
        # Verify paths exist
        if not self.blog_index_path.exists():
            raise FileNotFoundError(f"Blog index not found at {self.blog_index_path}")
        if not self.blog_dir.exists():
            raise FileNotFoundError(f"Blog directory not found at {self.blog_dir}")

    def remove_post(self, slug):
        """Remove a post from the index and delete its HTML file"""
        changes_made = False
        
        # Remove HTML file
        html_file = self.blog_dir / f"{slug}.html"
        if html_file.exists():
            html_file.unlink()
            print(f"Removed HTML file: {html_file}")
            changes_made = True
        else:
            print(f"HTML file not found: {html_file}")

        # Remove from index
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find and remove the entry
        pattern = f'<p><a href="../blog/{slug}.html">.*?</p>\n'
        new_content = re.sub(pattern, '', content)
        
        if new_content != content:
            with open(self.blog_index_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Removed {slug} from index")
            changes_made = True
        else:
            print(f"No entry found for {slug} in index")

        # Git commit if changes were made
        if changes_made:
            try:
                subprocess.run(['git', 'add', '.'], cwd=self.root_dir, check=True)
                subprocess.run(['git', 'commit', '-m', f"Remove post: {slug}"], cwd=self.root_dir, check=True)
                subprocess.run(['git', 'push'], cwd=self.root_dir, check=True)
                print("Changes committed and pushed")
            except subprocess.CalledProcessError as e:
                print(f"Git operation failed: {e}")
        else:
            print("No changes were made")

    def change_category(self, slug, new_category):
        """Move a post to a different category"""
        with open(self.blog_index_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Find the post entry
        link = soup.find('a', href=f"../blog/{slug}.html")
        if not link:
            print(f"Post {slug} not found in index")
            return

        # Get the entire <p> element
        entry = link.find_parent('p')
        if not entry:
            print("Entry structure not found")
            return

        # Remove from old category
        entry.extract()

        # Add to new category
        target_h3 = soup.find('h3', string=new_category)
        if not target_h3:
            print(f"Creating new category: {new_category}")
            # Create new category section
            new_section = soup.new_tag('div')
            new_section.append(soup.new_tag('h3'))
            new_section.h3.string = new_category
            new_section.append(entry)
            new_section.append(soup.new_tag('hr'))
            # Add before the last hr
            last_hr = soup.find_all('hr')[-1]
            last_hr.insert_before(new_section)
        else:
            # Add right after the h3
            target_h3.insert_after(entry)

        # Save changes
        with open(self.blog_index_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"Moved {slug} to category {new_category}")

        # Git commit
        try:
            subprocess.run(['git', 'add', '.'], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'commit', '-m', f"Move {slug} to {new_category}"], cwd=self.root_dir, check=True)
            subprocess.run(['git', 'push'], cwd=self.root_dir, check=True)
            print("Changes committed and pushed")
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Remove post:        python3 blog_index.py remove <slug>")
        print("  Change category:    python3 blog_index.py move <slug> <new-category>")
        sys.exit(1)

    try:
        manager = BlogIndexManager()
        command = sys.argv[1]

        if command == "remove":
            slug = sys.argv[2]
            manager.remove_post(slug)
        elif command == "move":
            if len(sys.argv) != 4:
                print("For move command: python3 blog_index.py move <slug> <new-category>")
                sys.exit(1)
            slug = sys.argv[2]
            new_category = sys.argv[3]
            manager.change_category(slug, new_category)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()