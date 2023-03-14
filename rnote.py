"""Summary
"""
import subprocess
import json
from optparse import OptionParser
import os
import tempfile
import shutil
import StringIO
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

# ==========================
# enforce the stdout encoding to utf-8
# in order to be able to redirect utf-8 content
# to a file
import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
# ==========================

_description = """
Generate release change log grouping all the commits by tags.
It is compatible with Hg and Git.

[VM]
"""

_LS = '#&!_#'


class Printer(object):  # pylint: disable=too-few-public-methods
    """Summary
    """

    def __init__(self):
        self.buffer = StringIO.StringIO()

    def bprint(self,text):
        self.buffer.write(text)
        self.buffer.write(os.linesep)

    def close(self):
        self.buffer.close()


    def show(self):
        print(self.buffer.getvalue())
        self.close()


    def save(self, filename):
        try:
            with open(filename, 'w') as f:
                f.write(self.buffer.getvalue())
        finally:
            self.close()

    @staticmethod
    def get(type_):
        """Summary

        Args:
            type_ (TYPE): Description

        Returns:
            TYPE: Description
        """
        if type_ == 'html':
            return HTMLPrinter()

        if type_ == 'json':
            return JSONPrinter()

        return TXTPrinter()




class JSONPrinter(Printer):

    def print_changes(self, changes):
        """Summary

        Args:
            changes (TYPE): Description
        """
        self.bprint(u"\"Changes\":")
        if changes:
            self.bprint(u"[")

        for idx, commit in enumerate(changes):
            if idx < len(changes) - 1:
                self.bprint(u"\"{0}\",".format(commit))
            else:
                self.bprint(u"\"{0}\"".format(commit))

        if changes:
            self.bprint(u"],")

    def print_contributors(self, contributors):
        """Summary

        Args:
            contributors (TYPE): Description
        """
        self.bprint(u"\"Contributors\":")
        if contributors:
            self.bprint(u"[")
        for idx, user in enumerate(contributors):
            if idx < len(contributors) - 1:
                self.bprint(u"\"{0}\",".format(user))
            else:
                self.bprint(u"\"{0}\"".format(user))

        if contributors:
            self.bprint(u"]},")

    def print_header(self):
        self.bprint(u"{")
        
    def print_title(self, release, date, custom):
        """Summary

        Args:
            release (TYPE): Description
            date (TYPE): Description
        """
        self.bprint(u"\"{0}\":".format(release))
        self.bprint(u"{0}:\"{1}\",".format("{\"Date\"",date))


    def print_diff_title(self, frev, trev, custom):
        """Summary

        Args:
            frev (TYPE): Description
            trev (TYPE): Description
        """
        self.bprint(u'\"{0} till {1}\": {{'.format(frev, trev))

    def print_footer(self):
        """Summary
        """
        import pprint
        text = self.buffer.getvalue()
        self.buffer.truncate(0)
        text = text[:-2]+"}"
        jtext = json.loads(text)
        pprint.pprint(jtext,self.buffer)

        

class HTMLPrinter(Printer):
    """Summary
    """

    def print_changes(self, changes):
        """Summary

        Args:
            changes (TYPE): Description
        """
        self.bprint(u"<h3>Changes</h3>")
        if changes:
            self.bprint(u"<ul>")

        for commit in changes:
            try:
                self.bprint(u" <li> {0} </li>".format(commit))
            except:
                print changes
                self.bprint(u'' + commit)
                

        if changes:
            self.bprint(u"</ul>")

    def print_contributors(self, contributors):
        """Summary

        Args:
            contributors (TYPE): Description
        """
        self.bprint(u"<h3>Contributors</h3>")
        if contributors:
            self.bprint(u"<ul>")
        for user in contributors:
            self.bprint(u" <li> {0} </li>".format(user))
        if contributors:
            self.bprint(u" </ul>")

    def print_header(self):
        """Summary
        """
        self.bprint(u'<!DOCTYPE html><html><body>')
        self.bprint(
            u" <font face='\"Helvetica Neue\", Helvetica, Arial, sans-serif'>")

    def print_title(self, release, date, custom):
        """Summary

        Args:
            release (TYPE): Description
            date (TYPE): Description
        """
        self.bprint(u" <h1>Release {0} </h1>".format(release))
        self.bprint(u" <div style='margin-top:-20px'> on {0} </div>".format(date))

    def print_diff_title(self, frev, trev, custom):
        """Summary

        Args:
            frev (TYPE): Description
            trev (TYPE): Description
        """
        self.bprint(u" <h1>Difference from {0} till {1} <h1>".format(frev, trev))

    def print_footer(self):
        """Summary
        """
        self.bprint(u" </font>")
        self.bprint(u" </body></html>")


