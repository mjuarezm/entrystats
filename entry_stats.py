import sys
import logging
from scapy.all import *
from time import strftime, sleep
import multiprocessing as mp
from os.path import join, dirname, realpath
from stem import control

# crawl
PARALLEL = False
NUM_PROCS = mp.cpu_count()
NUM_SAMPLES = 100
HEADERS = ['sample_id', 'guard_fp', 'latency']
TIMESTAMP = strftime('%y%m%d_%H%M%S')

# directories
BASE_DIR = dirname(realpath(__file__))
RESULTS_DIR = join(BASE_DIR, 'results')
LOG_PATH = join(RESULTS_DIR, '%s.log' % TIMESTAMP)
DATA_PATH = join(RESULTS_DIR, '%s.csv' % TIMESTAMP)

# network
CONTROL_PORT = '9051'

# logger
LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(filename=LOG_PATH, format=LOG_FORMAT, level=logging.DEBUG)


def get_network_entries():
    """Return network statuses from Tor consensus."""
    entries = []
    with control.Controller.from_port(port=int(CONTROL_PORT)) as c:
        c.authenticate()
        for s in c.get_network_statuses():
            if 'Guard' in s.flags:
                entries.append(((s.address, s.or_port), s.fingerprint))
    return entries


def connect(address):
    """Make TCP connection and return SYN and SYN+ACK packets."""
    dst, dport = address
    syn = TCP(sport=RandShort(), dport=dport, flags='S')
    synack = sr1(IP(dst=dst) / syn, timeout=10)
    if synack is None:
        raise Exception("No response from server: {0}:{1}".format(*address))
    return syn, synack


def latency(p1, p2):
    """Compute time difference between two packets."""
    return p2.time - p1.time


def get_stats(packets):
    """Return stats about list of packets."""
    return map(str, [latency(*packets)])


def measure_entry(entry):
    """Connect to entry."""
    address, fp = entry
    min_fp = fp[:len(fp) / 2]
    logging.info("Probing: {}".format(fp))
    sample = None
    sleep(random.random())
    try:
        packets = connect(address)
        sample = [strftime('%d%H%M%S'), min_fp] + get_stats(packets)
    except Exception as e:
        logging.exception("Entry {0}: {1}".format(fp, e))
    else:
        sleep(0.5)
    return sample


def main():
    entries = get_network_entries()
    with open(DATA_PATH, 'a') as f:
        f.write(','.join(HEADERS) + '\n')
        for _ in xrange(NUM_SAMPLES):
            p = mp.Pool(NUM_PROCS)
            for result in p.imap(measure_entry, entries):
                if result is not None:
                    f.write(','.join(result) + '\n')
                    f.flush()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
