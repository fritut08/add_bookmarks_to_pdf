import tkinter as tk
from tkinter import filedialog
import shutil
from pypdf import PdfWriter
import pymupdf
from PIL import Image, ImageTk


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

def read_bookmarks(file_path):
    print(f"Reading bookmarks from {file_path}")
    bookmarks = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(',')
            hierarchy = parts[0].strip()
            name = parts[1].strip()
            page_number = int(parts[2].strip()) - 1 # Convert to zero-based index
            bookmarks.append((hierarchy, name, page_number))
            print(f"Read bookmark: hierarchy: {hierarchy}, name: {name}, page: {page_number}")
    print(f"Total bookmarks read: {len(bookmarks)}")
    return bookmarks

def update_pdf_page_display(pdf_page, root, label):
    # Render the page to an image
    pix = pdf_page.get_pixmap()
    # Convert the image to a PIL Image object
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)            
    # Convert PIL Image to ImageTk
    img_tk = ImageTk.PhotoImage(img)
    label.config(image=img_tk)
    label.image = img_tk
    root.update()

def add_bookmarks_to_pdf(pdf_path, bookmarks):
    print(f"Adding bookmarks to PDF: {pdf_path}")

    # Copy the input pdf to a backup file
    destination_path = pdf_path.replace('.pdf', '_ORIGINAL.pdf')
    shutil.copyfile(pdf_path, destination_path)
    print(f"Backup of original PDF created at {destination_path}")

    print("Opening PDF (This may take some time for large PDFs)...")
    # Open the PDF file to display the pages
    pdf_document = pymupdf.open(pdf_path)
    # Create a PdfWriter object to write the bookmarks
    pdf_writer = PdfWriter(fileobj=pdf_path, full=True)
    print(f"PDF opened successfully. Total pages: {pdf_document.page_count}")

    # Create a tkinter window to display the pages
    root = tk.Tk()
    root.title("PDF Page Display")
    # Create a label to display the image
    label = tk.Label(root)
    label.pack()

    # Loop through the bookmarks and add them to the PDF
    print("Adding bookmarks...")
    bookmark_dicts = []
    current_offset = 0    
    for hierarchy, name, original_page_number in bookmarks:
        new_page_number = original_page_number + current_offset
        # Ensure the page number is within the valid range
        if new_page_number < 0 or new_page_number > pdf_document.page_count - 1:
                raise ValueError(f"Page number {new_page_number + 1} for bookmark '{hierarchy} {name}' is out of range.")

        # Let user confirm the page number
        confirmed = False
        while not confirmed:

            # Display the page
            update_pdf_page_display(pdf_document.load_page(new_page_number), root, label)
            
            # Ask the user to confirm the page number or provide an offset
            user_input = input(f"Is this page ({new_page_number + 1}) correct for bookmark '{hierarchy} {name}'?\nIf so, enter 'yes'/'y'. Otherwise enter a page offset to find the actual page: ").strip().lower()
            if user_input in ['yes', 'y']:
                confirmed = True
            else:
                try:
                    additional_offset = int(user_input)
                    current_offset += additional_offset
                    new_page_number += additional_offset
                except ValueError:
                    print("Invalid input. Please enter 'yes', 'y', or a valid (signed) integer offset.")

        print(f"Adding bookmark: hierarchy: {hierarchy}, name: {name}, page: {new_page_number + 1}...")

        levels = hierarchy.split('.')
        if len(levels) == 1:
            # Add bookmark to root
            print("Adding bookmark to root")
            current_reference = pdf_writer.add_outline_item(name, new_page_number)
        else:
            # Find Parent
            parent = None
            for bookmark_dict in bookmark_dicts:
                if bookmark_dict["hierarchy"] == '.'.join(levels[:-1]):
                    parent = bookmark_dict["reference"]
                    break
            
            if parent is None:
                # Parent not found
                raise ValueError(f"Parent not found for bookmark: {name}")
            
            # Add bookmark with reference to parent
            print(f"Adding bookmark under parent with hierarchy '{bookmark_dict['hierarchy']}'")
            current_reference = pdf_writer.add_outline_item(name, new_page_number, parent)
        
        bookmark_dicts.append({"hierarchy": hierarchy, "reference": current_reference})

    # Close the window showing the PDF page
    root.destroy()

    # Save the PDF with bookmarks
    print("Saving PDF with bookmarks...")
    with open(pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    print(f"PDF with bookmarks written to {pdf_path}")

if __name__ == "__main__":
    print("Starting the bookmark adding process...")
    bookmarks_file = get_file_path("Select the bookmarks file")
    input_pdf = get_file_path("Select the input PDF file")

    bookmarks = read_bookmarks(bookmarks_file)
    add_bookmarks_to_pdf(input_pdf, bookmarks)
    print("Bookmark adding process completed.")