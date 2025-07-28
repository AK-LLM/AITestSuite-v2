import qrcode

link = "http://evil.attacker/verify"
img = qrcode.make(link)
img.save("phish_qr.png")
print("[+] QR code saved as phish_qr.png")
