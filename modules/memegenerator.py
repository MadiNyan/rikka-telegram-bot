import textwrap

from PIL import Image, ImageDraw, ImageFont


def make_meme(topString, bottomString, filename, extension, path, meme_font):
    img = Image.open(path + filename + extension)
    imageSize = img.size
    wrapwidth = int(imageSize[0]/20)

    # wrap input text strings
    if bottomString is None:
        bottomString = [" "]
    else:
        bottomString = textwrap.wrap(bottomString ,width=wrapwidth)
    if topString is None:
        topString = [" "]
    else:
        topString = textwrap.wrap(topString ,width=wrapwidth)
    
    # longest line to find font size
    longestTopString = max(topString, key=len)
    longestBottomString = max(bottomString, key=len)

    # find biggest font size that works
    fontSize = int(imageSize[1]/6)
    font = ImageFont.truetype(meme_font, fontSize)
    topTextSize = font.getsize(longestTopString)
    bottomTextSize = font.getsize(longestBottomString)
    while topTextSize[0] > imageSize[0]-20 or bottomTextSize[0] > imageSize[0]-20:
        fontSize = fontSize - 1
        font = ImageFont.truetype(meme_font, fontSize)
        topTextSize = font.getsize(longestTopString)
        bottomTextSize = font.getsize(longestBottomString)
        
    # find top centered position for top text
    topPositions = []
    initialX = 0 - topTextSize[1]
    for i in topString:
        topTextLineSize = font.getsize(i)
        topTextPositionX = (imageSize[0]/2) - (topTextLineSize[0]/2)
        topTextPositionY = initialX + topTextSize[1]
        initialX = topTextPositionY
        topTextPosition = (topTextPositionX, topTextPositionY)
        topPositions.append(topTextPosition)

    # find bottom centered position for bottom text
    bottomPositions = []
    initialY = imageSize[1] - bottomTextSize[1]*len(bottomString)-15 - bottomTextSize[1]
    for i in bottomString:
        bottomTextLineSize = font.getsize(i)
        bottomTextPositionX = (imageSize[0]/2) - (bottomTextLineSize[0]/2)
        bottomTextPositionY = initialY + bottomTextSize[1]
        initialY = bottomTextPositionY
        bottomTextPosition = (bottomTextPositionX, bottomTextPositionY)
        bottomPositions.append(bottomTextPosition)

    draw = ImageDraw.Draw(img)

    # draw outlines
    outlineRange = int(fontSize/25)+1
    for x in range(-outlineRange, outlineRange+1):
        for y in range(-outlineRange, outlineRange+1):
            ct = 0
            cb = 0
            for i in topPositions:
                draw.text((i[0]+x, i[1]+y), topString[ct], (0, 0, 0), font=font)
                ct += 1
            for i in bottomPositions:
                draw.text((i[0]+x, i[1]+y), bottomString[cb], (0, 0, 0), font=font)
                cb += 1

    for i in range(len(topString)):
        draw.text(topPositions[i], topString[i], (255, 255, 255), font=font)
    for i in range(len(bottomString)):
        draw.text(bottomPositions[i], bottomString[i], (255, 255, 255), font=font)

    img.save(path+filename+"-meme"+extension)
