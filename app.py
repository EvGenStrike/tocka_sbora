import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

if __name__ == '__main__':
    file_name = default_storage.save('test_file.txt', ContentFile(b'Hello Yandex!'))
    print(default_storage.url(file_name))
    print(default_storage.__class__)

    # app.run(debug=True)
