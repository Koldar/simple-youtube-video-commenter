import json
import logging
import os
import re
import threading
from typing import Any, Tuple, Dict
from urllib import parse as urllib_parse

import httplib2
import oauth2client
from googleapiclient.discovery import build_from_document
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from oauth2client.file import Storage

import simple_youtube_video_commenter as commenter


class SimpleYoutubeVideoCommenter(object):
    """
    Model of the utility.

    Heavily inpired by
    :see: https://github.com/youtube/api-samples/blob/master/python/comment_handling.py
    """

    YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    """
    This OAuth 2.0 access scope allows for full read/write access to the
    authenticated user's account and requires requests to use an SSL connection.
    """

    def __init__(self, client_secret_pattern: str, oauth2_file: str, logging_level: str, data_json_file: str, discovery_document_file: str):
        super().__init__()
        self.client_secret_file = client_secret_pattern
        self.discovery_document_file = discovery_document_file
        self.oauth2_file = oauth2_file
        self.logging_level = logging_level
        self.data_json_file = data_json_file
        self.data_cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if not os.path.exists(self.data_json_file):
            set_cache = dict(next_id=0)
            with open(self.data_json_file, mode="w", encoding="utf8") as f:
                f.write(json.dumps(set_cache, indent=2))
        with open(self.data_json_file, mode="r", encoding="utf8") as f:
            return json.loads(f.read())

    def _has_from_cache(self, name: str) -> bool:
        return name in self.data_cache

    def _get_from_cache(self, name: str) -> Any:
        if name not in self.data_cache:
            raise ValueError(f"{name} in cache not found!")
        return self.data_cache[name]

    def _set_in_cache(self, name: str, value: Any):
        self.data_cache[name] = value
        with open(self.data_json_file, mode="w", encoding="utf8") as f:
            f.write(json.dumps(self.data_cache, indent=2))

    def _fetch_next_id_and_increase(self) -> int:
        if self._has_from_cache("next_id"):
            result = int(self._get_from_cache("next_id"))
            self._set_in_cache("next_id", result + 1)
            return result
        else:
            self._set_in_cache("next_id", 1)
            return 0

    def _get_client_secret(self) -> str:
        """

        :return: path to client secret
        """

        return os.path.abspath(self.client_secret_file)

    def _get_authenticated_service(self):
        """
        authenticate to the google service. Assume there are the credentials in client_secret

        :return:
        """

        client_secret_json = self._get_client_secret()
        flow = flow_from_clientsecrets(
            filename=client_secret_json,
            scope=self.YOUTUBE_READ_WRITE_SSL_SCOPE,
            message="""Client secret is not present. 
                See https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
            """)

        lock_variable = self.oauth2_file
        storage = Storage(lock_variable)

        credentials = storage.get()

        if credentials is None or credentials.invalid:
            args = commenter.FlowFlag(
                auth_host_name="https://oauth2.googleapis.com/token",
                auth_host_port=80,
                noauth_local_webserver=True,
                logging_level=self.logging_level
            )
            credentials = run_flow(flow, storage, args)

        # Trusted testers can download this discovery document from the developers page
        # and it should be in the same directory with the code.
        with open(self.discovery_document_file, "r", encoding="utf8") as f:
            doc = f.read()
            return build_from_document(doc, http=credentials.authorize(httplib2.Http()))

    def _get_channel_id_from_url(self, url: str) -> str:
        """
        get the channel id from the url (which is after the "v")
        :param url:
        :return:
        :see https://stackoverflow.com/a/21584580/1887602:
        """
        paths = urllib_parse.urlsplit(url).path
        return paths.split("/")[-1]

    def _get_video_id_from_url(self, url: str) -> str:
        """
        get the video id from the url (which is after the "v")
        :param url:
        :return:
        :see https://stackoverflow.com/a/21584580/1887602:
        """
        query = dict(urllib_parse.parse_qs(urllib_parse.urlsplit(url).query))
        return query["v"][0]

    def _get_video_parent_id(self, youtube, video_id: str):
        """
        get video id parent id
        :param youtube:
        :param video_id:
        :return:
        """
        results = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            textFormat="plainText"
        ).execute()

        return results["items"][0]["id"]

    def insert_comment(self, channel_url: str, video_url: str, text: str):
        """
        insert a new comment as you
        :param channel_url: url of the channel that has uploaded the video you want to comment
        :param video_url: url of the video
        :param text:
        :return:
        """
        logging.info(f"fetching the channel id from url {channel_url}...")
        channel_id = self._get_channel_id_from_url(channel_url)
        logging.info(f"Got {channel_id}. fetchin video id from video url {video_url}...")
        video_id = self._get_video_id_from_url(video_url)
        logging.info(f"Id is {video_id} authentication to youtube service...")
        youtube = self._get_authenticated_service()
        logging.info(f"polling the structure of the comment threads...")
        parent_id = self._get_video_parent_id(youtube, video_id)
        logging.info(f"fetching latest id and increasing the id in the storage...")
        next_id = self._fetch_next_id_and_increase()
        text = text.format(next_id=next_id)
        logging.info(f"inserting comment...")
        output, author, text, comment = self._insert_comment(
            youtube=youtube,
            channel_id=channel_id,
            video_id=video_id,
            text=text
        )
        logging.info(f"we have added a new comment in \"{video_url}\" as user \"{author}\": {text}")

    def _insert_comment(self, youtube, channel_id, video_id, text) -> [Any, str, str, str]:
        """

        :param youtube:
        :param channel_id:
        :param video_id:
        :param text:
        :return: tuple. output of hte insertion, author, text to add and comment
        """
        insert_result = youtube.commentThreads().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    channelId=channel_id,
                    videoId=video_id,
                    topLevelComment=dict(
                        snippet=dict(
                            textOriginal=text
                        )
                    )
                )
            )
        ).execute()
        logging.info(f"Comment insertion generated the following output:")
        logging.info(insert_result)

        comment = insert_result["snippet"]["topLevelComment"]
        author = comment["snippet"]["authorDisplayName"]
        text = comment["snippet"]["textDisplay"]
        return insert_result, author, text, comment

    def _reply_to_comment(self, youtube, parent_id, text: str) -> Tuple[Any, str, str]:
        """
        reply to a comment in a comment thrad in the comment section of a video.

        Call the API's comments.insert method to reply to a comment.
        (If the intention is to create a new to-level comment, commentThreads.insert
        method should be used instead.)

        :param parent_id:
        :param text:
        :return: tuple. first si the output of the insertion. seocndi s the author, third is the text passed in input
        """

        insert_result = youtube.comments().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    parentId=parent_id,
                    textOriginal=text
                )
            )
        ).execute()
        logging.info(f"Comment insertion generated the following output:")
        logging.info(insert_result)

        author = insert_result["snippet"]["authorDisplayName"]
        text = insert_result["snippet"]["textDisplay"]

        return insert_result, author, text
