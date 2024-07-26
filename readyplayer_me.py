import bpy
import urllib.request
import urllib.parse
import os
import time

class ReadyPlayerDownloadOperator(bpy.types.Operator):
    bl_idname = "object.readyplayer_download_glb"
    bl_label = "Download and Import GLB"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        base_url = scene.readyplayer_url.strip()
        morph_targets = []
        pose = scene.readyplayer_pose.upper()  # Ensure pose is uppercase

        # Collect selected morph targets
        if scene.morph_target_arkit:
            morph_targets.append("ARKit")
        if scene.morph_target_oculus_visemes:
            morph_targets.append("Oculus Visemes")
        if scene.morph_target_mouth_smile:
            morph_targets.append("mouthSmile")
        if scene.morph_target_mouth_open:
            morph_targets.append("mouthOpen")

        # Construct the query parameters
        query_params = {}
        if morph_targets:
            query_params["morphTargets"] = ",".join(morph_targets)
        if pose:
            query_params["pose"] = pose

        # Encode the query parameters
        query_string = urllib.parse.urlencode(query_params)

        # Final URL with query parameters
        final_url = f"{base_url}?{query_string}"
        if not final_url:
            self.report({'ERROR'}, "URL is empty. Please enter a valid URL.")
            return {'CANCELLED'}

        filename = final_url.split("/")[-1].split("?")[0]
        filepath = os.path.join(bpy.path.abspath("//"), filename)

        try:
            self.report({'INFO'}, f"Starting download of {filename}")
            with urllib.request.urlopen(final_url) as response:
                total_size = int(response.info().get("Content-Length").strip())
                downloaded_size = 0
                chunk_size = 1024 * 1024  # 1 MB
                start_time = time.time()

                with open(filepath, 'wb') as out_file:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded_size += len(chunk)

                        # Calculate download progress
                        progress = downloaded_size / total_size
                        scene.download_progress = int(progress * 100)
                        elapsed_time = time.time() - start_time
                        self.report({'INFO'}, f"Downloaded {scene.download_progress}% ({downloaded_size / (1024 * 1024):.2f} MB / {total_size / (1024 * 1024):.2f} MB) in {elapsed_time:.2f} seconds")

            self.report({'INFO'}, f"GLB file downloaded to {filepath}")

            # Import the GLB file
            bpy.ops.import_scene.gltf(filepath=filepath)

        except Exception as e:
            self.report({'ERROR'}, f"Failed to download or import GLB file: {e}")

        return {'FINISHED'}

class ReadyPlayerPanel(bpy.types.Panel):
    bl_label = "Ready Player"
    bl_idname = "VIEW3D_PT_readyplayer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ready Player"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "readyplayer_url", text="GLB URL")

        layout.label(text="Pose Type:")
        layout.prop(scene, "readyplayer_pose", text="")

        layout.label(text="Morph Targets:")
        layout.prop(scene, "morph_target_arkit", text="ARKit")
        layout.prop(scene, "morph_target_oculus_visemes", text="Oculus Visemes")
        layout.prop(scene, "morph_target_mouth_smile", text="mouthSmile")
        layout.prop(scene, "morph_target_mouth_open", text="mouthOpen")

        layout.operator(ReadyPlayerDownloadOperator.bl_idname)
        
        layout.label(text="Download Progress:")
        layout.prop(scene, "download_progress", text="Progress")

def register():
    bpy.utils.register_class(ReadyPlayerDownloadOperator)
    bpy.utils.register_class(ReadyPlayerPanel)
    bpy.types.Scene.readyplayer_url = bpy.props.StringProperty(
        name="GLB URL",
        description="URL of the GLB file to download",
        default=""
    )
    bpy.types.Scene.readyplayer_pose = bpy.props.EnumProperty(
        name="Pose Type",
        description="Select the pose type for the avatar",
        items=[
            ('T', "T Pose", "Create an avatar in T-pose"),
            ('A', "A Pose", "Create an avatar in A-pose"),
        ],
        default='T'
    )
    bpy.types.Scene.morph_target_arkit = bpy.props.BoolProperty(
        name="ARKit",
        description="Include ARKit morph targets",
        default=False
    )
    bpy.types.Scene.morph_target_oculus_visemes = bpy.props.BoolProperty(
        name="Oculus Visemes",
        description="Include Oculus Visemes morph targets",
        default=False
    )
    bpy.types.Scene.morph_target_mouth_smile = bpy.props.BoolProperty(
        name="mouthSmile",
        description="Include mouthSmile morph target",
        default=False
    )
    bpy.types.Scene.morph_target_mouth_open = bpy.props.BoolProperty(
        name="mouthOpen",
        description="Include mouthOpen morph target",
        default=False
    )
    bpy.types.Scene.download_progress = bpy.props.IntProperty(
        name="Download Progress",
        description="Shows the download progress",
        default=0,
        min=0,
        max=100
    )

def unregister():
    bpy.utils.unregister_class(ReadyPlayerDownloadOperator)
    bpy.utils.unregister_class(ReadyPlayerPanel)
    del bpy.types.Scene.readyplayer_url
    del bpy.types.Scene.readyplayer_pose
    del bpy.types.Scene.morph_target_arkit
    del bpy.types.Scene.morph_target_oculus_visemes
    del bpy.types.Scene.morph_target_mouth_smile
    del bpy.types.Scene.morph_target_mouth_open
    del bpy.types.Scene.download_progress

if __name__ == "__main__":
    register()
