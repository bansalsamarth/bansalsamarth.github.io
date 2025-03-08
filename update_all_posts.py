#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import subprocess

def main():
    """Update all blog posts to use the new template."""
    print("Starting blog update process...")
    root_dir = Path(__file__).parent.resolve()
    
    # Get a list of all markdown files in the published directory
    published_dir = root_dir / "SamarthBlog" / "published"
    md_files = list(published_dir.glob('*.md'))
    
    if not md_files:
        print("No markdown files found in the published directory.")
        return
    
    print(f"Found {len(md_files)} markdown files. Processing...")
    
    # Process each file
    for md_file in md_files:
        print(f"\nProcessing {md_file.name}")
        
        # Run create-pages.py with the file
        try:
            result = subprocess.run(
                ['python3', 'create-pages.py', md_file.name],
                cwd=root_dir,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"  Success: {md_file.name}")
            
            # Print verbose output if requested
            if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
                print(result.stdout)
                
        except subprocess.CalledProcessError as e:
            print(f"  ERROR processing {md_file.name}: {e}")
            print(e.stdout)
            print(e.stderr)
    
    print("\nUpdate process completed!")

if __name__ == "__main__":
    main()