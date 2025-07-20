---
title: Claude Code Rebuilt My Site. I Wrote Zero Lines of Code. (And I Don't Know How to Feel About It.)
date: 2025-07-20
published: true
---
I am writing this after completely rebuilding this site from scratch using [Claude Code](https://www.anthropic.com/claude-code). I didn't write a single line of code—Claude wrote everything while I played product manager, directing what I wanted in plain English.

And I am not sure how I feel about this. So I'm writing to think through my feelings.

---
### The Setup

**1) The problem statement was simple.** I didn't want any existing CMS platform (like WordPress or Ghost) to back my website. Too much bloat I didn't need. Even though I see the immense value of these platforms, I prefer simple text files (Markdown, always!) over complex databases for organizing my posts. A lightweight site like mine runs fast with just text files. I'm not tied to any platform, I control exactly what information I capture, and I'm not dependent on someone else's design choices. This gives me freedom, and the site loads blazingly fast. All I needed was software that converts my text files to web pages. Simple.

**2) I didn't want to use existing static site generators like Jekyll.** I've used them before and they work well, but my requirement was so simple. I wanted full understanding of what's happening in my site without going through frameworks to pick and choose. I was optimizing for simplicity and control. I just needed a file that converts markdown to HTML. That's it.

**3) So I wrote this converter myself.** And it kind of worked. Hacky software. My site was hosted on GitHub, and I set up a system where all my blog posts lived in a folder on my computer (Obsidian vault, which is also my note-taking software). For blogging, all I had to do was open that folder, write my post, run my converter script, and push to GitHub. Done.

**4) Except this system was so hacky it constantly broke.** Parsing errors were common: some special character would break and I wouldn't know what went wrong. I'd manually fix it, then realize I didn't have a script to update published blog posts in the blog listing. When I added that, I realized I didn't have functionality to check for edits and updates in older posts, so I wrote another script that I had to run separately. (This happened over extended periods with weeks and months in between, leading to really bloated software. I know the devs reading this are wondering about the extreme suckiness of what I built for such a simple problem. I'm letting 20-year-old Samarth down. Sigh.)

**5) This mess continued until I realised all these bugs were inhibiting me from quick blogging.** Every post meant wrestling with an operational mess. So I only published when I had a really good piece. Which defeated the whole idea of a blog: everything doesn't have to be a carefully crafted essay. I have so much to share and express in words, and blogging is my medium for that. What started as a need for control and freedom flipped around and became a handicap.

**6) So I decided to rebuild from scratch and use Claude Code as my AI assistant.** I started doing the [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action) course from Anthropic (so good!) and this became my test project. I spent a few hours rebuilding my system—directing Claude through conversations, reviewing its code, and iterating on requirements—without writing a single line myself.

This is the context: I had a simple problem, did a messy job solving it, and here comes an AI agent that just did it for me. How am I supposed to feel about this? Excited? Worried? Anxious? I actually don't know. It's a mixed bag.

---

### The Shakeup

**1) Part of me feels lost.** I spent years learning to code, fight bugs, and build things with patience and persistence. Even when I started using Python libraries and felt like I was just "plumbing things together," at least I was writing code. Now I'm giving instructions in English and the computer does everything. I can't call myself a programmer doing this—it feels like identity loss.

**2) The absurdity:** When I write buggy code that breaks, I feel like a real programmer. When AI writes flawless code that works, I feel like a fraud. What to make of this contradiction?

**3) This was my initial feeling, but then another realization set in.** I'm actually not deeply attached to the identity of a programmer. That was my past. I'm a writer who _used_ to write code and can write code when needed—but no part of how I exist in the world is deeply attached to making computers do things. It's a nostalgic identity that I deeply adore because it makes me feel powerful, because I know I can build things. But not doing it is also okay. Compare that to writing words, which has an existential dimension for my being: I don't know how I can be in this world if I don't write—it's deeply attached to my sense of self. Working with Claude Code made me realize "programmer" isn't an identity I hold dearly, even though it's something I was holding onto.

**4) The acceptance:** Once I admitted I care more about what the program _does_ than how it's made, me using Claude Code stopped feeling like a fraud and started feeling like freedom. It amplifies possibilities. Everything I'd imagined wanting to build—now I can actually make it happen. Because AI has bridged the gap between my taste and talent. (Hi there, [Ira Glass](https://www.youtube.com/watch?v=GHrmKL2XKcE)!)


---

This is where I am now. I'm choosing outcome over process, and for my particular relationship with code—nostalgic but not existential—that feels right. I care about having a working blog that lets me focus on writing, not about maintaining my credentials as someone who can wrangle Python scripts.

The question that I am still thinking through: If AI lets us skip the struggle and still get the result, what exactly are we mourning? The process itself, or just the identity we built around surviving it? And does that even need mourning?

---


