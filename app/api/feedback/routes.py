import json
import logging
from typing import Dict, Optional, Union

from fastapi import APIRouter, Request
from haystack.schema import Answer, Document, Label

from .api import (CreateLabelSerialized, FeedbackRequest, FeedbackResponse,
                  FilterRequest, LabelSerialized)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("", response_model=FeedbackResponse)
def post_feedback(feedback: FeedbackRequest, request: Request):
    DOCUMENT_STORE = request.app.state.feedback_document_store.component

    # is_correct_answer: bool,
    # is_correct_document: bool,
    # origin: Literal["user-feedback", "gold-label"],
    # answer: Optional[Answer],
    # id: Optional[str] = None,
    # no_answer: Optional[bool] = None,
    # pipeline_id: Optional[str] = None,
    # created_at: Optional[str] = None,
    # updated_at: Optional[str] = None,
    # meta: Optional[dict] = None,
    # filters: Optional[dict] = None,

    document = Document(id=feedback.document_id, content=feedback.context)
    answer = Answer(
        document_id=feedback.document_id,
        answer=feedback.answer,
        context=feedback.context,
        score=feedback.score,
        offsets_in_document=feedback.offsets_in_document,
    )
    props = dict(
        query=feedback.question,
        document=document,
        answer=answer,
        is_correct_answer=feedback.is_correct_answer,
        is_correct_document=feedback.is_correct_document,
        origin="user-feedback",
    )

    label = Label(**props)
    DOCUMENT_STORE.write_labels([label])


post_feedback.__doc__ = """
This endpoint allows the API user to submit feedback on an answer for a particular query.

For example, the user can send feedback on whether the answer was correct and
whether the right snippet was identified as the answer.

Information submitted through this endpoint is used to train the underlying QA model.
"""


@router.get("")
def get_feedback(request: Request):
    """
    This endpoint allows the API user to retrieve all the feedback that has been submitted
    through the `POST /feedback` endpoint.
    """
    DOCUMENT_STORE = request.app.state.feedback_document_store.component
    labels = DOCUMENT_STORE.get_all_labels()
    return labels


@router.delete("")
def delete_feedback(request: Request):
    """
    This endpoint allows the API user to delete all the
    feedback that has been sumbitted through the
    `POST /feedback` endpoint
    """
    DOCUMENT_STORE = request.app.state.feedback_document_store.component
    all_labels = DOCUMENT_STORE.get_all_labels()
    user_label_ids = [
        label.id for label in all_labels if label.origin == "user-feedback"
    ]
    DOCUMENT_STORE.delete_labels(ids=user_label_ids)


@router.post("/eval-feedback")
def get_feedback_metrics(request: Request, filters: FilterRequest = None):
    """
    This endpoint returns basic accuracy metrics based on user feedback,
    e.g., the ratio of correct answers or correctly identified documents.
    You can filter the output by document or label.

    Example:

    `curl --location --request POST 'http://127.0.0.1:8000/eval-doc-qa-feedback' \
     --header 'Content-Type: application/json' \
     --data-raw '{ "filters": {"document_id": ["XRR3xnEBCYVTkbTystOB"]} }'`
    """

    DOCUMENT_STORE = request.app.state.feedback_document_store.component
    if filters:
        filters_content = filters.filters or {}
        filters_content["origin"] = ["user-feedback"]
    else:
        filters_content = {"origin": ["user-feedback"]}

    labels = DOCUMENT_STORE.get_all_labels(filters=filters_content)

    res: Dict[str, Optional[Union[float, int]]]
    if len(labels) > 0:
        answer_feedback = [1 if l.is_correct_answer else 0 for l in labels]
        doc_feedback = [1 if l.is_correct_document else 0 for l in labels]

        answer_accuracy = sum(answer_feedback) / len(answer_feedback)
        doc_accuracy = sum(doc_feedback) / len(doc_feedback)

        res = {
            "answer_accuracy": answer_accuracy,
            "document_accuracy": doc_accuracy,
            "n_feedback": len(labels),
        }
    else:
        res = {"answer_accuracy": None, "document_accuracy": None, "n_feedback": 0}
    return res


