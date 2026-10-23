"""Reads new support tickets from the public inbox.

The inbox is reachable by anyone on the internet: a ticket's text is
whatever the sender wrote. This module hands each ticket to the agent
loop unchanged, which is exactly what `controlloop.yaml` declares under
`external_inputs`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    sender: str
    body: str


def poll_public_inbox(mailbox: list[dict[str, str]]) -> list[Ticket]:
    """Return every unread ticket, in arrival order. `mailbox` stands in
    for the mail service; no socket is opened here."""

    return [
        Ticket(ticket_id=item["id"], sender=item["from"], body=item["body"])
        for item in mailbox
        if item.get("unread", True)
    ]
