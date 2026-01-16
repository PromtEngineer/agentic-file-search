"""
Generate professional-looking PDF documents from markdown files.
Creates documents that look like real IT department documentation.

Usage:
    python generate_pdfs.py

Requirements:
    pip install fpdf2 markdown
"""

import re
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import markdown
from html.parser import HTMLParser


# Company branding
COMPANY_NAME = "DataFlow Corp"
DEPARTMENT = "Information Technology"
CONFIDENTIAL = "INTERNAL USE ONLY"


class HTMLToText(HTMLParser):
    """Simple HTML to text converter for markdown tables."""
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_td = False
        self.in_th = False
        self.current_row = []
        self.rows = []
        self.in_code = False
        self.in_pre = False

    def handle_starttag(self, tag, attrs):
        if tag == 'td':
            self.in_td = True
        elif tag == 'th':
            self.in_th = True
        elif tag == 'tr':
            self.current_row = []
        elif tag == 'code':
            self.in_code = True
        elif tag == 'pre':
            self.in_pre = True

    def handle_endtag(self, tag):
        if tag == 'td':
            self.in_td = False
        elif tag == 'th':
            self.in_th = False
        elif tag == 'tr':
            if self.current_row:
                self.rows.append(self.current_row)
        elif tag == 'code':
            self.in_code = False
        elif tag == 'pre':
            self.in_pre = False

    def handle_data(self, data):
        if self.in_td or self.in_th:
            self.current_row.append(data.strip())


