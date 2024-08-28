import shutil
from pathlib import Path

import pygit2

from app.models.metadata.metadata_factory import (
    _create_scenario_mod_from_rsc,
    _parse_basic,
    create_base_rules,
    create_listed_mod_from_path,
    create_mod_dependency,
    match_version,
    read_mods_config,
    read_rules_db,
    value_extractor,
    write_mods_config,
    write_rules_db,
)
from app.models.metadata.metadata_structure import (
    AboutXmlMod,
    CaseInsensitiveSet,
    CaseInsensitiveStr,
    ExternalRule,
    ExternalRulesSchema,
    ModType,
    SubExternalBoolRule,
    SubExternalRule,
)
from app.utils.xml import xml_path_to_json

RIMWORLD_PATH = Path("tests/data/mod_examples/RimWorld")
LOCAL_MODS_PATH = Path("tests/data/mod_examples/Local")
STEAM_WORKSHOP_PATH = Path("tests/data/mod_examples/Steam")


def test_value_extractor_string() -> None:
    # Test case: input is a string
    input_str = "Hello, World!"
    assert value_extractor(input_str) == input_str


def test_value_extractor_list() -> None:
    # Test case: input is a list
    input_list = ["apple", "banana", "cherry"]
    assert value_extractor(input_list) == input_list


def test_value_extractor_dict_li() -> None:
    # Test case: input is a dictionary with "li" key
    input_dict = {"li": ["apple", "banana", "cherry"]}
    assert value_extractor(input_dict) == input_dict["li"]


def test_value_extractor_dict_single_key() -> None:
    # Test case: input is a dictionary with single key
    input_dict = {"key": ["apple", "banana", "cherry"]}
    assert value_extractor(input_dict) == input_dict["key"]


def test_value_extractor_dict_string_value() -> None:
    # Test case: input is a dictionary string value
    input_dict = {"key": "apple"}
    assert value_extractor(input_dict) == input_dict["key"]


def test_value_extractor_dict_multiple_keys() -> None:
    # Test case: input is a dictionary with multiple keys
    input_dict = {"li": "value", "key2": "value2"}
    assert value_extractor(input_dict) == input_dict


def test_value_extractor_dict_li_one_value_list() -> None:
    # Test case: input is a dictionary with "li" key. Only one value list
    input_dict = {"li": ["apple"]}
    assert value_extractor(input_dict) == input_dict["li"]


def test_value_extractor_dict_li_one_value() -> None:
    # Test case: input is a dictionary with "li" key. Only one value
    input_dict = {"li": "apple"}
    assert value_extractor(input_dict) == input_dict["li"]


def test_value_extractor_ignore_if_no_matching_field() -> None:
    # Test case: Ignore if no matching field
    input_dict = {"@IgnoreIfNoMatchingField": "True", "#text": "input text"}
    assert value_extractor(input_dict) == input_dict["#text"]


def test__parse_required_ludeon_core() -> None:
    # Test parse required using data from data folder - Ludeon Core
    path = Path("tests/data/mod_examples/RimWorld/Data/Core/About/About.xml")
    mod_data = xml_path_to_json(str(path))["ModMetaData"]
    mod = _parse_basic(mod_data, AboutXmlMod())

    assert mod.package_id == "ludeon.rimworld"
    assert mod.authors == ["Ludeon Studios"]
    assert mod.steam_app_id == 294100
    assert mod.valid


def test__parse_required_ludeon_royalty() -> None:
    # Test parse required using data from data folder - Ludeon Royalty
    path = Path("tests/data/mod_examples/RimWorld/Data/Royalty/About/About.xml")
    mod_data = xml_path_to_json(str(path))["ModMetaData"]
    mod = _parse_basic(mod_data, AboutXmlMod())

    assert mod.package_id == "ludeon.rimworld.royalty"
    assert mod.authors == ["Ludeon Studios"]
    assert mod.steam_app_id == 1149640
    assert mod.supported_versions == {"1.5"}
    assert mod.valid


