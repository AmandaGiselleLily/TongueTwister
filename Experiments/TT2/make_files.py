"""Generate run files and task files for SMT.

Mixes built-in MTB tasks with custom speech tasks defined locally
in my_tasks.py.

Class lookups go through ut.get_task_class (runtime) and
ut.get_task_file_class (file generation). Both consult const.task_modules
first, then fall back to the shared MultiTaskBattery package. The
'<class>File' suffix convention for custom TaskFile classes is encapsulated
inside ut.get_task_file_class — make_files.py doesn't need to know about it.

Whether to pass run_number is decided by inspecting each task's
make_task_file signature.
"""

import inspect
import MultiTaskBattery.task_file as tf
import MultiTaskBattery.utils as ut
import constants as const

# Each block is (task_name, kwargs). 

blocks = [

    {
        'task':             'speech_sequence_whole',
        'condition' :       'simple',
        'sequence_len' :    7,
        'task_dur':         230.5,
        'trial_dur':        5,
        'iti_dur':          0.5,
        'stim_file':        'TTsyll.csv'
        
    },

]
num_runs = 8
subj_list = ['train']


def main(blocks, num_runs, subj_id):
    
    # Ensure task and run directories exist
    ut.dircheck(const.run_dir)
    for block in blocks:
        task = block['task']
        ut.dircheck(const.task_dir / task)

    # Generate run files that specify the order and duration of task blocks
    for r in range(1, num_runs + 1):
        tasks = [block['task'] for block in blocks]
        task_dur = [block.get('task_dur',30) for block in blocks]
        tfiles = [
            f"{subj_id}_{block['task']}_{'-'.join(block['condition']) if isinstance(block.get('condition'), list) else block['condition']}_{r:02d}.tsv"
            if block.get('condition') else
            f"{subj_id}_{block['task']}_{r:02d}.tsv"
            for block in blocks
            ]
        T = tf.make_run_file(tasks, tfiles, offset=5, task_dur=task_dur, run_time=240, exp_dir=const.exp_dir)
        T.to_csv(const.run_dir / f'{subj_id}_run_{r:02d}.tsv', sep='\t', index=False)

        # Generate a task_file for each task in each run that specifies the trial information
        for block, tfile in zip(blocks, tfiles):
            task = block['task']
            cond = block.get('condition')
            trial_dur = block.get('trial_dur')
            task_dur = block.get('task_dur')
            stim_file = block.get('stim_file')
            iti_dur = block.get('iti_dur')
            seq_len = block.get('sequence_len')
            row = T.loc[T['task_file']==tfile].iloc[0]
            cl = tf.get_task_class(task, exp_dir=const.exp_dir)
            TaskFileCls = ut.get_task_file_class(const, cl)
            myTask = TaskFileCls(const)

            # Only pass run_number if make_task_file actually accepts it., pass in task duration as a default
            args = {'task_dur': row['task_dur']}
            if cond is not None:
                args['condition'] = cond
            if trial_dur is not None:
                args['trial_dur'] = trial_dur
            if task_dur is not None:
                args['task_dur'] = task_dur
            if stim_file is not None:
                args['stim_file'] = stim_file
            if iti_dur is not None:
                args['iti_dur'] = iti_dur
            if seq_len is not None:
                args['sequence_len'] = seq_len
            if 'run_number' in inspect.signature(myTask.make_task_file).parameters:
                args['run_number'] = r

            myTask.make_task_file(file_name=tfile, **args)

if __name__ == "__main__":
    
    for subj_id in subj_list:
        main(blocks, num_runs, subj_id)