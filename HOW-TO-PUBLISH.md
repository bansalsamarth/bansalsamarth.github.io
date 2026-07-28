# How To Publish

Your reference manual for adding anything to samarthbansal.com. Everything runs through the `./blog` script from the project folder — you never need to remember generator or git commands.

## The 30-second version

```bash
./blog new post "My Post Title"   # 1. create
# ... write in Obsidian or any editor ...
./blog preview                    # 2. check it locally (optional)
./blog publish                    # 3. site goes live
```

---

## The three commands

### `./blog new <type> "Title"`

Creates a markdown file with the right frontmatter already filled in, and prints where it is. Types:

| Type | What it's for | File lands in |
|---|---|---|
| `post` | Blog — reflections, observations, working notes | `content/posts/` |
| `essay` | Essays — crafted long-form pieces | `content/essays/` |
| `journalism` | Journalism — curated links to your reporting | `content/journalism/` |
| `note` | Notes — microblog, quick thoughts, photos | `content/micro/` |

### `./blog preview`

Builds the site and serves it at http://localhost:8000 (opens your browser). This is **the** way to see your site with full design before publishing. Ctrl+C to stop.

### `./blog publish [optional message]`

Builds, commits everything, and pushes. Live at samarthbansal.com within a minute or two. If you don't give a message, it uses a dated one. If nothing changed, it tells you and does nothing.

**Safety net:** a GitHub Action rebuilds the site on every push. So if you ever edit a file directly on github.com (or push without building), the live site still updates itself.

---

## Recipes by section

### Blog post

```bash
./blog new post "What I Learned This Month"
```

Open the file, write below the `---`, done. Frontmatter you can tweak:

```yaml
title: "What I Learned This Month"
date: 2026-07-05
category: personal        # groups posts in the "By Category" view
published: true           # false = draft, invisible on the site
```

### Journalism entry

Journalism is a **curation, not an archive**. Each entry is a link plus a context note — why the story mattered, how it came about.

```bash
./blog new journalism "My Investigation Title"
```

```yaml
title: "My Investigation Title"
publication: "Mint"                          # shown as the purple label
date: 2021-02-16
external_url: "https://livemint.com/..."     # where the piece lives
published: true
```

**The markdown body below the frontmatter is the context note** — it appears under the link on the journalism page. A couple of sentences is perfect.

Your entire old CSV was migrated: all ~92 entries sit in `content/journalism/` as drafts (`published: false`). To hand-pick one: open it, write the context note, flip `published: true`, publish.

### Essay

Essays come in three flavours, all one small file:

**1. Written here as markdown** — like a blog post but in `content/essays/`. The body is the essay itself. For the note shown on the listing page, use a `context:` field:

```yaml
title: "My Essay"
date: 2026-07-05
context: "Why I wrote this — shown on the essays listing page."
```

**2. A custom-designed HTML page hosted on your site** (like `romantic-idiot.html`):

```yaml
title: "The Romantic Idiot"
date: 2023-07-22
external_url: "/romantic-idiot.html"    # relative = internal, no ↗ arrow
```

Body = context note. (Draft entries for all ten of your existing custom pages already sit in `content/essays/` and `content/journalism/` — write their notes and flip them on.)

**3. Published elsewhere:**

```yaml
external_url: "https://theatlantic.com/..."   # full URL = shows ↗, opens new tab
```

Body = context note.

### Note (microblog)

```bash
./blog new note "Anything — this becomes the note text"
```

Timestamped, no title, shows up on /micro/ like a tweet. Edit the file to add more, including photos:

1. Drop the image in `content/images/` (e.g. `content/images/sunset.jpg`)
2. Reference it in the note: `![](/images/sunset.jpg)`

Images work the same way in posts and essays.

---

## Things worth knowing

- **Drafts**: `published: false` in any file's frontmatter hides it from the site. Great for half-written things — they stay in the repo, invisible to readers.
- **Custom HTML pages**: to add a new hand-designed page, put the `.html` file in `docs/` root — the generator automatically preserves any root-level `.html` file during rebuilds. Then create an essay/journalism entry pointing at it (`external_url: "/my-page.html"`) so people can find it.
- **Custom URLs**: add `slug: my-custom-url` to frontmatter to control a post's URL (used to preserve old links).
- **Editing old posts**: just edit the markdown file and `./blog publish`. The build log tells you what was added/updated/deleted.
- **Evergreen** (`/evergreen/`) exists in the code but is still "coming soon" — activate later if you want it.
- **Previewing**: always judge the site through `./blog preview` (localhost:8000). Opening a template file from `templates/` in an editor preview shows unstyled fragments — the design is assembled from `base.html` only at build time.

## When something looks off

| Symptom | Likely cause |
|---|---|
| New piece doesn't show up | `published: false` still set, or you didn't rebuild — run `./blog publish` again |
| Piece shows but no context note | Note goes in the markdown body (external pieces) or `context:` field (hosted essays) |
| Site live but stale | Wait a minute for GitHub Pages; check the Actions tab on GitHub if it persists |
| Weird date or missing date | Frontmatter `date:` must be `YYYY-MM-DD` |
