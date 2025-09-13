import unittest
from unittest.mock import MagicMock, patch

from biobridge.control.usb.crispr import UsbCRISPR
from biobridge.genes.dna import DNA


class TestUsbCRISPR(unittest.TestCase):
    @patch("usb.core.find")
    @patch("usb.util.find_descriptor")
    def test_execute_edit(self, mock_find_descriptor, mock_find):
        # Setup mock USB device responses
        mock_device = MagicMock()
        mock_endpoint_out = MagicMock()
        mock_endpoint_in = MagicMock()
        mock_endpoint_in.read.return_value = b"OK"
        mock_find.return_value = mock_device
        mock_find_descriptor.side_effect = [mock_endpoint_out, mock_endpoint_in]

        # Create DNA and UsbCRISPR instance
        dna = DNA("ATGCTAGCTAGCTAGCTAGCTAGCTA")
        crispr = UsbCRISPR(
            guide_rna="TAGC", usb_vendor_id=0x1234, usb_product_id=0x5678
        )

        # Connect to the mock CRISPR kit
        crispr.connect()

        # Perform an insert edit
        edited_dna = crispr.execute_edit(dna, "insert", "GTC", occurrence=3)

        print(edited_dna)

        # Verify the USB requests were sent correctly
        mock_find.assert_called_with(idVendor=0x1234, idProduct=0x5678)

        # Test disconnection
        crispr.disconnect()


if __name__ == "__main__":
    unittest.main()
