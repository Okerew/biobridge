import unittest
from unittest.mock import MagicMock, patch
from biobridge.genes.dna import DNA
from biobridge.control.opcua.crispr import OpcuaCRISPR
from opcua import Server


class TestOpcuaCRISPR(unittest.TestCase):
    @patch('opcua.Client')
    def test_execute_edit(self, mock_client):
        # Create a mock OPC UA server
        server = Server()
        server.set_endpoint("opc.tcp://127.0.0.1:4840")
        server.start()

        # Setup mock OPC UA server responses
        mock_node = MagicMock()
        mock_node.get_value.return_value = 'OK'
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_node.return_value = mock_node

        # Create DNA and OpcuaCRISPR instance
        dna = DNA("ATGCTAGCTAGCTAGCTAGCTAGCTA")
        crispr = OpcuaCRISPR(guide_rna="TAGC", ip_address="127.0.0.1", port=4840)

        # Connect to the mock CRISPR kit
        crispr.connect()

        # Perform an insert edit
        edited_dna = crispr.execute_edit(dna, 'insert', 'GTC', occurrence=3)

        print(edited_dna)

        # Test disconnection
        crispr.disconnect()

        # Stop the mock OPC UA server
        server.stop()


if __name__ == '__main__':
    unittest.main()
