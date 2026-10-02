"""Explicit Discogs parent/style paths; no substring-based genre inference."""

VERSION = "discogs-parents-v1"
PARENTS = {
    "Electronic": ("genre:electronic", ["electronic", "electronica"]),
    "Rock": ("genre:rock", ["rock"]),
    "Pop": ("genre:pop", ["pop"]),
    "Hip Hop": ("genre:hip_hop", ["hip hop", "hip-hop", "rap"]),
    "Jazz": ("genre:jazz", ["jazz"]),
    "Funk / Soul": ("genre:funk-soul", ["funk / soul"]),
    "Folk, World, & Country": ("genre:folk-world-country", ["folk, world, & country"]),
    "Latin": ("genre:latin", ["latin", "latino"]),
    "Reggae": ("genre:reggae", ["reggae"]),
    "Blues": ("genre:blues", ["blues"]),
    "Classical": ("genre:classical", ["classical", "clasica", "clásica"]),
    "Stage & Screen": ("genre:stage-screen", ["stage & screen"]),
    "Children's": ("genre:childrens", ["children's"]),
    "Brass & Military": ("genre:brass-military", ["brass & military"]),
    "Non-Music": ("genre:non-music", ["non-music"]),
}


def parent_tags(label):
    parent, separator, _ = label.partition("---")
    return [PARENTS[parent][0]] if separator and parent in PARENTS else []
