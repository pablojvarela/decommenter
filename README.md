decommenter
===========

Yet another de-commenter tool

    $ python decommenter.py -h
    usage: decommenter.py [-h] [-x] [-i] [-g [REGION]] [-e [EXTENSION]] [-r]
                          source_path [source_path ...]
    
    positional arguments:
      source_path           The path to source files with XML structures in code
                            comments. Separate multiple paths with spaces.
    
    optional arguments:
      -h, --help            show this help message and exit
      -x, --extract         Extracts XML files from source code files. This is
                            the default behavior.
      -i, --insert          Inserts XML content into source code files as comments.
      -g [REGION], --region [REGION]
                            Filters which #region to parse for DITA content.
                            Default's to 'DOC'.
      -e [EXTENSION], --extension [EXTENSION]
                            Filters filenames by extension. A value of "xy" will
                            only parse *.xy files, ignoring any other file.
      -r, --recursive       Recursively parse all sub-folders and files under
                            source_path. See option "-i".


This nifty script takes source code files which contain XML structures inside code #regions as comments. For example:
      
      File myPython.py:
      #!/bin/python
      # <doc>Prints a message to the world.</doc>
      print 'Hello, World!'
    
It outputs as many XML files as necessary to hold the parsed XML:
      
      File doc.xml:
      <?xml version=1.0?>
      <doc>Prints a message to the world.</doc>
    
Check the issue tracker for known issues and To Dos.