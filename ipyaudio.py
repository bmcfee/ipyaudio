#!/usr/bin/env python
# CREATED:2014-10-18 10:24:43 by Brian McFee <brian.mcfee@nyu.edu>
# Bridge IPython widgets with PortAudio controls and DSP callbacks

import pyaudio
import numpy as np

import IPython.html.widgets

class AudioConnector(object):

    def __init__(self, handler, sr=22050, window=2048, dtype=np.float32, channels=1, width=2, output=False, **kwargs):

        self.channels = channels
        self.width = width

        self.handler = handler

        self.sr = sr
        self.window = window
        self.dtype = dtype

        self.output = output

        self.kwargs = kwargs

        # Helpers for interpreting the byte array as floats
        self.fmt = '<i{:d}'.format(self.width)
        self.scale = 1./float(1 << ((8 * self.width) - 1))

        # Build the portaudio interface
        self.port_ = pyaudio.PyAudio()

        # Instantiate the stream
        self.stream_ = self.port_.open(start=False,
                                       format=self.port_.get_format_from_width(self.width),
                                       frames_per_buffer=self.window,
                                       channels=self.channels,
                                       rate=self.sr,
                                       input=True,
                                       output=self.output,
                                       stream_callback=self.__audio_callback)

    def start(self):

        self.stream_.start_stream()

    def stop(self):
        
        self.stream_.stop_stream()

    def __audio_callback(self, in_data, frame_count, time_info, status):

        # TODO:   2014-10-18 10:33:11 by Brian McFee <brian.mcfee@nyu.edu>
        #  frame-drop here

        # Interpret the buffer as a numpy array of floats
        y = self.scale * np.frombuffer(in_data, self.fmt).astype(self.dtype)

        # Pass data to the callback
        self.handler(y, self.sr, **self.kwargs)

        # Let pyaudio continue
        return (in_data, pyaudio.paContinue)


    def __del__(self):

        # Close the stream
        self.stop()

        # Close the portaudio connector
        self.port_.terminate()


def playback_widget(audio_connector, play=u"\u25B6", pause=u"\u2161"):

    def __widget_callback(name, old, new):

        key, active = new
        if key != 'value':
            return

        if active:
            widget.description = pause
            audio_connector.start()
        else:
            widget.description = play
            audio_connector.stop()


    # Build a widget, off by default
    widget = IPython.html.widgets.ToggleButtonWidget(description=play,
                                                     value=False)

    # connect to the callback
    widget.on_trait_change(__widget_callback,
                           name=['_property_lock'])

    return widget
