#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 11:30:00 2026

@author: vahid
"""

import os
import re
import numpy as np
import pandas as pd
import soundfile as sf


# CREATE ONE TEXTGRID
def save_onset_offset_textgrid(
    wav_path: str,
    onset_times,
    offset_times,
    output_path: str,
    labels=None,
    tier_name: str = "syll",
    silence_label: str = "silent",):
    """
    Save detected syllable intervals as a Praat TextGrid.

    The first interval starts at 0.
    The final interval ends at the exact WAV duration.
    Gaps between syllables are stored as silence intervals.

    Silence intervals are labeled:
        "silent"
    """

    if output_path is None or str(output_path).strip() == "":
        raise ValueError("A valid output_path is required.")

    onset_times = np.asarray(
        onset_times,
        dtype=float).reshape(-1)

    offset_times = np.asarray(
        offset_times,
        dtype=float).reshape(-1)

    # -------------------------------------------------------------------------
    # Make sure onset and offset counts match
    # -------------------------------------------------------------------------
    if len(onset_times) != len(offset_times):
        raise ValueError(
            f"Number of onsets and offsets must be equal. "
            f"Got {len(onset_times)} onsets and "
            f"{len(offset_times)} offsets.")

    number_of_syllables = len(onset_times)

    # Labels
    # -------------------------------------------------------------------------
    if labels is None:
        labels = [""] * number_of_syllables

    else:
        labels = list(labels)

        if len(labels) != number_of_syllables:
            raise ValueError(
                f"Number of labels must match number of syllables. "
                f"Got {len(labels)} labels and "
                f"{number_of_syllables} syllables.")

    # Get exact WAV duration
    info = sf.info(wav_path)

    wav_duration = (
        float(info.frames)
        / float(info.samplerate))

    # Handle tiny floating-point differences
    TIME_TOLERANCE_SEC = 0.001
    for i in range(len(onset_times)):
        # Slightly negative onset -> 0
        if (
            onset_times[i] < 0
            and abs(onset_times[i]) <= TIME_TOLERANCE_SEC):
            onset_times[i] = 0.0

        # Slightly beyond WAV duration -> exact duration
        if (
            onset_times[i] > wav_duration
            and onset_times[i] - wav_duration <= TIME_TOLERANCE_SEC):
            onset_times[i] = wav_duration

        if (
            offset_times[i] > wav_duration
            and offset_times[i] - wav_duration <= TIME_TOLERANCE_SEC):
            offset_times[i] = wav_duration

    # Sort intervals based on onset time
    if number_of_syllables > 0:

        sort_indices = np.argsort(
            onset_times)

        onset_times = onset_times[sort_indices]

        offset_times = offset_times[sort_indices]

        labels = [
            labels[i]
            for i in sort_indices]

    # -------------------------------------------------------------------------
    # Validate intervals
    for i, (onset, offset) in enumerate(
        zip(
            onset_times,
            offset_times),start=1):

        if onset < 0:
            raise ValueError(
                f"Syllable {i}: onset cannot be negative. "
                f"Got onset={onset}")

        if offset < onset:
            raise ValueError(
                f"Syllable {i}: offset must be >= onset. "
                f"Got onset={onset}, offset={offset}")

        if onset > wav_duration:
            raise ValueError(
                f"Syllable {i}: onset exceeds WAV duration. "
                f"Got onset={onset}, "
                f"duration={wav_duration}")

        if offset > wav_duration:
            raise ValueError(
                f"Syllable {i}: offset exceeds WAV duration. "
                f"Got offset={offset}, "
                f"duration={wav_duration}")

        if (i > 1
            and onset < offset_times[i - 2]):
            raise ValueError(
                f"Syllable {i} overlaps previous syllable. "
                f"Current onset={onset}, "
                f"previous offset={offset_times[i - 2]}")

    # CREATE CONTINUOUS INTERVALS
    continuous_intervals = []

    current_time = 0.0

    for onset, offset, label in zip(
        onset_times,
        offset_times,
        labels):

        onset = float(onset)
        offset = float(offset)

        # Silence before syllable
        if onset > current_time:

            continuous_intervals.append(
                (
                    current_time,
                    onset,
                    silence_label))

        # Syllable interval
        continuous_intervals.append(
            (
                onset,
                offset,
                str(label)))

        current_time = offset

    # Final silence
    if current_time < wav_duration:

        continuous_intervals.append(
            (
                current_time,
                wav_duration,
                silence_label))

    # No detected syllables
    if not continuous_intervals:

        continuous_intervals.append(
            (
                0.0,
                wav_duration,
                silence_label))

    # SAVE TEXTGRID
    output_directory = os.path.dirname(
        output_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True)

    from pathlib import Path

    output_path = Path(output_path)

    output_path.parent.mkdir(
    parents=True,
    exist_ok=True)

    with output_path.open(
        
        "w",
        encoding="utf-8") as file:

        file.write('File type = "ooTextFile"\n')

        file.write('Object class = "TextGrid"\n\n')

        file.write("xmin = 0\n")

        file.write(f"xmax = {wav_duration:.10f}\n")

        file.write("tiers? <exists>\n")

        file.write("size = 1\n")

        file.write("item []:\n")

        file.write("    item [1]:\n")

        file.write('        class = "IntervalTier"\n')

        file.write(f'        name = "{tier_name}"\n')

        file.write("        xmin = 0\n")

        file.write(f"        xmax = {wav_duration:.10f}\n")

        file.write(f"        intervals: size = "
            f"{len(continuous_intervals)}\n")

        for index, (xmin, xmax, label) in enumerate(
            continuous_intervals, start=1):

            label = str(label).replace('"', '\\"')

            file.write(f"        intervals [{index}]:\n")

            file.write(f"            xmin = "
                f"{xmin:.10f}\n")

            file.write(f"            xmax = "
                f"{xmax:.10f}\n")

            file.write(f'            text = "{label}"\n')

    print(f"TextGrid saved: {output_path}")


# =============================================================================
# CREATE TEXTGRID NAME FROM WAV NAME
def create_textgrid_filename(wav_filename: str) -> str:
    """
    Convert:

        behav_sub-01_run-01_stim-01_day day day day.wav

    into:

        behav_sub-01_run-01_stim-01.TextGrid
    """

    basename = os.path.basename(wav_filename)

    pattern = re.compile(
        r"^(behav_sub-\d+_run-\d+_stim-\d+)_.*\.wav$",
        re.IGNORECASE)

    match = pattern.match(
        basename)

    if match is not None:

        base_name = match.group(1)

        return (base_name + ".TextGrid")

    # -------------------------------------------------------------------------
    # Fallback if filename has a slightly different format
    base_name = os.path.splitext(basename)[0]

    return (
        base_name
        + ".TextGrid")


# CONVERT OUTPUT TSV -> MANY TEXTGRIDS
def output_tsv_to_textgrids(
    input_tsv_path: str,
    wav_folder: str,
    output_folder: str,
    use_syllable_label: bool = True,):
    """
    Convert one subject's output TSV into separate TextGrid files.

    Each WAV/trial gets one TextGrid.

    Expected TSV columns:

        subject
        run
        trial
        syllable
        wav_file
        syllable_number
        onset_sec
        offset_sec

    Example outputs:

        behav_sub-01_run-01_stim-01.TextGrid
        behav_sub-01_run-01_stim-02.TextGrid
        behav_sub-01_run-01_stim-03.TextGrid

    All empty/gap intervals are labeled:
        silent
    """

    # =========================================================================
    # CHECK INPUTS
    # =========================================================================
    if not os.path.isfile(
        input_tsv_path):

        raise FileNotFoundError(
            f"TSV file does not exist:\n"
            f"{input_tsv_path}")

    if not os.path.isdir(wav_folder):

        raise NotADirectoryError(
            f"WAV folder does not exist:\n"
            f"{wav_folder}")

    os.makedirs(
        output_folder,
        exist_ok=True)

    # =========================================================================
    # LOAD TSV
    # =========================================================================

    df = pd.read_csv(
        input_tsv_path,
        sep="\t")

    required_columns = [
        "subject",
        "run",
        "trial",
        "syllable",
        "wav_file",
        "syllable_number",
        "onset_sec",
        "offset_sec",]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns]

    if missing_columns:

        raise ValueError(
            "TSV is missing required columns: "
            + ", ".join(
                missing_columns))

    print("\n" + "=" * 70)
    print("TSV -> TEXTGRID CONVERSION")
    print("=" * 70)

    print(f"TSV: {input_tsv_path}")

    print(f"Rows: {len(df)}")

    print(f"Trials/WAV files: "
        f"{df['wav_file'].nunique()}")

    # =========================================================================
    # GROUP BY WAV / TRIAL
    # =========================================================================

    grouped = df.groupby(
        "wav_file", sort=False)

    successful = 0
    failed = 0

    failed_files = []

    for wav_filename, trial_df in grouped:

        wav_filename = str( wav_filename)

        # ---------------------------------------------------------------------
        # Sort segments in correct order
        # ---------------------------------------------------------------------
        trial_df = (
            trial_df.sort_values(
                by="syllable_number")
            .reset_index(
                drop=True))

        wav_path = os.path.join(
            wav_folder,
            wav_filename)

        print("\n" + "-" * 70)

        print(f"WAV: {wav_filename}")

        # ---------------------------------------------------------------------
        # Make sure WAV exists
        # ---------------------------------------------------------------------
        if not os.path.isfile(wav_path):

            print("[ERROR] WAV file not found:")

            print(wav_path)

            failed += 1

            failed_files.append(
                {
                    "wav_file": wav_filename,
                    "error": "WAV file not found"})
            continue

        # ---------------------------------------------------------------------
        # Read onset/offset columns
        onset_times = (
            trial_df["onset_sec"]
            .astype(float)
            .to_numpy())

        offset_times = (
            trial_df["offset_sec"]
            .astype(float)
            .to_numpy())

        # ---------------------------------------------------------------------
        # Labels
        if use_syllable_label:

            labels = (
                trial_df["syllable"]
                .astype(str)
                .tolist())

        else:
            labels = None

        # Create output TextGrid filename
        textgrid_filename = (
            create_textgrid_filename(
                wav_filename))

        output_path = os.path.join(
            output_folder,
            textgrid_filename)

        # ---------------------------------------------------------------------
        # Save TextGrid
        # ---------------------------------------------------------------------
        try:

            save_onset_offset_textgrid(
                wav_path=wav_path,
                onset_times=onset_times,
                offset_times=offset_times,
                output_path=output_path,
                labels=labels,
                tier_name="syll",

                # IMPORTANT:
                # Every gap/empty interval will be "silent"
                silence_label="silent",)

            successful += 1

        except Exception as error:

            failed += 1

            print(f"[ERROR] {error}")

            failed_files.append(
                {
                    "wav_file": wav_filename,
                    "error": str(error)})

    # =========================================================================
    # FINAL REPORT
    print("\n" + "=" * 70)
    print("CONVERSION COMPLETE")

    print("=" * 70)
    print(
        f"Successfully created: "
        f"{successful} TextGrid files")

    print(f"Failed: {failed}")
    print(
        f"Output folder:\n"
        f"{output_folder}")

    # Optional failure report
    if failed_files:

        failed_df = pd.DataFrame(
            failed_files)

        failed_tsv_path = os.path.join(
            output_folder,
            "failed_textgrid_conversion.tsv")

        failed_df.to_csv(
            failed_tsv_path,
            sep="\t",
            index=False)

        print("\nFailure report saved to:")

        print(failed_tsv_path)


# =============================================================================
# MAIN
if __name__ == "__main__":

    # Subject output TSV
    INPUT_TSV_PATH = ("/home/alily/Documents/GitHub/TongueTwister/Analysis/sub_01.tsv")

    # Folder containing original WAV files. We need wave file to get the wave file duration in s.
    WAV_FOLDER = (
        "/home/alily/Documents/GitHub/TongueTwister/Experiments/TT1/data/sub-01")

    # Folder to save all generated TextGrid files
    OUTPUT_TEXTGRID_FOLDER = (
        "/home/alily/Documents/Projects/TongueTwister/Data/sub-01/TextGrids")

    # Run
    output_tsv_to_textgrids(
        input_tsv_path=INPUT_TSV_PATH,
        wav_folder=WAV_FOLDER,
        output_folder=OUTPUT_TEXTGRID_FOLDER,
        use_syllable_label=True,)