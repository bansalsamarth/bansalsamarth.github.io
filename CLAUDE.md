# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Samarth's personal blog/website built with a custom Python static site generator using Jinja2 templates. The site is deployed via GitHub Pages and serves from the `/docs` folder.

## Development Commands

- **Generate site**: `python generator.py` (outputs to `/docs` folder)
- **Generate journalism pages**: `python generate_journalism.py`
- **Development server**: `python -m http.server 8000` (serve from `/docs`)
- **Install dependencies**: `pip install jinja2 markdown python-frontmatter pytz python-dateutil`

## Architecture

- **Framework**: Custom Python static site generator
- **Templates**: Jinja2 (in `/templates` folder)
- **Content**: Markdown files with YAML frontmatter (in `/content`)
- **Styling**: CSS-in-HTML with CSS custom properties for theming
- **Deployment**: GitHub Pages serving from `/docs` folder
- **Repository**: https://github.com/bansalsamarth/bansalsamarth.github.io

## Content Structure

- `/content/posts/` - Blog posts
- `/content/essays/` - Long-form essays (currently "coming soon")
- `/content/micro/` - Microblog/notes (currently "coming soon") 
- `/content/evergreen/` - Living documents (currently "coming soon")
- `/journalism_links.csv` - External journalism portfolio data

## Key Files

- `config.py` - Site configuration and settings
- `generator.py` - Main site generator script
- `generate_journalism.py` - Journalism portfolio generator
- `templates/base.html` - Base template with navigation and styling
- `docs/` - Generated static site files (served by GitHub Pages)

## Design System

- Purple accent color: `rgb(93, 24, 220)` (light mode), `rgb(168, 132, 255)` (dark mode)
- Minimal, typography-focused design
- Dark/light mode support with system preference detection
- Responsive design with mobile breakpoints

## Deployment

1. Run `python generator.py` to build site
2. Commit changes: `git add -A && git commit -m "Update site"`
3. Push to GitHub: `git push origin main`
4. GitHub Pages automatically deploys from `/docs` folder
5. Live site: https://bansalsamarth.github.io

## Preserving Custom Files During Build

The generator automatically preserves certain files during rebuild:

**Auto-preserved:**
- `CNAME` (GitHub Pages custom domain)
- Any `.html` files in `/docs` root (except `index.html`)

**To preserve additional files/folders manually:**
Edit `generator.py` around line 242-268 and add your items to the lists:
```python
files_to_preserve = [
    'CNAME',  # GitHub Pages custom domain file
    'your-custom-page.html',        # Your custom HTML pages
    'robots.txt',                   # SEO files
    'sitemap.xml',                  # Sitemap
]

folders_to_preserve = [
    'assets',                       # Custom assets folder (already included)
    'uploads',                      # Upload directory
    'media',                        # Media files
    'custom-folder',                # Any custom directories
]
```

**Important:** Files in generated folders (`/posts/`, `/essays/`, etc.) are always regenerated and cannot be preserved.

## Coming Soon Sections

Currently showing "coming soon" messages with original code commented out:
- Essays (`/essays/`)
- Journalism (`/journalism/`) 
- Notes/Micro (`/micro/`)
- Evergreen (`/evergreen/`)

To activate any section, uncomment the original code in the respective template files.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.