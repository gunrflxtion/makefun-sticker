import os
import struct
import zlib
import hashlib

S = 2
W = H = 1024
RW = RH = W * S
NAVY = (22, 24, 58)
WHITE = (255, 255, 255)
VIOLET = (91, 61, 240)
GOLD = (255, 197, 55)
GOLD_D = (220, 145, 27)
GREY = (238, 244, 247)
GREY_D = (190, 210, 220)
TEAL = (35, 213, 190)

pixels = bytearray(RW * RH * 3)
TRANSFORM = 1.0
TRANSFORM_CENTER = (512.0, 506.0)
TRANSFORM_OFFSET_Y = 0.0

def transformed(x, y):
    return (TRANSFORM_CENTER[0] + (x - TRANSFORM_CENTER[0]) * TRANSFORM,
            TRANSFORM_CENTER[1] + (y - TRANSFORM_CENTER[1]) * TRANSFORM
            + TRANSFORM_OFFSET_Y)

def put(x, y, c):
    if 0 <= x < RW and 0 <= y < RH:
        i = (y * RW + x) * 3
        pixels[i:i+3] = bytes(c)

def rect(x0, y0, x1, y1, c):
    x0, y0 = transformed(x0, y0)
    x1, y1 = transformed(x1, y1)
    x0, y0, x1, y1 = [int(round(v*S)) for v in (x0,y0,x1,y1)]
    x0, x1 = max(0,x0), min(RW,x1)
    y0, y1 = max(0,y0), min(RH,y1)
    row = bytes(c) * max(0, x1-x0)
    for y in range(y0,y1):
        i = (y*RW+x0)*3
        pixels[i:i+len(row)] = row

def circle(cx, cy, r, c):
    cx, cy = transformed(cx, cy)
    r *= TRANSFORM
    cx, cy, r = int(round(cx*S)), int(round(cy*S)), int(round(r*S))
    r2 = r*r
    for y in range(max(0,cy-r), min(RH,cy+r+1)):
        dy = y-cy
        span = int((r2-dy*dy)**0.5) if r2 >= dy*dy else -1
        if span >= 0:
            x0, x1 = max(0,cx-span), min(RW,cx+span+1)
            i = (y*RW+x0)*3
            row = bytes(c)*(x1-x0)
            pixels[i:i+len(row)] = row

def polygon(points, c):
    pts = [(int(round(tx*S)),int(round(ty*S)))
           for tx,ty in (transformed(x,y) for x,y in points)]
    ymin=max(0,min(y for x,y in pts)); ymax=min(RH,max(y for x,y in pts)+1)
    for y in range(ymin,ymax):
        scan=y+0.5
        xs=[]
        for i in range(len(pts)):
            x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]
            if (y1 <= scan < y2) or (y2 <= scan < y1):
                xs.append(x1+(scan-y1)*(x2-x1)/(y2-y1))
        xs.sort()
        for j in range(0,len(xs)-1,2):
            x0=max(0,int(xs[j])); x1=min(RW,int(xs[j+1])+1)
            if x1>x0:
                i=(y*RW+x0)*3; row=bytes(c)*(x1-x0)
                pixels[i:i+len(row)]=row

def thickline(x1,y1,x2,y2,width,c):
    # A chain of overlapping discs gives the line rounded caps and joins.
    dx=x2-x1; dy=y2-y1
    n=max(1,int(max(abs(dx),abs(dy))*S/2))
    for k in range(n+1):
        t=k/n
        circle(x1+dx*t,y1+dy*t,width/2,c)

def rr(x0,y0,x1,y1,r,c):
    # Rounded rectangle assembled from a central bar and four discs.
    rect(x0+r,y0,x1-r,y1,c)
    rect(x0,y0+r,x1,y1-r,c)
    for x in (x0+r,x1-r):
        for y in (y0+r,y1-r):
            circle(x,y,r,c)

def outlined_rr(x0,y0,x1,y1,r,border,fill,stroke=10):
    rr(x0,y0,x1,y1,r,border)
    rr(x0+stroke,y0+stroke,x1-stroke,y1-stroke,max(1,r-stroke),fill)

# Transparent-free die-cut badge: white outer edge, dark keyline, vivid field.
rr(56,56,968,968,154,NAVY)
rr(48,48,960,960,154,WHITE)
rr(76,76,932,932,132,NAVY)
rr(88,88,920,920,120,VIOLET)

# Trophy arm raised on the left, placed behind the robot.
TRANSFORM = 1.15
TRANSFORM_OFFSET_Y = -35.0
thickline(368,477,292,388,31,NAVY)
thickline(368,477,292,388,18,GREY)
circle(282,379,30,NAVY); circle(282,379,20,GREY)
rr(242,312,259,350,8,NAVY)
polygon([(222,284),(297,284),(287,331),(273,348),(245,348),(231,331)],NAVY)
polygon([(233,294),(286,294),(278,322),(268,335),(250,335),(240,322)],GOLD)
rect(253,348,268,366,NAVY); rect(239,364,282,377,NAVY)
thickline(237,302,216,321,10,NAVY); thickline(282,302,303,321,10,NAVY)

