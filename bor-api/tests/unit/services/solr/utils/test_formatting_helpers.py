# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests to ensure that the Solr Service format helpers work as expected."""
import pytest

from bor_api.services.bor_solr.fields import EntityField
from bor_api.services.base_solr.utils import parse_facets, prep_query_str, prep_query_str_adv


@pytest.mark.parametrize(
    "test_name,facet_data,expected",
    [
        (
            "test_1",
            {
                "facets": {
                    EntityField.LEGAL_TYPE.value: {
                        "buckets": [
                            {"val": "BEN", "count": 23},
                            {"val": "CP", "count": 10},
                            {"val": "SP", "count": 102},
                        ]
                    },
                    EntityField.STATE.value: {
                        "buckets": [{"val": "ACTIVE", "count": 23}, {"val": "HISTORICAL", "count": 10}]
                    },
                }
            },
            {
                "fields": {
                    EntityField.LEGAL_TYPE.value: [
                        {"value": "BEN", "count": 23},
                        {"value": "CP", "count": 10},
                        {"value": "SP", "count": 102},
                    ],
                    EntityField.STATE.value: [{"value": "ACTIVE", "count": 23}, {"value": "HISTORICAL", "count": 10}],
                }
            },
        ),
    ],
)
def test_parse_facets(test_name, facet_data, expected):
    """Assert the parse_facets function works as expected."""
    facet_info = parse_facets(facet_data)
    assert facet_info == expected


@pytest.mark.parametrize(
    "test_name,value,expected",
    [
        ("test_basic_string", "test", "test"),
        ("test_none", None, ""),
        ("test_spec_char_[]", "test[square]bracket", "test square bracket"),
        ("test_spec_char_!", "test!exclamation!", "test exclamation "),
        ("test_spec_char_()", "(test)brackets", " test brackets"),
        ('test_spec_char_"', 'test"double" quotes', "test double  quotes"),
        ("test_spec_char_~", "test ~squiggle", "test  squiggle"),
        ("test_spec_char_*", "test asterix*", "test asterix "),
        ("test_spec_char_?", "?test? question?", " test  question "),
        ("test_spec_char_:", "test:colon", "test colon"),
        ("test_spec_char_/", "test/forward / slash", "test forward   slash"),
        ("test_spec_char_\\", "test\\backwards \ slash", "test backwards   slash"),
        ("test_spec_char_=", "test=equals", "test equals"),
        ("test_spec_char_{}", "test{curly} {brackets}", "test curly   brackets "),
        ("test_spec_char_^", "^test^carrot", " test carrot"),
        ("test_spec_char_%", "test %percent", "test  percent"),
        ("test_spec_char_`", "test`back tic`", "test back tic "),
        ("test_spec_char_#", "test #hashtag", "test  hashtag"),
        ("test_spec_char_|", "test|bar", "test bar"),
        ("test_spec_char_<>", "test>greater less <than", "test greater less  than"),
        ("test_spec_char_,", "test,comma", "test comma"),
        ("test_spec_char_.", "test.period.", "test period "),
        ("test_spec_char_@", "test@at", "test at"),
        ("test_spec_char_$", "test $dollar $ign", "test  dollar  ign"),
        ("test_spec_char_;", "test;semicolon;", "test semicolon "),
        ("test_spec_char__", "test_underscore", "test underscore"),
        ("test_spec_char_-", "test-dash - dash", "test dash   dash"),
        ("test_spec_char_multi", "test@multiple! [specials]", "test multiple   specials "),
        ("test_only_spec_char", '[]!()"~*?:/\={}^%`#|<>,.@$;_\-', "\\*"),
        ("test_handled_spec_char_+", "test+plus", "test \\+ plus"),
        ("test_handled_spec_char_++", "test+plus++plus", "test \\+ plus \\++ plus"),
        ("test_handled_spec_char_&", "test&ampersand", "test \\& ampersand"),
        ("test_handled_spec_char_&&", "test double&&ampersand", "test double \\&& ampersand"),
        (
            "test_handled_spec_char_mix",
            "test+handled &&spec++char & mix",
            "test \\+ handled  \\&& spec \\++ char  \\&  mix",
        ),
    ],
)
def test_prep_query_str(test_name, value, expected):
    """Assert the prep_query_str function works as expected."""
    assert prep_query_str(value) == expected


@pytest.mark.parametrize(
    "test_name,value,expected",
    [
        ("test_basic_string", "test", "test"),
        ("test_none", None, ""),
        ("test_uppercase", "test AND test OR NOT", "test and test or not"),
        ("test_spec_double_&", "& test&&test& &&", "& test&test& &"),
        ("test_spec_double_+", "test++test++", "test+test+"),
        ("test_spec_begin_+", "+ +test+test+ +", "\\+ \\+test+test+ \\+"),
        ("test_spec_begin_-", "- -test-test- -", "\\- \\-test-test- \\-"),
        ("test_spec_begin_/", "/ /test/test/ /", "\\/ \\/test/test/ \\/"),
        ("test_spec_begin_~", "~ ~test~test~ ~", "\\~ \\~test\\~test\\~ \\~"),
        ("test_spec_begin_!", "! !test!test! !", "\\! \\!test!test! \\!"),
        ('test_spec_all_"', '" "test"test" "', '\\" \\"test\\"test\\" \\"'),
        ("test_spec_all_:", ": :test:test: :", "\\: \\:test\\:test\\: \\:"),
        ("test_spec_all_[]", "[ ]test[test[ ]", "\\[ \\]test\\[test\\[ \\]"),
        ("test_spec_all_~", "~ ~test~test~ ~", "\\~ \\~test\\~test\\~ \\~"),
        ("test_spec_all_<>", "> <test>test< >", "\\> \\<test\\>test\\< \\>"),
        ("test_spec_all_?", "? ?test?test? ?", "\\? \\?test\\?test\\? \\?"),
        ("test_spec_rmv_^", "^ ^test^test^ ^", "testtest"),
        ("test_spec_rmv_\\", "\\ \\test\\test\\ \\", "testtest"),
        ("test_spec_rmv_|", "| |test||test| |", "testtest"),
        ("test_spec_rmv_^", "^ ^test^^test^ ^", "testtest"),
        ("test_spec_rmv_{}", "{ }test{t}est{ }", "testtest"),
        ("test_spec_rmv_()", "( )test(t)est( )", "testtest"),
        ("test_lower", "TESTTEST", "testtest"),
    ],
)
def test_prep_query_str_adv(test_name, value, expected):
    """Assert the prep_query_str_adv function works as expected."""
    assert prep_query_str_adv(value) == expected
