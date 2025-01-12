#!/bin/env python3

# Dynamically assemble docker compose file for
# various usages.

version = """CAVISE docker-compose generator, version 0.0.0 (pre-release)."""

doc = """Overview

    CAVISE docker-compose generator. This tool is used to dynamically
    create docker-compose configs depending on one's needs. Originally,
    the needs were:
        - use local builds or pull containers from remotes
        - optional artery mount
    these might be extended further.

Usage:

    --help                  prints this message.
    --version               prints script version.
    -v, --verbosity         set logger verbosity, numbers are related to python
                            logging levels, for ex. 10 - Debug, 20 - INFO.
    -e, --env-file FILE     name or absolute path to .env file that is used in preprocessing.
    -t, --template FILE     name or absolute path to template file.
    --handlers HANDLERS...  list of handlers to use. Overrides --pack, if also supplied.
    --pack PACK             pre-defined list of handlers to use.
    --output-name NAME      name of output file, defaults to compose.yml
    --output-path PATH      path, where output file is stored. Defaults to simdata.
    --template-path PATH    path, where template files are looked up.
    --environment-path PATH path, where .env files are looked up.
"""

import io
import re
import os
import sys
import enum
import errno
import shutil
import typing
import logging
import pathlib
import argparse
import fileinput
import importlib
import dataclasses

try:
    coloredlogs = importlib.import_module('coloredlogs')
except ModuleNotFoundError as error:
    coloredlogs = None
    print('could not find coloredlogs module! Your logs will look boring.')
    print('if you are interested: https://pypi.org/project/coloredlogs')

try:
    yaml = importlib.import_module('yaml')
except ModuleNotFoundError as error:
    print('how did you think I would work with yaml, if you have no yaml package installed?')
    print('install it: https://pypi.org/project/pyaml')
    sys.exit(errno.EPERM)


make_abs = lambda relative: pathlib.PurePath(os.getcwd()).joinpath(relative)

# dataclass for paths utilized in this script.
@dataclasses.dataclass(init=True, repr=True)
class HandlerConfig:
    # Generated compose name.
    output_name: str = 'compose.yml'
    # Where to put result.
    output_path: pathlib.PurePath = make_abs('dc-configs')
    # Where to look for templates.
    templates_path: pathlib.PurePath = make_abs('cavise/scripts/templates')
    # Where to look for .env files.
    environment_path: pathlib.PurePath = make_abs('cavise/scripts/environments')

# pre-defined collections of handlers, for convenience.
class Pack(enum.Enum):
    LOCAL_BUILD = 1
    LOCAL_ARTERY_BUILD = 2
    REMOTE_BUILD = 3

