#!/usr/bin/env python
'''Bridge IPython widgets with PortAudio controls and DSP callbacks'''

import logging
import numpy as np
import pyaudio
import IPython.html.widgets


LOG = logging.getLogger(__name__)


class AudioConnector(object):
    '''A class to connect a PyAudio stream to a callback function.'''

    def __init__(self, callback, sr=22050, window=1024, dtype=np.float32,
                 channels=1, width=2, output=False, **kwargs):
        '''
        :parameters:
            - callback : function
              Must support the positional arguments:
                - y : np.ndarray
                - sr : int

              If it returns a value, it must be a buffer of the
              same shape as y.

            - sr : int > 0
              The sampling rate from PyAudio

            - window : int > 0
              The number of samples to buffer

            - dtype : type
              The data type for the np.ndarray buffer

            - channels : int
              The number of channels to read

            - width : int
              The number of bytes per sample

            - output : bool
              Enable audio pass-through

            - **kwargs :
              Additional keyword arguments to pass through to `callback`
        '''
        self.channels = channels
        self.width = width

        self.callback = callback

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

        my_fmt = self.port_.get_format_from_width(self.width)
        # Instantiate the stream
        self.stream_ = self.port_.open(start=False,
                                       format=my_fmt,
                                       frames_per_buffer=self.window,
                                       channels=self.channels,
                                       rate=self.sr,
                                       input=True,
                                       output=self.output,
                                       stream_callback=self.__audio_callback)

    def start(self):
        '''Start the audio stream.'''

        LOG.info('Stream started')
        self.stream_.start_stream()

    def stop(self):
        '''Stop (pause) the audio stream.'''

        LOG.info('Stream stopped')
        self.stream_.stop_stream()

    def set_state(self, active):
        '''Set the state:

        :parameters:
          - active : bool
            If true, start streaming
            If false, stop streaming
        '''
        if active:
            self.start()
        else:
            self.stop()

    def __audio_callback(self, in_data, frame_count, t_info, status):
        '''Callback function for PyAudio.

        See PyAudio.Stream documentation for details.
        '''

        # Interpret the buffer as a numpy array of floats
        y = self.scale * np.frombuffer(in_data, self.fmt).astype(self.dtype)

        # Pass data to the callback
        try:
            y_out = self.callback(y, self.sr, **self.kwargs)
        except Exception as e_callback:
            LOG.error('Exception in callback: {0}'.format(e_callback))

        if y_out is None:
            # callback was silent, passthru
            out_data = in_data
        else:
            # reinterpret the result
            out_data = (y_out / self.scale).astype(self.fmt)

        # Let pyaudio continue
        if self.output:
            return (out_data, pyaudio.paContinue)
        else:
            return (None, pyaudio.paContinue)

    def test_callback(self, y=None):
        '''Test the stream callback.
        This can be useful for debugging your callback function without
        depending on PortAudio.

        :parameters:
          - y : ndarray or None
            Buffer to pass back as data to the callback.
            If none, white noise is used.
        '''

        if y is None:
            y = np.random.randn(self.window)

        self.callback(y, self.sr, **self.kwargs)

    def __del__(self):
        '''Class destructor.

        This stops the stream and terminates the PortAudio connection.
        '''

        # Close the stream
        self.stop()

        # Close the portaudio connector
        self.port_.terminate()


def playback_widget(audio_connector):
    '''Construct a toggle widget to control an AudioConnector object.

    :usage:
        >>> audio_connector = ipyaudio.AudioConnector(my_callback)
        >>> interact_widget = ipyaudio.playback_widget(audio_connector)
        >>> IPython.display.display(interact_widget)

    :parameters:
        - audio_connector : ipyaudio.AudioConnector
          An AudioConnector object

    :returns:
        - interact : IPython container widget
          An IPython interact widget
    '''

    play_widget = IPython.html.widgets.ToggleButtonWidget(value=False)

    def wrapper_f(**kwargs):
        '''A wrapper function to handle instancemethods in interact'''
        audio_connector.set_state(**kwargs)

    return IPython.html.widgets.interactive(wrapper_f, active=play_widget)
