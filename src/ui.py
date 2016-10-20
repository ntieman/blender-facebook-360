import bpy
from bpy.props import BoolProperty, StringProperty
from xmp import XMP


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
        box.operator(UI.AddPanoramaXMP.bl_idname, text=UI.AddPanoramaXMP.bl_label)

    @staticmethod
    def register():
        bpy.types.Scene.facebook_360_enabled = BoolProperty(
            name='Format for Facebook 360',
            default=True,
            description='')

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

        bpy.types.RENDER_PT_render.append(UI.facebook_360_UI)

        bpy.app.handlers.scene_update_post.append(UI.update_settings)

    @staticmethod
    def unregister():
        del bpy.types.Scene.facebook_360_enabled
        del bpy.types.Scene.facebook_360_enforce_aspect_ratio
        del bpy.types.Scene.facebook_360_enforce_bounds
        del bpy.types.Scene.facebook_360_enforce_camera

        bpy.utils.unregister_class(UI.AddPanoramaXMP)

        bpy.types.RENDER_PT_render.remove(UI.facebook_360_UI)

        bpy.app.handlers.scene_update_post.remove(UI.update_settings)
