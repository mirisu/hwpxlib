# Image Embedding

## Purpose
Embed raster images inline within document flow.

## Acceptance Criteria
- Supported formats: PNG, JPEG, GIF, BMP (detected from magic bytes)
- Images stored in BinData/ directory within the HWPX ZIP
- content.hpf manifest includes image items with `isEmbeded="1"`
- Image dimensions auto-detected from file headers
- Pixel-to-HWPUNIT conversion: 1 pixel = 75 HWPUNIT
- Custom width/height override auto-detection
- Each image gets unique binary_item_id ("image1", "image2", etc.)
- hp:pic element wraps image in paragraph with proper sz, pos, imgRect
- treatAsChar="1" for inline placement

## Edge Cases
- Unknown image format falls back to PNG mime type and 200x200 default size
- BMP with negative height (top-down) handled via abs()
