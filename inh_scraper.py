#%% Scrape website
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import csv

from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()
driver = webdriver.Chrome()

options = Options()
browser = webdriver.Chrome(options=options)

keys = ['Hydropsyche', 'Baetis', 'Tipula']

for key in keys:
    url = 'http://inhsinsectcollection.speciesfile.org/InsectCollection.aspx'
    browser.get(url)

    # Fill out the form
    browser.find_element('id','grdvSearchForm_ctl02_tbxSearchTerm').send_keys(key)
    browser.find_element('id', 'ddlPageSize').send_keys('200')
    browser.find_element('id', 'btnSearch').click()

    # Wait for the table to load
    browser.implicitly_wait(10)

    # Get the HTML content of the page
    html = browser.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find the table
    table = soup.find('table', id='grdvResults')

    import csv

    header = []
    table_header = table.find('tr')
    for th in table_header.find_all('th'):
        header.append(th.text)

    # Open a CSV file for writing
    with open(f'raw_data/{key}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)

        lbl_record_number = soup.find("span", id="lblRecordNumber").text
        total_pages = int(re.search(r"of (\d+)", lbl_record_number).group(1))

        next_page = 1
        while next_page <= total_pages:
            # Execute the JavaScript to navigate to the next page
            browser.execute_script(f"__doPostBack('grdvResults','Page${next_page}')")
        
            # Wait for the page to load
            browser.implicitly_wait(10)
        
            # Get the HTML content of the page
            html = browser.page_source
        
            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
        
            # Find the table
            table = soup.find('table', id='grdvResults')
        
            # Extract the data from the table
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                writer.writerow([cell.text for cell in cells])
        
            # Move to the next page
            next_page += 1

browser.quit()