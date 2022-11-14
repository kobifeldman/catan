import cv2
import numpy as np
import itertools, string
from PIL import Image

def setModeBackground(mode):
    if mode == 'minecraft':
            photo  = 'water.png'
    else: photo = 'background.png'

    path = cv2.imread(photo)

    img = cv2.cvtColor(path, cv2.COLOR_BGR2RGB)
    return img

def drawBoard(board, mode):
    image = setModeBackground(mode)

    topLeft = [225,90]
    botLeft = [225, 180]
    bot = [310, 230]
    botRight = [400, 180]
    topRight = [400, 90]
    top = [310, 40]

    allVertex = [topLeft, botLeft, bot, botRight, topRight, top]

    isClosed = True
    color = (255, 0, 0)
    thickness = 2


    startingTile = [0,0]

    if mode == 'minecraft':
        image = np.array(Image.open("water.png"))
    
    tileNumbers = board.materialNumberTile
    tileColors = list(itertools.chain.from_iterable(board.tileSpots))

    for tile in range(19):
        if(str(board.robberLocation) == '('+ str(startingTile[0]) + ', ' + str(startingTile[1]) + ')'):
            circleColor = (255,0,0)

        for number in tileNumbers:
            for material in tileNumbers[number]:
                if '('+ str(startingTile[0]) + ',' + str(startingTile[1]) + ')' in material:
                    numToDraw = number
                    break
                   
        if tile not in [2,6,11,15]:
            startingTile[1] += 1
        else:
            startingTile[1] = 0
            startingTile[0] += 1

        if tile in [3,7,12,16]:
            for vertex in allVertex:
                if mode == 'minecraft':
                    vertex[1] += 143
                else: vertex[1] += 140

                if tile in [3,16]:
                    if mode == 'minecraft':
                        vertex[0] -= 609
                    else: vertex[0] -= 612.5
                elif tile in [7,12]:
                    if mode == 'minecraft':
                        vertex[0] -= 784
                    else: vertex[0] -= 787.5

        pts = np.array([topLeft, botLeft,
                        bot, botRight,
                            topRight, top],
                        np.int32)   
        pts = pts.reshape((-1, 1, 2))

        if tileColors[tile] == 'rockTile':
            color = (120, 115, 99)
            block = "rock.png"
        elif tileColors[tile] == 'brickTile':
            color = (166, 104, 28)
            block = "brick.png"
        elif tileColors[tile] == 'sheepTile':
            color = (82, 161, 48)
            block = "sheep.png"
        elif tileColors[tile] == 'wheatTile':
            color = (230, 231, 121)
            block = "wheat.png"
        elif tileColors[tile] == 'treeTile':
            color = (84, 63, 17)
            block = "tree.png"
        else:
            color = (166, 7,44)
            block = "sand.png"

        if mode == 'minecraft':
            minecraftMode(int(topLeft[0]) -8, top[1], block, image)
            image = np.array(Image.open("test.png"))

        else: cv2.fillPoly(image, [pts], color)


        try:
            if(circleColor == (255,0,0)):
                image = cv2.circle(image, (int(top[0]), top[1] + 95), 30, circleColor, -1)
                circleColor = None
            else: image = cv2.circle(image, (int(top[0]), top[1] + 95), 30, (0,0,0), -1)

        except: image = cv2.circle(image, (int(top[0]), top[1] + 95), 30, (0,0,0), -1)

        if(numToDraw > 9):
            image = cv2.putText(image, str(numToDraw), (int(top[0] - 20), top[1] + 105), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)
        else: image = cv2.putText(image, str(numToDraw), (int(top[0] - 10), top[1] + 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)

        if mode == 'normal':
            image = cv2.polylines(image, [pts], isClosed, (0,0,0), thickness)

        for vertex in allVertex:
            if mode == 'minecraft':
                vertex[0] += 173
            else: vertex[0] += 175
        drawGrid(image)
    cv2.imwrite('test.png', image)

    im_cv = cv2.imread('test.png')
    im_cv = cv2.cvtColor(im_cv, cv2.COLOR_BGR2RGB)
    cv2.imwrite('test.png', im_cv)

def drawRobber(board, image):
    topLeft = [225,90]
    botLeft = [225, 180]
    bot = [310, 230]
    botRight = [400, 180]
    topRight = [400, 90]
    top = [310, 40]

    allVertex = [topLeft, botLeft, bot, botRight, topRight, top]

    startingTile = [0,0]
    tileNumbers = board.materialNumberTile

    for tile in range(19):
        if(str(board.robberLocation) == '('+ str(startingTile[0]) + ', ' + str(startingTile[1]) + ')'):
            circleColor = (0,0,255)

        for number in tileNumbers:
            for material in tileNumbers[number]:
                if '('+ str(startingTile[0]) + ',' + str(startingTile[1]) + ')' in material:
                    numToDraw = number
                    break
                   
        if tile not in [2,6,11,15]:
            startingTile[1] += 1
        else:
            startingTile[1] = 0
            startingTile[0] += 1

        if tile in [3,7,12,16]:
            for vertex in allVertex:
                vertex[1] += 140
                if tile == 3:
                    vertex[0] -= 612.5
                elif tile == 7:
                    vertex[0] -= 787.5
                elif tile == 12:
                    vertex[0] -= 787.5
                else:
                    vertex[0] -= 612.5

        pts = np.array([topLeft, botLeft,
                        bot, botRight,
                            topRight, top],
                        np.int32)   
        pts = pts.reshape((-1, 1, 2))

        try:
            if(circleColor == (0,0,255)):
                image = cv2.circle(image, (int(top[0]), top[1] + 95), 30, circleColor, -1)
                circleColor = None
            else: image = cv2.circle(image, (int(top[0]), top[1] + 95), 30, (0,0,0), -1)

        except: image = cv2.circle(image, (int(top[0]), top[1] + 95), 30, (0,0,0), -1)

        if(numToDraw > 9):
            image = cv2.putText(image, str(numToDraw), (int(top[0] - 20), top[1] + 105), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)
        else: image = cv2.putText(image, str(numToDraw), (int(top[0] - 10), top[1] + 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 2)

        for vertex in allVertex:
                vertex[0] += 175
    cv2.imwrite('test.png', image)

def drawGrid(image):
    capitalLetters = list(string.ascii_uppercase)
    letterIndex = 0
    xCoord = 50
    yCoord = 50

    for num in range(11):
        image = cv2.putText(image, capitalLetters[letterIndex], (xCoord, 23), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,0), 1)
        letterIndex += 1
        xCoord += 85
    
    for num in range(12):
        image = cv2.putText(image, str(num), (0, yCoord), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,0), 1)
        if(num % 2 == 0):
            yCoord += 50
        else: yCoord += 90

