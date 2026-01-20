import os

# Read the corrupted file in binary mode
input_file = r"f:\SIDE HUSTLE\Morning_Quiz\backend\main.py"
output_file = r"f:\SIDE HUSTLE\Morning_Quiz\backend\main_fixed.py"

print("Reading main.py...")
with open(input_file, 'rb') as f:
    content = f.read()

print(f"Original size: {len(content)} bytes")
print(f"Null bytes found: {content.count(b'\\x00')}")

# Remove null bytes
cleaned_content = content.replace(b'\x00', b'')

print(f"Cleaned size: {len(cleaned_content)} bytes")

# Write cleaned content
with open(output_file, 'wb') as f:
    f.write(cleaned_content)

print(f"✅ Clean file saved to: {output_file}")
print("\nNext: Run deploy-fixed-main.bat")
