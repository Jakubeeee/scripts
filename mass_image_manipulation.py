# This script allows you generate multiple distorted image sets for testing purposes
from PIL import Image, ImageEnhance
from imgaug import augmenters
import numpy
import shutil
import os

# path to the directory containing the input images
INPUT_IMAGES_DIR = 'C:\\input_images_dir'

# path to the directory where output images will be saved
OUTPUT_IMAGES_DIR = 'C:\\output_images_dir'

# a list that will be filled with file names from image input directory
IMAGE_NAMES = []

########################## filter configuration ##########################

# here you can configure filters that will be applied to input images
# you can either edit single filters or create/edit combined filters
# every single filter tuple consist of distortion name, min value, max value and step value
# every combined filter tuple consist of its name and multiple single filter tuples
FILTER_CONFIG_LIST = [

    # single filters
    ('ROTATION', 1, 50, 2.5),
    ('SHEAR', 1, 30, 1.5),
    ('BLUR', 0.2, 4, 0.2),
    ('SHARPEN', 0.05, 1, 0.05),
    ('EMBOSS', 0.05, 1, 0.05),
    ('PIXEL_DISPLACEMENT', 0.2, 4, 0.2),
    ('BRIGHTNESS_INCREMENT', 1, 3, 0.1),
    ('BRIGHTNESS_REDUCTION', 0.1, 1, 0.05),
    ('CONTRAST_INCREMENT', 1, 20, 1),
    ('CONTRAST_REDUCTION', 0.1, 1, 0.05),

    # example combined filters (you can also define your own)
    ('SHEAR_BRIGHTNESS_INCREMENT_COMBINED', ('SHEAR', 3, 30, 3), ('BRIGHTNESS_INCREMENT', 1.2, 3, 0.2)),
    ('ROTATION_PIXEL_DISPLACEMENT_COMBINED', ('ROTATION', 5, 50, 5), ('PIXEL_DISPLACEMENT', 0.4, 4, 0.4)),
    ('SHARPEN_EMBOSS_COMBINED', ('SHARPEN', 0.1, 1, 0.1), ('EMBOSS', 0.1, 1, 0.1)),
    ('ROTATION_BLUR_CONTRAST_REDUCTION_COMBINED', ('ROTATION', 10, 50, 10), ('BLUR', 0.8, 4, 0.8),
     ('CONTRAST_REDUCTION', 0.2, 1, 0.2)),
    ('ROTATION_BLUR_PIXEL_DISPLACEMENT_CONTRAST_INCREMENT_COMBINED', ('ROTATION', 25, 50, 25), ('BLUR', 2, 4, 2),
     ('PIXEL_DISPLACEMENT', 2, 4, 2), ('CONTRAST_INCREMENT', 10, 20, 10))
]

# filters for which image sets will be generated
ACTIVE_FILTERS = ['BLUR', 'SHEAR', 'EMBOSS', 'SHEAR_BRIGHTNESS_INCREMENT_COMBINED']

##########################################################################

final_output_data = []


def run():
    populate_image_names_list()
    clean_augmented_images()
    prepare_catalogue_structure()
    for image_name in IMAGE_NAMES:
        for filter_config_tuple in FILTER_CONFIG_LIST:
            if filter_config_tuple[0] in ACTIVE_FILTERS:
                prepare_augmented_images(image_name, filter_config_tuple)
    for image_to_save in final_output_data:
        save_augmented_image(*image_to_save)


def populate_image_names_list():
    for parent, dirNames, fileNames in os.walk(INPUT_IMAGES_DIR):
        for file_name in fileNames:
            IMAGE_NAMES.append(file_name)


def clean_augmented_images():
    for parent, dirNames, fileNames in os.walk(OUTPUT_IMAGES_DIR):
        for dir_name in dirNames:
            dir_path = os.path.join(parent, dir_name)
            shutil.rmtree(dir_path, ignore_errors=True)


def prepare_catalogue_structure():
    for face_owner in IMAGE_NAMES:
        for filter_config_tuple in FILTER_CONFIG_LIST:
            if filter_config_tuple[0] in ACTIVE_FILTERS:
                prepare_catalogue_structure_node(face_owner, filter_config_tuple[0])


def prepare_catalogue_structure_node(file_name, filter_name):
    directory_path = OUTPUT_IMAGES_DIR + '\\' + extensionless(file_name) + '\\' + filter_name
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def extensionless(filename):
    new_filename, file_extension = os.path.splitext(filename)
    return new_filename


