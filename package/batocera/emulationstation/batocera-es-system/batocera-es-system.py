#
# - Generates the es_systems.cfg file
# - Generates roms folder and emulators folders
# - Generate the _info.txt file with the emulator information
# - Information from the emulators are being extracted from the file es_system.yml
#

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import OrderedDict
from pathlib import Path
from typing import Final, NotRequired, Required, cast
from typing_extensions import TypedDict, TypeForm

import yaml

from batocera_es_system_shared import (
    MISSING,
    CoreDict,
    DefaultDict,
    SystemDict,
    get_deep_value,
    is_arch_valid,
    is_valid_requirements,
    safe_load_yaml,
)

# es_features.yml definitions


class _CFeatureBaseDict(TypedDict, total=False):
    prompt: Required[str]
    description: str
    group: str
    submenu: str
    order: int
    archs_include: list[str]
    archs_exclude: list[str]


class _CFeaturePresetDict(_CFeatureBaseDict):
    preset: Required[str]
    preset_parameters: str


class _CFeatureChoicesDict(_CFeatureBaseDict):
    choices: Required[dict[str, str | int | bool | None]]


type _CFeatureDict = _CFeaturePresetDict | _CFeatureChoicesDict


class _FeatureDict(TypedDict, total=False):
    features: list[str]  # List of feature names
    shared: list[str]  # Shared features to include
    cfeatures: dict[str, _CFeatureDict]  # Explicit feature whitelist
    cores: dict[str, _FeatureDict]
    systems: dict[str, _FeatureDict]


class _SystemFeaturesDict(TypedDict):
    cfeatures: dict[str, _CFeatureDict]


_Features = TypedDict('_Features', {'shared': _SystemFeaturesDict, 'global': _FeatureDict}, extra_items=_FeatureDict)


class _CommentDict(TypedDict):
    emulator: str
    core: NotRequired[str]


_DEFAULT_PARENTPATH: Final = '/userdata/roms'
_DEFAULT_COMMAND: Final = 'emulatorlauncher %CONTROLLERSCONFIG% -system %SYSTEM% -rom %ROM% -gameinfoxml %GAMEINFOXML% -systemname %SYSTEMNAME%'


def _ordered_load[T](
    file: Path,
    type: TypeForm[T],
    Loader: type[yaml.Loader] = yaml.Loader,
    object_pairs_hook: type[OrderedDict[str, object]] = OrderedDict,
) -> T:
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader: yaml.Loader, node: yaml.MappingNode) -> OrderedDict[str, object]:
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))  # pyright: ignore

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(file.read_text(), OrderedLoader)


