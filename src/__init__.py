from ui import UI

bl_info = {
    "name": "Facebook 360",
    "author": "Nicholas Tieman",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "Rendertab -> Render Panel",
    "description": "Render images ready for Facebook 360.",
    "category": "Render"
    }


def register():
    UI.register()


def unregister():
    UI.unregister()


if __name__ == "__main__":
    register()
