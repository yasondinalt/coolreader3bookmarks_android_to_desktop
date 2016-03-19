Export/convert CoolReader3 bookmarks from Android program version to Desktop Windows version (I run it with Wine, not tested with Linux native version).

Input Android: .cr3/cr3db.sqlite
Output Linux Wine: ~/.wine/drive_c/users/{USER}/cr3/cr3hist.bmk

Take book id in table 'bookmark', column 'book_fk'.
On Linux: sqliteman cr3db.sqlite

python3.4 cr3db2histbmk.py