# Antenna, behind head.
thickline(512,284,512,218,18,NAVY)
thickline(512,284,512,220,9,TEAL)
circle(512,203,28,NAVY); circle(512,203,18,GOLD)

# Robot silhouette, body first.
outlined_rr(392,520,632,727,49,NAVY,GREY,12)
# shoulders and arms
thickline(398,565,340,617,34,NAVY); thickline(398,565,340,617,20,GREY)
circle(335,623,25,NAVY); circle(335,623,15,TEAL)
thickline(625,565,681,520,34,NAVY); thickline(625,565,681,520,20,GREY)
circle(687,514,25,NAVY); circle(687,514,15,TEAL)
# chest plate and star
outlined_rr(444,586,580,683,22,NAVY,(220,235,239),8)
polygon([(512,600),(523,624),(549,626),(529,643),(535,668),(512,654),(489,668),(495,643),(475,626),(501,624)],GOLD)
# neck
rr(475,481,549,532,15,NAVY); rr(487,482,537,532,10,TEAL)
# head
outlined_rr(337,290,687,506,66,NAVY,GREY,13)
# ear pads
rr(313,366,348,438,16,NAVY); rr(676,366,711,438,16,NAVY)
rr(320,379,343,425,10,TEAL); rr(681,379,704,425,10,TEAL)
# eyes with bold pupils and friendly smile
circle(512,326,13,NAVY); circle(512,326,7,TEAL)
circle(438,384,31,NAVY); circle(586,384,31,NAVY)
circle(443,380,17,TEAL); circle(591,380,17,TEAL)
circle(448,374,6,WHITE); circle(596,374,6,WHITE)
thickline(470,437,489,452,10,NAVY)
thickline(489,452,535,452,10,NAVY)
thickline(535,452,554,437,10,NAVY)

# Podium: strong gold trapezoid with a large, custom #1.
polygon([(253,727),(771,727),(716,833),(308,833)],NAVY)
polygon([(270,739),(754,739),(707,817),(317,817)],GOLD)
polygon([(317,817),(707,817),(691,838),(333,838)],GOLD_D)

FONT = {
 'm':("10001","11011","10101","10101","10101","10101","10101"),
 'a':("01110","10001","00001","01111","10001","10011","01101"),
 'k':("10001","10010","10100","11000","10100","10010","10001"),
 'e':("01110","10001","10001","11111","10000","10001","01110"),
 '.':("00000","00000","00000","00000","00000","00110","00110"),
 'f':("00111","01000","01000","11110","01000","01000","01000"),
 'u':("10001","10001","10001","10001","10011","10101","01101"),
 'n':("10001","11001","10101","10011","10001","10001","10001"),
 '#':("01010","11111","01010","01010","11111","01010","00000"),
 '1':("00100","01100","00100","00100","00100","00100","01110"),
}

def text5x7(txt, x, y, cell, color, gap=1):
    for ch in txt:
        rows=FONT[ch]
        for gy,row in enumerate(rows):
            for gx,on in enumerate(row):
                if on == "1":
                    rect(x+gx*cell,y+gy*cell,x+(gx+1)*cell,y+(gy+1)*cell,color)
        x += 5*cell + gap*cell

# Centered #1: glyph scale chosen to read at sticker size.
text5x7("#1",449,755,9, NAVY, 1)

# Wordmark on a clean lower band.
TRANSFORM = 1.0
TRANSFORM_OFFSET_Y = 0.0
text5x7("make.fun",306.18,854,9.24,WHITE,0.65)

def png_chunk(kind,data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)

def downsample():
    out=bytearray(W*H*3)
    for y in range(H):
        for x in range(W):
            i=((y*2)*RW+x*2)*3
            j=i+RW*3
            d=(y*W+x)*3
            for c in range(3):
                out[d+c]=(pixels[i+c]+pixels[i+3+c]+pixels[j+c]+pixels[j+3+c]+2)//4
    return out

def main():
    rgb=downsample()
    raw=b"".join(b"\x00"+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    data=(b"\x89PNG\r\n\x1a\n"+
          png_chunk(b"IHDR",struct.pack(">IIBBBBB",W,H,8,2,0,0,0))+
          png_chunk(b"IDAT",zlib.compress(raw,9))+
          png_chunk(b"IEND",b""))
    outdir=os.environ.get("MAKEFUN_OUTPUT_DIR","/output")
    os.makedirs(outdir,exist_ok=True)
    with open(os.path.join(outdir,"entry.png"),"wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()
