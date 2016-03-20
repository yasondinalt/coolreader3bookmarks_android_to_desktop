#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
import sys
from lxml import etree
from io import StringIO
from copy import deepcopy

tree_output = etree.parse(StringIO(
"""<FictionBookMarks>
</FictionBookMarks>"""))
output_root = tree_output.getroot()

tree_first = etree.parse("cr3hist_note.bmk")
tree_second = etree.parse("cr3hist_nook.bmk")

#create sets of files
def make_file_set(tree):
    _set = set()
    for file in tree.iterfind("file"):
        filename = file.xpath('.//doc-filename')[0].text
        _set.add(filename)
    return _set
    
def get_file(search, tree):
    for file in tree.iterfind("file"):
        filename = file.xpath('.//doc-filename')[0].text
        if search == filename:
            return file
            
#create sets of bookmarks
def make_bookmarks_set(elem):
    _set = set()
    for bmk in elem.xpath('.//bookmark'):
        percent = bmk.attrib['percent']
        _set.add(percent)
    return _set

def get_bookmark(search, elem):
    for bmk in elem.xpath('.//bookmark'):
        percent = bmk.attrib['percent']
        if search == percent:
            return bmk

set_files_first = make_file_set(tree_first)
set_files_second = make_file_set(tree_second)

files_intersection_list = sorted(list(set_files_first.intersection(set_files_second)))
files_not_intersected_list = sorted(list(set_files_first.symmetric_difference(set_files_second)))

print("Add not intersected books")
for name in files_not_intersected_list:
    file = get_file(name, tree_first)
    if file is None:
        file = get_file(name, tree_second)
    set_bmks = make_bookmarks_set(file)
    if len(set_bmks) > 1: # filter can be removed
        print(name)
        print("Bookmarks: %s \n" % len(set_bmks))
        output_root.append(file)

print("\n\n")
print("Add intersected books with merged bookmarks \n")
for name in files_intersection_list:
    file_first = get_file(name, tree_first)
    file_second = get_file(name, tree_second)
    
    # make clean file element
    file_general = deepcopy(file_first)
    for elem in file_general.xpath('.//bookmark'):
        elem.getparent().remove(elem)

    set_bmk_first = make_bookmarks_set(file_first)
    set_bmk_second = make_bookmarks_set(file_second)
    bmk_union_list = sorted(list(set_bmk_first.union(set_bmk_second)))

    if len(bmk_union_list) > 2: # filter can be removed
        print(name)
        print("Bookmarks: in first {0}, second {1}, total {2} \n".format(
            len(set_bmk_first), len(set_bmk_second), len(bmk_union_list)))
        for name in bmk_union_list:
            bmk = get_bookmark(name, file_first)
            if bmk is None:
                bmk = get_bookmark(name, file_second)
            file_general.xpath('.//bookmark-list')[0].append(bmk)
        output_root.append(file_general)

# try to fix txt bookmarks, but position not match precisely
# epub, fb2, html look like ok
for file in tree_output.iterfind("file"):
    filename = file.xpath('.//doc-filename')[0].text
    if filename.lower().endswith('txt'):
        for bmk in file.xpath('.//bookmark'):
            start_point = bmk.xpath('.//start-point')[0]
            start_point.text = start_point.text.replace('section/p', 'pre')


tree_output.write("cr3hist.bmk", encoding="utf-8", xml_declaration=True)
