# Making the run files for each participants.

import pandas as pd
import os
import constants as const

# -------------------------------
# Set params: edit before running
# -------------------------------

# name of the file where the stimuli are stored
stim_file_name = "syllables.csv"
# time from stimulus presentation to GO cue
prep_dur = 1 
# time from the GO cue to the fixation cross
prod_dur = 4
# time between trials (fixation cross is presented)
iti_dur = 1
# time to initiate 1st trial
init_t = 5
# number of subjects
sub_n = 30
# number of runs
run_n = 8
# number of items
sequence_len = 9
# condition
con = "simple"

# ------------
# Define paths 
# ------------
base_dir = const.exp_dir                                       # Project dir
stim_dir = base_dir / "stimuli"                                # Stimuli dir
output_dir = const.run_dir                                     # Run files dir                   
if not os.path.exists(output_dir):
        os.makedirs(output_dir)  

# --------------
# load stimuli
# ---------------
stim_fullfile = stim_dir / stim_file_name
items = pd.read_csv(stim_fullfile,sep=',')


# ---------
# main loop
# ---------
for sub_id in range(1,sub_n+1):   
    for run_id in range(1,run_n+1):
        
        # randomly shuffle the order of the sequences
        items = items.sample(frac=1).reset_index(drop=True)
        
        # Name the run_file
        sub_id_name = f"{sub_id:02}"
        run_id_name = f"{run_id:02}"
        output_file_name = f'sub-{sub_id_name}_run-{run_id_name}.tsv'

        cur_t = init_t      # initiate time     
        trial_num = 0       # initiate trial number  
        output = []         # initiate output_file

        # creat single trials within a run
        for n in range(len(items)):
            trial_num += 1
            item = items["syll_list"][n]
            stim = ' '.join([item]*sequence_len)
            start_t = cur_t

            cur_t += prep_dur + prod_dur + iti_dur

            output.append({
                    'trial_num': trial_num,
                    'condition': con,
                    'stimulus': stim,
                    'start_time': start_t,
                    'go_signal': prep_dur,
                    'resp_time': prod_dur,
                    'record_time': prod_dur+iti_dur,
                    'iti_dur' : iti_dur,
                    })              
        # save run
        output_file= pd.DataFrame(output)
        output_fullfile = os.path.join(output_dir, output_file_name)
        output_file.to_csv(output_fullfile, sep='\t', index=False)
