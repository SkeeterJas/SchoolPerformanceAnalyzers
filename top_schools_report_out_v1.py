#!/usr/bin/env python3

import sys
import pandas as pd


def load_data(filename):
    """Load data and normalize the proficiency column name."""
    df = pd.read_excel(filename)

    # Use only rows for total population
    df = df[df['Student Group'].str.contains('Total Population', case=False, na=False)]

    # Normalize column name for proficiency
    if 'Percent Proficient (Level 3 or 4)' in df.columns:
        prof_col = 'Percent Proficient (Level 3 or 4)'
    elif 'Percent Proficient' in df.columns:
        prof_col = 'Percent Proficient'
    else:
        raise ValueError("Proficiency column not found in the expected format.")

    df = df[pd.to_numeric(df[prof_col], errors='coerce').notnull()]
    df[prof_col] = df[prof_col].astype(float)

    return df, prof_col

def main(filename):
    try:
        # Load Excel file and get normalized proficiency column name
        df, prof_col = load_data(filename)

        # Clean data
        df = df[df['Student Group'].str.contains('Total Population', case=False, na=False)]
        df = df[pd.to_numeric(df[prof_col], errors='coerce').notnull()]
        df[prof_col] = df[prof_col].astype(float)

        # Define school categories
        school_types = ['High School', 'Middle School', 'Elementary School']

        for s_type in school_types:
            subset = df[df['School'].str.contains(s_type, case=False, na=False)]
            top_schools = subset.sort_values(by=prof_col, ascending=False).head(10)

            print(f"\nTop 10 {s_type}s:")
            if top_schools.empty:
                print("  No matching schools found.")
            else:
                for _, row in top_schools.iterrows():
                    print(f"  {row['School']} ({row['District']}): {row[prof_col]:.1f}% proficient")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./top_schools_report_out_v1.py <input_file.xlsx>")
        sys.exit(1)
    main(sys.argv[1])
