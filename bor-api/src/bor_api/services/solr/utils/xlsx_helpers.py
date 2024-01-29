# Copyright © 2023 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""BOR solr xlsx methods."""
import os
from http import HTTPStatus
from uuid import uuid4

import xlsxwriter
from flask import make_response


def xlsx_response(results: dict):
    """Return the xlsx response containing the given results."""
    temp_name = uuid4()
    workbook = xlsxwriter.Workbook(f'tmp-excel/{temp_name}.xlsx')
    bold = workbook.add_format({'bold': True})

    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Name', bold)
    worksheet.write('B1', 'Address', bold)
    worksheet.write('C1', 'Postal code', bold)
    worksheet.write('D1', 'Roles', bold)
    worksheet.write('E1', 'Effective Dates Starting', bold)
    worksheet.write('F1', 'Effective Dates Ending', bold)
    worksheet.write('G1', 'Business Name', bold)
    worksheet.write('H1', 'Incorporation Number', bold)
    worksheet.write('I1', 'Business Number', bold)
    worksheet.write('J1', 'Business State', bold)
    worksheet.write('K1', 'Business Email', bold)

    # Iterate over the data and write it out row by row.
    for result, index in zip(results, range(1, len(results) + 1)):
        worksheet.write(index, 0, result['legalName'])
        if addresses := result.get('entityAddresses'):
            street = addresses[0].get('streetAddress') or ''
            city = addresses[0].get('addressCity') or ''
            region = addresses[0].get('addressRegion') or ''
            country = addresses[0].get('addressCountry') or ''
            worksheet.write(index, 1, f'{street} \n{city} {region} \n{country}')
            worksheet.write(index, 2, addresses[0].get('postalCode') or '')
        if roles := result.get('roles'):
            worksheet.write(index, 3, roles[0]['roleType'])
            # role dates (lop off the timestamp)
            start = roles[0]['roleDates'][0].get('start', 'Unknown')[:10]
            end = roles[0]['roleDates'][0].get('end', 'Current')[:10]
            worksheet.write(index, 4, start)
            worksheet.write(index, 5, end)

            # business details
            worksheet.write(index, 6, roles[0].get('relatedName') or '')
            worksheet.write(index, 7, roles[0].get('relatedIdentifier') or '')
            worksheet.write(index, 8, roles[0].get('relatedBN') or '')
            worksheet.write(index, 9, roles[0].get('relatedState') or '')
            worksheet.write(index, 10, roles[0].get('relatedEmail') or '')

    workbook.close()

    with open(f'tmp-excel/{temp_name}.xlsx', 'rb') as excel_file:
        resp = make_response(excel_file.read(), HTTPStatus.OK)
        excel_file.close()
    os.remove(f'tmp-excel/{temp_name}.xlsx')

    resp.headers['Content-Disposition'] = 'attachment; filename=director_search.xlsx'
    resp.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return resp
