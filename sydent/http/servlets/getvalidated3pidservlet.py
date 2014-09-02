# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# Copyright 2014 matrix.org
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

from twisted.web.resource import Resource

from sydent.http.servlets import jsonwrap, require_args
from sydent.db.valsession import ThreePidValSessionStore
from sydent.validators import SessionExpiredException, IncorrectClientSecretException, InvalidSessionIdException,\
    SessionNotValidatedException

class GetValidated3pidServlet(Resource):
    isLeaf = True

    def __init__(self, syd):
        self.sydent = syd

    @jsonwrap
    def render_GET(self, request):
        err = require_args(request, ('sid', 'clientSecret'))
        if err:
            return err

        sid = request.args['sid'][0]
        clientSecret = request.args['clientSecret'][0]

        valSessionStore = ThreePidValSessionStore(self.sydent)

        noMatchError = {'errcode': 'M_NO_VALID_SESSION',
                        'error': "No valid session was found matching that sid and client secret"}

        try:
            s = valSessionStore.getValidatedSession(sid, clientSecret)
        except IncorrectClientSecretException:
            return noMatchError
        except SessionExpiredException:
            return {'errcode': 'M_SESSION_EXPIRED',
                    'error': "This validation session has expired: call requestToken again"}
        except InvalidSessionIdException:
            return noMatchError
        except SessionNotValidatedException:
            return {'errcode': 'M_SESSION_NOT_VALIDATED',
                    'error': "This validation session has not yet been completed"}

        return { 'medium': s.medium, 'address': s.address, 'validatedAt': s.mtime }