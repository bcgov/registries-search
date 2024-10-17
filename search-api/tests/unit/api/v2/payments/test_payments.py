import json

from datetime import datetime
from dateutil.relativedelta import relativedelta

# monkeypatching
from search_api.resources.v2.payments.payments import simple_queue
from search_api.services.gcp_auth.auth_service import id_token

from search_api.enums import DocumentType
from search_api.models import Document, DocumentAccessRequest, User
from simple_cloudevent import SimpleCloudEvent


def _create_test_document_request():
    document_access_request = DocumentAccessRequest(
        business_identifier='CP1234567',
        account_id=123,
        submission_date=datetime.utcnow(),
        expiry_date=datetime.now() + relativedelta(days=7)
    )

    user = User(username='username', firstname='firstname', lastname='lastname', sub='sub', iss='iss', idp_userid='123')
    document_access_request.submitter = user

    document = Document(document_type=DocumentType.LETTER_UNDER_SEAL.value, document_key='test')
    document_access_request.documents.append(document)

    document_access_request.save()

    return document_access_request.id


claims = {
    'email': 'test@goole.email.com',
    'email_verified': True,
}
header = {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "flask-jwt-oidc-test-client"
}

def test_cc_payment_success(app, session, client, jwt, monkeypatch):


    def auth_jwt_claims(one, two, audience):
        return claims

    def ce_data(request, wrapped):
        x = SimpleCloudEvent
        x.data = {
            "id": dar_id,
            "statusCode": "COMPLETED",
            "filingIdentifier": "23542355235",
            "corpTypeCode": "BUS"
        }
        return x

    dar_id = _create_test_document_request()

    monkeypatch.setattr(id_token, 'verify_oauth2_token', auth_jwt_claims)
    monkeypatch.setattr(simple_queue, 'get_simple_cloud_event', ce_data)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(jwt.create_jwt(claims, header))
    }
    data = {
        "data": {
            "id": dar_id,
            "statusCode": "COMPLETED",
            "filingIdentifier": "23542355235",
            "corpTypeCode": "BUS"
        },
        "datacontenttype": "application/json",
        "id": "fabc66c4-fb1a-448b-a928-836e58899309",
        "source": "sbc-pay",
        "specversion": "1.0",
        "subject": "payment",
        "time": "2023-07-12T01:33:25.854304+00:00",
        "type": "bc.registry.payment"
    }

    response = client.post('/api/v2/payments/', headers=headers, data=json.dumps(data))
    assert response.status_code == 200
