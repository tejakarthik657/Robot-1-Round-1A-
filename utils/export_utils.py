import json
import os

def save_outline(outline, output_path, format):
    """Dispatcher to save the outline in the specified format."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if format == 'json':
        _save_as_json(outline, output_path)
    elif format == 'md':
        _save_as_markdown(outline, output_path)
    else:
        raise ValueError(f"Unsupported export format: {format}")

def _save_as_json(outline, output_path):
    """Saves the outline as a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(outline, f, indent=2, ensure_ascii=False)

def _save_as_markdown(outline, output_path):
    """Saves the outline as a Markdown file."""
    with open(output_path, "w", encoding="utf-8") as f:
        # Write title as H1
        f.write(f"# {outline['title']}\n\n")
        # Recursively write the children
        _write_md_children(f, outline['children'])

def _write_md_children(f, children, indent_level=2):
    """Recursively writes nested heading children to the markdown file."""
    for item in children:
        # Use heading level from analysis, or indent level for TOC-based
        level = item.get('level', indent_level)
        f.write(f"{'#' * level} {item['text']}\n")
        if item.get("children"):
            _write_md_children(f, item["children"], indent_level=level + 1)