class DocumentPDF(FPDF):
    """Custom PDF class with professional styling."""

    def __init__(self, doc_id="", version="", author="", status=""):
        super().__init__()
        self.doc_id = doc_id
        self.version = version
        self.author = author
        self.status = status
        self.print_date = datetime.now().strftime("%Y-%m-%d")

    def header(self):
        # Logo box
        self.set_fill_color(0, 102, 204)  # Blue
        self.rect(10, 8, 15, 15, 'F')
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 12)
        self.cell(15, 8, 'DF', 0, 0, 'C')

        # Company name
        self.set_text_color(0, 102, 204)
        self.set_font('Helvetica', 'B', 12)
        self.set_xy(28, 10)
        self.cell(0, 5, COMPANY_NAME, 0, 1)

        # Department
        self.set_text_color(100, 100, 100)
        self.set_font('Helvetica', '', 9)
        self.set_xy(28, 16)
        self.cell(0, 5, DEPARTMENT, 0, 1)

        # Blue line under header
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, 26, 200, 26)

        self.ln(15)

    def footer(self):
        self.set_y(-20)

        # Confidential notice (left)
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(200, 0, 0)
        self.cell(60, 5, CONFIDENTIAL, 0, 0, 'L')

        # Page number (center)
        self.set_text_color(100, 100, 100)
        self.set_font('Helvetica', '', 8)
        self.cell(70, 5, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

        # Date (right)
        self.cell(60, 5, self.print_date, 0, 0, 'R')

    def add_metadata_box(self):
        """Add document metadata box at top of first page."""
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.rect(10, self.get_y(), 190, 22, 'DF')

        y_start = self.get_y() + 3
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)

        # Row 1
        self.set_xy(15, y_start)
        self.cell(25, 5, 'Document ID:', 0, 0)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0, 0, 0)
        self.cell(45, 5, self.doc_id, 0, 0)

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(20, 5, 'Version:', 0, 0)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0, 0, 0)
        self.cell(20, 5, self.version, 0, 0)

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(20, 5, 'Status:', 0, 0)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0, 0, 0)
        self.cell(30, 5, self.status, 0, 1)

        # Row 2
        self.set_xy(15, y_start + 7)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(25, 5, 'Author:', 0, 0)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0, 0, 0)
        self.cell(45, 5, self.author, 0, 0)

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(20, 5, 'Print Date:', 0, 0)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0, 0, 0)
        self.cell(20, 5, self.print_date, 0, 0)

        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(200, 0, 0)
        self.cell(50, 5, CONFIDENTIAL, 0, 1)

        self.ln(15)

    def add_title(self, title):
        """Add document title."""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, title, 0, 1)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def add_heading2(self, text):
        """Add H2 heading."""
        self.ln(5)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 68, 153)
        self.cell(0, 8, text, 0, 1)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def add_heading3(self, text):
        """Add H3 heading."""
        self.ln(3)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(51, 51, 51)
        self.cell(0, 7, text, 0, 1)
        self.ln(2)

    def add_paragraph(self, text):
        """Add paragraph text."""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        # Handle bold text markers
        self.multi_cell(0, 5, text)
        self.ln(2)

    def add_bullet(self, text, level=0):
        """Add bullet point."""
        indent = 10 + (level * 5)
        self.set_x(indent)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        bullet = chr(149) if level == 0 else '-'
        self.cell(5, 5, bullet, 0, 0)
        # Limit text width to avoid overflow
        self.multi_cell(180 - indent, 5, text[:200])

    def add_table(self, headers, rows):
        """Add a table."""
        self.ln(3)

        # Calculate column widths
        num_cols = len(headers) if headers else (len(rows[0]) if rows else 0)
        if num_cols == 0:
            return

        # Limit columns and calculate width
        max_cols = 5
        if num_cols > max_cols:
            num_cols = max_cols
            headers = headers[:max_cols] if headers else headers
            rows = [row[:max_cols] for row in rows]

        col_width = min(190 / num_cols, 60)  # Cap column width

        # Header row
        if headers:
            self.set_fill_color(0, 102, 204)
            self.set_text_color(255, 255, 255)
            self.set_font('Helvetica', 'B', 9)
            for header in headers:
                self.cell(col_width, 7, str(header)[:30], 1, 0, 'L', True)
            self.ln()

        # Data rows
        self.set_font('Helvetica', '', 9)
        self.set_text_color(51, 51, 51)
        fill = False
        for row in rows:
            if fill:
                self.set_fill_color(249, 249, 249)
            else:
                self.set_fill_color(255, 255, 255)
            for cell in row:
                self.cell(col_width, 6, str(cell)[:30], 1, 0, 'L', True)
            self.ln()
            fill = not fill

        self.ln(3)

    def add_code_block(self, code):
        """Add a code block."""
        self.set_fill_color(45, 45, 45)
        self.set_text_color(248, 248, 242)
        self.set_font('Courier', '', 7)  # Smaller font for code

        lines = code.strip().split('\n')
        # Truncate long lines and limit line count
        lines = [line[:70] for line in lines[:20]]

        start_y = self.get_y()
        height = len(lines) * 3.5 + 6

        # Check if we need a new page
        if start_y + height > 270:
            self.add_page()
            start_y = self.get_y()

        self.rect(10, start_y, 190, height, 'F')
        self.set_xy(13, start_y + 3)

        for line in lines:
            # Replace special characters that might cause issues
            line = line.replace('\u2502', '|').replace('\u2500', '-')
            self.cell(0, 3.5, line, 0, 1)
            self.set_x(13)

        self.set_y(start_y + height + 3)
        self.set_text_color(51, 51, 51)

    def add_blockquote(self, text):
        """Add a blockquote."""
        self.set_fill_color(230, 242, 255)
        self.set_draw_color(0, 102, 204)

        start_y = self.get_y()
        self.set_x(15)
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(51, 51, 51)
        self.multi_cell(180, 5, text)
        end_y = self.get_y()

        # Draw left border
        self.set_line_width(1)
        self.line(12, start_y - 2, 12, end_y + 2)

        self.ln(3)


def extract_metadata(content: str) -> dict:
    """Extract document metadata from markdown content."""
    metadata = {
        "doc_id": "DOC-2026-XXX",
        "version": "1.0",
        "author": "IT Department",
        "status": "Final",
        "title": "Document"
    }

    lines = content.split('\n')
    for i, line in enumerate(lines[:30]):
        if line.startswith('# ') and 'title' not in metadata:
            metadata["title"] = line[2:].strip()
        if "Document ID:" in line:
            metadata["doc_id"] = line.split(":")[-1].strip().replace("**", "")
        elif "Version:" in line:
            metadata["version"] = line.split(":")[-1].strip().replace("**", "")
        elif "Author:" in line:
            metadata["author"] = line.split(":")[-1].strip().replace("**", "")
        elif "Status:" in line:
            metadata["status"] = line.split(":")[-1].strip().replace("**", "")

    return metadata


