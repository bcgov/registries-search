import datetime
from uuid import uuid4

from freezegun import freeze_time

# from search_api.services.sce import SimpleCloudEvent
from simple_cloudevent import SimpleCloudEvent, SIMPLE_CE_SPEC_VERSION


from tests.unit.request_handlers.test_document_access_request_handler import DOCUMENT_ACCESS_REQUEST_TEMPLATE


def test_create_cloud_event_example():

    from search_api.enums import DocumentType

    now = datetime.datetime(1970, 1, 1, 0, 0).replace(tzinfo=datetime.timezone.utc)
    with freeze_time(now):
        # setup
        msg_id = str(uuid4())
        identifier = 'BC1234567'
        source = 'registry-search'
        subject = 'document-request'
        account_id = 5678
        user = 'bcsc/twolpert'
        time = now
        key1 = str(uuid4())


        # this is what we want ou CE to have as
        # far as data and structure
        base_dict = {
            'id': msg_id,
            'source': source,
            'subject': subject,
            'time': time,
        }
        document_request = {
            'businessIdentifier': identifier,
            'accountId': account_id,
            'user': user,
            'documents': [
                {'documentKey': key1,
                 'documentType': DocumentType.BUSINESS_SUMMARY_FILING_HISTORY.value},
            ]
        }
        base_dict['data'] = document_request
        
        # test
        ce = SimpleCloudEvent(**base_dict)

        # check
        assert isinstance(ce, SimpleCloudEvent)
        assert ce.specversion == SIMPLE_CE_SPEC_VERSION

        assert ce.id == msg_id
        assert ce.source == source
        assert ce.subject == subject
        assert ce.time == now

        assert ce.data
        assert ce.data.get('businessIdentifier')
        assert ce.data.get('accountId')
        assert ce.data.get('user')

        for doc_req in ce.data.get('documents'):
            assert doc_req.get('documentKey')
            assert doc_req.get('documentType') in DocumentType


def test_create_doc_request_ce(client, session, set_env, jwt, mocker):

    from search_api.enums import DocumentType
    from search_api.services.document_services import create_doc_request_ce
    from flask import current_app, g

    from search_api.models import DocumentAccessRequest, User
    from search_api.request_handlers.document_access_request_handler import save_request

    now = datetime.datetime(1970, 1, 1, 0, 0).replace(tzinfo=datetime.timezone.utc)

    set_env('SERVICE_NAME', 'registry-search')
    set_env('SERVICE_DOCUMENT_SUBJECT', 'document-request')
    with freeze_time(now):
        # setup
        identifier = 'BC1234567'
        source = 'registry-search'
        subject = 'document-request'
        account_id = 5678
        user_sub = f'bcsc{str(uuid4())}'[:36]
        time = now
        key1 = str(uuid4())


        # this is what we want ou CE to have as
        # far as data and structure
        # base_dict = {
        #     'id': msg_id,
        #     'source': source,
        #     'subject': subject,
        #     'time': time,
        # }
        g.jwt_oidc_token_info={}
        user = User(username='username', firstname='firstname', lastname='lastname', sub=user_sub, iss='iss', idp_userid='123')
        user.save()
        mocker.patch('search_api.models.User.get_or_create_user_by_jwt', return_value=user)
        document_access_request = save_request(1, 1, DOCUMENT_ACCESS_REQUEST_TEMPLATE)
        
        # test
        ce = create_doc_request_ce(document_access_request)

        # check
        assert isinstance(ce, SimpleCloudEvent)
        assert ce.specversion == SIMPLE_CE_SPEC_VERSION

        assert isinstance(ce.id, str)
        assert ce.source == source
        assert ce.subject == subject
        assert ce.time == now

        assert ce.data
        assert ce.data.get('businessIdentifier')
        assert ce.data.get('accountId')
        assert ce.data.get('user')

        for doc_req in ce.data.get('documents'):
            assert doc_req.get('documentKey')
            assert doc_req.get('documentType') in DocumentType
