from markdown_pdf import MarkdownPdf, Section

def create_pdf(markdown_content: str):
    pdf = MarkdownPdf()
    pdf.meta["title"] = 'Generated Content'
    pdf.add_section(Section(markdown_content, toc=False))
    pdf.save('output.pdf')

def determine_sqlite_type(value):
    if value == "None" or value is None:
        return "NULL"
    try:
        int(value)
        return "INTEGER"
    except ValueError:
        try:
            float(value)
            return "REAL"
        except ValueError:
            return "TEXT"
