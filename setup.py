from setuptools import setup


setup(
  name='m42pl-commands-lab',
  author='@jpclipffel',
  url='https://github.com/jpclipffel/m42pl-commands-lab',
  version='1.0.0',
  packages=['m42pl_commands_lab',],
  install_requires=[
    'm42pl',
    'm42pl_commands',
    # ---
    'Pillow',
    'selenium',
    'mediapipe',
    'opencv-contrib-python'
  ]
)
