from django import dispatch

"""
Creates a signal to be triggered after a balance gets increased.
"""

add_balance_signal = dispatch.Signal()



