import unittest
from unittest.mock import Mock, patch
from connector import Connector
import os
import connector

class TestApp(unittest.TestCase):

    def setUp(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    mocked_table.return_value.columns = ["Table", 'name', 'somethingelse']
                    self.inst = Connector('somedb', 'sometable', 'someesindex', 'somedb_type')

    def test_connector_instance_creation(self):
        self.assertEqual(self.inst.elastic_index, 'someesindex')
        self.assertEqual(self.inst.elastic_doc_type, 'somedb_type')

    def test_connector_instance_creation_with_wrong_table_name_negative(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector('somedb', 3, 'someesindex', 'somedb_type')
        self.assertEqual(raised_exception.exception.args[0],
                         'table must be str')

    def test_connector_instance_creation_with_wrong_database_name_negative(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector((1,2,3), 'sad', 'someesindex', 'somedb_type')
        self.assertEqual(raised_exception.exception.args[0],
                         'database must be str')

    def test_connector_instance_creation_with_wrong_elastic_index_negative(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector('dsa', 'sad', 523, 'somedb_type')
        self.assertEqual(raised_exception.exception.args[0],
                         'elastic_index must be str')

    def test_connector_instance_creation_with_wrong_elastic_doc_type_negative(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector("sad", 'sad', 'someesindex', 0000)
        self.assertEqual(raised_exception.exception.args[0],
                         'elastic_doc_type must be str')

    def test_connector_instance_creation_without_connection_to_database_wrong(self):
        with self.assertRaises(connector.DatabaseConnectionError) as raised_exception:
            inst = Connector("sad", 'sad', 'someesindex', 'sda')
        self.assertEqual(raised_exception.exception.args[0], 'Connection to databes has failed')

    def test_connector_headers_property(self):
        self.assertEqual(self.inst.headers, ("Table",'name','somethingelse'))

    def test_get_json_from_row(self):
        head = Mock()
        head.name = 'sad'
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    mocked_table.return_value.columns = [head]
                    inst = Connector("sad", 'sad', 'someesindex', 'sda')
        self.assertEqual(inst.get_json_from_row((2,['Table'])), {'sad': 'Table',})

    def test_get_json_from_row_with_wrong_row_negative(self):
        with self.assertRaises(TypeError) as raised_exc:
            self.inst.get_json_from_row(213)
        self.assertEqual(raised_exc.exception.args[0],'row must be tuple')


    def test_get_json_from_row_with_wrong_first_arg_negative(self):
        with self.assertRaises(TypeError) as raised_exc:
            self.inst.get_json_from_row(([],))
        self.assertEqual(raised_exc.exception.args[0],'first arg of row must be int')

    def test_get_json_from_row_with_negarive_firsta_argument(self):
        with self.assertRaises(ValueError) as raised_exc:
            self.inst.get_json_from_row((-213,))
        self.assertEqual(raised_exc.exception.args[0],'first value of row must be positive')

    def test_table_set(self):
        pass


    def test_privite_index(self):
        head = Mock()
        head.name = 'sad'
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    mocked_table.return_value.columns = [head]
                    inst = Connector("sad", 'sad', 'someesindex', 'sda')
                    with patch('connector.Connector.es.index') as mock_es:
                        mock_es.return_value.index = 'sa'
                        res = inst._index((2,['Table']))
        self.assertEqual(None, res)

    def test_privite_index_negative(self):
        with self.assertRaises(connector.ElasticConnectionError) as raised_exc:
            self.inst._index((2,'Table'))
        self.assertEqual(raised_exc.exception.args[0], 'Connection to elasticsearch has failed')


    def test_index_with_wrong_argument_negative(self):
        with self.assertRaises(TypeError) as raised_exception:
            self.inst.index('s')
        self.assertEqual(raised_exception.exception.args[0], 'threads must be int')

    def test_index_with_negative_threads_negative(self):
        with self.assertRaises(ValueError) as raised_exception:
            self.inst.index(-1)
        self.assertEqual(raised_exception.exception.args[0], 'threads must be positive')

    def test_index_with_zero_threads_negative(self):
        with self.assertRaises(ValueError) as raised_exception:
            self.inst.index(0)
        self.assertEqual(raised_exception.exception.args[0], 'number of threads must be more than 1')

    def test_delete_index(self):
        with patch('connector.Connector.es.indices.delete') as mock_es:
            mock_es.return_value.indices.delete = 'sa'
            self.assertEqual(None, self.inst.delete_index())

    def test_delete_index_negative(self):
        mock = Mock(side_effect=connector.ElasticConnectionError)
        with self.assertRaises(connector.ElasticConnectionError) as raise_exception:
            with patch('connector.Connector.es') as mock_es:
                mock_es.return_value.indices.delete= mock()
                self.inst.delete_index()

    @classmethod
    def tearDownClass(cls):
        os.remove('log.txt')


if __name__ == '__main__':
    unittest.main()