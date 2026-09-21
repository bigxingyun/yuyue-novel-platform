"""用户头像等通用工具。"""


def default_avatar_url(user_id: int | str) -> str:
    return f"https://api.dicebear.com/7.x/notionists/svg?seed={user_id}"


def resolve_avatar(user: object | None) -> str:
    if user is None:
        return default_avatar_url("guest")
    avatar = getattr(user, "avatar", "") or ""
    if avatar.strip():
        return avatar
    return default_avatar_url(getattr(user, "id", "guest"))
