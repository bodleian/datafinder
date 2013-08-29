# ---------------------------------------------------------------------
#
# Copyright (c) 2012 University of Oxford
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, --INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ---------------------------------------------------------------------

from rdflib import Namespace

DCTERMS = Namespace('http://purl.org/dc/terms/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
OXDS = Namespace('http://vocab.ox.ac.uk/dataset/schema#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
HTML = Namespace('http://www.w3.org/1999/xhtml')
XHTML = Namespace('http://www.w3.org/1999/xhtml#')
FUND = Namespace('http://vocab.ox.ac.uk/projectfunding#')
BIBO =  Namespace("http://purl.org/ontology/bibo/")
GEO =  Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
namespaces = {}

for name, value in locals().items():
    if isinstance(value, Namespace):
        namespaces[name.lower()] = value

def bind_namespaces(graph):
    for prefix, uri in namespaces.iteritems():
        graph.bind(prefix, uri)
    
    return graph