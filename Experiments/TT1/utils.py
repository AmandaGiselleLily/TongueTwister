import sounddevice as sd
from scipy.io.wavfile import write as save_wav
import numpy as np
from psychopy import core, event
import os

# -------------
# Record audio
# -------------

def record_audio(duration, save_path):
    """
    Records audio for a specified duration and saves it to the specified file path.

    """

    sample_rate = 44100  # Standard audio sampling rate
    print(f"Recording audio for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait() 
    save_wav(save_path, sample_rate, audio_data) 
    print(f"Recording complete. Saving to {save_path}")

# ----------
# Save data
# ----------

def save_data(output_file, output_data):
              
    """
    Appends trial data to a specified output file in tab-delimited format.

    """
    output_data.to_csv(output_file, mode='a', header=True, index=False, sep='\t')


# -----------
# Termination
# -----------

def check_termination():
    """
    Checks if the 'escape' key has been pressed to terminate the experiment.
    """
    if 'escape' in event.getKeys():  # Check for the escape key
        core.quit()  # Terminates the experiment and closes the window


# ---------------
# Check directory
# ---------------

def dircheck(path2dir):
    """
    Checks if a directory exists! if it does not exist, it creates it
    Args:
        dir_path (str, path)
            path to the directory you want to be created
    """
    if not os.path.exists(path2dir):
        print(f"creating {path2dir}")
        os.makedirs(path2dir)