# Generate the es_systems.cfg file by searching the information in the es_system.yml file
def _generate_all(
    rulesYaml: Path,
    featuresYaml: Path,
    configFile: Path,
    esSystemFile: Path,
    esFeaturesFile: Path,
    esTranslationFile: Path,
    esKeysTranslationFile: Path,
    esKeysParentFolder: Path,
    esBlacklistedWordsFile: Path,
    systemsConfigFile: Path,
    archSystemsConfigFile: Path,
    romsdirsource: Path,
    romsdirtarget: Path,
    arch: str,
    /,
) -> None:
    rules = safe_load_yaml(rulesYaml, dict[str, SystemDict])
    config = _load_config(configFile)
    es_system: list[str] = [
        '<?xml version="1.0"?>',
        '<systemList>',
    ]

    archSystemsConfig = safe_load_yaml(archSystemsConfigFile, dict[str, DefaultDict] | None)
    if archSystemsConfig is None:
        archSystemsConfig = {}
    systemsConfig = safe_load_yaml(systemsConfigFile, dict[str, DefaultDict])

    # sort to be determinist
    sortedRules = sorted(rules.items(), key=lambda x: x[0])

    print(f'generating the {esSystemFile} file...')
    for system, system_def in sortedRules:
        # compute default emulator/cores
        defaultCore: str | None = None
        defaultEmulator: str | None = None

        if (archEmulator := get_deep_value(archSystemsConfig, system, 'emulator')) is not MISSING:
            defaultEmulator = archEmulator
        elif (systemsEmulator := get_deep_value(systemsConfig, system, 'emulator')) is not MISSING:
            defaultEmulator = systemsEmulator

        if (archCore := get_deep_value(archSystemsConfig, system, 'core')) is not MISSING:
            defaultCore = archCore
        elif (systemsCore := get_deep_value(systemsConfig, system, 'core')) is not MISSING:
            defaultCore = systemsCore

        es_system.extend(_generate_system(system, system_def, config, defaultEmulator, defaultCore, arch))

    es_system.extend(['</systemList>', ''])

    esSystemFile.write_text('\n'.join(es_system))

    toTranslateOnArch: dict[str | None, list[_CommentDict]] = {}
    _create_es_features(featuresYaml, rules, esFeaturesFile, arch, toTranslateOnArch)
    toTranslate = _find_translations(featuresYaml)

    # remove blacklisted words
    with esBlacklistedWordsFile.open() as fp:
        for line in fp:
            line = line.rstrip('\n')
            if line in toTranslate:
                del toTranslate[line]
    ###

    _create_es_translations(esTranslationFile, toTranslate)
    _create_es_keys_translations(esKeysTranslationFile, esKeysParentFolder)

    print(f'removing the {romsdirtarget} folder...')
    if romsdirtarget.is_dir():
        shutil.rmtree(romsdirtarget)
    print(f'generating the {romsdirtarget} folder...')
    for system, system_def in sortedRules:
        if system_def:
            if _need_folder(system, system_def, config, arch):
                _create_folders(system, system_def, romsdirsource, romsdirtarget)
                _info_system(system, system_def, romsdirtarget)
            else:
                print(f'skipping directory for system {system}')


# check if the folder is required
def _need_folder(system: str, data: SystemDict, config: dict[str, int], arch: str, /) -> bool:
    # no emulator
    if 'emulators' not in data:
        return False

    for emulator in sorted(data['emulators']):
        emulatorData = data['emulators'][emulator]

        if not is_arch_valid(arch, emulatorData):
            continue

        core_keys = [key for key in emulatorData if key not in ['archs_include', 'archs_exclude']]

        for core in sorted(core_keys):
            coreData = cast('CoreDict', emulatorData[core])

            if (
                'requireAnyOf' in coreData
                and is_arch_valid(arch, coreData)
                and is_valid_requirements(config, coreData['requireAnyOf'])
            ):
                return True

    return False


# Loads the .config file
def _load_config(configFile: Path, /) -> dict[str, int]:
    config: dict[str, int] = {}
    with configFile.open() as fp:
        for line in fp:
            m = re.search('^([^ ]+)=y$', line)
            if m:
                config[m.group(1)] = 1
    return config


# Generate emulator system
def _generate_system(
    system: str,
    data: SystemDict,
    config: dict[str, int],
    defaultEmulator: str | None,
    defaultCore: str | None,
    arch: str,
    /,
) -> list[str]:
    emulators_txt = _list_emulators(data, config, defaultEmulator, defaultCore, arch)
    if not emulators_txt and not data.get('force'):
        return []

    pathValue = _system_path(system, data)
    platformValue = _system_platform(system, data)
    listExtensions = _list_extension(data, False)
    groupValue = _system_group(system, data)
    command = _command_name(data)

    system_txt: list[str] = [
        '  <system>',
        f'        <fullname>{_protect_xml(data["name"])}</fullname>',
        f'        <name>{system}</name>',
        f'        <manufacturer>{_protect_xml(data["manufacturer"])}</manufacturer>',
        f'        <release>{_protect_xml(data["release"])}</release>',
        f'        <hardware>{_protect_xml(data["hardware"])}</hardware>',
    ]
    if listExtensions:
        if pathValue:
            system_txt.append(f'        <path>{pathValue}</path>')
        system_txt.extend(
            [
                f'        <extension>{listExtensions}</extension>',
                f'        <command>{command}</command>',
            ]
        )
    if platformValue:
        system_txt.append(f'        <platform>{_protect_xml(platformValue)}</platform>')
    system_txt.append(f'        <theme>{_theme_name(system, data)}</theme>')
    if groupValue:
        system_txt.append(f'        <group>{_protect_xml(groupValue)}</group>')

    system_txt.extend([*emulators_txt, '  </system>'])

    return system_txt