class Handler:

    # default handlers for common docker-compose usage.
    DEFAULT = ['graphics', 'healthcheck', 'xorg', 'build-local', 'command']

    # packs.
    LOCAL_BUILD = ['graphics', 'healthcheck', 'xorg', 'build-local', 'command']
    LOCAL_ARTERY_BUILD = ['graphics', 'healthcheck', 'xorg', 'build-local', 'artery-local', 'command']
    REMOTE_BUILD = ['graphics', 'healthcheck', 'xorg', 'build-remote', 'command']

    # use this to map enum values to actual pack values.
    PACK_RESOLVER = {
        Pack.LOCAL_BUILD: LOCAL_BUILD,
        Pack.LOCAL_ARTERY_BUILD: LOCAL_ARTERY_BUILD,
        Pack.REMOTE_BUILD: REMOTE_BUILD
    }

    def __init__(self, template: pathlib.PurePath, environ: typing.Dict[str, str], config: HandlerConfig) -> None:
        if not os.path.exists(template):
            raise ValueError(f'file was not found: {template}')
        self.environ = environ
        self.config = config
        self.template = template

    def __enter__(self) -> 'Handler':
        self.generated = self.config.output_path.joinpath(self.config.output_name)
        shutil.copy(self.template, self.generated)
        result = self.__load_environment(self.generated, self.environ)
        if result is not None:
            raise ValueError(result)
        with open(self.generated, 'r') as stream:
            self.yaml = yaml.load(stream, yaml.SafeLoader)
        return self
    
    def __exit__(self, *_) -> None:
        with open(self.generated, 'w') as stream:
            yaml.dump(self.yaml, stream, default_flow_style=False)

    @staticmethod
    def add_mountpoint(name: str, service: typing.Dict[str, str], slave: str, master: str) -> typing.Dict[str, str]:
        if 'volumes' not in service:
            service['volumes'] = list()
        if any([element.startswith(master) for element in service['volumes']]):
            logging.warning(f'service {name} already has defined mountpoint: {slave}')
            return
        service['volumes'].append(f'{master}:{slave}')
        return service

    @staticmethod
    def add_environment_variable(name: str, service: typing.Dict[str, str], variable: str, value: str) -> typing.Dict[str, str]:
        if 'environment' not in service:
            service['environment'] = list()
        if any([element.startswith(variable) for element in service['environment']]):
            logging.warning(f'service {name} already has defined variable {variable} set to {value}')
            return
        service['environment'].append(f'{variable}={value}')
        return service

    # Performs search for environment variables and replaces them with current environment variables loaded.
    # Should not be called on template itself!
    def __load_environment(self, path: pathlib.PurePath, environ: typing.Dict[str, str]) -> None | str:
        if path.match('*cavise/scripts/templates/*'):
            return f'refusing to load environment, is path {path} leads to template? copy it somewhere else first!'
        regex = re.compile(r'\$\{\w*\}')
        with fileinput.input(path, inplace=True) as file:
            for i, line in enumerate(file):
                last = 0
                for group, position in map(lambda match: (match.group(), match.start()), regex.finditer(line)):
                    print(line[last:position], end='')
                    last = position + len(group)
                    key = group[2:-1]
                    if key not in environ:
                        return f'failed to find environment variable: {key} on line {i}'
                    print(environ[key], end='')
                print(line[last:], end='')

    def handle_command(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str] | str:
        if 'command' in service:
            logging.warning(f'service {name} already has defined command, skipping')
            return service
        service['command'] = ['sh', '-c', 'sleep infinity']
        return service

    @staticmethod
    def handle_graphics(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str] | str:
        Handler.add_mountpoint(name, service, '/usr/share/vulkan/icd.d', '/usr/share/vulkan/icd.d')
        Handler.add_mountpoint(name, service, '/tmp/.X11-unix', '/tmp/.X11-unix')
        tag = service
        for key in ['deploy', 'resources', 'reservations']:
            if tag.get(key, None) is None:
                tag[key] = dict()
            tag = tag[key]
        tag = service['deploy']['resources']['reservations']
        if 'devices' in tag:
            logging.warning('devices section is not empty! I\'m scared, skipping setup here')
            return service
        tag['devices'] = [{'driver': 'nvidia', 'capabilities': ['gpu']}]
        return service

    @staticmethod
    def handle_xorg(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str]:
        service = Handler.add_environment_variable(name, service, r'DISPLAY', r'${DISPLAY}')
        service = Handler.add_environment_variable(name, service, r'XAUTHORITY', r'${XAUTHORITY}')
        return Handler.add_mountpoint(name, service, r'${XAUTHORITY}', r'${XAUTHORITY}')

    @staticmethod
    def handle_healthcheck(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str]:
        if 'healthcheck' in service:
            logging.warning(f'service {name} already has healthcheck, skipping')
            return service
        healthcheck = dict()
        healthcheck['test'] = ['CMD', 'ping', '-c', '1', name]
        healthcheck['interval'] = '30s'
        healthcheck['timeout'] = '10s'
        healthcheck['retries'] = 3
        healthcheck['start_period'] = '10s'
        service['healthcheck'] = healthcheck
        return service

    @staticmethod
    def handle_build_local(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str]:
        if 'build' in service:
            if 'dockerfile' in service['build']:
                logging.warning(f'dockerfile already specified for local build for service: {name}, why?')
                return service
        else:
            service['build'] = dict()
        service['build']['dockerfile'] = f'{name}/Dockerfile'
        service['build']['context'] = os.getcwd()
        return service

    @staticmethod
    def handle_build_remote(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str]:
        if 'image' in service:
            logging.warning(f'image already specified for remote build for service: {name}, why?')
            return service
        service['image'] = r'${NEXUS_ADDR}/${' + f'{name.upper()}_IMAGE' + r'}:${TAG}'
        return service

    @staticmethod
    def handle_artery_local(name: str, service: typing.Dict[str, str]) -> typing.Dict[str, str]:
        if name.lower().startswith('artery'):
            return Handler.add_mountpoint(name, service, r'cavise/artery', r'./artery')
        return service


# Parse .env file into python dictionary. Two formats are allowed:
# KEY: VALUE and KEY=VALUE
# Mixing those two in one file is fine.
def parse_environment_file(path: pathlib.PurePath) -> typing.Dict[str, str] | str:
    if not os.path.exists(path):
        return f'failed to find a file: {path}'
    environ = dict()
    with open(path, 'r') as env_file:
        for line in map(lambda line: line.strip(), env_file.readlines()):
            key = value = None
            if re.match(r'.*:\s.*', line) and line.count(': ') == 1:
                key, value = line.split(': ')
            if re.match(r'[^=]*=[^=]*', line):
                key, value = line.split('=')
            
            if key is None and value is None:
                return f'failed to match a line in .env file: {line}'
            if key in environ:
                return f'double key detected - key {key} has two conflicting values: {value} and {environ[key]}'
            environ[key] = value                
    return environ

# Handles creation of environment - in python's terms it is a dictionary,
# where key and value are both strings. Path argument instructs function
# to take environ either from values inherited by process or values read from a file.
def create_environment(path: pathlib.PurePath | None = None) -> typing.Dict[str, str] | str:
    if path is None:
        environ = os.environ
        logging.info('path to .env file was not specified, using inherited environment')
    else:
        holder = parse_environment_file(path)
        if isinstance(holder, str):
            return f'failed to parse .env file, parser reported: {holder}'
        environ = holder
    return environ

