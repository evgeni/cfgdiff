import unittest
import cfgdiff


class CfgDiffTestCase(unittest.TestCase):

    def _test_same(self, cls, filea, fileb, parser=None):
        a = cls(filea, ordered=False, parser=parser)
        b = cls(fileb, ordered=False, parser=parser)

        self.assertIsNone(a.error)
        self.assertIsNone(b.error)

        self.assertEqual(a.readlines(), b.readlines())

    def _test_different(self, cls, filea, fileb, parser=None):
        a = cls(filea, ordered=False, parser=parser)
        b = cls(fileb, ordered=False, parser=parser)

        self.assertIsNone(a.error)
        self.assertIsNone(b.error)

        self.assertNotEqual(a.readlines(), b.readlines())


class INIDiffTestCase(CfgDiffTestCase):

    def test_ini_same(self):
        self._test_same(cfgdiff.INIDiff, './test/test_same_1-a.ini',
                        './test/test_same_1-b.ini')

    def test_ini_different(self):
        self._test_different(cfgdiff.INIDiff,
                             './test/test_different_1-a.ini',
                             './test/test_different_1-b.ini')


class JSONDiffTestCase(CfgDiffTestCase):

    def test_json_same(self):
        self._test_same(cfgdiff.JSONDiff, './test/test_same_1-a.json',
                        './test/test_same_1-b.json')

    def test_json_different(self):
        self._test_different(cfgdiff.JSONDiff,
                             './test/test_different_1-a.json',
                             './test/test_different_1-b.json')


@unittest.skipUnless('yaml' in cfgdiff.supported_formats, 'requires PyYAML')
class YAMLDiffTestcase(CfgDiffTestCase):

    def test_yaml_same(self):
        self._test_same(cfgdiff.YAMLDiff, './test/test_same_1-a.yaml',
                        './test/test_same_1-b.yaml')

    def test_yaml_different(self):
        self._test_different(cfgdiff.YAMLDiff,
                             './test/test_different_1-a.yaml',
                             './test/test_different_1-b.yaml')


@unittest.skipUnless('xml' in cfgdiff.supported_formats, 'requires LXML')
class XMLDiffTestCase(CfgDiffTestCase):

    def test_xml_same(self):
        self._test_same(cfgdiff.XMLDiff, './test/test_same_1-a.xml',
                        './test/test_same_1-b.xml')

    def test_xml_different(self):
        self._test_different(cfgdiff.XMLDiff,
                             './test/test_different_1-a.xml',
                             './test/test_different_1-b.xml')


@unittest.skipUnless('conf' in cfgdiff.supported_formats, 'requires ConfigObj')
class ConfigDiffTestCase(CfgDiffTestCase):

    def test_conf_same(self):
        self._test_same(cfgdiff.ConfigDiff, './test/test_same_1-a.ini',
                        './test/test_same_1-b.ini')

    def test_conf_different(self):
        self._test_different(cfgdiff.ConfigDiff,
                             './test/test_different_1-a.ini',
                             './test/test_different_1-b.ini')


@unittest.skipUnless('reconf' in cfgdiff.supported_formats,
                     'requires reconfigure')
class ReconfigureDiffTestCase(CfgDiffTestCase):

    def setUp(self):
        configs = __import__('reconfigure.configs', fromlist=['reconfigure'])
        self.parser = configs.SambaConfig

    @unittest.expectedFailure
    def test_reconf_same(self):
        self._test_same(cfgdiff.ReconfigureDiff,
                        './test/test_same_1-a.ini',
                        './test/test_same_1-b.ini', self.parser)

    def test_reconf_different(self):
        self._test_different(cfgdiff.ReconfigureDiff,
                             './test/test_different_1-a.ini',
                             './test/test_different_1-b.ini', self.parser)
