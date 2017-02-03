import sys
import logging
from scapy.all import *
from time import strftime, sleep
import multiprocessing as mp
from os.path import join, dirname, realpath
from stem import control, process
from itertools import repeat

# crawl
NUM_PROCS = mp.cpu_count()
NUM_BATCHES = 100
NUM_SAMPLES = 3
HEADERS = ['sample_id', 'guard_fp', 'latency']
TIMESTAMP = strftime('%y%m%d_%H%M%S')

# directories
BASE_DIR = dirname(realpath(__file__))
RESULTS_DIR = join(BASE_DIR, 'results')
LOG_PATH = join(RESULTS_DIR, '%s.log' % TIMESTAMP)
DATA_PATH = join(RESULTS_DIR, '%s.csv' % TIMESTAMP)

# network
CONTROL_PORT = '9051'
SYN_TIMEOUT = 10
SAMPLE_SLEEP = 0.4

# logger
LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
logging.basicConfig(filename=LOG_PATH, format=LOG_FORMAT, level=logging.DEBUG)


def get_entries():
    """Return network statuses from Tor consensus."""
    entries = []
    p = process.launch_tor_with_config({'ControlPort': CONTROL_PORT})
    with control.Controller.from_port(port=int(CONTROL_PORT)) as c:
        c.authenticate()
        for s in c.get_network_statuses():
            if 'Guard' in s.flags:
                entries.append(((s.address, s.or_port), s.fingerprint))
    p.kill()
    return entries


def connect(address):
    """Make TCP connection and return SYN and SYN+ACK packets."""
    dst, dport = address
    syn = TCP(sport=RandShort(), dport=dport, flags='S')
    synack = sr1(IP(dst=dst) / syn, timeout=SYN_TIMEOUT)
    if synack is None:
        raise Exception("No response from server: {0}:{1}".format(*address))
    return syn, synack


def latency(p1, p2):
    """Compute time difference between two packets."""
    return p2.time - p1.time


def get_stats(packets):
    """Return stats about list of packets."""
    STATS = [latency, ]
    return map(str, [stat(*packets) for stat in STATS])


def measure_entry(entry):
    """Connect to entry."""
    address, fp = entry
    sleep(5 * random.random())
    samples = []
    for i in xrange(NUM_SAMPLES):
        sample = None
        try:
            logging.info("Probing: {}".format(fp))
            packets = connect(address)
            sample_id = '%s%s' % (strftime('%d%H%M%S'), i)
            sample = [sample_id, fp] + get_stats(packets)
        except Exception as e:
            logging.exception("Entry {0}: {1}".format(fp, e))
        samples.append(sample)
        sleep(SAMPLE_SLEEP)
    return samples


def gen_it_entries(entries):
    """Return iterator over entries according to number of samples"""
    def it_entries():
        for batch in repeat(entries, NUM_BATCHES):
            for entry in batch:
                yield entry
    return it_entries


def main():
    it_entries = gen_it_entries(get_entries())
    with open(DATA_PATH, 'a') as f:
        f.write(','.join(HEADERS) + '\n')
        p = mp.Pool(NUM_PROCS)
        for samples in p.imap(measure_entry, it_entries()):
            for sample in samples:
                if sample is not None:
                    f.write(','.join(sample) + '\n')
                    f.flush()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
