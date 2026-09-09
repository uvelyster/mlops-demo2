# main.py
import click
import requests

from bs4 import BeautifulSoup

from transformers import pipeline


def extract_url(url: str) -> str:

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    html = requests.get(url, headers=headers, timeout=20)

    html.raise_for_status()

    soup = BeautifulSoup(html.text, "html.parser")

    paragraphs = [
        p.get_text(" ", strip=True)
        for p in soup.find_all("p")
    ]

    return "\n".join(paragraphs)


def load_file(path: str):

    with open(path, encoding="utf-8") as f:
        return f.read()


@click.command()

@click.option("--url", help="URL to summarize")

@click.option("--file", help="Local file")

@click.option(
    "--model",
    required=True,
    help="Local HuggingFace model directory"
)

@click.option(
    "--max-length",
    default=150,
)

@click.option(
    "--min-length",
    default=40,
)

def main(
    url,
    file,
    model,
    max_length,
    min_length,
):

    if not url and not file:
        raise click.UsageError(
            "Specify either --url or --file"
        )

    if url:
        text = extract_url(url)
    else:
        text = load_file(file)

    summarizer = pipeline(
        task="summarization",
        model=model,
        tokenizer=model,
        framework="pt",
    )

    summary = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        truncation=True,
    )

    print()
    print("=" * 80)
    print(summary[0]["summary_text"])
    print("=" * 80)


if __name__ == "__main__":
    main()
