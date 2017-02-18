import sys
import logging
from scapy.all import *
from time import sleep
from datetime import datetime
import multiprocessing as mp
from os.path import join, dirname, realpath
from stem import control, process
from itertools import repeat

# crawl
NUM_PROCS = mp.cpu_count()
NUM_BATCHES = 50
NUM_SAMPLES = 5
HEADERS = ['batch_id', 'sample_id', 'fp', 'flags', 'latency']
TIMESTAMP = datetime.now().strftime('%d%H%M%S')

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


def get_nodes():
    """Return network statuses from Tor consensus."""
    nodes = []
    p = process.launch_tor_with_config({'ControlPort': CONTROL_PORT})
    with control.Controller.from_port(port=int(CONTROL_PORT)) as c:
        c.authenticate()
        for s in c.get_network_statuses():
            nodes.append(((s.address, s.or_port), s.fingerprint, s.flags))
    p.kill()
    return nodes


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


def measure_node(node):
    """Connect to node."""
    address, fp, flags = node
    sleep(5 * random.random())
    samples = []
    ts, pid = datetime.now().strftime('%d%H%M%S%f'), id(mp.current_process())
    batch_id = '%s%s' % (ts, pid)
    for i in xrange(NUM_SAMPLES):
        sample = None
        try:
            logging.info("Probing: {}".format(fp))
            packets = connect(address)
            sample = [batch_id, i, fp, ' '.join(flags)] + get_stats(packets)
        except Exception as e:
            logging.exception("Node {0}: {1}".format(fp, e))
        samples.append(sample)
        sleep(SAMPLE_SLEEP)
    return samples


def gen_it_nodes(nodes):
    """Return iterator over nodes according to number of samples"""
    def it_nodes():
        for batch in repeat(nodes, NUM_BATCHES):
            for node in batch:
                yield node
    return it_nodes


def main():
    it_nodes = gen_it_nodes(get_nodes())
    with open(DATA_PATH, 'a') as f:
        f.write(','.join(HEADERS) + '\n')
        p = mp.Pool(NUM_PROCS)
        for samples in p.imap(measure_node, it_nodes()):
            for sample in samples:
                if sample is not None:
                    f.write(','.join(map(str, sample)) + '\n')
            f.flush()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
