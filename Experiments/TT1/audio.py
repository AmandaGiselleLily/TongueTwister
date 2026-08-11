import numpy as np
import sounddevice as sd

class Audio:
    """
    Manage continuous audio recording and extraction of individual trials.

    A single audio input stream is kept open while the experiment runs.
    Individual trial recordings are obtained by marking their start and end
    positions within the continuous audio buffer.
    """
    
    def __init__(self,sample_rate=44100):
        self.sample_rate = sample_rate
        self.audio_buffer = []
        self.sample_count = 0
        self.stream = None
        self.recording_start = None
        
    def open_audio(self):
        """
        Open and start a continuous audio input stream.
        Audio is stored continously in memory until the stream is closed.
        """

        self.audio_buffer = []
        self.sample_count = 0
        
        # Creat the stream
        self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                callback=self.audio_callback,
                )
        self.stream.start()
        
    def audio_callback(self, indata, frames, time, status):
        """
        Store each block of audio recorded by the input stream.
            
        Args:
        indata (numpy.ndarray): Audio samples for the current block.
        frames (int): Number of samples in the current block.
        time: Timing information provided by sounddevice.
        status: Stream status information.
        """
        # store a copy of the audio "chunk"
        self.audio_buffer.append(indata.copy())
        # keeps track of number of recorded samples
        self.sample_count += frames
        
    def close_audio(self):
        """ Stop and close the audio stream """
        if hasattr(self, "stream") and self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
    def start_trial_recording(self):
        """ 
        Stors the index of the current sample.
        This sample marks the begining of the recording.
        """
        self.recording_start = self.sample_count
        
    def stop_trial_recording(self):
        """
        Extract the audio recording.
            
        Returns:
            audio (numpy.ndarray) : Audio samples between 'start_trial_recording()' 
            and 'stop_trial_recording()'. 
        """
        # mark the end of trial
        end_sample = self.sample_count
        # concatenate all recorded audio blocks into a single array
        audio = np.concatenate(self.audio_buffer, axis=0)
        # return only the desired samples
        return audio[self.recording_start:end_sample]