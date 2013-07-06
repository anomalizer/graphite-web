import fnmatch
from graphite.node import BranchNode, LeafNode
from graphite.logger import log
from graphite.koolstof.models import KoolstofFs

class KoolstofFinder(object):
    def __init__(self):
        pass

    def find_nodes(self, query):
        #TODO: not ignore time components

        return self._find_nodes(query.pattern.split('.'), 0, '')

    def _find_nodes(self, parts, current_level, parent_path):

        if len(parts) == current_level:
            if KoolstofFs.objects.filter(path=parent_path):
                yield parent_path  # TODO: leaf v/s branch
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
