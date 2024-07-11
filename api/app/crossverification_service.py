from fuzzywuzzy import fuzz
import dateparser
from app.models import DocumentInfo

def cross_verify(doc_info: DocumentInfo, spoken_text: str) -> float:
    name_match = compare_name(doc_info.name, spoken_text)
    dob_match = compare_dob(doc_info.dob, spoken_text)
    address_match = compare_address(doc_info.address, spoken_text)
    
    return (name_match + dob_match + address_match) / 3

def compare_name(doc_name: str, spoken_text: str) -> float:
    return fuzz.token_sort_ratio(doc_name.lower(), spoken_text.lower()) / 100

def compare_dob(doc_dob: str, spoken_text: str) -> float:
    doc_date = dateparser.parse(doc_dob)
    spoken_date = dateparser.search.search_dates(spoken_text)
    
    if doc_date and spoken_date:
        spoken_date = spoken_date[0][1]
        if doc_date.date() == spoken_date.date():
            return 1.0
    return 0.0

def compare_address(doc_address: str, spoken_text: str) -> float:
    return fuzz.partial_ratio(doc_address.lower(), spoken_text.lower()) / 100