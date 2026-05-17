# JSON Canvas Format

Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian.

## Format Specification

### Basic Structure
```json
{
  "nodes": [
    {
      "id": "node-id-1",
      "type": "text",
      "text": "Node content",
      "x": 100,
      "y": 100,
      "width": 250,
      "height": 60
    }
  ],
  "edges": [
    {
      "id": "edge-id-1",
      "fromNode": "node-id-1",
      "toNode": "node-id-2",
      "fromSide": "right",
      "toSide": "left"
    }
  ]
}
```

### Node Types

| Type | Description | Required Fields |
|------|-------------|----------------|
| `text` | Text node | `text` |
| `file` | File embed | `file` |
| `link` | External link | `url` |
| `group` | Container | `label` |

### Node Properties

```json
{
  "id": "unique-id",
  "type": "text",
  "text": "Content",
  "x": 0,
  "y": 0,
  "width": 300,
  "height": 100,
  "color": "1",  // Optional color (1-6)
  "backgroundColor": "#ff0000",  // Optional custom color
  "textColor": "#ffffff"  // Optional text color
}
```

### Edge Properties

```json
{
  "id": "edge-1",
  "fromNode": "node-a",
  "toNode": "node-b",
  "fromSide": "right",  // top, right, bottom, left
  "toSide": "left",
  "color": "2",
  "label": "relates to"
}
```

### Group Nodes

```json
{
  "id": "group-1",
  "type": "group",
  "label": "Project A",
  "x": 0,
  "y": 0,
  "width": 500,
  "height": 400,
  "backgroundColor": "#f0f0f0",
  "children": ["node-1", "node-2"]
}
```

## Examples

### Simple Mind Map
```json
{
  "nodes": [
    {
      "id": "center",
      "type": "text",
      "text": "Main Idea",
      "x": 400,
      "y": 300,
      "width": 200,
      "height": 80
    },
    {
      "id": "branch1",
      "type": "text",
      "text": "Branch 1",
      "x": 700,
      "y": 200,
      "width": 150,
      "height": 60
    },
    {
      "id": "branch2",
      "type": "text",
      "text": "Branch 2",
      "x": 700,
      "y": 400,
      "width": 150,
      "height": 60
    }
  ],
  "edges": [
    {
      "id": "e1",
      "fromNode": "center",
      "toNode": "branch1",
      "fromSide": "right",
      "toSide": "left"
    },
    {
      "id": "e2",
      "fromNode": "center",
      "toNode": "branch2",
      "fromSide": "right",
      "toSide": "left"
    }
  ]
}
```

### Flowchart
```json
{
  "nodes": [
    {
      "id": "start",
      "type": "text",
      "text": "Start",
      "x": 100,
      "y": 100
    },
    {
      "id": "decision",
      "type": "text",
      "text": "Decision?",
      "x": 100,
      "y": 250
    }
  ],
  "edges": [
    {
      "id": "e1",
      "fromNode": "start",
      "toNode": "decision",
      "fromSide": "bottom",
      "toSide": "top",
      "label": "next"
    }
  ]
}
```

## Best Practices

- Use unique IDs (UUID or descriptive)
- Position nodes with adequate spacing (min 50px between)
- Use consistent colors for related nodes
- Label edges for clarity
- Group related nodes visually
- Keep canvas focused (max ~50 nodes for performance)

## References

- [JSON Canvas Spec](https://jsoncanvas.org/)
- [Obsidian Canvas Documentation](https://help.obsidian.md/canvas)
