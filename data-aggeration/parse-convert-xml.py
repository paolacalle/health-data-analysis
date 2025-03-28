import xml.etree.ElementTree as ET
import csv
from datetime import datetime
import os

""" 
This script converts Apple Health export XML files into CSV format.
It can handle both the CDA-style export and the flat export.
The CDA-style export is more complex and includes nested elements.
The flat export is simpler and contains a single level of records.
The script includes functions to:
- Convert CDA-style export to CSV
- Convert flat export to CSV
- Export workouts to CSV
- Export activity summary to CSV
"""

def parse_cda_time(value):
    """Convert CDA time format to ISO datetime string."""
    try:
        dt = datetime.strptime(value[:14], "%Y%m%d%H%M%S")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    except Exception:
        return ""

def convert_export_cda(path="apple_health_export/export_cda.xml", output_path="apple_health_parsed_cda.csv"):
    """Convert CDA-style Apple Health export to CSV."""
    tree = ET.parse(path)
    root = tree.getroot()

    ns = {'cda': 'urn:hl7-org:v3'}
    csv_data = []

    for component in root.findall(".//cda:component", ns):
        obs = component.find("cda:observation", ns)
        if obs is None:
            continue

        try:
            code_elem = obs.find("cda:code", ns)
            text = obs.find("cda:text", ns)
            value_elem = obs.find("cda:value", ns)

            low = obs.find("cda:effectiveTime/cda:low", ns)
            high = obs.find("cda:effectiveTime/cda:high", ns)

            lowTime_raw = low.attrib.get("value", "") if low is not None else ""
            highTime_raw = high.attrib.get("value", "") if high is not None else ""
            
            startDate, startTime = parse_cda_time(lowTime_raw)
            endDate, endTime = parse_cda_time(highTime_raw)

            row = {
                "measurement": code_elem.attrib.get("displayName", "") if code_elem is not None else "",
                "value": value_elem.attrib.get("value", "") if value_elem is not None else "",
                "unit": value_elem.attrib.get("unit", "") if value_elem is not None else "",
                "source": text.findtext("cda:sourceName", default="", namespaces=ns) if text is not None else "",
                "sourceVersion": text.findtext("cda:sourceVersion", default="", namespaces=ns) if text is not None else "",
                # "type": text.findtext("cda:type", default="", namespaces=ns) if text is not None else "",
                "startDate": startDate,
                "endDate": endDate,
                "startTime": startTime,
                "endTime": endTime,
                "status": obs.find("cda:statusCode", ns).attrib.get("code", "") if obs.find("cda:statusCode", ns) is not None else ""
            }

            csv_data.append(row)

        except Exception as e:
            print(f"Skipping component due to error: {e}")
            continue

    if csv_data:
        write_to_csv(csv_data, output_path, csv_data[0].keys())
        print(f"Exported {len(csv_data)} CDA records to {output_path}")
    else:
        print("No CDA records found.")

def convert_export_record(path="apple_health_export/export.xml", output_path="apple_health_parsed.csv"):
    """Convert flat Apple Health export.xml to CSV."""
    tree = ET.parse(path)
    root = tree.getroot()

    records = []
    for record in root.findall("Record"):
        rec_data = record.attrib
        records.append({
            "type": rec_data.get("type", ""),
            "unit": rec_data.get("unit", ""),
            "value": rec_data.get("value", ""),
            "sourceName": rec_data.get("sourceName", ""),
            "sourceVersion": rec_data.get("sourceVersion", ""),
            # "device": rec_data.get("device", ""),
            "creationDate": rec_data.get("creationDate", ""),
            "startDate": rec_data.get("startDate", ""),
            "endDate": rec_data.get("endDate", "")
        })

    if records:
        write_to_csv(records, output_path, records[0].keys())
        print(f"Exported {len(records)} Record entries to {output_path}")
    else:
        print("No Record entries found.")
        
def export_workouts(path="apple_health_export/export.xml", output_path="apple_health_workouts.csv"):
    tree = ET.parse(path)
    root = tree.getroot()

    workouts = []
    for w in root.findall("Workout"):
        workouts.append({
            "activity": w.attrib.get("workoutActivityType"),
            "duration": w.attrib.get("duration"),
            "durationUnit": w.attrib.get("durationUnit"),
            "source": w.attrib.get("sourceName"),
            "startDate": w.attrib.get("startDate"),
            "endDate": w.attrib.get("endDate")
        })
        
    if workouts:
        write_to_csv(workouts, output_path, workouts[0].keys())
        print(f"Exported {len(workouts)} Record entries to {output_path}")
    else:
        print("No Record entries found.")
        
def export_active_summary(path="apple_health_export/export.xml", output_path="apple_health_active_summary.csv"):
    tree = ET.parse(path)
    root = tree.getroot()
    active_summary = []
    
    for summary in root.findall("ActivitySummary"):
        active_summary.append({
            "dateComponents": summary.attrib.get("dateComponents"),
            "activeEnergyBurned": summary.attrib.get("activeEnergyBurned"),
            "activeEnergyBurnedGoal": summary.attrib.get("activeEnergyBurnedGoal"),
            "activeEnergyBurnedUnit": summary.attrib.get("activeEnergyBurnedUnit"),
            "appleExerciseTime": summary.attrib.get("appleExerciseTime"),
            "appleExerciseTimeGoal": summary.attrib.get("appleExerciseTimeGoal"),
            "appleStandHours": summary.attrib.get("appleStandHours"),
            "appleStandHoursGoal": summary.attrib.get("appleStandHoursGoal"),
        })
        
    if active_summary:
        write_to_csv(active_summary, output_path, active_summary[0].keys())
        print(f"Exported {len(active_summary)} ActivitySummary entries to {output_path}")
    else:
        print("No ActivitySummary entries found.")

def write_to_csv(data, filename, headers):
    os.makedirs("parsed/", exist_ok=True)
    filename = os.path.join("parsed", filename)
    
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

def main():
    # Choose which to run — or both!
    # convert_export_cda()
    # convert_export_record()
    # export_workouts()
    export_active_summary()
    
if __name__ == "__main__":
    main()
