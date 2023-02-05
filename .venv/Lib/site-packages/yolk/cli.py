# PYTHON_ARGCOMPLETE_OK

"""cli.

Desc: Command-line tool for listing Python packages installed by setuptools,
      package metadata, package dependencies, and querying The Cheese Shop
      (PyPI) for Python package release information such as which installed
      packages have updates available.

Author: Rob Cakebread <gentoodev a t gmail.com>

License : BSD (See COPYING)

"""

from __future__ import print_function

import argparse
import inspect
import os
import pkg_resources
import pprint
import re
import site
import struct
import subprocess
import sys
import webbrowser

if sys.version_info[0] == 2:
    from httplib import HTTPException
    from urllib import urlretrieve
    from urlparse import urlparse
    from xmlrpclib import Fault as XMLRPCFault
else:
    from http.client import HTTPException
    from urllib.request import urlretrieve
    from urllib.parse import urlparse
    from xmlrpc.client import Fault as XMLRPCFault

from distutils.sysconfig import get_python_lib
from yolk.metadata import get_metadata
from yolk import yolklib
from yolk.pypi import CheeseShop
from yolk.setuptools_support import get_download_uri, get_pkglist
from yolk.utils import run_command, command_successful
from yolk.__init__ import __version__ as VERSION


class YolkException(Exception):

    """Exception for communicating top-level error to user."""


class StdOut(object):

    """Filter stdout or stderr from specific modules So far this is just used
    for pkg_resources."""

    def __init__(self, stream, modulenames):
        self.stdout = stream
        # Modules to squelch
        self.modulenames = modulenames

    def __getattr__(self, attribute):
        if attribute not in self.__dict__ or attribute == '__doc__':
            return getattr(self.stdout, attribute)
        return self.__dict__[attribute]

    def flush(self):
        """Bug workaround for Python 3.2+: Exception AttributeError: 'flush'
        in.

        <yolk.cli.StdOut object...

        """

    def write(self, inline):
        """Write a line to stdout if it isn't in a blacklist.

        Try to get the name of the calling module to see if we want to
        filter it. If there is no calling module, use current frame in
        case there's a traceback before there is any calling module

        """
        frame = inspect.currentframe().f_back
        if frame:
            mod = frame.f_globals.get('__name__')
        else:
            mod = sys._getframe(0).f_globals.get('__name__')
        if mod not in self.modulenames:
            self.stdout.write(inline)

    def writelines(self, inline):
        """Write multiple lines."""
        for line in inline:
            self.write(line)


