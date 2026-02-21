from pathlib import Path
from PIL import Image

from gdo.base.Application import Application
from gdo.base.Util import Files


class ImageConverter:

    @classmethod
    def convert(
            cls,
            src_path: str,
            dest_path: str = None,
            to_fmt: str = None,
            dim: tuple[int, int] = None,
    ):
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(src_path)

        # Normalize format
        if to_fmt:
            to_fmt = to_fmt.lower().replace(".", "")

        # Determine source format
        with Image.open(src) as im:
            src_fmt = im.format.lower()

        # Decide target format
        target_fmt = to_fmt or src_fmt

        # Determine destination path
        if dest_path is None:
            if not to_fmt:
                raise ValueError("Refusing to overwrite source without format change.")
            dest = src.with_suffix("." + target_fmt)
        else:
            dest = Path(dest_path)

        if dest.resolve() == src.resolve():
            raise ValueError("Source and destination are identical.")

        if dest.exists():
            raise FileExistsError(dest)

        # Convert
        with Image.open(src) as im:
            im = im.convert("RGBA")

            if dim:
                im = im.resize(dim, Image.LANCZOS)

            save_kwargs = {}

            if target_fmt == "ico":
                sizes = [dim] if dim else [(16, 16), (32, 32), (48, 48), (64, 64)]
                save_kwargs["sizes"] = sizes

            dest.parent.mkdir(int(Application.config('file.mode.dir', '0o0700'), 0), True, True)

            im.save(dest, format=target_fmt.upper(), **save_kwargs)

        return str(dest)
