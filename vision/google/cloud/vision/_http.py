# Copyright 2016 Google Inc.
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

"""HTTP Client for interacting with the Google Cloud Vision API."""

from google.cloud import _http

from google.cloud.vision.annotations import Annotations
from google.cloud.vision.feature import Feature


class Connection(_http.JSONConnection):
    """A connection to Google Cloud Vision via the JSON REST API.

    :type client: :class:`~google.cloud.vision.client.Client`
    :param client: The client that owns the current connection.
    """

    API_BASE_URL = 'https://vision.googleapis.com'
    """The base of the API call URL."""

    API_VERSION = 'v1'
    """The version of the API, used in building the API call's URL."""

    API_URL_TEMPLATE = '{api_base_url}/{api_version}{path}'
    """A template for the URL of a particular API call."""


class _HTTPVisionAPI(object):
    """Vision API for interacting with the JSON/HTTP version of Vision

    :type client: :class:`~google.cloud.core.client.Client`
    :param client: Instance of ``Client`` object.
    """

    def __init__(self, client):
        self._client = client
        self._connection = client._connection

    def annotate(self, images):
        """Annotate an image to discover it's attributes.

        :type images: list of :class:`~google.cloud.vision.image.Image`
        :param images: A list of ``Image``.

        :rtype: list
        :returns: List of :class:`~googe.cloud.vision.annotations.Annotations`.
        """
        requests = []
        for image, features in images:
            requests.append(_make_request(image, features))
        data = {'requests': requests}
        api_response = self._connection.api_request(
            method='POST', path='/images:annotate', data=data)
        responses = api_response.get('responses')
        return [Annotations.from_api_repr(response) for response in responses]


def _make_request(image, features):
    """Prepare request object to send to Vision API.

    :type image: :class:`~google.cloud.vision.image.Image`
    :param image: Instance of ``Image``.

    :type features: list of :class:`~google.cloud.vision.feature.Feature`
    :param features: Either a list of ``Feature`` instances or a single
                     instance of ``Feature``.

    :rtype: dict
    :returns: Dictionary prepared to send to the Vision API.
    """
    if isinstance(features, Feature):
        features = [features]

    feature_check = (isinstance(feature, Feature) for feature in features)
    if not any(feature_check):
        raise TypeError('Feature or list of Feature classes are required.')

    return {
        'image': image.as_dict(),
        'features': [feature.as_dict() for feature in features],
    }
