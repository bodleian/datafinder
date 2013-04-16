
from rdflib import URIRef
from rdflib.plugin import register
try: # These moved during the transition from rdflib 2.4 to rdflib 3.0.
    from rdflib.plugins.serializers.rdfxml import PrettyXMLSerializer  # 3.0
    from rdflib.serializer import Serializer
except ImportError:
    from rdflib.syntax.serializers.PrettyXMLSerializer import PrettyXMLSerializer  # 2.4
    from rdflib.syntax.serializers import Serializer

class BetterPrettyXMLSerializer(PrettyXMLSerializer):
    def relativize(self, uri):
        base = URIRef(self.base)
        basedir = URIRef(self.base if base.endswith('/') else base.rsplit('/', 1)[0])
        if base is not None:
            if uri == base:
                uri = URIRef('')
            elif uri == basedir:
                uri = URIRef('.')
            elif uri.startswith(basedir + '/'):
                uri = URIRef(uri.replace(basedir + '/', "", 1))
        return uri
    
register('better-pretty-xml', Serializer, __name__, 'BetterPrettyXMLSerializer')
    
