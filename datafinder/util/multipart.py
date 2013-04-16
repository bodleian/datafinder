
import mimetools
import mimetypes

class MultiPartFormData(object):
    def __init__(self, fields=None, files=None):
        self._boundary = mimetools.choose_boundary()
        self._fields = fields or ()
        self._files = files or ()
        for file in self._files:
            file['mimetype'] = file.get('mimetype') or mimetypes.guess_type(file['filename'])[0] or 'application/octet-stream'
        self._body = self._body_iterator()
    
    @property
    def content_type(self):
        return 'multipart/form-data; boundary=%s' % self._boundary
    
    @property
    def content_length(self):
        field_padding = '--\r\nContent-Disposition: form-data; name=""\r\n\r\n\r\n'
        file_padding = '--\r\nContent-Disposition: form-data; name=""; filename=""\r\nContent-Type: \r\n\r\n'
        
        field_length = sum(sum(map(len, [self._boundary, field_padding, k, v])) for k,v in self._fields)
        file_length = sum(f['size'] + sum(map(len, [self._boundary, file_padding, f['name'], f['filename'], f['mimetype']])) for f in self._files)
        
        return field_length + file_length + len('----\r\n') + len(self._boundary)

    def _body_iterator(self):
        for (key, value) in self._fields:
            yield '--%s\r\n' % self._boundary
            yield 'Content-Disposition: form-data; name="%s"\r\n' % key
            yield '\r\n'
            if value:
                yield value
            yield '\r\n'
        for file in self._files:
            yield '--%s\r\n' % self._boundary
            yield 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (file['name'], file['filename'])
            yield 'Content-Type: %s\r\n' % file['mimetype']
            yield '\r\n'
            
            stream = file['stream']
            while True:
                data = stream.read(4096)
                if not data:
                    break
                yield data
        yield '--%s--\r\n' % self._boundary
    
    def read(self, blocksize):
        try:
            return self._body.next()
        except StopIteration:
            return ''
