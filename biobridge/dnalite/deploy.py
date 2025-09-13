from flask import Flask, request, jsonify, abort
from biobridge.dnalite.sqld import SQLDNAEncoder


def create_app():
    app = Flask(__name__)
    encoder = SQLDNAEncoder()  # Initialize the encoder with the default database

    @app.route('/store', methods=['POST'])
    def store_data():
        if not request.json or 'data_name' not in request.json or 'data' not in request.json:
            abort(400, 'Missing required fields: data_name and data')

        data_name = request.json['data_name']
        data = request.json['data']

        try:
            encoder.store_data(data_name, data)
            return jsonify({'message': 'Data stored successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/retrieve/<data_name>', methods=['GET'])
    def retrieve_data(data_name):
        try:
            data = encoder.retrieve_data(data_name)
            if data is None:
                return jsonify({'message': 'Data not found'}), 404
            return jsonify(data), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/list', methods=['GET'])
    def list_stored_data():
        try:
            data_names = encoder.list_stored_data()
            return jsonify(data_names), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/delete/<data_name>', methods=['DELETE'])
    def delete_data(data_name):
        try:
            encoder.delete_data(data_name)
            return jsonify({'message': 'Data deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/copy', methods=['POST'])
    def copy():
        if not request.json or 'db_name' not in request.json:
            abort(400, 'Missing required field: db_name')

        new_db_name = request.json['db_name']
        try:
            encoder.copy(new_db_name)
            return jsonify({'message': f'Database copied to {new_db_name}'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
