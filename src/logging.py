import inspect
import sys
from typing import Optional

LocType = Optional[inspect.FrameInfo]


class LoggerContext:
    def __init__(self, name: str):
        self.name = name
        self.context_str = "[%s]" % self.name

    def sub_contex(self, name: str):
        logger = getLogger(name)
        logger.parent = self
        logger.context_str = self.context_str + logger.context_str
        return logger

    def __self__(self, name: str):
        return self.sub_contex(name)

    def _loc_str(self, loc: LocType = None):
        if loc is None:
            return ""
        return 'File "%s", line %d' % (loc.filename, loc.lineno)

    def _msg_str(self, fstr: str, *args):
        try:
            return fstr.format(*args)
        except IndexError:
            self.ERROR(
                'Failed format log message \n\tfstr="{}"\n\targs=[{}]', fstr, args
            )
            return fstr

    def _output(self, logtype: str, fstr: str, args: tuple, loc: LocType = None):
        msg_str = self._msg_str(fstr, *args)
        output = "{} {}: {}\n".format(logtype, self.context_str, msg_str)
        if loc:
            output += "\t{}\n".format(self._loc_str(loc))
        return output

    def ERROR(self, fstr: str, *args, loc: LocType = None):
        sys.stderr.write(self._output("ERROR", fstr, args, loc))

    def WARNING(self, fstr: str, *args, loc: LocType = None):
        sys.stdout.write(self._output("WARNING", fstr, args, loc))

    def INFO(self, fstr: str, *args, loc: LocType = None):
        sys.stdout.write(self._output("INFO", fstr, args, loc))

    def DEBUG(self, fstr: str, *args, loc: LocType = None):
        sys.stdout.write(self._output("DEBUG", fstr, args, loc))


def _call_location(call_context: int = 0) -> LocType:
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    return caller_frame[call_context + 1]
