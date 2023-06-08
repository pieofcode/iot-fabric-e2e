from datetime import datetime
import os
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os
import json


def test_func():
    print("***************** FUNC LOADED **************")


class ImageGenerator:

    img_root_dir = ""
    original_img_dir = ""
    output_img_dir = ""
    img_metadata = []

    @staticmethod
    def get_all_images(img_root_dir, original_img_dir):
        ImageGenerator.img_root_dir = img_root_dir
        ImageGenerator.original_img_dir = original_img_dir
        ImageGenerator.output_img_dir = "output"

        img_dir_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.original_img_dir}"
        img_list = []
        files = os.listdir(img_dir_path)
        for img_file in files:
            if os.path.isdir(f"{ImageGenerator.img_root_dir}/{ImageGenerator.original_img_dir}/{img_file}"):
                continue

            img_list.append(img_file)

        return img_list

    @staticmethod
    def get_all_orientation():
        return ['', 'GRAY', 'DEFECTIVE', 'ROTATED', 'SCALED', 'DEFECTIVE2', 'SCALED2', 'SCALED3']

    @staticmethod
    def get_metadata(part_name, orientation, img_path, tag="POSITIVE"):
        epoch_time = time.time()
        orientation = orientation if orientation else "ORIGINAL"
        metadata = {
            "id": f"{part_name}/{orientation}/{epoch_time}",
            "name": part_name,
            "orientation": orientation,
            "file_path": img_path,
            "tag": tag,
            "classification": None,
            "created_on": datetime.utcfromtimestamp(epoch_time).isoformat()
        }
        ImageGenerator.img_metadata.append(metadata)
        return metadata

    @staticmethod
    def get_image(img_file, orientation):

        name_template = f'{img_file.replace(".png", "")}'
        # Open an original image
        img = cv.imread(
            f"{ImageGenerator.img_root_dir}/{ImageGenerator.original_img_dir}/{img_file}")

        output_file_path = ""
        if(orientation == ""):
            output_file_path, metadata = ImageGenerator.get_original_image(
                name_template, img)

        if(orientation == "GRAY"):
            output_file_path, metadata = ImageGenerator.get_gray_image(
                name_template, img)

        if(orientation == "DEFECTIVE"):
            output_file_path, metadata = ImageGenerator.get_defective_image(
                name_template, img)

        if(orientation == "ROTATED"):
            output_file_path, metadata = ImageGenerator.get_rotated_image(
                name_template, img)

        if(orientation == "SCALED"):
            output_file_path, metadata = ImageGenerator.get_scaled_image(
                name_template, img)

        if(orientation == "DEFECTIVE2"):
            output_file_path, metadata = ImageGenerator.get_defective2_image(
                name_template, img)

        if(orientation == "SCALED2"):
            output_file_path, metadata = ImageGenerator.get_scaled2_image(
                name_template, img)

        if(orientation == "SCALED3"):
            output_file_path, metadata = ImageGenerator.get_scaled3_image(
                name_template, img)

        return output_file_path, metadata

    @staticmethod
    def get_original_image(name_template, img):
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{name_template}.png"

        # gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        metadata = ImageGenerator.get_metadata(
            name_template, "", output_file_path)
        cv.imwrite(output_file_path, img)
        print(
            f"File [{output_file_path}] written to the directory: {os.path.exists(output_file_path)}")

        return output_file_path, metadata

    @staticmethod
    def get_gray_image(name_template, img):

        h, w, c = img.shape
        gray_image_file = f'{name_template}_GRAY.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{gray_image_file}"
        print(f"Gray image file: {output_file_path}")

        gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        metadata = ImageGenerator.get_metadata(
            name_template, "GRAY", output_file_path)
        cv.imwrite(output_file_path, gray_image)

        return output_file_path, metadata

    @staticmethod
    def get_defective_image(name_template, img):
        defective_image_file = f'{name_template}_DEFECTIVE.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{defective_image_file}"
        print(f"Defective image file: {defective_image_file}")
        defective_image = cv.circle(img, (300, 300), 60, (0, 0, 255), -1)
        metadata = ImageGenerator.get_metadata(
            name_template, "DEFECTIVE", output_file_path, "NEGATIVE")
        cv.imwrite(output_file_path, defective_image)

        return output_file_path, metadata

    @staticmethod
    def get_rotated_image(name_template, img):
        rotated_image_file = f'{name_template}_ROTATED.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{rotated_image_file}"
        print(f"Rotated image file: {rotated_image_file}")
        h, w = img.shape[:2]
        rotation_matrix = cv.getRotationMatrix2D((w/2, h/2), -180, 0.5)
        rotated_image = cv.warpAffine(img, rotation_matrix, (w, h))
        rotated_image_final = cv.cvtColor(rotated_image, cv.COLOR_BGR2RGB)
        metadata = ImageGenerator.get_metadata(
            name_template, "GRAY", output_file_path)
        cv.imwrite(output_file_path, rotated_image_final)

        return output_file_path, metadata

    @staticmethod
    def get_defective2_image(name_template, img):
        h, w, c = img.shape
        defective2_image_file = f'{name_template}_DEFECTIVE2.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{defective2_image_file}"
        print(f"Defective2 image file: {defective2_image_file}")
        defective2_image = cv.line(
            img, (int(h/2), int(w/2)), (int(h/2)+40, int(w/2)+40), (0, 0, 0), 10)
        metadata = ImageGenerator.get_metadata(
            name_template, "DEFECTIVE2", output_file_path, "NEGATIVE")
        cv.imwrite(output_file_path, defective2_image)

        return output_file_path, metadata

    @staticmethod
    def get_scaled_image(name_template, img):
        scaled_image_file = f'{name_template}_SCALED.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{scaled_image_file}"
        print(f"Scaled image file: {scaled_image_file}")
        image_scaled = cv.resize(img, None, fx=0.15, fy=0.15)
        scaled_image = cv.cvtColor(image_scaled, cv.COLOR_BGR2RGB)
        metadata = ImageGenerator.get_metadata(
            name_template, "SCALED", output_file_path)
        cv.imwrite(output_file_path, scaled_image)

        return output_file_path, metadata

    @staticmethod
    def get_scaled2_image(name_template, img):
        scaled2_image_file = f'{name_template}_SCALED2.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{scaled2_image_file}"
        print(f"Scaled image file: {scaled2_image_file}")
        image_scaled_2 = cv.resize(
            img, None, fx=2, fy=2, interpolation=cv.INTER_CUBIC)
        scaled2_image = cv.cvtColor(image_scaled_2, cv.COLOR_BGR2RGB)
        metadata = ImageGenerator.get_metadata(
            name_template, "SCALED2", output_file_path, "NEGATIVE")
        cv.imwrite(output_file_path, scaled2_image)

        return output_file_path, metadata

    @staticmethod
    def get_scaled3_image(name_template, img):
        scaled3_image_file = f'{name_template}_SCALED3.png'
        output_file_path = f"{ImageGenerator.img_root_dir}/{ImageGenerator.output_img_dir}/{scaled3_image_file}"
        print(f"Scaled image file: {scaled3_image_file}")
        image_scaled_3 = cv.resize(
            img, (200, 400), interpolation=cv.INTER_AREA)
        output_image_3 = cv.cvtColor(image_scaled_3, cv.COLOR_BGR2RGB)
        metadata = ImageGenerator.get_metadata(
            name_template, "SCALED3", output_file_path, "NEGATIVE")
        cv.imwrite(output_file_path, output_image_3)

        return output_file_path, metadata
