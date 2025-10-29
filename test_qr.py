from app.utils.qr import generate_qr_base64

if __name__ == "__main__":
    data = "test-checkin-token-123"
    qr_base64 = generate_qr_base64(data)
    print("Base64 QR code string:")
    print(qr_base64)
    # Optionally, save to file for visual check
    with open("test_qr.png", "wb") as f:
        import base64
        f.write(base64.b64decode(qr_base64))
    print("QR code image saved as test_qr.png")
