import subprocess
import requests
from bs4 import BeautifulSoup

'''
Book Parser and Converter

Overview:

This script dynamically fetches and parses text content from an online book. 
It iterates through pages of the book, extracting text enclosed within <p> tags. 
The parsed content is saved to a .txt file.
Once all pages are processed, the script automatically converts the .txt file to .mobi format,
using either Calibre's `ebook-convert` tool.

Features:
- Fetches and parses pages from a specified online book URL.
- Dynamically adjusts the page number and handles non-existent pages.
- Cleans and formats extracted text by removing unwanted characters and tags.
- Converts the final .txt file to .mobi format for eBook compatibility.

Dependencies:
- Requests: For making HTTP requests to fetch book pages.
- BeautifulSoup (bs4): For parsing and extracting HTML content.
- Calibre (ebook-convert): For converting .txt files to .mobi format.

Usage:
1. Ensure `ebook-convert` is installed and accessible in your PATH.
2. Modify the `base_url` variable to point to the book's online URL.
3. Run the script to fetch, parse, and convert the book content.

Author: Oleksandra
Date: 06/08/2024
'''

# The base URL for accessing the book's pages is as follows:
base_url = 'http://book-online.com.ua/read.php?book=38&page={page}'

# Output file name
output_file = 'book_content.txt'
mobi_file = 'book_content.mobi'

# Maximum number of pages to check
max_pages = 800


# Function to fetch and parse a page
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


# Function to write parsed content to a file
def save_content(file, content):
    file.write(content + "\n\n")


# Function to clean content by removing unwanted characters
def clean_content(content):
    # Remove non-breaking spaces and the dash at the beginning of lines in order to parse clean text only
    cleaned_content = content.replace('\u2013\u00a0', '').replace('\u00a0', ' ').strip()
    return cleaned_content


# Function to extract and save content from <p> tags around the specific markers
def extract_and_save_content(soup, file, page_number):
    # Find the div containing the specific page number marker
    page_marker = soup.find_all(
        lambda tag: tag.name == "img" and tag.next_sibling and str(page_number) in tag.next_sibling)

    for marker in page_marker:
        # Find the next sibling, which should contain the paragraphs
        next_sibling = marker.find_next('p')
        while next_sibling and next_sibling.name == "p":
            content = next_sibling.get_text()
            # evoke clean_content() function
            cleaned_content = clean_content(content)
            # evoke save_content() function
            save_content(file, cleaned_content)
            next_sibling = next_sibling.find_next_sibling('p')


# Open the output file using a context manager
with open(output_file, 'w', encoding='utf-8') as file:
    page_number = 1
    last_content = ""
    empty_page_counter = 0

    while page_number <= max_pages:
        # Construct the URL for the current page
        url = base_url.format(page=page_number)
        print(f"Fetching page {page_number}: {url}")

        # Fetch the page content
        page_content = fetch_page(url)
        if page_content:
            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(page_content, 'html.parser')

            # Extract and save content from <p> tags around the specific markers
            extract_and_save_content(soup, file, page_number)

            # Check if the content is empty or repetitive
            # in order to be able to stop and not run into infinite loop
            current_content = soup.get_text()
            if not current_content.strip() or current_content == last_content:
                empty_page_counter += 1
                if empty_page_counter >= 3:  # Assuming 3 consecutive empty or repetitive pages indicate the end
                    print(f"Detected end of book at page {page_number - 3}. Stopping.")
                    break
            else:
                empty_page_counter = 0  # Reset counter if new content is found
            last_content = current_content

            # Move to the next page and proceed to the next iteration
            page_number += 1
        else:
            print(f"Page {page_number} does not exist. Stopping.")
            break

print("Book parsing completed.")


# Convert the .txt file to .mobi using ebook-convert

# To convert a .txt file into .mobi format,
# I'll be using the ebook-convert tool,
# which is part of the Calibre suite.

# Calibre is a powerful e-book management software
# that supports various conversion formats.
def convert_txt_to_mobi(txt_file, mobi_file):
    try:
        subprocess.run(['ebook-convert', txt_file, mobi_file], check=True)
        print(f"Conversion to {mobi_file} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")

convert_txt_to_mobi(output_file, mobi_file)
