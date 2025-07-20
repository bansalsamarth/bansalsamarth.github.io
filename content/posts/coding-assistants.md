---
title: Claude Code Rebuilt My Site. I Wrote Zero Lines of Code. (And I Don't Know How to Feel About It.)
date: 2025-07-20
published: true
---
I am writing this after completely rebuilding this site—the one you are reading—from scratch. But I can't say "I built it." Because unlike the previous version (which now lies dismantled in historical Git commits) that I coded with my own hands, I didn't write a single line of code in this new system. Zero. I got Claude Code to build my site backend for me.

And I am not sure how I feel about this. So I'm writing to think through my feelings.

#### Context 

**1 - The problem statement was simple.** I didn't want any existing CMS platform (like WordPress or Ghost) to back my website. Too much bloat I don't need. Even though I see the immense value of these platforms, my hacker self values markdown files as a way to organize information over loaded databases. A lightweight site like mine will fly with markdown files. No lock-in with any platform. I can choose what I want to capture in my files—including metadata—and no design dependency on platforms. This gives me freedom, and the site is blazing fast because it's just static pages. All I needed in the backend was software that converts markdown files to HTML. Simple.

**2 - I didn't want to use existing static site generators** like Jekyll. I've used them before and they work well, but my requirement was so simple. I wanted full understanding of what's happening in my site without going through frameworks to pick and choose. I was optimizing for simplicity and control. I just needed a file that converts markdown to HTML. That's it.

**3 - So I wrote this converter myself,** and it kind of worked. Hacky software that just worked. My site was hosted on GitHub pages, and I made a system where all markdown files for blogging were in an Obsidian vault. For blogging, all I had to do was open that vault, write in markdown, run a script to generate the HTML, and push to GitHub. Done.

**4 - Except this system was so hacky it constantly broke.** Parsing errors were common: some special character would break and I wouldn't know what went wrong. I'd manually fix it, then realize I didn't have a script to update published blog posts in the blog listing. When I added that, I realized I didn't have functionality to check for edits and updates in older posts, so I wrote another script that I had to run separately. (This happened over extended periods with weeks and months in between, leading to really bloated software. I know the devs reading this are wondering about the extreme suckiness of what I built for such a simple problem. I'm letting 20-year-old Samarth down. Sigh.)

**5 - This mess continued until I realised** all these bugs were inhibiting me from quick blogging—because writing and publishing meant dealing with this operational nightmare. So I only published when I had a really good piece. Which defeated the whole idea of a blog: everything doesn't have to be a carefully crafted essay. I have so much to share and express in words, and blogging is my medium for that. What started as a need for control and freedom flipped around and became a handicap.

**6 - So I decided to rebuild from scratch** and use Claude Code as my AI assistant. I started doing the "Claude Code in Action" course from Anthropic (so good!) and this became my test project. I spent a few hours rebuilding my system—which now works efficiently, exactly how I wanted, without bugs, including migration of old content. I did this without writing a single line of code. Claude wrote every single line (yes, simple system but still) and I just had to be the Product Manager, guiding what exactly I wanted, including design preferences.

This is the context: I had a simple problem, did a messy job solving it, and here comes an AI agent that just did it for me. How am I supposed to feel about this? Excited? Worried? Anxious? I actually don't know. It's a mixed bag.

#### Feeling feelings

**1 - Part of me feels lost** because I spent so much time during college learning to code, mess around with documentation, and fight bugs to build things. I'd always felt that after mastering the basics, the single biggest trait that makes a good engineer stand apart was just... patience. If you know the technical fundamentals and have solid problem-solving ability—baseline assumptions—then you just need to spend time with the problem. A better programmer might find an elegant solution faster, but you can get there. What happens to that ability now? Does it even matter? What is that skill for?

**2 - I remember feeling off** when I started building simple tools in Python because for everything there was a library and I was just plumbing things together. What's my contribution, really? Put together an architecture, learn the frameworks, write the boilerplate, spend hours on StackOverflow finding how others solved this bug, fix it, and boom... app is ready. (Talking about simple apps—not production-ready software.) There was this feeling that if I'm not writing new libraries that unlock new things, I'm not a real programmer. In that context, what's happening now is I'm even more distant from the core of what makes computers work: I can give instructions for plumbing in English—not even Python—and the computer does it for me. I can't call myself a programmer doing this. It feels like identity loss.

**3 - But look at this from a zoomed-out lens:** making a messy system that breaks makes me feel like a programmer; making a system that works perfectly using a coding assistant makes me feel like a fraud.

**4 - This was my initial feeling, but then another realization set in.** I'm actually not deeply attached to the identity of a programmer. That was my past. I'm a writer who _used_ to write code and can write code when needed—but no part of how I exist in the world is deeply attached to making computers do things. It's a nostalgic identity that I deeply adore because it makes me feel powerful, because I know I can build things. But not doing it is also okay. Compare that to writing words, which has an existential dimension for my being: I don't know how I can be in this world if I don't write—it's deeply attached to my sense of self. Working with Claude Code made me realize "programmer" isn't an identity I hold dearly, even though it's something I was holding onto.

**5 - So despite the fraud feeling and discomfort,** once I accept that I care about the outcome of a program more than the process of creating it, Claude Code feels absolutely wonderful. It amplifies possibilities. Everything I'd thought I wanted to exist in the world—now I can make it happen, with sharper things I feel need to be there and stuff that aligns with my taste and design principles.

This is where I am now. I'll mess around with agents more to see how it evolves. But for now, I'm choosing outcome over process, and that feels like the right trade-off. The site works, I can focus on writing, and maybe that's what actually matters?

The question really is: If AI lets us skip the pain and still get the result, what do we mourn—the process, or the identity we built around it? And does that even need mourning?


