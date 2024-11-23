import sys
import bpy
import os

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in bpy.data.objects:
        bpy.data.objects.remove(block, do_unlink=True)

clean_scene()

# Obtener las rutas de los archivos de entrada, salida y textura
input_file = sys.argv[sys.argv.index("--") + 1]  # Ruta del archivo OBJ
output_file = sys.argv[sys.argv.index("--") + 2]  # Ruta de salida FBX
texture_file = sys.argv[sys.argv.index("--") + 3]  # Ruta de la textura (por ejemplo, .png)

# Importar el archivo OBJ
bpy.ops.import_scene.obj(filepath=input_file)

# Obtener el objeto importado (asumimos que es el primero)
obj = bpy.context.selected_objects[0]

# Aplicar transformaciones para asegurarnos de que las transformaciones sean permanentes
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Centrar el pivote en el centro del modelo 3D (usando el centro de la masa)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

# Posicionar el objeto en el origen (0, 0, 0)
obj.location = (0, 0, 0)

# Ajustar la escala para que sea 1, manteniendo la proporción
# Si la escala original es 100, ajustamos para que la escala sea 1 en lugar de 100
scale_factor = 1 / obj.scale[0]  # Usamos el valor de la escala en X (se asume uniforme)
obj.scale = (scale_factor, scale_factor, scale_factor)

# Aumentar la rotación en 60 grados sobre el eje X (convirtiendo a radianes)
obj.rotation_euler[0] += 155 * (3.14159 / 180)  # 60 grados convertidos a radianes

# Si la textura existe, asignarla al objeto importado
if os.path.exists(texture_file):
    print(f"Textura encontrada: {texture_file}")
    
    # Crear una nueva textura
    texture = bpy.data.textures.new("ImportedTexture", type='IMAGE')
    texture_file_absolute = os.path.abspath(texture_file).replace("\\", "/")
    texture.image = bpy.data.images.load(texture_file_absolute)

    # Crear un material
    material = bpy.data.materials.new(name="MaterialWithTexture")
    material.use_nodes = True

    # Crear un nodo de textura e integrarlo al material
    bsdf = material.node_tree.nodes["Principled BSDF"]
    tex_image_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
    tex_image_node.image = texture.image
    material.node_tree.links.new(bsdf.inputs['Base Color'], tex_image_node.outputs['Color'])

    # Asignar el material al objeto
    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)

else:
    print(f"No se encontró la textura: {texture_file}")

# Exportar el archivo a FBX con texturas embebidas
bpy.ops.export_scene.fbx(
    filepath=output_file,
    use_selection=True,  # Solo exporta los objetos seleccionados
    embed_textures=True,  # Embeder las texturas en el archivo FBX
    path_mode='COPY'
)

print("Conversión completa: {} -> {}".format(input_file, output_file))