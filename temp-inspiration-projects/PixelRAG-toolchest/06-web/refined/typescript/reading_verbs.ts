const READING_VERBS = [
  "Looking at",
  "Reading",
  "Studying",
  "Examining",
  "Poring over",
  "Peering at",
  "Taking in",
  "Scanning",
]

function TileGallery({ tiles, loading, onTileClick }: { tiles: TileView[]; loading?: boolean; onTileClick: (hit: Hit, allHits: Hit[]) => void }) {
