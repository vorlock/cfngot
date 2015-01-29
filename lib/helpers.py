import os
import fnmatch

class Helpers(object):
    def _find_all_files(suffix):
        """
        Finds all files recursively with the given suffix and returns list of
        them
        """
        matches = []
        for root, dirnames, filenames in os.walk('.'):
            for filename in fnmatch.filter(filenames, suffix):
                matches.append(os.path.join(root, filename))
        return matches