def getSpot(spot):
    spotAdj = [spot[1],spot[0]]

    firstSpot = [310, 40]
    if spot[0] == 1:
        firstSpot[1] += 50
        firstSpot[0] -= 85
    elif spot[0] == 2:
        firstSpot[1] += 140
        firstSpot[0] -= 85
    elif spot[0] == 3:
        firstSpot[1] += 190
        firstSpot[0] -= 175
    elif spot[0] == 4:
        firstSpot[1] += 280
        firstSpot[0] -= 175
    elif spot[0] == 5:
        firstSpot[1] += 330
        firstSpot[0] -= 260
    elif spot[0] == 6:
        firstSpot[1] += 420
        firstSpot[0] -= 260
    elif spot[0] == 7:
        firstSpot[1] += 470
        firstSpot[0] -= 175
    elif spot[0] == 8:
        firstSpot[1] += 560
        firstSpot[0] -= 175
    elif spot[0] == 9:
        firstSpot[1] += 610
        firstSpot[0] -= 85
    elif spot[0] == 10:
        firstSpot[1] += 700
        firstSpot[0] -= 85
    elif spot[0] == 11: 
        firstSpot[1] += 750
        
    firstSpot[0] += spotAdj[0] * 175

    return firstSpot

def determineColor(player):

    color = player.color

    if(color == "Blue"):
        color = (255,0,0)
    elif(color == "Red"):
        color = (0,0,255)
    elif(color == "Orange"):
        color = (27, 133, 241)
    elif(color == "White"):
        color = (255,255,255)

    return color

def drawSettle(image, player, spot):

    boardLocation = getSpot(spot)
    settleColor = determineColor(player)
    
    cv2.rectangle(image,(boardLocation[0] - 15,boardLocation[1]-15),(boardLocation[0] + 15,boardLocation[1] + 15),settleColor,-1)
    cv2.imwrite('test.png', image)

def drawCity(image, player, spot):

    boardLocation = getSpot(spot)
    settleColor = (255,255,255)
    
    cv2.rectangle(image,(boardLocation[0] - 10,boardLocation[1]-10),(boardLocation[0] + 10,boardLocation[1] + 10),settleColor,-1)
    cv2.imwrite('test.png', image)

def drawRoad(image, player, spot1, spot2):
    
    boardLocation1 = getSpot(spot1)
    boardLocation2 = getSpot(spot2)

    roadColor = determineColor(player)

    cv2.line(image, boardLocation1, boardLocation2, roadColor, 15) 
    cv2.imwrite('test.png', image)


def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """Overlay `img_overlay` onto `img` at (x, y) and blend using `alpha_mask`.

    `alpha_mask` must have same HxW as `img_overlay` and values in range [0, 1].
    """
    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    # Blend overlay within the determined ranges
    img_crop = img[y1:y2, x1:x2]
    img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
    alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
    alpha_inv = 1.0 - alpha

    img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop

    
def minecraftMode(x, y, material_img, img):
    img_overlay_rgba = np.array(Image.open(material_img))

    # Perform blending
    alpha_mask = img_overlay_rgba[:, :, 3] / 255.0
    img_result = img[:, :, :3].copy()
    img_overlay = img_overlay_rgba[:, :, :3]
    overlay_image_alpha(img_result, img_overlay, x, y, alpha_mask)

    # Save result
    Image.fromarray(img_result).save("test.png")


