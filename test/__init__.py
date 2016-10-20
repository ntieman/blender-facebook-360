import os
import sys

__dir__ = os.path.dirname(os.path.realpath(__file__))


def path(relative):
    return os.path.join(__dir__, relative)


sys.path.insert(0, path('../src'))