def test__parse_required_ludeon_biotech() -> None:
    # Test parse required using data from data folder - Ludeon Biotech
    path = Path("tests/data/mod_examples/RimWorld/Data/Biotech/About/About.xml")
    mod_data = xml_path_to_json(str(path))["ModMetaData"]
    mod = _parse_basic(mod_data, AboutXmlMod())

    assert mod.package_id == "ludeon.rimworld.biotech"
    assert mod.authors == ["Ludeon Studios"]
    assert mod.steam_app_id == 1826140
    assert mod.supported_versions == {"1.5"}
    assert mod.valid


def test__parse_required_future_dlc() -> None:
    # Test parse required using data from data folder - Future DLC (Unknown dlc not in constants). Has valid steam app id
    path = Path("tests/data/mod_examples/RimWorld/Data/FutureDLC/About/About.xml")
    mod_data = xml_path_to_json(str(path))["ModMetaData"]
    mod = _parse_basic(mod_data, AboutXmlMod())

    assert mod.supported_versions == {"1.999999", "3.141"}
    assert mod.valid


def test__parse_required_local_fishery() -> None:
    # Test case: Fishery mod
    path = Path("tests/data/mod_examples/Local/Fishery/About/About.xml")
    mod_data = xml_path_to_json(str(path))["ModMetaData"]
    mod = _parse_basic(mod_data, AboutXmlMod())

    assert isinstance(mod, AboutXmlMod)
    assert mod.package_id == "bs.fishery"
    assert mod.name == "Fishery - Modding Library"
    assert mod.authors == ["bradson"]
    assert mod.supported_versions == {"1.2", "1.3", "1.4", "1.5"}
    assert mod.valid


def test_match_version_found() -> None:
    # Test case: matching key is found
    input_dict = {"v1.2": "value1", "v1.3": "value2", "v1.4": "value3"}
    target_version = "1.3"
    assert match_version(input_dict, target_version) == (True, ["value2"])


def test_match_version_not_found() -> None:
    # Test case: matching key is not found
    input_dict = {"v1.2": "value1", "v1.3": "value2", "v1.4": "value3"}
    target_version = "1.5"
    assert match_version(input_dict, target_version) == (False, None)


def test_match_version_multiple_results() -> None:
    # Test case: multiple matching keys are found
    input_dict = {"v1.2": "value1", "v1.3": "value2", "v1.3.1": "value3"}
    target_version = "1.3"
    assert match_version(input_dict, target_version) == (True, ["value2", "value3"])


def test_match_version_multiple_results_stop_at_first() -> None:
    # Test case: stop_at_first parameter is set to True
    input_dict = {"v1.2": "value1", "v1.3": "value2", "v1.3.1": "value3"}
    target_version = "1.3"
    assert match_version(input_dict, target_version, stop_at_first=True) == (
        True,
        ["value2"],
    )


def test_create_mod_dependency() -> None:
    # Test case: valid input dictionary
    input_dict = {
        "packageId": "com.example.mod",
        "displayName": "Example Mod",
        "workshopUrl": "https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890",
    }
    mod = create_mod_dependency(input_dict)
    assert mod.package_id == "com.example.mod"
    assert mod.name == "Example Mod"
    assert (
        mod.workshop_url
        == "https://steamcommunity.com/sharedfiles/filedetails/?id=1234567890"
    )


def test_create_mod_dependency_missing_fields() -> None:
    # Test case: missing fields in the input dictionary
    input_dict = {"packageId": "com.example.mod"}
    mod = create_mod_dependency(input_dict)
    assert mod.package_id == "com.example.mod"
    assert mod.name == "Unknown Mod Name"
    assert mod.workshop_url == ""


def test_create_base_rules_ludeon_core() -> None:
    # Test case: Ludeon Core
    path = Path("tests/data/mod_examples/RimWorld/Data/Core/About/About.xml")
    mod_data = xml_path_to_json(str(path))["ModMetaData"]
    rules = create_base_rules(mod_data, "1.5")

    assert rules.dependencies == {}
    assert rules.load_before == CaseInsensitiveSet(
        {"ludeon.rimworld.ideology", "ludeon.rimworld.royalty"}
    )
    assert rules.load_after == CaseInsensitiveSet()


