import unittest
from unittest.mock import Mock, patch
from connector import Connector
import connector


class TestApp(unittest.TestCase):

    def setUp(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    mocked_table.return_value.columns = [
                        "Table", 'name', 'somethingelse']
                    self.inst = Connector(
                        'somedb', 'sometable', 'someesindex', 'somedb_type')

    def test_connector_instance_creation(self):
        self.assertEqual(self.inst.elastic_index, 'someesindex')
        self.assertEqual(self.inst.elastic_doc_type, 'somedb_type')

    def test_connector_instance_creation_with_wrong_table_name_negative(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector(
                            'somedb', 3, 'someesindex', 'somedb_type')
        self.assertEqual(raised_exception.exception.args[0],
                         'table must be str')

    def test_connector_instance_creation_with_wrong_database_name_negative(
            self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector(
                            (1, 2, 3), 'sad', 'someesindex', 'somedb_type')
        self.assertEqual(raised_exception.exception.args[0],
                         'database must be str')

    def test_connector_instance_creation_with_wrong_elastic_index_negative(
            self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector('dsa', 'sad', 523, 'somedb_type')
        self.assertEqual(raised_exception.exception.args[0],
                         'elastic_index must be str')

    def test_connector_instance_creation_with_wrong_elastic_doc_type_negative(
            self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    with self.assertRaises(TypeError) as raised_exception:
                        inst = Connector("sad", 'sad', 'someesindex', 0000)
        self.assertEqual(raised_exception.exception.args[0],
                         'elastic_doc_type must be str')

    def test_connector_instance_creation_without_connection_to_database_wrong(
            self):
        with self.assertRaises(connector.DatabaseConnectionError) as raised_exception:
            inst = Connector("sad", 'sad', 'someesindex', 'sda')
        self.assertEqual(
            raised_exception.exception.args[0],
            'Connection to databes has failed')

    def test_connector_headers_property(self):
        self.assertEqual(self.inst.headers, ("Table", 'name', 'somethingelse'))

    def test_get_json_from_row(self):
        head = Mock()
        head.name = 'sad'
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    mocked_table.return_value.columns = [head]
                    inst = Connector("sad", 'sad', 'someesindex', 'sda')
        self.assertEqual(inst.get_json_from_row(['Table']), {'sad': 'Table',})




    def test_delete_index(self):
        with patch('connector.Connector.es.indices.delete') as mock_es:
            mock_es.return_value.indices.delete = 'sa'
            self.assertEqual(None, self.inst.delete_index())

    def test_delete_index_negative(self):
        mock = Mock(side_effect=connector.ElasticConnectionError)
        with self.assertRaises(connector.ElasticConnectionError) as raise_exception:
            with patch('connector.Connector.es') as mock_es:
                mock_es.return_value.indices.delete = mock()
                self.inst.delete_index()

    def test_primary_key(self):
        with patch('connector.create_engine') as mocked_engine:
            with patch('connector.MetaData') as mocked_metadata:
                with patch('connector.Table') as mocked_table:
                    mocked_table.return_value.primary_key.columns.values()[0].name = 'id'
                    inst = Connector('somedb', 'sometable', 'someesindex', 'somedb_type')
                    self.assertEqual(inst.primary_key, 'id')




if __name__ == '__main__':
    unittest.main()
