import time

from src import database_binding as db_bind

def start_download(args):
    time.sleep(2)
    id = int
    url = str
    session = db_bind.init_db()
    while True:
        time.sleep(0.2)
        try:
            id, url = db_bind.get_wait_url(session)
            # need to parse url and write parser-information into db
            # for write into database, methods "update_state_by_id" and "update_row_by_id"
            # first way: create instance of WikiSpider and take him url (not working)
            # second way: create response-object(his type must be equal type of response in func process) (not working)

            db_bind.reparse_by_id(session, id, url)
            print(id)
        except IOError as e:
            print("error", e)
