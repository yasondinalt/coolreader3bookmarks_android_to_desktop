#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
"""
Export/convert CoolReader3 bookmarks from Android program version to Desktop
Windows version (I run it with Wine, not tested with Linux native version).

Input Android: .cr3/cr3db.sqlite
Output Linux Wine: ~/.wine/drive_c/users/{USER}/cr3/cr3hist.bmk

python3.4 coolreader3bookmarks_android_to_desktop.py

v0.3 TODO: merge bookmarks, not overwrite

v0.2
Now handle all books, no need in custom book id.

v0.1
Take book id in table 'bookmark', column 'book_fk'.
On Linux: sqliteman cr3db.sqlite
"""

import sqlite3 as sqlite

# access by key
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn = sqlite.connect("cr3db.sqlite")
conn.row_factory = dict_factory
cursor = conn.cursor()

cursor.execute("SELECT * FROM 'book'")
db_books = cursor.fetchall()

all_books = ""
for db_book in db_books:
    cursor.execute("SELECT * FROM 'bookmark' WHERE book_fk=? ORDER BY percent", (db_book['id'],))
    db_bookmarks = cursor.fetchall()

    bookmarks = ""
    for b in db_bookmarks:
        btype = 'lastpos' if b['type'] == 0 else 'position'
        bookmarks += """
    <bookmark type="{btype}" percent="{percent}%" timestamp="{timestamp}" shortcut="{shortcut}" page="0">
        <start-point>{start_pos}</start-point>
        <end-point/>
        </header-text>
        <selection-text>{pos_text}</selection-text>
        <comment-text/>
    </bookmark>
        """.format( btype = btype, 
                    percent = "{0:.2f}".format(b['percent']/100),
                    timestamp = b['time_stamp'],
                    shortcut = b['shortcut'],
                    start_pos = b['start_pos'],
                    pos_text = b['pos_text'])
    if len(bookmarks) > 0:
        all_books += """
  <file>
    <file-info>
      <doc-title>{title}</doc-title>
      <doc-author/>
      <doc-series/>
      <doc-filename>{filename}</doc-filename>
      <doc-filepath>{pathname}</doc-filepath>
      <doc-filesize>{filesize}</doc-filesize>
    </file-info>
    <bookmark-list>
    {bookmarks}
    </bookmark-list>
  </file>
        """.format( pathname = db_book['pathname'],
                    filename = db_book['filename'],
                    title = db_book['title'],
                    filesize = db_book['filesize'],
                    bookmarks = bookmarks)
                
                
bmk_body = """<?xml version="1.0" encoding="utf-8"?>
<FictionBookMarks>
{all_books}
</FictionBookMarks>
""".format( all_books = all_books)

with open('cr3hist.bmk', 'w', encoding='utf-8') as file:
    file.write(bmk_body)

