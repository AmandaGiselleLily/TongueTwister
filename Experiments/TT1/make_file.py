# Making the run files for each participants.

import pandas as pd
import random
import os
from psychopy import gui, core
import constants as const
import numpy as np
import itertools

def get_bag_of_words(stim_list, num_words):
    # Randomly select 'num_words' rows from stim_list
    random_rows = random.sample(range(stim_list.shape[0]), num_words)
    random_words = [stim_list[row] for row in random_rows]
    return random_words

def generate_sentence(words,sentence_len,con):
    stim_matrix = []
    if con == 'simple':
        syll_list = np.unique(words)
        for syll in syll_list:
            cur_sentence = [syll]*(sentence_len*3)
            stim_matrix.append(cur_sentence)
    else:
        sentence_list = list(itertools.permutations(words,sentence_len))
        for sentence in sentence_list:
            cur_sentence = [word for row in sentence for word in row]
            if con == 'random':
                random.shuffle(cur_sentence)
            stim_matrix.append(cur_sentence)
    return stim_matrix

# -------------------------
# dialog box for user input
# -------------------------
exp_info = {
        'Enter condition:': ['simple'],
        'Enter the file name where the stimuli are stored:': "sentences.tsv",
        'Enter which type of run files you wish to create (mri / behav):': "behav",
        'Enter preperation duration (sec):': 1,
        'Enter production duration (sec):': 4,
        'Enter rest epoch duration (sec):': 0,
        'Enter iti duration (sec):': 1,
        'Enter time initiate first trial (sec):': 5,
        'Enter the number of subjects:': 30,
        'Enter the number of runs for each subject:': 8,
        'Enter the number of blocks within a run:': 0,
        'Enter the number of words in the bag:': 5,
        'Enter the number of words in the sentence:': 3
        }
    
dlg = gui.DlgFromDict(dictionary=exp_info, title="Set Parameters")
if dlg.OK:  # If the user presses OK, proceed
    try: 
        stim_file_name = exp_info['Enter the file name where the stimuli are stored:'] 
        file_type = exp_info['Enter which type of run files you wish to create (mri / behav):'] 
        prep_dur = float(exp_info['Enter preperation duration (sec):']) 
        prod_dur = float(exp_info['Enter production duration (sec):'])  
        rest_dur = float(exp_info['Enter rest epoch duration (sec):']) 
        iti_dur = float(exp_info['Enter iti duration (sec):']) 
        init_t = float(exp_info['Enter time initiate first trial (sec):']) 
        sub_n = int(exp_info['Enter the number of subjects:']) 
        run_n = int(exp_info['Enter the number of runs for each subject:']) 
        block_n = int(exp_info['Enter the number of blocks within a run:'])
        num_words = int(exp_info['Enter the number of words in the bag:']) 
        sentence_len = int(exp_info['Enter the number of words in the sentence:']) 
        con = exp_info['Enter condition:']
    except ValueError as e:
        print(f"Error: {e}. Please ensure all inputs are valid numbers where required.")
        core.quit()  # Exit if there is an error
else:
    core.quit()  # Exit if the user presses Cancel

# ------------
# Define paths 
# ------------
base_dir = const.exp_dir                                       # Project dir
stim_dir = base_dir / "stimuli"                                # Stimuli dir
output_dir = const.run_dir                                     # Run files dir                   
if not os.path.exists(output_dir):
        os.makedirs(output_dir)  

# ------------
# Load stimuli
# ------------
stim_fullfile = stim_dir / stim_file_name
all_words = pd.read_csv(stim_fullfile, sep='\t')
all_words = np.array(all_words)


# ---------
# main loop
# ---------
for sub_id in range(1,sub_n+1):
    
    # Build stimuli for each subject based on its unique bag of words
    words = get_bag_of_words(all_words, num_words)  # pick a random list of words for each subject
    stimuli = generate_sentence(words,sentence_len,con)
    random.shuffle(stimuli)



    for run_id in range(1,run_n+1):

        # Name the run_file
        sub_id_name = f"{sub_id:02}"
        run_id_name = f"{run_id:02}"
        output_file_name = f'{file_type}_sub-{sub_id_name}_run-{run_id_name}.tsv'

        cur_t = init_t      # initiate time     
        trial_num = 0       # initiate trial number  
        output = []         # initiate output_file


        for trial in range(1,len(stimuli)):
            trial_num += 1
            stim = stimuli[trial]
            start_t = cur_t

            cur_t += prep_dur + prod_dur + iti_dur


            output.append({
                    'trial_num': trial_num,
                    'condition': con,
                    'stimulus': ' '.join(stim),
                    'start_time': start_t,
                    'go_signal': prep_dur,
                    'resp_time': prod_dur,
                    'record_time': prod_dur+iti_dur,
                    'iti_dur' : iti_dur,
                    })              
         
        output_file= pd.DataFrame(output)
        output_fullfile = os.path.join(output_dir, output_file_name)
        output_file.to_csv(output_fullfile, sep='\t', index=False)
