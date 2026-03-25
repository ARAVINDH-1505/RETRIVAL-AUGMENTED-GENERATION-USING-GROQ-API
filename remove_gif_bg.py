import sys
try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

def remove_white_bg_gif(input_path, output_path, tolerance=40):
    try:
        img = Image.open(input_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    frames = []
    duration = img.info.get("duration", 100)
    
    # Process each frame
    try:
        for frame_idx in range(img.n_frames):
            img.seek(frame_idx)
            
            # Convert to RGBA
            rgba_frame = img.convert("RGBA")
            data = rgba_frame.getdata()
            
            new_data = []
            for item in data:
                # If R, G, B are all high (close to white)
                if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
                    # Make it transparent
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
                    
            rgba_frame.putdata(new_data)
            frames.append(rgba_frame)
    except EOFError:
        pass
        
    if frames:
        # Save as a new transparent GIF
        frames[0].save(
            output_path, 
            save_all=True, 
            append_images=frames[1:], 
            loop=0, 
            duration=duration,
            disposal=2
        )
        print(f"Successfully processed GIF and saved to: {output_path}")

input_gif = "app/static/rick-and-morty-nave.gif"
output_gif = "app/static/spaceship_transparent.gif"

print(f"Processing {input_gif}...")
remove_white_bg_gif(input_gif, output_gif)
