import sys
import time
from os import makedirs, killpg, getpgid, setsid
from os.path import join, dirname, realpath
from stem.control import Controller
import random
import socket
from contextlib import contextmanager
from subprocess import Popen, PIPE
import logging
from signal import SIGTERM
from multiprocessing import cpu_count, Pool


# current directory
RESULTS_DIR = join(dirname(realpath(__file__)), 'results')
TIMESTAMP = time.strftime('%y%m%d_%H%M%S')
CUR_DIR = join(RESULTS_DIR, TIMESTAMP)

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
           " -e tcp.flags -e tcp.seq -e tcp.ack -e tcp.nxtseq"
           " -e tcp.analysis.acks_frame -e tcp.window_size_value"
           " -e _ws.expert.message"
           " -e tcp.options.timestamp.tsval -e tcp.options.timestamp.tsecr"
           " -o tcp.relative_sequence_numbers:False -f")

# globals
NUM_PROCS = cpu_count()
CONTROL_PORT = '9051'
NUM_SAMPLES = 10


@contextmanager
def record(output, filter=''):
    """Capture network packets with tshark."""
    with open(output, 'w') as f:
        cmd = COMMAND.split() + ['%s' % filter]
        logger.info("tshark cmd: %s", ' '.join(cmd))
        p = Popen(cmd, stdout=f, stderr=PIPE, preexec_fn=setsid)
        yield p
        killpg(getpgid(p.pid), SIGTERM)


def walk_guards(controller):
    """Iterate over all entry guard fingerprints."""
    for rs in controller.get_network_statuses():
        if 'Guard' in rs.flags:
            yield (rs.address, rs.or_port), rs.fingerprint


def all_entries():
    """Return all entry guards in the consensus."""
    entries = []
    with Controller.from_port(port=int(CONTROL_PORT)) as controller:
        controller.authenticate()
        for address, fingerprint in walk_guards(controller):
            entries.append((address, fingerprint))
    return entries


def connect(address):
    """Make TCP connectio to ip:port."""
    logger.debug("Attempt connection to: %s:%s" % address)
    s = socket.create_connection(address, timeout=10)
    s.close()


def measure_entry(entry):
    """Capture traffic genrated by making a TCP connection to entry."""
    address, fp = entry
    ip, _ = address
    output = join(CUR_DIR, '%s_%s.tshark' % (fp, time.strftime('%d%H%M%S')))
    time.sleep(2 * (random.random() + 1))
    with record(output, FILTER.format(entry_ip=ip)):
        time.sleep(1)
        try:
            connect(address)
        except Exception as exc:
            logger.exception('%s => %s' % (id, exc))
        else:
            time.sleep(1)


def main():
    makedirs(CUR_DIR)
    entries = all_entries()
    for _ in xrange(NUM_SAMPLES):
        # parallelize visits for each sample
        p = Pool(NUM_PROCS)
        p.map(measure_entry, entries)
        p.close()
        p.join()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
