import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.daiict.ac.in"
faculty_pages = {
    "faculty": f"{BASE_URL}/faculty",
    "adjunct": f"{BASE_URL}/adjunct-faculty",
    "adjunct_international": f"{BASE_URL}/adjunct-faculty-international",
    "distinguished_professor": f"{BASE_URL}/distinguished-professor",
    "professor_of_practice": f"{BASE_URL}/professor-practice"
}

class Faculty:
    def __init__(self, name="Not provided", specialization="Not provided",
                 education="Not provided", number="Not provided",
                 address="Not provided", email="Not provided",
                 biography="Not provided", publications="Not provided"):
        self.name = name.strip()
        self.specialization = specialization.strip()
        self.education = education.strip()
        self.number = number.strip()
        self.address = address.strip()
        self.email = email.strip()
        self.biography = biography.strip()
        self.publications = publications.strip()

    def __repr__(self):
        return (f"{self.name} | {self.specialization} | {self.education} | "
                f"{self.number} | {self.address} | {self.email} | "
                f"{self.biography} | {self.publications}")


FOOTER_KEYWORDS = [
    "Reliance", "Contact Us", "Admissions", "Follow Us", "facebook",
    "Instagram", "LinkedIn", "Gandhinagar", "DA-IICT Road",
    "For Admission Enquiries", "Support Ticket", "Scholarships",
    "Undergraduate", "Postgraduate", "Doctoral Program"
]

def clean_footer_text(text):
    for kw in FOOTER_KEYWORDS:
        if kw.lower() in text.lower():
            text = text.split(kw)[0]
    return re.sub(r"\s+", " ", text).strip()

def extract_faculty_listing(block):
    name = block.find("h3").get_text(strip=True) if block.find("h3") else "Not provided"

    spec_div = block.find("div", class_="areaSpecialization")
    specialization = spec_div.find("p").get_text(strip=True) if spec_div and spec_div.find("p") else "Not provided"

    edu_div = block.find("div", class_="facultyEducation")
    education = edu_div.get_text(strip=True) if edu_div else "Not provided"

    contact = block.find("div", class_="contactDetails")
    number = contact.find("span", class_="facultyNumber").get_text(strip=True) if contact and contact.find("span", class_="facultyNumber") else "Not provided"
    address = contact.find("span", class_="facultyAddress").get_text(strip=True) if contact and contact.find("span", class_="facultyAddress") else "Not provided"
    email = contact.find("span", class_="facultyemail").get_text(strip=True) if contact and contact.find("span", class_="facultyemail") else "Not provided"

    return name, specialization, education, number, address, email

def extract_faculty_profile(url):
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    container = soup.find("div", class_="rit-cover")

    if not container:
        return "Not provided", "Not provided"

    def get_section(title):
        heading = container.find(
            lambda t: t.name in ["h2", "h3"] and title.lower() in t.get_text(strip=True).lower()
        )
        if not heading:
            return "Not provided"

        content = []
        for elem in heading.next_elements:
            if getattr(elem, "name", None) in ["h2", "h3"]:
                break
            if getattr(elem, "name", None) in ["p", "li"]:
                text = elem.get_text(" ", strip=True)
                if text:
                    content.append(text)

        final_text = clean_footer_text(" ".join(content))
        return final_text if final_text else "Not provided"

    biography = get_section("biography")
    publications = get_section("publications")

    return biography, publications

def build_faculty(block):
    name, specialization, education, number, address, email = extract_faculty_listing(block)
    profile_url = block.find("a")["href"]
    biography, publications = extract_faculty_profile(profile_url)

    return Faculty(
        name, specialization, education,
        number, address, email,
        biography, publications
    )


all_faculty_records = {}

for category, url in faculty_pages.items():
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    all_faculty_records[category] = [
        build_faculty(block)
        for block in soup.find_all("div", class_="facultyDetails")
        if block.find("a")
    ]

for category, records in all_faculty_records.items():
    print(f"\n{'='*60}")
    print(f"{category.upper()} FACULTY RECORDS")
    print(f"{'='*60}")
    for i, rec in enumerate(records, 1):
        print(f"{i}. {rec}")
