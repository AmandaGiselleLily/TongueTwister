# Making the run files for each participants.

import pandas as pd
import numpy as np
import random
import os
from psychopy import gui, core
import constants as const
import sys

# -------------------------
# dialog box for user input
# -------------------------
exp_info = {
        'Enter the file name where the stimuli are stored:': "TongueTwisterOrthopraphicStimuli.csv",
        'Enter which type of run files you wish to create (mri / behav):': "behav",
        'Enter stimulus duration (sec):': 4,
        'Enter record duration (sec):': 4.5,
        'Enter rest epoch duration (sec):': 2,
        'Enter iti duration (sec):': 4,
        'Enter time initiate first trial (sec):': 4,
        'Enter the number of subjects:': 10,
        'Enter the number of runs for each subject:': 8,
        'Enter the number of blocks within a run:': 3
    }
    
dlg = gui.DlgFromDict(dictionary=exp_info, title="Set Parameters")
if dlg.OK:  # If the user presses OK, proceed
    try: 
        stim_file_name = exp_info['Enter the file name where the stimuli are stored:'] 
        file_type = exp_info['Enter which type of run files you wish to create (mri / behav):'] 
        stim_dur = float(exp_info['Enter stimulus duration (sec):']) 
        record_dur = float(exp_info['Enter record duration (sec):'])  
        rest_dur = float(exp_info['Enter rest epoch duration (sec):']) 
        iti_dur = float(exp_info['Enter iti duration (sec):']) 
        init_t = float(exp_info['Enter time initiate first trial (sec):']) 
        sub_n = int(exp_info['Enter the number of subjects:']) 
        run_n = int(exp_info['Enter the number of runs for each subject:']) 
        block_n = int(exp_info['Enter the number of blocks within a run:']) 
    except ValueError as e:
        print(f"Error: {e}. Please ensure all inputs are valid numbers where required.")
        core.quit()  # Exit if there is an error
else:
    core.quit()  # Exit if the user presses Cancel

# ------------
# Define paths 
# ------------
#base_dir = const.exp_dir                                       # Project dir
stim_dir = "/home/alily/Downloads/"                               # Stimuli dir
output_dir = "/home/alily/Downloads/"                                     # Run files dir                   
#if not os.path.exists(output_dir):
#        os.makedirs(output_dir)  

# ------------
# Load stimuli
# ------------
stim_fullfile = stim_dir + stim_file_name
stim_file = pd.read_csv(stim_fullfile, sep=",", encoding="utf-8",encoding_errors="ignore")

# ---------
# main loop
# ---------
for sub_id in range(1,sub_n+1):

    
    rows = np.random.randint(low=1, high=stim_file.shape[0], size=run_n+1)
    cols = np.random.randint(low=1, high=stim_file.shape[1], size=run_n+1)
    coords = list(set(zip(rows, cols)))
    coords = pd.Series(coords)

    if len(coords) < run_n:
       rows1 = np.random.randint(low=1, high=stim_file.shape[0], size=run_n+1)
       cols1 = np.random.randint(low=1, high=stim_file.shape[1], size=run_n+1)
       coords1 = list(set(zip(rows, cols)))
       coords1 = pd.Series(coords1)

       coords = coords1

# 4. Extract values as a Series or list
    stim_list = [stim_file.iloc[r, c] for r, c in coords]
    
    
    for run_id in range(1,run_n+1):

        cur_t = init_t      # initiate time     
        trial_num = 0       # initiate trial number  
        output = []         # initiate output_file

        # Name the run_file
        sub_id_name = f"{sub_id:02}"
        run_id_name = f"{run_id:02}"
        output_file_name = f'sub-{sub_id_name}_run-{run_id_name}.tsv'
 
        
        for block_id in range(1, block_n + 1):
            

            # Randomize and duplicate stimuli for the block
            random_stim_list = random.sample(stim_list, block_n)
            cur_stim_list = [item for item in random_stim_list for _ in range(2)]

            print(random_stim_list)
            
            #if file_type == 'mri': 
            #    cur_stim_list = [item for item in random_stim_list for _ in range(2)]
            #elif file_type == 'behav':
                #cur_stim_list = random_stim_list
            block_length = len(random_stim_list)

            # Generate start_time and record time for each stimulus
            for trial in range(0, block_length): 
                trial_num += 1
                stim = random_stim_list[trial-1] + " "
                start_t = cur_t
                # For last stim in a block, iti = rest
                if trial == block_length:
                    cur_t +=  iti_dur + rest_dur
                else:
                    cur_t += iti_dur + rest_dur

                print(output)
                output.append({
                    'trial_num': trial_num,
                    'condition': 0, 
                    'stimulus': stim*9,
                    'start_time': start_t,
                    'go_signal':1,
                    'resp_time': stim_dur,
                    'record_time': record_dur,
                    'rest_dur':rest_dur
                    })              
         
        output_file= pd.DataFrame(output)
        output_fullfile = os.path.join(output_dir, output_file_name)
        output_file.to_csv(output_fullfile, sep='\t', index=False)