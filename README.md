# Samarth's Blog - Static Site Generator

A modern, Python-based static site generator built with Mistune, Jinja2, and clean design principles.

## Features

- **Fast Markdown Processing**: Using Mistune for reliable markdown parsing
- **Template System**: Jinja2 templates with custom filters
- **Category System**: Organize posts with toggle views (All Posts / By Category)
- **URL Preservation**: Maintains existing URLs for backward compatibility
- **India Timezone**: Built-in Asia/Kolkata timezone support
- **Migration Tools**: Scripts to import existing content
- **Clean Design**: Purple accent colors with responsive layout
- **Auto-generation**: Create new content with proper frontmatter

## Quick Start

### Requirements

```bash
pip install -r requirements.txt
```

### Build the Site

```bash
python generator.py build
```

The generated site will be in the `output/` directory.

### Development Workflow

1. Add new content to `content/posts/`, `content/essays/`, or `content/pages/`
2. Run `python generator.py build` to regenerate
3. Open `output/index.html` in your browser

## Adding Content

### New Blog Post

```bash
python generator.py new post "My New Post Title"
```

This creates a new markdown file in `content/posts/` with proper frontmatter:

```yaml
---
title: "My New Post Title"
date: 2025-07-19
published: true
category: personal  # Add this manually if desired
---
```

### New Essay

```bash
python generator.py new essay "My Essay Title"
```

For external essays (published elsewhere), add the external URL:

```yaml
---
title: "My Essay Title"
date: 2025-07-19
published: true
external_url: "https://example.com/my-essay"
---
```

### New Page

```bash
python generator.py new page "About Me"
```

## Content Organization

### Directory Structure

```
content/
├── posts/          # Blog posts
├── essays/         # Essays & journalism
└── pages/          # Static pages
```

### Frontmatter Options

All content supports these frontmatter fields:

```yaml
---
title: "Post Title"           # Required
date: 2025-07-19             # Required (YYYY-MM-DD)
published: true              # Optional, defaults to true
category: journalism         # Optional, for categorization
slug: custom-url             # Optional, overrides auto-generated slug
external_url: "https://..."  # Optional, for external essays
---
```

### Categories

Posts are automatically categorized based on keywords in content. You can also manually set categories:

- `journalism` - Journalism and media posts
- `personal` - Personal thoughts and experiences  
- `tech` - Technology and programming
- `food` - Food and health content
- `uncategorized` - Default category

## URL Structure

The site generates clean URLs:

- Blog posts: `/posts/post-slug/`
- Essays: `/essays/essay-slug/`
- Pages: `/page-slug/`
- Home: `/`
- Blog listing: `/blog/`
- Essays listing: `/essays/`

## Migration from Existing Site

If you have existing markdown files, use the migration script:

```bash
python migrate.py
```

This will:
- Convert existing frontmatter formats
- Preserve original slugs and URLs
- Handle multiple date formats
- Auto-categorize based on content

## Customization

### Design Changes

Edit the CSS in `templates/base.html`. Key CSS variables:

```css
:root {
    --link-color: rgb(93, 24, 220);     /* Purple accent */
    --text-primary: rgb(17, 17, 17);    /* Main text */
    --text-secondary: rgb(82, 82, 82);  /* Secondary text */
}
```

### Template Modifications

Templates are in `templates/`:

- `base.html` - Base template with CSS and layout
- `index.html` - Home page
- `blog.html` - Blog listing with category toggle
- `essays.html` - Essays listing
- `post.html` - Individual post/essay/page

### Configuration

Modify settings in `config.py`:

```python
class Config:
    SITE_URL = "https://www.samarthbansal.com/"
    SITE_NAME = "Samarth's Blog"
    AUTHOR = "Samarth Bansal"
    TIMEZONE = pytz.timezone('Asia/Kolkata')
```

## File Structure

```
samarth-blog/
├── config.py              # Site configuration
├── content_processor.py   # Markdown processing
├── generator.py           # Main generator script
├── migrate.py             # Migration utilities
├── requirements.txt       # Python dependencies
├── content/               # Markdown content
│   ├── posts/
│   ├── essays/
│   └── pages/
├── templates/             # Jinja2 templates
├── static/                # Static assets (optional)
├── output/                # Generated site
└── migrate_posts/         # Migration staging area
```

## Commands Reference

```bash
# Build the site
python generator.py build

# Create new content
python generator.py new post "Title"
python generator.py new essay "Title"  
python generator.py new page "Title"

# Migrate existing content
python migrate.py

# Install dependencies
pip install -r requirements.txt
```

## Tips

1. **Dates**: Always use YYYY-MM-DD format in frontmatter
2. **Slugs**: Auto-generated from titles, but can be overridden
3. **Categories**: Use lowercase in frontmatter (journalism, personal, tech, food)
4. **External Essays**: Use `external_url` field for essays published elsewhere
5. **Images**: Place in `static/` directory, reference as `/static/image.jpg`

## Troubleshooting

### Build Errors

Check that:
- All markdown files have valid frontmatter
- Dates are in YYYY-MM-DD format
- Required dependencies are installed

### Missing Content

Ensure:
- Files are in correct `content/` subdirectories
- Frontmatter has `published: true` (or omit field)
- File encoding is UTF-8

### URL Issues

The generator preserves existing slugs from frontmatter. If URLs aren't working:
- Check `slug` field in frontmatter
- Verify directory structure in `output/`
- Rebuild with `python generator.py build`