def test_get_rules_db_large_db() -> None:
    path = Path("tests/data/dbs/large_rules.json")
    _ = read_rules_db(path)


def test_get_rules_db_values() -> None:
    path = Path("tests/data/dbs/userRules.json")
    rules = read_rules_db(path)

    expected_value = ExternalRulesSchema(
        timestamp=1715795801,
        rules={
            "test.test1": ExternalRule(
                loadAfter={},
                loadBefore={
                    "a.a": SubExternalRule(name="AA", comment="test1 load before"),
                    "b.b": SubExternalRule(name="aa", comment="test2 load before"),
                    "c.c.core": SubExternalRule(name="test3", comment=""),
                },
                loadTop=SubExternalBoolRule(False),
                loadBottom=SubExternalBoolRule(),
            ),
            "test.test2": ExternalRule(
                loadAfter={
                    "a.a": SubExternalRule(name="AA", comment="test1 load before"),
                    "b.b": SubExternalRule(name="aa", comment="test2 load before"),
                    "c.c.core": SubExternalRule(name="test3", comment=""),
                },
                loadBefore={},
                loadTop=SubExternalBoolRule(False),
                loadBottom=SubExternalBoolRule(value=True, comment="It is known."),
            ),
        },
    )

    assert rules == expected_value


def test_write_rules_db(tmp_path: Path) -> None:
    path = tmp_path / "test.json"
    rules = ExternalRulesSchema(
        timestamp=1715795801,
        rules={
            "test.test1": ExternalRule(
                loadAfter={},
                loadBefore={
                    "a.a": SubExternalRule(name="AA", comment="test1 load before"),
                    "b.b": SubExternalRule(name="aa", comment="test2 load before"),
                    "c.c.core": SubExternalRule(name="test3", comment=""),
                },
                loadTop=SubExternalBoolRule(False),
                loadBottom=SubExternalBoolRule(),
            ),
            "test.test2": ExternalRule(
                loadAfter={
                    "a.a": SubExternalRule(name="AA", comment="test1 load before"),
                    "b.b": SubExternalRule(name="aa", comment="test2 load before"),
                    "c.c.core": SubExternalRule(name="test3", comment=""),
                },
                loadBefore={},
                loadTop=SubExternalBoolRule(False),
                loadBottom=SubExternalBoolRule(value=True, comment="It is known."),
            ),
        },
    )

    write_rules_db(path, rules)

    new_rules = read_rules_db(path)
    assert rules == new_rules


def test_create_scenario_mod_from_rsc_invalid_meta() -> None:
    path = Path(
        "tests/data/mod_examples/Local/invalid_scenario_mod_meta/scenario abc.rsc"
    )

    valid, mod = _create_scenario_mod_from_rsc(path.parent, path)

    assert not valid
    assert not mod.valid


def test_create_scenario_mod_from_rsc_invalid_scenario() -> None:
    path = Path(
        "tests/data/mod_examples/Local/invalid_scenario_mod_scenario/scenario abc.rsc"
    )

    valid, mod = _create_scenario_mod_from_rsc(path.parent, path)

    assert not valid
    assert not mod.valid


def test_create_scenario_mod_from_rsc_valid() -> None:
    path = Path("tests/data/mod_examples/Local/scenario_mod_1/scenario abc.rsc")

    valid, mod = _create_scenario_mod_from_rsc(path.parent, path)

    assert valid
    assert mod.valid

    assert mod.supported_versions == {"1.2.2900 rev837"}
    assert mod.name == "Name"
    assert mod.summary == "Summary"
    assert mod.description == "Description"


def test_create_listed_mod_from_path_invalid_folder() -> None:
    path = Path("tests/data/mod_examples/Local/invalid folder")

    valid, mod = create_listed_mod_from_path(
        path, "1.5", LOCAL_MODS_PATH, RIMWORLD_PATH, STEAM_WORKSHOP_PATH
    )

    assert not valid
    assert not mod.valid
    assert mod.mod_type == ModType.LOCAL


