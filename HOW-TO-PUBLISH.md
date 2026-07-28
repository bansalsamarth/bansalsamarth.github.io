# How To Publish

Quick reference. Run everything from the project folder.

## The three commands

- `./blog new post|essay|journalism|note "Title"` — makes the file, frontmatter already filled in
- `./blog preview` — builds and opens http://localhost:8000. Safe, local only. Ctrl+C to stop.
- `./blog publish` — builds, commits, **and pushes. This puts it live for the world.**

## Blog post

1. `./blog new post "My Title"`
2. Open the file in `content/posts/`, write below the `---`
3. `./blog preview` to check
4. `./blog publish`

Frontmatter you can change:
- `date:` — must be `YYYY-MM-DD`
- `category:` — groups posts in the "By Category" view
- `published: false` — hides it (draft)
- `slug:` — custom URL, if you need to keep an old link working

## Journalism entry

A link plus a note on why the story mattered. Not an archive of everything.

1. `./blog new journalism "Story Title"`
2. Fill in:
   - `publication:` — shows as the purple label
   - `external_url:` — where the piece lives
   - `published: true`
3. **Write the context note in the body, below the `---`.** This is what appears under the title.

## Essay

Same shape. Three kinds:

- **Written here** — body is the essay itself, so put the listing note in a `context:` field
- **Custom HTML page on your site** — `external_url: "/my-page.html"`, body is the note
- **Published elsewhere** — `external_url: "https://..."`, body is the note

## Note (microblog)

`./blog new note "the text"` — timestamped, no title, lands in `content/micro/`.

## Images

1. Drop the file in `content/images/`
2. Reference it as `![](/images/name.jpg)`

Works in posts, essays, and notes.

## Links: internal vs external

- `https://...` → shows a ↗ and opens in a new tab
- `/my-page.html` → treated as your own site, no arrow

To add a hand-designed HTML page: put the `.html` file in the `docs/` root (the build preserves root-level HTML files), then point an essay or journalism entry at it.

## Current state

- 87 journalism entries live in `content/journalism/`, all `published: false`. 65 already have context notes from the old CSV; about 22 still need one.
- Essays and Journalism pages show an empty-state message until you flip entries to `published: true`.
- Notes (`/micro/`) and Evergreen (`/evergreen/`) are still "coming soon" pages.

## If something looks wrong

- **Piece doesn't appear** — `published: false` is still set
- **Appears but no note** — note goes in the body (for external links) or a `context:` field (for essays written here)
- **Build fails** — read the error; a bad `date:` format is the usual cause
- **Site live but stale** — give GitHub Pages a minute, then check the Actions tab

A GitHub Action rebuilds the site after any push that touches content, so edits made on github.com or your phone still go live.
