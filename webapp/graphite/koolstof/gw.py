import fnmatch
from graphite.node import BranchNode, LeafNode
from graphite.logger import log


class KoolstofFinder(object):
    def __init__(self):
        pass

    def find_nodes(self, query):
        #TODO: not ignore time components

        return self._find_nodes(query.pattern.split('.'), 0, '')

    def _find_nodes(self, parts, current_level, parent_path):

        if len(parts) == current_level:
            yield parent_path  # TODO: verify it exists
        else:
            component = parts[current_level]
            if '*' in component:
                pass  # TODO :real impl
            else:
                new_path = '%s.%s' % (parent_path, component) if parent_path else component
                for x in self._find_nodes(parts, current_level + 1, new_path):
                    yield x
