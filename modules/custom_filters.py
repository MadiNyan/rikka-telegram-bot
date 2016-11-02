# photo with caption
def caption_filter(text):
    return lambda msg: bool(msg.photo) and msg.caption.startswith(text)


# text of choice
def text_filter(text):
    return lambda msg: bool(text in msg.text)
