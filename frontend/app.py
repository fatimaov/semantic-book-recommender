"""Gradio interface for the Flask book recommendation API."""

import gradio as gr

from frontend.config import CATEGORY_CHOICES, PAGE_SIZE, TONE_CHOICES
from frontend.services.recommendation_api import (
    RecommendationAPIError,
    fetch_recommendations,
)
from frontend.utils.gallery_formatter import NO_DESCRIPTION, format_gallery


SELECT_BOOK_PROMPT = "Select a recommended book to read its full description."


def _empty_search_result(message: str):
    return (
        [],
        [],
        [],
        0,
        "Page 1 of 1",
        message,
        gr.Button(interactive=False),
        gr.Button(interactive=False),
    )


def recommend_books(query: str, category: str, tone: str):
    """Fetch books from Flask and prepare the visible page and descriptions."""
    if not query or not query.strip():
        return _empty_search_result("Enter a description to find recommendations.")

    try:
        books = fetch_recommendations(
            query=query,
            category=category,
            emotion=tone,
        )
    except RecommendationAPIError as error:
        return _empty_search_result(f"Could not load recommendations: {error}")

    if not books:
        return _empty_search_result(
            "No recommendations found. Try a different description or filter."
        )

    gallery_items, descriptions = format_gallery(books)
    page_count = max(1, (len(gallery_items) + PAGE_SIZE - 1) // PAGE_SIZE)
    return (
        gallery_items[:PAGE_SIZE],
        gallery_items,
        descriptions,
        0,
        f"Page 1 of {page_count}",
        SELECT_BOOK_PROMPT,
        gr.Button(interactive=False),
        gr.Button(interactive=page_count > 1),
    )


def change_recommendation_page(direction: int, recommendations, page: int):
    """Show a page of gallery results and update navigation controls."""
    page_count = max(1, (len(recommendations) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page + direction, page_count - 1))
    start = page * PAGE_SIZE
    return (
        recommendations[start : start + PAGE_SIZE],
        page,
        f"Page {page + 1} of {page_count}",
        SELECT_BOOK_PROMPT,
        gr.Button(interactive=page > 0),
        gr.Button(interactive=page < page_count - 1),
    )


def show_selected_description(descriptions: list[str], page: int, event: gr.SelectData):
    """Show the selected book's full description."""
    index = event.index
    index = index[0] if isinstance(index, (tuple, list)) else index
    index += page * PAGE_SIZE
    if not descriptions or not 0 <= index < len(descriptions):
        return NO_DESCRIPTION
    return descriptions[index] or NO_DESCRIPTION


with gr.Blocks(theme=gr.Theme.from_hub("harsh8001/skymist")) as dashboard:
    gr.Markdown("# Semantic Book Recommender", elem_id="dashboard-title")

    user_query = gr.Textbox(
        label="Please enter a description of a book:",
        placeholder="e.g., A story about forgiveness",
    )

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                category_dropdown = gr.Dropdown(
                    choices=CATEGORY_CHOICES,
                    label="Select a category:",
                    value="All",
                )
                tone_dropdown = gr.Dropdown(
                    choices=TONE_CHOICES,
                    label="Select an emotional tone:",
                    value="All",
                )

    with gr.Row():
        submit_button = gr.Button("Find recommendations", scale=1, min_width=0)

    gr.Markdown("## Recommendations")
    output = gr.Gallery(
        label="Recommended books",
        columns=8,
        rows=2,
        elem_id="recommendations-gallery",
    )
    recommendations_state = gr.State([])
    descriptions_state = gr.State([])
    page_state = gr.State(0)

    with gr.Row():
        previous_page = gr.Button("Previous", interactive=False, scale=1)
        page_indicator = gr.Markdown("Page 1 of 1", elem_id="page-indicator", scale=1)
        next_page = gr.Button("Next", interactive=False, scale=1)

    full_description = gr.Textbox(
        label="Full description",
        lines=8,
        interactive=False,
    )

    submit_button.click(
        fn=recommend_books,
        inputs=[user_query, category_dropdown, tone_dropdown],
        outputs=[
            output,
            recommendations_state,
            descriptions_state,
            page_state,
            page_indicator,
            full_description,
            previous_page,
            next_page,
        ],
    )
    previous_page.click(
        fn=lambda recommendations, page: change_recommendation_page(
            -1, recommendations, page
        ),
        inputs=[recommendations_state, page_state],
        outputs=[
            output,
            page_state,
            page_indicator,
            full_description,
            previous_page,
            next_page,
        ],
    )
    next_page.click(
        fn=lambda recommendations, page: change_recommendation_page(
            1, recommendations, page
        ),
        inputs=[recommendations_state, page_state],
        outputs=[
            output,
            page_state,
            page_indicator,
            full_description,
            previous_page,
            next_page,
        ],
    )
    output.select(
        fn=show_selected_description,
        inputs=[descriptions_state, page_state],
        outputs=full_description,
    )


if __name__ == "__main__":
    dashboard.launch(
        css="""
        #dashboard-title {
            margin: 2rem 0 2.5rem;
            text-align: center;
        }
        #page-indicator {
            text-align: center;
            align-self: center;
        }
        #recommendations-gallery .grid-container {
            grid-template-columns: repeat(8, minmax(0, 1fr)) !important;
        }
        @media (max-width: 900px) {
            #recommendations-gallery .grid-container {
                grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
            }
        }
        @media (max-width: 600px) {
            #recommendations-gallery .grid-container {
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            }
        }
        """
    )