# Returns the path to the rom folder for the emulator
def _system_path(system: str, data: SystemDict, /) -> str:
    if 'path' in data:
        if data['path'] is None:
            return ''
        if data['path'][0] == '/':  # absolute path
            return data['path']
        return _DEFAULT_PARENTPATH + '/' + data['path']
    return _DEFAULT_PARENTPATH + '/' + system


def _system_sub_roms_dir(system: str, data: SystemDict, /) -> str | None:
    if 'path' in data:
        if data['path'] is None:
            return None  # no path to create
        if data['path'][0] == '/':  # absolute path
            return None  # don't create absolute paths
        return data['path']
    return system


# Returns the path to the rom folder for the emulator
def _system_platform(system: str, data: SystemDict, /) -> str:
    if 'platform' in data:
        if data['platform'] is None:
            return ''
        return data['platform']
    return system


# Some emulators have different names between roms and themes
def _theme_name(system: str, data: SystemDict, /) -> str:
    if 'theme' in data:
        return data['theme']
    return system


# In case you need to specify a different command line
def _command_name(data: SystemDict, /) -> str | None:
    return data.get('command', _DEFAULT_COMMAND)


# Create the folders of the consoles in the roms folder
def _create_folders(system: str, data: SystemDict, romsdirsource: Path, romsdirtarget: Path, /) -> None:
    subdir = _system_sub_roms_dir(system, data)

    # nothing to create
    if subdir is None:
        return

    roms_target_subdir = romsdirtarget / subdir
    if not roms_target_subdir.is_dir():
        roms_target_subdir.mkdir(parents=True)

        roms_source_subdir = romsdirsource / subdir
        # copy from the template one, or just keep it empty
        if roms_source_subdir.is_dir():
            roms_target_subdir.rmdir()  # remove the last level
            shutil.copytree(roms_source_subdir, roms_target_subdir)


# Creates an _info.txt file inside the emulators folders in roms with the information of the supported extensions.
def _info_system(system: str, data: SystemDict, romsdir: Path, /) -> None:
    subdir = _system_sub_roms_dir(system, data)

    # nothing to create
    if subdir is None:
        return

    infoTxt = f'## SYSTEM {data["name"].upper()} ##\n'
    infoTxt += '-------------------------------------------------------------------------------\n'
    infoTxt += f'ROM files extensions accepted: "{_list_extension(data, False)}"\n'
    if 'comment_en' in data:
        infoTxt += '\n' + data['comment_en']
    infoTxt += '-------------------------------------------------------------------------------\n'
    infoTxt += f'Extensions des fichiers ROMs permises: "{_list_extension(data, False)}"\n'
    if 'comment_fr' in data:
        infoTxt += '\n' + data['comment_fr']

    arqtxt = romsdir / subdir / '_info.txt'

    arqtxt.write_text(infoTxt)


