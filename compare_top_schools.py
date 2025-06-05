#!/usr/bin/env python3

import sys
import subprocess
import pandas as pd
import re

def get_top_schools_grouped(earlier_file):
    """Run the original script and group top schools by category."""
    try:
        result = subprocess.run(
            ["./top_schools_report_out_v1.py", earlier_file],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout
        groups = {"High School": [], "Middle School": [], "Elementary School": []}

        current_group = None
        for line in output.splitlines():
            if "High Schools" in line:
                current_group = "High School"
            elif "Middle Schools" in line:
                current_group = "Middle School"
            elif "Elementary Schools" in line:
                current_group = "Elementary School"
            elif line.strip().startswith("") and current_group:
                match = re.match(r'^\s*(.+?) \(.+?\): \d+\.?\d*% proficient', line)
                if match:
                    groups[current_group].append(match.group(1).strip())

        return groups

    except subprocess.CalledProcessError as e:
        print("Error running top_schools_report_out_v1.py:", e.stderr)
        sys.exit(1)


def load_and_normalize(filename):
    """Load Excel and normalize proficiency column."""
    df = pd.read_excel(filename)
    df = df[df['Student Group'].str.contains('Total Population', case=False, na=False)]

    if 'Percent Proficient (Level 3 or 4)' in df.columns:
        prof_col = 'Percent Proficient (Level 3 or 4)'
    elif 'Percent Proficient' in df.columns:
        prof_col = 'Percent Proficient'
    else:
        raise ValueError(f"Proficiency column not found in {filename}")

    df = df[pd.to_numeric(df[prof_col], errors='coerce').notnull()]
    df[prof_col] = df[prof_col].astype(float)

    return df, prof_col


def compare_performance_grouped(groups, df_early, prof_col_early, df_late, prof_col_late):
    for group_name, schools in groups.items():
        print(f"\nPerformance Comparison of Top 10 {group_name}s:\n")
        if not schools:
            print("  No schools found in this category.")
            continue

        for school_name in schools:
            early_match = df_early[df_early['School'].str.contains(school_name, case=False, na=False)]
            later_match = df_late[df_late['School'].str.contains(school_name, case=False, na=False)]

            # Both found
            if not early_match.empty and not later_match.empty:
                early_score = early_match.iloc[0][prof_col_early]
                later_score = later_match.iloc[0][prof_col_late]
                change = later_score - early_score
                trend = (
                    "Improved 📈" if change > 1 else
                    "Declined 📉" if change < -1 else
                    "Stable ➖"
                )
                print(f"  {school_name}: {early_score:.1f}% → {later_score:.1f}% ({'+' if change >= 0 else ''}{change:.1f}) — {trend}")

            # Only early found
            elif not early_match.empty:
                early_score = early_match.iloc[0][prof_col_early]
                print(f"  {school_name}: {early_score:.1f}% → ??? — No follow-up data available 📭")

            # Only later found
            elif not later_match.empty:
                later_score = later_match.iloc[0][prof_col_late]
                print(f"  {school_name}: ??? → {later_score:.1f}% — No baseline data available ❓")

            # Neither found
            else:
                print(f"  {school_name}: No matching data in either dataset ❌")



def compare_performance_grouped_old(groups, df_early, df_late):
    for group_name, schools in groups.items():
        print(f"\nPerformance Comparison of Top 10 {group_name}s:\n")
        if not schools:
            print("  No schools found in this category.")
            continue

        for school_name in schools:
            early_match = df_early[df_early['School'].str.contains(school_name, case=False, na=False)]
            later_match = df_late[df_late['School'].str.contains(school_name, case=False, na=False)]

            # Both found
            if not early_match.empty and not later_match.empty:
                early_score = early_match.iloc[0]['Percent Proficient (Level 3 or 4)']
                later_score = later_match.iloc[0]['Percent Proficient (Level 3 or 4)']
                change = later_score - early_score
                trend = (
                    "Improved 📈" if change > 1 else
                    "Declined 📉" if change < -1 else
                    "Stable ➖"
                )
                print(f"  {school_name}: {early_score:.1f}% → {later_score:.1f}% ({'+' if change >= 0 else ''}{change:.1f}) — {trend}")

            # Only early found
            elif not early_match.empty:
                early_score = early_match.iloc[0]['Percent Proficient (Level 3 or 4)']
                print(f"  {school_name}: {early_score:.1f}% → ??? — No follow-up data available 📭")

            # Only later found
            elif not later_match.empty:
                later_score = later_match.iloc[0]['Percent Proficient (Level 3 or 4)']
                print(f"  {school_name}: ??? → {later_score:.1f}% — No baseline data available ❓")

            # Neither found
            else:
                print(f"  {school_name}: No matching data in either dataset ❌")

def main():
    if len(sys.argv) != 3:
        print("Usage: ./compare_top_schools.py <earlier_file.xlsx> <later_file.xlsx>")
        sys.exit(1)

    earlier_file, later_file = sys.argv[1], sys.argv[2]

    groups = get_top_schools_grouped(earlier_file)
    if not any(groups.values()):
        print("No top schools identified.")
        sys.exit(1)

    df_early, prof_col_init = load_and_normalize(earlier_file)
    df_late, prof_col_follow = load_and_normalize(later_file)

    compare_performance_grouped(groups, df_early, prof_col_init, df_late, prof_col_follow)

    #compare_performance_grouped(groups, df_early, df_late)

if __name__ == "__main__":
    main()

