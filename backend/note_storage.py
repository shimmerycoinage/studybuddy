from fastapi import WebSocketException
from pycrdt import Doc, merge_updates
from sqlalchemy import select

from database import SessionLocal
from models import GroupMembership, Note


EMPTY_NOTE = Doc().get_update()


def note_state(note_id: int, user_id: int, update: bytes | None = None) -> bytes | None:
    query = (
        select(Note)
        .join(GroupMembership, GroupMembership.group_id == Note.group_id)
        .where(Note.id == note_id, GroupMembership.user_id == user_id)
    )

    if update is not None:
        query = query.with_for_update()

    with SessionLocal.begin() as db:
        note = db.scalar(query)
        if note is None:
            raise WebSocketException(code=1008)

        if update is not None:
            previous = note.yjs_state if note.yjs_state is not None else EMPTY_NOTE
            try:
                note.yjs_state = merge_updates(previous, update)
            except ValueError as error:
                raise WebSocketException(code=1007) from error

        return note.yjs_state