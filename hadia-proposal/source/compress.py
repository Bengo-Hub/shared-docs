import sys, pikepdf
src, dst = sys.argv[1], sys.argv[2]
with pikepdf.open(src) as pdf:
    pdf.docinfo["/Title"] = "Hadia Gifting Registry: Proposal and SRDD"
    pdf.docinfo["/Author"] = "Codevertex Africa Limited"
    pdf.docinfo["/Subject"] = "Software requirements and design, delivery plan and commercials"
    pdf.remove_unreferenced_resources()
    pdf.save(dst, compress_streams=True, recompress_flate=True,
             object_stream_mode=pikepdf.ObjectStreamMode.generate, linearize=True)
