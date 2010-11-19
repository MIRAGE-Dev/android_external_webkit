# Copyright (c) 2010, Google Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# A module for parsing results.html files generated by old-run-webkit-tests

from webkitpy.thirdparty.BeautifulSoup import BeautifulSoup, SoupStrainer


# FIXME: This should be unified with all the layout test results code in the layout_tests package
# This doesn't belong in common.net, but we don't have a better place for it yet.
def path_for_layout_test(test_name):
    return "LayoutTests/%s" % test_name


# FIXME: This should be unified with all the layout test results code in the layout_tests package
# This doesn't belong in common.net, but we don't have a better place for it yet.
class LayoutTestResults(object):
    """This class knows how to parse old-run-webkit-tests results.html files."""

    stderr_key = u'Tests that had stderr output:'
    fail_key = u'Tests where results did not match expected results:'
    timeout_key = u'Tests that timed out:'
    crash_key = u'Tests that caused the DumpRenderTree tool to crash:'
    missing_key = u'Tests that had no expected results (probably new):'

    expected_keys = [
        stderr_key,
        fail_key,
        crash_key,
        timeout_key,
        missing_key,
    ]

    @classmethod
    def _parse_results_html(cls, page):
        if not page:
            return None
        parsed_results = {}
        tables = BeautifulSoup(page).findAll("table")
        for table in tables:
            table_title = unicode(table.findPreviousSibling("p").string)
            if table_title not in cls.expected_keys:
                # This Exception should only ever be hit if run-webkit-tests changes its results.html format.
                raise Exception("Unhandled title: %s" % table_title)
            # We might want to translate table titles into identifiers before storing.
            parsed_results[table_title] = [unicode(row.find("a").string) for row in table.findAll("tr")]

        return parsed_results

    @classmethod
    def results_from_string(cls, string):
        parsed_results = cls._parse_results_html(string)
        if not parsed_results:
            return None
        return cls(parsed_results)

    def __init__(self, parsed_results):
        self._parsed_results = parsed_results

    def parsed_results(self):
        return self._parsed_results

    def failing_tests(self):
        failing_keys = [self.fail_key, self.crash_key, self.timeout_key]
        return sorted(sum([tests for key, tests in self._parsed_results.items() if key in failing_keys], []))
