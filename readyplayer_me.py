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
                with open(filepath, 'wb') as out_file:
                    out_file.write(response.read())

            self.report({'INFO'}, f"GLB file downloaded to {filepath}")

            # Import the GLB file
            bpy.ops.import_scene.gltf(filepath=filepath)

            # Adjust the pose if the selected pose is T-pose
            if pose == 'T':
                self.convert_to_t_pose(context)

        except Exception as e:
            self.report({'ERROR'}, f"Failed to download or import GLB file: {e}")

        return {'FINISHED'}

    def convert_to_t_pose(self, context):
        # Ensure that the imported armature is selected and active
        for obj in bpy.context.scene.objects:
            if obj.type == 'ARMATURE':
                armature = obj
                bpy.context.view_layer.objects.active = armature
                armature.select_set(True)
                break

        bpy.ops.object.mode_set(mode='POSE')
        shoulder_bones = ["upper_arm.L", "upper_arm.R"]

        for bone_name in shoulder_bones:
            bone = armature.pose.bones.get(bone_name)
            if bone:
                # Rotate the shoulder bones to convert to T-pose
                bone.rotation_mode = 'XYZ'
                bone.rotation_euler[0] = 0  # X-axis rotation
                bone.rotation_euler[1] = 0  # Y-axis rotation
                bone.rotation_euler[2] = 0  # Z-axis rotation

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "Converted armature to T-pose")

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

def unregister():
    bpy.utils.unregister_class(ReadyPlayerDownloadOperator)
    bpy.utils.unregister_class(ReadyPlayerPanel)
    del bpy.types.Scene.readyplayer_url
    del bpy.types.Scene.readyplayer_pose
    del bpy.types.Scene.morph_target_arkit
    del bpy.types.Scene.morph_target_oculus_visemes
    del bpy.types.Scene.morph_target_mouth_smile
    del bpy.types.Scene.morph_target_mouth_open

if __name__ == "__main__":
    register()
