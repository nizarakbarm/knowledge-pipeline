# Obsidian Flavored Markdown Reference

Create and edit valid Obsidian Flavored Markdown. Obsidian extends CommonMark and GFM with wikilinks, embeds, callouts, properties, comments, and other syntax. This reference covers only Obsidian-specific extensions -- standard Markdown is assumed knowledge.

## Workflow: Creating an Obsidian Note

1. **Add frontmatter** with properties (title, tags, aliases) at the top of the file
2. **Write content** using standard Markdown for structure, plus Obsidian-specific syntax below
3. **Link related notes** using wikilinks (`[[Note]]`) for internal vault connections, or standard Markdown links for external URLs
4. **Embed content** from other notes, images, or PDFs using the `![[embed]]` syntax
5. **Add callouts** for highlighted information using `> [!type]` syntax
6. **Verify** the note renders correctly in Obsidian's reading view

> When choosing between wikilinks and Markdown links: use `[[wikilinks]]` for notes within the vault (Obsidian tracks renames automatically) and `[text](url)` for external URLs only.

## Internal Links (Wikilinks)

```markdown
[[Note Name]]                          Link to note
[[Note Name|Display Text]]             Custom display text
[[Note Name#Heading]]                  Link to heading
[[Note Name#^block-id]]                Link to block
[[#Heading in same note]]              Same-note heading link
```

Define a block ID by appending `^block-id` to any paragraph:

```markdown
This paragraph can be linked to. ^my-block-id
```

For lists and quotes, place the block ID on a separate line after the block:

```markdown
> A quote block

^quote-id
```

## Embeds

Prefix any wikilink with `!` to embed its content inline:

```markdown
![[Note Name]]                         Embed full note
![[Note Name#Heading]]                 Embed section
![[image.png]]                         Embed image
![[image.png|300]]                     Embed image with width
![[document.pdf#page=3]]               Embed PDF page
```

## Callouts

```markdown
> [!note]
> Basic callout.

> [!warning] Custom Title
> Callout with a custom title.

> [!faq]- Collapsed by default
> Foldable callout (- collapsed, + expanded).
```

Common types: `note`, `tip`, `warning`, `info`, `example`, `quote`, `bug`, `danger`, `success`, `failure`, `question`, `abstract`, `todo`.

## Properties (Frontmatter)

```yaml
---
title: My Note
date: 2024-01-15
tags:
  - project
  - active
aliases:
  - Alternative Name
cssclasses:
  - custom-class
---
```

Default properties: `tags` (searchable labels), `aliases` (alternative note names for link suggestions), `cssclasses` (CSS classes for styling).

## Tags

```markdown
#tag                    Inline tag
#nested/tag             Nested tag with hierarchy
```

Tags can contain letters, numbers (not first character), underscores, hyphens, and forward slashes. Tags can also be defined in frontmatter under the `tags` property.

## Comments

```markdown
This is visible %%but this is hidden%% text.

%%
This entire block is hidden in reading view.
%%
```

## Obsidian-Specific Formatting

```markdown
==Highlighted text==                   Highlight syntax
```

## Math (LaTeX)

```markdown
Inline: $e^{i\pi} + 1 = 0$

Block:
$$
\frac{a}{b} = c
$$
```

## Diagrams (Mermaid)

````markdown
```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Do this]
    B -->|No| D[Do that]
```
````

To link Mermaid nodes to Obsidian notes, add `class NodeName internal-link;`.

## Footnotes

```markdown
Text with a footnote[^1].

[^1]: Footnote content.

Inline footnote.^[This is inline.]
```

## Complete Example

````markdown
---
title: Project Alpha
date: 2024-01-15
tags:
  - project
  - active
status: in-progress
---

# Project Alpha

This project aims to [[improve workflow]] using modern techniques.

> [!important] Key Deadline
> The first milestone is due on ==January 30th==.

## Tasks

- [x] Initial planning
- [ ] Development phase
  - [ ] Backend implementation
  - [ ] Frontend design

## Notes

The algorithm uses $O(n \log n)$ sorting. See [[Algorithm Notes#Sorting]] for details.

![[Architecture Diagram.png|600]]

Reviewed in [[Meeting Notes 2024-01-10#Decisions]].
````

## Properties Reference

### Property Types

| Type | Example | Description |
|------|---------|-------------|
| Text | `title: My Note` | Plain text |
| List | `tags: [a, b]` | Array of values |
| Number | `rating: 5` | Numeric value |
| Checkbox | `published: true` | Boolean |
| Date | `date: 2024-01-15` | ISO date |
| DateTime | `created: 2024-01-15T10:30:00` | ISO datetime |

### Special Properties

- `tags` - Searchable labels
- `aliases` - Alternative names for link resolution
- `cssclasses` - CSS classes for styling
- `up` - Hierarchical parent (LYT convention)
- `related` - Related notes (LYT convention)
- `in` - Vault section (LYT convention)

## Embed Types

### Note Embeds
```markdown
![[Note Name]]
![[Note Name#Heading]]
![[Note Name#^block-id]]
```

### Image Embeds
```markdown
![[image.png]]
![[image.png|300]]
![[image.png|300x200]]
```

### PDF Embeds
```markdown
![[document.pdf]]
![[document.pdf#page=3]]
![[document.pdf#height=400]]
```

### Audio/Video
```markdown
![[audio.mp3]]
![[video.mp4]]
```

## Callout Types

| Type | Alias | Use Case |
|------|-------|----------|
| note | | General information |
| tip | hint, important | Helpful advice |
| warning | caution, attention | Warning |
| info | | Informational |
| example | | Example |
| quote | cite | Quotation |
| bug | | Bug report |
| danger | | Dangerous action |
| success | check, done | Success |
| failure | missing, fail | Failure |
| question | help, faq | Question |
| abstract | summary, tldr | Summary |
| todo | | Task list |

## References

- [Obsidian Flavored Markdown](https://help.obsidian.md/obsidian-flavored-markdown)
- [Internal links](https://help.obsidian.md/links)
- [Embed files](https://help.obsidian.md/embeds)
- [Callouts](https://help.obsidian.md/callouts)
- [Properties](https://help.obsidian.md/properties)
