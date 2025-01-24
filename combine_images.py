import sys, os
from tiktok_uploader.Config import Config
from moviepy import ImageClip, concatenate_videoclips, VideoClip, AudioFileClip
from PIL import Image
import numpy as np
import random

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
        
def remove_images(image_paths):
    for image_path in image_paths:
        os.remove(image_path)
# Function to create a flipping effect
def create_clip(image_path, duration=2):
    # Open and resize the image
    image = Image.open(image_path).resize((1080, 1350))
    
    # Convert the PIL image to a NumPy array
    image_array = np.array(image)
    return ImageClip(image_array, duration=duration)
   

def create_image_video(image_paths):
    # Get a random audio file from the audio directory
    audio_dir = os.path.join(os.getcwd(), 'AudioDirPath/')
    sound = audio_dir + random.choice(os.listdir(audio_dir))
    print('Sound:',sound)
    # Create a list of clips with the flip effect
    clips = [create_clip(image_path, duration=6) for image_path in image_paths]

    # Concatenate all the clips into a single video
    concat_clips = concatenate_videoclips(clips)
    # Resize to 4:5
    resized_clip = concat_clips.resized(width=1080, height=1350) # 4:5 aspect ratio
    
    # Load the audio file
    audio_clip = AudioFileClip(sound)
    # Truncate the audio to match the duration of the video
    audio_clip = audio_clip.subclipped(0, resized_clip.duration)

    # Set the audio to the video clip
    final_clip = resized_clip.with_audio(audio_clip)

    # Save the resulting video
    final_clip.write_videofile("./VideosDirPath/output_video.mp4", fps=24)
    # delete all images in image directory
    remove_images(image_paths)

