'''Simple data class for storing track info'''
class Track:
    title : str
    artist : str

    def __init__(self,
        title: str,
        artist: str
        ) -> None:
        self.title = title
        self.artist = artist
    def __hash__(self) -> int:
        return hash(self.title) ^ hash(self.artist)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Track):
            return NotImplemented
        return (
            (self.title, self.artist) == (other.title, other.artist)
        )
