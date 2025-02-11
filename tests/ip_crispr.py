import unittest
from unittest.mock import patch
from biobridge.genes.dna import DNA
from biobridge.control.ip.crispr import IpCRISPR

class TestIpCRISPR(unittest.TestCase):
    @patch('requests.get')
    @patch('requests.post')
    def test_execute_edit(self, mock_post, mock_get):
        # Setup mock server responses
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'response': 'OK'}

        # Create DNA and IpCRISPR instance
        dna = DNA("ATGCTAGCTAGCTAGCTAGCTAGCTA")
        crispr = IpCRISPR(guide_rna="TAGC", ip_address="127.0.0.1", port=8080)

        # Connect to the mock CRISPR kit
        crispr.connect()

        # Perform an insert edit
        edited_dna = crispr.execute_edit(dna, 'insert', 'GTC', occurrence=3)

        print(edited_dna)

        # Verify the HTTP requests were sent correctly
        mock_get.assert_called_with('http://127.0.0.1:8080/connect', timeout=1)

        # Test disconnection
        crispr.disconnect()

if __name__ == '__main__':
    unittest.main()
