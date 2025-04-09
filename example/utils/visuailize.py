import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt

def tree(dir_path, max_files=3, max_lines=20):
    '''
    dir_path: str, directory path
    max_files: int, maximum number of files to display per directory
    max_lines: int, maximum total number of lines to display
    '''
    line_count = 0
    
    for root, dirs, files in os.walk(dir_path):
        if line_count >= max_lines:
            print(f"\n... and more directories (reached max_lines={max_lines})")
            break
            
        level = root.replace(dir_path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        line_count += 1
        
        sub_indent = ' ' * 4 * (level + 1)
        
        # Display files up to max_files limit
        for f in files[:max_files]:
            if line_count >= max_lines:
                print(f"{sub_indent}... and more files (reached max_lines={max_lines})")
                break
            print(f"{sub_indent}{f}")
            line_count += 1
        
        # If there are more files, show a count
        if len(files) > max_files and line_count < max_lines:
            print(f"{sub_indent}... and {len(files) - max_files} more files")
            line_count += 1

def read_and_get_image_array(image_path):
    '''
    image_path: str, nii.gz file path
    '''
    
    image = nib.load(image_path)
    image_array = image.get_fdata()
    return image_array

def display_slices(image_array):
    '''
    image_array: 3D numpy array
    '''
    if len(image_array.shape) != 3:
        print("The input file is not a valid 3D image.")
        return None
    
    axial_view = image_array[image_array.shape[0] // 2]
    sagittal_view = image_array[:, image_array.shape[1] // 2, :]
    coronal_view = image_array[:, :, image_array.shape[2] // 2]

    view_shapes = [
        ('Axial View', axial_view),
        ('Sagittal View', sagittal_view),
        ('Coronal View', coronal_view)
    ]

    max_shape_index = np.argmax([np.prod(view.shape) for _, view in view_shapes])
    
    return view_shapes[max_shape_index]

def visualize_nii_slices(image_paths, columns=5, max_images=20, verbose=True):
    '''
    image_paths: list of str, nii.gz file paths
    columns: int, number of columns in the plot
    max_images: int, maximum number of images to plot
    '''
    if len(image_paths) == 0:
        print("No image paths provided.")
        return
    if len(image_paths) > max_images:
        image_paths = image_paths[:max_images]

    if verbose:
        for i, img_path in enumerate(image_paths):
            print(f"Image {i+1}: {img_path}")

    num_images = len(image_paths)
    num_rows = (num_images + columns - 1) // columns
    fig, axes = plt.subplots(num_rows, columns, figsize=(columns * 5, num_rows * 4))
    
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])

    axes_flat = axes.ravel() 

    for i, image_path in enumerate(image_paths):
        row = i // columns
        col = i % columns
        
        image_array = read_and_get_image_array(image_path)
        view_name, max_view = display_slices(image_array)

        if max_view is None:
            continue

        ax = axes_flat[i]
        ax.imshow(max_view, cmap='gray')
        ax.set_title(f'Image {i+1}: {view_name}')

    for i in range(num_rows * columns):
        row = i // columns
        col = i % columns
        if num_rows * columns > len(image_paths) and (row * columns + col >= len(image_paths)):
            axes_flat[i].axis('off')

    plt.tight_layout()
    plt.show()
