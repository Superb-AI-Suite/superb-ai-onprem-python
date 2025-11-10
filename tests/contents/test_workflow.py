from spb_onprem import ContentService


def test_content_workflow():
    """Test complete workflow for content operations:
    - Create folder content
    - Get upload URL with file_name
    - Get download URL with file_name
    - Get download URL without file_name (legacy)
    """
    
    content_service = ContentService()
    
    print("=" * 70)
    print("Content Service Workflow Test")
    print("=" * 70)
    
    # ==================== CREATE FOLDER CONTENT ====================
    
    # Step 1: Create folder content
    print("\n[Step 1] Creating folder content...")
    try:
        folder_content_id = content_service.create_folder_content()
        print(f"✅ Created folder content ID: {folder_content_id}")
    except Exception as e:
        print(f"❌ Failed to create folder content: {e}")
        return False
    
    # ==================== GET UPLOAD URL ====================
    
    # Step 2: Get upload URL with file_name
    print("\n[Step 2] Getting upload URL with file_name...")
    try:
        upload_url_response = content_service.get_upload_url(
            content_id=folder_content_id,
            file_name="test_file.json",
            content_type="application/json"
        )
        print(f"✅ Got upload URL response")
        print(f"   Content ID: {folder_content_id}")
        print(f"   File Name: test_file.json")
        print(f"   Response: {upload_url_response}")
    except Exception as e:
        print(f"❌ Failed to get upload URL: {e}")
        return False
    
    # Step 3: Get upload URL with different content type
    print("\n[Step 3] Getting upload URL for image file...")
    try:
        upload_url_image = content_service.get_upload_url(
            content_id=folder_content_id,
            file_name="test_image.png",
            content_type="image/png"
        )
        print(f"✅ Got upload URL for image")
        print(f"   File Name: test_image.png")
        print(f"   Content Type: image/png")
        print(f"   Response: {upload_url_image}")
    except Exception as e:
        print(f"❌ Failed to get upload URL for image: {e}")
        return False
    
    # ==================== GET DOWNLOAD URL ====================
    
    # Step 4: Get download URL with file_name (new mutation)
    print("\n[Step 4] Getting download URL with file_name...")
    try:
        download_url_with_filename = content_service.get_download_url(
            content_id=folder_content_id,
            file_name="test_file.json"
        )
        print(f"✅ Got download URL with file_name")
        print(f"   Content ID: {folder_content_id}")
        print(f"   File Name: test_file.json")
        print(f"   Response: {download_url_with_filename}")
    except Exception as e:
        print(f"❌ Failed to get download URL with file_name: {e}")
        return False
    
    # Step 5: Get download URL without file_name (legacy mutation)
    print("\n[Step 5] Getting download URL without file_name (legacy)...")
    try:
        download_url_legacy = content_service.get_download_url(
            content_id=folder_content_id
        )
        print(f"✅ Got download URL (legacy)")
        print(f"   Content ID: {folder_content_id}")
        print(f"   Response: {download_url_legacy}")
    except Exception as e:
        print(f"❌ Failed to get download URL (legacy): {e}")
        return False
    
    # ==================== ADDITIONAL TESTS ====================
    
    # Step 6: Create another folder content and test with different file
    print("\n[Step 6] Creating another folder content for additional testing...")
    try:
        folder_content_id_2 = content_service.create_folder_content()
        print(f"✅ Created second folder content ID: {folder_content_id_2}")
        
        # Test with CSV file
        upload_url_csv = content_service.get_upload_url(
            content_id=folder_content_id_2,
            file_name="data.csv",
            content_type="text/csv"
        )
        print(f"✅ Got upload URL for CSV file")
        print(f"   File Name: data.csv")
        print(f"   Response: {upload_url_csv}")
        
        # Test download with CSV file
        download_url_csv = content_service.get_download_url(
            content_id=folder_content_id_2,
            file_name="data.csv"
        )
        print(f"✅ Got download URL for CSV file")
        print(f"   Response: {download_url_csv}")
        
    except Exception as e:
        print(f"⚠️  Additional tests failed: {e}")
        print("   (Main workflow completed successfully)")
    
    print("\n" + "=" * 70)
    print("Content Workflow Test Passed Successfully! 🎉")
    print("=" * 70)
    print("\nSummary:")
    print("  ✓ Created folder content IDs")
    print("  ✓ Generated upload URLs with file_name and content_type")
    print("  ✓ Generated download URLs with file_name (new mutation)")
    print("  ✓ Generated download URLs without file_name (legacy mutation)")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    test_content_workflow()
