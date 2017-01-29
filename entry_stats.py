import sys
import time
from os import makedirs
from os.path import join, dirname, realpath, isdir
import stem.control
import stem.process
from stem import Signal
from contextlib import contextmanager
from subprocess import Popen, PIPE
import logging

# current directory
RESULTS_DIR = join(dirname(realpath(__file__)), 'results')
TIMESTAMP = time.strftime('%y%m%d_%H%M%S')
CURRENT_DIR = join(RESULTS_DIR, TIMESTAMP)

# logger
FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger()
logfile = join(RESULTS_DIR, '%s.log' % TIMESTAMP)
fileHandler = logging.FileHandler(logfile)
fileHandler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

# capture config
FILTER = 'host {entry_ip}'
COMMAND = ("tshark -l -nn -T fields -E separator=,"
           " -e ip.proto"
           " -e frame.time_epoch"
           " -e ip.src -e ip.dst"
           " -e tcp.srcport -e tcp.dstport"
           " -e ip.len -e ip.hdr_len -e tcp.hdr_len -e data.len"
           " -e tcp.flags -e tcp.seq -e tcp.ack"
           " -e tcp.window_size_value -e _ws.expert.message"
           " -e tcp.options.timestamp.tsval -e tcp.options.timestamp.tsecr"
           " -f")


@contextmanager
def record(output, filter=''):
    """Capture network packets with tshark."""
    with open(output, 'w') as f:
        p = Popen(COMMAND.split() + ['%s' % filter], stdout=f, stderr=PIPE)
        yield p
        p.kill()


def walk_guards(controller):
    """Iterate over all entry guard fingerprints."""
    for router_status in controller.get_network_statuses():
        if 'Guard' in router_status.flags:
            yield router_status.address, router_status.fingerprint


def main():
    if not isdir(RESULTS_DIR):
        makedirs(RESULTS_DIR)
    makedirs(CURRENT_DIR)
    stem.process.launch_tor_with_config(config={'ControlPort': '9051'})
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        for i in xrange(3):
            for ip, fingerprint in walk_guards(controller):
                output = join(CURRENT_DIR, "%s_%s.tshark" % (fingerprint, i))
                with record(output, FILTER.format(entry_ip=ip)):
                    time.sleep(1)
                    logger.info('Recording: %s, %s' % (ip, fingerprint))
                    try:
                        controller.set_conf('EntryNodes', fingerprint)
                        controller.signal(Signal.HUP)
                        controller.signal(Signal.NEWNYM)
                        time.sleep(controller.get_newnym_wait())
                    except Exception as exc:
                        logger.exception('%s => %s' % (fingerprint, exc))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
