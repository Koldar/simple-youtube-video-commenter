import argparse
import logging
import random
import sys
import json
import time

import simple_youtube_video_commenter as commenter

CLIENT_SECRET_FILE_PATTERN = r"client_secret.json"


def _parse_options(args):
    parser = argparse.ArgumentParser(prog="simple-youtube-video-commenter", description="""
    A small utility that just create a new comment on the comment section of a single video.
    It is BY DESIGN simple, since I don't want developers to spam several video via several messages.   
    """, epilog=f"Massimo Bono Copyright 2021, version={commenter.version.VERSION}")

    parser.add_argument("--videoURL", type=str, required=True, help="""
    The url of the video that you want to comment
    """)
    parser.add_argument("--channelURL", type=str, required=True, help="""
        The url of the channel that has uploaded the video that you want to comment
        """)
    parser.add_argument("--text", type=str, required=False, help="""
        text of the comment to add. Do not use {} inside the comment, since we use it to format the string.
        You can use {next_id} to fetch an incremental id w.r.t. all the comments you have posted. Such an id is stored in
        data.json
    """)
    parser.add_argument("--textLineFile", type=str, required=False, help="""
            A file contaning several line. Each line represents a different comment. When publishing a comment, we
            randomly choose one of them. Each line is the same of "text". Muttually exclusive with "text"
        """)
    parser.add_argument("--clientSecretFile", type=str, required=False, default=CLIENT_SECRET_FILE_PATTERN, help=f"""
        File where the file is in the CWD. Follows python regex. Defaults to {CLIENT_SECRET_FILE_PATTERN}
    """)
    parser.add_argument("--oauth2File", type=str, required=False, default="oauth2.json", help=f"""
            File representing the oauth2.json. Default to "oauth2.json"
        """)
    parser.add_argument("--dataJsonFile", type=str, required=False, default="data_file.json", help=f"""
        File representing the persistence storage of this utility. Default to "data_file.json".
    """)
    parser.add_argument("--discoveryDocumentFile", type=str, required=False, default="youtube-v3-discoverydocument.json", help=f"""
        File representing the document file (used for testing only)
    """)

    parser.add_argument("--version", action="store_true", help="""
        Fetch the version of this utility
    """)

    return parser.parse_args(args)


def fetch_file(text: str, text_line_file: str) -> str:
    if text_line_file is not None:
        with open(text_line_file, mode="r", encoding="utf8") as f:
            lines = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), f.readlines())))
            index = random.randrange(0, len(lines))
            return lines[index]
    else:
        return text


def main():
    random.seed(time.time())
    options = _parse_options(sys.argv[1:])

    if options.version:
        print(options.version)
        sys.exit(0)

    logging.basicConfig(level="INFO")

    model = commenter.SimpleYoutubeVideoCommenter(
        client_secret_pattern=str(options.clientSecretFile),
        oauth2_file=str(options.oauth2File),
        logging_level="INFO",
        data_json_file=options.dataJsonFile,
        discovery_document_file=options.discoveryDocumentFile
    )

    text = fetch_file(options.text, options.textLineFile)

    model.insert_comment(
        channel_url=options.channelURL,
        video_url=options.videoURL,
        text=text,
    )
    logging.info("DONE!")


if __name__ == "__main__":
    main()
