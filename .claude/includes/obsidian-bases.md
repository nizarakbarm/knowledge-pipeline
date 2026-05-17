# Obsidian Bases Format

Create and edit Obsidian Bases (.base files) with views, filters, formulas, and summaries. Use when working with .base files, creating database-like views of notes, or when the user mentions Bases, table views, card views, filters, or formulas in Obsidian.

## Format Overview

Obsidian Bases provide a database-like interface for your notes using frontmatter properties as fields.

## Base File Structure

```yaml
---
name: Project Tracker
source: "Projects/"
properties:
  - name: status
    type: select
    options:
      - todo
      - in-progress
      - done
  - name: priority
    type: number
  - name: due
    type: date
  - name: tags
    type: tags
---
```

## Property Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Plain text | `title: My Project` |
| `number` | Numeric value | `priority: 3` |
| `select` | Single choice | `status: done` |
| `multi_select` | Multiple choices | `tags: [urgent, client-a]` |
| `date` | Date value | `due: 2024-01-15` |
| `checkbox` | Boolean | `completed: true` |
| `url` | Web link | `pr: https://github.com/...` |
| `email` | Email address | `contact: dev@example.com` |

## Views

### Table View
```yaml
views:
  - name: All Projects
    type: table
    sort:
      - property: priority
        direction: desc
    filter:
      - property: status
        condition: is_not
        value: done
```

### Card View
```yaml
views:
  - name: Kanban
    type: board
    group_by: status
    card_properties:
      - title
      - priority
      - due
```

### Gallery View
```yaml
views:
  - name: Gallery
    type: gallery
    cover_property: cover_image
    card_properties:
      - title
      - description
```

## Filters

```yaml
filter:
  - property: status
    condition: is
    value: in-progress
  - property: priority
    condition: greater_than
    value: 2
```

### Filter Conditions

| Condition | Description |
|-----------|-------------|
| `is` | Equals |
| `is_not` | Not equals |
| `contains` | Contains text |
| `does_not_contain` | Doesn't contain |
| `starts_with` | Starts with |
| `ends_with` | Ends with |
| `is_empty` | Is empty |
| `is_not_empty` | Is not empty |
| `greater_than` | > (numbers/dates) |
| `less_than` | < (numbers/dates) |
| `is_before` | Before date |
| `is_after` | After date |

## Formulas

```yaml
properties:
  - name: days_until_due
    type: formula
    formula: "due - today()"
  - name: is_overdue
    type: formula
    formula: "due < today()"
  - name: progress_pct
    type: formula
    formula: "(completed_tasks / total_tasks) * 100"
```

### Formula Functions

| Function | Description | Example |
|----------|-------------|---------|
| `today()` | Current date | `due - today()` |
| `now()` | Current datetime | `now()` |
| `length()` | Array length | `length(tags)` |
| `contains()` | Check inclusion | `contains(tags, "urgent")` |
| `date()` | Parse date | `date("2024-01-15")` |
| `number()` | Parse number | `number("42")` |
| `concat()` | Join strings | `concat(first, " ", last)` |

## Complete Example

```yaml
---
name: Task Manager
source: "Tasks/"
properties:
  - name: title
    type: text
  - name: status
    type: select
    options:
      - todo
      - in-progress
      - review
      - done
  - name: priority
    type: select
    options:
      - low
      - medium
      - high
      - critical
  - name: due
    type: date
  - name: assignee
    type: text
  - name: tags
    type: multi_select
    options:
      - bug
      - feature
      - docs
      - refactor
  - name: is_overdue
    type: formula
    formula: "due < today() and status != 'done'"
views:
  - name: All Tasks
    type: table
    sort:
      - property: priority
        direction: asc
      - property: due
        direction: asc
  - name: Kanban
    type: board
    group_by: status
  - name: Overdue
    type: table
    filter:
      - property: is_overdue
        condition: is
        value: true
---
```

## Tips

- Use consistent property names across notes
- Set default values in frontmatter templates
- Use formulas to reduce manual updates
- Create focused views for different workflows
- Filter out archived/done items from main views