# generate the fake translations from *.keys files
def _create_es_keys_translations(esKeysTranslationFile: Path, esKeysParentFolder: Path, /) -> None:
    print(f'generating {esKeysTranslationFile}...')
    files = esKeysParentFolder.glob('**/*.keys')
    vals: dict[str, set[str]] = {}
    for file in files:
        print(f'... {file}')
        content = json.loads(file.read_text())
        for device in content:
            for action in content[device]:
                if 'description' in action:
                    if action['description'] not in vals:
                        vals[action['description']] = {file.name}
                    else:
                        vals[action['description']].add(file.name)

    fd = esKeysTranslationFile.open('w')
    fd.write("// file generated automatically by batocera-es-system.py, don't modify it\n\n")
    n = 0
    for tr in vals:
        vcomment = ''
        vn = 0
        for v in sorted(vals[tr]):
            if vn < 5:
                if vcomment != '':
                    vcomment = vcomment + ', '
                vcomment = vcomment + v
            else:
                if vn == 5:
                    vcomment = vcomment + ', ...'
            vn = vn + 1
        fd.write('/* TRANSLATION: ' + vcomment + ' */\n')
        fd.write(
            '#define fake_gettext_external_' + str(n) + ' pgettext("keys_files", "' + tr.replace('"', '\\"') + '")\n'
        )
        n = n + 1
    fd.close()


# generate the fake translations from external options
def _create_es_translations(esTranslationFile: Path, toTranslate: dict[str | None, list[_CommentDict]], /) -> None:
    if not toTranslate:
        return
    with esTranslationFile.open('w') as fd:
        n = 1
        fd.write("// file generated automatically by batocera-es-system.py, don't modify it\n\n")
        for tr in toTranslate:
            # skip if tr is None
            if tr is None:
                continue
            # skip empty string
            if tr == '':
                continue
            # skip numbers (8, 10, 500+)
            m = re.search('^[0-9]+[+]?$', tr)
            if m:
                continue
            # skip floats (2.5)
            m = re.search('^[0-9]+\\.[0-9]+[+]?$', tr)
            if m:
                continue
            # skip ratio (4:3)
            m = re.search('^[0-9]+:[0-9]+$', tr)
            if m:
                continue
            # skip ratio (4/3)
            m = re.search('^[0-9]+/[0-9]+$', tr)
            if m:
                continue
            # skip numbers (100%, 3x, +50%)
            m = re.search('^[+-]?[0-9]+[%x]?$', tr)
            if m:
                continue
            # skip resolutions (640x480)
            m = re.search('^[0-9]+x[0-9]+$', tr)
            if m:
                continue
            # skip resolutions (2x 640x480, 4x (640x480), x4 640x480, 3x 1080p (1920x1584), 2x 720p, 7x 2880p 5K
            m = re.search('^[xX]?[0-9]*[xX]?[ ]*\\(?[0-9]+[x]?[0-9]+[pK]?\\)?[ ]*\\(?[0-9]+[x]?[0-9]+[pK]?\\)?$', tr)
            if m:
                continue

            vcomment = ''
            vn = 0
            vincomment = {}
            for v in sorted(toTranslate[tr], key=lambda x: x['emulator'] + ('/' + x['core'] if 'core' in x else '')):
                vword = None
                if 'core' not in v or v['emulator'] == v['core']:
                    vword = v['emulator']
                else:
                    vword = v['emulator'] + '/' + v['core']

                if vn < 5:
                    if vword not in vincomment:  # not already set in comment
                        if vcomment != '':
                            vcomment = vcomment + ', '
                        vincomment[vword] = True
                        vcomment = vcomment + vword
                        vn = vn + 1
                else:
                    # add ... if there are some other values
                    if vn == 5 and vword not in vincomment:  # not already set in comment
                        vcomment = vcomment + ', ...'
                        vn = vn + 1
            fd.write('/* TRANSLATION: ' + vcomment + ' */\n')
            fd.write(
                '#define fake_gettext_external_'
                + str(n)
                + ' pgettext("game_options", "'
                + tr.replace('"', '\\"')
                + '")\n'
            )
            n = n + 1


def _protect_xml(strval: object, /) -> str:
    strval = str(strval)
    strval = strval.replace('&', '&amp;')
    strval = strval.replace('<', '&lt;')
    strval = strval.replace('>', '&gt;')
    strval = strval.replace('"', '&quot;')
    return strval.replace('\n', '&#x0a;')


