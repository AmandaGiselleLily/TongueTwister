# Language_localzier experiment - main script
# created 2023: Bassel Arafat, Jorn Diedrichsen
# Edit Nov 2024: Sivan Jossinger

import constants as const
import my_experiment as exp

def main(subj_id):
    """_summary_
    make sure you to adjust constanst.py file before running the experiment
    (e.g., experiment_name, eye_tracker, screen, etc.)

    Args:
        subj_id (str): id of the subject
    """
    my_Exp = exp.Experiment(const,subj_id)
    
    while True:
        my_Exp.confirm_run_info()
        my_Exp.init_run()
        my_Exp.run()
    return

if __name__ == "__main__":
    main(1)