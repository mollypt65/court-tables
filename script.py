import os
import requests
import tabula
from bs4 import BeautifulSoup
import pandas as pd
# webhook = os.getenv("CHAT_WEBHOOK")
#
# if not webhook:
#     raise ValueError("CHAT_WEBHOOK not set!")
#
# message = {"text": "🤖 Hello from GitHub Actions!"}
# response = requests.post(webhook, json=message)
# response.raise_for_status()
#
# print("Message sent!")

'''
Get link to court schedule pdf 
'''
def get_url():
    url = "https://www.nysd.uscourts.gov/about/news-and-events"
    # Fetch the page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            if 'Proceedings' in link_str:
                pdf_path = 'https://www.nysd.uscourts.gov/' + link_str
                print("PDF: ", pdf_path)
                return pdf_path

'''
Read first page of the PDF
'''
def build_table(pdf_path):
    # Read the table from the PDF on page 1 excluding header stuff
    dfs = tabula.read_pdf(pdf_path, area=[170, 0, 1000, 1000], pages=1, multiple_tables=True)

    # Get first table
    df = dfs[0]

    # Rename columns
    df.columns = ['Case Name', 'Case No.', 'Proceeding', 'Judge', 'Room/Telephone', 'Date', 'Time', 'NA']
    df = df.drop(columns=['NA'])

    # Rename df
    first_table = df

    # Get tables on all pages after first
    all_tables = tabula.read_pdf(pdf_path, pages='all', pandas_options={'header': None}, multiple_tables=True)
    for table in all_tables[1:]:
        table = table.drop(columns=[0, 8])
        table.columns = ['Case Name', 'Case No.', 'Proceeding', 'Judge', 'Room/Telephone', 'Date', 'Time']
        first_table = pd.concat([first_table, table], axis=0)

    pd.set_option('display.max_rows', None)
    all_cases = first_table.reset_index(drop=True)
    return all_cases

def main():
    path_url = get_url()
    table = build_table(path_url)
    print(table.head())
    print(table.to_csv())


    webhook = os.getenv("CHAT_WEBHOOK")
    #
    if not webhook:
        raise ValueError("CHAT_WEBHOOK not set!")

    message = {"text": table.to_csv()}
    response = requests.post(webhook, json=message)
    response.raise_for_status()

    print("Message sent!")


if __name__ == '__main__':
    main()