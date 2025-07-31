#!/usr/bin/env python3
"""
Test auto-scroll functionality
"""

from settings_manager import SettingsManager

def test_auto_scroll_setting():
    """Test that auto-scroll setting works correctly"""
    print("Testing auto-scroll feature...")
    
    # Initialize settings manager
    settings = SettingsManager()
    
    # Test default value
    default_value = settings.get('auto_scroll_on_page_change', None)
    print(f"Default auto-scroll setting: {default_value}")
    
    # Test setting the value
    settings.set('auto_scroll_on_page_change', False)
    value_after_set = settings.get('auto_scroll_on_page_change')
    print(f"After setting to False: {value_after_set}")
    
    # Test setting back to True
    settings.set('auto_scroll_on_page_change', True)
    value_after_true = settings.get('auto_scroll_on_page_change')
    print(f"After setting to True: {value_after_true}")
    
    # Verify the setting is saved and loaded correctly
    settings.save()
    
    # Create new instance to test loading
    new_settings = SettingsManager()
    new_settings.load()
    loaded_value = new_settings.get('auto_scroll_on_page_change')
    print(f"After loading from file: {loaded_value}")
    
    if loaded_value == True:
        print("✅ Auto-scroll setting test passed!")
        return True
    else:
        print("❌ Auto-scroll setting test failed!")
        return False

if __name__ == "__main__":
    test_auto_scroll_setting()