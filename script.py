import sqlite3
import re

SQLITE_DB_PATH = 'domains.db'
BAD_PROMPTS = ['static.developer.xxx.com','sub.yyy.com']


def db_query_exect(query):
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
    except sqlite3.Error as error:
        print("Connection error", error)

    for row in cursor.execute(query):
        yield row

    conn.close()
    
def write_to_db(query):
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
    except sqlite3.Error as error:
       print("Connection error", error)
    
    cursor.execute(query)
    conn.commit()
    conn.close()

def test():
    query = 'SELECT * FROM rules;'
    result = db_query_exect(query)
    regex_pattern = {}
    for res in result:
        regex_pattern[res[0]] = res[1]


    query = 'SELECT * FROM domains;'
    result = db_query_exect(query)
    for record in result:
        filter = re.findall(regex_pattern[record[0]], record[1])
        if filter:
            print(filter)


if __name__ == "__main__":
    query = 'SELECT DISTINCT project_id FROM domains;'
    project_ids = db_query_exect(query)

    regexp_rule = []

    for id in project_ids:
    
        query = f'SELECT name FROM domains WHERE project_id="{id[0]}"'
        result = db_query_exect(query)

        good_domains = []

        for record in result:
            domen = record[0] 
            position = [domen.find(prompt) for prompt in BAD_PROMPTS]
            if sum(position) == -2:
                good_domains.append(domen)

        regexp = "|".join(good_domains)
        regexp_rule.append((id[0],regexp))

    for rule in regexp_rule:
        insert_query = f'INSERT INTO rules (project_id, regexp) VALUES ("{rule[0]}","{rule[1]}");'
        write_to_db(insert_query)

