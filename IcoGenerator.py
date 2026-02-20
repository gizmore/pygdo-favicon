from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.Logger import Logger
from gdo.base.Trans import t
from gdo.base.Util import Strings, Files, module_config_var
from gdo.core.GDO_File import GDO_File
from gdo.favicon.ImageConverter import ImageConverter
from gdo.file.GDO_SeoFile import GDO_SeoFile


class IcoGenerator:

    @classmethod
    def generate(cls, src_file: GDO_File):
        path = src_file.get_path()

        from gdo.core.module_core import module_core
        base = module_core.instance().assets_path()
        # Files.create_dir(Application.temp_path('assets/'))

        cls._generate_b(path, f'{base}favicon32.png', 'PNG', (32, 32))
        cls._generate_b(path, f'{base}favicon180.png', 'PNG', (180, 180))
        cls._generate_b(path, f'{base}favicon192.png', 'PNG', (192, 192))
        cls._generate_b(path, f'{base}favicon512.png', 'PNG', (512, 512))
        cls._generate_b(path, f'{base}favicon.ico', 'ICO', (32, 32))

    @classmethod
    def _generate_b(cls, src_path: str, dest_path: str, to_fmt: str, dim: tuple[int, int]):
        new_path = ''
        try:
            seo_file = GDO_SeoFile.get_by_url(dest_path) or GDO_SeoFile.blank({'sf_url': dest_path})
            new_path = ImageConverter.convert(src_path, Application.temp_path(dest_path), to_fmt, dim)
            gdo_file = GDO_File.blank({
                'file_name': Strings.rsubstr_from(dest_path, '/', dest_path),
                'file_size': str(Files.size(new_path)),
                'file_mime': Files.mime(new_path),
                'file_hash': Files.md5(new_path),
                'file_width': str(dim[0]),
                'file_height': str(dim[1]),
            }).insert()
            Files.move(new_path, gdo_file.get_path())
            seo_file.set_val('sf_file', gdo_file.get_id())
            seo_file.save()
        except Exception as e:
            Logger.exception(e, 'cannot convert image')
        finally:
            if new_path and Files.is_file(new_path):
                Files.remove(new_path)

    @classmethod
    def generate_manifest(cls):
        path = 'assets/manifest.json'
        rev = GDO_Module.CORE_REV
        content = f"""
                {{
                    "name": "{t('sitename')}",
                    "short_name": "{Application.config('core.sitename')}",
                    "description": "{t('sitedesc')}",
                    "start_url": "{Application.config('core.web_root')}",
                    "scope": "{Application.config('core.web_root')}",
                    "display": "standalone",
                    "background_color": "#{module_config_var('favicon', 'bg_color')[0:6]}",
                    "theme_color": "#{module_config_var('favicon', 'theme_color')[0:6]}",
                    "icons": [
                        {{
                            "src": "/assets/favicon192.png?{rev}", "sizes": "192x192", "type": "image/png"
                        }},
                        {{
                            "src": "/assets/favicon512.png?{rev}", "sizes": "512x512", "type": "image/png"
                        }}
                    ]
                }}
        """
        seo_file = GDO_SeoFile.get_by_url(path) or GDO_SeoFile.blank({'sf_url': path})
        if not seo_file.gdo_val('sf_file'):
            gdo_file = GDO_File.blank({
                'file_name': Strings.rsubstr_from(path, '/', path),
                'file_size': str(len(content.encode())),
                'file_mime': 'application/manifest+json',
            }).insert()
        else:
            gdo_file = seo_file.gdo_value('sf_file')[0]
        Files.put_contents(gdo_file.get_path(), content)
        gdo_file.set_vals({
            'file_size': str(len(content.encode())),
        })
        gdo_file.save()
        seo_file.save_val('sf_file', gdo_file.get_id())
