import fnmatch
from graphite.node import BranchNode, LeafNode
from graphite.intervals import Interval, IntervalSet
from graphite.logger import log

from graphite.koolstof.models import KoolstofFs, KoolstofTimeseries


class KoolstofFinder(object):
    def __init__(self):
        pass

    def find_nodes(self, query):
        #TODO: not ignore time components

        return self._find_nodes(query.pattern.split('.'), 0, '')

    def _find_nodes(self, parts, current_level, parent_path):

        if len(parts) == current_level:
            inodes = KoolstofFs.objects.filter(path=parent_path)
            if inodes:
                inode = inodes[0]
                if inode.metric_registry:
                    reader = KoolstofReader(inode.metric_registry.id, parent_path)
                    yield LeafNode(parent_path, reader)
                else:
                    if parent_path:  # special check for empty path
                        yield BranchNode(parent_path)
        else:
            component = parts[current_level]
            new_path = '%s.%s' % (parent_path, component) if parent_path else component

            if '*' in component:
                candidates = []
                for x in KoolstofFs.objects.filter(parent__path=parent_path):
                    f = x.lastname
                    partial_path = '%s.%s' % (parent_path, f) if parent_path else f
                    candidates.append(partial_path)

                for y in fnmatch.filter(candidates, new_path):
                    for z in self._find_nodes(parts, current_level + 1, y):
                        yield z
            else:
                for x in self._find_nodes(parts, current_level + 1, new_path):
                    yield x


class KoolstofReader(object):
    def __init__(self, metric_int_id, path):
        self.num_id = metric_int_id
        self.path = path

    def get_intervals(self):
        x = self._range()
        return IntervalSet([Interval(x['start'], x['end']), ])

    def fetch(self, startTime, endTime):
        x = self._range()
        step = x['step']
        eff_start = max(int(startTime) / step * step, x['start'])
        eff_end = min(int(endTime) / step * step, x['end'])

        if(eff_end < x['start']):
            return  # requested end before available start
        elif(eff_start > x['end']):
            return  # requested start ahead of available end
        else:
            time_info = (eff_start, eff_end, x['step'])
            start_ptr = x['tail'] - ((x['end'] - eff_start) / x['slots'])
            end_ptr = x['tail'] - ((x['end'] - eff_end) / x['slots'])
            if start_ptr > 0:
                if end_ptr > 0:
                    pass
            #  return (time_info, self._efetch(x))
            pass

    def __repr__(self):
        return '<KoolstofReader[%x]: %s (%d)>' % (id(self), self.path, self.num_id)

    def _range(self):
        row = KoolstofTimeseries.objects.defer('measurements').get(pk=self.num_id)
        end_time = row.tail_time
        start_time = end_time - row.step_in_seconds * row.field_slots
        return {'start': start_time, 'end': end_time,
                'step': row.step_in_seconds, 'v': row.field_version,
                'slots': row.field_slots, 'tail': row.tail_ptr}
