# Content Service

Complete guide for ContentService - Upload, download, and manage files.

## Coming Soon
This documentation is being prepared. Please check back soon for comprehensive guides on:
- File upload and download
- Content type handling
- File management best practices
- Storage optimization

## Overwriting a content in place

The web editor saves an annotation by overwriting its content; the content keeps its ID.
Do the same instead of creating a new content and pointing the annotation at it (which
leaves the old content behind):

```python
from spb_onprem import ContentService, DataService

ContentService().update_json_content(content_id, {"objects": [...]})        # JSON
ContentService().update_content_with_data(content_id, png_bytes, "image/png")
ContentService().update_content(content_id, "/path/to/file.json")           # type from the name

# A slice annotation version, found by its ids:
DataService().overwrite_slice_annotation_version_content(
    dataset_id, data_id, slice_id, version_id, {"objects": [...]},
)
```

The platform does not check that the content exists: a mistyped ID would create a new object
under it. The `update_*` functions therefore check first (`content_exists`, one HEAD request) and
refuse a missing content; pass `check_exists=False` to skip it.

`get_update_url(content_id, content_type)` returns the presigned PUT URL (from
`generateContentUpdateURL`) if you upload yourself: send the same `Content-Type`, and do not log
the URL (its query is a credential). The SDK sends no platform credentials to it.
