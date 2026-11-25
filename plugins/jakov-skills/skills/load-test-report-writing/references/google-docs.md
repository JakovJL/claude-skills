# Publishing reports as Google Docs

Uses the `google-workspace` MCP (`import_to_google_doc`, `update_drive_file`, `get_drive_file_download_url`, `get_doc_as_markdown`). Before creating or changing Google files, also load the `anthropic-skills:google-workspace` skill if it is available.

## Steps

1. **Markdown → styled HTML**: `python -I <skill folder>/scripts/md2gdoc.py report.md report.html`. Supports headings, paragraphs, bold, code, links, two-level lists and pipe tables (a column whose separator ends with `:` is right-aligned). Column widths come from the content, so IDs and values like "0.24 s" never break inside a cell. Verdict words "Held, no slowdowns" / "Held with slowdowns" / "Failed" are coloured green / amber / red.
2. **Put the HTML where the connector may read it.** It refuses other folders and names the allowed one in the error (for the workspace MCP usually `~/.workspace-mcp/attachments/`).
3. **Pass the file as a `file:///` URL** (`file:///C:/Users/<user>/.workspace-mcp/attachments/report.html`); a plain Windows path is refused.
4. **New doc**: `import_to_google_doc(file_name, file_path=<file URL>, source_format="html")`. The name is cut at its last dot ("24.11.2026 (summary)" becomes "24.11"): end the name with `.md` (it is stripped) or write dates as "24 Nov 2026".
   **Existing doc**: `update_drive_file(file_id, file_path=<file URL>, source_format="html", name=...)` replaces the content in place and keeps the link. Use this for every change after the first publish.
5. **Cross-links**: publish the full report, put its link into the short one, publish the short one, then update the full one with the short report's link.
6. **Look at it**: `get_drive_file_download_url(file_id, export_format="pdf")` saves the PDF locally; render pages with
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <skill folder>/scripts/pdf2png.ps1 -Pdf "<pdf>" -OutDir "<scratch>/pages" -Width 800`
   (Windows PowerShell 5.1 and the built-in Windows PDF API; no poppler). Read every page image: the short report fits two pages; nothing breaks inside table cells; text is not glued to tables; lists are indented; no table row is split across pages. Fix, update in place, look again.

## Known behaviour

- Plain markdown import makes header cells bold, gives every column the same width and leaves no space after tables; use HTML.
- Google ignores margins after a table; `md2gdoc.py` adds a 5 pt empty paragraph after each one.
- Body Arial 10 pt, tables 8.5 pt, Letter page with 1" margins (468 pt text width, used for column widths).
- Claude Docs mention chips export as the plain word "Doc"; use ordinary links in anything meant for Google Docs.
- `get_doc_as_markdown(document_id, include_comments=false)` confirms content and links quickly; the PDF render confirms the look.
