#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 14:28:00 2026

@author: vahid
"""

import os
import re
import pandas as pd


# READ ONE TEXTGRID
def read_textgrid_intervals(
    textgrid_path: str,
    silence_label: str = "silent",):
    """
    Read one Praat TextGrid and return only non-silent intervals.

    Returns
    -------
    intervals : list of dict

        Each item contains:

            syllable
            onset_sec
            offset_sec
    """

    with open(
        textgrid_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    intervals = []

    current_xmin = None
    current_xmax = None
    current_text = None

    # Read TextGrid line by line
    for line in lines:

        stripped = line.strip()

        # Read xmin
        if stripped.startswith("xmin ="):

            value = stripped.split(
                "=", 1)[1].strip()
            try:
                current_xmin = float(value)
            except ValueError:
                current_xmin = None

        # Read xmax
        elif stripped.startswith("xmax ="):

            value = stripped.split("=",1)[1].strip()

            try:
                current_xmax = float(value)
            except ValueError:
                current_xmax = None

        # Read text
        elif stripped.startswith("text ="):

            value = stripped.split(
                "=",
                1
            )[1].strip()

            # Remove surrounding quotes
            if (
                len(value) >= 2
                and value[0] == '"'
                and value[-1] == '"'):
                value = value[1:-1]
            current_text = value

            # We now have one complete interval
            if (
                current_xmin is not None
                and current_xmax is not None):

                label = str(current_text).strip()

               
                # Keep actual syllable intervals
                if (
                    label != ""
                    and label.lower()
                    != silence_label.lower()):

                    intervals.append(
                        {
                            "syllable": label,
                            "onset_sec": current_xmin,
                            "offset_sec": current_xmax,})
            # Reset for next interval
            current_xmin = None
            current_xmax = None
            current_text = None
    return intervals


# EXTRACT INFORMATION FROM TEXTGRID FILENAME
def parse_textgrid_filename(textgrid_filename: str):
    """
    Parse TextGrid filename.

    Expected format:

        behav_sub-02_run-08_trial-25.TextGrid

    Returns:

        subject = sub-02
        run     = 8
        trial   = 25
    """

    basename = os.path.basename(textgrid_filename)
    pattern = re.compile(
        r"^behav_(sub-\d+)_run-(\d+)_trial-(\d+)\.TextGrid$", re.IGNORECASE)

    match = pattern.match(basename)

    if match is None:

        raise ValueError(
            f"Cannot parse TextGrid filename:\n"
            f"{basename}\n"
            f"Expected format:\n"
            f"behav_sub-XX_run-XX_trial-XX.TextGrid")

    subject = match.group(1)

    run = int(match.group(2))

    trial = int(match.group(3))

    return (subject, run, trial)


# =============================================================================
# CREATE WAV FILENAME
def create_wav_filename(
    subject: str,
    run: int,
    trial: int,):
    """
    Create WAV filename corresponding to the TextGrid.

    Example:

        subject = sub-02
        run     = 8
        trial   = 25

    returns:

        behav_sub-02_run-08_trial-25.wav

    The syllable is NOT added to the filename because the current WAV
    naming format is:

        behav_sub-02_run-08_trial-25.wav
    """

    return (
        f"behav_{subject}_"
        f"run-{run:02d}_"
        f"trial-{trial:02d}.wav")


# =============================================================================
# CONVERT MANY TEXTGRIDS -> ONE TSV
def textgrids_to_output_tsv(
    textgrid_folder: str,
    output_tsv_path: str,
    silence_label: str = "silent",):
    """
    Convert all TextGrid files in one folder into one TSV.

    Output columns:

        subject
        run
        trial
        syllable
        wav_file
        syllable_number
        onset_sec
        offset_sec
    """
    # Check input folder
    if not os.path.isdir(
        textgrid_folder):

        raise NotADirectoryError(f"TextGrid folder does not exist:\n"
            f"{textgrid_folder}")

    rows = []

    # Get all TextGrid files
    textgrid_files = sorted(
        [
            filename
            for filename in os.listdir(
                textgrid_folder)
            if filename.lower().endswith(
                ".textgrid")])

    if len(textgrid_files) == 0:
        raise ValueError(
            f"No TextGrid files found in:\n"
            f"{textgrid_folder}")

    print(f"\nFound {len(textgrid_files)} TextGrid files.")
    print("=" * 70)

    # Process each TextGrid
    for file_index, filename in enumerate(
        textgrid_files,
        start=1):

        textgrid_path = os.path.join(
            textgrid_folder,
            filename)

        print(f"[{file_index}/{len(textgrid_files)}] "
            f"Processing: {filename}")

        try:

            # -----------------------------------------------------------------
            # Parse:
            #
            # subject
            # run
            # trial
            subject, run, trial = (
                parse_textgrid_filename(
                    filename))

            # Read syllable intervals
            intervals = (
                read_textgrid_intervals(
                    textgrid_path=textgrid_path,
                    silence_label=silence_label,))

            print(f"    Found {len(intervals)} "
                f"non-silent intervals.")

            # Create corresponding WAV filename
            wav_file = create_wav_filename(
                subject=subject,
                run=run,
                trial=trial,)

            # One row per non-silent interval
            for syllable_number, interval in enumerate(
                intervals,
                start=1):

                syllable = interval["syllable"]

                rows.append(
                    {
                        "subject": subject,
                        "run": run,
                        "trial": trial,
                        "syllable": syllable,
                        "wav_file": wav_file,
                        "syllable_number": syllable_number,
                        "onset_sec": interval[
                            "onset_sec"],
                        "offset_sec": interval[
                            "offset_sec"],})

        except Exception as error:

            print(f"[ERROR] {filename}: {error}")

    # CREATE DATAFRAME
    columns = [
        "subject",
        "run",
        "trial",
        "syllable",
        "wav_file",
        "syllable_number",
        "onset_sec",
        "offset_sec",]

    df = pd.DataFrame(rows, columns=columns)

    # Sort
    if len(df) > 0:

        df = (
            df
            .sort_values(
                by=[
                    "subject",
                    "run",
                    "trial",
                    "syllable_number",]).reset_index(drop=True))

    # Make output directory
    output_directory = os.path.dirname(output_tsv_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True)

    # Save TSV
    df.to_csv(
        output_tsv_path,
        sep="\t",
        index=False,
        float_format="%.4f",)

    # Final information
    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)
    print(f"TextGrid files processed: "
        f"{len(textgrid_files)}")

    print(f"Total syllable intervals: "
        f"{len(df)}")

    print(f"Output TSV saved to:\n"
        f"{output_tsv_path}")

    # Warning if output is empty
    if len(df) == 0:
        print("\nWARNING:")
        print("No syllable intervals were written to the TSV.")
        print("Check the TextGrid labels and make sure the syllable "
            "intervals are not empty or labeled 'silent'.")
    return df


# MAIN
if __name__ == "__main__":
    TEXTGRID_FOLDER = (
        "/home/alily/Documents/GitHub/TongueTwister/Analysis/Text Grid")

    # Output TSV
    OUTPUT_TSV_PATH = ("/home/alily/Documents/GitHub/TongueTwister/Analysis/Model Output/sub_01 (Copy).tsv")

    # Convert
    textgrids_to_output_tsv(
        textgrid_folder=TEXTGRID_FOLDER,
        output_tsv_path=OUTPUT_TSV_PATH,
        silence_label="silent",)