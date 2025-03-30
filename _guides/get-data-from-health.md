# Exporting Data from Apple Health (for Analysis)

1. Open the Health App on your iPhone.
2. Tap your profile icon (top right).
3. Scroll down and tap Export All Health Data.
4. AirDrop it to your Mac

The .zip will contain a file named export.xml.

# Convert to csv

The script `01-parse-convert-xml.py `located in `health-data-analysis/data-aggeration/` uses the `AppleHealthParser` to convert Apple Health XML exports into CSV files for easier analysis.


## How It Works
Run the script with:

```bash
python 01-parse-convert-xml.py <input_path> <output_path> [options]
```

Arguments:
- input_path: Path to your export.xml
- output_path: Destination for the generated CSV files

Optional Flags:
- --cda: Parse CDA-style exports
- --flat: Flatten nested structures
- --workouts: Include workouts data
- --active-summary: Include daily activity summary

# Getting the clean data

Run the commands in.

`/data-aggeration/02-combined-parsed-clean.Rmd`