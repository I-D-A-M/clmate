import sqlite3

while True:
    decision = input('Are your adding the index or removing it? (add/remove)')
    conn = sqlite3.connect('ClMATE_DB.db')
    curs = conn.cursor()

    if decision == 'add':
        print('Adding the index "results_index" to the results table under the UPN column...')
        curs.execute('create index results_index on results(UPN)')
        conn.commit()
        conn.close()    
    elif decision == 'remove':
        print('Dropping index from results table...')
        curs.execute('drop index results_index')
        conn.commit()
        conn.close()
    else:
        print('you need to select either "add" or "remove" you muppet!')
