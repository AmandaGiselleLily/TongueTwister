import sys

# sys.path.insert(0, "/home/alily/Documents/GitHub")

import experiment as exp

from psychopy import gui
import sys
import pandas as pd
from MultiTaskBattery.ttl_clock import TTLClock
from screen import Screen
import utils as ut
import threading

class Experiment:
    def __init__(self, const, subj_id):

        """    A general class with attributes common to experiments

               Args: 
                    const (module):
                        local constants.py module (see pontine_7T/constants.py) as example

                Returns:
                    self (object):
                        an instance of the Experiment class
        """
        self.exp_name    = const.exp_name
        self.subj_id     = subj_id
        self.run_number  = 0
        self.const       = const
        self.ttl_clock = TTLClock()
        # open screen and display fixation cross
        ### set the resolution of the subject screen here:
        self.screen = Screen(const.screen)

    def confirm_run_info(self):
        """
        Presents a GUI to confirm the settings for the run:

        The following parameters will be set:
        run_number      - run number
        subj_id         - id assigned to the subject
        ttl_flag        - should the program wait for the ttl pulse or not? For scanning THIS FLAG HAS TO BE SET TO TRUE

        Args:
        """
        # a dialog box pops up so you can enter info
        #Set up input box
        inputDlg = gui.Dlg(title = f"{self.exp_name}")
        inputDlg.addField('Enter Subject id (str):',initial = self.subj_id)      
        inputDlg.addField('Enter Run Number (int):',initial = self.run_number+1)      
        inputDlg.addField('Run File name (str):',initial = self.const.default_run_filename.format(f'{int(self.subj_id):02d}', f'{int(self.run_number) + 1:02d}'))      
        #inputDlg.addField('Run in MRI?', initial = True) 
        inputDlg.addField('Record data?', initial = True)

        inputDlg.show()

        if inputDlg.OK:
            self.subj_id        = str(inputDlg.data[0])
            self.run_number     = int(inputDlg.data[1])
            self.run_filename   = str(inputDlg.data[2])
            #self.wait_ttl       = bool(inputDlg.data[3])
            self.record_data    = bool(inputDlg.data[3])
        else:
            sys.exit()
        
        # set exp_type based on user input
        if "training" in self.run_filename:
            self.exp_type = 'training'
        elif "mri" in self.run_filename:
            self.exp_type = 'mri'
        elif "behav" in self.run_filename:
            self.exp_type = 'behav'

    def init_run(self):
        """
        initializing the run:
            making sure a directory is created for the behavioral results
            getting run file
        """

        # 1. get the run file info: creates self.run_info
        self.run_info = pd.read_csv(self.const.run_dir / self.run_filename, sep='\t')
     
        # 2. make subject folder in data/<subj_id>
        self.subj_dir = self.const.data_dir / f"{int(self.subj_id):02d}"
        ut.dircheck(self.subj_dir) # making sure the directory is created!

        # 3. make subject data file with the name <data_type>_sub<subj_id>
        self.run_data_file = self.subj_dir / (f"{self.exp_type}_sub-{int(self.subj_id):02d}.tsv")  

    def run(self):
        """
        run a run of the experiment
        """
        print(f"running the experiment for subject {int(self.subj_id):02d}")
        self.screen.fixation_cross()
        self.ttl_clock.reset()
        self.ttl_clock.wait_for_first_ttl(wait = self.wait_ttl)

        data = pd.DataFrame()
        # Loop over each trial
        for ind, row in self.run_info.iterrows():
            self.trial_num = ind+1
            trial_info = self.run_trial(row)
            trial_info = trial_info.to_frame().T
            data = pd.concat([data, trial_info],ignore_index=True)
        print(f"******Run {int(self.run_number):02d} completed for subject {int(self.subj_id):02d}******")
        
        # Save the data here 
        ut.save_data(self.run_data_file, data)

        # Wait until last ttl finish
        self.ttl_clock.wait_until(row['end_time_real'] + 10)


    def run_trial(self,row):
        """
        run a trial of the experiment
        """
        # get trial information 
        trial_num   = row['trial_num']
        stimulus    = row['stimulus']
        start_time  = row['start_time'] 
        resp_time   = row['resp_time'] 
        record_time = row['record_time']

        # Wait until start time
        self.ttl_clock.wait_until(start_time)
        start_time_real = self.ttl_clock.get_time() # real time of stim onset

        # Show stimulus on screen
        self.screen.stimulus_screen(stimulus)

        # Initiate GO signal
        if 'go_signal' in row.index:
            go_time = row['go_signal']
            # change stim color
            self.ttl_clock.wait_until(start_time + go_time)
            self.screen.stimulus_screen(stimulus, color='green') 
        else: 
            go_time = 0

        # Start recording
        if self.record_data:
            audio_file = self.subj_dir / f"{self.exp_type}_sub-{int(self.subj_id):02d}_run-{int(self.run_number):02d}_stim-{trial_num:02d}_{stimulus}.wav"
            record_thread = threading.Thread(target=ut.record_audio, args=(record_time, audio_file))
            record_thread.start()

        # Show fixation cross
        self.ttl_clock.wait_until(start_time + go_time + resp_time)
        self.screen.fixation_cross()

        end_time_real = self.ttl_clock.get_time()

        # End recording
        if self.record_data:
           record_thread.join()

        # Append trial data to the current trial row
        row['run']                       = self.run_number
        row['trial']                     = self.trial_num
        row['start_time_real']           = start_time_real
        row['end_time_real']             = end_time_real

        return row
