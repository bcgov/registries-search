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
"""Enum Utilities."""

from enum import Enum, EnumMeta  # pylint: disable=W0611;


class BaseMeta(EnumMeta):
    """Meta class for the enum."""

    def __contains__(self, other):  # noqa: N804
        """Return True if 'in' the Enum."""
        try:
            self(other)
        except ValueError:
            return False

        return True


class BaseEnum(str, Enum, metaclass=BaseMeta):
    """Replace autoname from Enum class."""

    @classmethod
    def get_enum_by_value(cls, value: str) -> str | None:
        """Return the enum by value."""
        for enum_value in cls:
            if enum_value.value == value:
                return enum_value
        return None

    @classmethod
    def get_enum_by_name(cls, value: str) -> str | None:
        """Return the enum by value."""
        for enum_value in cls:
            if enum_value.name == value:
                return enum_value
        return None

    #pragma warning disable S5720;
    # disable sonar cloud complaining about this signature
    def _generate_next_value_(name, start, count, last_values):  # pylint: disable=E0213;# noqa: N805
        """Return the name of the key."""
        return name
