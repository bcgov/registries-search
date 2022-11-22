from http import HTTPStatus

from freezegun import freeze_time

# from search_api.models import Document, DocumentAccessRequest
# from search_api.services.document_services import document_creation_request
# from search_api.utils.datetime import datetime

# def test_place_document_creation_on_queue():
#     '''Test that a document ceration request can get place on the queue.'''

#     business_identifier = 'FM123456789'
#     account_id = '123456789'
#     user_id = 12
#     business_name = 'test business name'

#     # freeze time
#     # with freeze_time(now):
#     # setup
#     document_access_request: DocumentAccessRequest = DocumentAccessRequest(
#         business_identifier=business_identifier,
#         account_id=account_id,
#         _submitter_id=user_id,
#         submission_date=datetime.utcnow(),
#         business_name=business_name
#     )
#     for doc in request_json.get('documentAccessRequest', {}).get('documents', []):
#         document_type = DocumentType.get_enum_by_name(doc.get('type'))
#         document = Document(
#             document_type=document_type.value,
#             document_key=_generate_key()
#         )
#         document_access_request.documents.append(document)

#     # test
#     response, code = document_creation_request(document_access_request, request_json, business_json)

#     assert not response
#     assert code is HTTPStatus.OK