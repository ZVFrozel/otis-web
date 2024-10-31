"""
DiamondFinder: Scans files for hidden "diamond" patterns.

This script defines a `DiamondFinder` class to scan text files for character 
sequences ("diamonds") matching given constraints on character set and length.
When run, it automatically detects the `otis-web` directory (no matter where 
the script is placed within `otis-web`) and recursively scans for diamonds, 
outputting matches with tags.

Find this code in a GitHub gist:
https://gist.github.com/zvfrozel/6af7ded7daf1c761bf8bdf6ebec08429

Simple RegEx that does this in GitHub search:
>>> owner:vEnhance /[a-f0-9]{24,26}/

### Usage:
1. Place this script anywhere within the `otis-web` directory.
2. Run in the terminal:
   
   ```bash
   python path/to/diamonds.py

Alternatively, you can run this on a python shell:
>>> from hacks.diamonds import DiamondFinder
>>> otis_df = DiamondFinder(chars='0123456789abcdef', minlen=24, maxlen=26)
>>> otis_df.scandir('blah/blah/blah/otis-web/', deep=True, exclude='.lock')
...
>>> print(otis_df)

I got 4 legitimate diamonds and 14 charisma points doing this.
"""

import os
import io
import pathlib
import warnings
from collections import defaultdict


class DiamondFinder(defaultdict):
    def __init__(self, chars, minlen, maxlen, notify_diamonds=False):
        self.chars = chars
        self.minlen = minlen
        self.maxlen = maxlen
        self.notify_diamonds = notify_diamonds
        super().__init__(list)

    def __repr__(self):
        return f'{__class__.__name__}({super(defaultdict, self).__repr__()})' 

    def __str__(self):
        return '\n'.join(self.keys())

    def scan(self, source=None, tag=None):
        """
        Public-facing scan function. Scan strings or text streams.
        Set the tag argument to tag where the diamond was found.
        The tag will also be expanded to include the line number.
        """
        if source is None:
            return
        if tag is None:
            tag = ()
        elif not isinstance(tag, tuple):
            tag = (tag,)
        if isinstance(source, str):
            self.scantext(source, tag)
        elif isinstance(source, io.TextIOBase):
            self.scanstream(source, tag)

    def scantext(self, text, tag=()):
        """Scan text string for diamonds."""
        lines = text.split('\n')
        for count, line in enumerate(lines, 1):
            linetag = tag + (count,)
            self.scanline(line + '\n', linetag)

    def scandir(self, directory, deep=False, tag=(), **kwargs):
        """
        Scan all files in directory.
        If deep is set to True, scan nested files too.
        """
        dirtag = tag + (directory,)
        if deep:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    self.scanfile(
                        os.path.join(root, file),
                        relpath=directory,
                        tag=dirtag,
                        **kwargs
                    )
        else:
            for file in os.listdir(directory):
                fullpath = os.path.join(directory, file)
                if os.path.isfile(fullpath):
                    self.scanfile(
                        fullpath,
                        relpath=directory,
                        tag=dirtag,
                        **kwargs
                    )

    def scanfile(self, file, include=None, exclude=None, relpath=None, tag=()):
        """
        Scan a file for diamonds.
        Extensions can be set to a list of file extensions to check,
            other file types are not opened or scanned.
        """
        if not self.check_extension(file, include, exclude):
            return
        filetag = file if relpath is None else os.path.relpath(file, relpath)
        tag = tag + (filetag,)
        # TODO: We need a patch when the encoding is not utf-8
        with open(file, mode='r', encoding='utf-8') as stream:
            self.scanstream(stream, tag)

    @staticmethod
    def check_extension(file, include=None, exclude=None):
        """
        Check whether the file extension is
        in the extensions to include and not in the extensions to exclude.
        """
        extension = pathlib.Path(file).suffix
        if include is not None:
            if isinstance(include, str):
                include = [include]
            if extension in include:
                return False
        if exclude is not None:
            if isinstance(exclude, str):
                exclude = [exclude]
            if extension in exclude:
                return False
        return True

    def scanstream(self, stream, tag=()):
        """Scan a text stream, such as a io.TextIOBase object."""
        count = 1
        while True:
            try:
                line = stream.readline()
            except UnicodeDecodeError:
                warnings.warn(
                    f'Failed to decode line {count} of {tag}',
                    UnicodeWarning
                )
            else:
                if not line:
                    break
                linetag = tag + (count,)
                self.scanline(line, linetag)
            finally:
                count += 1

    def scanline(self, line, tag=()):
        """
        Scan one line of text for diamonds.
        The line must end with "\n".
        """
        # TODO: We need a patch when the encoding is not utf-8
        diamond_array = bytearray(self.maxlen)
        index = 0
        for char in line:
            if char in self.chars:
                if index >= self.maxlen:
                    continue
                diamond_array[index] = ord(char)
                index += 1
            else:
                if (self.minlen <= index <= self.maxlen):
                    diamond = diamond_array[:index].decode('utf-8')
                    self.add_diamond(diamond, tag)
                index = 0

    def add_diamond(self, diamond, tag=()):
        if self.notify_diamonds:
            print(diamond, tag)
        self[diamond].append(tag)


# Main function for scanning diamonds when running this file directly
def main():
    """
    Main function to detect and scan the 'otis-web' directory for hidden 
    diamond patterns.
    
    Automatically detects the 'otis-web' directory by searching up from the 
    script's location. Scans this directory recursively for diamonds, 
    excluding specific file types and directories.
    """
    
    # Configure DiamondFinder parameters
    chars = '0123456789abcdef'
    minlen = 24
    maxlen = 26
    notify_diamonds = True

    # Locate 'otis-web' directory by searching upward from current script location
    current_dir = pathlib.Path(__file__).resolve()
    otis_web_dir = None
    for parent in current_dir.parents:
        if parent.name == 'otis-web':
            otis_web_dir = parent
            break
    
    if otis_web_dir is None:
        raise FileNotFoundError("Could not locate 'otis-web' directory")

    # Instantiate and use DiamondFinder to scan
    finder = DiamondFinder(chars, minlen, maxlen, notify_diamonds)
    print(f"Scanning directory: {otis_web_dir}")

    # Exclude specific file types and directories during scanning
    finder.scandir(
        otis_web_dir, 
        deep=True, 
        exclude=['.pdf', '.png', '.lock', '.pack', '.idx']
    )

    # Output results
    print()
    print("Diamonds found:")
    print(finder)

    # Print the number of unique diamonds found
    print(f"\nTotal number of diamonds found: {len(finder)}")


# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