class Yolk(object):

    """Main class for yolk."""

    def __init__(self):
        # PyPI project name with proper case
        self.project_name = ''
        # PyPI project version
        self.version = ''
        # List of all versions not hidden on PyPI
        self.all_versions = []
        self.pkg_spec = None
        self.options = None

        # Squelch output from setuptools
        # Add future offenders to this list.
        shut_up = ['distutils.log']
        sys.stdout = StdOut(sys.stdout, shut_up)
        sys.stderr = StdOut(sys.stderr, shut_up)
        self.pypi = None

    def get_plugin(self, method):
        """Return plugin object if CLI option is activated and method exists.

        @param method: name of plugin's method we're calling
        @type method: string

        @returns: list of plugins with `method`

        """
        all_plugins = []
        for entry_point in pkg_resources.iter_entry_points('yolk.plugins'):
            plugin_obj = entry_point.load()
            plugin = plugin_obj()
            plugin.configure(self.options, None)
            if plugin.enabled:
                if not hasattr(plugin, method):
                    plugin = None
                else:
                    all_plugins.append(plugin)
        return all_plugins

    def run(self):
        """Perform actions based on CLI options.

        @returns: status code

        """
        parser = setup_parser()

        try:
            import argcomplete
            argcomplete.autocomplete(parser)
        except ImportError:
            pass

        self.options = parser.parse_args()

        pkg_spec = validate_pypi_opts(parser)
        if not pkg_spec:
            pkg_spec = self.options.pkg_spec
        self.pkg_spec = pkg_spec

        if self.options.fields:
            self.options.fields = [s.strip().lower()
                                   for s in self.options.fields.split(',')]
        else:
            self.options.fields = []

        if (
            not self.options.pypi_search and
            len(sys.argv) == 1
        ):
            parser.print_help()
            return 2

        # Options that depend on querying installed packages, not PyPI.
        # We find the proper case for package names if they are installed,
        # otherwise PyPI returns the correct case.
        if (
            self.options.show_deps or
            self.options.show_all or
            self.options.show_active or
            self.options.show_non_active or
            (self.options.show_updates and pkg_spec) or
            self.options.upgrade
        ):
            want_installed = True
        else:
            want_installed = False
        # show_updates may or may not have a pkg_spec
        if (
            not want_installed or
            self.options.show_updates or
            self.options.upgrade
        ):
            self.pypi = CheeseShop(self.options.debug)
            # XXX: We should return 2 here if we couldn't create xmlrpc server

        if pkg_spec:
            (self.project_name,
             self.version,
             self.all_versions) = self.parse_pkg_ver(want_installed)
            if want_installed and not self.project_name:
                print(u'{} is not installed'.format(pkg_spec),
                      file=sys.stderr)
                return 1

        # I could prefix all these with 'cmd_' and the methods also
        # and then iterate over the `options` dictionary keys...
        commands = ['show_deps', 'query_metadata_pypi', 'fetch',
                    'versions_available', 'show_updates', 'upgrade',
                    'browse_website',
                    'show_download_links', 'pypi_search',
                    'show_pypi_changelog', 'show_pypi_releases',
                    'yolk_version', 'show_all',
                    'show_active', 'show_non_active', 'show_entry_map',
                    'show_entry_points']

        # Run first command it finds, and only the first command, then return
        # XXX: Check if more than one command was set in options and give
        # error?
        for action in commands:
            if getattr(self.options, action):
                return getattr(self, action)()
        parser.print_help()

    def show_active(self):
        """Show installed active packages."""
        return self.show_distributions('active')

    def show_non_active(self):
        """Show installed non-active packages."""
        return self.show_distributions('nonactive')

    def show_all(self):
        """Show all installed packages."""
        return self.show_distributions('all')

    def show_updates(self):
        """Check installed packages for available updates on PyPI.

        @param project_name: optional package name to check; checks every
                             installed package if none specified
        @type project_name: string

        @returns: None

        """
        if self.project_name:
            pkg_list = [self.project_name]
        else:
            pkg_list = get_pkglist()

        for (project_name, version, newest) in _updates(
                pkg_list,
                self.pypi,
                user_installs_only=self.options.user):
            print(u'{} {} ({})'.format(project_name,
                                       version,
                                       newest))

        return 0

    def upgrade(self):
        """Check installed packages for available updates on PyPI and upgrade.

        @param project_name: optional package name to check; checks every
                             installed package if none specified
        @type project_name: string

        @returns: None

        """
        if self.project_name:
            pkg_list = [self.project_name]
        else:
            pkg_list = get_pkglist()

        names = [values[0]
                 for values in _updates(pkg_list,
                                        self.pypi,
                                        user_installs_only=self.options.user)]
        if names:
            subprocess.call(
                [sys.executable, '-m', 'pip', 'install', '--upgrade'] +
                (['--user'] if self.options.user else []) +
                names)

        return 0

    def show_distributions(self, show):
        """Show list of installed activated OR non-activated packages.

        @param show: type of pkgs to show (all, active or nonactive)
        @type show: string

        @returns: None or 2 if error

        """
        # Search for any plugins with active CLI options with add_column()
        # method.
        plugins = self.get_plugin('add_column')

        # Some locations show false positive for 'development' packages:
        ignores = ['/UNIONFS', '/KNOPPIX.IMG']

        # See http://cheeseshop.python.org/pypi/workingenv.py for details.
        workingenv = os.environ.get('WORKING_ENV')
        if workingenv:
            ignores.append(workingenv)

        results = None
        for (dist, active) in yolklib.get_distributions(show,
                                                        self.project_name,
                                                        self.version):
            metadata = get_metadata(dist)
            for prefix in ignores:
                if dist.location.startswith(prefix):
                    dist.location = dist.location.replace(prefix, '')
            # Case-insensitive search because of Windows.
            if dist.location.lower().startswith(get_python_lib().lower()):
                develop = ''
            else:
                develop = dist.location
            if metadata:
                add_column_text = ''
                for my_plugin in plugins:
                    # See if package is 'owned' by a package manager such as
                    # portage, apt, rpm etc.
                    add_column_text += my_plugin.add_column(dist) + ' '
                self.print_metadata(metadata, develop, active, add_column_text)
            else:
                print(str(dist) + ' has no metadata')
            results = True
        if not results and self.project_name:
            if self.version:
                pkg_spec = '{}=={}'.format(self.project_name, self.version)
            else:
                pkg_spec = self.project_name
            if show == 'all':
                print(
                    u'There are no versions of {} installed'.format(pkg_spec),
                    file=sys.stderr)
            else:
                print(
                    u'There are no {} versions of {} installed'.format(
                        show, pkg_spec),
                    file=sys.stderr)
            return 2
        elif show == 'all' and results and self.options.fields:
            print("Versions with '*' are non-active.")
            print("Versions with '!' are deployed in development mode.")

    def print_metadata(self, metadata, develop, active, installed_by):
        """Print out formatted metadata.

        @param metadata: package's metadata
        @type metadata:  pkg_resources Distribution obj

        @param develop: path to pkg if its deployed in development mode
        @type develop: string

        @param active: show if package is activated or not
        @type active: boolean

        @param installed_by: Shows if pkg was installed by a package manager
                             other than setuptools
        @type installed_by: string

        @returns: None

        """
        show_metadata = self.options.metadata
        version = metadata['Version']

        # When showing all packages, note which are not active:
        if active:
            if self.options.fields:
                active_status = ''
            else:
                active_status = 'active'
        else:
            if self.options.fields:
                active_status = '*'
            else:
                active_status = 'non-active'
        if develop:
            if self.options.fields:
                development_status = '! ({})'.format(develop)
            else:
                development_status = 'development ({})'.format(develop)
        else:
            development_status = installed_by
        status = '{} {}'.format(active_status, development_status)
        if self.options.fields:
            print(
                '{} ({}){} {}'.format(metadata['Name'], version, active_status,
                                      development_status))
        else:
            # Need intelligent justification.
            print(metadata['Name'].ljust(15) + ' - ' + version.ljust(12) +
                  ' - ' + status)
        if self.options.fields:
            for field in metadata.keys():
                if field.lower() in self.options.fields:
                    print(u'    {}: {}'.format(field, metadata[field]))
            print()
        elif show_metadata:
            for field in metadata.keys():
                if field != 'Name' and field != 'Summary':
                    print(u'    {}: {}'.format(field, metadata[field]))

    def show_deps(self):
        """Show dependencies for package(s)

        @returns: 0 - success  1 - No dependency info supplied

        """

        pkgs = pkg_resources.Environment()

        for pkg in pkgs[self.project_name]:
            if not self.version:
                print(pkg.project_name, pkg.version)

            i = len(list(pkg._dep_map.values())[0])
            if i:
                while i:
                    if (
                        not self.version or
                        self.version and
                        pkg.version == self.version
                    ):
                        if self.version and i == len(list(
                                pkg._dep_map.values())[0]):
                            print(pkg.project_name, pkg.version)
                        print(u'  ' + str(list(
                            pkg._dep_map.values())[0][i - 1]))
                    i -= 1
            else:
                return 1
        return 0

    def show_pypi_changelog(self):
        """Show detailed PyPI ChangeLog for the last `hours`

        @returns: 0 = success or 1 if failed to retrieve from XML-RPC server

        """
        hours = self.options.show_pypi_changelog
        if not hours.isdigit():
            print('You must supply an integer',
                  file=sys.stderr)
            return 1

        try:
            changelog = self.pypi.changelog(int(hours))
        except XMLRPCFault as err_msg:
            print(err_msg, file=sys.stderr)
            print("Couldn't retrieve changelog", file=sys.stderr)
            return 1

        last_pkg = ''
        for entry in changelog:
            pkg = entry[0]
            if pkg != last_pkg:
                print(u'{} {}\n\t{}'.format(entry[0], entry[1], entry[3]))
                last_pkg = pkg
            else:
                print(u'\t{}'.format(entry[3]))

        return 0

    def show_pypi_releases(self):
        """Show PyPI releases for the last number of `hours`

        @returns: 0 = success or 1 if failed to retrieve from XML-RPC server

        """
        try:
            hours = int(self.options.show_pypi_releases)
        except ValueError:
            print('You must supply an integer', file=sys.stderr)
            return 1
        try:
            latest_releases = self.pypi.updated_releases(hours)
        except XMLRPCFault as err_msg:
            print(err_msg, file=sys.stderr)
            print("Couldn't retrieve latest releases.", file=sys.stderr)
            return 1

        for release in latest_releases:
            print(u'{} {}'.format(release[0], release[1]))
        return 0

    def show_download_links(self):
        """Query PyPI for pkg download URI for a packge.

        @returns: 0

        """
        # In case they specify version as 'dev' instead of using -T svn,
        # don't show three svn URI's
        if self.options.file_type == 'all' and self.version == 'dev':
            self.options.file_type = 'svn'

        if self.options.file_type == 'svn':
            version = 'dev'
        else:
            if self.version:
                version = self.version
            else:
                version = self.all_versions[0]
        if self.options.file_type == 'all':
            # Search for source, egg, and svn.
            self.print_download_uri(version, True)
            self.print_download_uri(version, False)
            self.print_download_uri('dev', True)
        else:
            if self.options.file_type == 'source':
                source = True
            else:
                source = False
            self.print_download_uri(version, source)
        return 0

    def print_download_uri(self, version, source):
        """@param version: version number or 'dev' for svn.

        @type version: string

        @param source: download source or egg
        @type source: boolean

        @returns: None

        """

        if version == 'dev':
            source = True

        # Use setuptools monkey-patch to grab url.
        url = get_download_uri(self.project_name, version, source,
                               self.options.pypi_index)
        if url:
            print(u'{}'.format(url))

    def fetch(self):
        """Download a package.

        @returns: 0 = success or 1 if failed download

        """
        source = True
        directory = '.'

        if self.options.file_type == 'svn':
            svn_uri = get_download_uri(self.project_name,
                                       'dev', True)
            if svn_uri:
                directory = self.project_name + '_svn'
                return self.fetch_svn(svn_uri, directory)
            else:
                print(
                    'No subversion repository found for {}'.format(
                        self.project_name),
                    file=sys.stderr)
                return 1
        elif self.options.file_type == 'source':
            source = True
        elif self.options.file_type == 'egg':
            source = False

        uri = get_download_uri(self.project_name, self.version, source)
        if uri:
            return self.fetch_uri(directory, uri)
        else:
            print(u'No {} URI found for package: {}'.format(
                self.options.file_type, self.project_name))
            return 1

    def fetch_uri(self, directory, uri):
        """Use ``urllib.urlretrieve`` to download package to file in sandbox
        dir.

        @param directory: directory to download to
        @type directory: string

        @param uri: uri to download
        @type uri: string

        @returns: 0 = success or 1 for failed download

        """
        filename = os.path.basename(urlparse(uri)[2])
        if os.path.exists(filename):
            print(u'File exists: ' + filename, file=sys.stderr)
            return 1

        try:
            downloaded_filename, headers = urlretrieve(uri, filename)
        except IOError as err_msg:
            print(
                'Error downloading package {} from URL {}'.format(
                    filename, uri),
                file=sys.stderr)
            print(str(err_msg), file=sys.stderr)
            return 1

        if 'text/html' in headers:
            dfile = open(downloaded_filename)
            if re.search('404 Not Found', ''.join(dfile.readlines())):
                dfile.close()
                print("'404 Not Found' error", file=sys.stderr)
                return 1
            dfile.close()
        return 0

    def fetch_svn(self, svn_uri, directory):
        """Fetch subversion repository.

        @param svn_uri: subversion repository uri to check out
        @type svn_uri: string

        @param directory: directory to download to
        @type directory: string

        """
        if not command_successful(['svn', '--version']):
            raise YolkException('Do you have subversion installed?')
        if os.path.exists(directory):
            raise YolkException(
                'Checkout directory exists - {}'.format(directory))
        try:
            os.mkdir(directory)
        except OSError as err_msg:
            raise YolkException('' + str(err_msg))
        cwd = os.path.realpath(os.curdir)
        os.chdir(directory)
        status, _ = run_command(['svn', 'checkout', svn_uri])
        os.chdir(cwd)

    def browse_website(self, browser=None):
        """Launch web browser at project's homepage.

        @param browser: name of web browser to use
        @type browser: string

        @returns: 0 if homepage found, 1 if no homepage found

        """
        if len(self.all_versions):
            metadata = self.pypi.release_data(self.project_name,
                                              self.all_versions[0])
            if 'home_page' in metadata:
                if browser == 'konqueror':
                    browser = webbrowser.Konqueror()
                else:
                    browser = webbrowser.get()
                    browser.open(metadata['home_page'], 2)
                return 0

        print('No homepage URL found', file=sys.stderr)
        return 1

    def query_metadata_pypi(self):
        """Show pkg metadata queried from PyPI.

        @returns: 0

        """
        if self.version and self.version in self.all_versions:
            metadata = self.pypi.release_data(self.project_name, self.version)
        else:
            # Give highest version
            metadata = self.pypi.release_data(self.project_name,
                                              self.all_versions[0])

        if metadata:
            if len(self.options.fields) == 1:
                try:
                    print(metadata[self.options.fields[0]])
                except KeyError:
                    pass
            else:
                for key in metadata.keys():
                    if (
                        not self.options.fields or
                        (self.options.fields and
                         key.lower() in self.options.fields)
                    ):
                        print(u'{}: {}'.format(key, metadata[key]))
        return 0

    def versions_available(self):
        """Query PyPI for a particular version or all versions of a package.

        @returns: 0 if version(s) found or 1 if none found

        """
        if self.all_versions and self.version in self.all_versions:
            print_pkg_versions(self.project_name, [self.version])
        elif not self.version and self.all_versions:
            print_pkg_versions(self.project_name, self.all_versions)
        else:
            if self.version:
                print(
                    'No package found for version {}'.format(self.version),
                    file=sys.stderr)
            else:
                print(
                    'No package found for {}'.format(self.project_name),
                    file=sys.stderr)
            return 1
        return 0

    def parse_search_spec(self, spec):
        """Parse search args and return spec dict for PyPI.

        * Owwww, my eyes!. Re-write this.

        @param spec: Cheese Shop package search spec
                     e.g.
                     name=Cheetah
                     license=ZPL
                     license=ZPL AND name=Cheetah
        @type spec: string

        @returns:  tuple with spec and operator

        """

        usage = """You can search PyPI by the following:
     name
     version
     author
     author_email
     maintainer
     maintainer_email
     home_page
     license
     summary
     description
     keywords
     platform
     download_url

     e.g. yolk -S name=Cheetah
          yolk -S name=yolk AND license=PSF
          """

        if not spec:
            print(usage, file=sys.stderr)
            return (None, None)

        try:
            spec = (' ').join(spec)
            operator = 'AND'
            first = second = ''
            if ' AND ' in spec:
                (first, second) = spec.split('AND')
            elif ' OR ' in spec:
                (first, second) = spec.split('OR')
                operator = 'OR'
            else:
                first = spec
            (key1, term1) = first.split('=')
            key1 = key1.strip()
            if second:
                (key2, term2) = second.split('=')
                key2 = key2.strip()

            spec = {}
            spec[key1] = term1
            if second:
                spec[key2] = term2
        except:
            print(usage, file=sys.stderr)
            spec = operator = None
        return (spec, operator)

    def pypi_search(self):
        """Search PyPI by metadata keyword e.g.

        yolk -S name=yolk AND license=GPL

        @param spec: Cheese Shop search spec
        @type spec: list of strings

        spec examples:
          ["name=yolk"]
          ["license=GPL"]
          ["name=yolk", "AND", "license=GPL"]

        @returns: 0 on success or 1 if mal-formed search spec

        """
        spec = self.pkg_spec
        # Add remaining cli arguments to options.pypi_search.
        search_arg = self.options.pypi_search
        spec.insert(0, search_arg.strip())

        (spec, operator) = self.parse_search_spec(spec)
        if not spec:
            return 1
        for pkg in self.pypi.search(spec, operator):
            if pkg['summary']:
                summary = pkg['summary'].encode('utf-8')
            else:
                summary = ''
            print("""{} ({}):
        {}
    """.format(pkg['name'].encode('utf-8'), pkg['version'],
               summary))
        return 0

    def show_entry_map(self):
        """Show entry map for a package.

        @param dist: package
        @param type: string

        @returns: 0 for success or 1 if error

        """
        pprinter = pprint.PrettyPrinter()
        try:
            entry_map = pkg_resources.get_entry_map(
                self.options.show_entry_map)
            if entry_map:
                pprinter.pprint(entry_map)
        except pkg_resources.DistributionNotFound:
            print(
                'Distribution not found: {}'.format(
                    self.options.show_entry_map),
                file=sys.stderr)
            return 1
        return 0

    def show_entry_points(self):
        """Show entry points for a module.

        @returns: 0 for success or 1 if error

        """
        found = False
        for entry_point in pkg_resources.iter_entry_points(
                self.options.show_entry_points):

            found = True
            try:
                plugin = entry_point.load()
                print(plugin.__module__)
                print(u'   {}'.format(entry_point))
                if plugin.__doc__:
                    print(plugin.__doc__)
                print()
            except ImportError:
                pass
        if not found:
            print(
                'No entry points found for {}'.format(
                    self.options.show_entry_points),
                file=sys.stderr)
            return 1
        return 0

    def yolk_version(self):
        """Show yolk's version."""
        print(u'yolk {}'.format(VERSION))

    def parse_pkg_ver(self, want_installed):
        """Return tuple with project_name and version from CLI args If the user
        gave the wrong case for the project name, this corrects it.

        @param want_installed: whether package we want is installed or not
        @type want_installed: boolean

        @returns: tuple(project_name, version, all_versions)

        """
        all_versions = []

        arg_str = self.pkg_spec
        if '==' not in arg_str:
            # No version specified.
            project_name = arg_str
            version = None
        else:
            (project_name, version) = arg_str.split('==')
            project_name = project_name.strip()
            version = version.strip()
        # Find proper case for package name.
        if want_installed:
            project_name = yolklib.case_sensitive_name(project_name)
        else:
            (project_name, all_versions) = self.pypi.query_versions_pypi(
                project_name)

            if not len(all_versions):
                msg = "I'm afraid we have no '{}' at ".format(project_name)
                msg += 'The Cheese Shop. A little Red Leicester, perhaps?'
                print(msg, file=sys.stderr)
                sys.exit(2)
        return (project_name, version, all_versions)