class TXTPrinter(Printer):
    """Summary
    """

    def print_changes(self, changes):
        """Summary

        Args:
            changes (TYPE): Description
        """
        #print(u" Changes")
        for commit in changes:
            self.bprint(u" * {0}".format(commit))

    def print_contributors(self, contributors):
        """Summary

        Args:
            contributors (TYPE): Description
        """
        self.bprint(u" \n Contributors")
        for user in contributors:
            self.bprint(u"  {0}".format(user))

    def print_header(self):
        """Summary
        """
        pass

    def print_title(self, release, date, custom=None):
        """Summary

        Args:
            release (TYPE): Description
            date (TYPE): Description
        """
        self.bprint('')
        if custom:
            self.bprint(u"{0}".format(custom))

        else:
            self.bprint(u"Release {0} ({1})".format(release, date))
            self.bprint(u"======================================")

    def print_diff_title(self, frev, trev, custom):
        """Summary

        Args:
            frev (TYPE): Description
            trev (TYPE): Description
        """
        if custom:
            self.bprint(u"{0}".format(custom))
        else:
            self.bprint(u"Difference from {0} till {1}".format(frev, trev))

    def print_footer(self):
        """Summary
        """
        pass


def check_output(*popenargs, **kwargs):
    """Run command with arguments and return its output as a byte string.
    Backported from Python 2.7 as it's implemented as pure python on stdlib.
    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2

    Args:
        *popenargs: Description
        **kwargs: Description

    Returns:
        TYPE: Description

    Raises:
        error: Description
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_echangelog = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


def _run_cmd(cmd, folder=None):
    """Summary

    Args:
        cmd (TYPE): Description
        repo (TYPE): Description

    Returns:
        TYPE: Description
    """
    # return subprocess.check_output(cmd,shell=True, cwd=repo) # Python >= 2.7
    cwd = os.getcwd()
    if folder:
        os.chdir(folder)
    try:
        result = check_output(cmd.split(' '))
    finally:
        os.chdir(cwd)
    return result.split('\n')

class SCM(object):

    @staticmethod
    def is_git(repo):
        """Summary

        Args:
            repo (TYPE): Description

        Returns:
            TYPE: Description
        """
        return os.path.isdir(os.path.join(repo, '.git'))

    @staticmethod
    def is_hg(repo):
        """Summary

        Args:
            repo (TYPE): Description

        Returns:
            TYPE: Description
        """
        return os.path.isdir(os.path.join(repo, '.hg'))

    @staticmethod
    def clone(repo, local_repo):

        clone_cmd_git = "git clone -b master " + repo + " " + local_repo + " --quiet"
        if '.git' in repo:
            try:
                _run_cmd(clone_cmd_git)
                return local_repo
            except:
                pass

        clone_cmd_hg = "hg clone " + repo + " " + local_repo
        try:
            _run_cmd(clone_cmd_hg)
            return local_repo
        except:
            pass

        print(u" Not a repository [Hg / Git]")
        return None

    @staticmethod
    def get_log(repo):
        """Summary

        Args:
            repo (TYPE): Description

        Returns:
            TYPE: Description
        """
        if SCM.is_hg(repo):
            log_cmd = "hg log --template {date|shortdate}" + \
                _LS + "{tags}" + _LS + "{author}" + _LS + "{desc}\n"
            raw = _run_cmd(log_cmd, repo)
            return raw
        if SCM.is_git(repo):
            log_cmd = "git log --date=short --pretty=format:%cd" + \
                _LS + "%D" + _LS + "%an" + _LS + "%s"
            raw = _run_cmd(log_cmd, repo)
            out = list()
            for each in raw:
                each = each.replace('HEAD -> master, ', '')
                each = each.replace('tag: ', '')
                out.append(each)
            return out

        print(u" Not a repository [Hg / Git]")
        return None


def print_diff(changelog, frev, trev, printer, custom):
    """Summary

    Args:
        changelog (TYPE): Description
        frev (TYPE): Description
        trev (TYPE): Description
        printer (TYPE): Description
    """
    changelog = OrderedDict(reversed(list(changelog.items())))
    printer.print_diff_title(frev, trev, custom)
    frev_found = False
    trev_found = False
    changes = list()
    contributors = set()
    for release in changelog:
        if frev_found:
            changes = changes + changelog[release]['desc']
            contributors = contributors.union(set(changelog[release]['user']))
            if trev in release:
                trev_found = True
                break

        if frev in release:
            frev_found = True

    if trev_found and frev_found:
        printer.print_changes(changes)
        printer.print_contributors(contributors)


def _sanityze(value):
    if type(value) == str:
        # Ignore errors even if the string is not proper UTF-8 or has
        # broken marker bytes.
        # Python built-in function unicode() can do this.
        value = unicode(value, "utf-8", errors="ignore")
    else:
        # Assume the value object has proper __unicode__() method
        value = unicode(value)
    return value


def _valid_commit(commit, current_tag, pattern):
    """Summary

    Args:
        commit (TYPE): Description
        current_tag (TYPE): Description
        pattern (TYPE): Description

    Returns:
        TYPE: Description
    """
    if pattern:
        if pattern not in current_tag:
            return False

    return True


def print_changelog(changelog, printer, custom):
    """Summary

    Args:
        changelog (TYPE): Description
        printer (TYPE): Description
    """
    for release in changelog:
        printer.print_title(release, changelog[release]['date'], custom)
        printer.print_changes(changelog[release]['desc'])
        printer.print_contributors(changelog[release]['user'])


def parse_raw_log(txt):
    """Summary

    Args:
        txt (TYPE): Description

    Returns:
        TYPE: Description
    """
    parsed = list()
    if txt:
        for line in txt:
            line = line.split(_LS)
            try:
                item = dict()
                item['date'] = line[0]
                item['tags'] = line[1]
                item['user'] = line[2]
                item['desc'] = _sanityze(line[3] or str())
                parsed.append(item)
            except IndexError as ex:
                pass
    return parsed


def add_item(current_tag, commit, changelog):
    """Summary

    Args:
        current_tag (TYPE): Description
        commit (TYPE): Description
        changelog (TYPE): Description
    """
    desc = commit['desc']
    date = commit['date']
    if current_tag not in changelog:
        changelog[current_tag] = dict()
        changelog[current_tag]['desc'] = list()
        changelog[current_tag]['user'] = set()
        changelog[current_tag]['userslist'] = list()
    changelog[current_tag]['desc'].append(desc)
    changelog[current_tag]['user'].add(commit['user'])
    changelog[current_tag]['userslist'].append(commit['user'])
    changelog[current_tag]['date'] = date


def build_changelog(repo, limit, pattern):
    """Summary

    Args:
        repo (str): Description
        limit (int): Description
        pattern (str): Description

    Returns:
        OrderedDict: changelog
    """
    raw = SCM.get_log(repo)
    raw = parse_raw_log(raw)
    jlog = json.dumps(raw)
    jlog = json.loads(jlog)
    changelog = OrderedDict()
    current_tag = str()
    for commit in jlog:
        if commit['tags']:
            if current_tag != commit['tags']:
                if limit:
                    if len(changelog) >= limit:
                        break
            current_tag = commit['tags']

        if not _valid_commit(commit, current_tag, pattern):
            continue
        add_item(current_tag, commit, changelog)

    return changelog



def print_stat(changelog):
    tag_stats = dict()
    user_stats = dict()
    for tag in changelog:
        tag_stats[tag+' ('+changelog[tag]['date']+')'] = len(changelog[tag]['desc'])

        for user in changelog[tag]['userslist']:
            try:
                user_count = user_stats[user]
            except:
                user_count = 0
            user_stats[user] = user_count + 1

    print(u'Most changes')
    tag_stats_sorted_key = sorted(tag_stats, key=tag_stats.get, reverse=True)
    for key in tag_stats_sorted_key:
        print (u'[{0:8}] {1}'.format(tag_stats[key], key))

    print('')
    print(u'Most active users')
    user_stats_sorted_key = sorted(user_stats, key=user_stats.get, reverse=True)
    for key in user_stats_sorted_key:
        print (u'[{0:8}] {1}'.format(user_stats[key], key))
 



def run(repo, limit, frev, trev, output_type, pattern, custom, output_file, stat):
    """Summary

    Args:
        repo (TYPE): Description
        limit (TYPE): Description
        frev (TYPE): Description
        trev (TYPE): Description
        output_type (TYPE): Description
        pattern (TYPE): Description
    """
    changelog = build_changelog(repo, limit, pattern)
    if stat:
        print_stat(changelog)
        return

    if changelog:
        printer = Printer.get(output_type)
        printer.print_header()
        if frev:
            print_diff(changelog, frev, trev, printer, custom)
        else:
            print_changelog(changelog, printer, custom)
        printer.print_footer()
        if output_file:
            printer.save(output_file)
        else:
            printer.show()



def parse_input():
    """Summary
    """
    parser = OptionParser(description=_description)
    parser.add_option(
        "-r",
        "--repo",
        default=None,
        dest="repo",
        help="repository to scan. Defaulted to current directory.",
        metavar="REPO")
    parser.add_option(
        "-l",
        "--limit",
        default=None,
        dest="limit",
        help="limit the number of revision will be showed",
        metavar="LIMIT")
    parser.add_option(
        "-f",
        "--from",
        default=None,
        dest="frev",
        help="from revision (the older one)",
        metavar="FREV")
    parser.add_option(
        "-t",
        "--to",
        default=None,
        dest="trev",
        help="to revision (the newer one)",
        metavar="TREV")
    parser.add_option(
        "-o",
        "--output_type",
        default='txt',
        dest="output_type",
        help="display txt or html format",
        metavar="OUTPUT_TYPE",
        choices=["txt", "html", "json"])
    parser.add_option(
        "-p",
        "--pattern",
        default=None,
        dest="pattern",
        help="only the tags containing the PATTERN will be showed",
        metavar="PATTERN")
    parser.add_option(
        "-c",
        "--custom_title",
        default=None,
        dest="custom",
        help="custom title for the revision",
        metavar="CUSTOM")
    parser.add_option(
        "-w",
        "--write",
        default=None,
        dest="output_file",
        help="Write the changelog into the file",
        metavar="OUTPUT_FILE")
    parser.add_option(
        "-s",
        "--stat",
        default=False,
        action = "store_true",
        dest="stat",
        help="Display statistcs, all other option but -r are discarder",
        metavar="STAT")

    (options, _) = parser.parse_args()
    if not options.repo:
        options.repo = os.getcwd()

    if options.limit:
        options.limit = int(options.limit)

    if (options.frev and not options.trev) or (not options.frev
                                               and options.trev):
        parser.print_help()
        parser.error(
            '-f and -t option are mandatory has to be specified together')

    if options.frev and options.limit:
        parser.print_help()
        parser.error('-f or -t and -l option are not compatible')

    if options.custom:
        options.custom = options.custom.replace('\\n', '\n')

    return options.repo, options.limit, options.frev, options.trev, options.output_type, options.pattern, options.custom, options.output_file, options.stat


def clone_repo(repo):
    local_repo = tempfile.mkdtemp()
    return SCM.clone(repo, local_repo)


def resolve_repo(repo):
    if repo is None:
        return None
    if os.path.isdir(repo):
        return repo
    if ":" in repo:
        return clone_repo(repo)
    return None


def main():
    """Summary
    """
    repo, limit, frev, trev, output_type, pattern, custom, output_file, stat = parse_input()
    local_repo = resolve_repo(repo)
    if local_repo:
        run(local_repo, limit, frev, trev, output_type, pattern, custom, output_file, stat)
        if local_repo != repo:
            if os.path.isdir:
                shutil.rmtree(local_repo)


if __name__ == '__main__':
    main()
