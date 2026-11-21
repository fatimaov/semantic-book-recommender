"""Format Flask book records for Gradio's gallery and description panel."""

from typing import Any

from frontend.config import COVER_NOT_FOUND_PATH


NO_DESCRIPTION = "No description is available for this book."


def _format_authors(authors: Any) -> str:
    if not isinstance(authors, str) or not authors.strip():
        return "unknown"

    names = [author.strip() for author in authors.split(";") if author.strip()]
    if not names:
        return "unknown"
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    if len(names) > 2:
        return f"{', '.join(names[:-1])}, and {names[-1]}"
    return names[0]


def _cover_for(book: dict[str, Any]) -> str:
    thumbnail = book.get("thumbnail")
    if not isinstance(thumbnail, str) or not thumbnail.strip():
        return str(COVER_NOT_FOUND_PATH)

    thumbnail = thumbnail.strip()
    if "fife=w800" in thumbnail:
        return thumbnail
    separator = "&" if "?" in thumbnail else "?"
    return f"{thumbnail}{separator}fife=w800"


def format_gallery(
    books: list[dict[str, Any]],
) -> tuple[list[tuple[str, str]], list[str]]:
    """Return gallery image-caption pairs and matching full descriptions."""
    gallery_items = []
    descriptions = []

    for book in books:
        title = book.get("title_and_subtitle") or "Untitled"
        authors = _format_authors(book.get("authors"))
        caption = f"{title} by {authors}"
        description = book.get("description")
        if not isinstance(description, str) or not description.strip():
            description = NO_DESCRIPTION

        gallery_items.append((_cover_for(book), caption))
        descriptions.append(f"{caption}\n\n{description}")

    return gallery_items, descriptions
