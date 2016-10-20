import os
import test
import shutil
import unittest
from xml.dom import minidom
from xmp import XMP


class XMPTestCase(unittest.TestCase):
    """Tests for `xmp.py`."""

    def test_decode_tag_size(self):
        """decode_tag_size - Read section size from byte pair"""
        self.assertEqual(XMP.decode_tag_size(b'\x00\xff'), 255)
        self.assertEqual(XMP.decode_tag_size(b'\xff\x00'), 65280)
        self.assertEqual(XMP.decode_tag_size(b'\x00\x00'), 0)
        self.assertEqual(XMP.decode_tag_size(b'\xab\xcd'), 43981)

    def test_encode_tag_size(self):
        """encode_tag_size - Convert section size to byte pair"""
        self.assertEqual(XMP.encode_tag_size(255), b'\x00\xff')
        self.assertEqual(XMP.encode_tag_size(65280), b'\xff\x00')
        self.assertEqual(XMP.encode_tag_size(0), b'\x00\x00')
        self.assertEqual(XMP.encode_tag_size(43981), b'\xab\xcd')

    def test_get_xmp(self):
        """get_xmp - Retrieve existing XMP data from file"""
        self.assertEqual(XMP.get_xmp(test.path('img/test-no-XMP.jpg')), '')
        self.assertTrue(len(XMP.get_xmp(test.path('img/test-XMP.jpg'))) > 0)

    def test_set_xmp(self):
        """set_xmp - Write XMP to file"""
        shutil.copy(test.path('img/test-no-XMP.jpg'), test.path('img/test-no-xmp-temp.jpg'))
        xmp_raw = XMP.get_xmp(test.path('img/test-XMP.jpg'))
        XMP.set_xmp(test.path('img/test-no-xmp-temp.jpg'), xmp_raw)
        self.assertTrue(len(XMP.get_xmp(test.path('img/test-no-xmp-temp.jpg'))) > 0)
        os.remove(test.path('img/test-no-xmp-temp.jpg'))

        shutil.copy(test.path('img/test-XMP.jpg'), test.path('img/test-xmp-temp.jpg'))
        self.assertTrue(len(XMP.get_xmp(test.path('img/test-xmp-temp.jpg'))) > 0)
        XMP.set_xmp(test.path('img/test-xmp-temp.jpg'), XMP.XMP_IDENTIFIER)
        self.assertTrue(XMP.get_xmp(test.path('img/test-xmp-temp.jpg')) == XMP.XMP_IDENTIFIER)
        os.remove(test.path('img/test-xmp-temp.jpg'))

    def test_xmp_to_minidom(self):
        """xmp_to_minidom - Convert raw XMP data to minidom object"""
        xmp_raw = XMP.get_xmp(test.path('img/test-XMP.jpg'))
        xmp_minidom = XMP.xmp_to_minidom(xmp_raw)
        self.assertIsInstance(xmp_minidom, minidom.Document)

        xmp_minidom = XMP.xmp_to_minidom(b'')
        self.assertIsInstance(xmp_minidom, minidom.Document)

    def test_minidom_to_xmp(self):
        """minidom_to_xmp - Convert minidom object into raw XMP data"""
        xmp_raw = XMP.get_xmp(test.path('img/test-XMP.jpg'))
        xmp_minidom = XMP.xmp_to_minidom(xmp_raw)
        xmp_raw = XMP.minidom_to_xmp(xmp_minidom)
        self.assertTrue(XMP.XMP_IDENTIFIER in xmp_raw)
        self.assertTrue(XMP.XMP_PACKET_BEGIN in xmp_raw)
        self.assertTrue(XMP.XMP_PACKET_END in xmp_raw)

        xmp_minidom = XMP.xmp_to_minidom(b'')
        xmp_raw = XMP.minidom_to_xmp(xmp_minidom)
        self.assertTrue(XMP.XMP_IDENTIFIER in xmp_raw)
        self.assertTrue(XMP.XMP_PACKET_BEGIN in xmp_raw)
        self.assertTrue(XMP.XMP_PACKET_END in xmp_raw)

    def test_add_panorama_xmp(self):
        """add_panorama_xmp - Add panorama marker to file XMP"""
        shutil.copy(test.path('img/test-no-XMP.jpg'), test.path('img/test-no-xmp-temp.jpg'))
        XMP.add_panorama_xmp(test.path('img/test-no-xmp-temp.jpg'))
        self.assertTrue(b'GPano' in XMP.get_xmp(test.path('img/test-no-xmp-temp.jpg')))
        os.remove(test.path('img/test-no-xmp-temp.jpg'))

if __name__ == '__main__':
    unittest.main()