def parse_markdown_to_pdf(md_content: str, pdf: DocumentPDF):
    """Parse markdown content and add to PDF."""

    lines = md_content.split('\n')
    i = 0
    in_code_block = False
    code_buffer = []
    in_table = False
    table_rows = []
    table_headers = []

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                pdf.add_code_block('\n'.join(code_buffer))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                # Parse header row
                cells = [c.strip() for c in line.split('|')[1:-1]]
                table_headers = cells
                i += 1
                # Skip separator row
                if i < len(lines) and '---' in lines[i]:
                    i += 1
                continue
            else:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if cells and not all(c.replace('-', '').strip() == '' for c in cells):
                    table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            # End of table
            if table_headers or table_rows:
                pdf.add_table(table_headers, table_rows)
            in_table = False
            table_headers = []
            table_rows = []

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Skip metadata lines (already processed)
        if any(x in line for x in ['Document ID:', 'Version:', 'Last Updated:', 'Author:', 'Status:', 'Classification:']):
            i += 1
            continue

        # Horizontal rule
        if line.strip().startswith('---') or line.strip().startswith('***'):
            pdf.ln(5)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            i += 1
            continue

        # Headings
        if line.startswith('# '):
            # Skip main title (already added)
            i += 1
            continue
        elif line.startswith('## '):
            pdf.add_heading2(line[3:].strip())
            i += 1
            continue
        elif line.startswith('### '):
            pdf.add_heading3(line[4:].strip())
            i += 1
            continue

        # Blockquotes
        if line.startswith('>'):
            quote_text = line[1:].strip()
            while i + 1 < len(lines) and lines[i + 1].startswith('>'):
                i += 1
                quote_text += ' ' + lines[i][1:].strip()
            pdf.add_blockquote(quote_text)
            i += 1
            continue

        # Bullet points
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            level = (len(line) - len(line.lstrip())) // 2
            text = line.strip()[2:]
            # Clean up markdown formatting
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
            pdf.add_bullet(text, level)
            i += 1
            continue

        # Numbered lists
        if re.match(r'^\d+\.\s', line.strip()):
            text = re.sub(r'^\d+\.\s', '', line.strip())
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            pdf.add_bullet(text)
            i += 1
            continue

        # Regular paragraphs
        text = line.strip()
        # Clean up markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

        if text:
            pdf.add_paragraph(text)

        i += 1

    # Handle any remaining table
    if in_table and (table_headers or table_rows):
        pdf.add_table(table_headers, table_rows)


def convert_to_pdf(md_path: Path, output_dir: Path) -> Path:
    """Convert a markdown file to a professional PDF."""

    # Read markdown content
    content = md_path.read_text(encoding='utf-8')

    # Extract metadata
    meta = extract_metadata(content)

    # Create PDF
    pdf = DocumentPDF(
        doc_id=meta['doc_id'],
        version=meta['version'],
        author=meta['author'],
        status=meta['status']
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    # Add metadata box
    pdf.add_metadata_box()

    # Add title
    pdf.add_title(meta['title'])

    # Parse and add content
    parse_markdown_to_pdf(content, pdf)

    # Output path
    pdf_path = output_dir / f"{md_path.stem}.pdf"
    pdf.output(pdf_path)

    return pdf_path


def main():
    """Main function to convert all demo documents to PDF."""

    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    demo_docs_dir = project_root / "data" / "demo_project"
    output_dir = demo_docs_dir  # Output PDFs in same folder

    print(f"\n{'='*60}")
    print(f"  {COMPANY_NAME} - Document Generator")
    print(f"  Converting IT Project Documents to PDF")
    print(f"{'='*60}\n")

    # Find all markdown files
    md_files = list(demo_docs_dir.glob("*.md"))

    if not md_files:
        print(f"No markdown files found in {demo_docs_dir}")
        return

    print(f"Found {len(md_files)} documents to convert:\n")

    # Convert each file
    for md_file in sorted(md_files):
        print(f"  Converting: {md_file.name}...", end=" ")
        try:
            pdf_path = convert_to_pdf(md_file, output_dir)
            print(f"OK -> {pdf_path.name}")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"  Conversion complete!")
    print(f"  PDFs saved to: {output_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
