import fitz  # PyMuPDF
import statistics
from collections import Counter

class PDFOutlineExtractor:
    """
    Extracts a hierarchical outline from a PDF using either its
    bookmarks (ToC) or statistical font analysis.
    """
    def __init__(self, pdf_path, config):
        self.doc = fitz.open(pdf_path)
        self.config = config
        self.font_styles = []

    def extract(self):
        """
        Primary extraction method. Tries bookmarks first, then falls back
        to font analysis based on the configuration.
        """
        title = self.doc.metadata.get("title", "Untitled Document")
        if not title:
            title = "Untitled Document"

        outline = {"title": title, "children": []}

        # Attempt to use bookmarks (Table of Contents) first
        if self.config['extraction_method'] == 'bookmarks':
            toc = self.doc.get_toc()
            if toc:
                outline["children"] = self._build_hierarchy_from_toc(toc)
                return outline
        
        # Fallback or forced method: Statistical Font Analysis
        self._analyze_font_styles()
        outline["children"] = self._build_hierarchy_from_styles()
        return outline

    def _build_hierarchy_from_toc(self, toc):
        """Recursively builds a nested structure from PyMuPDF's ToC."""
        if not toc:
            return []

        # Create a tree structure from the flat ToC list
        # See: https://pymupdf.readthedocs.io/en/latest/faq.html#making-a-tree-from-the-toc
        def build_tree(items):
            if not items:
                return []
            
            # Find the top level (minimum level number)
            min_level = min(item[0] for item in items)
            
            # Group items by their parent at the current top level
            root_nodes = []
            children_items = []
            
            i = 0
            while i < len(items):
                level, text, _ = items[i]
                if level == min_level:
                    # This is a root node at the current level
                    node = {"level": level, "text": text.strip(), "children": []}
                    
                    # Find all direct children of this node
                    children_start_index = i + 1
                    children_end_index = children_start_index
                    while children_end_index < len(items) and items[children_end_index][0] > min_level:
                        children_end_index += 1
                    
                    # Recursively build the subtree for the children
                    node["children"] = build_tree(items[children_start_index:children_end_index])
                    
                    root_nodes.append(node)
                    i = children_end_index # Move index past the processed children
                else:
                    i += 1 # Should not happen if list is ordered, but as a safeguard
            
            return root_nodes

        return build_tree(toc)


    def _analyze_font_styles(self):
        """Scans the document to find all unique font styles and their frequencies."""
        styles = []
        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b['type'] == 0 and "lines" in b:  # Block type 0 is text
                    for l in b["lines"]:
                        for s in l["spans"]:
                            # A style is a tuple of (size, flags, font_name)
                            # Flags help identify bold/italic
                            styles.append((round(s['size']), s['flags'], s['font']))
        
        self.font_styles = Counter(styles)

    def _build_hierarchy_from_styles(self):
        """Identifies heading styles and builds a nested outline."""
        if not self.font_styles:
            return []

        # Ignore the most common styles (likely body text)
        num_to_ignore = self.config.get('ignore_top_n_styles', 1)
        heading_styles = {style: count for style, count in self.font_styles.items()}
        for style, _ in self.font_styles.most_common(num_to_ignore):
            del heading_styles[style]

        if not heading_styles:
            return []

        # Sort remaining styles to determine hierarchy (e.g., by size, then boldness)
        # Larger font size -> higher heading level (lower level number)
        # BOLD flag is bit 4 (16)
        is_bold = lambda flags: (flags & 16)
        
        # Sort by size (desc), then by bold (desc)
        sorted_heading_styles = sorted(heading_styles.keys(), key=lambda s: (s[0], is_bold(s[1])), reverse=True)
        
        # Map styles to heading levels (1, 2, 3...)
        style_to_level = {style: i + 1 for i, style in enumerate(sorted_heading_styles)}
        
        # Now, iterate through the document again and build the hierarchy
        outline = []
        path = [] # Tracks the current path in the hierarchy tree
        
        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b['type'] == 0 and "lines" in b:
                    for l in b["lines"]:
                        # Heuristic: a line is a heading if its primary style is a heading style
                        span = l['spans'][0]
                        style = (round(span['size']), span['flags'], span['font'])

                        if style in style_to_level:
                            level = style_to_level[style]
                            text = " ".join(s['text'] for s in l['spans']).strip()
                            if not text: continue
                            
                            node = {"level": level, "text": text, "children": []}

                            # Find the correct parent in the hierarchy
                            while path and path[-1]["level"] >= level:
                                path.pop()

                            if not path: # This is a top-level heading
                                outline.append(node)
                            else: # This is a sub-heading
                                path[-1]["children"].append(node)
                            
                            path.append(node)
        return outline