# adding this in content-that-talks/modules/textgen, because i currently dont have a folder for general modules.

"""
Usage notes (personal experience):
    - generally, docs not clear enough; i had to figure out how to use it.
"""

import json
from abc import ABC, abstractmethod

# I wish this supported storage of nested objects
class PersistenceABC(ABC):
    """Handles saving to and loading from a file

    Note from myself to myself after using this:
    --
    on init -- need to call super().__init__(path)

    Arguments:
    --
    path -- the file where a description of your object is stored (for implement_filedata)

    Abstract methods:
    --
    object_to_filedata() -- Should return something that you can put into a file. (for saving)
    implement_filedata(filedata) -- Use data (like a dict or string or list) to edit/create/etc, the object. (for loading)

    Will grant you these methods:
    --
    save() -- Store the current state of the object in self.path
    load() -- Get data from self.path and implement it

    Dependencies
    --
    text_create(path, content)
    text_read(path)
    make_json(dic_or_list, path)
    open_json(path)
    """

    def __init__(self, path):
        """Set path, saver and loader"""

        self.path = path
        self.ext = path.split('.')[-1]
        
        # set saver and loader
        if self.ext == 'txt':
            self._saver = self._save_txt
            self._loader = self._load_txt
        elif self.ext == 'json':
            self._saver = self._save_json
            self._loader = self._load_json
        else:
            raise ValueError(f'extension must be txt or json, but path is {path}')

    # Set these to be allowed to use this class.

    @abstractmethod
    def object_to_filedata(self):
        """Should return something that you can put into a file. (for saving)"""
        pass
    @abstractmethod
    def implement_filedata(self, filedata):
        """Use data (like a dict or string or list) to edit/create/etc, the object. (for loading)"""
        pass

    # internal methods

    ## save to self.path
    def _save_txt(self, contents):
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(contents)
    def _save_json(self, contents):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(contents, f, indent=2)

    ## load from self.path
    def _load_txt(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            contents = f.read()
        return contents
    def _load_json(self):
        with open(self.path, 'r', encoding="utf-8") as f:
            contents = json.load(f)
        return contents

    # external methods

    def save(self):
        """Store the current state of the object in self.path"""
        filedata = self.object_to_filedata()
        self._saver(filedata)

    def load(self):
        """Get data from self.path and implement it"""
        filedata = self._loader()
        self.implement_filedata(filedata)