def _add_comment_to_dict_key(
    dictvar: dict[str | None, list[_CommentDict]], dictval: str | None, comment: _CommentDict, /
) -> None:
    if dictval not in dictvar:
        dictvar[dictval] = []
    dictvar[dictval].append(comment)


def _get_xml_feature(
    nfspaces: int,
    key: str,
    infos: _CFeatureDict,
    toTranslate: dict[str | None, list[_CommentDict]],
    emulator: str,
    core: str | None,
    /,
) -> list[str]:
    fspaces = ' ' * nfspaces
    lines: list[str] = []
    description = infos.get('description', '')
    submenustr = f' submenu="{_protect_xml(infos["submenu"])}"' if 'submenu' in infos else ''
    groupstr = f' group="{_protect_xml(infos["group"])}"' if 'group' in infos else ''
    orderstr = f' order="{_protect_xml(infos["order"])}"' if 'order' in infos else ''
    presetstr = ''
    if 'preset' in infos:
        presetstr = f' preset="{_protect_xml(infos["preset"])}"'
    if 'preset_parameters' in infos:
        presetstr += f' preset-parameters="{_protect_xml(infos["preset_parameters"])}"'

    lines.append(
        f'{fspaces}<feature name="{_protect_xml(infos["prompt"])}"{submenustr}{groupstr}{orderstr} value="{
            _protect_xml(key)
        }" description="{_protect_xml(description)}"{presetstr}>'
    )

    comment: _CommentDict = {'emulator': emulator}
    if core is not None:
        comment['core'] = core

    _add_comment_to_dict_key(toTranslate, infos['prompt'], comment)
    _add_comment_to_dict_key(toTranslate, description, comment.copy())
    if 'preset' not in infos:
        for choice in infos['choices']:
            lines.append(
                f'{fspaces}  <choice name="{_protect_xml(choice)}" value="{_protect_xml(infos["choices"][choice])}" />'
            )
            _add_comment_to_dict_key(toTranslate, choice, comment.copy())
    lines.append(f'{fspaces}</feature>')
    return lines


def _array_to_comma_string(arr: list[str] | None, /) -> str:
    return '' if arr is None else ', '.join([item for item in arr if item])