@router.get("/export-feedback")
def export_feedback(
    request: Request,
    context_size: int = 100_000,
    full_document_context: bool = True,
    only_positive_labels: bool = False,
):
    """
    This endpoint returns JSON output in the SQuAD format for question/answer pairs
    that were marked as "relevant" by user feedback through the `POST /feedback` endpoint.

    The context_size param can be used to limit response size for large documents.
    """
    DOCUMENT_STORE = request.app.state.feedback_document_store.component
    if only_positive_labels:
        labels = DOCUMENT_STORE.get_all_labels(
            filters={"is_correct_answer": [True], "origin": ["user-feedback"]}
        )
    else:
        labels = DOCUMENT_STORE.get_all_labels(filters={"origin": ["user-feedback"]})
        # Filter out the labels where the passage is correct but answer is wrong (in SQuAD this matches
        # neither a "positive example" nor a negative "is_impossible" one)
        labels = [
            l
            for l in labels
            if not (l.is_correct_document is True and l.is_correct_answer is False)
        ]

    export_data = []

    for label in labels:
        if full_document_context:
            context = label.document.content

            answer_start = label.answer.offsets_in_document[0].start
        else:
            text = label.document.content
            # the final length of context(including the answer string) is 'context_size'.
            # we try to add equal characters for context before and after the answer string.
            # if either beginning or end of text is reached, we correspondingly
            # append more context characters at the other end of answer string.
            context_to_add = int((context_size - len(label.answer.answer)) / 2)
            start_pos = max(
                label.answer.offsets_in_document[0].start - context_to_add, 0
            )
            additional_context_at_end = max(
                context_to_add - label.answer.offsets_in_document[0].start, 0
            )
            end_pos = min(
                label.answer.offsets_in_document[0].start
                + len(label.answer.answer)
                + context_to_add,
                len(text) - 1,
            )
            additional_context_at_start = max(
                label.answer.offsets_in_document[0].start
                + len(label.answer.answer)
                + context_to_add
                - len(text),
                0,
            )
            start_pos = max(0, start_pos - additional_context_at_start)
            end_pos = min(len(text) - 1, end_pos + additional_context_at_end)
            context = text[start_pos:end_pos]
            answer_start = label.answer.offsets_in_document[0].start - start_pos

        if (
            label.is_correct_answer is False and label.is_correct_document is False
        ):  # No answer
            squad_label = {
                "paragraphs": [
                    {
                        "context": context,
                        "id": label.document.id,
                        "qas": [
                            {
                                "question": label.query,
                                "id": label.id,
                                "is_impossible": True,
                                "answers": [],
                            }
                        ],
                    }
                ]
            }
        else:
            squad_label = {
                "paragraphs": [
                    {
                        "context": context,
                        "id": label.document.id,
                        "qas": [
                            {
                                "question": label.query,
                                "id": label.id,
                                "is_impossible": False,
                                "answers": [
                                    {
                                        "text": label.answer.answer,
                                        "answer_start": answer_start,
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }

            # quality check
            start = squad_label["paragraphs"][0]["qas"][0]["answers"][0]["answer_start"]
            answer = squad_label["paragraphs"][0]["qas"][0]["answers"][0]["text"]
            context = squad_label["paragraphs"][0]["context"]
            if not context[start : start + len(answer)] == answer:
                logger.error(
                    f"Skipping invalid squad label as string via offsets "
                    f"('{context[start:start + len(answer)]}') does not match answer string ('{answer}') "
                )
        export_data.append(squad_label)

    export = {"data": export_data}

    with open("feedback_squad_direct.json", "w", encoding="utf8") as f:
        json.dump(export_data, f, ensure_ascii=False, sort_keys=True, indent=4)
    return export
