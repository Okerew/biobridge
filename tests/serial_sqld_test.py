import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from biobridge.genes.dna import DNA
from biobridge.dnalite.sqld import SQLDNAEncoder


class TestSQLDNAEncoder(unittest.TestCase):
    @patch('sqlite3.connect')
    @patch('biobridge.control.serial.crispr.SerialCRISPR.connect')
    @patch('biobridge.control.serial.crispr.SerialCRISPR.execute_edit')
    def test_insert_dna_data(self, mock_execute_edit, mock_crispr_connect, mock_connect):
        # Setup mock SQLite and CRISPR connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_crispr_connect.return_value = None
        mock_execute_edit.return_value = DNA('ATCG')

        # Create SQLDNAEncoder instance
        encoder = SQLDNAEncoder(db_name='test.db')

        # Insert new DNA data
        data_name = 'new_data'
        dna = DNA('ATGC')
        encoder.serial_insert_dna_data(data_name, dna, occurrence=2, baudrate=115200, timeout=0.1, guide_rna='TAGC', port='/dev/ttyUSB0')

        # Verify the CRISPR edit and data storage
        mock_crispr_connect.assert_called_once()
        mock_execute_edit.assert_called_with(dna, 'insert', dna.sequence, occurrence=2)

    @patch('sqlite3.connect')
    @patch('biobridge.control.serial.crispr.SerialCRISPR.connect')
    @patch('biobridge.control.serial.crispr.SerialCRISPR.execute_edit')
    def test_delete_dna_data(self, mock_execute_edit, mock_crispr_connect, mock_connect):
        # Setup mock SQLite and CRISPR connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_crispr = MagicMock()
        mock_crispr_connect.return_value = None
        mock_execute_edit.return_value = DNA('ATCG')

        # Create SQLDNAEncoder instance
        encoder = SQLDNAEncoder(db_name='test.db')

        # Delete DNA data
        data = {"name": "John Doe", "age": 30, "city": "New York"}
        data_name = 'test_data'
        encoder.store_data(data_name, data)
        encoder.serial_delete_dna_data(data_name, occurrence=3, baudrate=115200, timeout=0.1, guide_rna='TAGC',
                                       port='/dev/ttyUSB0')

        # Verify the CRISPR edit and data deletion
        mock_crispr_connect.assert_called_once()
        mock_crispr.disconnect()

    @patch('sqlite3.connect')
    @patch('biobridge.control.serial.crispr.SerialCRISPR.connect')
    @patch('biobridge.control.serial.crispr.SerialCRISPR.execute_edit')
    def test_replace_dna_data(self, mock_execute_edit, mock_crispr_connect, mock_connect):
        # Setup mock SQLite and CRISPR connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_crispr_connect.return_value = None
        mock_execute_edit.return_value = DNA('CGTA')
        mock_execute_edit.return_value = DNA('ATCG')

        # Create SQLDNAEncoder instance
        encoder = SQLDNAEncoder(db_name='test.db')

        # Replace DNA data
        data_name = 'test_data'
        new_dna = DNA('CGTA')
        encoder.serial_replace_dna_data(data_name, new_dna, occurrence=2, baudrate=115200, timeout=0.1, guide_rna='TAGC', port='/dev/ttyUSB0')

        # Verify the CRISPR edit and data replacement
        mock_crispr_connect.assert_called_once()
        mock_execute_edit.assert_called_with(mock.ANY, 'replace', new_dna.sequence, occurrence=2)

    @patch('sqlite3.connect')
    @patch('biobridge.control.serial.sequencer.SerialDNASequencer.connect')
    @patch('biobridge.control.serial.sequencer.SerialDNASequencer.analyze_sequence')
    @patch.object(SQLDNAEncoder, 'retrieve_data')  # Mock the retrieve_data method
    def test_analyze_dna_data(self, mock_analyze, mock_retrieve_data, mock_crispr_connect, mock_connect):
        # Setup mock SQLite and DNA Sequencer connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_crispr_connect.return_value = None
        mock_retrieve_data.return_value = 'ATCG'

        # Create SQLDNAEncoder instance
        encoder = SQLDNAEncoder(db_name='test.db')

        data_name = 'test_data'

        # Analyze DNA data
        encoder.serial_analyze_dna_data(data_name, port='/dev/ttyUSB1')


if __name__ == '__main__':
    unittest.main()
