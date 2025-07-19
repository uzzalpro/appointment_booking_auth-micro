import json
from pathlib import Path
from typing import Dict, List
import os

def load_location_data() -> Dict:
    """Load location data from JSON file"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    static_path = os.path.join(project_root, "static", "bd-dd-ui-en.JSON")
    with open(static_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_divisions() -> List[str]:
    """Get all division names"""
    data = load_location_data()
    return [div["name"] for div in data["divisions"]]

def get_districts(division: str) -> List[str]:
    """Get districts for a division"""
    data = load_location_data()
    for div in data["divisions"]:
        if div["name"].lower() == division.lower():
            return [dist["name"] for dist in div["districts"]]
    return []

def get_upazilas(division: str, district: str) -> List[str]:
    """Get upazilas/thanas for a district"""
    data = load_location_data()
    for div in data["divisions"]:
        if div["name"].lower() == division.lower():
            for dist in div["districts"]:
                if dist["name"].lower() == district.lower():
                    if isinstance(dist["upazilas"][0], str):
                        return dist["upazilas"]
                    return [upazila["name"] for upazila in dist["upazilas"]]
    return []