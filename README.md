# Samarth Bansal's Personal Website

This repository contains the code for my personal website and blog. The site is built using a custom static site generator that converts markdown files to HTML using templates.

## System Overview

The website is organized as follows:

- **SamarthBlog/published/**: Contains all blog posts as markdown files
- **SamarthBlog/migrations/**: Blog posts to be migrated
- **blog/**: Contains the generated HTML blog posts
- **pages/**: Contains static pages like blog index, about, etc.
- **templates/**: Contains HTML templates for posts and pages
- **css/**: Contains stylesheets (style.css for the new design)
- **assets/**: Contains images and other static assets

## Available Commands

### Blog Post Management

#### Creating a New Blog Post

```bash
python3 new_post.py "Your Post Title"
```

Creates a new markdown file in `SamarthBlog/published/` with the date and slug derived from the title. The file includes pre-filled frontmatter with:
- Title
- Publication date (current date)
- Author name
- Slug
- Empty tags array

The file will be automatically opened in your default editor.

#### Publishing Blog Posts

```bash
python3 create-pages.py all
```

Processes all markdown files in the `SamarthBlog/published/` directory and generates HTML files in the `blog/` directory.

To publish a single post:

```bash
python3 create-pages.py filename.md
```

#### Synchronizing Blog Posts

If you delete markdown files from the `SamarthBlog/published/` directory, you can remove the corresponding HTML files:

```bash
python3 sync_posts.py
```

Use the `--force` flag to skip confirmation prompts:

```bash
python3 sync_posts.py --force
```

#### Creating Markdown Files for Existing HTML Posts

```bash
python3 create_missing_md.py
```

Scans the `blog/` directory for HTML files that don't have corresponding markdown files in `SamarthBlog/published/` and creates them, extracting title, date, and content.

#### Updating All Posts with New Template

```bash
python3 update_all_posts.py
```

Reprocesses all markdown files with the latest template.

### Page Management

#### Creating a New Page

```bash
python3 new_page.py "Page Title" [filename.html]
```

Creates a new HTML page in the `pages/` directory using the site's base design and styling.

### Design Updates

#### Fixing Blog Page Styling

```bash
python3 update_design.py
```

Fixes styling and structure issues in the blog index page.

## Blog System Architecture

### Templates

The system uses two main templates:

1. **templates/base.html**: The main site template with Jinja-style placeholders (`{{ }}`)
2. **templates/post-template.html**: Blog post template with variable placeholders (`$title$`, `$body$`, etc.)

### Blog Organization

The blog is organized in two views:

1. **Chronological**: All posts ordered by date
2. **By Category**: Posts grouped by category (derived from tags)

Categories are mapped in the `get_category_from_tags` function in `create-pages.py`.

### Styling

The site uses a clean, modern design with:

- Responsive layout
- Subtle animations and hover effects
- Consistent typography and spacing
- Mobile-friendly design

## Development Workflow

1. Create new posts using `new_post.py`
2. Edit markdown files in `SamarthBlog/published/`
3. Preview changes locally by running `create-pages.py`
4. Create new pages using `new_page.py` when needed
5. Update design elements in `css/style.css`

## Troubleshooting

- If posts aren't showing the new design, run `update_all_posts.py`
- If blog index styling is inconsistent, run `update_design.py`
- If some HTML posts don't have markdown files, run `create_missing_md.py`

---

## Notes on Updating the Design

If you modify the templates or CSS, follow these steps to update the site:

1. Edit the templates in `templates/`
2. Edit CSS in `css/style.css`
3. Run `python3 update_all_posts.py` to reprocess all posts
4. Run `python3 update_design.py` to fix any blog index issues

---

Last updated: April 4, 2025