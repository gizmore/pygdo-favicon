import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import get_module, Files
from gdo.core.method.clear_cache import clear_cache
from gdo.favicon.module_favicon import module_favicon
from gdo.file.GDO_SeoFile import GDO_SeoFile
from gdotest.TestUtil import GDOTestCase, install_module, reinstall_module


class FunTestCase(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        Application.init_cli()
        loader = ModuleLoader.instance()
        install_module('favicon')
        loader.load_modules_db(True)
        loader.init_modules(True, True)
        loader.init_cli()

    async def test_00_reinstall(self):
        reinstall_module('favicon')
        self.assertIs(type(get_module('favicon')), module_favicon, 'cannot reinstall favicon.')

    async def test_01_no_icon_rebuild_manifest(self):
        await clear_cache().gdo_execute()
        self.assertTrue(GDO_SeoFile.get_by_url('assets/manifest.json') is not None, 'Cannot create empty manifest.')


if __name__ == '__main__':
    unittest.main()
