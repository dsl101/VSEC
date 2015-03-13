"""
VSE Crossfades
Copyright (C) 2015 Nathan Craddock

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

bl_info = {
    "name": "VSE Crossfades",
    "author": "Nathan Craddock",
    "version": (1, 0, 0),
    "blender": (2, 7, 3),
    "location": "Object Mode >> Tool Shelf >> VSE Crossfade (Tab)",
    "description": "Allows the user to select a directory, and it adds the files in the directory to the VSE with crossfades.",
    "category": "Tools"
}

import bpy
import random
import os

class vseCrossfadesPanel(bpy.types.Panel):
    """VSE Crossfade Addon Panel"""
    bl_category = "VSE Crossfade"
    bl_idname = "tools.vse_crossfade_panel"
    bl_context = "objectmode"
    bl_label = "VSE Crossfades"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        directory = context.scene.vsec_directory_path
        mode = context.scene.vsec_mode
        
        layout = self.layout
        
        row = layout.row()
        row.prop(context.scene, "vsec_mode")
        
        row = layout.row()
        row.prop(context.scene, "vsec_directory_path", text="")
        
        row = layout.row()
        
        #Display information about selected directory       
        if directory == "":
            row.label(text = "Choose a directory")
        else:
            #Check if it is a path
            if os.path.exists(os.path.dirname(directory)):
                #Print information about the path
                
                file_list = []
                for f in os.listdir(directory):
                    if mode == "vid":
                        if f.endswith('.mp4') or f.endswith('.mov') or f.endswith('.avi') or f.endswith('.mpg') or f.endswith('.xvid'):
                            file_list.append(f)
                    elif mode == "img":
                        if f.endswith('.bmp') or f.endswith('.png') or f.endswith('.jpg') or f.endswith('.tif') or f.endswith('.exr'):
                            file_list.append(f)
                row.label(text = "Number of files: " + str(len(file_list)))
            else:
                row.label(text = "Invalid Path")
        
        #Sorting methods
        row = layout.row()
        row.prop(context.scene, "vsec_sort_type")
        
        #Image-Only options
        if mode == "img":    
            row = layout.row()
            row.prop(context.scene, "vsec_image_length")
            row.prop(context.scene, "vsec_image_length_range")
        
        #Crossfade options
        layout.separator()
        row = layout.row()
        row.prop(context.scene, "vsec_crossfade_length")
        row.prop(context.scene, "vsec_crossfade_length_range")
        
        #Other options
        split = layout.split()
        col = split.column(align = True)
        col.prop(context.scene, "vsec_auto_timeline")
        col = split.column(align = True)
        col.prop(context.scene, "vsec_clear_sequencer")
        row = layout.row()
        row.prop(context.scene, "vsec_start_frame")
        row = layout.row()
        row.operator("tools.vse_crossfade_addon")
        

class vseCrossfades(bpy.types.Operator):
    """Add files to the Video Sequence Editor using the values above"""
    bl_idname = "tools.vse_crossfade_addon"
    bl_label = "Add files to VSE"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #Get the files from the directory, based on file type
        path = context.scene.vsec_directory_path
        mode = context.scene.vsec_mode
        sort_method = context.scene.vsec_sort_type
        
        file_list = []
        for f in os.listdir(path):
            if mode == "vid":
                if f.endswith('.mp4') or f.endswith('.mov') or f.endswith('.avi') or f.endswith('.mpg') or f.endswith('.xvid'):
                    file_list.append(f)
            elif mode == "img":
                if f.endswith('.bmp') or f.endswith('.png') or f.endswith('.jpg') or f.endswith('.tif') or f.endswith('.exr'):
                    file_list.append(f)
                
        for item in file_list:
            print(item)
            
        #Sorting
        if sort_method == "alpha":
            #Should already be sorted
            print("sorted")
            
        strips = []
        for strip in file_list:
            strips.append(os.path.join(path, strip))
            
        #Add sorting algorithms here
        
        frame_offset = context.scene.vsec_crossfade_length
        frame_offset_random = context.scene.vsec_crossfade_length_range

        

        #Add the strips
        bpy.context.area.type = 'SEQUENCE_EDITOR'
        
        if context.scene.vsec_clear_sequencer:
            bpy.context.scene.sequence_editor_clear()

        offset = context.scene.vsec_start_frame
        channel_offset = 1
        strip_number = 1

        for i in range(0, len(strips)):
            
            #Change the channel offset
            if strip_number % 2 == 1:
                channel_offset = 1
            else:
                channel_offset = 2
            
            if mode == 'vid':
                bpy.ops.sequencer.movie_strip_add(filepath = strips[i], frame_start = offset, channel = channel_offset)
            elif mode == 'img':
                print("created")
                bpy.ops.sequencer.image_strip_add(directory = path, files = [{"name" : file_list[i]}], frame_start = offset, frame_end = offset + context.scene.vsec_image_length, channel = channel_offset)
            
            #Make into meta strip if video
            if mode == "vid":
                bpy.ops.sequencer.meta_make()
            
            #Rename for easy selecting
            bpy.context.selected_sequences[0].name = str(strip_number)
            
            #crossfade
            if len(bpy.context.sequences) > 1:
                print("adding crossfade")
                
                #Deselect everything
                bpy.ops.sequencer.select_all()
                
                bpy.data.scenes["Scene"].sequence_editor.sequences_all[str(strip_number)].select = True
                bpy.data.scenes["Scene"].sequence_editor.sequences_all[str(strip_number - 1)].select = True
                
                bpy.ops.sequencer.effect_strip_add(type='CROSS')
                
                bpy.ops.sequencer.select_all()
                
                bpy.data.scenes["Scene"].sequence_editor.sequences_all[str(strip_number)].select = True
            
            
            #Add the length of the current strip to the offset
            randInt = random.randint(0, 1)
            if randInt == 0:
                offset += bpy.context.selected_sequences[0].frame_final_duration - (frame_offset - random.randint(0, frame_offset_random))
            else:
                offset += bpy.context.selected_sequences[0].frame_final_duration - (frame_offset + random.randint(0, frame_offset_random))
            
            strip_number += 1

            
        #Set the length of the timeline to the duration
        if context.scene.vsec_auto_timeline:
            bpy.ops.sequencer.select_all()
            bpy.data.scenes["Scene"].sequence_editor.sequences_all[str(strip_number - 1)].select = True
            last_frame = bpy.context.selected_sequences[0].frame_final_end
            bpy.context.area.type = 'VIEW_3D'
            bpy.context.scene.frame_end = last_frame - 1
            
            bpy.context.area.type = 'TIMELINE'
            
            bpy.ops.time.view_all()
        
            bpy.context.area.type = 'VIEW_3D'
            
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(vseCrossfades)
    bpy.utils.register_class(vseCrossfadesPanel)
    bpy.types.Scene.vsec_crossfade_length = bpy.props.IntProperty(name="Crossfade Length", description="Length in frames of the crossfade", default=10, min = 1)
    bpy.types.Scene.vsec_crossfade_length_range = bpy.props.IntProperty(name="Variation", description="How much variation to add to the crossfade length", default=0, min=0)
    bpy.types.Scene.vsec_image_length = bpy.props.IntProperty(name="Image Length", description="How long should each image be?", default=75, min=1)
    bpy.types.Scene.vsec_image_length_range = bpy.props.IntProperty(name="Variation", description="How much variation to add to the image length", default=0, min=0)
    bpy.types.Scene.vsec_start_frame = bpy.props.IntProperty(name="Start Frame", description="What frame to start on", default=1, min=1)
    bpy.types.Scene.vsec_auto_timeline = bpy.props.BoolProperty(name="Auto Timeline", description="Automatically set the end frame.", default = True)
    bpy.types.Scene.vsec_clear_sequencer = bpy.props.BoolProperty(name="Clear Sequencer", description="Clear the sequencer before running", default = True)
    bpy.types.Scene.vsec_directory_path = bpy.props.StringProperty(name="Directory", description="Choose the folder where the video files are located", default="", subtype='DIR_PATH')
    bpy.types.Scene.vsec_mode = bpy.props.EnumProperty(name = "Mode", items = [("img", "Images", "Use only Images"), ("vid", "Video", "Use only Videos")], default = "vid")
    bpy.types.Scene.vsec_sort_type = bpy.props.EnumProperty(name="Sorting Method", items =[("alpha", "Alphabetical", "Sort the files alphabetically"), ("size", "File Size", "Sort the files by size")], default = "alpha")

def unregister():
    bpy.utils.unregister_class(vseCrossfades)
    bpy.utils.unregister_class(vseCrossfadesPanel)
    
if __name__ == "__main__":
    register()