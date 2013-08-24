import fnmatch
from graphite.node import BranchNode, LeafNode
from graphite.intervals import Interval, IntervalSet
from graphite.logger import log

from time import time
import jsonrpclib

class LevelRpcFinder(object):
    def __init__(self, server_path):
        self.server = server_path

    def find_nodes(self, query):
        #TODO: not ignore time components

        return self._find_nodes(query.pattern.split('.'), 0, '')

    def _find_nodes(self, parts, current_level, parent_path):
        client = _get_rpc_client(self.server)

        if len(parts) == current_level: #  we have fully eval'ed the path
            if client.is_node_leaf(parent_path):
                reader = LevelRpcReader(parent_path, self.server)
                yield LeafNode(parent_path, reader)
            else:
                yield BranchNode(parent_path)
        else: #  we are still expanding a regex'ed path
            component = parts[current_level]
            new_path = '%s.%s' % (parent_path, component) if parent_path else component

            if '*' in component: #  does this segment need globbing?
                candidates = []
                for f in client.get_child_nodes(parent_path):
                    partial_path = '%s.%s' % (parent_path, f) if parent_path else f
                    candidates.append(partial_path)

                for y in fnmatch.filter(candidates, new_path):
                    for z in self._find_nodes(parts, current_level + 1, y):
                        yield z
            else:
                for x in self._find_nodes(parts, current_level + 1, new_path):
                    yield x


class LevelRpcReader(object):
    # TODO: fix the step
    step_in_seconds = 60

    def __init__(self, metric_name, server_url):
        self.metric = metric_name
        self.server = server_url

    def get_intervals(self):
        # pretend we support entire range for now
        return IntervalSet([Interval(1, int(time())), ])

    def fetch(self, startTime, endTime):
        client = _get_rpc_client(self.server)
        values = client.get_range_data(self.metric, startTime, endTime)
        if values:
            ts = [x[1] for x in values]
            time_info = (values[0][0], values[-1][0], self.step_in_seconds)
        else:
            time_info = (0, 0, self.step_in_seconds)
            ts = []
        return (time_info, ts)

    def __repr__(self):
        return '<LevelRpcReader[%x]: %s>' % (id(self), self.metric)


def _get_rpc_client(server):
    return jsonrpclib.Server(server)
