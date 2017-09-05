#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2017 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

BASE_URL = "http://localhost:8080/"
""" The default base URL to be used when no other
base URL value is provided to the constructor """

CLIENT_ID = None
""" The default value to be used for the client id
in case no client id is provided to the api client """

CLIENT_SECRET = None
""" The secret value to be used for situations where
no client secret has been provided to the client """

REDIRECT_URL = "http://localhost:8080/oauth"
""" The redirect URL used as default (fallback) value
in case none is provided to the api (client) """

SCOPE = ("admin", "user")
""" The list of permissions to be used to create the
scope string for the oauth value """

class API(appier.OAuth2API):

    def __init__(self, *args, **kwargs):
        appier.OAuth2API.__init__(self, *args, **kwargs)
        self.base_url = appier.conf("ADMIN_BASE_URL", BASE_URL)
        self.client_id = appier.conf("ADMIN_ID", CLIENT_ID)
        self.client_secret = appier.conf("ADMIN_SECRET", CLIENT_SECRET)
        self.redirect_url = appier.conf("ADMIN_REDIRECT_URL", REDIRECT_URL)
        self.scope = appier.conf("ADMIN_SCOPE", SCOPE)
        self.base_url = kwargs.get("base_url", self.base_url)
        self.client_id = kwargs.get("client_id", self.client_id)
        self.client_secret = kwargs.get("client_secret", self.client_secret)
        self.redirect_url = kwargs.get("redirect_url", self.redirect_url)
        self.scope = kwargs.get("scope", self.scope)
        self.access_token = kwargs.get("access_token", None)
        self.session_id = kwargs.get("session_id", None)
        self.tokens = kwargs.get("tokens", None)

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        auth = kwargs.pop("auth", True)
        token = kwargs.pop("token", False)
        if auth: kwargs["session_id"] = self.get_session_id()
        if token: kwargs["access_token"] = self.get_access_token()

    def get_session_id(self):
        if self.session_id: return self.session_id
        return self.oauth_login()

    def auth_callback(self, params, headers):
        if not self._has_mode(): raise appier.APIAccessError(
            message = "Session expired or authentication issues"
        )
        self.session_id = None
        session_id = self.get_session_id()
        params["session_id"] = session_id

    def oauth_authorize(self, state = None):
        url = self.base_url + "admin/oauth/authorize"
        values = dict(
            client_id = self.client_id,
            redirect_uri = self.redirect_url,
            response_type = "code",
            scope = " ".join(self.scope)
        )
        if state: values["state"] = state
        data = appier.legacy.urlencode(values)
        url = url + "?" + data
        return url

    def oauth_access(self, code):
        url = self.base_url + "admin/oauth/access_token"
        contents = self.post(
            url,
            auth = False,
            token = False,
            client_id = self.client_id,
            client_secret = self.client_secret,
            grant_type = "authorization_code",
            redirect_uri = self.redirect_url,
            code = code
        )
        self.access_token = contents["access_token"]
        self.trigger("access_token", self.access_token)
        return self.access_token

    def oauth_login(self):
        url = self.base_url + "admin/oauth/login"
        contents = self.get(url, callback = False, auth = False, token = True)
        self.username = contents.get("username", None)
        self.session_id = contents.get("session_id", None)
        self.tokens = contents.get("tokens", None)
        self.trigger("auth", contents)
        return self.session_id

    def ping(self):
        url = self.base_url + "api/admin/ping"
        contents = self.get(url, auth = False)
        return contents

    def me_account(self):
        url = self.base_url + "api/admin/accounts/me"
        contents = self.get(url)
        return contents
