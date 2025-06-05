#!/usr/bin/env python3

import sys
import pandas as pd

def load_and_normalize(filename):
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


def compute_deltas(df_early, prof_col_early, df_late, prof_col_late, school_type):
    early = df_early[df_early['School'].str.contains(school_type, case=False, na=False)].copy()
    late = df_late[df_late['School'].str.contains(school_type, case=False, na=False)].copy()

    # Merge and compute actual column names
    merged = pd.merge(
        early,
        late,
        on=['School', 'District'],
        suffixes=('_early', '_late')
    )

    early_col = prof_col_early + '_early'
    late_col = prof_col_late + '_late'

    if early_col not in merged.columns or late_col not in merged.columns:
        raise KeyError(f"Expected columns '{early_col}' and/or '{late_col}' not found after merge.")

    merged['Delta'] = merged[late_col] - merged[early_col]
    merged = merged[['School', 'District', early_col, late_col, 'Delta']]

    return merged

def compute_deltas_old(df_early, prof_col_early, df_late, prof_col_late, school_type):
    early = df_early[df_early['School'].str.contains(school_type, case=False, na=False)].copy()
    late = df_late[df_late['School'].str.contains(school_type, case=False, na=False)].copy()

    # Merge on school name and district to get best match
    merged = pd.merge(
        early,
        late,
        on=['School', 'District'],
        suffixes=('_early', '_late')
    )

    merged['Delta'] = merged[prof_col_late + '_late'] - merged[prof_col_early + '_early']
    merged = merged[['School', 'District', prof_col_early + '_early', prof_col_late + '_late', 'Delta']]

    return merged

def report_extremes(merged_df, category):
    print(f"\n📈 Top 10 Improving {category}s:\n")
    top = merged_df.sort_values(by='Delta', ascending=False).head(10)
    for _, row in top.iterrows():
        print(f"  {row['School']} ({row['District']}): {row[merged_df.columns[2]]:.1f}% → {row[merged_df.columns[3]]:.1f}% (Δ +{row['Delta']:.1f})")

    print(f"\n📉 Bottom 10 Declining {category}s:\n")
    bottom = merged_df.sort_values(by='Delta', ascending=True).head(10)
    for _, row in bottom.iterrows():
        print(f"  {row['School']} ({row['District']}): {row[merged_df.columns[2]]:.1f}% → {row[merged_df.columns[3]]:.1f}% (Δ {row['Delta']:.1f})")

def main():
    if len(sys.argv) != 3:
        print("Usage: ./trend_extremes.py <early_file.xlsx> <late_file.xlsx>")
        sys.exit(1)

    early_file, late_file = sys.argv[1], sys.argv[2]

    try:
        df_early, prof_col_early = load_and_normalize(early_file)
        df_late, prof_col_late = load_and_normalize(late_file)

        for s_type in ['High School', 'Middle School', 'Elementary School']:
            merged = compute_deltas(df_early, prof_col_early, df_late, prof_col_late, s_type)
            if merged.empty:
                print(f"\n⚠️  No matching data found for {s_type}s.\n")
            else:
                report_extremes(merged, s_type)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

