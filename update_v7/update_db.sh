sql_file="flumut_db.sql"
sqlite_file="update_v7/sql_files/flumut_db.sqlite"
sql_updates_file="update_v7/sql_files/sql_updates.sql"
sql_updated_file="update_v7/sql_files/flumut_db.sql"

rm $sqlite_file
cat $sql_file | sqlite3 $sqlite_file

python update_v7/sql_updates.py >$sql_updates_file
cat $sql_updates_file | sqlite3 $sqlite_file

sqlite3 $sqlite_file .dump  >$sql_updated_file
