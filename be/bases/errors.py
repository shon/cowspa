complete_retcode = 0
invalid_api = 1
auth_failed = 2
validation_failed_retcode = 3
execution_error = 4
exception_retcode = 5

class WrapperException(Exception):
    def __init__(self, retcode, result, *args, **kw):
        self.suggested_retcode = retcode
        self.suggested_result = result
        super(WrapperException, self).__init__(*args, **kw)

class APIExecutionError(Exception):
    def __init__(self, msgs, data=None):
        self.msgs = msgs if isinstance(msgs, (list, tuple)) else (msgs,)
        super(APIExecutionError, self).__init__(*args, **kw)
