import xml.etree.ElementTree as ET
import csv
from datetime import datetime
import os
import argparse

class AppleHealthParser:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = self.create_directory(output_path)

    @staticmethod
    def parse_cda_time(value):
        """Convert CDA time format to ISO datetime string."""
        try:
            dt = datetime.strptime(value[:14], "%Y%m%d%H%M%S")
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except Exception:
            return "", ""

    @staticmethod
    def write_to_csv(data, filename, headers):
        with open(filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def create_directory(path):
        """Create the directory if it doesn't exist."""
        file_name = __file__.split(".")[0].split("/")[-1]
        full_output_path = os.path.join(path, file_name)
        os.makedirs(full_output_path, exist_ok=True)
        return full_output_path

    def convert_export_cda(self, input_filename="export_cda.xml", output_filename="apple_health_parsed_cda.csv"):
        input_file = os.path.join(self.input_path, input_filename)
        tree = ET.parse(input_file)
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

                startDate, startTime = self.parse_cda_time(lowTime_raw)
                endDate, endTime = self.parse_cda_time(highTime_raw)

                row = {
                    "type": text.findtext("cda:type", default="", namespaces=ns) if text is not None else "",
                    # "measurement": code_elem.attrib.get("displayName", "") if code_elem is not None else "",
                    "value": value_elem.attrib.get("value", "") if value_elem is not None else "",
                    "unit": value_elem.attrib.get("unit", "") if value_elem is not None else "",
                    "source": text.findtext("cda:sourceName", default="", namespaces=ns) if text is not None else "",
                    "sourceVersion": text.findtext("cda:sourceVersion", default="", namespaces=ns) if text is not None else "",
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
            output_file = os.path.join(self.output_path, output_filename)
            self.write_to_csv(csv_data, output_file, csv_data[0].keys())
            print(f"Exported {len(csv_data)} CDA records to {output_file}")
        else:
            print("No CDA records found.")

    def dynamic_export_parse(self, columns_to_extract, tag_name, output_filename, input_filename="export.xml"):
        input_file = os.path.join(self.input_path, input_filename)
        tree = ET.parse(input_file)
        root = tree.getroot()

        records = []
        for record in root.findall(tag_name):
            rec_data = record.attrib
            records.append({col: rec_data.get(col, "") for col in columns_to_extract})

        if records:
            output_file = os.path.join(self.output_path, output_filename)
            self.write_to_csv(records, output_file, records[0].keys())
            print(f"Exported {len(records)} {tag_name} entries to {output_file}")
        else:
            print(f"No {tag_name} entries found.")

    def convert_export_record(self, output_filename="apple_health_record.csv"):
        columns_to_extract = [
            "type",
            "unit",
            "value",
            "sourceName",
            "sourceVersion",
            "creationDate",
            "startDate",
            "endDate"
        ]
        self.dynamic_export_parse(columns_to_extract, "Record", output_filename)

    def export_workouts(self, output_filename="apple_health_workout.csv"):
        columns_to_extract = [
            "workoutActivityType",
            "duration",
            "durationUnit",
            "sourceName",
            "startDate",
            "endDate"
        ]
        self.dynamic_export_parse(columns_to_extract, "Workout", output_filename)

    def export_active_summary(self, output_filename="apple_health_active_summary.csv"):
        columns_to_extract = [
            "dateComponents",
            "activeEnergyBurned",
            "activeEnergyBurnedGoal",
            "activeEnergyBurnedUnit",
            "appleExerciseTime",
            "appleExerciseTimeGoal",
            "appleStandHours",
            "appleStandHoursGoal"
        ]
        self.dynamic_export_parse(columns_to_extract, "ActivitySummary", output_filename)


def main(input_path, output_path, cda=False, flat=False, workouts=False, active_summary=False):
    parser = AppleHealthParser(input_path, output_path)

    if cda:
        parser.convert_export_cda()
    if flat:
        parser.convert_export_record()
    if workouts:
        parser.export_workouts()
    if active_summary:
        parser.export_active_summary()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Apple Health export XML files to CSV format.")
    parser.add_argument("input_path", help="Path to the Apple Health export XML file")
    parser.add_argument("output_path", help="Output path for the CSV file")
    parser.add_argument("--cda", action="store_true", help="Convert CDA-style export")
    parser.add_argument("--flat", action="store_true", help="Convert flat export")
    parser.add_argument("--workouts", action="store_true", help="Export workouts")
    parser.add_argument("--active-summary", action="store_true", help="Export activity summary")
    args = parser.parse_args()

    main(args.input_path, args.output_path, args.cda, args.flat, args.workouts, args.active_summary)
