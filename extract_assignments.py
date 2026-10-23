from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table

for path in sorted(Path('assignments').glob('*.docx')):
    doc = Document(path)
    lines = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn('w:p'):
            p = Paragraph(child, doc)
            if p.text.strip():
                lines.append(f'[{p.style.name}] {p.text}')
        elif child.tag == qn('w:tbl'):
            table = Table(child, doc)
            lines.append('[TABLE]')
            for row in table.rows:
                lines.append(' | '.join(cell.text.replace('\n', ' / ') for cell in row.cells))
            lines.append('[/TABLE]')
    for i, section in enumerate(doc.sections):
        for label, part in [('header', section.header), ('footer', section.footer)]:
            for p in part.paragraphs:
                if p.text.strip():
                    lines.append(f'[{label} {i}] {p.text}')
    output = path.with_suffix('.extracted.txt')
    output.write_text('\n'.join(lines), encoding='utf-8')
    print(f'{path.name}: {len(lines)} lines -> {output}')
