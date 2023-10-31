bl_info = {
    "name": "Remove Empty Vertex Groups",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy

class OBJECT_OT_remove_empty_vertex_groups(bpy.types.Operator):
    bl_idname = "object.remove_empty_vertex_groups"
    bl_label = "Remove Empty Vertex Groups"
    bl_description = "Remove all vertex groups with no weights assigned to any vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        to_remove = []

        def is_group_empty(vg):
            for v in obj.data.vertices:
                try:
                    if vg.weight(v.index) > 0:
                        return False
                except RuntimeError:
                    pass
            return True

        for vg in obj.vertex_groups:
            partner_name = None
            if vg.name.endswith(".L"):
                partner_name = vg.name[:-2] + ".R"
            elif vg.name.endswith(".R"):
                partner_name = vg.name[:-2] + ".L"
            elif vg.name.endswith("_L"):
                partner_name = vg.name[:-2] + "_R"
            elif vg.name.endswith("_R"):
                partner_name = vg.name[:-2] + "_L"

            if partner_name and obj.vertex_groups.get(partner_name):
                if is_group_empty(vg) and is_group_empty(obj.vertex_groups[partner_name]):
                    to_remove.append(vg.name)
                    to_remove.append(partner_name)
            else:
                if is_group_empty(vg):
                    to_remove.append(vg.name)

        to_remove = list(set(to_remove))  # Remove duplicates
        for vg_name in to_remove:
            obj.vertex_groups.remove(obj.vertex_groups[vg_name])

        self.report({'INFO'}, f"Removed {len(to_remove)} empty vertex groups")
        return {'FINISHED'}

def draw_func(self, context):
    layout = self.layout
    layout.operator(OBJECT_OT_remove_empty_vertex_groups.bl_idname)

class VIEW3D_PT_tools_remove_empty_vertex_groups(bpy.types.Panel):
    bl_label = "Remove Empty Vertex Groups"
    bl_idname = "OBJECT_PT_remove_empty_vertex_groups"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_context = 'objectmode'
    
    def draw(self, context):
        draw_func(self, context)

def register():
    bpy.utils.register_class(OBJECT_OT_remove_empty_vertex_groups)
    bpy.utils.register_class(VIEW3D_PT_tools_remove_empty_vertex_groups)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_remove_empty_vertex_groups)
    bpy.utils.unregister_class(VIEW3D_PT_tools_remove_empty_vertex_groups)

if __name__ == "__main__":
    register()
