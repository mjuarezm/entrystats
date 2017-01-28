import time
import stem.control


def it_guard_ips(controller):
    """Iterate over all entry guard fingerprints."""
    for router_status in controller.get_network_statuses():
        if 'Guard' in router_status.flags:
            yield router_status.fingerprint


def measure(controller, path):
    circuit_id = controller.new_circuit(path, await_build = True)
  
    def attach_stream(stream):
        if stream.status == 'NEW':
            controller.attach_stream(stream.id, circuit_id)
  
    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)
  
    stats = []
    try:
  
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
  
        return stats
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')


if __name__ == "__main__":
    with stem.control.Controller.from_port() as controller:
	controller.authenticate()
	for entry in it_entry_guards(controller):
	    time.sleep(1)
	    print('recording: %s' % entry)
	    try:
		stats = measure(controller, [entry])
		print('%s => %0.2f seconds' % (entry, stats))
	    except Exception as exc:
		print('%s => %s' % (entry, exc))
