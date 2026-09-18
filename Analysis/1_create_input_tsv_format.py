#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 12:04:01 2026

@author: vahid
"""

import os
import re
import pandas as pd


# READ SUBJECT TSV
def read_subject_tsv(subject_tsv_path):
    """
    Read one subject TSV and prepare the run/trial/stimulus data.
    """

    print(f"Reading TSV: {subject_tsv_path}")

    
    # Read TSV as strings first
    df = pd.read_csv(
        subject_tsv_path,
        sep="\t",
        dtype=str)

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns]

    print("TSV columns:", list(df.columns))

    # Required columns
    required_columns = ["run",
        "trial",
        "stimulus"]

    missing_columns = []
    for column in required_columns:
        if column not in df.columns:
            missing_columns.append(column)

    if missing_columns:

        raise ValueError(
            f"\nMissing columns in {subject_tsv_path}:\n"
            f"{missing_columns}\n\n"
            f"Available columns:\n"
            f"{list(df.columns)}")

    # Convert run/trial to numeric
    df["run"] = pd.to_numeric(
        df["run"],
        errors="coerce")

    df["trial"] = pd.to_numeric(df["trial"], errors="coerce")

    # Remove repeated header rows / invalid rows
    df = df.dropna(
        subset=["run",
            "trial",
            "stimulus"]).copy()

    # Convert numbers to integer
    df["run"] = df["run"].astype(int)
    df["trial"] = df["trial"].astype(int)

    # Clean stimulus
    df["stimulus"] = (
        df["stimulus"]
        .astype(str)
        .str.strip())

    # Remove empty stimulus
    df = df[
        df["stimulus"] != ""].copy()

    # Extract first word as syllable
    df["syllable"] = df["stimulus"].apply(
        lambda stimulus:
        stimulus.split()[0]
        if stimulus.split()
        else "")

    print(f"Valid TSV rows: {len(df)}")
    return df


# CREATE INPUT TSV FOR ONE SUBJECT
def create_input_tsv_for_subject(
    subject_folder,
    tsv_output_folder):

    subject_name = os.path.basename(
        os.path.normpath(subject_folder))

    print()
    print(f"Subject folder: {subject_folder}")
    print(f"Subject name:   {subject_name}")

    subject_tsv_path = os.path.join(
        subject_folder, f"{subject_name}.tsv")

    print(f"Looking for TSV: {subject_tsv_path}")

    
    # Check that TSV exists
    if not os.path.isfile(subject_tsv_path):

        print(f"ERROR: TSV file not found for {subject_name}")

        return None

    # Read subject TSV
    subject_df = read_subject_tsv(subject_tsv_path)

    # ---------------------------------------------------------
    syllable_lookup = {}

    for _, row in subject_df.iterrows():

        run = int(row["run"])
        trial = int(row["trial"])
        syllable = row["syllable"]

        key = (run, trial)
      
        if key in syllable_lookup:

            old_syllable = syllable_lookup[key]

            if old_syllable != syllable:

                print(
                    f"WARNING: conflicting syllable for "
                    f"run={run}, trial={trial}: "
                    f"{old_syllable} vs {syllable}")

        syllable_lookup[key] = syllable

    print(
        f"Created lookup with "
        f"{len(syllable_lookup)} run/trial combinations")

    
    # NEW WAV filename format
    #
    # behav_sub-01_run-03_trial-18.wav
    wav_pattern = re.compile(
        r"^(sub-\d+)_run-(\d+)_trial-(\d+)\.wav$", re.IGNORECASE)

    rows = []

    total_wavs = 0
    matched_wavs = 0
    unmatched_wavs = 0

    # Go through all files in subject folder
    for filename in sorted(os.listdir(subject_folder)):

        # Only WAV
        if not filename.lower().endswith(".wav"):
            continue

        total_wavs += 1

        # -----------------------------------------------------
        # Parse WAV filename
        # -----------------------------------------------------
        match = wav_pattern.match(filename)

        if match is None:

            print(
                f"Could not parse WAV filename: "
                f"{filename}"
            )

            unmatched_wavs += 1
            continue

        # -----------------------------------------------------
        # Extract from filename
        # -----------------------------------------------------
        subject = match.group(1)

        run = int(
            match.group(2)
        )

        trial = int(
            match.group(3)
        )

        # -----------------------------------------------------
        # Check subject
        # -----------------------------------------------------
        if subject.lower() != subject_name.lower():

            print(
                f"WARNING: subject mismatch:\n"
                f"    folder  = {subject_name}\n"
                f"    wav     = {subject}\n"
                f"    file    = {filename}")
            
        # Find corresponding stimulus using:
        #
        # run + trial
        key = (run, trial)

        if key not in syllable_lookup:

            print(
                f"No TSV match:\n"
                f"    file  = {filename}\n"
                f"    run   = {run}\n"
                f"    trial = {trial}")

            unmatched_wavs += 1
            continue

        # Get syllable
        syllable = syllable_lookup[key]

        # Save row
        rows.append({
            "subject": subject_name,
            "run": run,
            "trial": trial,
            "syllable": syllable,
            "wav_file": filename})

        matched_wavs += 1

    # Print debugging information
    print()
    print(f"Total WAV files found: {total_wavs}")
    print(f"Matched WAV files:     {matched_wavs}")
    print(f"Unmatched WAV files:   {unmatched_wavs}")

    # No matching files
    if not rows:

        print(
            f"\nNo matching WAV files were found for "
            f"{subject_name}")

        return None

    # Create output DataFrame
    output_df = pd.DataFrame(rows)

    # Sort:
    output_df = output_df.sort_values(
        by=["run", "trial"]).reset_index(drop=True)

   
    # Create output folder
    os.makedirs(
        tsv_output_folder,
        exist_ok=True)

    # Output filename
    output_path = os.path.join(
        tsv_output_folder,
        f"{subject_name}_input.tsv")

    # Save
    output_df.to_csv(
        output_path,
        sep="\t",
        index=False)

    print()
    print(
        f"Created output TSV:\n"
        f"{output_path}")

    print(
        f"Number of trials written: "
        f"{len(output_df)}")

    # Show first 10 rows
    print()
    print("First 10 output rows:")

    print(
        output_df.head(10).to_string(
            index=False))

    return output_df


# CREATE INPUT TSV FOR ALL SUBJECTS
# ============================================================
def create_input_tsv_for_all_subjects(
    wav_root_folder,
    tsv_output_folder):

    print("=" * 70)
    print("STARTING")
    print("=" * 70)

    print(
        f"\nRoot folder:\n"
        f"{wav_root_folder}")

    # Make sure root exists
    # ---------------------------------------------------------
    if not os.path.isdir(wav_root_folder):

        raise FileNotFoundError(
            f"\nRoot folder does not exist:\n"
            f"{wav_root_folder}")

    # Show what is inside root folder
    root_items = sorted(
        os.listdir(wav_root_folder))

    print()
    print(
        f"Items found in root folder: "
        f"{len(root_items)}")

    subject_count = 0

    # Go through folders
    for item in root_items:

        subject_folder = os.path.join(
            wav_root_folder,
            item)

        # Must be directory
        if not os.path.isdir(subject_folder):
            continue
        
        if re.fullmatch(
            r"sub-\d+",
            item,
            re.IGNORECASE) is None:

            continue

        print()
        print("=" * 70)
        print(f"Processing {item}")
        print("=" * 70)

        result = create_input_tsv_for_subject(
            subject_folder=subject_folder,
            tsv_output_folder=tsv_output_folder)

        if result is not None:

            subject_count += 1

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------
    print()
    print("=" * 70)
    print("FINISHED")
    print("=" * 70)

    print(
        f"Successfully processed subjects: "
        f"{subject_count}")



if __name__ == "__main__":

    # INPUT
    WAV_ROOT_FOLDER = (
        "/home/alily/Documents/GitHub/TongueTwister/Experiments/TT1/data")

    # OUTPUT
    TSV_OUTPUT_FOLDER = (
        "/home/alily/Documents/GitHub/TongueTwister/Experiments/TT1/data")

    # RUN
    create_input_tsv_for_all_subjects(
        wav_root_folder=WAV_ROOT_FOLDER,
        tsv_output_folder=TSV_OUTPUT_FOLDER)
