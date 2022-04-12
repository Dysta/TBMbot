def clean_description(desc: str) -> str:
    return (
        desc.replace("\r", "")
        .replace("\n", "")
        .replace("<hr />", "")
        .replace("/!\\", "❕ ")
        .strip()
    )