# Write the information in the es_features.cfg file
def _create_es_features(
    featuresYaml: Path,
    systems: dict[str, SystemDict],
    esFeaturesFile: Path,
    arch: str,
    toTranslate: dict[str | None, list[_CommentDict]],
    /,
) -> None:
    features = _ordered_load(featuresYaml, _Features)
    features_lines: list[str] = ['<?xml version="1.0" encoding="UTF-8" ?>', '<features>']
    for emulator, emulator_def in features.items():
        emulator_featuresTxt = _array_to_comma_string(emulator_def.get('features'))
        if emulator == 'global':
            features_lines.append('  <globalFeatures')
        elif emulator == 'shared':
            features_lines.append('  <sharedFeatures')
        else:
            features_lines.append(
                f'  <emulator name="{_protect_xml(emulator)}" features="{_protect_xml(emulator_featuresTxt)}"'
            )

        if (
            'cores' in emulator_def
            or 'systems' in emulator_def
            or 'cfeatures' in emulator_def
            or 'shared' in emulator_def
        ):
            features_lines[-1] += '>'
            if 'cores' in emulator_def:
                emulator_cores = emulator_def['cores']
                features_lines.append('    <cores>')
                for core, core_def in emulator_cores.items():
                    core_featuresTxt = _array_to_comma_string(core_def.get('features'))
                    if 'cfeatures' in core_def or 'shared' in core_def or 'systems' in core_def:
                        features_lines.append(
                            f'      <core name="{_protect_xml(core)}" features="{_protect_xml(core_featuresTxt)}">'
                        )
                        if 'shared' in core_def:
                            features_lines.extend(
                                f'        <sharedFeature value="{_protect_xml(shared)}" />'
                                for shared in core_def['shared']
                                if is_arch_valid(arch, features['shared']['cfeatures'][shared])
                            )
                        # core features
                        if 'cfeatures' in core_def:
                            for cfeature, cfeature_def in core_def['cfeatures'].items():
                                if is_arch_valid(arch, cfeature_def):
                                    features_lines.extend(
                                        _get_xml_feature(8, cfeature, cfeature_def, toTranslate, emulator, core)
                                    )
                                else:
                                    print('skipping core ' + emulator + '/' + core + ' cfeature ' + cfeature)
                        # #############

                        # systems in cores/core
                        if 'systems' in core_def:
                            features_lines.append('        <systems>')
                            for system, system_def in core_def['systems'].items():
                                system_featuresTxt = _array_to_comma_string(system_def.get('features'))
                                features_lines.append(
                                    f'          <system name="{_protect_xml(system)}" features="{_protect_xml(system_featuresTxt)}" >'
                                )
                                if 'shared' in system_def:
                                    for shared in system_def['shared']:
                                        if is_arch_valid(arch, features['shared']['cfeatures'][shared]):
                                            features_lines.append(
                                                f'    <sharedFeature value="{_protect_xml(shared)}" />'
                                            )
                                        else:
                                            print('skipping system ' + emulator + '/' + system + ' shared ' + shared)
                                if 'cfeatures' in system_def:
                                    for cfeature, cfeature_def in system_def['cfeatures'].items():
                                        if is_arch_valid(arch, cfeature_def):
                                            features_lines.extend(
                                                _get_xml_feature(
                                                    12, cfeature, cfeature_def, toTranslate, emulator, core
                                                )
                                            )
                                        else:
                                            print(
                                                'skipping system ' + emulator + '/' + system + ' cfeature ' + cfeature
                                            )
                                features_lines.append('          </system>')
                            features_lines.append('        </systems>')
                            ###
                        features_lines.append('      </core>')
                    else:
                        features_lines.append(
                            f'      <core name="{_protect_xml(core)}" features="{_protect_xml(core_featuresTxt)}" />'
                        )
                features_lines.append('    </cores>')

            if 'systems' in emulator_def:
                features_lines.append('    <systems>')
                for system, system_def in emulator_def['systems'].items():
                    system_featuresTxt = _array_to_comma_string(system_def.get('features'))
                    features_lines.append(
                        f'      <system name="{_protect_xml(system)}" features="{_protect_xml(system_featuresTxt)}" >'
                    )
                    if 'shared' in system_def:
                        for shared in system_def['shared']:
                            if is_arch_valid(arch, features['shared']['cfeatures'][shared]):
                                features_lines.append(f'    <sharedFeature value="{_protect_xml(shared)}" />')
                            else:
                                print('skipping system ' + emulator + '/' + system + ' shared ' + shared)
                    if 'cfeatures' in system_def:
                        for cfeature, cfeature_def in system_def['cfeatures'].items():
                            if is_arch_valid(arch, cfeature_def):
                                features_lines.extend(
                                    _get_xml_feature(8, cfeature, cfeature_def, toTranslate, emulator, None)
                                )
                            else:
                                print('skipping system ' + emulator + '/' + system + ' cfeature ' + cfeature)
                    features_lines.append('      </system>')
                features_lines.append('    </systems>')
            if 'shared' in emulator_def:
                for shared in emulator_def['shared']:
                    if is_arch_valid(arch, features['shared']['cfeatures'][shared]):
                        features_lines.append(f'    <sharedFeature value="{_protect_xml(shared)}" />')
                    else:
                        print('skipping emulator ' + emulator + ' shared ' + shared)

            if 'cfeatures' in emulator_def:
                for cfeature, cfeature_def in emulator_def['cfeatures'].items():
                    if is_arch_valid(arch, cfeature_def):
                        features_lines.extend(_get_xml_feature(4, cfeature, cfeature_def, toTranslate, emulator, None))
                    else:
                        print('skipping emulator ' + emulator + ' cfeature ' + cfeature)

            if emulator == 'global':
                features_lines.append('  </globalFeatures>')
            elif emulator == 'shared':
                features_lines.append('  </sharedFeatures>')
            else:
                features_lines.append('  </emulator>')
        else:
            features_lines[-1] += ' />'
    features_lines.extend(['</features>', ''])
    esFeaturesFile.write_text('\n'.join(features_lines))


