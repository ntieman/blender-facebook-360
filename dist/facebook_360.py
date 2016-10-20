#xmp.py
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

#ui.py
import bpy
from bpy.props import BoolProperty, StringProperty


class UI:
    MAX_WIDTH = 6000
    MAX_HEIGHT = 3000

    ASPECT_RATIO_X = 2
    ASPECT_RATIO_Y = 1
    ASPECT_RATIO = ASPECT_RATIO_X / ASPECT_RATIO_Y

    CAMERA_TYPE = 'PANO'
    CAMERA_PANORAMA_TYPE = 'EQUIRECTANGULAR'

    old_resolution_x = 0
    old_resolution_y = 0

    class AddPanoramaXMP(bpy.types.Operator):
        """Adds panorama XMP to an existing file"""
        bl_idname = "export.add_xmp"
        bl_label = "Add Panorama XMP"

        filepath = bpy.props.StringProperty(subtype="FILE_PATH")

        def execute(self, context):
            if self.filepath:
                XMP.add_panorama_xmp(self.filepath)

            return {'FINISHED'}

        def invoke(self, context, event):
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}

    class UpdateSettings(bpy.types.Operator):
        """Update Facebook 360 settings to match constraints"""
        bl_idname = "export.update_facebook_settings"
        bl_label = "Update Settings"

        def execute(self, context):
            context.scene.facebook_360_enabled = True
            UI.update_settings(context.scene)
            context.scene.facebook_360_enabled = False
            return {'FINISHED'}

        def invoke(self, context, event):
            return self.execute(context)

    def __init__(self):
        pass

    @staticmethod
    def update_settings(scene):
        if UI.old_resolution_x == 0:
            UI.old_resolution_x = scene.render.resolution_x

        if UI.old_resolution_y == 0:
            UI.old_resolution_y = scene.render.resolution_y

        if scene.facebook_360_enabled:
            if scene.facebook_360_enforce_bounds:
                if scene.render.resolution_x > UI.MAX_WIDTH:
                    scene.render.resolution_x = UI.MAX_WIDTH

                if scene.render.resolution_y > UI.MAX_HEIGHT:
                    scene.render.resolution_y = UI.MAX_HEIGHT

            if scene.facebook_360_enforce_aspect_ratio:
                if scene.render.resolution_x / scene.render.resolution_y != UI.ASPECT_RATIO:
                    if UI.old_resolution_y != scene.render.resolution_y:
                        scene.render.resolution_x = scene.render.resolution_y * UI.ASPECT_RATIO
                    else:
                        scene.render.resolution_y = scene.render.resolution_x / UI.ASPECT_RATIO

                    if scene.facebook_360_enforce_bounds:
                        if scene.render.resolution_x > UI.MAX_WIDTH or scene.render.resolution_y > UI.MAX_HEIGHT:
                            scene.render.resolution_x = UI.MAX_WIDTH
                            scene.render.resolution_y = UI.MAX_HEIGHT

            if scene.facebook_360_enforce_camera:
                for camera in bpy.data.cameras:
                    camera.type = UI.CAMERA_TYPE
                    camera.cycles.panorama_type = UI.CAMERA_PANORAMA_TYPE

        old_resolution_x = scene.render.resolution_x
        old_resolution_y = scene.render.resolution_y

    @staticmethod
    def facebook_360_UI(self, context):
        self.layout.operator_context = 'INVOKE_DEFAULT'

        layout = self.layout

        box = layout.box()

        box.prop(context.scene, 'facebook_360_enabled', toggle=False)
        box.prop(context.scene, 'facebook_360_enforce_aspect_ratio', toggle=False)
        box.prop(context.scene, 'facebook_360_enforce_bounds', toggle=False)
        box.prop(context.scene, 'facebook_360_enforce_camera', toggle=False)
        box.operator(UI.UpdateSettings.bl_idname, text=UI.UpdateSettings.bl_label)
        box.operator(UI.AddPanoramaXMP.bl_idname, text=UI.AddPanoramaXMP.bl_label)

    @staticmethod
    def register():
        bpy.types.Scene.facebook_360_enabled = BoolProperty(
            name='Enforce Settings',
            default=True,
            description='Restrict setting choices to the options below')

        bpy.types.Scene.facebook_360_enforce_aspect_ratio = BoolProperty(
            name='Enforce Aspect',
            default=True,
            description='Facebook requires {}:{} aspect ratio for 360 images'.format(UI.ASPECT_RATIO_X, UI.ASPECT_RATIO_Y)
        )

        bpy.types.Scene.facebook_360_enforce_bounds = BoolProperty(
            name='Enforce Bounds',
            default=True,
            description='The maximum size for Facebook 360 images is {} x {}'.format(UI.MAX_WIDTH, UI.MAX_HEIGHT)
        )

        bpy.types.Scene.facebook_360_enforce_camera = BoolProperty(
            name='Enforce Camera',
            default=True,
            description='Facebook needs equirectangular rendering to display properly'
        )

        bpy.utils.register_class(UI.AddPanoramaXMP)
        bpy.utils.register_class(UI.UpdateSettings)

        bpy.types.RENDER_PT_render.append(UI.facebook_360_UI)

        bpy.app.handlers.scene_update_post.append(UI.update_settings)

    @staticmethod
    def unregister():
        del bpy.types.Scene.facebook_360_enabled
        del bpy.types.Scene.facebook_360_enforce_aspect_ratio
        del bpy.types.Scene.facebook_360_enforce_bounds
        del bpy.types.Scene.facebook_360_enforce_camera

        bpy.utils.unregister_class(UI.AddPanoramaXMP)
        bpy.utils.unregister_class(UI.UpdateSettings)

        bpy.types.RENDER_PT_render.remove(UI.facebook_360_UI)

        bpy.app.handlers.scene_update_post.remove(UI.update_settings)

#__init__.py

bl_info = {
    "name": "Facebook 360",
    "author": "Nicholas Tieman",
    "version": (0, 0, 2),
    "blender": (2, 78, 0),
    "location": "Rendertab -> Render Panel",
    "description": "Render images ready for Facebook 360.",
    "category": "Render",
    "support": "TESTING"
    }


def register():
    UI.register()


def unregister():
    UI.unregister()


if __name__ == "__main__":
    register()

