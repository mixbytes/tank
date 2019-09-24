import copy
import tempfile

import pytest

from tank.core.exc import TankTestCaseError
from tank.core import testcase as tc
from tank.core.regions import RegionsConfig
from tank.core.utils import yaml_dump
from tank.main import MixbytesTank


content = {
    'binding': 'polkadot',
    'instances': {
        'type': 'standard',
        'packetloss': 10,

        'boot': {
            'count': 1,
            'type': 'large',
            'packetloss': 5,
        },

        'producer': 1,

        'test': {
            'count': 1,
        },

        'name': {
            'type': 'small',
            'packetloss': 3,
            'count': 6,
            'regions': {
                'Europe': {
                    'count': 1,
                    'type': 'large',
                    'packetloss': 15,
                },
                'Asia': {
                    'count': 1,
                    'type': 'standard',
                },
                'NorthAmerica': 1,
                'random': {
                    'type': 'standard',
                    'count': 3,
                },
            }
        }
    },
    'ansible': {
        'forks': 50,
    },
}


class TestTestcaseValidation:
    """Tests class for TestCaseValidator class."""

    def _test(self, raises = None):
        if raises:
            with pytest.raises(raises):
                tc.TestCaseValidator(self._content, 'filename').validate()
        else:
            tc.TestCaseValidator(self._content, 'filename').validate()

    def setup(self):
        self._content = copy.deepcopy(content)

    def test_invalid_keys(self):
        self._content['invalid'] = 0
        self._test(raises=TankTestCaseError)

    def test_required_keys(self):
        self._content.pop('instances')
        self._test(raises=TankTestCaseError)

    def test_reserved_names_check(self):
        self._content['instances']['monitoring'] = 1
        self._test(raises=TankTestCaseError)

    def test_counts_equality_check(self):
        self._test()  # test on valid

        self._content['instances']['name']['count'] = 1
        self._test(raises=TankTestCaseError)

    def test_invalid_configuration(self):
        self._content['instances']['new'] = 'string'
        self._test(raises=TankTestCaseError)

    def test_invalid_count(self):
        self._content['instances']['new'] = -100
        self._test(raises=TankTestCaseError)

    def test_invalid_packetloss(self):
        self._content['instances']['name']['packetloss'] = 120
        self._test(raises=TankTestCaseError)

    def test_invalid_type(self):
        self._content['instances']['type'] = 'a'
        self._test(raises=TankTestCaseError)

    def test_invalid_region(self):
        self._content['instances']['name']['regions']['a'] = 1
        self._test(raises=TankTestCaseError)

    def test_valid_testcase(self):
        self._test()


class TestInstancesCanonizer:
    """Tests class for InstancesCanonizer class."""

    def _test(self, content: dict, expected: dict):
        canonized = tc.InstancesCanonizer(content).canonize()
        assert canonized == expected

    def test_integer_config_canonization(self):
        content = {
            'role': 10,
        }

        expected = {
            'role': {
                'default': {
                    'type': tc.InstancesCanonizer._GENERAL_OPTIONS['type'],
                    'packetloss': tc.InstancesCanonizer._GENERAL_OPTIONS['packetloss'] / 100,
                    'count': content['role'],
                },
            },
        }

        self._test(content, expected)

    def test_minimal_object_config_canonization(self):
        content = {
            'role': {
                'count': 10,
            }
        }

        expected = {
            'role': {
                'default': {
                    'type': tc.InstancesCanonizer._GENERAL_OPTIONS['type'],
                    'packetloss': tc.InstancesCanonizer._GENERAL_OPTIONS['packetloss'] / 100,
                    'count': content['role']['count'],
                },
            },
        }

        self._test(content, expected)

    def test_generally_applicable_options_applying(self):
        content = {
            'type': 'large',
            'packetloss': 50,

            'role': 10,
        }

        expected = {
            'role': {
                'default': {
                    'type': content['type'],
                    'packetloss': content['packetloss'] / 100,
                    'count': content['role'],
                },
            },
        }

        self._test(content, expected)

    def test_full_object_config_canonization(self):
        content = {
            'role': {
                'type': 'small',
                'packetloss': 3,
                'count': 2,

                'regions': {
                    'Europe': {
                        'count': 1,
                        'type': 'large',
                        'packetloss': 15,
                    },
                    'Asia': 1,
                },
            },
        }

        expected = {
            'role': {
                'Europe': {
                    'count': content['role']['regions']['Europe']['count'],
                    'type': content['role']['regions']['Europe']['type'],
                    'packetloss': content['role']['regions']['Europe']['packetloss'] / 100,
                },
                'Asia': {
                    'count': content['role']['regions']['Asia'],
                    'type': content['role']['type'],
                    'packetloss': content['role']['packetloss'] / 100,
                },
            },
        }

        self._test(content, expected)


class TestRegionsConverter:
    """Tests class for RegionsConverter class."""

    def _find_configuration(self, target: dict, container: list) -> bool:
        for configuration in container:
            if all(configuration[param] == target[param] for param in tc.RegionsConverter._GROUP_PARAMETERS):
               return True

        return False

    def _test(self, content: dict, expected: dict):
        converted = self._converter.convert(content)
        assert len(converted) == len(expected)

        for role, configurations in converted.items():
            assert role in expected.keys()
            for cfg in configurations:
                assert self._find_configuration(cfg, expected[role])

    def setup_class(self):
        with MixbytesTank() as app:
            self._regions_config = RegionsConfig(app).config
            self._provider = app.provider
            self._converter = tc.RegionsConverter(app)

    def test_convert_regions(self):
        content = {
            'role': {
                'Europe': {
                    'count': 1,
                    'type': 'small',
                    'packetloss': 0,
                },
                'Asia': {
                    'count': 1,
                    'type': 'small',
                    'packetloss': 0,
                },
            }
        }

        expected = {
            'role': [
                {
                    'region': self._regions_config[self._provider]['Europe'],
                    **content['role']['Europe'],
                },
                {
                    'region': self._regions_config[self._provider]['Asia'],
                    **content['role']['Asia'],
                },
            ]
        }

        self._test(content, expected)

    def test_merging_configurations(self):
        content = {
            'role': {
                'random': {
                    'count': 3,
                    'type': 'small',
                    'packetloss': 0,
                },
                'Asia': {
                    'count': 1,
                    'type': 'small',
                    'packetloss': 0,
                },
            }
        }

        expected = {
            'role': [
                {
                    'region': self._regions_config[self._provider]['NorthAmerica'],
                    'count': 1,
                    'type': content['role']['random']['type'],
                    'packetloss': content['role']['random']['packetloss'],
                },
                {
                    'region': self._regions_config[self._provider]['Asia'],
                    'count': 2,
                    'type': content['role']['random']['type'],
                    'packetloss': content['role']['random']['packetloss'],
                },
                {
                    'region': self._regions_config[self._provider]['Europe'],
                    'count': 1,
                    'type': content['role']['random']['type'],
                    'packetloss': content['role']['random']['packetloss'],
                },
            ]
        }

        self._test(content, expected)


class TestTestcaseClass:
    """Tests class for TestCase class."""

    def setup_class(self):
        testcase_file = tempfile.NamedTemporaryFile()
        yaml_dump(testcase_file.name, data=content)

        with MixbytesTank() as app:
            self._testcase = tc.TestCase(testcase_file.name, app)  # test for initialization is here

    def test_total_instances(self):
        assert self._testcase.total_instances == 9

    def test_binding(self):
        assert self._testcase.binding == content['binding']
