import time
import logging
from contextlib import suppress

from src import database_binding as db_bind


def start_download():
    time.sleep(2)
    id = int
    url = str
    session = db_bind.init_db()
    while True:
        try:
            res = db_bind.get_wait_url(session)
            if res:
                id=res[0]
                url=res[1]
                db_bind.reparse_by_id(session, id, url)
                logging.debug(f"{id}, {url}")
            # need to parse url and write parser-information into db
            # for write into database, methods "update_state_by_id" and "update_row_by_id"
            # first way: create instance of WikiSpider and take him url (not working)
            # second way: create response-object(his type must be equal type of response in func process) (not working)
        except (Exception, KeyboardInterrupt) as error:
            logging.error(f"error {error}")
            continue
