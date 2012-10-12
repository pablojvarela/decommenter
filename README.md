decommenter
===========

Yet another de-commenter tool

    $ python decommenter.py -h
    usage: decommenter.py [-h] [-x] [-i] [-c [CATALOG]] [-g [REGION]] [-f [FILES]]
                          [-e [EXTENSION]] [-r] [-y]
                          source_path [source_path ...]

    positional arguments:
      source_path           The path to source files with documentation as code
                            comments. Separate multiple paths with spaces.

    optional arguments:
      -h, --help            show this help message and exit
      -x, --extract         Extracts DITA files from source code files. This is
                            the default behavior.
      -i, --insert          Inserts DITA content into source code files. * Not
                            implemented. *
      -c [CATALOG], --catalog [CATALOG]
                            Specifies which XML Catalog to use to resolve DOCTYPE
                            declarations. Only public declarations with uri
                            resolves are supported.
      -g [REGION], --region [REGION]
                            Filters which #region to parse for DITA content.
                            Default's to 'DOC'.
      -f [FILES], --files [FILES]
                            Filters filenames by extension. A value of "vx yz"
                            will only parse *.vx and *.yz files, ignoring any
                            other file. Separate multiple extensions with spaces.
      -e [EXTENSION], --extension [EXTENSION]
                            Specifies what extension to append to created files.
                            Do not precede with '.'.
      -r, --recursive       Recursively parse all sub-folders and files under
                            source_path.
      -y, --dirty           Keep all temporary files. Good for debugging.
      -o [OUT], --out [OUT] Directory where to save extracted DITA files. 
                            Non-existing directories will be created.
    

This nifty script takes source code files which contain XML structures inside code #regions as comments. For example:
      
      File myPython.py:
      #!/bin/python
      # region Doc
      # <doc>Prints a message to the world.</doc>
      # endregion
      print 'Hello, World!'
    
It outputs as many XML files as necessary to hold the parsed XML:
      
      File doc.xml:
      <?xml version=1.0?>
      <doc>Prints a message to the world.</doc>
    
Check the issue tracker for known issues and To Dos.