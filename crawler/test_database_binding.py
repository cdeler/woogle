import unittest
from database_binding import init_db, insert, update, read, reparse_by_id, delete


class TestDatabaseBinding(unittest.TestCase):

    def test_insert_and_read_options(self):
        session = init_db()
        columns = ('title', 'url', 'text')
        input_data = ('some title', 'some url', 'some text')
        input_row = {k: v for k, v in zip(columns, input_data)}
        insert(session, **input_row)
        output_data = read(session, title='some title')
        self.assertEqual(input_data, output_data)

    def test_update(self):
        session = init_db()
        id = 5
        columns = ('id', 'title', 'url', 'text')
        old_data = (id, 'old title', 'old url', 'old text')
        new_data = (id, 'new title', 'new url', 'new text')
        old_row = {k: v for k, v in zip(columns, old_data)}
        insert(session, **old_row)
        new_row = {k: v for k, v in zip(columns, new_data)}
        update(session, **new_row)
        self.assertEqual(read(session, id=id), new_data[1:])
        delete(session, id=id)

    def test_reparse(self):
        session = init_db()
        columns = ('title', 'url', 'text')
        id = 345
        relevant_info = read(session, id=id)
        irrelevant_info = (
            'irrevelant title',
            relevant_info[1],
            relevant_info[2])
        input_row = {k: v for k, v in zip(columns, irrelevant_info)}
        update(session, id=id, **input_row)
        reparse_by_id(session, id=id)
        self.assertEqual(read(session, id=id), relevant_info)

    def test_delete(self):
        session = init_db()
        columns = ('title', 'url', 'text')
        input_data = ('some title', 'some url', 'some text')
        input_row = {k: v for k, v in zip(columns, input_data)}
        id = 501
        insert(session, id=id, **input_row)
        delete(session, id=id)
        self.assertEqual(None, read(session, id=id))


if __name__ == '__main__':
    unittest.main()
