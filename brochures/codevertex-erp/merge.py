"""Joins cover.pdf and body.pdf into the brochure PDF, published with the ERP user guide."""
import os
import pikepdf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "docs", "user-guide", "erp", "assets", "Codevertex-ERP.pdf")

pdf = pikepdf.Pdf.new()
for name in ("cover.pdf", "body.pdf"):
    src = pikepdf.Pdf.open(os.path.join(HERE, name))
    pdf.pages.extend(src.pages)
pdf.docinfo["/Title"] = "Codevertex ERP: HR, Payroll, Time and Attendance and Integrated Services"
pdf.docinfo["/Author"] = "Codevertex Africa Limited"
pdf.save(OUT, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
print(OUT, len(pdf.pages), "pages", os.path.getsize(OUT) // 1024, "KB")