# find all translation independantly of the arch
def _find_translations(featuresYaml: Path, /) -> dict[str | None, list[_CommentDict]]:
    toTranslate: dict[str | None, list[_CommentDict]] = {}
    features = _ordered_load(featuresYaml, _Features)
    for emulator, emulator_def in features.items():
        if (
            'cores' in emulator_def
            or 'systems' in emulator_def
            or 'cfeatures' in emulator_def
            or 'shared' in emulator_def
        ):
            if 'cores' in emulator_def:
                for core, core_def in emulator_def['cores'].items():
                    if 'cfeatures' in core_def or 'systems' in core_def:
                        # core features
                        if 'cfeatures' in core_def:
                            for cfeature_def in core_def['cfeatures'].values():
                                for tag in ['description', 'submenu', 'group', 'prompt']:
                                    if tag in cfeature_def:
                                        tagval = cast('str', cfeature_def[tag])
                                        _add_comment_to_dict_key(
                                            toTranslate, tagval, {'emulator': emulator, 'core': core}
                                        )
                                if 'choices' in cfeature_def:
                                    for choice in cfeature_def['choices']:
                                        _add_comment_to_dict_key(
                                            toTranslate, choice, {'emulator': emulator, 'core': core}
                                        )
                        # #############

                        # systems in cores/core
                        if 'systems' in core_def:
                            for system_def in core_def['systems'].values():
                                if 'cfeatures' in system_def:
                                    for cfeature_def in system_def['cfeatures'].values():
                                        for tag in ['description', 'submenu', 'group', 'prompt']:
                                            if tag in cfeature_def:
                                                tagval = cast('str', cfeature_def[tag])
                                                _add_comment_to_dict_key(
                                                    toTranslate, tagval, {'emulator': emulator, 'core': core}
                                                )
                                        if 'choices' in cfeature_def:
                                            for choice in cfeature_def['choices']:
                                                _add_comment_to_dict_key(
                                                    toTranslate, choice, {'emulator': emulator, 'core': core}
                                                )
            if 'systems' in emulator_def:
                for system_def in emulator_def['systems'].values():
                    if 'cfeatures' in system_def:
                        for cfeature_def in system_def['cfeatures'].values():
                            for tag in ['description', 'submenu', 'group', 'prompt']:
                                if tag in cfeature_def:
                                    tagval = cast('str', cfeature_def[tag])
                                    _add_comment_to_dict_key(toTranslate, tagval, {'emulator': emulator})
                            if 'choices' in cfeature_def:
                                for choice in cfeature_def['choices']:
                                    _add_comment_to_dict_key(toTranslate, choice, {'emulator': emulator})
            if 'cfeatures' in emulator_def:
                for cfeature_def in emulator_def['cfeatures'].values():
                    for tag in ['description', 'submenu', 'group', 'prompt']:
                        if tag in cfeature_def:
                            tagval = cast('str', cfeature_def[tag])
                            _add_comment_to_dict_key(toTranslate, tagval, {'emulator': emulator})
                    if 'choices' in cfeature_def:
                        for choice in cfeature_def['choices']:
                            _add_comment_to_dict_key(toTranslate, choice, {'emulator': emulator})
    return toTranslate