def prepare_augmented_images(file_name, filter_config_tuple):
    target_image = Image.open(INPUT_IMAGES_DIR + '\\' + file_name)
    overall_filter_name = filter_config_tuple[0]

    if isinstance(filter_config_tuple[1], tuple):
        final_output_data.extend(get_output_data_for_multiple_filters(target_image, file_name, filter_config_tuple))
    else:
        final_output_data.extend(
            get_output_data_for_single_filter(target_image, file_name, overall_filter_name, filter_config_tuple))


def get_output_data_for_multiple_filters(target_image, file_name, filter_config_tuple):
    single_filter_name = filter_config_tuple[1][0]
    output_data = get_output_data_for_single_filter(target_image, file_name, single_filter_name,
                                                    filter_config_tuple[1])
    combined_filter_name = single_filter_name

    for i in range(2, len(filter_config_tuple)):
        temp_output_data = []
        single_filter_name = filter_config_tuple[i][0]
        combined_filter_name = combined_filter_name.replace('_COMBINED', '') + '_' + single_filter_name + '_COMBINED'

        for single_output_data in output_data:
            distortion_value = single_output_data[3]
            nested_output_data = (
                get_output_data_for_single_filter(single_output_data[0], file_name, single_filter_name,
                                                  filter_config_tuple[2]))
            for single_nested_output_data in nested_output_data:
                single_nested_output_data[2] = combined_filter_name
                single_nested_output_data[3] = str(distortion_value) + '_' + str(single_nested_output_data[3])
                temp_output_data.extend(nested_output_data)

        output_data = temp_output_data.copy()
    return output_data


def get_output_data_for_single_filter(target_image, file_name, filter_name, filter_config_tuple):
    output_data = []
    min_value = filter_config_tuple[1]
    max_value = filter_config_tuple[2]
    step = filter_config_tuple[3]
    distortion_value = min_value
    while distortion_value <= max_value:
        edited_image = edit_image(target_image, filter_name, distortion_value)
        image_data_to_save = [edited_image, file_name, filter_name, distortion_value]
        output_data.append(image_data_to_save)
        distortion_value += step
        distortion_value = float("{0:.5f}".format(distortion_value))
    return output_data


def edit_image(image, filter_name, distortion_value):
    if filter_name == 'SCALE':
        edited_image = apply_imgaug_effect(image, augmenters.Scale(distortion_value))
    elif filter_name == 'ROTATION':
        edited_image = image.rotate(distortion_value)
    elif filter_name == 'SHEAR':
        edited_image = apply_imgaug_effect(image, augmenters.Affine(shear=distortion_value))
    elif filter_name == 'BLUR':
        edited_image = apply_imgaug_effect(image, augmenters.GaussianBlur(sigma=distortion_value))
    elif filter_name == 'SHARPEN':
        edited_image = apply_imgaug_effect(image, augmenters.Sharpen(alpha=distortion_value, lightness=1.0))
    elif filter_name == 'EMBOSS':
        edited_image = apply_imgaug_effect(image, augmenters.Emboss(alpha=distortion_value, strength=1.0))
    elif filter_name == 'DISTORTIONS':
        edited_image = apply_imgaug_effect(image, augmenters.PiecewiseAffine(scale=distortion_value))
    elif filter_name == 'PIXEL_DISPLACEMENT':
        edited_image = apply_imgaug_effect(image, augmenters.ElasticTransformation(alpha=distortion_value, sigma=0.25))
    elif filter_name == 'BRIGHTNESS_INCREMENT':
        edited_image = ImageEnhance.Brightness(image).enhance(distortion_value)
    elif filter_name == 'BRIGHTNESS_REDUCTION':
        edited_image = ImageEnhance.Brightness(image).enhance(distortion_value)
    elif filter_name == 'CONTRAST_INCREMENT':
        edited_image = ImageEnhance.Contrast(image).enhance(distortion_value)
    elif filter_name == 'CONTRAST_REDUCTION':
        edited_image = ImageEnhance.Contrast(image).enhance(distortion_value)
    else:
        edited_image = image
    return edited_image


def apply_imgaug_effect(image, imgaug_filter):
    image_as_ndarray = numpy.array(image)
    edited_image = imgaug_filter.augment_image(image_as_ndarray)
    return Image.fromarray(numpy.uint8(edited_image))


def save_augmented_image(image, file_name, filter_name, distortion_value):
    image.save(
        OUTPUT_IMAGES_DIR + '\\' + '{}\\'.format(extensionless(file_name)) + filter_name + '\\' + "IMG_{}_{}_{}.jpg"
        .format(extensionless(file_name), filter_name, distortion_value))
    print('Created image of {} with {} on level(s) {}'.format(extensionless(file_name), filter_name, distortion_value))


run()
