from setuptools import setup

setup(
    name='ipyaudio',
    version='0.0',
    description='Bridge PortAudio, IPython interactive widgets, and DSP callbacks',
    author='Brian McFee',
    author_email='brian.mcfee@nyu.edu',
    url='http://github.com/bmcfee/ipyaudio',
    download_url='http://github.com/bmcfee/ipyaudio/releases',
    long_description="""\
        Bridge PortAudio, IPython interactive widgets, and DSP callbacks
    """,
    packages=['ipyaudio.py'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
    ],
    keywords='audio realtime interactive ipython',
    license='MIT',
    install_requires=[
        'IPython >= 2.0',
        'PyAudio >= 0.2.8',
        'numpy'
    ],
)
