# Workflows

## Knowledge Pipeline (3-Agent Flow)

When user provides "Gathered Knowledge" (articles, snippets, thoughts, resources):

**Step 1: @sensemaker** — Content Distillation
- **Input:** Raw content (any format)
- **Process:** Extract core concepts, classify knowledge type, generate structured note
- **Output:** Distilled note with frontmatter draft + confidence score + knowledge type

**Step 2: @librarian** — Location Determination
- **Input:** Distilled note + suggested tags/MOCs
- **Process:** Determine optimal vault location (Atlas/Calendar/Efforts), generate filename
- **Output:** File path + folder creation instructions + confidence score

**Step 3: @connector** — Linking & MOC Updates
- **Input:** Note content + file location + knowledge type
- **Process:** Populate `up:`/`related:` properties, update MOCs, check for duplicates
- **Output:** Fully-linked note with bidirectional connections + confidence score

### Confidence-Based Execution

| Confidence | Action |
|------------|--------|
| **≥0.85** | Auto-execute, present summary for confirmation |
| **0.70-0.84** | Present pipeline summary, 1-click confirm |
| **<0.70** | Present options at each step, require explicit choices |

### Pipeline Failures

1. If @sensemaker fails → Ask for clarification on input type
2. If @librarian fails → Default to `+/` (inbox)
3. If @connector fails → Create note without links, flag for later

---

## ARC Workflow (Add → Relate → Communicate)

**Add:** Capture without friction (daily log, fleeting notes, inbox)
**Relate:** Search first, classify, extract atomic, establish connections, validate
**Communicate:** Use in output, reference in projects, build on for future

---

## Enrichment Workflows

**Article/Book:** Read → Capture to daily log → Identify concepts → Classify → Check duplicates → Create/update notes → Add to MOC

**Experience:** Capture → Reflect → Identify generalizable insight → Extract as principle/concept → Link to daily log

**Research:** Gather sources → Create synthesis → Identify gaps → Create atomic notes → Update MOC → Archive synthesis

---

## Validation Checklist

Before considering enrichment complete:
- [ ] Frontmatter has `up:` and `created:`
- [ ] Note added to relevant MOC
- [ ] At least one `related:` link if applicable
- [ ] No broken links introduced
- [ ] No duplicate created (or duplicates merged)
- [ ] Knowledge type classified (Concept/Process/Entity/Principle)
- [ ] Source attribution included
