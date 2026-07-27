import sqlite3

conn = sqlite3.connect('tracevault_dev.db')
cur = conn.cursor()

cur.execute('SELECT processing_status, COUNT(*) FROM recordings GROUP BY processing_status')
print('STATUS COUNTS:', cur.fetchall())

cur.execute("SELECT id, original_filename, processing_status, substr(processing_error,1,80) FROM recordings ORDER BY created_at DESC LIMIT 15")
recs = cur.fetchall()
print('\nALL RECORDINGS (recent 15):')
for r in recs:
    print(f"  {r[0][:8]}... | {r[1][:30]} | {r[2]} | err={r[3]}")

conn.close()
