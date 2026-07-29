
from psychopy import visual, event, monitors
import utils as ut


class Screen:

    def __init__(self, const):
        self.fullscr  = const['fullscr']
        self.units    = 'deg'
        self.color    = '#808080'
        self.size     = const['size'] #[800, 800] #[1440, 900]
        self.distance = 57.0
        self.width    = 30.0
        self.allowGUI = True
        self.screen_number = const['number']
        self.font_size = const['font size ratio']
        self.monitor  = monitors.Monitor(
                "stimulus",
                distance = self.distance,
                width = self.width,
        )
        self.monitor.setSizePix(self.size) # screen size (not window!) look in display prefs
        self.monitor.saveMon()

        self.win   = visual.Window(size = self.size,
                             screen = self.screen_number,
                             monitor = self.monitor,
                             fullscr = self.fullscr,
                             units = self.units,
                             color = self.color,
                             allowGUI = self.allowGUI, allowStencil=True)

        
    def fixation_cross(self, color='white'):
        """
        Show fixation cross
        """
        fixation = visual.ShapeStim(self.win,
            vertices=((0, -0.06), (0, 0.06), (0,0), (-0.04,0), (0.04, 0)),
            lineWidth=10,
            closeShape=False,
            lineColor=color,
            units='norm'
        )
        fixation.draw()
        self.win.flip()
        ut.check_termination()

    def stimulus_screen(self, stim, color='black'):
        """
        Show a stimulus on the screen
        """
        event.clearEvents()

        # Calculate font size relative to screen size
        screen_height = self.size[1]  # assuming size is [width, height]
        font_size = self.font_size * screen_height  # scaling font size relative to the screen height

        stimulus = visual.TextStim(self.win,
            text = stim,
            height=font_size,
            color=color,
            units='norm',
            wrapWidth=500

        )

        stimulus.draw()
        self.win.flip()
        ut.check_termination()
