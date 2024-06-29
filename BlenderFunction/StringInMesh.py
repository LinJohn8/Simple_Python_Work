import bpy
import gpu
import numpy as np
from mathutils import Color


def draw(self, context):
    if self.modal_redraw == True:

        # 获取当前绑定的帧缓冲区
        self.framebuffer = gpu.state.active_framebuffer_get()
        # 获取当前视口的信息
        self.viewport_info = gpu.state.viewport_get()
        self.width = self.viewport_info[2]
        self.height = self.viewport_info[3]
        # 获取视图像素
        self.pixelBuffer = self.framebuffer.read_color(0, 0, self.width, self.height, 3, 0, 'FLOAT')
        self.pixelBuffer.dimensions = self.width * self.height * 3
        # 处理
        array = np.array(self.pixelBuffer).reshape(self.height, self.width, 3)[::self.step * -2, ::self.step]
        # 将像素矩阵转化为字符串
        pixel_group = []
        for i in array:
            for j in i:
                pixel_group.append(self.Character_draw[int(min(Color(j).v, 1) * (len(self.Character_draw) - 1))])
            pixel_group.append("\n")

        self.framebuffer_texts.clear()
        self.framebuffer_texts.write("".join(pixel_group))
        self.modal_redraw = False


class TextCharacterDrawing(bpy.types.Operator):
    bl_idname = "view3d.text_character_drawing"
    bl_label = "Draw 3D View Framebuffer"

    def __init__(self):
        print("启动")

        self.width = 32
        self.height = 32
        self.modal_redraw = False
        self.text_name = "Generated Text"
        self.framebuffer = None
        self.viewport_info = None
        self.pixelBuffer = None
        self.default_texts = None
        self.framebuffer_texts = None
        self.Character_draw = list(
            " .(){}01A")  # 按透明度从小到大排序，字符
        self.step = 5  #抽取的像素数量，越高，字符越少，越低，越卡【字符也多】

    # 当运算符结束时，在系统控制台上提示
    def __del__(self):
        print("结束演示代码")

    # 控制图像重画的模态运算符
    def modal(self, context, event):
        # esc 停止
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')

            # 当程序退出时回到原来的文本块
            area = [area for area in bpy.context.screen.areas if area.type == 'TEXT_EDITOR'][0]
            if area:
                area.spaces[0].text = self.default_texts

            print("删除绘图处理程序")
            return {'CANCELLED'}

        else:
            self.modal_redraw = True

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if not self.text_name in bpy.data.texts:
            self.framebuffer_texts = bpy.data.texts.new(self.text_name)
        else:
            self.framebuffer_texts = bpy.data.texts[self.text_name]

        area = [area for area in bpy.context.screen.areas if area.type == 'TEXT_EDITOR'][0]
        if area:
            if area.spaces[0].text:
                self.default_texts = area.spaces[0].text
            area.spaces[0].text = self.framebuffer_texts
            with bpy.context.temp_override(area=area):
                bpy.ops.text.move(type='FILE_TOP')
                bpy.ops.text.move(type='LINE_BEGIN')

        # 添加区域OpenGL图形回调函数
        self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw, (self, context), 'WINDOW', 'PRE_VIEW')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(TextCharacterDrawing)


def unregister():
    bpy.utils.unregister_class(TextCharacterDrawing)


if __name__ == "__main__":
    register()

    bpy.ops.view3d.text_character_drawing('INVOKE_DEFAULT')


