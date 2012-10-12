# By pablojvarela
# Aug 2012
# https://github.com/pablojvarela
#
#  Copyright 2012 Pablo J. Varela
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import argparse
import codecs
import os
import shutil
from xml.etree import ElementTree as et



EXT_FILTER = ''         # The extension that filters which files are processed.
REGION_FILTER = ''      # The name that filters which code regions are processed.
XML_CATALOG_NAME = ''   # The XML Catalog to scavenge for DOCTYPE declarations.
XML_CATALOG_TREE = ''   # An ElementTree instance of the XML Catalog.
NEW_EXT = ''            # The extension to give to new, split files.
CLEAN = True
OUT_DIR = ''            # Output directory where to save extractdd files. 


def filter_extension(extension):
    global EXT_FILTER
    if extension != None:
        EXT_FILTER = '.' + extension


def filter_region(region):
    global REGION_FILTER
    if region != None:
        REGION_FILTER = '#region ' + region

def get_catalog(catalogname):
    global XML_CATALOG_NAME
    XML_CATALOG_NAME = catalogname    
    global XML_CATALOG_TREE
    XML_CATALOG_TREE = et.parse(open(catalogname, 'r'))

def set_extension(extension):
    global NEW_EXT
    NEW_EXT = '.' + extension


def set_outdir(dirpath):
    global OUT_DIR
    OUT_DIR = dirpath 


# Given a source file with code regions, extracts the contents of that region.
def extract(source_file):    
    print "Extracting..."
    p, e = os.path.splitext(source_file)
    ext_tmp = p + '.ext'

    region = False
    r = 0
    with codecs.open(ext_tmp, 'w', encoding='utf-8-sig') as tmp:
        with codecs.open(source_file, 'rb', 'utf-8') as f:
            for line in f:
                # Save all lines inside #region DOC
                if REGION_FILTER in line:
                    region= True
                    r += 1
                if "#end" in line:
                    region= False
                # REGION_FILTER survives if we do not kill it here
                elif region and REGION_FILTER not in line:
                    tmp.write(line)
    
    # Was any region extracted?
    if r > 0:
        return ext_tmp
    else:
        os.remove(ext_tmp)
        return None


# Given a file with code commented lines, de-comment them.
# Also, wrap lines with a <dita /> element.  
def decomment(source_file):
    print "De-commenting..."
    dec_tmp = source_file + '.dec'
    
    with codecs.open(dec_tmp, 'w', 'utf-8-sig') as tmp:
        tmp.write('<data>\n')
        with codecs.open(source_file, 'rb', 'utf-8-sig') as f:
            for line in f:
                # Remove all '///'
                if '///' in line:
                    i = line.find('///')
                    line = line[:i] + line[i+3:]
                    tmp.write(line)
        tmp.write('\n</data>')
    return dec_tmp


# Given a file with multiple XML tree siblings, split each into a new file.
# Each new file will be named after the XML tree's root element 'id' attribute.
# Each new file will have al appropriate DOCTYPE declaration from the XML Catalog
def split(source_file):
    print "Splitting..."
    
    splits = [] # The list of new files to create.
    d, n = os.path.split(source_file)

#    To DO: use pure unicode instead of numerical entities
#    with codecs.open(source_file, 'r', 'utf-8-sig') as u_source_file:
#        tree = et.parse(u_source_file)

#   BUG: When parsing from source_file, unicode characters are being converted to numerical entities 
    tree = et.parse(source_file)
    root = tree.getroot()
    for child in root:
        # Set name for new file
        filename = os.path.join(d, child.attrib['id'] + '.split')
        # A new tree from this child of root
        newtree = et.ElementTree(child)
        # Get DOCTYPE declaration
        declaration = declare(newtree)
        with codecs.open(filename, 'a', 'utf-8-sig') as f:
            f.write(declaration)
            newtree.write(f)



        splits.append(filename)
    return splits

# Given an xml.ElementTree, get the appropriate DOCTYPE declaration from an XML Catalog.
def declare(etree):
    print "Doctyping..."
    
    # The root defines the XML's type
    roottype = etree.getroot().tag
    
    # Parse the catalog for the appropriate DOCTYPE
    catalog_root = XML_CATALOG_TREE.getroot()
    for child in catalog_root:
        # Check the uri name with .dtd extension
        if roottype in child.attrib['uri'] and '.dtd' in child.attrib['uri']:
            publicid = child.attrib['publicId']
            uri = child.attrib['uri']
            break

    # Now return DOCTYPE values
    if publicid != None or uri != None:
        return '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE ' + roottype + ' PUBLIC "' + publicid + '" "' + uri + '">\n'
    else:
        return '<?xml version="1.0" encoding="UTF-8"?>\n'
            