def setup_parser():
    """Setup the argparser.

    @returns: parser.ArgumentParser

    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', action='store_true', dest='yolk_version',
                        default=False,
                        help='show yolk version and exit')

    parser.add_argument('--debug', action='store_true',
                        default=False, help='show debugging information')

    parser.add_argument('-q', '--quiet', action='store_true',
                        default=False, help='show less output')

    parser.add_argument('pkg_spec', nargs='?')

    group_local = parser.add_argument_group(
        'Query installed Python packages',
        'The following options show information about installed Python '
        'packages. Activated packages are normal packages on sys.path that '
        'can be imported. Non-activated packages need '
        "'pkg_resources.require()' before they can be imported, such as "
        "packages installed with 'easy_install --multi-version'. PKG_SPEC can "
        'be either a package name or package name and version e.g. Paste==0.9')

    group_local.add_argument(
        '-l', '--list', action='store_true', dest='show_all', default=False,
        help='list all Python packages installed by distutils or setuptools. '
             'Use PKG_SPEC to narrow results')

    group_local.add_argument(
        '-a', '--activated', action='store_true',
        dest='show_active', default=False,
        help='list activated packages installed by distutils or setuptools. '
             'Use PKG_SPEC to narrow results')

    group_local.add_argument(
        '-n', '--non-activated', action='store_true',
        dest='show_non_active', default=False,
        help='list non-activated packages installed by distutils or '
             'setuptools. Use PKG_SPEC to narrow results')

    group_local.add_argument(
        '-m', '--metadata', action='store_true',
        default=False,
        help='show all metadata for packages installed by '
             'setuptools (use with -l -a or -n)')

    group_local.add_argument(
        '-f', '--fields', action='store', default=False,
        help='show specific metadata (comma-separated) fields; '
             'use with -m or -M')

    group_local.add_argument(
        '-d', '--depends', action='store', dest='show_deps',
        metavar='PKG_SPEC',
        help='show dependencies for a package installed by '
             'setuptools if they are available')

    group_local.add_argument(
        '--entry-points', action='store',
        dest='show_entry_points', default=False,
        help='list entry points for a module. e.g. --entry-points '
             'nose.plugins',
        metavar='MODULE')

    group_local.add_argument(
        '--entry-map', action='store',
        dest='show_entry_map', default=False,
        help='list entry map for a package. e.g. --entry-map yolk',
        metavar='PACKAGE_NAME')

    group_pypi = parser.add_argument_group(
        'PyPI (Cheese Shop) options',
        'The following options query the Python Package Index:')

    group_pypi.add_argument(
        '-C', '--changelog', action='store',
        dest='show_pypi_changelog', metavar='HOURS',
        default=False,
        help='show detailed ChangeLog for PyPI for last n hours')

    group_pypi.add_argument(
        '-D', '--download-links', action='store',
        metavar='PKG_SPEC', dest='show_download_links',
        default=False,
        help="show download URL's for package listed on PyPI. Use with -T to "
             'specify egg, source etc')

    group_pypi.add_argument(
        '-F', '--fetch-package', action='store',
        metavar='PKG_SPEC', dest='fetch',
        default=False,
        help='download package source or egg; You can specify a file type '
             'with -T')

    group_pypi.add_argument(
        '-H', '--browse-homepage', action='store',
        metavar='PKG_SPEC', dest='browse_website',
        default=False,
        help='launch web browser at home page for package')

    group_pypi.add_argument('-I', '--pypi-index', action='store',
                            default=False,
                            help='specify PyPI mirror for package index')

    group_pypi.add_argument('-L', '--latest-releases', action='store',
                            dest='show_pypi_releases', metavar='HOURS',
                            default=False,
                            help='show PyPI releases for last n hours')

    group_pypi.add_argument(
        '-M', '--query-metadata', action='store',
        dest='query_metadata_pypi', default=False,
        metavar='PKG_SPEC',
        help='show metadata for a package listed on PyPI. Use -f to show '
             'particular fields')

    group_pypi.add_argument(
        '-S', action='store', dest='pypi_search',
        default=False,
        help='search PyPI by spec and optional AND/OR operator',
        metavar='SEARCH_SPEC <AND/OR SEARCH_SPEC>')

    group_pypi.add_argument(
        '-T', '--file-type', action='store', default='all',
        help="You may specify 'source', 'egg', 'svn' or 'all' when using -D.")

    group_pypi.add_argument('-U', '--show-updates', action='store_true',
                            default=False,
                            help='check PyPI for updates on package(s)')

    group_pypi.add_argument('--upgrade', '--pip', action='store_true',
                            help='run pip command to upgrade outdated '
                                 'packages; may be used with --user')

    group_pypi.add_argument('--user', action='store_true',
                            help='run pip with --user; for use with --upgrade')

    group_pypi.add_argument('-V', '--versions-available', action='store',
                            default=False, metavar='PKG_SPEC',
                            help='show available versions for given package '
                                 'listed on PyPI')

    return parser


def print_pkg_versions(project_name, versions):
    """Print list of versions available for a package.

    @returns: None

    """
    for ver in versions:
        print(u'{} {}'.format(project_name, ver))


def validate_pypi_opts(parser):
    """Check parse options that require pkg_spec.

    @returns: pkg_spec

    """

    options = parser.parse_args()
    options_pkg_specs = [options.versions_available,
                         options.query_metadata_pypi,
                         options.show_download_links,
                         options.browse_website,
                         options.fetch,
                         options.show_deps,
                         ]
    for pkg_spec in options_pkg_specs:
        if pkg_spec:
            return pkg_spec


def _updates(names, pypi, user_installs_only):
    """Return updates."""
    from multiprocessing.pool import ThreadPool

    exception = None

    def worker_function(pkg):
        for (dist, active) in yolklib.get_distributions(
                'all', pkg,
                yolklib.get_highest_installed(pkg)):

            if exception:
                return

            width = terminal_width()
            if width:
                print(u'\rChecking {}'.format(dist.project_name).ljust(width),
                      end='',
                      file=sys.stderr)

            (project_name, versions) = pypi.query_versions_pypi(
                dist.project_name)
        return (pkg, dist, project_name, versions)

    import multiprocessing
    pool = ThreadPool(multiprocessing.cpu_count())

    try:
        results = pool.map(worker_function, names)
    except IOError as _exception:
        exception = _exception

    print('\r', end='', file=sys.stderr)

    if exception:
        raise YolkException(exception)

    for (pkg, dist, project_name, versions) in results:
        try:
            if (
                user_installs_only and
                not dist.location.startswith(site.getusersitepackages())
            ):
                continue
        except AttributeError:
            # Probably inside a virtualenv.
            pass

        if versions:
            # PyPI returns them in chronological order,
            # but who knows if its guaranteed in the API?
            # Make sure we grab the highest version:

            newest = yolklib.get_highest_version(versions)
            if newest != dist.version:
                # We may have newer than what PyPI knows about.
                if (
                    pkg_resources.parse_version(dist.version) <
                    pkg_resources.parse_version(newest)
                ):
                    yield (project_name, dist.version, newest)


def terminal_width():
    try:
        import fcntl
        import termios
        return struct.unpack(
            'HHHH',
            fcntl.ioctl(sys.stderr.fileno(),
                        termios.TIOCGWINSZ,
                        struct.pack('HHHH', 0, 0, 0, 0)))[1]
    except (ImportError, OSError):
        # ImportError for non-Unix.
        # OSError for non-TTYs.
        return None


def main():
    """Let's do it."""
    try:
        my_yolk = Yolk()
        my_yolk.run()
    except (HTTPException, IOError, YolkException) as exception:
        print(exception, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 1
