# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is Samarth's personal blog/website built with a custom Python static site generator using Jinja2 templates. The site is deployed via GitHub Pages and serves from the `/docs` folder.

## Development Commands

The `./blog` helper script is the primary interface:

- **Create content**: `./blog new post|essay|journalism|note "Title"`
- **Preview locally**: `./blog preview` (builds + serves at localhost:8000)
- **Publish**: `./blog publish [optional message]` (builds + commits + pushes)

Lower-level commands:
- **Generate site**: `python generator.py build` (outputs to `/docs` folder)
- **Install dependencies**: `pip install -r requirements.txt` (project uses `venv/`)

A GitHub Action (`.github/workflows/build-site.yml`) rebuilds the site on every push, so content edits pushed without a local build still go live.

## Architecture

- **Framework**: Custom Python static site generator
- **Templates**: Jinja2 (in `/templates` folder)
- **Content**: Markdown files with YAML frontmatter (in `/content`)
- **Styling**: CSS-in-HTML with CSS custom properties for theming
- **Deployment**: GitHub Pages serving from `/docs` folder
- **Repository**: https://github.com/bansalsamarth/bansalsamarth.github.io

## Content Structure

- `/content/posts/` - Blog posts
- `/content/essays/` - Curated long-form essays (hosted markdown, custom HTML pages, or external links)
- `/content/journalism/` - Curated journalism entries (one markdown file per piece)
- `/content/micro/` - Notes/microblog (short, title-less, timestamped)
- `/content/evergreen/` - Living documents (currently "coming soon")
- `/content/images/` - Images copied to `/images/` on the site (reference as `/images/<name>`)
- `/journalism_links.csv` - Legacy journalism data (migrated to `/content/journalism/`; kept as archive)

### Curated entries (essays & journalism)

Essays and journalism are curations, not dumps. Each entry is a markdown file:
- `external_url` in frontmatter points to where the piece lives — an external site (`https://...`) or a custom HTML page hosted here (`/my-page.html`). Relative URLs are treated as internal (no ↗ marker).
- For external/hosted-HTML entries, the markdown **body is the context note** shown under the link on the listing page (why the piece matters).
- For essays written here as markdown, the body is the essay itself; use a `context:` frontmatter field for the listing note.
- Journalism entries also take a `publication:` field.
- Draft entries use `published: false`; flip to `true` after writing the context note.

## Key Files

- `blog` - Publishing helper script (new/preview/publish)
- `config.py` - Site configuration and settings
- `generator.py` - Main site generator script
- `content_processor.py` - Markdown/frontmatter parsing into ContentItem objects
- `templates/base.html` - Base template with navigation and styling
- `docs/` - Generated static site files (served by GitHub Pages)

## Design System

- Purple accent color: `rgb(93, 24, 220)` (light mode), `rgb(168, 132, 255)` (dark mode)
- Minimal, typography-focused design
- Dark/light mode support with system preference detection
- Responsive design with mobile breakpoints

## Deployment

1. Run `./blog publish` (builds, commits, pushes in one step)
2. GitHub Pages automatically deploys from `/docs` folder
3. Live site: https://www.samarthbansal.com

The GitHub Action also rebuilds `/docs` automatically after any push that changes content, as a safety net.

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

## Site Sections

Live sections: Blog (`/blog/`), Essays (`/essays/`), Journalism (`/journalism/`), Notes (`/micro/`), Contact (`/contact/`).

Still "coming soon" (original code commented out in its template): Evergreen (`/evergreen/`).

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.