def test_create_listed_mod_from_path_fishery(tmp_path: Path) -> None:
    path = Path("tests/data/mod_examples/Local/Fishery")
    # Copy entierty of path to temporary folder
    shutil.copytree(path, tmp_path / path)

    # Init temp git repo
    _ = pygit2.init_repository(str(tmp_path / path), False)

    path = tmp_path / path

    valid, mod = create_listed_mod_from_path(
        path,
        "1.5",
        tmp_path / LOCAL_MODS_PATH,
        tmp_path / RIMWORLD_PATH,
        tmp_path / STEAM_WORKSHOP_PATH,
    )
    assert valid
    assert mod.valid

    assert isinstance(mod, AboutXmlMod)
    assert mod.package_id == "bs.fishery"
    assert mod.name == "Fishery - Modding Library"
    assert mod.authors == ["bradson"]
    assert mod.supported_versions == {"1.2", "1.3", "1.4", "1.5"}
    assert mod.mod_type == ModType.GIT


def test_read_mod_config_valid_1(tmp_path: Path) -> None:
    path = Path("tests/data/modconfigs/valid_1/ModConfig.xml")
    shutil.copytree(path.parent, tmp_path / path.parent)
    path = tmp_path / path

    mods_config = read_mods_config(path)

    assert mods_config is not None
    assert len(mods_config.activeMods) == 7
    assert len(mods_config.knownExpansions) == 4
    assert mods_config.version == "1.5.4104 rev435"


def test_read_write_mod_config_valid_1(tmp_path: Path) -> None:
    path = Path("tests/data/modconfigs/valid_1/ModConfig.xml")
    shutil.copytree(path.parent, tmp_path / path.parent)
    path = tmp_path / path

    mods_config = read_mods_config(path)

    assert mods_config is not None
    am = mods_config.activeMods
    ke = mods_config.knownExpansions

    am.append(CaseInsensitiveStr("test"))
    ke.append(CaseInsensitiveStr("testke"))

    write_mods_config(path, mods_config)
    new_mods_config = read_mods_config(path)

    assert new_mods_config is not None
    assert len(new_mods_config.activeMods) == len(mods_config.activeMods)
    assert len(new_mods_config.knownExpansions) == len(mods_config.knownExpansions)
    assert new_mods_config.activeMods == mods_config.activeMods
    assert new_mods_config.knownExpansions == mods_config.knownExpansions
    assert new_mods_config.version == mods_config.version
    assert am != new_mods_config.activeMods
    assert ke != new_mods_config.knownExpansions
    assert "test" not in new_mods_config.activeMods
    assert "testke" not in new_mods_config.knownExpansions

    mods_config.activeMods = am
    mods_config.knownExpansions = ke

    success = write_mods_config(path, mods_config)
    assert success
    new_mods_config_1 = read_mods_config(path)

    assert new_mods_config_1 is not None
    assert len(new_mods_config_1.activeMods) == len(mods_config.activeMods)
    assert len(new_mods_config_1.knownExpansions) == len(mods_config.knownExpansions)
    assert new_mods_config_1.activeMods == am
    assert new_mods_config_1.knownExpansions == ke
    assert new_mods_config_1.version == mods_config.version


def test_read_mod_config_invalid_1() -> None:
    path = Path("tests/data/modconfigs/invalid_1/ModConfig.xml")
    mods_config = read_mods_config(path)

    assert mods_config is None


def test_read_mod_config_invalid_2() -> None:
    path = Path("tests/data/modconfigs/invalid_2/ModConfig.xml")
    mods_config = read_mods_config(path)

    assert mods_config is None


def test_read_mod_config_invalid_3() -> None:
    path = Path("tests/data/modconfigs/invalid_3/ModConfig.xml")
    mods_config = read_mods_config(path)

    assert mods_config is None
