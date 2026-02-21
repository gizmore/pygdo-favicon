from __future__ import annotations

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT

from typing import TYPE_CHECKING, Self

from gdo.base.Util import Random
from gdo.core.GDO_File import GDO_File
from gdo.favicon.IcoGenerator import IcoGenerator
from gdo.ui.GDT_Color import GDT_Color
from gdo.ui.GDT_Image import GDT_Image

if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page


class module_favicon(GDO_Module):

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Image('favicon'),
            GDT_Color('bg_color').initial('#eeeeee').not_null().label('bg_color'),
            GDT_Color('theme_color').initial('#111111').not_null().label('theme_color'),
        ]

    def cfg_favicon_original(self) -> GDO_File | None:
        images = self.get_config_value('favicon')
        return images[0] if images else None

    def cfg_bg_color(self) -> str:
        return self.get_config_val('bg_color')

    def cfg_theme_color(self) -> str:
        return self.get_config_val('theme_color')

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe("clear_cache", self.on_cc)
        Application.EVENTS.subscribe("module_favicon_favicon_changed", self.favicon_changed)
        Application.EVENTS.subscribe("module_favicon_bg_color_changed", self.manifest_changed)
        Application.EVENTS.subscribe("module_favicon_theme_color_changed", self.manifest_changed)

    async def on_cc(self):
        await self.favicon_changed(self, None)

    async def favicon_changed(self, module: Self, gdt: GDT_Image | None) -> None:
        if image := module.cfg_favicon_original():
            IcoGenerator.generate(image)
        IcoGenerator.generate_manifest()

    async def manifest_changed(self, module: Self, gdt: GDT_Image):
        IcoGenerator.generate_manifest()

    def gdo_install(self):
        if not self.cfg_favicon_original():
            path = Random.list_item(['img/chappy.png', 'img/pygdo8.png'])
            favicon = GDO_File.from_path(self.file_path(path)).insert()
            self.save_config_val('favicon', favicon.get_id())

    def gdo_load_scripts(self, page: 'GDT_Page'):
        rev = self.av_cache_key()
        page.__class__._meta += f'<meta name="theme-color" content="#{self.cfg_theme_color()[2:]}">'
        if self.cfg_favicon_original():
           page.__class__._link += f"""
            <link rel="icon" href="/assets/favicon.ico?{rev}" sizes="any">
            <link rel="icon" type="image/png" href="/assets/favicon32.png?{rev}" sizes="32x32">
            <link rel="icon" type="image/png" href="/assets/favicon180.png?{rev}" sizes="180x180">
            <link rel="icon" type="image/png" href="/assets/favicon512.png?{rev}" sizes="512x512">
            <link rel="apple-touch-icon" href="/assets/favicon180.png?{rev}">
            <link rel="manifest" href="/assets/manifest.json?{rev}">"""
