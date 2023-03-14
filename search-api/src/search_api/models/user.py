# Copyright © 2022 Province of British Columbia
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
"""This manages a User record that can be used in an audit trail.

Actual user data is kept in the OIDC and IDP services, this data is
here as a convenience for audit and db reporting.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from flask import current_app

from search_api.exceptions import BusinessException
from search_api.services.authz import user_info
from search_api.utils.auth import jwt

from .db import db


class UserRoles(str, Enum):
    """Enum of the roles used across the domain."""

    SYSTEM = 'system'
    STAFF = 'staff'
    BASIC_USER = 'basic'
    COLIN_SVC = 'colin'
    PUBLIC_USER = 'public_user'


class User(db.Model):
    """Used to hold the audit information for a User of this service."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000), index=True)
    firstname = db.Column(db.String(1000))
    lastname = db.Column(db.String(1000))
    email = db.Column(db.String(1024))
    login_source = db.Column('login_source', db.String(200), nullable=True)
    idp_userid = db.Column(db.String(256), index=True, unique=True)
    sub = db.Column(db.String(36))
    iss = db.Column(db.String(1024))
    creation_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    @property
    def display_name(self):
        """Display name of user; do not show sensitive data like BCSC username.

        If there is actual name info, return that; otherwise username.
        """
        if self.firstname or self.lastname:
            return ' '.join(filter(None, [self.firstname, self.lastname])).strip()

        # parse off idir\ or @idir
        if self.username:
            if self.username[:4] == 'idir':
                return self.username[5:]
            if self.username[-4:] == 'idir':
                return self.username[:-5]

            # do not show services card usernames
            if self.username[:4] == 'bcsc':
                return None

        return self.username if self.username else None

    @classmethod
    def find_by_id(cls, submitter_id: int = None):
        """Return a User if they exist and match the provided submitter id."""
        return cls.query.filter_by(id=submitter_id).one_or_none()

    @classmethod
    def find_by_jwt_token(cls, token: dict):
        """Return a User if they exist and match the provided JWT."""
        return cls.query.filter_by(idp_userid=token.get('idp_userid', 'unknown')).one_or_none()

    @classmethod
    def create_from_jwt_token(cls, token: dict):
        """Create a user record from the provided JWT token.

        Use the values found in the vaild JWT for the realm
        to populate the User audit data
        """
        if token:
            firstname = token.get(current_app.config.get('JWT_OIDC_FIRSTNAME'), None)
            lastname = token.get(current_app.config.get('JWT_OIDC_LASTNAME'), None)
            if token.get('loginSource') == 'BCEID':
                # bceid doesn't use the names from the token so have to get from auth
                auth_user = user_info(jwt.get_token_auth_header())
                firstname = auth_user['firstname']
                lastname = auth_user['lastname']

            user = User(
                username=token.get(current_app.config.get('JWT_OIDC_USERNAME'), None),
                firstname=firstname,
                lastname=lastname,
                iss=token['iss'],
                sub=token['sub'],
                login_source=token.get('loginSource', 'unknown'),
                idp_userid=token.get('idp_userid', 'unknown'),
            )
            # pylint: disable=consider-using-f-string
            current_app.logger.debug('Creating user from JWT:{}; User:{}'.format(token, user))
            db.session.add(user)
            db.session.commit()
            return user
        return None

    @classmethod
    def get_or_create_user_by_jwt(cls, jwt_oidc_token: dict):
        """Return a valid user for audit tracking purposes."""
        # GET existing or CREATE new user based on the JWT info
        try:
            user = User.find_by_jwt_token(jwt_oidc_token)
            current_app.logger.debug(f'finding user: {jwt_oidc_token}')
            if not user:
                current_app.logger.debug(f'didnt find user, attempting to create new user:{jwt_oidc_token}')
                user = User.create_from_jwt_token(jwt_oidc_token)
            elif jwt_oidc_token.get('loginSource') == 'BCEID':  # BCEID doesn't use the jwt values for their name
                auth_user = user_info(jwt.get_token_auth_header())
                if user.firstname != auth_user['firstname']:
                    user.firstname = auth_user['firstname']
                if user.lastname != auth_user['lastname']:
                    user.lastname = auth_user['lastname']
                user.save()
            else:
                # update if there are any values that weren't saved previously or have changed since
                user_keys = [{'jwt_key': current_app.config.get('JWT_OIDC_USERNAME'), 'table_key': 'username'},
                             {'jwt_key': current_app.config.get('JWT_OIDC_FIRSTNAME'), 'table_key': 'firstname'},
                             {'jwt_key': current_app.config.get('JWT_OIDC_LASTNAME'), 'table_key': 'lastname'}]
                for keys in user_keys:
                    value = jwt_oidc_token.get(keys['jwt_key'], None)
                    if value and value != getattr(user, keys['table_key']):
                        current_app.logger.debug(
                            f'found new user value, attempting to update user {keys["table_key"]}:{value}')
                        setattr(user, keys['table_key'], value)
                        user.save()

            return user
        except Exception as err:  # noqa: B902
            current_app.logger.error(err.with_traceback(None))
            raise BusinessException('unable_to_get_or_create_user',
                                    '{"code": "unable_to_get_or_create_user",'
                                    '"description": "Unable to get or create user from the JWT, ABORT"}'
                                    ) from err

    @classmethod
    def find_by_username(cls, username):
        """Return the oldest User record for the provided username."""
        return cls.query.filter_by(username=username).order_by(User.creation_date.desc()).first()

    @classmethod
    def find_by_sub(cls, sub):
        """Return a User based on the unique sub field."""
        return cls.query.filter_by(sub=sub).one_or_none()

    def save(self):
        """Store the User into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Cannot delete User records."""
        return self
        # need to intercept the ORM and stop Users from being deleted
