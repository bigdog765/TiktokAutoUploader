import sys, os
from tiktok_uploader.Config import Config
from moviepy import ImageClip, concatenate_videoclips, VideoClip
from PIL import Image
import numpy as np

def get_image_files():
    image_dir = os.path.join(os.getcwd(), Config.get().images_dir)
    if os.path.exists(image_dir):
        image_list = []
        for image_name in os.listdir(image_dir):
            print(image_name)
            if not image_name.endswith(".mp4"):
                image_list.append(os.path.join(os.getcwd(), Config.get().images_dir, image_name))
        print('List:', image_list)
        return image_list
        

# Function to create a flipping effect
def create_clip(image_path, duration=2):
    # Open and resize the image
    image = Image.open(image_path).resize((1080, 1920))
    
    # Convert the PIL image to a NumPy array
    image_array = np.array(image)
    return ImageClip(image_array, duration=duration)
   

def create_image_video(image_paths):
    # Create a list of clips with the flip effect
    clips = [create_clip(image_path, duration=8) for image_path in image_paths]

    # Concatenate all the clips into a single video
    concat_clips = concatenate_videoclips(clips)
    # Resize to 1080x1920
    resized_clip = concat_clips.resized(width=1080, height=1920)

    # Save the resulting video
    resized_clip.write_videofile("./VideosDirPath/output_video.mp4", fps=24)