# Parses command line arguments and returns initialized namespace with them.
# Best place to look for program options.
def parse_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    # supported options.
    parser.add_argument('--help', action='store_true', dest='help')
    parser.add_argument('--version', action='store_true', dest='version')
    # generator options.
    parser.add_argument('-v', '--verbosity', action='store', dest='verbosity', default=logging.INFO)
    parser.add_argument('-e', '--env-file', action='store', dest='env_file')
    parser.add_argument('-t', '--template', action='store', dest='template')
    parser.add_argument('--handlers', nargs='+', dest='handlers')
    parser.add_argument('--pack', action='store', dest='pack')
    parser.add_argument('--output-name', action='store', dest='output_name')
    parser.add_argument('--output-path', action='store', dest='output_path')
    parser.add_argument('--template-path', action='store', dest='template_path')
    parser.add_argument('--environment-path', action='store', dest='environment_path')

    return parser.parse_args()

def parse_string(params) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    # supported options.
    parser.add_argument('--help', action='store_true', dest='help')
    parser.add_argument('--version', action='store_true', dest='version')
    # generator options.
    parser.add_argument('-v', '--verbosity', action='store', dest='verbosity', default=logging.INFO)
    parser.add_argument('-e', '--env-file', action='store', dest='env_file')
    parser.add_argument('-t', '--template', action='store', dest='template')
    parser.add_argument('--handlers', nargs='+', dest='handlers')
    parser.add_argument('--pack', action='store', dest='pack')
    parser.add_argument('--output-name', action='store', dest='output_name')
    parser.add_argument('--output-path', action='store', dest='output_path')
    parser.add_argument('--template-path', action='store', dest='template_path')
    parser.add_argument('--environment-path', action='store', dest='environment_path')

    return parser.parse_args(params)

# Various checks regarding correctness of usage of this script.
def sanity_check() -> str | None:
    pwd = pathlib.PurePath(os.getcwd())
    if not os.path.exists(pwd.joinpath('.gitignore')):
        return f'current location: {pwd}, no .gitignore found. Are you sure this runs from cavise root?'
    
def resolve_path(path: pathlib.PurePath, anchor: pathlib.PurePath) -> pathlib.PurePath:
    if path.is_absolute():
        return path
    return anchor.joinpath(path)

# Is this needed to be explained?
def main() -> None:
    args = parse_command_line()
    # dry run commands.
    if getattr(args, 'help'):
        print(doc)
        sys.exit()
    if getattr(args, 'version'):
        print(version)
        sys.exit()

    if coloredlogs is not None:
        logging.basicConfig(handlers=[logging.StreamHandler(log_stream)])
        coloredlogs.install(level=int(getattr(args, 'verbosity')), fmt='- [%(asctime)s] %(message)s', datefmt='%M:%S')
    else:
        logging.basicConfig(level=int(getattr(args, 'verbosity')), fmt='- [%(asctime)s] %(message)s', datefmt='%M:%S', handlers=[logging.StreamHandler(log_stream)])

    holder = sanity_check()
    if isinstance(holder, str):
        logging.error(holder)
        sys.exit(errno.EPERM)

    config = HandlerConfig()
    for entry in ['output_name', 'output_path', 'template_path', 'environment_path']:
        if getattr(args, entry) is not None:
            setattr(config, entry, pathlib.PurePath(getattr(args, entry)))
    logging.debug(f'using handler config: {config}')

    env_file = None
    if getattr(args, 'env_file') is not None:
        env_file = resolve_path(pathlib.PurePath(getattr(args, 'env_file')), config.environment_path)
    if getattr(args, 'template') is None:
        logging.error('no template was specified. Why are so cruel?')
        sys.exit(errno.EPERM)
    template = resolve_path(pathlib.PurePath(getattr(args, 'template')), config.templates_path)

    holder = create_environment(env_file)
    if isinstance(holder, str):
        logging.error(holder)
        sys.exit(errno.EINVAL)
    environ = holder
    logging.info(f'using environment with {len(environ)} variables specified')
    logging.debug(f'environ: {environ}')

    try:
        with Handler(template, environ, config) as handler:
            if getattr(args, 'handlers') is not None:
                handles = getattr(args, 'handlers')
                logging.info('using user-defined handles: ' + ', '.join(handles))
            elif getattr(args, 'pack') is not None:
                pack = getattr(args, 'pack')
                logging.info(f'using pack: {pack}')
                handles = Handler.PACK_RESOLVER[Pack[pack]]
            else:
                logging.warning('no handlers or packs were specified, running default')
                handles = Handler.DEFAULT
            logging.info('using handles: ' + ', '.join(handles))
            services = handler.yaml['services']
            names = services.keys()
            for name in names:
                logging.info(f'processing service: {name}')
                for handle in handles:
                    logging.info(f'service: {name}; running handler {handle}')
                    f = getattr(Handler, 'handle_' + handle.replace('-', '_'))
                    services[name] = f(name, services[name])
            handler.yaml['services'] = services
    except Exception as error:
        logging.error(f'handler failed with error: {error}')
    logging.info('Bye bye.')

    return log_stream.getvalue()


if __name__ == '__main__':
    main()