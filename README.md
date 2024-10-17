# Add Bookmarks to PDF
This Python script allows you to add bookmarks to a PDF file using a bookmarks file.

## Requirements
- Python 3.x
- tkinter
- PyPDF
- pymupdf
- PIL

## Usage
1. Clone the repository.
2. Install the required packages.
3. Run the script.
```bash
python add_bookmarks_to_pdf.py
```

## How it works
1. The script prompts you to select a bookmarks file and a PDF file.
2. It reads the bookmarks from the selected file.
3. It shows the page of each bookmark in a dedicated window and asks for confirmation or lets the user enter an offset to adjust the page number.
3. It adds the bookmarks to the selected PDF file.

## Bookmarks file format
The bookmarks file should be a comma-separated values (CSV) file with the following format. The first column is the bookmark hierarchy, the second column is the bookmark title, and the third column is the page number, e.g.:
```
1,An Interesting Title,1
1.1,Introduction,1
1.2,Notation,5
1.3,Summary,13
2,The Theory of Everything,77
2.1,Background, 77
2.2,Unification with Gravity,83
```
Sometimes, PDF files leave out empty pages from the printed version, so the page numbers in the table of contents might not match the actual page numbers in the PDF file. This is not an issue since the script visually asks for confirmation for each bookmark and lets you adjust the page number. 