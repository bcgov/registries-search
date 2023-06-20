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
"""Tests to assure the SolrSynonymList Class."""
import pytest

from sqlalchemy.exc import IntegrityError

from bor_api.models import SolrSynonymList


def test_solr_synonym_list(session):
    """Assert that a SolrSynonymList can be stored in the service."""
    synonym_list = SolrSynonymList(synonym='robert', synonym_list=['bob', 'robert'])

    session.add(synonym_list)
    session.commit()

    assert synonym_list.synonym is not None
    assert synonym_list.synonym_list is not None
    assert synonym_list.last_update_date is not None


def test_solr_synonym_list_no_dupes(session):
    """Assert that no dupe mappings are allowed."""
    with pytest.raises(IntegrityError):
        SolrSynonymList(synonym='robert', synonym_list=['bob', 'robert']).save()
        SolrSynonymList(synonym='robert', synonym_list=['bobby', 'robert']).save()


@pytest.mark.parametrize('test_name, synonyms, search_value, expected', [
    ('test_found', ['robert', 'bob', 'robby', 'roberts'], 'robert', 'robert'),
    ('test_not_found', ['robert', 'bob', 'robby', 'roberts'], 'rober', None)
])
def test_find_by_synonym(session, test_name, synonyms, search_value, expected):
    """Assert that the find_by_synonym method works as expected."""
    for synonym in synonyms:
        session.add(SolrSynonymList(synonym=synonym, synonym_list=['1', '2', synonym]))
    session.commit()
    
    result = SolrSynonymList.find_by_synonym(search_value)
    assert (not expected and not result) or result.synonym == expected


@pytest.mark.parametrize('test_name, synonyms, search_value, expected', [
    ('test_basic', ['robert', 'bob'], 'robert', ['robert']),
    ('test_basic_multi_match', ['robert', 'bob', 'robby', 'roberts'], 'rob', ['robert','robby','roberts']),
    ('test_basic_no_match', ['robert', 'bob', 'robby', 'roberts'], 'ob', []),
    ('test_multi_word', ['british columbia', 'bc', 'canada'], 'british', ['british columbia']),
    ('test_multi_word_multi_match', ['british columbia', 'british', 'canada', 'britania', 'british properties'], 'british', ['british columbia', 'british', 'british properties']),
    ('test_multi_word_no_match', ['british columbia', 'british', 'canada', 'britania'], 'columbia', []),
])
def test_find_all_beginning_with_phrase(session, test_name, synonyms, search_value, expected):
    """Assert that the find_all_beginning_with_phrase method works as expected."""
    for synonym in synonyms:
        session.add(SolrSynonymList(synonym=synonym, synonym_list=['1', '2', synonym]))
    session.commit()
    
    results = SolrSynonymList.find_all_beginning_with_phrase(search_value)
    assert len(results) == len(expected)
    for result in results:
        assert result.synonym in expected
