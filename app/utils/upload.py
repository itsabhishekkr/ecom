import os
import uuid
import shutil


def save_product_image(image):

    os.makedirs(
        "uploads/products",
        exist_ok=True
    )

    extension = (
        image.filename.split(".")[-1]
    )

    filename = (
        f"{uuid.uuid4()}.{extension}"
    )

    path = (
        f"uploads/products/{filename}"
    )

    with open(
        path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            image.file,
            buffer
        )

    return f"/{path}"