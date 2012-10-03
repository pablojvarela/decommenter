# By pablojvarela
# Aug 2012
# https://github.com/pablojvarela
# Licensed for use under http://www.apache.org/licenses/LICENSE-2.0
#
import argparse
import fileinput
import os
from xml.etree import ElementTree as et


EXT_FILTER = ''
def filter_extension(extension):
    global EXT_FILTER
    if extension != None:
        EXT_FILTER = '.' + extension


REGION_FILTER = ''
def filter_region(region):
    global REGION_FILTER
    if region != None:
        REGION_FILTER = '#region ' + region



def extract(source_file):    
    print "Extracting..."
    p, e = os.path.splitext(source_file)
    dita_tmp = p + '.ext.tmp'

    region = False
    with open(dita_tmp, 'w') as tmp:
        for line in fileinput.input(source_file):
            # Save all lines inside #region DOC
            if REGION_FILTER in line:
                region= True
            if "#end" in line:
                region= False
            else: # Somehow the first REGION_FILTER survives if we do not kill it here
                if region and REGION_FILTER not in line:
                    tmp.write(line)
    return dita_tmp



def decomment(source_file):
    print "De-commenting..."
    p, e = os.path.splitext(source_file)
    dita_tmp = p + '.dec.tmp'
    
    with open(dita_tmp, 'w') as tmp:
        tmp.write(u'<dita>\n')
        for line in fileinput.input(source_file):
            # Remove all '///'
            if '///' in line:
                i = line.find('///')
                line = line[:i] + line[i+3:]
                tmp.write(line)
        tmp.write(u'\n</dita>')
    return dita_tmp



def split(source_file):
    print "Splitting..."
    splits = []
    d, n = os.path.split(source_file)
    
    tree = et.parse(source_file)
    root = tree.getroot()
    for child in root:
        filename = os.path.join(d, child.attrib['id'] + ".dita")
        splits.append(filename)
        xml = et.tostring(child, encoding="utf8")
        with open(filename, 'w') as f:
            f.write(xml)
    return splits
    


def pyg(source_file):
    p, e = os.path.splitext(source_file)
    if e == EXT_FILTER:
        print "Pygging ", source_file
        ext_tmp = extract(source_file)
        print "Extracted at ", ext_tmp 
        dec_tmp = decomment(ext_tmp)
        print "De-commented at ", dec_tmp
        spl_tmp = split(dec_tmp)
        print "Splits at ", spl_tmp


def main():
    # Parse command line options
    parser = argparse.ArgumentParser()     
    parser.add_argument("-x", "--extract",
                        action='store_true',
                        help='Extracts DITA files from source code files. This is the default behavior.')
    parser.add_argument("-i", "--insert", # To Do: not implemented
                        action='store_false',
                        help='Inserts DITA content into source code files.')
    parser.add_argument("-g", "--region",
                        nargs='?',
                        default= 'DOC',
                        help='Filters which #region to parse for DITA content. Default\'s to  \'DOC\'.')
    parser.add_argument("-e", "--extension",
                        nargs='?',
                        default= 'cs',
                        help='Filters filenames by extension. A value of "cs" will only parse *.cs files, ignoring any other file.')
    parser.add_argument("-r", "--recursive",
                        action='store_true',
                        help='Recursively parse all sub-folders and files under source_path. See option "-i".')
    parser.add_argument("source_path", 
                         nargs='+',
                         help='The path to source files with documentation as code comments. Separate multiple paths with spaces.')
    args = parser.parse_args()


    # Set a value for the region filter
    filter_region(args.region)
    print "Region filter set: ", REGION_FILTER
 
    # Set a value for the extension filter
    filter_extension(args.extension)
    print "Extension filter set: ", EXT_FILTER

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