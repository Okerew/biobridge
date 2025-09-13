import sqlite3
import json
import uuid
import base64
from contextlib import closing
from biobridge.genes.dna import DNA
from biobridge.control.serial.sequencer import SerialDNASequencer
from biobridge.control.serial.crispr import SerialCRISPR
from biobridge.control.ip.sequencer import IpDNASequencer
from biobridge.control.ip.crispr import IpCRISPR
from biobridge.control.opcua.sequencer import DNASequencerOpcua
from biobridge.control.opcua.crispr import OpcuaCRISPR
from biobridge.control.usb.sequencer import UsbDNASequencer
from biobridge.control.usb.crispr import UsbCRISPR


class SQLDNAEncoder:
    def __init__(self, db_name='dna_database.db'):
        self.db_name = db_name
        self.conn = self._connect()
        self.cursor = self.conn.cursor()
        self.create_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        with closing(self._connect()) as conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS dna_data (
                id INTEGER PRIMARY KEY,
                data_name TEXT UNIQUE,
                dna_sequence TEXT,
                unique_key TEXT UNIQUE
            )
            ''')
            conn.commit()

    def _text_to_base64(self, text):
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    def _base64_to_text(self, base64_data):
        return base64.b64decode(base64_data.encode('utf-8')).decode('utf-8')

    def generate_unique_key(self):
        return str(uuid.uuid4())

    def store_data(self, data_name, data):
        unique_key = self.generate_unique_key()
        json_data = json.dumps(data)
        base64_data = self._text_to_base64(json_data)

        key_base64 = self._text_to_base64(unique_key)
        full_base64 = key_base64 + base64_data

        dna = DNA('')
        dna_sequence = dna.encode_8bit(full_base64)

        with closing(self._connect()) as conn:
            conn.execute('''
            INSERT OR REPLACE INTO dna_data (data_name, dna_sequence, unique_key)
            VALUES (?, ?, ?)
            ''', (data_name, dna_sequence, unique_key))
            conn.commit()

    def retrieve_data(self, data_name):
        with closing(self._connect()) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT dna_sequence, unique_key FROM dna_data WHERE data_name = ?',
                               (data_name,)).fetchone()

        if row:
            dna_sequence, stored_key = row['dna_sequence'], row['unique_key']
            dna = DNA(dna_sequence)
            full_base64 = dna.decode_8bit(dna)

            key_length = len(self._text_to_base64(stored_key))
            key_base64 = full_base64[:key_length]
            data_base64 = full_base64[key_length:]

            decoded_key = self._base64_to_text(key_base64)
            if decoded_key != stored_key:
                raise ValueError("Data integrity check failed: Unique key mismatch")

            json_data = self._base64_to_text(data_base64)
            return json.loads(json_data)
        return None

    def retrieve_dna(self, data_name):
        with closing(self._connect()) as conn:
            row = conn.execute('SELECT dna_sequence FROM dna_data WHERE data_name = ?',
                               (data_name,)).fetchone()

        if row:
            return row['dna_sequence']
        return None

    def list_stored_data(self):
        with closing(self._connect()) as conn:
            return [row['data_name'] for row in conn.execute('SELECT data_name FROM dna_data')]

    def delete_data(self, data_name):
        with closing(self._connect()) as conn:
            conn.execute('DELETE FROM dna_data WHERE data_name = ?', (data_name,))
            conn.commit()

    def close(self):
        # The context manager takes care of closing the connection.
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def copy(self, new_db_name):
        """
        Copies the SQLDNAEncoder to a new SQLite database file.

        Args:
            new_db_name (str): The path to the new SQLite database file.
        """
        # Close the current connection if open
        self.close()

        # Copy the current database to the new one
        with closing(sqlite3.connect(self.db_name)) as old_conn:
            with closing(sqlite3.connect(new_db_name)) as new_conn:
                old_conn.backup(new_conn)

        # Update the instance to use the new database
        self.db_name = new_db_name
        self.conn = self._connect()
        self.cursor = self.conn.cursor()
        print(f"Copied to new database: {new_db_name}")

    def serial_insert_dna_data(self, data_name, dna: DNA, port, baudrate, timeout, guide_rna, occurrence: int = 1):
        """
        Insert new DNA data using CRISPR.

        :param data_name: The name of the data to insert.
        :param dna: The DNA object to insert.
        :param occurrence: The occurrence number of the guide RNA where the edit should take place (1-based index).
        """
        serial_crispr = SerialCRISPR(guide_rna=guide_rna, port=port, baudrate=baudrate, timeout=timeout)
        try:
            serial_crispr.connect()
            new_dna = serial_crispr.execute_edit(dna, 'insert', dna.strand1, occurrence=occurrence)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            serial_crispr.disconnect()

    def serial_delete_dna_data(self, data_name, port, baudrate, timeout, guide_rna, occurrence: int = 1):
        """
        Delete DNA data using CRISPR.

        :param data_name: The name of the data to delete.
        :param occurrence: The occurrence number of the guide RNA where the edit should take place (1-based index).
        """
        serial_crispr = SerialCRISPR(guide_rna=guide_rna, port=port, baudrate=baudrate, timeout=timeout)
        try:
            serial_crispr.connect()
            dna = self.retrieve_dna(data_name)
            print(dna)
            new_dna = serial_crispr.execute_edit(DNA(dna), 'delete', len(dna), occurrence=occurrence)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            serial_crispr.disconnect()

    def serial_replace_dna_data(self, data_name, new_dna: DNA, port, baudrate, timeout, guide_rna, occurrence: int = 1):
        """
        Replace DNA data using CRISPR.

        :param data_name: The name of the data to replace.
        :param new_dna: The new DNA object to replace the existing one.
        :param occurrence: The occurrence number of the guide RNA where the edit should take place (1-based index).
        """
        serial_crispr = SerialCRISPR(guide_rna=guide_rna, port=port, baudrate=baudrate, timeout=timeout)
        try:
            serial_crispr.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = serial_crispr.execute_edit(dna, 'replace', new_dna.strand1, occurrence=occurrence)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            serial_crispr.disconnect()

    def serial_analyze_dna_data(self, data_name, port):
        """
        Analyze the DNA data using the SerialDNASequencer.

        :param data_name: The name of the data to analyze.
        """
        dna = self.retrieve_data(data_name)
        sequencer = SerialDNASequencer(port=port)
        try:
            sequencer.connect()
            sequencer.analyze_sequence(DNA(dna))
        finally:
            sequencer.disconnect()

    def ip_analyze_dna_data(self, data_name, ip_address):
        """
        Analyze the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to analyze.
        """
        dna = self.retrieve_data(data_name)
        sequencer = IpDNASequencer(ip_address)
        try:
            sequencer.connect()
            sequencer.analyze_sequence(DNA(dna))
        finally:
            sequencer.disconnect()

    def ip_replace_dna_data(self, data_name, new_dna: DNA, ip_address, guide_rna):
        """
        Replace the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to replace.
        :param new_dna: The new DNA object to replace the existing one.
        """
        sequencer = IpCRISPR(guide_rna, ip_address)
        try:
            sequencer.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = sequencer.execute_edit(DNA(dna), 'replace', new_dna.strand1)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def ip_delete_dna_data(self, data_name, ip_address, guide_rna):
        """
        Delete the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to delete.
        """
        sequencer = IpCRISPR(guide_rna, ip_address)
        try:
            sequencer.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = sequencer.execute_edit(DNA(dna), 'delete', len(dna))
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def ip_insert_dna_data(self, data_name, new_dna: DNA, ip_address, guide_rna):
        """
        Insert the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to insert.
        :param new_dna: The new DNA object to insert.
        """
        sequencer = IpCRISPR(guide_rna, ip_address)
        try:
            sequencer.connect()
            new_dna = sequencer.execute_edit(DNA(new_dna), 'insert', new_dna.strand1)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def opcua_analyze_dna_data(self, data_name, ip_address):
        """
        Analyze the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to analyze.
        """
        dna = self.retrieve_data(data_name)
        sequencer = (DNASequencerOpcua(ip_address))
        try:
            sequencer.connect()
            sequencer.analyze_sequence(DNA(dna))
        finally:
            sequencer.disconnect()

    def opcua_replace_dna_data(self, data_name, new_dna: DNA, ip_address, guide_rna):
        """
        Replace the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to replace.
        :param new_dna: The new DNA object to replace the existing one.
        """
        sequencer = (OpcuaCRISPR(ip_address, guide_rna))
        try:
            sequencer.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = sequencer.execute_edit(DNA(dna), 'replace', new_dna.strand1)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def opcua_delete_dna_data(self, data_name, ip_address, guide_rna):
        """
        Delete the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to delete.
        """
        sequencer = (OpcuaCRISPR(ip_address, guide_rna))
        try:
            sequencer.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = sequencer.execute_edit(DNA(dna), 'delete', len(dna))
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def opcua_insert_dna_data(self, data_name, new_dna: DNA, ip_address, guide_rna):
        """
        Insert the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to insert.
        :param new_dna: The new DNA object to insert.
        """
        sequencer = (OpcuaCRISPR(ip_address, guide_rna))
        try:
            sequencer.connect()
            new_dna = sequencer.execute_edit(DNA(new_dna), 'insert', new_dna.strand1)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def usb_analyze_dna_data(self, data_name, product_id, vendor_id):
        """
        Analyze the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to analyze.
        """
        dna = self.retrieve_data(data_name)
        sequencer = (UsbDNASequencer(usb_product_id=product_id, usb_vendor_id=vendor_id))
        try:
            sequencer.connect()
            sequencer.analyze_sequence(DNA(dna))
        finally:
            sequencer.disconnect()

    def usb_replace_dna_data(self, data_name, new_dna: DNA, product_id, vendor_id, guide_rna):
        """
        Replace the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to replace.
        :param new_dna: The new DNA object to replace the existing one.
        """
        sequencer = (UsbCRISPR(usb_product_id=product_id, usb_vendor_id=vendor_id, guide_rna=guide_rna))
        try:
            sequencer.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = sequencer.execute_edit(DNA(dna), 'replace', new_dna.strand1)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def usb_delete_dna_data(self, data_name, product_id, vendor_id, guide_rna):
        """
        Delete the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to delete.
        """
        sequencer = (UsbCRISPR(usb_product_id=product_id, usb_vendor_id=vendor_id, guide_rna=guide_rna))
        try:
            sequencer.connect()
            dna = self.retrieve_dna(data_name)
            new_dna = sequencer.execute_edit(DNA(dna), 'delete', len(dna))
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()

    def usb_insert_dna_data(self, data_name, new_dna: DNA, product_id, vendor_id, guide_rna):
        """
        Insert the DNA data using the IPDNASequencer.

        :param data_name: The name of the data to insert.
        :param new_dna: The new DNA object to insert.
        """
        sequencer = (UsbCRISPR(usb_product_id=product_id, usb_vendor_id=vendor_id, guide_rna=guide_rna))
        try:
            sequencer.connect()
            new_dna = sequencer.execute_edit(DNA(new_dna), 'insert', new_dna.strand1)
            self.store_data(data_name, new_dna.to_dict())
        finally:
            sequencer.disconnect()
