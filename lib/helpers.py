import os
import fnmatch

class Helpers(object):
    def _find_all_files(suffix):
        """
        Finds all files recursively with the given suffix and returns list of
        them
        """
        matches = []
        excludes = ['env','venv']
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in excludes]
            for filename in fnmatch.filter(files, suffix):
                matches.append(os.path.join(root, filename))
        return matches
