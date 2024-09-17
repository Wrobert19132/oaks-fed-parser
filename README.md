# Oaks Federation Parser
A parser to parse an Oaks Federation PDF Book, spitting out all the images with metadata adjusted for date, caption, and caption author.

Written for Linux - untested on any other platform.

Requires **pypdf** for image parsing, and **pdfplumber** for text parsing. Needs **exiftool** for metadata editing. 