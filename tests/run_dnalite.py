from biobridge.dnalite.deploy import create_app
import os


def main():
    port = int(os.getenv('FLASK_PORT', 5000))
    app = create_app()
    app.run(port=port, debug=True)


if __name__ == '__main__':
    main()
