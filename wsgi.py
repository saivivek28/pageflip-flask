from pageflip_app import create_app

application = create_app()

# For gunicorn: gunicorn wsgi:application
