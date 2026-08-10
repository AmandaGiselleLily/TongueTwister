"""Custom Task and TaskFile classes for the SpeechMultiTask experiment.

Each task has both a Task class (e.g. VerbalFluency) and a matching
TaskFile generator class with a 'File' suffix (e.g. VerbalFluencyFile).

This module is registered in constants.py via `task_modules = [my_tasks]`,
and make_files.py looks up the TaskFile version by appending 'File' to the
class name from task_table.tsv.
"""

import pandas as pd
import numpy as np
from psychopy import visual, event
from MultiTaskBattery.task_blocks import Task
from MultiTaskBattery.task_file import TaskFile
import MultiTaskBattery.utils as ut
import random
import threading
import sounddevice as sd
from scipy.io.wavfile import write as save_wav
import numpy as np
from ast import literal_eval
from itertools import product

    
class SpeechSequenceWhole(Task):
    """
    Speech sequence task
    """
    def __init__(self, info, screen, ttl_clock, const, subj_id):
        super().__init__(info, screen, ttl_clock, const, subj_id)
        self.feedback_type = 'None'
        self.subj_id = subj_id
        
    def init_task(self):
        """
        Initialize task - default is to read the target information into the trial_info dataframe
        """
        trial_info_file = self.const.task_dir / self.name / self.task_file
        self.trial_info = pd.read_csv(trial_info_file, sep='\t')
        self.sample_rate = 44100
        self.stream = None
        
    def display_instructions(self):
        self.instruction_text = f"{self.descriptive_name} Task \n\n Repeate out loud the syllables in the order shown on the screen"
        instr_visual = visual.TextStim(self.window, text=self.instruction_text, height=self.const.instruction_text_height, color=[-1, -1, -1])
        instr_visual.draw()
        self.flip()
        
    def run(self):
        """
        Run the task with continuous audio recording.

        This method overrides the `run()` method executed by the
        MultiTaskBattery framework. It opens the audio input stream before
        the task begins and closes it when the task finishes, even if an
        error occurs during execution.

        Returns:
            The value returned by the parent class `run()` method.
        """
        self.open_audio()
            
        try:
            return super().run()
        finally:
            self.close_audio()
            
    def run_trial(self, trial):
        """ Run a single trial of the speech sequence task. """
        
        #clear buffer
        event.clearEvents()

        # create stimulus
        sequence = trial['stim']
        stim = visual.TextStim(self.window, text=sequence, pos=(0, 0),  alignHoriz='center',
                                color=(-1, -1, -1), units='deg', wrapWidth=25, height=1.25)

        trial_start = self.ttl_clock.get_time()
        
        # Start recording
        if trial['record_trial'] == 1:
            self.start_trial_recording()
            
        # preperation
        stim.draw()
        self.flip()
        self.ttl_clock.wait_until(trial_start+trial['go_time'])
        
        # execution
        stim.color = 'green'
        stim.draw()
        self.flip()
        self.ttl_clock.wait_until(trial_start+trial['trial_dur'])
        
        # ISI
        self.flip()
        self.ttl_clock.wait_until(trial_start + trial['trial_dur'] +trial['iti_dur'])

        # save audio
        if trial['record_trial'] == 1:
            # end recording
            trial_audio = self.stop_trial_recording()
            # save file
            run = self.task_file.split("_")[-1].replace(".tsv", "")
            file_name =  f"{self.subj_id}_{self.code}-{trial['condition']}_run-{run}_trial-{trial['trial_num']:02d}.wav"
            audio_file = self.const.data_dir / self.subj_id / file_name
            save_wav(audio_file, self.sample_rate, trial_audio)
            
        return trial


class SpeechSequenceWholeFile(TaskFile):
    def __init__(self, const):
        super().__init__(const)
        self.name = 'speech_sequence_whole'

    def generate_sequence(self,condition,sequence_len, items,n):
        """
        Generate a sequence for the speech sequence task.
                
        Args:
            condition (str): sequence complexity
                - 'simple': same letter repeated
                - 'complex': different letters in the sequence.
            sequence_len (int): number of letters in the sequence
            items (list): items to use for the sequence.
            n (str) : trial number
                    
        Returns:
            sequence (str): a space-seperated sequence of letters
        """
        
        if condition == 'simple':
            item = items[n]
            sequence = [item] * sequence_len
            
        elif condition == 'complex':
            sequence = [random.choice(items)]
            while len(sequence) < sequence_len:
                next_item = random.choice([d for d in items if d != sequence[-1]])
                sequence.append(next_item)
        sequence = ' '.join(map(str, sequence))
        return sequence

    def make_task_file(self,
                        condition = "complex",
                        sequence_len = 6,
                        task_dur=30,
                        trial_dur=3.25,
                        go_time = 1,
                        iti_dur=0.5,
                        file_name=None,
                        stim_file = None
                        ):
        """
        Create a speech-sequence task file (say a sequence  of syllables in order).
        Each letter (P, T, K) is a syllable to utter (e.g., /pa/); no feedback.

        Args:
            condition (str): Sequence complexity ('simple' or 'complex').
            sequence_len (int): Number of letters in the sequence
            task_dur (float): Total task duration in seconds.
            trial_dur (float): Duration of each trial in seconds.
            iti_dur (float): Inter-trial interval duration in seconds.
            file_name (str): Name of the file to save the task data.
            stim_file (str): Optional path to a stimulus csv file.

        Returns:
            pd.DataFrame: Task information as a DataFrame.
        """
        # Get items for sequence generation
        if stim_file is not None:
            stim_data = pd.read_csv(ut.find_stim(self.const, self.name, stim_file or f'{self.name}.csv'))
            items = stim_data['item'].dropna().tolist()
        else:
            items = ['P', 'T', 'K']

        # randomly shuffle items for different runs
        random.shuffle(items)
        
        # length of audio recording
        record_duration = trial_dur + iti_dur 
        
        n_trials = int(np.floor(task_dur / (trial_dur + iti_dur)))
        trial_info = []

        t = 0

        for n in range(n_trials):
            trial = {}
            trial['trial_num'] = n
            trial['condition'] = condition
            trial['sequence_len'] = sequence_len
            trial['trial_dur'] = trial_dur
            trial['go_time'] = go_time
            trial['iti_dur'] = iti_dur
            trial['record_dur'] = record_duration
            trial['record_trial'] = True
            trial['display_trial_feedback'] = False
            # choose random sequence
            trial['stim'] = self.generate_sequence(condition,sequence_len,items,n)
            trial['start_time'] = t
            trial['end_time'] = t + trial_dur + iti_dur
            trial_info.append(trial)
            t = trial['end_time']

        trial_info = pd.DataFrame(trial_info)
        if file_name is not None:
            ut.dircheck(self.task_dir / self.name)
            trial_info.to_csv(self.task_dir / self.name / file_name, sep='\t', index=False)

        return trial_info

