"""
EFC Four-Channel Consistency Test

One-parameter test of EFC background coupling against BAO, RSD, CMB lensing, and SN Ia.
"""

from .four_channel_test import (
    FourChannelTest,
    TransitionFunction,
    ChannelResult,
    PAPER_RESULTS,
)

__all__ = ['FourChannelTest', 'TransitionFunction', 'ChannelResult', 'PAPER_RESULTS']
__version__ = '1.0.0'
