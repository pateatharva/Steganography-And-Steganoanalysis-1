import torch
import torch.nn as nn
import torch.nn.functional as F

def SN(module):
    return nn.utils.spectral_norm(module)

class UNetBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, 1, 1),
            nn.GroupNorm(8, out_ch),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, 1, 1),
            nn.GroupNorm(8, out_ch),
            nn.LeakyReLU(0.2, inplace=True)
        )
    def forward(self, x):
        return self.block(x)

class AdvancedGenerator(nn.Module):
    def __init__(self, message_len=256):
        super().__init__()
        self.down1 = UNetBlock(4, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = UNetBlock(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.down3 = UNetBlock(128, 256)
        self.pool3 = nn.MaxPool2d(2)
        self.bottleneck = UNetBlock(256, 512)
        self.up3 = nn.ConvTranspose2d(512, 256, 2, 2)
        self.upblock3 = UNetBlock(512, 256)
        self.up2 = nn.ConvTranspose2d(256, 128, 2, 2)
        self.upblock2 = UNetBlock(256, 128)
        self.up1 = nn.ConvTranspose2d(128, 64, 2, 2)
        self.upblock1 = UNetBlock(128, 64)
        self.outconv = nn.Conv2d(64, 3, 1)
        self.final_act = nn.Tanh()
        self.msg_proj = nn.Linear(message_len, 96*96)

    def forward(self, image, message):
        B,_,H,W = image.shape
        msg_map = self.msg_proj(message).view(B,1,H,W)
        x = torch.cat([image, msg_map], 1)
        d1 = self.down1(x)
        d2 = self.down2(self.pool1(d1))
        d3 = self.down3(self.pool2(d2))
        bn = self.bottleneck(self.pool3(d3))
        u3 = self.up3(bn)
        u3 = torch.cat([u3, d3], 1)
        u3 = self.upblock3(u3)
        u2 = self.up2(u3)
        u2 = torch.cat([u2, d2], 1)
        u2 = self.upblock2(u2)
        u1 = self.up1(u2)
        u1 = torch.cat([u1, d1], 1)
        u1 = self.upblock1(u1)
        out = self.outconv(u1)
        return self.final_act(out)

class ResidualBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, 1, 1),
            nn.GroupNorm(8, out_ch),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, 1, 1),
            nn.GroupNorm(8, out_ch)
        )
        self.shortcut = nn.Conv2d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()

    def forward(self, x):
        return F.leaky_relu(self.conv(x) + self.shortcut(x), 0.2)

class AdvancedDecoder(nn.Module):
    def __init__(self, message_len=256):
        super().__init__()
        self.seq = nn.Sequential(
            ResidualBlock(3, 64),
            nn.AvgPool2d(2),
            ResidualBlock(64, 128),
            nn.AvgPool2d(2),
            ResidualBlock(128, 256),
            nn.AvgPool2d(2),
            ResidualBlock(256, 512),
            nn.AdaptiveAvgPool2d((6, 6)),
            nn.Flatten(),
            nn.Linear(512*6*6, 1024),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Dropout(0.3),
            nn.Linear(1024, message_len),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.seq(x)

class AdvancedDiscriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.main = nn.Sequential(
            SN(nn.Conv2d(3, 64, 4, 2, 1)), 
            nn.LeakyReLU(0.2, inplace=True), 
            nn.Dropout2d(0.25),
            SN(nn.Conv2d(64, 128, 4, 2, 1)), 
            nn.GroupNorm(8, 128), 
            nn.LeakyReLU(0.2, inplace=True), 
            nn.Dropout2d(0.25),
            SN(nn.Conv2d(128, 256, 4, 2, 1)), 
            nn.GroupNorm(16, 256), 
            nn.LeakyReLU(0.2, inplace=True), 
            nn.Dropout2d(0.25),
            SN(nn.Conv2d(256, 512, 4, 2, 1)), 
            nn.GroupNorm(32, 512), 
            nn.LeakyReLU(0.2, inplace=True),
            nn.AdaptiveAvgPool2d((6, 6)),
            nn.Flatten(),
            nn.Linear(512*6*6, 1)
        )
    def forward(self, x):
        return self.main(x)

def text_to_bits(text, max_len=32):
    bits = ''.join(format(ord(c), '08b') for c in text)
    bits = bits.ljust(max_len*8, '0')
    return torch.tensor([int(bit) for bit in bits[:max_len*8]], dtype=torch.float32)

def bits_to_text(bits):
    # Convert a sequence of bits (0/1) to bytes, then to a safe string.
    byte_vals = []
    for b in range(0, len(bits), 8):
        byte = bits[b:b+8]
        byte_str = ''.join([str(int(bit)) for bit in byte])
        byte_vals.append(int(byte_str, 2))
    data = bytes(byte_vals)
    # If data is printable ASCII, return as text. Otherwise return a base64 wrapper so
    # frontends can handle binary payloads safely.
    try:
        import base64
        if all((32 <= c <= 126) or c in (9,10,13) for c in data):
            return data.decode('ascii').rstrip('\x00')
        else:
            return 'RAWB64:' + base64.b64encode(data).decode('ascii')
    except Exception:
        # Fallback: best-effort decode
        try:
            return data.decode('utf-8', errors='replace').rstrip('\x00')
        except Exception:
            return ''