#!/usr/bin/env python3
"""Report exact page count of a .docx using the installed Word.

Word refuses paths with awkward characters, so the file is copied to a
simple temp path first.
"""
import os, sys, shutil, tempfile
import win32com.client as win32

src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                      else "IE3122-Northbridge-Report-Concise.docx")
tmp = os.path.join(tempfile.gettempdir(), "_pagecount.docx")
shutil.copy2(src, tmp)

word = win32.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
try:
    doc = word.Documents.Open(FileName=tmp, ReadOnly=True,
                              AddToRecentFiles=False, ConfirmConversions=False)
    doc.Repaginate()
    pages = doc.ComputeStatistics(2)
    words = doc.ComputeStatistics(0)
    doc.Close(False)
    status = "OK" if pages <= 40 else f"OVER by {pages-40}"
    print(f"{os.path.basename(src)}: {pages} pages, {words:,} words   [{status}]")
finally:
    word.Quit()
    try: os.remove(tmp)
    except OSError: pass
