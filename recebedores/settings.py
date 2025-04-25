SECRET_KEY = 'example'
DEBUG = True
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'pedidos',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'recebedores',
        'USER': 'recebedores',
        'PASSWORD': 'recebedores',
        'HOST': 'db',
        'PORT': '5432',
    }
}
ROOT_URLCONF = 'recebedores.urls'
WSGI_APPLICATION = 'recebedores.wsgi.application'
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_TASK_ROUTES = {
    'pedidos.tasks.processar_pedidos': {
        'queue': 'pedidos_recebedor',
    }
}