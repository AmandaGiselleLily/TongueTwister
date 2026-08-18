import pandas as pd
import os
import re

def load_runs(wdir, sn_list, bn_list):
    """
    Load all subject/run TSV files into one dataframe.

    Parameters
    ----------
    wdir : str
        Base directory containing subject folders.
    sn_list : list
        List of subject IDs (e.g., ['sub-02','sub-03']).
    bn_list : list
        List of run IDs (e.g., ['run-01','run-03']).

    Returns
    -------
    data_file : pandas.DataFrame
        Concatenated dataframe with all runs.
    """
    
    runs = []

    for sn in sn_list:
        for bn in bn_list:
            file_path = os.path.join(wdir, sn, bn + ".tsv")
            try:
                df = pd.read_csv(file_path, sep="\t")
                runs.append(df)
            except FileNotFoundError:
                print(f"Skipping missing file: {file_path}")
                continue

    data_file = pd.concat(runs, ignore_index=True)
    
    return data_file

def save_data(data,wdir,out_name):
    """
    Save a pandas DataFrame to a TSV file.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataframe to be saved.
    wdir : str
        Path to the directory where the file will be saved.
    out_name : str
        Name of the output file (e.g., 'results.tsv').
    """
    
    data_path = os.path.join(wdir,out_name)
    data.to_csv(data_path, sep="\t", index=False,na_rep="NaN")
    print(f" Data was saved to {data_path}")
    
from pathlib import Path
import pandas as pd

def get_runs_info(info_file):
    """
    Load and clean behavioral TSV for a subject.

    Parameters
    ----------
    info_file : full path to behavioral file metadata

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe with numeric run and trial columns
    """


    # load as string to avoid silent dtype issues
    runs_info = pd.read_csv(info_file, sep="\t", dtype=str)

    # remove accidental repeated header rows
    if "run" in runs_info.columns:
        runs_info = runs_info[runs_info["run"] != "run"]
    elif 'BN' in runs_info.columns:
        runs_info = runs_info[runs_info["BN"] != "BN"]

    # safe numeric conversion
    if "run" in runs_info.columns:
        runs_info["run"] = pd.to_numeric(runs_info["run"], errors="coerce")
    elif 'BN' in runs_info.columns:
        runs_info["BN"] = pd.to_numeric(runs_info["BN"], errors="coerce")

    if "trial" in runs_info.columns:
        runs_info["trial"] = pd.to_numeric(runs_info["trial"], errors="coerce")
    elif 'TN' in runs_info.columns:
        runs_info["TN"] = pd.to_numeric(runs_info["TN"], errors="coerce")


    # drop bad rows
    if "run" in runs_info.columns:
        runs_info = runs_info.dropna(subset=["run", "trial"])
    elif 'BN' in runs_info.columns:
        runs_info = runs_info.dropna(subset=["BN", "TN"])


    # convert to int
    if "run" in runs_info.columns:
        runs_info["run"] = runs_info["run"].astype(int)
    elif "BN" in runs_info.columns:
        runs_info["BN"] = runs_info["BN"].astype(int)
    if "trial" in runs_info.columns:
        runs_info["trial"] = runs_info["trial"].astype(int)
    elif 'TN' in runs_info.columns:
        runs_info["TN"] = runs_info["TN"].astype(int)


    return runs_info



def get_trial_info(file, runs_info):
    """
    Extract run/trial from filename and return matching row from runs_info.

    Parameters
    ----------
    file : Path or os.PathLike
        WAV file
    runs_info : pd.DataFrame
        DataFrame containing columns ['run', 'trial']

    Returns
    -------
    pd.DataFrame
        Filtered row(s) matching run + trial
    """

    filename = file.name

    pattern1 = re.compile(r"sub-(\d+)_run-(\d+).*trial-(\d+)\.wav$")
    pattern2 = re.compile(r"SN\d+_BN(\d+)_TN(\d+)_Eff\d+\.wav$")
    
    # run_match = re.search(r"run-(\d+)", filename)
    # stim_match = re.search(r"stim-(\d+)", filename)
    # syllable_match = re.search(r"stim-\d+_(.+)\.wav$", filename)

    # run = int(run_match.group(1)) if run_match else None
    # trial = int(stim_match.group(1)) if stim_match else None
    # syllables = (syllable_match.group(1).split() if syllable_match else [])
    
    m = pattern1.match(filename)
    if m:
        run, trial= int(m.group(2)), int(m.group(3))
        #syllables = syllables.split()
        syllables=None
    else:
        m = pattern2.match(filename)
        if not m:
            raise ValueError(f"Unknown filename format: {filename}")
        run, trial = int(m.group(1)), int(m.group(2))
        syllables = None

    if "run" in runs_info.columns:
        run_col = "run"
        trial_col = "trial"
    elif "BN" in runs_info.columns:
        run_col = "BN"
        trial_col = "TN"
    else:
        raise KeyError("Could not find run/trial columns.")
    #     if run is None or trial is None:
    #         return None

    # trial_info = runs_info[
    #     (runs_info["run"] == run) &
    #     (runs_info["trial"] == trial)
    # ]
    
    if run is None or trial is None:
        return None

    trial_info = runs_info[
        (runs_info[run_col] == run) &
        (runs_info[trial_col] == trial)
        ]

    return trial_info, syllables



def make_speech_trial_out(sub, trial_info, syllables, onset, offset):
    """
    Create a dataframe with one row per syllable.

    Parameters
    ----------
    sub : str
        Subject ID (e.g. 'sub-02')
    trial_info : pd.DataFrame
        Single-row dataframe returned by get_trial_info_from_file()
    syllables : list[str]
        Syllable labels in order
    onset : array-like
        Onset times
    offset : array-like
        Offset times

    Returns
    -------
    pd.DataFrame
    """

    # Get the single row as a Series
    info = trial_info.iloc[0]
    
    # If the stimulus is a single repeated syllable (e.g., "pre"),
    # repeat the label to match the number of detected syllables.
    # if len(syllables) == 1:
    #     syllables = syllables * len(onset)
        
    # if not (len(syllables) == len(onset) == len(offset)):
    #     if "run" in info:
    #         print(
    #             f"Skipping {sub}, run {info['run']}, trial {info['trial']}: "
    #             f"length mismatch "
    #             f"({len(syllables)} syllables, "
    #             f"{len(onset)} onsets, "
    #             f"{len(offset)} offsets)."
    #         )
    #     elif "BN" in info:
    #         print(
    #             f"Skipping {sub}, run {info['BN']}, trial {info['TN']}: "
    #             f"length mismatch "
    #             f"({len(syllables)} syllables, "
    #             f"{len(onset)} onsets, "
    #             f"{len(offset)} offsets)."
    #         )
    #     return None
    
    return pd.DataFrame({
        "SubNum": sub,
        "BN": info["run"],
        "TN": info["trial"],
        "condition": info["condition"],
        "SyllNum": range(1, len(onset) + 1),
        "syllable": syllables,
        "onset": onset,
        "offset": offset,
    })