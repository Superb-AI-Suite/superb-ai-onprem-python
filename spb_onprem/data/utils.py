from PIL import Image
from io import BytesIO

class Utils:
    """Data Module Utils."""
   

    @staticmethod
    def create_thumbnail(
        image: BytesIO,
        thumbnail_size=(128, 128)
    ):
        """Create a thumbnail image from the given BytesIO image data.

        Args:
            image (BytesIO): The image data in BytesIO format.
            thumbnail_size (tuple): The size of the thumbnail image.
        """
        with Image.open(image) as img:
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

            thumb = Image.new('RGB', thumbnail_size, (255, 255, 255))  # White background

            left = (thumbnail_size[0] - img.width) // 2
            top = (thumbnail_size[1] - img.height) // 2

            thumb.paste(img, (left, top))

            thumbnail_io = BytesIO()
            thumb.save(thumbnail_io, format='JPEG')
            thumbnail_io.seek(0)
            return thumbnail_io
    
    @staticmethod
    def create_thumbnail_from_path(
        image_path: str,
        thumbnail_size=(128, 128)
    ):
        """Create a thumbnail image from the given image path.

        Args:
            image_path (str): The path to the image file.
            thumbnail_size (tuple): The size of the thumbnail image.
        """
        with open(image_path, 'rb') as image_file:
            image_data = BytesIO(image_file.read())
            return Utils.create_thumbnail(image_data, thumbnail_size)
