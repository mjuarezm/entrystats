import sys
import StringIO
import pycurl
import time
from os import makedirs
from os.path import join, dirname, realpath
import stem.control
from contextlib import contextmanager
from subprocess import Popen, PIPE

# current directory
RESULTS_DIR = join(dirname(realpath(__file__)), 'results')
CURRENT_DIR = join(RESULTS_DIR, time.strftime('%y%m%d_%H%M%S'))

# tor config
SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

# capture config
TIMEOUT = 60
MAX_SIZE = 1000
FILTER = 'tcp and host {entry_ip}'
COMMAND = ("tshark -nn -T fields -E separator=,"
           " -e ip.proto"
           " -e frame.time_epoch"
           " -e ip.src -e ip.dst"
           " -e tcp.srcport -e tcp.dstport"
           " -e ip.len -e ip.hdr_len -e tcp.hdr_len -e data.len"
           " -e tcp.flags -e tcp.seq -e tcp.ack"
           " -e tcp.window_size_value -e _ws.expert.message"
           " -e tcp.options.timestamp.tsval -e tcp.options.timestamp.tsecr"
           " -a duration:{timeout} -a filesize:{max_size} -s 0 -f \'{filter}\' > {output}")


class Sniffer():
    """Captures traffic logs using tshark."""
    def __init__(self, timeout=TIMEOUT, max_size=MAX_SIZE, filter=''):
        self.command = COMMAND.format(timeout=timeout, max_size=max_size, filter=filter)

    @contextmanager
    def record(self, output):
        try:
            self.p0 = Popen(self.command.format(output=output), stdout=PIPE, stderr=PIPE)
        finally:
            self.p0.kill()


def query(url):
    """
    Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
    """

    output = StringIO.StringIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
    query.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        query.perform()
        return output.getvalue()
    except pycurl.error as exc:
        raise ValueError("Unable to reach %s (%s)" % (url, exc))


def walk_guards(controller):
    """Iterate over all entry guard fingerprints."""
    for router_status in controller.get_network_statuses():
        if 'Guard' in router_status.flags:
            yield router_status.address, router_status.fingerprint


def build(controller, path):
    circuit_id = controller.new_circuit(path, await_build=True)

    def attach_stream(stream):
        if stream.status == 'NEW':
            controller.attach_stream(stream.id, circuit_id)

    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')
        check_page = query('https://check.torproject.org/')
        return check_page
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')


def main():
    makedirs(CURRENT_DIR)
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        for ip, fingerprint in walk_guards(controller):
            sniffer = Sniffer(filter=FILTER.format(entry_ip=ip))
            with sniffer.record(join(CURRENT_DIR, "%s.tshark" % fingerprint)):
                time.sleep(1)
                print('recording: %s' % fingerprint)
                try:
                    build(controller, [fingerprint])
                except Exception as exc:
                    print('%s => %s' % (fingerprint, exc))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
