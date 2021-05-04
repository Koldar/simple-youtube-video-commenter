import argparse
import logging
import sys
import json

import simple_youtube_video_commenter as commenter

CLIENT_SECRET_FILE_PATTERN = r"^client_secret.*\.json$"


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
    parser.add_argument("--text", type=str, required=True, help="""
        text of the comment to add. Do not use {} inside the comment, since we use it to format the string.
        You can use {next_id} to fetch an incremental id w.r.t. all the comments you have posted. Such an id is stored in
        data.json
    """)
    parser.add_argument("--clientSecretFile", type=str, required=False, default=CLIENT_SECRET_FILE_PATTERN, help=f"""
        Pattern where the file is in the CWD. Follows python regex. Defaults to {CLIENT_SECRET_FILE_PATTERN}
    """)
    parser.add_argument("--oauth2File", type=str, required=False, default="oauth2.json", help=f"""
            File representing the oauth2.json. Default to "oauth2.json"
        """)
    parser.add_argument("--dataJsonFile", type=str, required=False, default="data_file.json", help=f"""
        File representing the persistence storage of this utility. Default to "data_file.json".
    """)

    parser.add_argument("--version", action="store_true", help="""
        Fetch the version of this utility
    """)

    return parser.parse_args(args)


def main():
    options = _parse_options(sys.argv[1:])

    if options.version:
        print(options.version)
        sys.exit(0)

    logging.basicConfig(level="INFO")

    model = commenter.SimpleYoutubeVideoCommenter(
        client_secret_pattern=str(options.clientSecretFile),
        oauth2_file=str(options.oauth2File),
        logging_level="INFO",
        data_json_file=options.dataJsonFile
    )
    model.insert_comment(
        channel_url=options.channelURL,
        video_url=options.videoURL,
        text=options.text
    )
    logging.info("DONE!")


if __name__ == "__main__":
    main()
