"""Decision Is All You Need: live demos for the Jatim Developer Day talk about Jev (slides live in Google Slides).

    uv run main.py              # live Jev calls when TYPESAFE_API_KEY is set (env or .env)
    uv run main.py --offline    # never call the API, replay responses cached during rehearsal
    uv run main.py --share      # public link, e.g. to let the audience open it on their phones
"""

import argparse
from pathlib import Path

from dotenv import load_dotenv

from deck import jev
from deck.app import build_app, launch_options

load_dotenv(Path(__file__).resolve().parent / ".env")  # TYPESAFE_API_KEY
demo = build_app()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--offline", action="store_true", help="replay cached Jev responses instead of calling the API")
    parser.add_argument("--share", action="store_true", help="create a public Gradio share link")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    jev.offline = args.offline
    demo.launch(share=args.share, server_port=args.port, inbrowser=True, **launch_options())


if __name__ == "__main__":
    main()
