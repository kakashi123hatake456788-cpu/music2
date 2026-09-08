import collections

# chat_id -> deque[Track]
_queues: dict[int, collections.deque] = collections.defaultdict(collections.deque)
# chat_id -> Track currently playing
_now_playing: dict[int, object] = {}


def push(chat_id: int, track) -> None:
    _queues[chat_id].append(track)


def pop_next(chat_id: int):
    q = _queues[chat_id]
    return q.popleft() if q else None


def peek_queue(chat_id: int):
    return list(_queues[chat_id])


def clear(chat_id: int) -> None:
    _queues[chat_id].clear()
    _now_playing.pop(chat_id, None)


def set_now_playing(chat_id: int, track) -> None:
    _now_playing[chat_id] = track


def get_now_playing(chat_id: int):
    return _now_playing.get(chat_id)
