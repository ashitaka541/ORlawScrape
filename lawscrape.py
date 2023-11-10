import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

base_url = "https://www.oregonlegislature.gov/bills_laws/pages/ors"
original_set = set([
    "011", "013", "016", "023", "026", "027", "029", "032", "038", "039", "047-050", "057", "061", "064", "068-070", "076", "085", "089", "120-123",
     "134", "139-141", "143", "145", "148", "149", "154-155", "168", "170", "175", "181", "189", "207", "214", "216-220", "228-235", "239", "245", "252",
     "269", "281", "285", "286", "287", "288", "298", "252", "269", "281", "285-288", "298-304", "325", "331", "333", "351", "360-365", "375", "378-380", 
     "385", "392-395", "397", "400", "405", "422", "424", "425", "429", "434", "437", "449", "477", "481-495", "499", "500", "502-505", "514", "515", "518", 
     "519", "524", "525", "528", "531", "533-535", "544", "546", "556", "557", "559", "560", "562", "563", "572-575", "579", "585", "588-595", "597", "598", 
     "605", "606", "611-615", "620", "626", "627", "636-644", "664-669", "708", "721", "722", "724", "727", "736", "738-740", "745", "747", "749", "751",
     "753-755", "760-771", "773", "775", "781", "782", "784-800", "827-829"
     ])
excluded_pages = set()

for item in original_set:
    if '-' in item:
        start, end = map(int, item.split('-'))
        excluded_pages.update(map(str, range(start, end + 1)))
    else:
        excluded_pages.add(item)

additional_pages = set([
    "131A", "163A", "181A", "197A", "238A", "276A", "279A", "279B", "279C", "285A", "285B", "285C", "286A", "287A", "308A", "317A", "329A", "419A", "419B",
    "419C", "420A", "431A", "459A", "468A", "468B", "469A", "469B", "475A", "475C", "543A", "646A", "657B", "659A", "706A", "725A", "745A", "745B", "835-838"
])

def fetch_and_process_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <b> tags
        bold_tags = soup.find_all('b')

        # Initialize variables to store the dictionary
        result_dict = {}

        # Iterate through <b> tags to extract information
        for bold_tag in bold_tags:
            # Extract the key from the <b> tag
            key = bold_tag.text.strip()

            # Find the following sibling <span> tag
            span_tag = bold_tag.find_next('span')

            # Extract the text from the <span> tag
            value = span_tag.text.strip() if span_tag else ""

            # Save the key-value pair in the result dictionary
            result_dict[key] = value

        # Save the result dictionary to a file
        with open("result.csv", "a") as f:
            for key, value in result_dict.items():
                f.write(f"{key}, {value}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")

with ThreadPoolExecutor(max_workers=10) as executor:
    for page_suffix in range(1, 829):
        page_number = f"{page_suffix:03d}"

        if page_number in excluded_pages:
            continue

        url = f"{base_url}{page_number}.aspx"
        executor.submit(fetch_and_process_page, url)

    for additional_page in additional_pages:
        url = f"{base_url}{additional_page}.aspx"
        executor.submit(fetch_and_process_page, url)
