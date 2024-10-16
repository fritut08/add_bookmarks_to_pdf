import tkinter as tk
from tkinter import filedialog
import shutil
import PyPDF2

def get_file_path(prompt):
    print(prompt)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title=prompt)
    root.destroy()
    if file_path:
        print(f"Selected file: {file_path}")
    else:
        print("No file selected.")
    return file_path

def read_bookmarks(file_path, first_page_number):
    print(f"Reading bookmarks from {file_path} with first page number as {first_page_number}")
    bookmarks = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            hierarchy = parts[0].strip()
            name = parts[1].strip()
            page = int(parts[2].strip()) - 1 + (first_page_number-1) # Shift to first page number and convert to zero-based index
            bookmarks.append((hierarchy, name, page))
            print(f"Read bookmark: hierarchy: {hierarchy}, name: {name}, page: {page}")
    print(f"Total bookmarks read: {len(bookmarks)}")
    return bookmarks

def add_bookmarks_to_pdf(pdf_path, bookmarks):
    print(f"Adding bookmarks to PDF: {pdf_path}")

    # Copy the input pdf to a backup file
    destination_path = pdf_path.replace('.pdf', '_ORIGINAL.pdf')
    shutil.copyfile(pdf_path, destination_path)
    print(f"Backup of original PDF created at {destination_path}")

    pdf_reader = PyPDF2.PdfReader(pdf_path)
    pdf_writer = PyPDF2.PdfWriter()

    print("Copying pages from original PDF (This may take some time for large PDFs)...")
    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    bookmark_dicts = []
    for hierarchy, name, page in bookmarks:
        print(f"Adding bookmark: hierarchy: {hierarchy}, name: {name}, page: {page}")

        levels = hierarchy.split('.')
        if len(levels) == 1:
            # Add bookmark to root
            current_reference = pdf_writer.add_outline_item(name, page)
        else:
            # Find Parent
            for bookmark_dict in bookmark_dicts:
                if bookmark_dict["hierarchy"] == '.'.join(levels[:-1]):
                    parent = bookmark_dict["reference"]
                    break
            
            if parent is None:
                # Parent not found
                raise ValueError(f"Parent not found for bookmark: {name}")
            
            # Add bookmark with reference to parent
            current_reference = pdf_writer.add_outline_item(name, page, parent)
        
        bookmark_dicts.append({"hierarchy": hierarchy, "reference": current_reference})

    with open(pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    print(f"PDF with bookmarks written to {pdf_path}")

if __name__ == "__main__":
    print("Starting the bookmark adding process...")
    bookmarks_file = get_file_path("Select the bookmarks file")
    input_pdf = get_file_path("Select the input PDF file")
    first_page_number = int(input("Enter the actual page number of the page that is labeled with page number 1: "))

    bookmarks = read_bookmarks(bookmarks_file, first_page_number)
    add_bookmarks_to_pdf(input_pdf, bookmarks)
    print("Bookmark adding process completed.")