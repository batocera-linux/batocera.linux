#!/usr/bin/env python3
"""
VPX Media Scraper

@lbrpdx for Batocera -- this program is free and open source given as is, but this header must
always be kept untouched and distributed along any modified version of this file.

This script processes .vpx files in /userdata/roms/vpinball, matches them with
the VPS database, downloads media files, and updates gamelist.xml.

Thanks to superhac for maintening a database of VPX metadata.
"""
import os
import json
import re
import csv
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from difflib import SequenceMatcher
from urllib.parse import urljoin
from typing import Dict, List, Optional, Tuple
from io import StringIO

class VPXProcessor:
    def __init__(self):
        self.vpx_directory = Path("/userdata/roms/vpinball")
        self.gamelist_path = self.vpx_directory / "gamelist.xml"
        self.vpsdb_url = "https://raw.githubusercontent.com/VirtualPinballSpreadsheet/vps-db/refs/heads/main/db/vpsdb.json"
        self.puplookup_url = "https://raw.githubusercontent.com/VirtualPinballSpreadsheet/vps-db/refs/heads/main/db/puplookup.csv"
        self.media_base_url = "https://raw.githubusercontent.com/superhac/vpinmediadb/main/"
        self.vpsdb_data = None
        self.puplookup_data = None

    def download_puplookup_csv(self) -> bool:
        """Download the PUP lookup CSV file."""
        try:
            print("Downloading PUP lookup CSV...")
            response = requests.get(self.puplookup_url, timeout=30)
            response.raise_for_status()

            # Parse CSV data
            csv_content = StringIO(response.text)
            csv_reader = csv.DictReader(csv_content)
            self.puplookup_data = list(csv_reader)

            print(f"Downloaded PUP lookup CSV with {len(self.puplookup_data)} entries")
            return True
        except Exception as e:
            print(f"Error downloading PUP lookup CSV: {e}")
            return False

    def download_vpsdb(self) -> bool:
        """Download the VPS database JSON file."""
        try:
            print("Downloading VPS database...")
            response = requests.get(self.vpsdb_url, timeout=30)
            response.raise_for_status()
            self.vpsdb_data = response.json()
            print(f"Downloaded VPS database with {len(self.vpsdb_data)} entries")
            return True
        except Exception as e:
            print(f"Error downloading VPS database: {e}")
            return False

    def find_vpx_files(self) -> List[Path]:
        """Find all .vpx files in the directory and subdirectories."""
        vpx_files = []
        for root, dirs, files in os.walk(self.vpx_directory):
            for file in files:
                if file.lower().endswith('.vpx'):
                    vpx_files.append(Path(root) / file)

        print(f"Found {len(vpx_files)} VPX files")
        return vpx_files

    def extract_year_from_filename(self, filename: str) -> Optional[str]:
        """Extract year from filename (4-digit number between 1930 and 2030)."""
        matches = re.findall(r'\b(19[3-9]\d|20[0-2]\d|2030)\b', filename)
        return matches[0] if matches else None

    def extract_version_from_filename(self, filename: str) -> Optional[str]:
        """Extract version number from filename (e.g., 1.0.2, v2.1, etc.)."""
        # Look for version patterns like 1.0.2, v2.1, V1.5, etc.
        patterns = [
            r'[vV]?(\d+\.\d+(?:\.\d+)*)',  # v1.0.2, 1.0.2, V2.1
            r'[vV](\d+(?:\.\d+)*)',        # v1, V2
        ]

        for pattern in patterns:
            matches = re.findall(pattern, filename)
            if matches:
                return matches[-1]  # Return the last match (likely the version)
        return None

    def search_puplookup_csv(self, vpx_filename: str) -> List[Dict]:
        """Search for matches in the PUP lookup CSV based on GameFileName."""
        if not self.puplookup_data:
            return []

        # Remove .vpx extension for matching
        clean_filename = Path(vpx_filename).stem

        matches = []

        for row in self.puplookup_data:
            game_filename = row.get('GameFileName', '').strip()
            if not game_filename:
                continue

            # Direct exact match first (case insensitive)
            if clean_filename.lower() == game_filename.lower():
                matches.append({
                    'row': row,
                    'ratio': 1.0,
                    'match_type': 'exact'
                })
                continue

            # Fuzzy matching
            ratio = SequenceMatcher(None, clean_filename.lower(), game_filename.lower()).ratio()
            if ratio >= 0.85:  # High threshold for CSV matching
                matches.append({
                    'row': row,
                    'ratio': ratio,
                    'match_type': 'fuzzy'
                })

        # Sort by ratio (best matches first)
        matches.sort(key=lambda x: x['ratio'], reverse=True)

        if matches:
            print(f"Found {len(matches)} CSV matches for '{vpx_filename}':")
            for i, match in enumerate(matches[:5]):  # Show top 5 matches
                print(f"  {i+1}. {match['row'].get('GameFileName', '')} (confidence: {match['ratio']:.2f}, {match['match_type']})")

        return matches

    def get_vps_id_from_csv(self, csv_row: Dict) -> Optional[str]:
        """Extract VPS-ID from CSV row."""
        vps_id = csv_row.get('VPS-ID', '').strip()
        return vps_id if vps_id else None

    def find_vpsdb_by_id(self, vps_id: str) -> Optional[Dict]:
        """Find entry in VPS database by exact ID match."""
        if not self.vpsdb_data or not vps_id:
            return None

        for entry in self.vpsdb_data:
            if entry.get('id') == vps_id:
                print(f"Found VPS database entry for ID: {vps_id}")
                return entry

        return None

    def merge_csv_and_json_data(self, csv_row: Dict, json_entry: Optional[Dict]) -> Dict:
        """Merge data from CSV and JSON, prioritizing CSV where available."""
        merged_data = {}

        # Start with JSON data if available
        if json_entry:
            merged_data.update(json_entry)

        # Override with CSV data where available
        if csv_row.get('Manufact'):
            merged_data['manufacturer'] = csv_row['Manufact'].strip()

        if csv_row.get('Author'):
            # Split authors by common delimiters and clean up
            authors = []
            author_text = csv_row['Author'].strip()
            # Split by various delimiters
            for delimiter in [',', '&', ' and ', '/']:
                if delimiter in author_text:
                    authors = [a.strip() for a in author_text.split(delimiter) if a.strip()]
                    break
            if not authors and author_text:
                authors = [author_text]
            merged_data['authors'] = authors

        if csv_row.get('GameYear'):
            try:
                year = int(csv_row['GameYear'].strip())
                merged_data['year'] = year
            except (ValueError, AttributeError):
                pass

        if csv_row.get('NumPlayers'):
            merged_data['players'] = csv_row['NumPlayers'].strip()

        # Use GameFileName as name if no name is available
        if csv_row.get('GameFileName') and not merged_data.get('name'):
            merged_data['name'] = csv_row['GameFileName'].strip()

        return merged_data

    def count_populated_fields(self, entry: Dict) -> int:
        """Count the number of populated fields in a JSON entry."""
        count = 0
        for key, value in entry.items():
            if value:  # Check if value is not None, empty string, or empty list
                if isinstance(value, list) and len(value) > 0:
                    count += 1
                elif isinstance(value, str) and value.strip():
                    count += 1
                elif not isinstance(value, (str, list)):
                    count += 1
        return count

    def test_media_completeness(self, game_id: str) -> Tuple[int, Dict[str, bool]]:
        """Test media completeness for a given game ID and return score and availability."""
        wheel_exists, cab_exists, fss_exists = self.check_media_exists(game_id)

        media_status = {
            'wheel': wheel_exists,
            'cab': cab_exists,
            'fss': fss_exists
        }

        # Calculate completeness score
        score = sum(media_status.values())

        return score, media_status

    def find_best_vps_id_by_media(self, candidate_ids: List[str], vpx_filename: str) -> Tuple[Optional[str], Dict[str, bool]]:
        """Try multiple VPS IDs and return the one with most complete media files."""
        best_id = None
        best_score = -1
        best_media_status = {}

        print(f"Testing media availability for {len(candidate_ids)} candidate VPS IDs...")

        for i, vps_id in enumerate(candidate_ids):
            print(f"  Testing VPS ID {i+1}/{len(candidate_ids)}: {vps_id}")
            score, media_status = self.test_media_completeness(vps_id)

            available_media = [media for media, available in media_status.items() if available]
            print(f"    Available media: {', '.join(available_media) if available_media else 'none'} (score: {score}/3)")

            if score > best_score:
                best_score = score
                best_id = vps_id
                best_media_status = media_status
                print(f"    ^ New best candidate (score: {score}/3)")

            # If we found a perfect match (all 3 media files), stop searching
            if score == 3:
                print(f"    Perfect match found! Using VPS ID: {vps_id}")
                break

        if best_id:
            available_media = [media for media, available in best_media_status.items() if available]
            print(f"Selected VPS ID '{best_id}' with {best_score}/3 media files: {', '.join(available_media) if available_media else 'none'}")
        else:
            print("No suitable VPS ID found with available media")

        return best_id, best_media_status

    def fuzzy_match_name(self, vpx_filename: str) -> Optional[Dict]:
        """Find the best matching entry using CSV first, then VPS database, testing media availability."""
        candidate_ids = []
        candidate_data = []

        # First, try to find matches in the CSV
        csv_matches = self.search_puplookup_csv(vpx_filename)
        for csv_match in csv_matches:
            vps_id = self.get_vps_id_from_csv(csv_match['row'])
            if vps_id and vps_id not in candidate_ids:
                candidate_ids.append(vps_id)
                # Try to find corresponding JSON entry
                json_match = self.find_vpsdb_by_id(vps_id)
                merged_data = self.merge_csv_and_json_data(csv_match['row'], json_match)
                merged_data['source'] = 'csv'
                merged_data['confidence'] = csv_match['ratio']
                candidate_data.append(merged_data)

        # If no CSV matches or CSV matches don't have complete media, try JSON fuzzy matching
        json_candidates = self.fuzzy_match_json_only(vpx_filename)
        for json_candidate in json_candidates:
            json_entry = json_candidate['entry']
            if json_entry.get('id') and json_entry['id'] not in candidate_ids:
                candidate_ids.append(json_entry['id'])
                json_entry['source'] = 'json'
                json_entry['confidence'] = json_candidate['ratio']
                candidate_data.append(json_entry)

        if not candidate_ids:
            print(f"No candidate VPS IDs found for '{vpx_filename}'")
            return None

        # Test media availability for all candidates
        best_vps_id, media_status = self.find_best_vps_id_by_media(candidate_ids, vpx_filename)

        if not best_vps_id:
            print(f"No VPS ID with available media found for '{vpx_filename}'")
            return None

        # Find the corresponding data for the best VPS ID
        best_data = None
        for data in candidate_data:
            if data.get('id') == best_vps_id:
                best_data = data
                break

        if not best_data:
            print(f"Error: Could not find data for selected VPS ID {best_vps_id}")
            return None

        # Add media status to the data
        best_data['media_status'] = media_status

        print(f"Final selection for '{vpx_filename}': '{best_data.get('name', 'Unknown')}' " +
              f"(ID: {best_vps_id}, source: {best_data.get('source', 'unknown')}, " +
              f"confidence: {best_data.get('confidence', 0):.2f})")

        return best_data

    def fuzzy_match_json_only(self, vpx_filename: str) -> List[Dict]:
        """Original fuzzy matching logic for JSON database only, returning multiple candidates."""
        if not self.vpsdb_data:
            return []

        # Extract additional info from filename
        extracted_year = self.extract_year_from_filename(vpx_filename)
        extracted_version = self.extract_version_from_filename(vpx_filename)

        # Clean the filename for better matching
        clean_name = self.clean_filename(vpx_filename)

        candidates = []

        for entry in self.vpsdb_data:
            if 'name' not in entry:
                continue

            # Base name matching
            name_ratio = SequenceMatcher(None, clean_name.lower(), entry['name'].lower()).ratio()

            # Also check alternative names if they exist
            if 'altNames' in entry:
                for alt_name in entry['altNames']:
                    alt_ratio = SequenceMatcher(None, clean_name.lower(), alt_name.lower()).ratio()
                    name_ratio = max(name_ratio, alt_ratio)

            if name_ratio < 0.6:  # Skip if name match is too low
                continue

            total_ratio = name_ratio
            bonus_points = 0

            # Year matching bonus
            if extracted_year and 'year' in entry and entry['year']:
                if str(extracted_year) == str(entry['year']):
                    bonus_points += 0.2  # Significant bonus for exact year match
                elif abs(int(extracted_year) - int(entry['year'])) <= 1:
                    bonus_points += 0.1  # Small bonus for close year match

            # Version matching bonus
            if extracted_version and 'version' in entry and entry['version']:
                version_ratio = SequenceMatcher(None, extracted_version.lower(), 
                                              str(entry['version']).lower()).ratio()
                if version_ratio > 0.8:
                    bonus_points += 0.15  # Bonus for good version match

            final_ratio = total_ratio + bonus_points
            populated_fields = self.count_populated_fields(entry)

            candidates.append({
                'entry': entry,
                'ratio': final_ratio,
                'populated_fields': populated_fields,
                'name_ratio': name_ratio
            })

        if not candidates:
            print(f"No JSON matches found for '{vpx_filename}'")
            return []

        # Sort by ratio first, then by populated fields for tie-breaking
        candidates.sort(key=lambda x: (x['ratio'], x['populated_fields']), reverse=True)

        # Return top candidates that are close to the best match
        best_ratio = candidates[0]['ratio']
        good_candidates = [c for c in candidates if c['ratio'] >= best_ratio - 0.1]  # Within 0.1 of best

        if good_candidates:
            print(f"Found {len(good_candidates)} JSON candidates for '{vpx_filename}':")
            for i, candidate in enumerate(good_candidates[:5]):  # Show top 5
                print(f"  {i+1}. {candidate['entry']['name']} (confidence: {candidate['ratio']:.2f})")

        if extracted_year:
            print(f"  Extracted year: {extracted_year}")
        if extracted_version:
            print(f"  Extracted version: {extracted_version}")

        return good_candidates

    def clean_filename(self, filename: str) -> str:
        """Clean filename for better matching."""
        # Remove file extension
        name = Path(filename).stem

        # Remove common patterns
        patterns = [
            r'\([^)]*\)',  # Remove parentheses content
            r'\[[^\]]*\]',  # Remove brackets content
            r'_+',          # Replace multiple underscores
            r'-+',          # Replace multiple dashes
            r'\s+',         # Replace multiple spaces
        ]

        for pattern in patterns:
            name = re.sub(pattern, ' ', name)

        return name.strip()

    def check_media_exists(self, game_id: str) -> Tuple[bool, bool, bool]:
        """Check if wheel.png, cab.png, and fss.png exist for the given game ID."""
        wheel_url = f"{self.media_base_url}{game_id}/wheel.png"
        cab_url = f"{self.media_base_url}{game_id}/cab.png"
        fss_url = f"{self.media_base_url}{game_id}/1k/fss.png"

        try:
            wheel_response = requests.head(wheel_url, timeout=10)
            wheel_exists = wheel_response.status_code == 200
        except:
            wheel_exists = False

        try:
            cab_response = requests.head(cab_url, timeout=10)
            cab_exists = cab_response.status_code == 200
        except:
            cab_exists = False

        try:
            fss_response = requests.head(fss_url, timeout=10)
            fss_exists = fss_response.status_code == 200
        except:
            fss_exists = False

        return wheel_exists, cab_exists, fss_exists

    def download_media_file(self, game_id: str, media_type: str, vpx_name: str) -> Optional[Path]:
        """Download media file and rename it."""
        if media_type not in ['wheel', 'cab', 'fss']:
            return None

        # Set URL and filename based on media type
        if media_type == 'fss':
            url = f"{self.media_base_url}{game_id}/1k/fss.png"
            filename = f"{Path(vpx_name).stem}-image.png"  # fss becomes -image
        else:
            url = f"{self.media_base_url}{game_id}/{media_type}.png"
            filename = f"{Path(vpx_name).stem}-{media_type}.png"

        local_path = self.vpx_directory / "images" / filename

        # Create images directory if it doesn't exist
        local_path.parent.mkdir(exist_ok=True)

        try:
            print(f"Downloading {media_type} for {vpx_name}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded {filename}")
            return local_path

        except Exception as e:
            print(f"Error downloading {media_type} for {vpx_name}: {e}")
            return None

    def load_gamelist_xml(self) -> ET.Element:
        """Load existing gamelist.xml or create a new one."""
        if self.gamelist_path.exists():
            try:
                tree = ET.parse(self.gamelist_path)
                return tree.getroot()
            except ET.ParseError as e:
                print(f"Error parsing existing gamelist.xml: {e}")
                print("Creating new gamelist.xml")

        # Create new XML structure
        root = ET.Element("gameList")
        return root

    def find_existing_game(self, root: ET.Element, vpx_path: str) -> Optional[ET.Element]:
        """Find existing game entry in XML by path."""
        for game in root.findall('game'):
            path_elem = game.find('path')
            if path_elem is not None and path_elem.text == vpx_path:
                return game
        return None

    def update_game_element(self, game_elem: ET.Element, match_data: Dict, vpx_file: Path,
                           wheel_path: Optional[Path], cab_path: Optional[Path], 
                           fss_path: Optional[Path]) -> None:
        """Update an existing game XML element with new data while preserving other fields."""
        # Create display name with manufacturer suffix if available
        display_name = match_data.get('name', vpx_file.stem)
        manufacturer = match_data.get('manufacturer', '')
        if manufacturer:
            display_name += f" ({manufacturer})"

        # Fields to update
        updates = {
            'name': display_name,
            'publisher': manufacturer,
            'developer': ', '.join(match_data.get('authors', [])) if match_data.get('authors') else '',
            'genre': 'Pinball',
            'releasedate': f"{match_data.get('year', '')}0101T000000" if match_data.get('year') else '',
        }

        # Add players field if available
        if match_data.get('players'):
            updates['players'] = str(match_data['players'])

        # Add media paths if they exist
        if fss_path:  # FSS image goes to <image> field
            updates['image'] = f"./images/{fss_path.name}"
        if wheel_path:  # Wheel goes to <marquee> field
            updates['marquee'] = f"./images/{wheel_path.name}"
        if cab_path:  # Cabinet goes to <thumbnail> field
            updates['thumbnail'] = f"./images/{cab_path.name}"

        # Update existing elements or create new ones
        for field_name, new_value in updates.items():
            if not new_value:  # Skip empty values
                continue

            # Find existing element
            existing_elem = game_elem.find(field_name)
            if existing_elem is not None:
                # Update existing element
                existing_elem.text = str(new_value)
            else:
                # Create new element
                new_elem = ET.SubElement(game_elem, field_name)
                new_elem.text = str(new_value)

    def create_game_element(self, match_data: Dict, vpx_file: Path, 
                          wheel_path: Optional[Path], cab_path: Optional[Path], 
                          fss_path: Optional[Path]) -> ET.Element:
        """Create a new game XML element."""
        game = ET.Element('game')

        # Relative path from vpx_directory
        rel_path = f"./{vpx_file.relative_to(self.vpx_directory)}"

        # Create display name with manufacturer suffix if available
        display_name = match_data.get('name', vpx_file.stem)
        manufacturer = match_data.get('manufacturer', '')
        if manufacturer:
            display_name += f" ({manufacturer})"

        # Required elements
        elements = {
            'path': rel_path,
            'name': display_name,
            'publisher': manufacturer,
            'developer': ', '.join(match_data.get('authors', [])) if match_data.get('authors') else '',
            'genre': 'Pinball',
            'releasedate': f"{match_data.get('year', '')}0101T000000" if match_data.get('year') else '',
        }

        # Add players field if available
        if match_data.get('players'):
            elements['players'] = str(match_data['players'])

        # Add media paths if they exist
        if fss_path:  # FSS image goes to <image> field
            elements['image'] = f"./images/{fss_path.name}"
        if wheel_path:  # Wheel goes to <marquee> field
            elements['marquee'] = f"./images/{wheel_path.name}"
        if cab_path:  # Cabinet goes to <thumbnail> field
            elements['thumbnail'] = f"./images/{cab_path.name}"

        # Create XML elements
        for key, value in elements.items():
            if value:  # Only add non-empty values
                elem = ET.SubElement(game, key)
                elem.text = str(value)

        return game

    def save_gamelist_xml(self, root: ET.Element) -> bool:
        """Save the updated gamelist.xml."""
        try:
            # Create a backup of existing file
            if self.gamelist_path.exists():
                backup_path = self.gamelist_path.with_suffix('.xml.bak')
                self.gamelist_path.rename(backup_path)
                print(f"Backed up existing gamelist.xml to {backup_path}")

            # Pretty print XML
            self.indent_xml(root)

            tree = ET.ElementTree(root)
            tree.write(self.gamelist_path, encoding='utf-8', xml_declaration=True)
            print(f"Saved updated gamelist.xml with {len(root.findall('game'))} games")
            return True

        except Exception as e:
            print(f"Error saving gamelist.xml: {e}")
            return False

    def indent_xml(self, elem: ET.Element, level: int = 0) -> None:
        """Add indentation to XML for pretty printing."""
        i = "\n" + level * "\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def process_all_vpx_files(self) -> None:
        """Main processing function."""
        print("Starting VPX file processing...")

        # Download both CSV and JSON databases
        if not self.download_puplookup_csv():
            print("Failed to download PUP lookup CSV. Continuing without CSV data.")

        if not self.download_vpsdb():
            print("Failed to download VPS database. Exiting.")
            return

        # Find all VPX files
        vpx_files = self.find_vpx_files()
        if not vpx_files:
            print("No VPX files found.")
            return

        # Load existing gamelist.xml
        root = self.load_gamelist_xml()

        # Process each VPX file
        processed_count = 0
        for vpx_file in vpx_files:
            print(f"\nProcessing: {vpx_file.name}")

            # Find matching entry (CSV first, then JSON fallback, with media testing)
            match_data = self.fuzzy_match_name(vpx_file.name)
            if not match_data or 'id' not in match_data:
                print(f"Skipping {vpx_file.name} - no valid match found")
                continue

            game_id = match_data['id']
            print(f"Found ID: {game_id}")

            # Use the pre-tested media status if available
            media_status = match_data.get('media_status', {})
            wheel_exists = media_status.get('wheel', False)
            cab_exists = media_status.get('cab', False)
            fss_exists = media_status.get('fss', False)

            # If media status wasn't pre-tested, check now
            if not media_status:
                wheel_exists, cab_exists, fss_exists = self.check_media_exists(game_id)

            wheel_path = None
            cab_path = None
            fss_path = None

            if wheel_exists:
                wheel_path = self.download_media_file(game_id, 'wheel', vpx_file.name)
            else:
                print(f"Wheel image not available for {vpx_file.name}")

            if cab_exists:
                cab_path = self.download_media_file(game_id, 'cab', vpx_file.name)
            else:
                print(f"Cabinet image not available for {vpx_file.name}")

            if fss_exists:
                fss_path = self.download_media_file(game_id, 'fss', vpx_file.name)
            else:
                print(f"FSS image not available for {vpx_file.name}")

            # Update XML
            rel_path = f"./{vpx_file.relative_to(self.vpx_directory)}"
            existing_game = self.find_existing_game(root, rel_path)

            if existing_game is not None:
                # Update existing entry while preserving other fields
                self.update_game_element(existing_game, match_data, vpx_file, wheel_path, cab_path, fss_path)
                print(f"Updated existing entry for {vpx_file.name}")
            else:
                # Create new game element
                new_game = self.create_game_element(match_data, vpx_file, wheel_path, cab_path, fss_path)
                root.append(new_game)
                print(f"Added new entry for {vpx_file.name}")

            processed_count += 1
            print(f"Processed {vpx_file.name} successfully")

        # Save updated XML
        if processed_count > 0:
            if self.save_gamelist_xml(root):
                print(f"\nProcessing complete! Updated {processed_count} games.")
            else:
                print("\nError saving gamelist.xml")
        else:
            print("\nNo games were processed successfully.")

def main():
    """Main entry point."""
    processor = VPXProcessor()
    processor.process_all_vpx_files()

if __name__ == "__main__":
    main()
