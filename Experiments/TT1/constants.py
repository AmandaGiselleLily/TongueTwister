# constants.py defines parameters and settings for an experiment
# it is passed to the Experiment class on initialization
from pathlib import Path
import os
import MultiTaskBattery as mtb

#Necessary definitions for the experiment:
exp_name = 'TT1'

# These are the response keys (change depending on your keyboard)
response_keys    = ['a', 's', 'd', 'f']

# Directory definitions for experiment
exp_dir = Path(os.path.dirname(os.path.realpath(__file__)))   # where the experiment code is stored
task_dir = exp_dir / "task_files"  # contains target files for the task
run_dir    = exp_dir / "run_files"     # contains run files for each session
data_dir   = exp_dir / "data"          # This is where the result files are being saved

# This is were the stimuli for the different task are stored
package_dir = Path(os.path.dirname(os.path.dirname(os.path.realpath(mtb.__file__))))
stim_dir   = package_dir / "stimuli"

# Optional: list of local Python modules that hold custom Task / TaskFile
# classes. Uncomment and import your module if you want to add custom
# tasks without editing the shared MultiTaskBattery package. See
# the "Implementing new tasks" page for details and
# experiments/example_custom_task for a working example.
# import my_tasks
# task_modules = [my_tasks]

# Use {} so the GUI auto-fills the run number (e.g. run_01.tsv, run_02.tsv, ...)
default_run_filename = 'behav_sub-{}_run-{}.tsv'

# Is the Eye tracker being used?
eye_tracker = False

# Running in debug mode?
debug = False # set to True for debugging

# Screen settings for subject display
screen = {}
screen['size'] = [1440, 900]#[1920, 1080]        # screen resolution
screen['fullscr'] = False           # full screen?
screen['number'] = 1                # 0 = main display, 1 = secondary display
screen['font size ratio'] = 0.0001