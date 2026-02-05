import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.daiict.ac.in"
faculty_pages = {
    "faculty": f"{BASE_URL}/faculty",
    "adjunct": f"{BASE_URL}/adjunct-faculty",
    "adjunct_international": f"{BASE_URL}/adjunct-faculty-international",
    "distinguished_professor": f"{BASE_URL}/distinguished-professor",
    "professor_of_practice": f"{BASE_URL}/professor-practice"
}

def fetch_faculty_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
        faculty_blocks = soup.find_all("div", class_="facultyDetails")
        return faculty_blocks
    else:
        print(f"Failed to fetch {url} with status code {response.status_code}")
        return []

# Loop through each page and collect faculty data
all_faculty_data = {}
for category, url in faculty_pages.items():
    print(f"Fetching data from: {category}")
    faculty_info = fetch_faculty_data(url)
    all_faculty_data[category] = faculty_info

# Print names from each category
for category, blocks in all_faculty_data.items():
    print(f"\n{category.upper()} FACULTY:")
    for block in blocks:
        name_tag = block.find('h3')
        if name_tag:
            print(name_tag.text.strip())
