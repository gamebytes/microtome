#
# microtome - Tim Conkling, 2012

import re
import logging
from collections import namedtuple, OrderedDict

Section = namedtuple("Section", ["name", "contents", "disabled"])

LOG = logging.getLogger(__name__)


class Matcher(object):
    '''Analog to java.util.regex.Matcher. Iterates over a string with the given pattern,
    and delegates all method calls to the most recent MatchObject iteration result.'''
    def __init__(self, pattern, string):
        self._finditer = pattern.finditer(string)
        self._last_match = None

    def __iter__(self):
        return self

    def next(self):
        self._last_match = self._finditer.next()
        return self._last_match

    def __getattr__(self, name):
        return getattr(self._last_match, name)


class GeneratedSourceMerger(object):
    '''Merges updates to a generated source file into a previously-generated version of that
    file, while leaving changes outside marked sections alone.
    Adapted from com.threerings.presents.tools.GeneratedSourceMerger
    '''

    def __init__(self, comment_str=r'//'):
        self._section_delimiter = re.compile(r'\s*' + comment_str + r' GENERATED (\w+) (START|END|DISABLED)\r?\n')

    def merge(self, newly_generated, previously_generated):
        '''returns previously_generated with marked sections updated from the same
        marked sections in newly_generated. Everything outside these sections in
        previously_generated is returned as-is. A marked section starts with
        "// GENERATED {name} START" and ends with "// GENERATED {name} END".

        If previously_generated has a generated section replaced with
        "// GENERATED {name} DISABLED", that section will no longer be updated.
        '''

        # If neither file has a GENERATED section, there's nothing for us to merge.
        if self._section_delimiter.search(newly_generated) is None and \
                self._section_delimiter.search(previously_generated) is None:
            LOG.warn("No generated sections found; not merging")
            return newly_generated

        # Extract the generated section names from the output and make sure they're all matched
        sections = OrderedDict()
        matcher = Matcher(self._section_delimiter, newly_generated)
        for _ in matcher:
            section = self._extract_generated_section(matcher, newly_generated)
            if section.name in sections:
                raise RuntimeError("Section %s used more than once" % section.name)
            sections[section.name] = section

        # Merge with the previously generated source
        merged = []
        matcher = Matcher(self._section_delimiter, previously_generated)
        current_start = 0
        for _ in matcher:
            merged.append(previously_generated[current_start:matcher.start()])
            existing_section = self._extract_generated_section(matcher, previously_generated)
            new_section = sections.pop(existing_section.name, None)
            if new_section is None:
                # Allow generated sections to be dropped in the template, but warn in case
                # something odd's happening
                LOG.warn("Droping previously-generated section '%s' that's no longer generated by the template" % matcher.group(1))
            elif existing_section.disabled:
                # If the existing code disables this generation, add that disabled comment
                merged.append(existing_section.contents)
            else:
                # Otherwise pop in the newly-generated code in place of what was there before
                merged.append(new_section.contents)

            current_start = matcher.end()

        # Add generated sections that weren't present in the old output before the last
        # non-generated code. It's a 50-50 shot, so warn when this happens
        for new_section in sections.itervalues():
            LOG.warn("Adding previously-missing generated section '%s' before the last non-generated text" % new_section.name)
            merged.append(new_section.contents)

        # Add any text past the last previously-generated section
        merged.append(previously_generated[current_start:])

        return ''.join(merged)

    def _extract_generated_section(self, matcher, string):
        '''Returns a section name and its contents from the given match pointing to the start
        of a section. matcher is at the end of the section when this returns.'''
        start_idx = matcher.start()
        name = matcher.group(1)
        if matcher.group(2) == "DISABLED":
            return Section(name, string[start_idx:matcher.end()], True)

        if matcher.group(2) != "START":
            raise RuntimeError("'%s' END without START" % name)

        try:
            matcher.next()
        except StopIteration:
            raise RuntimeError("'%s' START without END" % name)

        end_name = matcher.group(1)

        if matcher.group(2) != "END":
            raise RuntimeError("'%s' START after '%s' START" % (end_name, name))

        if end_name != name:
            raise RuntimeError("'%s' END after '%s' START" % (end_name, name))

        return Section(name, string[start_idx:matcher.end()], False)

if __name__ == "__main__":
    NEW = '''
    // GENERATED TEST START
    generated: new
    // GENERATED TEST END
    '''
    OLD = '''
    old start
    // GENERATED TEST START
    generated: old
    // GENERATED TEST END
    old end
    '''
    print GeneratedSourceMerger().merge(NEW, OLD)

