"""
YouTube video metadata builder.

Converts a script dict (from ScriptGenerator) into a fully-formed
YouTube Data API v3 metadata body ready for videos.insert().

YouTube constraints enforced here:
  - Title: ≤ 70 characters (channel style guide) + hard cap at 100.
  - Description: ≤ 5 000 characters.
  - Tags: each tag ≤ 100 chars; total tags ≤ 500 chars joined by comma.
  - At most 20 tags.

Description structure:
  {hook line from script description}

  {SEO summary sentence}

  Follow @ClickBaitn't for daily mind-blowing facts!

  {hashtag block: mandatory + topic + niche + viral, 15-30 total}

Usage:
    builder  = MetadataBuilder()
    metadata = builder.build(script, video_id="vid_001")
    # metadata: dict ready to pass to YouTubeUploader.upload()
"""

from src.utils.config_loader import get_config
from src.utils.logger import log

_MAX_TITLE_LEN       = 70
_MAX_TITLE_HARD_CAP  = 100
_MAX_DESCRIPTION_LEN = 5_000
_MAX_TAG_CHARS       = 500    # total joined length
_MAX_TAGS            = 20
_MAX_SINGLE_TAG_LEN  = 100


class MetadataBuilder:
    """
    Builds YouTube API metadata from a script dict.

    Usage:
        builder  = MetadataBuilder()
        metadata = builder.build(script, video_id)
    """

    def __init__(self) -> None:
        cfg = get_config()
        yt  = cfg.youtube

        self._category_id:       str       = str(yt.get("channel_category", "22"))
        self._privacy:           str       = yt.get("privacy", "public")
        self._made_for_kids:     bool      = bool(yt.get("made_for_kids", False))
        self._default_tags:      list[str] = list(yt.get("default_tags", []))
        self._channel_name:      str       = yt.get("channel_name", "ClickBaitn't")
        self._channel_hashtag:   str       = yt.get("channel_hashtag", "#ClickBaitnt")
        self._mandatory_hashtags: list[str] = list(yt.get("mandatory_hashtags", ["#Shorts", "#ClickBaitnt"]))
        self._viral_hashtags:    list[str] = list(yt.get("viral_hashtags", []))
        self._min_hashtags:      int       = int(yt.get("min_hashtags", 15))
        self._max_hashtags:      int       = int(yt.get("max_hashtags", 30))

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def build(self, script: dict, video_id: str) -> dict:
        """
        Build the full YouTube metadata dict for a video.

        Args:
            script:   Script dict from ScriptGenerator (needs 'title',
                      'description', 'tags', 'topic', 'category',
                      optionally 'topic_hashtags').
            video_id: Unique video identifier (used as fallback title).

        Returns:
            Dict with keys: title, description, tags, categoryId,
            privacyStatus, selfDeclaredMadeForKids.
        """
        title       = self._build_title(script, video_id)
        description = self._build_description(script)
        tags        = self._build_tags(script)

        metadata = {
            "title":                    title,
            "description":              description,
            "tags":                     tags,
            "categoryId":               self._category_id,
            "privacyStatus":            self._privacy,
            "selfDeclaredMadeForKids":  self._made_for_kids,
        }

        log.info(
            "metadata_builder.build",
            video_id=video_id,
            title=title[:60],
            tags=len(tags),
            privacy=self._privacy,
        )
        return metadata

    # ------------------------------------------------------------------ #
    #  Field builders                                                      #
    # ------------------------------------------------------------------ #

    def _build_title(self, script: dict, video_id: str) -> str:
        """
        Derive a YouTube-safe title.

        Preference order: script["title"] → script["topic"] → video_id.
        Appends ' #Shorts' if not already present and fits within 70 chars.
        Hard cap at 100 chars.
        """
        raw = (
            script.get("title")
            or script.get("topic")
            or video_id
        ).strip()

        # Strip existing #Shorts so we can reinsert at the end cleanly
        shorts_suffix = " #Shorts"
        if raw.endswith("#Shorts"):
            raw = raw[: -len("#Shorts")].rstrip()

        # Append #Shorts if it fits within the 70-char soft limit
        if len(raw) + len(shorts_suffix) <= _MAX_TITLE_LEN:
            raw = raw + shorts_suffix
        elif not raw.endswith("#Shorts"):
            # Title already too long for suffix — truncate to make room
            raw = raw[: _MAX_TITLE_LEN - len(shorts_suffix)].rstrip() + shorts_suffix

        # Hard cap at 100 chars (YouTube absolute limit)
        if len(raw) > _MAX_TITLE_HARD_CAP:
            raw = raw[: _MAX_TITLE_HARD_CAP - 1] + "…"

        return raw

    def _build_description(self, script: dict) -> str:
        """
        Build the video description in 4 sections:

          1. Hook line (first sentence of script description)
          2. SEO summary (remainder of description, or topic fallback)
          3. Follow footer with channel name
          4. Hashtag block (15-30 hashtags across 4 categories)
        """
        raw_desc = (script.get("description") or "").strip()
        topic    = (script.get("topic") or "").strip()

        # Section 1 + 2: split description into hook + body
        sentences = [s.strip() for s in raw_desc.split(".") if s.strip()]
        if len(sentences) >= 2:
            hook_line   = sentences[0] + "."
            seo_summary = ". ".join(sentences[1:]) + "."
        elif sentences:
            hook_line   = sentences[0] + "."
            seo_summary = topic
        else:
            hook_line   = topic
            seo_summary = ""

        # Section 3: channel follow line
        follow_line = f"Follow @{self._channel_name} for daily mind-blowing facts!"

        # Section 4: hashtag block
        category        = script.get("category", "general")
        topic_hashtags  = list(script.get("topic_hashtags", []))
        hashtag_block   = self._build_hashtag_block(category, topic_hashtags)

        parts = [hook_line]
        if seo_summary:
            parts.append(seo_summary)
        parts.append(follow_line)
        parts.append(hashtag_block)

        full = "\n\n".join(parts)

        if len(full) > _MAX_DESCRIPTION_LEN:
            full = full[: _MAX_DESCRIPTION_LEN - 3] + "..."

        return full

    def _build_hashtag_block(self, category: str, topic_hashtags: list[str]) -> str:
        """
        Assemble the hashtag block from 4 sources (in priority order):

          1. Mandatory  (#Shorts, #ClickBaitnt  — always first)
          2. Topic-specific (from script["topic_hashtags"], 5-8 used)
          3. Niche/category  (mapped from category string, 3-5)
          4. Viral/evergreen (from config viral_hashtags, fills remaining slots)

        Total capped at max_hashtags.  Deduplication via lowercase seen set.
        """
        seen: set[str] = set()
        result: list[str] = []

        def _add(tag: str) -> bool:
            """Normalise and add tag if not already seen. Return True if added."""
            t = tag.strip()
            if not t.startswith("#"):
                t = "#" + t
            key = t.lower()
            if key in seen:
                return False
            seen.add(key)
            result.append(t)
            return True

        # 1. Mandatory
        for h in self._mandatory_hashtags:
            _add(h)

        # 2. Topic-specific (cap at 8)
        for h in topic_hashtags[:8]:
            if len(result) >= self._max_hashtags:
                break
            _add(h)

        # 3. Niche
        for h in _category_to_niche_hashtags(category):
            if len(result) >= self._max_hashtags:
                break
            _add(h)

        # 4. Viral fill-up
        for h in self._viral_hashtags:
            if len(result) >= self._max_hashtags:
                break
            _add(h)

        # Pad with defaults if still below minimum (unlikely but safe)
        defaults = ["#Facts", "#Viral", "#Trending", "#Amazing", "#Science",
                    "#Psychology", "#History", "#Money", "#Technology", "#Learn"]
        for h in defaults:
            if len(result) >= self._min_hashtags:
                break
            _add(h)

        return " ".join(result)

    def _build_tags(self, script: dict) -> list[str]:
        """
        Merge script tags with config default tags, deduplicate,
        and cap to YouTube's 500-char total / 20-tag limit.
        """
        script_tags: list[str] = list(script.get("tags", []))
        topic_words: list[str] = _topic_to_tags(script.get("topic", ""))

        # Merge: script tags first (higher priority), then defaults
        combined: list[str] = []
        seen: set[str] = set()

        for tag in script_tags + self._default_tags + topic_words:
            tag_clean = tag.strip().lower()
            if not tag_clean or tag_clean in seen:
                continue
            if len(tag_clean) > _MAX_SINGLE_TAG_LEN:
                tag_clean = tag_clean[:_MAX_SINGLE_TAG_LEN]
            seen.add(tag_clean)
            combined.append(tag_clean)

        # Respect limits
        combined = combined[:_MAX_TAGS]
        combined = _truncate_to_char_limit(combined, _MAX_TAG_CHARS)

        return combined


