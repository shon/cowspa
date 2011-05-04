# Based on http://amix.dk/blog/post/19390
# We can add a bit more later
SIGNALS = {}

def connect(signal_key, callback):
    """Connect `callback` to signal's callback sequence.
    """
    if signal_key in SIGNALS:
        SIGNALS[signal_key].append( callback )
    else:
        SIGNALS[signal_key] = [callback]


def send_signal(signal_key, *args, **kwargs):
    """Sending a signal will iterate over a signal's callback.
    """
    if not signal_key in SIGNALS:
        raise Exception('No handlers for signal: %s' % signal_key)

    for callback in SIGNALS[signal_key]:
        callback(*args, **kwargs)