#    Given a source code file:
#        1. Extract lines within a certain region. Decommenter.py expects XML trees as code comments in those lines.
#        2. Eliminate comment markers from each line.
#        3. Save each XML tree as a new file.
#        4. Add DOCTYPE declarations to each new file.
def pyg(source_file):
    # Process only files with a given extension:
    source_file_path, source_file_extension = os.path.splitext(source_file)
    if source_file_extension == EXT_FILTER:
        print "Pygging ", source_file
        
        extraction_tmp = extract(source_file)
        if extraction_tmp == None:
            print 'Nothing to extract in ', source_file
        else:
            print "Extracted at ", extraction_tmp 
        
            decomment_tmp = decomment(extraction_tmp)
            print "De-commented at ", decomment_tmp
            
            split_tmp = split(decomment_tmp)
            print "Splits at ", split_tmp
            
            print 'Renaming files...'
            final_files = []
            for old in split_tmp:
                    p, e = os.path.splitext(old)
                    new = p + NEW_EXT
                    shutil.copy(old, new)
                    final_files.append(new)
    
            print 'Moving files...'
            if not os.path.exists(OUT_DIR):
                os.makedirs(OUT_DIR)
            for src in final_files:
                oldpath, filename = os.path.split(src)
                dst = os.path.join(OUT_DIR, filename)
                
                shutil.move(src, dst)
                print "\t Moved ", oldpath, dst
    
            if CLEAN:
                print 'Removing temporary files...'
                os.remove(extraction_tmp)
                os.remove(decomment_tmp)
                for s in split_tmp:
                    os.remove(s)
            else:
                print "Keeping temporary files."




def main():
    # Parse command line options
    parser = argparse.ArgumentParser()     
    parser.add_argument("-x", "--extract",
                        action='store_true',
                        help='Extracts DITA files from source code files. This is the default behavior.')
    parser.add_argument("-i", "--insert", # To Do: not implemented
                        action='store_false',
                        help='Inserts DITA content into source code files. * Not implemented. *')
    parser.add_argument("-c", "--catalog",
                        nargs='?',
                        help='Specifies which XML Catalog to use to resolve DOCTYPE declarations. Only public declarations with uri resolves are supported.')
    parser.add_argument("-g", "--region",
                        nargs='?',
                        default= 'DOC',
                        const= 'DOC',
                        help='Filters which #region to parse for DITA content. Default\'s to  \'DOC\'.')
    parser.add_argument("-f", "--files",
                        nargs='?',
                        default= 'cs',
                        const= 'cs',
                        help='Filters filenames by extension. A value of "vx yz" will only parse *.vx and *.yz files, ignoring any other file. Separate multiple extensions with spaces.')
    parser.add_argument("-e", "--extension",
                        nargs='?',
                        default= 'dita',
                        const= 'dita',
                        help='Specifies what extension to append to created files. Do not precede with \'.\'.')
    parser.add_argument("-r", "--recursive",
                        action='store_true',
                        help='Recursively parse all sub-folders and files under source_path.')
    parser.add_argument("-y", "--dirty",
                        action='store_false',
                        help='Keep all temporary files. Good for debugging.')
    parser.add_argument("-o", "--out",
                        nargs='?',
                        default= '',
                        const= '',
                        help='Directory where to save extracted DITA files. Non-existing directories will be created.')
    parser.add_argument("source_path", 
                         nargs='+',
                         help='The path to source files with documentation as code comments. Separate multiple paths with spaces.')
    args = parser.parse_args()


    # Set a value for the region filter
    filter_region(args.region)
    print "Region filter set: ", REGION_FILTER
 
    # Set a value for the extension filter
    filter_extension(args.files)
    print "Extension filter set: ", EXT_FILTER
    
    # Set the extension of created files
    set_extension(args.extension)
    print "Extension for created files: ", NEW_EXT
    
    # Set the XML Catalog
    get_catalog(args.catalog)
    print "XML Catalog: ", XML_CATALOG_NAME
    
    # Turn cleaning on or off
    if args.dirty == False:
        global CLEAN
        CLEAN = False

    # Set Output Directory
    set_outdir(args.out)
    print "Output directory: ", OUT_DIR

    # Process files
    if args.recursive:
        for path in args.source_path:
            for root, dirs, files in os.walk(path):
                for filename in files:
                    source_file = os.path.join(root, filename)
                    pyg(source_file)
    else:
        for source_file in args.source_path:
            pyg(source_file)


    print "End."


if __name__ == "__main__":
    main()