# ------------------------------------------------------------------ #
#  Module-level helpers                                               #
# ------------------------------------------------------------------ #

def _category_to_niche_hashtags(category: str) -> list[str]:
    """Map a niche category string to 3-5 relevant hashtags."""
    mapping: dict[str, list[str]] = {
        "technology":      ["#Technology", "#TechFacts", "#Innovation", "#FutureTech"],
        "science":         ["#Science", "#ScienceFacts", "#Physics", "#Biology"],
        "psychology":      ["#Psychology", "#MindFacts", "#BrainFacts", "#HumanBehavior"],
        "money":           ["#Money", "#Finance", "#WealthTips", "#PersonalFinance"],
        "history":         ["#History", "#HistoryFacts", "#AncientHistory", "#Historical"],
        "shocking facts":  ["#ShockingFacts", "#CrazyFacts", "#Unbelievable", "#MindBlowing"],
        "general":         ["#Facts", "#InterestingFacts", "#DailyFacts", "#KnowledgeIsPower"],
    }
    cat_lower = category.lower().strip()
    return mapping.get(cat_lower, mapping["general"])


def _topic_to_tags(topic: str) -> list[str]:
    """Split a topic string into individual word tags (3+ chars)."""
    words = topic.lower().split()
    return [w.strip(".,!?") for w in words if len(w) >= 3]


def _truncate_to_char_limit(tags: list[str], max_chars: int) -> list[str]:
    """
    Return the longest prefix of tags whose joined length <= max_chars.
    Tags are joined by comma (matching YouTube's internal counting).
    """
    result: list[str] = []
    total = 0
    for tag in tags:
        addition = len(tag) + (1 if result else 0)   # +1 for comma separator
        if total + addition > max_chars:
            break
        result.append(tag)
        total += addition
    return result
