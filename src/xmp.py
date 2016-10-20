from xml.dom import minidom
from xml.parsers.expat import ExpatError


class XMP:
    MARKER_SOI = b'\xff\xd8'
    MARKER_EOI = b'\xff\xd9'
    MARKER_SOS = b'\xff\xda'
    MARKER_APP1 = b'\xff\xe1'

    XMP_IDENTIFIER = b'http://ns.adobe.com/xap/1.0/\x00'
    XMP_PACKET_BEGIN = b'<?xpacket begin="w" id="W5M0MpCehiHzreSzNTczkc9d"?>'
    XMP_PACKET_END = b'<?xpacket end="w"?>'

    def __init__(self):
        pass

    @staticmethod
    def decode_tag_size(size_bytes):
        if size_bytes and len(size_bytes):
            return int.from_bytes(size_bytes, byteorder='big')
        else:
            return 0

    @staticmethod
    def encode_tag_size(size):
        return size.to_bytes(2, byteorder='big')

    @staticmethod
    def get_xmp(file_name):
        with open(file_name, 'rb') as f:
            f.seek(2)
            marker = f.read(2)

            while marker and marker != XMP.MARKER_SOS and marker != XMP.MARKER_EOI:
                size = XMP.decode_tag_size(f.read(2))

                if marker == XMP.MARKER_APP1:
                    content = f.read(size - 2)

                    if content[0:len(XMP.XMP_IDENTIFIER)] == XMP.XMP_IDENTIFIER:
                        return content
                elif size > 2:
                    f.seek(size - 2, 1)

                marker = f.read(2)
            return ''

    @staticmethod
    def set_xmp(file_name, xmp):
        with open(file_name, 'rb') as f:
            f.seek(2)
            marker = f.read(2)
            xmp_start = 2
            xmp_length = 0

            while marker and marker != XMP.MARKER_SOS and marker != XMP.MARKER_EOI:
                size = XMP.decode_tag_size(f.read(2))

                if marker == XMP.MARKER_APP1:
                    content = f.read(size - 2)

                    if content[0:len(XMP.XMP_IDENTIFIER)] == XMP.XMP_IDENTIFIER:
                        xmp_length = size + 2
                        xmp_start = f.tell() - xmp_length

                        break
                elif size > 2:
                    f.seek(size - 2, 1)

                marker = f.read(2)

            f.seek(0)
            file_head = f.read(xmp_start)
            f.seek(xmp_length, 1)
            file_tail = f.read()

        with open(file_name, 'wb') as f:
            f.write(file_head)
            f.write(XMP.MARKER_APP1)
            f.write(XMP.encode_tag_size(len(xmp) + 2))
            f.write(xmp)
            f.write(file_tail)

    @staticmethod
    def xmp_to_minidom(xmp):
        if xmp[0:2] == XMP.MARKER_APP1:
            xmp = xmp[4:]

        xmp = xmp.replace(XMP.XMP_IDENTIFIER, b'')

        try:
            dom = minidom.parseString(xmp)
        except ExpatError:
            dom = minidom.Document()

        if len(dom.getElementsByTagName('x:xmpmeta')) == 0:
            node = dom.createElement('x:xmpmeta')
            node.setAttribute('xmlns:x', 'adobe:ns:meta')
            node.setAttribute('x:xmptk', 'Adobe XMP Core 5.6-c132 79.159284, 2016/04/19-13:13:40')
            dom.appendChild(node)

        if XMP.XMP_PACKET_BEGIN not in bytearray(dom.toxml(), 'utf8'):
            pi = dom.createProcessingInstruction('xpacket', 'begin="w" id="W5M0MpCehiHzreSzNTczkc9d"')
            dom.insertBefore(pi, dom.getElementsByTagName('x:xmpmeta')[0])

        if XMP.XMP_PACKET_END not in bytearray(dom.toxml(), 'utf8'):
            pi = dom.createProcessingInstruction('xpacket', 'end="w"')
            dom.appendChild(pi)

        if len(dom.getElementsByTagName('x:xmpmeta')) == 0:
            node = dom.createElement('x:xmpmeta')
            node.setAttribute('xmlns:x', 'adobe:ns:meta')
            node.setAttribute('x:xmptk', 'Adobe XMP Core 5.6-c132 79.159284, 2016/04/19-13:13:40')
            dom.appendChild(node)

        if len(dom.getElementsByTagName('rdf:RDF')) == 0:
            node = dom.createElement('rdf:RDF')
            node.setAttribute('xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
            dom.getElementsByTagName('x:xmpmeta')[0].appendChild(node)

        if len(dom.getElementsByTagName('rdf:Description')) == 0:
            node = dom.createElement('rdf:Description')
            node.setAttribute('rdf:about', '')
            node.setAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
            node.setAttribute('xmlns:xmp', 'http://ns.adobe.com/xap/1.0/')
            node.setAttribute('dc:format', 'image/jpeg')
            dom.getElementsByTagName('rdf:RDF')[0].appendChild(node)

        return dom

    @staticmethod
    def minidom_to_xmp(dom):
        xml = bytearray(dom.toxml(), 'utf8')
        xml = xml.replace(b'<?xml version="1.0" ?>', b'')
        xml = xml.strip()

        return XMP.XMP_IDENTIFIER + xml

    @staticmethod
    def add_panorama_xmp(source_file_name, output_file_name=''):
        if output_file_name == '':
            output_file_name = source_file_name

        old_xmp_raw = XMP.get_xmp(source_file_name)
        xmp_dom = XMP.xmp_to_minidom(bytearray(old_xmp_raw, 'utf8'))
        description = xmp_dom.getElementsByTagName('rdf:Description')[0]

        if not description.hasAttribute('xmlns:GPano'):
            description.setAttribute('xmlns:GPano', 'http://ns.google.com/photos/1.0/panorama/')

        if len(xmp_dom.getElementsByTagName('GPano:ProjectionType')) == 0:
            node = xmp_dom.createElement('GPano:ProjectionType')
            node.appendChild(xmp_dom.createTextNode('equirectangular'))
            description.appendChild(node)

        XMP.set_xmp(output_file_name, XMP.minidom_to_xmp(xmp_dom))