# Returns the extensions supported by the emulator
def _list_extension(data: SystemDict, uppercase: bool, /) -> str:
    extension_txt: list[str] = []

    if 'extensions' in data:
        extensions = data['extensions']
        for item in extensions:
            extension_txt.append('.' + str(item).lower())
            if uppercase:
                extension_txt.append('.' + str(item).upper())

    return ' '.join(extension_txt)


# Returns group to emulator rom folder
def _system_group(system: str, data: SystemDict, /) -> str:
    if 'group' in data:
        if data['group'] is None:
            return ''
        return data['group']
    return ''


# Returns the enabled cores in the .config file for the emulator
def _list_emulators(
    data: SystemDict,
    config: dict[str, int],
    defaultEmulator: str | None,
    defaultCore: str | None,
    arch: str,
    /,
) -> list[str]:
    if 'emulators' not in data:
        return []

    emulators_txt: list[str] = []
    for emulator, emulatorData in sorted(data['emulators'].items(), key=lambda x: x[0]):
        if not is_arch_valid(arch, emulatorData):
            continue

        # CORES
        cores_txt: list[str] = []

        # Get a list of actual cores, filtering out our architecture keys
        core_keys = [key for key in emulatorData if key not in ['archs_include', 'archs_exclude']]
        for core in sorted(core_keys):
            coreData = cast('dict[str, CoreDict]', emulatorData)[core]
            if is_valid_requirements(config, coreData['requireAnyOf']) and is_arch_valid(arch, coreData):
                incompatible_extensionsTxt = ''
                if 'incompatible_extensions' in coreData:
                    for ext in coreData['incompatible_extensions']:
                        if incompatible_extensionsTxt != '':
                            incompatible_extensionsTxt += ' '
                        incompatible_extensionsTxt += '.' + str(ext).lower()
                    incompatible_extensionsTxt = ' incompatible_extensions="' + incompatible_extensionsTxt + '"'

                cores_txt.append(
                    f'                    <core default="true"{incompatible_extensionsTxt}>{core}</core>'
                    if emulator == defaultEmulator and core == defaultCore
                    else f'                    <core{incompatible_extensionsTxt}>{core}</core>'
                )

        if cores_txt:
            emulators_txt.extend(
                [
                    f'            <emulator name="{emulator}">',
                    '                <cores>',
                    *cores_txt,
                    '                </cores>',
                    '            </emulator>',
                ]
            )

    if emulators_txt:
        return ['        <emulators>', *emulators_txt, '        </emulators>']

    return emulators_txt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('yml', help='es_systems.yml definition file', type=Path)
    parser.add_argument('features', help='es_features.yml file', type=Path)
    parser.add_argument('es_translations', help='es_translations.h file', type=Path)
    parser.add_argument('es_keys_translations', help='es_keys_translations.h file', type=Path)
    parser.add_argument(
        'es_keys_parent_folder', help='es_keys files parent folder (where to search for .keys files)', type=Path
    )
    parser.add_argument('blacklisted_words', help='blacklisted_words.txt file', type=Path)
    parser.add_argument('config', help='.config buildroot file', type=Path)
    parser.add_argument('es_systems', help='es_systems.cfg emulationstation file', type=Path)
    parser.add_argument('es_features', help='es_features.cfg emulationstation file', type=Path)
    parser.add_argument('gen_defaults_global', help='global configgen defaults', type=Path)
    parser.add_argument('gen_defaults_arch', help='defaults configgen defaults', type=Path)
    parser.add_argument('romsdirsource', help='emulationstation roms directory', type=Path)
    parser.add_argument('romsdirtarget', help='emulationstation roms directory', type=Path)
    parser.add_argument('arch', help='arch')
    args = parser.parse_args()
    _generate_all(
        args.yml,
        args.features,
        args.config,
        args.es_systems,
        args.es_features,
        args.es_translations,
        args.es_keys_translations,
        args.es_keys_parent_folder,
        args.blacklisted_words,
        args.gen_defaults_global,
        args.gen_defaults_arch,
        args.romsdirsource,
        args.romsdirtarget,
        args.arch,
    )
