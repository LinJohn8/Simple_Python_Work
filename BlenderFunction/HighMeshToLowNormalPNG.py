import bpy


def bake_high_to_low(high_poly_obj, low_poly_obj):
    # 切换到Cycles渲染引擎
    bpy.context.scene.render.engine = 'CYCLES'

    # 确保所需的对象在场景中
    if high_poly_obj not in bpy.data.objects or low_poly_obj not in bpy.data.objects:
        print("指定的对象未找到")
        return

    high_poly = bpy.data.objects[high_poly_obj]
    low_poly = bpy.data.objects[low_poly_obj]

    # 选择低模
    bpy.context.view_layer.objects.active = low_poly
    low_poly.select_set(True)

    # 添加一个新的图像来存储烘焙结果
    bake_image = bpy.data.images.new("BakeImage", width=2048, height=2048, alpha=False)

    # 创建新的材质和纹理
    mat = bpy.data.materials.new(name="BakeMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # 清除默认节点
    for node in nodes:
        nodes.remove(node)

    # 添加所需的节点
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    tex_image = nodes.new(type='ShaderNodeTexImage')

    tex_image.image = bake_image
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])
    mat.node_tree.links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])

    # 将新材质赋给低模
    if low_poly.data.materials:
        low_poly.data.materials[0] = mat
    else:
        low_poly.data.materials.append(mat)

    # 配置烘焙设置
    bpy.context.scene.cycles.bake_type = 'NORMAL'
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.cage_extrusion = 0.1
    bpy.context.scene.render.bake.cage_object = high_poly

    # 选择高模
    high_poly.select_set(True)

    # 烘焙
    bpy.ops.object.bake(type='NORMAL')

    # 保存烘焙图像
    bake_image.filepath_raw = "YourPath"
    bake_image.file_format = 'PNG'
    bake_image.save()


# 使用对象名称调用函数
bake_high_to_low('monster1_high', 'monster1_low')